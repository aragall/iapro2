import google.generativeai as genai
import os
import json

def configure_gemini(api_key):
    """Configures the Gemini API with the provided key."""
    if not api_key:
        return False
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"Error configuring Gemini: {e}")
        return False

def extract_invoice_data(content, mime_type="image/jpeg"):
    """
    Uses Gemini 2.5 Flash to extract structured data from an invoice image or audio.
    
    Args:
        content: Raw bytes of the file.
        mime_type: MIME type of the content.
        
    Returns:
        dict: Extracted data in JSON format.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    if mime_type.startswith("audio/"):
        prompt = """
        You are an expert financial assistant processing a voice note for an invoice.
        
        Crucial: Extract only the following three key details relative to the service provided:
        1. CLIENT NAME (Who is the invoice for?)
        2. ITEMS/SERVICES (What was provided? quantity? price per unit?)
        3. TOTAL AMOUNT (If manually stated, otherwise assume unit_price * quantity)

        Output strict JSON:
        {
            "client_name": "Name of Client",
            "date": "YYYY-MM-DD",
            "invoice_number": "DRAFT-00X",
            "items": [
                {
                    "description": "Clear description of service/product",
                    "quantity": number (default 1),
                    "unit_price": number,
                    "total": number
                }
            ],
            "total_amount": number
        }
        
        Ignore conversational filler. If the user says "factura para Pepsi", the client is Pepsi.
        """
    else:
        prompt = """
        You are an expert financial assistant. Analyze this document (invoice or delivery note).
        Extract the following information in strict JSON format:
        - invoice_number (string, if available)
        - date (string, YYYY-MM-DD)
        - client_name (string, vendor or bill to depending on context)
        - client_address (string)
        - items (list of objects with 'description', 'quantity', 'unit_price', 'total')
        - total_amount (number)
        - currency (string)
        
        If a field is missing, use null. do not include markdown code fence blocks.
        """
    
    try:
        response = model.generate_content([
            {'mime_type': mime_type, 'data': content},
            prompt
        ])
        
        # Clean response text to ensure valid JSON
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
            
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}

def compare_documents(invoice_text, delivery_note_text):
    """
    Uses Gemini to compare an invoice against a delivery note for discrepancies.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Compare the following Invoice text with the Delivery Note text.
    Identify any discrepancies in items, quantities, or prices.
    
    Invoice:
    {invoice_text}
    
    Delivery Note:
    {delivery_note_text}
    
    Output a summary of discrepancies or "No discrepancies found".
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error during comparison: {e}"
