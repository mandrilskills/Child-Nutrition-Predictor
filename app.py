import streamlit as st
import json
import numpy as np
from dotenv import load_dotenv

# Import modularized functions
from utils import generate_pdf_report

load_dotenv()

# Set up the page configuration
st.set_page_config(page_title="Pediatric Assessment System", layout="wide")

# --- CUSTOM CSS FOR PROFESSIONAL UI ---
st.markdown("""
<style>
    /* Import Inter font from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Apply global font */
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif !important;
    }

    /* Typography adjustments */
    h1, h2, h3 {
        color: #111827;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    h4, h5, h6 {
        color: #374151;
        font-weight: 500 !important;
    }
    p {
        color: #4B5563;
    }

    /* Style the metric cards */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #E5E7EB;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stMetricLabel"] {
        color: #6B7280;
        font-weight: 500;
        font-size: 0.875rem;
    }
    div[data-testid="stMetricValue"] {
        color: #111827;
        font-weight: 600;
    }

    /* Primary Button Styling (Enterprise Blue) */
    div.stButton > button:first-child {
        background-color: #0F52BA; /* Sapphire Blue */
        color: white;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        border-radius: 6px;
        padding: 0.6rem 1.5rem;
        border: none;
        box-shadow: 0 2px 4px rgba(15, 82, 186, 0.2);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:first-child:hover {
        background-color: #08367B;
        box-shadow: 0 4px 6px rgba(15, 82, 186, 0.3);
        transform: translateY(-1px);
    }

    /* Container adjustments */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        border-radius: 8px !important;
        border-color: #E5E7EB !important;
        background-color: #FAFAFA;
        padding: 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)
# --------------------------------------

try:
    from model_logic import score
    with open('label_encoders.json', 'r') as f:
        encoders = json.load(f)
except Exception as e:
    st.error("System Error: Ensure `model_logic.py` and `label_encoders.json` are properly generated and present in the directory.")
    st.stop()

from agent_graph import clinical_agent_app

# --- MAIN SCREEN HEADER ---
st.title("Pediatric Nutritional Assessment System")
st.markdown("##### Powered by Machine Learning and Self-Auditing Agentic AI")
st.divider()

# --- PATIENT INTAKE FORM ---
st.markdown("### Patient Intake Form")
st.markdown("Enter the patient's anthropometric and socio-economic data for evaluation.")

with st.container(border=True):
    col_form1, col_form2, col_form3 = st.columns(3)
    
    with col_form1:
        st.markdown("#### Physical Metrics")
        age = st.number_input("Age (in years)", min_value=0, max_value=15, value=5)
        gender_input = st.selectbox("Gender", ["Male", "Female"])
        weight = st.slider("Weight (in kg)", min_value=2.0, max_value=50.0, value=16.65)
        height = st.slider("Height (in cm)", min_value=40.0, max_value=150.0, value=95.0)
        
    with col_form2:
        st.markdown("#### Dietary & Environmental")
        meals_input = st.selectbox("Consistent Regular Meals?", ["Yes", "No"])
        fruits_input = st.selectbox("Daily Vegetable/Fruit Intake?", ["Yes", "No"])
        water_input = st.selectbox("Access to Clean Drinking Water?", ["Yes", "No"])
        
    with col_form3:
        st.markdown("#### Socio-Economic Context")
        region = st.text_input("Region / State", value="West Bengal")
        setting = st.selectbox("Living Setting", ["Rural", "Urban", "Peri-Urban"])
        budget = st.number_input("Daily Food Budget (INR)", min_value=10, max_value=2000, value=60)
        
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("Initialize Clinical Assessment", type="primary", use_container_width=True)

st.divider()

# --- CLINICAL DASHBOARD RESULTS ---
if analyze_btn:
    try:
        # Encode inputs for the deterministic ML model
        input_features = [
            float(age), float(encoders['Gender'][gender_input]),
            float(weight), float(height),
            float(encoders['Has_Regular_Meals'][meals_input]),
            float(encoders['Eats_Fruits_Veggies'][fruits_input]),
            float(encoders['Clean_Drinking_Water'][water_input])
        ]
        
        # ML Prediction execution
        ml_scores = score(input_features)
        predicted_index = int(np.argmax(ml_scores))
        status_map = {v: k for k, v in encoders['Nutrition_Status'].items()}
        ml_prediction = status_map[predicted_index]
        
        # Standard BMI calculation
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        
    except Exception as e:
        st.error(f"Processing Error: {e}")
        st.stop()

    # Dashboard Metrics Row
    st.markdown("### Assessment Results")
    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    col_res1.metric("Patient Age", f"{age} Years")
    col_res2.metric("Calculated BMI", f"{bmi:.1f}")
    col_res3.metric("Daily Budget Constraint", f"INR {budget}")
    
    # ML Prediction Callout
    if ml_prediction == "Healthy":
        col_res4.metric("Diagnostic Status", "Healthy")
        st.success("Primary Machine Learning evaluation indicates the patient is within healthy parameters.")
    else:
        col_res4.metric("Diagnostic Status", f"{ml_prediction}")
        st.error(f"Primary Machine Learning evaluation detected nutritional risk: {ml_prediction.upper()}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Generative AI Execution
    with st.spinner("Executing Multi-Agent Clinical Evaluation & Safety Audit..."):
        patient_dict = {
            "Age": age, "Gender": gender_input, "Weight (kg)": weight, "Height (cm)": height,
            "Regular Meals": meals_input, "Eats Veggies": fruits_input, "Clean Water": water_input,
            "Region": region, "Setting": setting, "Daily Budget (INR)": budget
        }
        
        initial_state = {
            "patient_data": patient_dict,
            "ml_prediction": ml_prediction,
            "messages": []
        }
        
        final_state = clinical_agent_app.invoke(initial_state)
        messages = final_state.get("messages", [])
        
        if len(messages) >= 3:
            explainer_msg = messages[-3].content
            unicef_msg = messages[-2].content
            audit_msg = messages[-1].content
            
            # Display Agent Outputs
            with st.container(border=True):
                st.markdown("#### Phase 1: Clinical Analysis (Explainer Agent)")
                st.write(explainer_msg)
            
            with st.container(border=True):
                st.markdown("#### Phase 2: Socio-Economic Intervention (Policy Agent)")
                st.write(unicef_msg)

            with st.container(border=True):
                st.markdown("#### Phase 3: Medical Guardrail (Critic Agent)")
                if "VERIFIED SAFE" in audit_msg.upper():
                    st.success(audit_msg)
                else:
                    st.warning(audit_msg)
            
            # Generate PDF
            pdf_bytes = generate_pdf_report(patient_dict, bmi, ml_prediction, explainer_msg, unicef_msg, audit_msg)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="Download Official Assessment Report (PDF)",
                data=pdf_bytes,
                file_name=f"Clinical_Report_{ml_prediction.lower().replace(' ', '_')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        else:
            st.error("System Failure: The Agentic framework failed to complete the required 3-tier audit process.")
else:
    # Empty State Architecture Overview
    st.info("System Ready. Please complete the Patient Intake Form above and initialize the assessment.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### System Architecture Overview")
    st.markdown("""
    This platform integrates **Machine Learning** with **Agentic AI** to provide a comprehensive public health assessment tool:
    1. **Primary Sensor (Deterministic ML):** A mathematically rigorous Machine Learning model computes the immediate nutritional risk based on anthropometric data.
    2. **Analysis Brain (Generative AI):** A network of Specialized AI Agents synthesizes hyper-local, budget-constrained interventions guided by global UNICEF standards.
    3. **Safety Guardrail (Critic Agent):** A final algorithmic pass strictly audits the generated intervention for medical safety and economic viability prior to output.
    """)
