import streamlit as st
import json
import numpy as np
import os
from dotenv import load_dotenv
from fpdf import FPDF

# Load environment variables
load_dotenv()
st.set_page_config(page_title="Neuro-Symbolic Nutrition AI", layout="wide")

try:
    from model_logic import score
    with open('label_encoders.json', 'r') as f:
        encoders = json.load(f)
except Exception as e:
    st.error("⚠️ Ensure `model_logic.py` and `label_encoders.json` are present.")
    st.stop()

from agent_graph import clinical_agent_app

# --- PDF GENERATOR HELPER ---
def generate_pdf_report(patient_data, ml_prediction, explainer_text, unicef_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Clinical Pediatric Nutrition Report", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Patient Profile:", ln=True)
    pdf.set_font("Arial", size=12)
    for key, value in patient_data.items():
        pdf.cell(200, 8, txt=f"{key}: {value}", ln=True)
        
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt=f"Diagnostic Status: {ml_prediction.upper()}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Clinical AI Analysis:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, txt=explainer_text)
    
    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="UNICEF Aligned Intervention Measures:", ln=True)
    pdf.set_font("Arial", size=11)
    # Ensure unicode characters (like bullets) don't break the PDF
    safe_unicef_text = unicef_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, txt=safe_unicef_text)
    
    # Output to a byte string
    return pdf.output(dest='S').encode('latin-1')

# --- UI LAYOUT ---
st.title("🧒 AI Pediatric Nutrition Dashboard")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Patient Intake")
    with st.container(border=True):
        age = st.number_input("Age (in years)", 0, 15, 5)
        gender_input = st.selectbox("Gender", ["Male", "Female"])
        weight = st.slider("Weight (in kg)", 2.0, 50.0, 14.0)
        height = st.slider("Height (in cm)", 40.0, 150.0, 95.0)
        meals_input = st.selectbox("Has Regular Meals?", ["Yes", "No"])
        fruits_input = st.selectbox("Eats Fruits/Vegetables Daily?", ["Yes", "No"])
        water_input = st.selectbox("Access to Clean Drinking Water?", ["Yes", "No"])
        
        analyze_btn = st.button("Run Clinical Analysis", type="primary", use_container_width=True)

with col2:
    st.header("AI Clinical Report")
    
    if analyze_btn:
        try:
            input_features = [
                float(age), float(encoders['Gender'][gender_input]),
                float(weight), float(height),
                float(encoders['Has_Regular_Meals'][meals_input]),
                float(encoders['Eats_Fruits_Veggies'][fruits_input]),
                float(encoders['Clean_Drinking_Water'][water_input])
            ]
            ml_scores = score(input_features)
            predicted_index = int(np.argmax(ml_scores))
            status_map = {v: k for k, v in encoders['Nutrition_Status'].items()}
            ml_prediction = status_map[predicted_index]
            
        except Exception as e:
            st.error(f"Error processing inputs: {e}")
            st.stop()

        if ml_prediction == "Healthy":
            st.success(f"**ML Sensor Prediction:** {ml_prediction} ✅")
            st.info("Patient is healthy. No intervention required.")
        else:
            st.error(f"**ML Sensor Prediction:** {ml_prediction} ⚠️")
            
            with st.spinner("Compiling UNICEF Intervention Report..."):
                patient_dict = {
                    "Age": age, "Gender": gender_input, "Weight": weight, "Height": height,
                    "Regular Meals": meals_input, "Eats Veggies": fruits_input, "Clean Water": water_input
                }
                
                initial_state = {
                    "patient_data": patient_dict,
                    "ml_prediction": ml_prediction,
                    "messages": []
                }
                
                final_state = clinical_agent_app.invoke(initial_state)
                messages = final_state.get("messages", [])
                
                if len(messages) >= 2:
                    explainer_msg = messages[-2].content
                    unicef_msg = messages[-1].content
                    
                    st.subheader("👨‍⚕️ Clinical Analysis")
                    st.info(explainer_msg)
                    
                    st.subheader("🌐 UNICEF Intervention Plan")
                    st.success(unicef_msg)
                    
                    # Generate the PDF
                    pdf_bytes = generate_pdf_report(patient_dict, ml_prediction, explainer_msg, unicef_msg)
                    
                    st.download_button(
                        label="📄 Download Official Clinical Report (PDF)",
                        data=pdf_bytes,
                        file_name="pediatric_nutrition_report.pdf",
                        mime="application/pdf",
                        type="primary"
                    )
                else:
                    st.warning("Failed to generate complete report.")
    else:
        st.write("Enter patient data to begin.")
