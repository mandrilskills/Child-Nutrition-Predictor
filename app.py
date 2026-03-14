import streamlit as st
import json
import numpy as np
from dotenv import load_dotenv

# Import modularized functions
from utils import generate_pdf_report

load_dotenv()
st.set_page_config(page_title="Neuro-Symbolic Pediatric Triage", layout="wide", page_icon="🏥")

try:
    from model_logic import score
    with open('label_encoders.json', 'r') as f:
        encoders = json.load(f)
except Exception as e:
    st.error("⚠️ Ensure `model_logic.py` and `label_encoders.json` are properly generated and present.")
    st.stop()

from agent_graph import clinical_agent_app

# --- SIDEBAR: PATIENT INTAKE ---
with st.sidebar:
    st.title("🏥 Patient Intake")
    st.markdown("Enter anthropometric and socio-economic data.")
    
    st.subheader("1. Physical Metrics")
    age = st.number_input("Age (in years)", 0, 15, 5)
    gender_input = st.selectbox("Gender", ["Male", "Female"])
    weight = st.slider("Weight (in kg)", 2.0, 50.0, 16.65)
    height = st.slider("Height (in cm)", 40.0, 150.0, 95.0)
    
    st.subheader("2. Dietary & WASH Indicators")
    meals_input = st.selectbox("Has Regular Meals?", ["Yes", "No"])
    fruits_input = st.selectbox("Eats Fruits/Vegetables Daily?", ["Yes", "No"])
    water_input = st.selectbox("Access to Clean Drinking Water?", ["Yes", "No"])
    
    st.subheader("3. Socio-Economic Context")
    region = st.text_input("Region / State", value="West Bengal")
    setting = st.selectbox("Living Setting", ["Rural", "Urban", "Peri-Urban"])
    budget = st.number_input("Daily Food Budget (INR)", min_value=10, max_value=2000, value=60)
    
    st.divider()
    analyze_btn = st.button("🚀 Execute Neuro-Symbolic Triage", type="primary", use_container_width=True)

# --- MAIN SCREEN: CLINICAL DASHBOARD ---
st.title("Neuro-Symbolic Pediatric Nutritional Triage System")
st.markdown("##### A Geo-Culturally Responsive & Self-Auditing AI Framework")
st.divider()

if analyze_btn:
    try:
        # Encode inputs
        input_features = [
            float(age), float(encoders['Gender'][gender_input]),
            float(weight), float(height),
            float(encoders['Has_Regular_Meals'][meals_input]),
            float(encoders['Eats_Fruits_Veggies'][fruits_input]),
            float(encoders['Clean_Drinking_Water'][water_input])
        ]
        
        # Deterministic ML Prediction
        ml_scores = score(input_features)
        predicted_index = int(np.argmax(ml_scores))
        status_map = {v: k for k, v in encoders['Nutrition_Status'].items()}
        ml_prediction = status_map[predicted_index]
        
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        
    except Exception as e:
        st.error(f"Error processing inputs: {e}")
        st.stop()

    # Dashboard Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Patient Age", f"{age} yrs")
    col2.metric("Calculated BMI", f"{bmi:.1f}")
    col3.metric("Daily Budget", f"₹ {budget}")
    
    # Highlight the ML Prediction heavily
    if ml_prediction == "Healthy":
        col4.metric("Diagnostic Status", "Healthy ✅")
        st.success("Primary ML Sensor confirms patient is within healthy parameters.")
    else:
        col4.metric("Diagnostic Status", f"{ml_prediction} ⚠️")
        st.error(f"Primary ML Sensor detected nutritional risk: **{ml_prediction}**")

    st.divider()

    # Generative AI Execution
    with st.spinner("Initializing Multi-Agent Clinical Evaluation & Safety Audit..."):
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
            
            # Display Agent Outputs in Clean Containers
            with st.container(border=True):
                st.markdown("### 🧠 Phase 1: Clinical Analysis (Explainer Agent)")
                st.write(explainer_msg)
            
            with st.container(border=True):
                st.markdown("### 🌍 Phase 2: Socio-Economic Intervention (Policy Agent)")
                st.write(unicef_msg)

            with st.container(border=True):
                st.markdown("### 🛡️ Phase 3: Medical Guardrail (CMO Critic Agent)")
                if "VERIFIED SAFE" in audit_msg.upper():
                    st.success(audit_msg)
                else:
                    st.warning(audit_msg)
            
            # Generate PDF
            pdf_bytes = generate_pdf_report(patient_dict, bmi, ml_prediction, explainer_msg, unicef_msg, audit_msg)
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="📥 Download Official Triage Report (PDF)",
                data=pdf_bytes,
                file_name=f"Triage_Report_{ml_prediction.lower().replace(' ', '_')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        else:
            st.error("Agentic framework failed to complete the 3-tier audit process.")
else:
    # Empty State Instructions
    st.info("👈 Please enter the patient's anthropometric and socio-economic details in the sidebar and click **Execute Neuro-Symbolic Triage**.")
    
    # Architecture Overview for the UI
    st.markdown("### ⚙️ System Architecture")
    st.markdown("""
    This system utilizes a **Neuro-Symbolic** approach to public health:
    1. **Sensor (Deterministic ML):** A mathematically rigorous Decision Tree model calculates the immediate nutritional risk.
    2. **Brain (Generative AI):** LangGraph agents synthesize hyper-local, budget-constrained interventions based on global UNICEF guidelines.
    3. **Immune System (Critic Agent):** A final LLM pass strictly audits the intervention for medical safety and economic viability before outputting the report.
    """)
