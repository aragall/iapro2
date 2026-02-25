from fpdf import FPDF
from datetime import datetime

class PremiumInvoicePDF(FPDF):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()

    def header(self):
        # Background color for header
        self.set_fill_color(14, 17, 23)  # #0E1117 (Dark)
        self.rect(0, 0, 210, 50, 'F')
        
        # Logo / Title
        self.set_y(15)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(212, 175, 55)  # #D4AF37 (Gold)
        self.cell(0, 10, 'AURA FINANCE', ln=True, align='L')
        
        # Sender Details (Hardcoded Template)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(200, 200, 200)
        self.cell(0, 5, 'Paseo de la Castellana 1, Madrid', ln=True, align='L')
        self.cell(0, 5, 'VAT: ES-B12345678', ln=True, align='L')
        self.cell(0, 5, 'contact@aurafinance.lux', ln=True, align='L')
        
        # Invoice Label
        self.set_y(15)
        self.set_font('Helvetica', 'B', 30)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'INVOICE', ln=True, align='R')
        
        self.set_font('Helvetica', '', 10)
        self.cell(0, 10, f"#{self.data.get('invoice_number', 'DRAFT')}", ln=True, align='R')
        self.ln(20)

    def footer(self):
        self.set_y(-20)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, 'Payment due within 30 days.', 0, 1, 'C')
        self.cell(0, 5, 'Thank you for your business.', 0, 1, 'C')

    def generate(self, output_path):
        # Client Info
        self.set_y(60)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, "BILL TO:", ln=True)
        
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, f"{self.data.get('client_name', 'Unknown Client').upper()}", ln=True)
        
        self.set_font('Helvetica', '', 10)
        self.set_text_color(60, 60, 60)
        address = self.data.get('client_address')
        if address:
            self.cell(0, 5, address, ln=True)
        
        self.set_y(60)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, "DATE:", ln=True, align='R')
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, f"{self.data.get('date', datetime.now().strftime('%Y-%m-%d'))}", ln=True, align='R')
        
        self.ln(20)
        
        # Table Header
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 0, 0)
        self.set_font('Helvetica', 'B', 9)
        self.cell(110, 8, "DESCRIPTION", 0, 0, 'L', True)
        self.cell(20, 8, "QTY", 0, 0, 'C', True)
        self.cell(30, 8, "UNIT PRICE", 0, 0, 'R', True)
        self.cell(30, 8, "AMOUNT", 0, 1, 'R', True)
        
        self.ln(2)
        
        # Table Rows
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        
        total_amount = 0.0
        
        items = self.data.get('items', [])
        for item in items:
            description = item.get('description', 'Item')
            
            # Safe conversion helper
            def safe_float(val, default=0.0):
                try:
                    if val is None: return default
                    return float(val)
                except (ValueError, TypeError):
                    return default

            qty = safe_float(item.get('quantity'), 1.0)
            price = safe_float(item.get('unit_price'), 0.0)
            total = safe_float(item.get('total'), qty * price)
            
            self.cell(110, 10, description, 'B')
            self.cell(20, 10, str(int(qty)), 'B', 0, 'C')
            self.cell(30, 10, f"{price:,.2f}", 'B', 0, 'R')
            self.cell(30, 10, f"{total:,.2f}", 'B', 1, 'R')
            
            total_amount += total
            
        # Totals Section
        self.ln(10)
        
        # Use extracted total if valid, otherwise calculated
        extracted_total = self.data.get('total_amount')
        try:
             final_total = float(extracted_total) if extracted_total else total_amount
        except:
             final_total = total_amount
             
        self.set_font('Helvetica', '', 10)
        self.cell(160, 8, "Subtotal", 0, 0, 'R')
        self.cell(30, 8, f"{final_total:,.2f}", 0, 1, 'R')
        
        self.cell(160, 8, "Tax (21%)", 0, 0, 'R')
        tax = final_total * 0.21
        self.cell(30, 8, f"{tax:,.2f}", 0, 1, 'R')
        
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(212, 175, 55) # Gold
        self.cell(160, 10, "TOTAL EUR", 0, 0, 'R')
        self.cell(30, 10, f"{(final_total + tax):,.2f}", 0, 1, 'R')
        
        self.output(output_path)
