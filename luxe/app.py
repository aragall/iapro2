import streamlit as st
import ui_components as ui
import database as db
import processor as proc
import pandas as pd

# --- Page Setup ---
ui.setup_page()

# --- Sidebar Configuration ---
with st.sidebar:
    st.title("AURA FINANCE")
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
    st.markdown("v1.0.0 | Luxury Edition")

# --- Page Logic ---

if page == "Dashboard":
    ui.section_header("Executive Dashboard", "Global Financial Overview | Real-time")
    
    metrics = db.get_dashboard_metrics()
    client_count = len(db.get_clients())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ui.metric_card("Total Revenue", f"€{metrics['total_revenue']:,.2f}", delta=metrics['delta_revenue'])
    with col2:
        ui.metric_card("Pending Payments", f"€{metrics['pending_revenue']:,.2f}", delta=f"-{metrics['delta_pending']}")
    with col3:
        ui.metric_card("Overdue", f"€{metrics['overdue_revenue']:,.2f}", delta=metrics['delta_overdue'])
    with col4:
        ui.metric_card("Active Clients", f"{client_count}", delta=f"+{client_count} New")

    st.markdown("### 📊 Market Activity")
    invoices = db.get_invoices()
    if not invoices.empty:
        st.dataframe(
            invoices.tail(10), 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No recent transaction data available.")

elif page == "Smart Invoicing":
    ui.section_header("Smart Invoicing", "AI-powered document processing")
    
    tab1, tab2 = st.tabs(["Upload & Process", "History"])
    
    with tab1:
        st.markdown("#### Upload Document or Voice Note")
        uploaded_file = st.file_uploader(
            "Drop Invoice, Delivery Note, or Audio", 
            type=["png", "jpg", "jpeg", "pdf", "mp3", "wav", "m4a"]
        )
        
        if uploaded_file and api_key:
            mime_type = uploaded_file.type
            
            if mime_type.startswith("audio"):
                st.audio(uploaded_file, format=mime_type)
            else:
                st.image(uploaded_file, caption="Preview", width=300)
            
            if st.button("Analyze with Gemini"):
                with st.spinner("AI analyzing document structure..."):
                    # Read file based on type
                    bytes_data = uploaded_file.getvalue()
                    
                    data = proc.extract_invoice_data(bytes_data, mime_type)
                    
                    if "error" in data:
                        st.error(f"Analysis Failed: {data['error']}")
                    else:
                        st.success("Extraction Complete")
                        st.json(data)
                        
                        # Save to Session State for PDF generation/DB Save
                        st.session_state['last_invoice_data'] = data
                        
        elif not api_key:
            st.warning("Please configure your API Key in the sidebar.")
            
        # PDF Generation & Database Save Section
        if 'last_invoice_data' in st.session_state:
            st.markdown("---")
            st.markdown("### 📄 Actions")
            
            col_save, col_pdf = st.columns(2)
            
            data = st.session_state['last_invoice_data']
            
            with col_save:
                if st.button("Save to Database"):
                    saved = db.add_invoice(
                        client_name=data.get('client_name', 'Unknown Client'),
                        invoice_number=data.get('invoice_number', 'Draft'),
                        date=data.get('date', pd.Timestamp.now().strftime('%Y-%m-%d')),
                        amount=data.get('total_amount', 0.0),
                        items=data.get('items', []),
                        status='Pending'
                    )
                    if saved:
                        st.success("✅ Invoice Saved to Registry")
                        st.balloons() # Interactive feedback
                    else:
                        st.error("❌ Database Error")

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
        st.dataframe(db.get_invoices(), use_container_width=True)

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
                if db.add_client(name, email, phone):
                    st.success(f"Client {name} added.")
                else:
                    st.error("Failed to add client.")
                    
    with col2:
        st.markdown("### Client Directory")
        st.dataframe(db.get_clients(), use_container_width=True)

elif page == "Financial Planning":
    ui.section_header("Financial Planning", "Future forecasting & Tax Sentinel")
    st.info("Module under construction. Will include AI-driven revenue forecasting.")

