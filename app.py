import streamlit as st
import json
import numpy as np
from dotenv import load_dotenv

# Import modularized functions
from utils import generate_pdf_report

load_dotenv()

# Set up the page configuration without any emojis
st.set_page_config(page_title="Pediatric Assessment System", layout="wide")

try:
    from model_logic import score
    with open('label_encoders.json', 'r') as f:
        encoders = json.load(f)
except Exception as e:
    st.error("System Error: Ensure `model_logic.py` and `label_encoders.json` are properly generated and present in the directory.")
    st.stop()

from agent_graph import clinical_agent_app

# --- SIDEBAR: PATIENT INTAKE ---
with st.sidebar:
    st.title("Patient Intake Form")
    st.markdown("Enter the patient's anthropometric and socio-economic data for evaluation.")
    st.divider()
    
    st.subheader("Physical Metrics")
    age = st.number_input("Age (in years)", min_value=0, max_value=15, value=5)
    gender_input = st.selectbox("Gender", ["Male", "Female"])
    weight = st.slider("Weight (in kg)", min_value=2.0, max_value=50.0, value=16.65)
    height = st.slider("Height (in cm)", min_value=40.0, max_value=150.0, value=95.0)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Dietary & Environmental Factors")
    meals_input = st.selectbox("Consistent Regular Meals?", ["Yes", "No"])
    fruits_input = st.selectbox("Daily Vegetable/Fruit Intake?", ["Yes", "No"])
    water_input = st.selectbox("Access to Clean Drinking Water?", ["Yes", "No"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Socio-Economic Context")
    region = st.text_input("Region / State", value="West Bengal")
    setting = st.selectbox("Living Setting", ["Rural", "Urban", "Peri-Urban"])
    budget = st.number_input("Daily Food Budget (INR)", min_value=10, max_value=2000, value=60)
    
    st.divider()
    analyze_btn = st.button("Initialize Clinical Assessment", type="primary", use_container_width=True)

# --- MAIN SCREEN: CLINICAL DASHBOARD ---
st.title("Pediatric Nutritional Assessment System")
st.markdown("##### Powered by Machine Learning and Self-Auditing Agentic AI")
st.divider()

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
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Patient Age", f"{age} Years")
    col2.metric("Calculated BMI", f"{bmi:.1f}")
    col3.metric("Daily Budget Constraint", f"INR {budget}")
    
    # ML Prediction Callout
    if ml_prediction == "Healthy":
        col4.metric("Diagnostic Status", "Healthy")
        st.success("Primary Machine Learning evaluation indicates the patient is within healthy parameters.")
    else:
        col4.metric("Diagnostic Status", f"{ml_prediction}")
        st.error(f"Primary Machine Learning evaluation detected nutritional risk: {ml_prediction.upper()}")

    st.divider()

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
            
            # Display Agent Outputs in Clinical-Style Containers
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
    # Empty State Instructions
    st.info("System Ready. Please complete the Patient Intake Form in the sidebar and initialize the assessment.")
    
    # Architecture Overview
    st.markdown("### System Architecture Overview")
    st.markdown("""
    This platform integrates **Machine Learning** with **Agentic AI** to provide a comprehensive public health assessment tool:
    1. **Primary Sensor (Deterministic ML):** A mathematically rigorous Machine Learning model computes the immediate nutritional risk based on anthropometric data.
    2. **Analysis Brain (Generative AI):** A network of Specialized AI Agents synthesizes hyper-local, budget-constrained interventions guided by global UNICEF standards.
    3. **Safety Guardrail (Critic Agent):** A final algorithmic pass strictly audits the generated intervention for medical safety and economic viability prior to output.
    """)
