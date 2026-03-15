import streamlit as st
import json
import numpy as np
from dotenv import load_dotenv

# Import modularized functions
from utils import generate_pdf_report

load_dotenv()

# Set up the page configuration using native Streamlit settings
st.set_page_config(page_title="Pediatric Assessment System", layout="wide")

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
st.caption("Powered by Machine Learning and Self-Auditing Agentic AI")
st.divider()

# --- PATIENT INTAKE FORM ---
st.markdown("### Patient Intake Form")
st.write("Enter the patient's anthropometric and socio-economic data for evaluation.")

with st.container(border=True):
    col_form1, col_form2, col_form3 = st.columns(3)
    
    with col_form1:
        st.markdown("**Physical Metrics**")
        age = st.number_input("Age (in years)", min_value=0, max_value=15, value=5)
        gender_input = st.selectbox("Gender", ["Male", "Female"])
        weight = st.slider("Weight (in kg)", min_value=2.0, max_value=50.0, value=16.65)
        height = st.slider("Height (in cm)", min_value=40.0, max_value=150.0, value=95.0)
        
    with col_form2:
        st.markdown("**Dietary & Environmental**")
        meals_input = st.selectbox("Consistent Regular Meals?", ["Yes", "No"])
        fruits_input = st.selectbox("Daily Vegetable/Fruit Intake?", ["Yes", "No"])
        water_input = st.selectbox("Access to Clean Drinking Water?", ["Yes", "No"])
        
    with col_form3:
        st.markdown("**Socio-Economic Context**")
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
    
    # Using a bordered container to group the metrics professionally
    with st.container(border=True):
        col_res1, col_res2, col_res3, col_res4 = st.columns(4)
        col_res1.metric("Patient Age", f"{age} Years")
        col_res2.metric("Calculated BMI (Pediatric)", f"{bmi:.1f}")
        col_res3.metric("Daily Budget Constraint", f"INR {budget}")
        
        # ML Prediction Metric
        if ml_prediction == "Healthy":
            col_res4.metric("Diagnostic Status", "Healthy")
        else:
            col_res4.metric("Diagnostic Status", f"{ml_prediction}")

    # Explicit Callout for Status
    if ml_prediction == "Healthy":
        st.success("Primary Machine Learning evaluation indicates the patient is within healthy parameters.")
    else:
        st.error(f"Primary Machine Learning evaluation detected nutritional risk: {ml_prediction.upper()}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Generative AI Execution
    with st.spinner("Executing Multi-Agent Clinical Evaluation & Safety Audit..."):
        # Explicitly injecting the calculated BMI so the Explainer Agent can reference it against the Age
        patient_dict = {
            "Age": age, "Gender": gender_input, "Weight (kg)": weight, "Height (cm)": height,
            "Calculated BMI": round(bmi, 2), 
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
            
            st.markdown("### Agentic Analysis & Interventions")
            
            # Display Agent Outputs using native bordered containers
            with st.container(border=True):
                st.markdown("**Phase 1: Clinical Analysis (Explainer Agent)**")
                st.info(explainer_msg)
            
            with st.container(border=True):
                st.markdown("**Phase 2: Socio-Economic Intervention (Policy Agent)**")
                st.write(unicef_msg)

            with st.container(border=True):
                st.markdown("**Phase 3: Medical Guardrail (Critic Agent)**")
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
    st.info("System Ready. Please complete the Patient Intake Form above and initialize the assessment.")
