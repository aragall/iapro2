import streamlit as st
import ui_components as ui
import database as db
import processor as proc
import pandas as pd

# --- Page Setup ---
ui.setup_page()

# Initialize session state for auth
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'dni' not in st.session_state:
    st.session_state['dni'] = None

# Custom Auth UI
if not st.session_state['user_id']:
    st.markdown("<div style='text-align: center; margin-top: 50px;'><h1 style='font-size: 3rem;'>AURA FINANCE</h1><p style='color: #6B7280;'>Enter your credentials to access your personal CRM</p></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='system-access-box'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                log_dni = st.text_input("DNI / NIF")
                log_password = st.text_input("Contraseña", type="password")
                submit_login = st.form_submit_button("Acceder al Sistema")
                
                if submit_login:
                    user_id = db.verify_user(log_dni, log_password)
                    if user_id:
                        st.session_state['user_id'] = user_id
                        st.session_state['dni'] = log_dni
                        st.rerun()
                    else:
                        st.error("Credenciales Inválidas")
                        
        with tab2:
            with st.form("register_form"):
                reg_dni = st.text_input("DNI / NIF (Registro)")
                reg_password = st.text_input("Nueva Contraseña", type="password")
                submit_register = st.form_submit_button("Crear Cuenta")
                
                if submit_register:
                    if len(reg_dni) < 5 or len(reg_password) < 6:
                        st.error("Introduzca un DNI válido y una contraseña mayor de 6 caracteres.")
                    else:
                        success = db.create_user(reg_dni, reg_password)
                        if success:
                            st.success("¡Cuenta creada con éxito! Por favor inicie sesión.")
                        else:
                            st.error("Este DNI ya está registrado en el sistema.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop() # Halt execution here if not logged in

# --- Sidebar Configuration ---
with st.sidebar:
    st.title(f"AURA FINANCE\n\n*Usuario:\n{st.session_state['dni']}*")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation", 
        ["Dashboard", "Smart Invoicing", "CRM & Clients", "Financial Planning"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # API Key Configuration
    st.markdown("### 🔑 System Access")
    api_key = st.text_input("Google API Key", type="password", help="Required for AI features")
    
    if api_key:
        if proc.configure_gemini(api_key):
            st.success("System Online")
        else:
            st.error("Connection Failed")
    else:
        st.warning("API Key Required")
        
    st.markdown("---")
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state['user_id'] = None
        st.session_state['dni'] = None
        st.rerun()
    st.markdown("v1.0.0 | Luxury Edition")

# --- Page Logic ---

user_id = st.session_state['user_id']

if page == "Dashboard":
    # 1. Hero Balance Section
    metrics = db.get_dashboard_metrics(user_id)
    ui.hero_section(f"€{metrics['total_revenue']:,.2f}", metrics['delta_revenue'])
    
    # 2. Quick Stats Row
    st.markdown("#### Stats Overview")
    col1, col2, col3 = st.columns(3)
    client_count = len(db.get_clients(user_id))
    
    with col1:
        ui.stat_card("Pending", f"€{metrics['pending_revenue']:,.2f}", "#FBBF24") # Amber
    with col2:
        ui.stat_card("Overdue", f"€{metrics['overdue_revenue']:,.2f}", "#F87171") # Red
    with col3:
        ui.stat_card("Active Clients", f"{client_count}", "#3B82F6") # Blue

    # 3. Transaction List
    st.markdown("#### Recent Transactions")
    invoices = db.get_invoices(user_id)
    
    if not invoices.empty:
        # Iterate over last 5 invoices and render as beautiful rows
        for _, row in invoices.head(10).iterrows():
            delete_clicked = ui.transaction_row(
                invoice_id=row['id'],
                client=row['client_name'],
                date=row['date'],
                amount=row['amount'],
                status=row['status']
            )
            
            if delete_clicked:
                if db.delete_invoice(user_id, row['id']):
                    st.success("Invoice Deleted")
                    st.rerun()
        
        if st.button("View All Transactions"):
            page = "Smart Invoicing" # Simple navigation simulation
    else:
        st.info("No recent transactions.")

    # 4. Database Views (Restored)
    st.markdown("### 📂 Database Records")
    
    with st.expander("View All Invoices (Live Data)", expanded=False):
        all_invoices = db.get_invoices(user_id)
        if not all_invoices.empty:
            st.dataframe(
                all_invoices,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "amount": st.column_config.NumberColumn("Amount", format="€%.2f"),
                    "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                    "client_name": "Client",
                    "status": "Status"
                }
            )
        else:
            st.info("No invoices found.")

    with st.expander("Client Registry", expanded=False):
        all_clients = db.get_clients(user_id)
        if not all_clients.empty:
            st.dataframe(
                all_clients, 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("No clients registered.")

elif page == "Smart Invoicing":
    ui.section_header("Gestión Inteligente", "Procesamiento de documentos por IA")
    
    tab1, tab2 = st.tabs(["Subir & Procesar", "Historial"])
    
    with tab1:
        st.markdown("#### Documentos y Notas de Voz")
        
        col_up, col_rec = st.columns(2)
        with col_up:
            uploaded_file = st.file_uploader(
                "📂 Subir Archivo", 
                type=["png", "jpg", "jpeg", "pdf", "mp3", "wav", "m4a", "mp4"]
            )
        with col_rec:
            recorded_audio = st.audio_input("🎙️ Grabar Nota Directamente")
            
        active_file = recorded_audio if recorded_audio else uploaded_file
        
        if active_file and api_key:
            mime_type = getattr(active_file, "type", "audio/wav")
            
            if mime_type.startswith("audio") or mime_type == "video/mp4":
                st.audio(active_file, format=mime_type)
            else:
                st.image(active_file, caption="Vista Previa", width=300)
            
            if st.button("Analizar con Gemini", use_container_width=True):
                with st.spinner("La IA está analizando la estructura..."):
                    # Read file based on type
                    bytes_data = active_file.getvalue()
                    
                    data = proc.extract_invoice_data(bytes_data, mime_type)
                    
                    if "error" in data:
                        st.error(f"Fallo en Análisis: {data['error']}")
                    else:
                        st.success("Extracción Completada")
                        st.json(data)
                        
                        # Save to Session State for PDF generation/DB Save
                        st.session_state['last_invoice_data'] = data
                        
        elif not api_key:
            st.warning("Por favor configura tu API Key en el menú lateral.")
            
        # PDF Generation & Database Save Section
        if 'last_invoice_data' in st.session_state:
            st.markdown("---")
            st.markdown("### 📄 Acciones")
            
            col_save, col_pdf = st.columns(2)
            
            data = st.session_state['last_invoice_data']
            
            with col_save:
                if st.button("Guardar en Base de Datos", use_container_width=True):
                    saved = db.add_invoice(
                        user_id=st.session_state['user_id'],
                        client_name=data.get('client_name', 'Unknown Client'),
                        invoice_number=data.get('invoice_number', 'Draft'),
                        date=data.get('date', pd.Timestamp.now().strftime('%Y-%m-%d')),
                        amount=data.get('total_amount', 0.0),
                        items=data.get('items', []),
                        status='Pending'
                    )
                    if saved:
                        st.success("✅ Factura Guardada en el Registro")
                        st.balloons() # Interactive feedback
                    else:
                        st.error("❌ Error en la Base de Datos")

            with col_pdf:
                # Prepare PDF for download
                from invoice_generator import PremiumInvoicePDF
                import tempfile
                
                try:
                    pdf = PremiumInvoicePDF(data)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        pdf.generate(tmp.name)
                        tmp_path = tmp.name
                        
                    with open(tmp_path, "rb") as f:
                        st.download_button(
                            label="Generate Premium PDF",
                            data=f,
                            file_name=f"Invoice_{data.get('invoice_number', 'Draft')}.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"PDF Generation Error: {e}")
                        
    with tab2:
        st.dataframe(db.get_invoices(st.session_state['user_id']), use_container_width=True)

elif page == "CRM & Clients":
    ui.section_header("CRM Suite", "Client management & delinquency tracking")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Add New Client")
        with st.form("new_client"):
            name = st.text_input("Clint Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            
            if st.form_submit_button("Register Client"):
                if db.add_client(st.session_state['user_id'], name, email, phone):
                    st.success(f"Client {name} added.")
                else:
                    st.error("Failed to add client.")
                    
    with col2:
        st.markdown("### Client Directory")
        st.dataframe(db.get_clients(st.session_state['user_id']), use_container_width=True)

elif page == "Financial Planning":
    ui.section_header("Financial Planning", "Future forecasting & Tax Sentinel")
    st.info("Module under construction. Will include AI-driven revenue forecasting.")

