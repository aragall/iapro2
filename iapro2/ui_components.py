import streamlit as st

def setup_page():
    """Sets up the page configuration and custom Fintech CSS."""
    st.set_page_config(
        page_title="AURA Finance | App",
        page_icon="💸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for Neo-bank Look (Revolut Style)
    custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

        /* General Body */
        .stApp {
            background-color: #000000; /* Pure Black */
            color: #FFFFFF;
            font-family: 'Inter', sans-serif;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0c0c0c; /* Slightly lighter than main */
            border-right: 1px solid #1C1C1E;
        }

        /* Sidebar Navigation (Modern Pills) */
        .stRadio > div[role="radiogroup"] {
            gap: 8px;
            padding-top: 20px;
        }
        
        .stRadio > div[role="radiogroup"] > label {
            background-color: transparent;
            border: 1px solid transparent;
            color: #6B7280;
            font-weight: 500;
            padding: 10px 16px;
            border-radius: 12px;
            transition: all 0.2s;
            margin-bottom: 4px;
        }
        
        .stRadio > div[role="radiogroup"] > label:hover {
            color: #FFFFFF;
            background-color: #1C1C1E;
        }
        
        /* Selected Tab Styling (Hack via ARIA) */
        .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
            background-color: #1C1C1E;
            border: 1px solid #3B82F6;
            color: #FFFFFF;
            font-weight: 600;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.1);
        }

        /* System Access Section */
        .system-access-box {
            background: #121212;
            border: 1px dashed #2C2C2E;
            border-radius: 12px;
            padding: 15px;
            margin-top: 20px;
        }

        /* Hero Balance Card */
        .hero-container {
            background: linear-gradient(135deg, #1C1C1E 0%, #2C2C2E 100%);
            border-radius: 24px;
            padding: 30px;
            margin-bottom: 20px;
            text-align: center;
            border: 1px solid #2C2C2E;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        
        .hero-label {
            font-size: 14px;
            color: #9CA3AF;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        
        .hero-value {
            font-size: 56px;
            font-weight: 900;
            color: #FFFFFF;
            letter-spacing: -1.5px;
        }
        
        .hero-delta {
            display: inline-block;
            background-color: rgba(59, 130, 246, 0.2); /* Blue tint */
            color: #60A5FA;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-top: 10px;
        }

        /* Quick Stats (Pills) */
        .stat-card {
            background-color: #1C1C1E;
            border-radius: 20px;
            padding: 20px;
            border: 1px solid #2C2C2E;
            transition: transform 0.2s;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
            border-color: #3B82F6;
        }
        
        .stat-label {
            font-size: 12px;
            color: #9CA3AF;
        }
        
        .stat-value {
            font-size: 20px;
            font-weight: 700;
            margin-top: 4px;
        }

        /* Transaction List Row */
        .transaction-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #121212;
            padding: 16px 20px;
            border-radius: 16px;
            margin-bottom: 8px;
            transition: background-color 0.2s;
        }
        
        .transaction-row:hover {
            background-color: #1C1C1E;
        }
        
        .t-left { display: flex; flex-direction: column; }
        .t-title { font-weight: 600; font-size: 15px; color: #FFF; }
        .t-sub { font-size: 12px; color: #6B7280; }
        
        .t-right { text-align: right; }
        .t-amount { font-weight: 700; font-size: 15px; }
        .t-status { font-size: 11px; padding: 2px 8px; border-radius: 10px; }
        
        .status-paid { background-color: rgba(16, 185, 129, 0.2); color: #34D399; }
        .status-pending { background-color: rgba(245, 158, 11, 0.2); color: #FBBF24; }
        .status-overdue { background-color: rgba(239, 68, 68, 0.2); color: #F87171; }

        /* Buttons (Pill Shape) */
        .stButton > button {
            border-radius: 50px;
            background-color: #3B82F6; /* Vivid Blue */
            color: white;
            border: none;
            padding: 8px 24px;
            font-weight: 600;
        }
        
        .stButton > button:hover {
            background-color: #2563EB;
        }

    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def hero_section(total_revenue, delta):
    """Renders the main account balance styling."""
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-label">Total Balance</div>
        <div class="hero-value">{total_revenue}</div>
        <div class="hero-delta">▲ {delta} this month</div>
    </div>
    """, unsafe_allow_html=True)

def stat_card(label, value, color="#FFF"):
    """Renders a quick stat pill."""
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">{label}</div>
        <div class="stat-value" style="color: {color}">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def transaction_row(invoice_id, client, date, amount, status):
    """Renders a single row for the transaction list with a delete option."""
    status_lower = status.lower()
    initial = client[0] if client else "?"
    
    # Container styling
    row_style = """
        <style>
        .t-row {
            display: flex; 
            align-items: center; 
            background-color: #121212; 
            padding: 12px; 
            border-radius: 16px; 
            margin-bottom: 8px;
            border: 1px solid #1C1C1E;
        }
        .t-icon {
            width: 40px; height: 40px; 
            background: #2C2C2E; 
            border-radius: 50%; 
            display: flex; align-items: center; justify-content: center; 
            font-weight: bold; color: #6B7280;
            margin-right: 15px;
        }
        .t-details { flex-grow: 1; }
        .t-title { display: block; font-weight: 600; font-size: 14px; color: #FFF; }
        .t-sub { display: block; font-size: 12px; color: #6B7280; }
        .t-amount { font-weight: 700; font-size: 14px; color: #FFF; text-align: right; margin-right: 15px;}
        .status-badge {
            font-size: 10px; padding: 4px 8px; border-radius: 6px; font-weight: 600;
        }
        .status-paid { background-color: rgba(16, 185, 129, 0.2); color: #34D399; }
        .status-pending { background-color: rgba(245, 158, 11, 0.2); color: #FBBF24; }
        .status-overdue { background-color: rgba(239, 68, 68, 0.2); color: #F87171; }
        </style>
    """
    st.markdown(row_style, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.7, 0.2, 0.1])
    
    with col1:
        st.markdown(f"""
        <div class="t-row">
            <div class="t-icon">{initial}</div>
            <div class="t-details">
                <span class="t-title">{client}</span>
                <span class="t-sub">{date}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        # Amount and Status
        st.markdown(f"""
        <div style="text-align: right; padding-top: 10px;">
            <div class="t-amount">€{amount:,.2f}</div>
            <span class="status-badge status-{status_lower}">{status}</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        # Delete Button (Invisible styling hack or standard button)
        st.markdown("<div style='padding-top: 15px;'>", unsafe_allow_html=True)
        if st.button("🗑️", key=f"del_{invoice_id}", help="Delete Invoice"):
            return True
        st.markdown("</div>", unsafe_allow_html=True)
            
    return False
    
def section_header(title, subtitle=None):
    st.markdown(f"### {title}")


