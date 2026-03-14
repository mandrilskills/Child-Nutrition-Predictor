import datetime
from fpdf import FPDF

def sanitize_for_pdf(text):
    """Replaces common unicode characters with ASCII equivalents for FPDF."""
    text = text.replace("•", "-").replace("’", "'").replace("‘", "'").replace("”", '"').replace("“", '"').replace("–", "-").replace("—", "-").replace("⭐", "").replace("🛡️", "").replace("✅", "").replace("⚠️", "")
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf_report(patient_data, bmi, ml_prediction, explainer_text, unicef_text, audit_text):
    """Generates a downloadable clinical PDF report."""
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", style="B", size=15)
    pdf.cell(200, 10, txt="Pediatric Nutritional Triage & Intervention Report", ln=True, align='C')
    pdf.set_font("Arial", style="I", size=10)
    pdf.cell(200, 10, txt=f"System: Neuro-Symbolic AI Framework | Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.ln(5)
    
    # Patient Context & Metrics
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="1. Patient Demographics & Context:", ln=True)
    pdf.set_font("Arial", size=11)
    for key, value in patient_data.items():
        pdf.cell(200, 8, txt=f"   - {key}: {value}", ln=True)
    pdf.cell(200, 8, txt=f"   - Calculated BMI: {bmi:.2f}", ln=True)
        
    pdf.ln(5)
    
    # ML Diagnosis
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt=f"2. Deterministic ML Diagnosis: {ml_prediction.upper()}", ln=True)
    
    pdf.ln(5)
    
    # AI Clinical Analysis
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="3. AI Clinical Analysis (Explainer Agent):", ln=True)
    pdf.set_font("Arial", size=11)
    safe_explainer_text = sanitize_for_pdf(explainer_text)
    pdf.multi_cell(0, 8, txt=safe_explainer_text)
    
    pdf.ln(5)
    
    # Cost-Constrained Guidelines
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="4. Socio-Economically Constrained Intervention:", ln=True)
    pdf.set_font("Arial", size=11)
    safe_unicef_text = sanitize_for_pdf(unicef_text)
    pdf.multi_cell(0, 8, txt=safe_unicef_text)

    pdf.ln(5)
    
    # Safety Audit
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="5. CMO Guardrail Safety Audit:", ln=True)
    pdf.set_font("Arial", size=11)
    safe_audit_text = sanitize_for_pdf(audit_text)
    pdf.multi_cell(0, 8, txt=safe_audit_text)
    
    return bytes(pdf.output())
