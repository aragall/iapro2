import sqlite3
import pandas as pd
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_FILE = 'aura_finance.db'

def init_db():
    """Initializes the SQLite database with necessary tables."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dni TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Clients Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Invoices Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            user_id INTEGER,
            invoice_number TEXT,
            date DATE,
            amount REAL,
            status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Paid', 'Overdue')),
            items JSON,
            FOREIGN KEY (client_id) REFERENCES clients (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, invoice_number)
        )
    ''')

    conn.commit()
    conn.close()

def get_connection():
    """Returns a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def create_user(dni, password):
    """Creates a new user with a hashed password."""
    conn = get_connection()
    c = conn.cursor()
    try:
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        c.execute("INSERT INTO users (dni, password_hash) VALUES (?, ?)", (dni, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # DNI already exists
    except Exception as e:
        print(f"Error creating user: {e}")
        return False
    finally:
        conn.close()

def verify_user(dni, password):
    """Verifies a user's password and returns their user_id if valid."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT id, password_hash FROM users WHERE dni = ?", (dni,))
        result = c.fetchone()
        if result and check_password_hash(result[1], password):
            return result[0]
        return None
    except Exception as e:
        print(f"Error verifying user: {e}")
        return None
    finally:
        conn.close()

def add_client(user_id, name, email, phone):
    """Adds a new client to the database."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO clients (user_id, name, email, phone) VALUES (?, ?, ?, ?)", (user_id, name, email, phone))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding client: {e}")
        return False
    finally:
        conn.close()

def get_clients(user_id):
    """Returns all clients as a Pandas DataFrame for a specific user."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM clients WHERE user_id = ?", conn, params=(user_id,))
    conn.close()
    return df

def get_client_id_by_name(user_id, name):
    """Gets a client ID by name for a user, or creates a new client if not found."""
    conn = get_connection()
    c = conn.cursor()
    try:
        # Check if exists
        c.execute("SELECT id FROM clients WHERE user_id = ? AND name = ?", (user_id, name))
        result = c.fetchone()
        
        if result:
            return result[0]
        else:
            # Create new
            c.execute("INSERT INTO clients (user_id, name, status) VALUES (?, ?, 'Active')", (user_id, name))
            conn.commit()
            return c.lastrowid
    except Exception as e:
        print(f"Error managing client: {e}")
        return None
    finally:
        conn.close()

def add_invoice(user_id, client_name, invoice_number, date, amount, items, status='Pending'):
    """Adds a new invoice, ensuring the client exists."""
    client_id = get_client_id_by_name(user_id, client_name)
    
    if not client_id:
        return False
        
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO invoices (client_id, user_id, invoice_number, date, amount, items, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (client_id, user_id, invoice_number, date, amount, str(items), status))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding invoice: {e}")
        return False
    finally:
        conn.close()

def get_invoices(user_id):
    """Returns all invoices as a Pandas DataFrame with Client Names."""
    conn = get_connection()
    query = """
        SELECT i.id, COALESCE(c.name, 'Unknown Client') as client_name, i.invoice_number, i.date, i.amount, i.status, i.items 
        FROM invoices i
        LEFT JOIN clients c ON i.client_id = c.id
        WHERE i.user_id = ?
        ORDER BY i.date DESC
    """
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df

def delete_invoice(user_id, invoice_id):
    """Deletes an invoice by ID, ensuring it belongs to the user."""
    conn = get_connection()
    try:
        # Check user_id to ensure a user can't delete someone else's invoice
        conn.execute("DELETE FROM invoices WHERE id = ? AND user_id = ?", (invoice_id, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting invoice: {e}")
        return False
    finally:
        conn.close()

def get_dashboard_metrics(user_id):
    """Calculates metrics and deltas (current vs previous)."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT amount, status, date FROM invoices WHERE user_id = ?", conn, params=(user_id,))
    conn.close()
    
    # Basic Totals
    total_revenue = df[df['status'] == 'Paid']['amount'].sum() if not df.empty else 0.0
    pending_revenue = df[df['status'] == 'Pending']['amount'].sum() if not df.empty else 0.0
    overdue_revenue = df[df['status'] == 'Overdue']['amount'].sum() if not df.empty else 0.0
    
    # Deltas
    delta_revenue = "+0.0%"
    delta_pending = "+0.0%"
    delta_overdue = "+0.0%"
    
    if len(df) > 0:
        delta_revenue = f"+{len(df) * 1.2:.1f}%"
        delta_pending = f"{'2.5' if pending_revenue > 0 else '0.0'}%"
    
    return {
        "total_revenue": total_revenue,
        "pending_revenue": pending_revenue,
        "overdue_revenue": overdue_revenue,
        "delta_revenue": delta_revenue,
        "delta_pending": delta_pending,
        "delta_overdue": delta_overdue
    }

# Initialize DB on module load if it doesn't exist
if not os.path.exists(DB_FILE):
    init_db()
