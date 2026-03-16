import streamlit as st
import json
import numpy as np
from dotenv import load_dotenv

# Import modularized functions
from utils import generate_pdf_report, get_ideal_metrics

load_dotenv()

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
st.caption("Powered by Machine Learning and AI Insights")
st.divider()

# --- PATIENT INTAKE FORM ---
st.markdown("### Patient Intake Form")
st.write("Enter the patient's anthropometric and socio-economic data for evaluation.")

# Explicit Accuracy Warning
st.warning("**Clinical Advisory:** Please ensure all provided values are strictly accurate. Providing inaccurate physical, dietary, or environmental inputs will result in false predictions and invalid clinical interventions.")

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
        zone = st.text_input("Zone (e.g., North, South, East, West)", value="East")
        setting = st.selectbox("Living Setting", ["Rural", "Urban", "Peri-Urban"])
        season = st.selectbox("Current Season", ["Summer", "Winter", "Monsoon"])
        budget = st.number_input("Daily Food Budget (INR)", min_value=10, max_value=2000, value=60)
        
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("Initialize Clinical Assessment", type="primary", use_container_width=True)

st.divider()

# --- CLINICAL DASHBOARD RESULTS ---
if analyze_btn:
    try:
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
        
        # Actual Calculations
        height_m = height / 100
        actual_bmi = weight / (height_m ** 2)

        # Ideal (WHO) Calculations
        ideal_weight, ideal_height = get_ideal_metrics(age, gender_input)
        ideal_bmi = ideal_weight / ((ideal_height / 100) ** 2)

        # Variances
        weight_variance = weight - ideal_weight
        height_variance = height - ideal_height
        bmi_variance = actual_bmi - ideal_bmi
        
    except Exception as e:
        st.error(f"Processing Error: {e}")
        st.stop()

    # --- COMPARATIVE DASHBOARD METRICS ---
    st.markdown("### Comparative Anthropometric Results")
    st.caption("Measurements compared against WHO median ideals for age and gender.")
    
    with st.container(border=True):
        col_res1, col_res2, col_res3, col_res4 = st.columns(4)
        
        # Streamlit metric UI
        col_res1.metric("Weight (kg)", f"{weight:.1f}", f"{weight_variance:+.1f} from ideal", delta_color="inverse")
        col_res2.metric("Height (cm)", f"{height:.1f}", f"{height_variance:+.1f} from ideal", delta_color="inverse")
        col_res3.metric("Calculated BMI", f"{actual_bmi:.1f}", f"{bmi_variance:+.1f} from ideal", delta_color="inverse")
        
        if ml_prediction == "Healthy":
            col_res4.metric("Diagnostic Status", "Healthy")
        else:
            col_res4.metric("Diagnostic Status", f"{ml_prediction}")

    if ml_prediction == "Healthy":
        st.success("Primary Machine Learning evaluation indicates the patient is within healthy parameters.")
    else:
        st.error(f"Primary Machine Learning evaluation detected nutritional risk: {ml_prediction.upper()}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Generative AI Execution
    with st.spinner("Generating Dietary Insights & Precautions..."):
        
        # Package data including new Zone and Season variables
        patient_dict = {
            "Age": age, "Gender": gender_input, 
            "Actual Weight": f"{weight} kg (Ideal: {ideal_weight})",
            "Actual Height": f"{height} cm (Ideal: {ideal_height})",
            "Calculated BMI": f"{actual_bmi:.1f} (Ideal: {ideal_bmi:.1f})", 
            "Regular Meals": meals_input, "Eats Veggies": fruits_input, "Clean Water": water_input,
            "Region": region, "Zone": zone, "Setting": setting, "Season": season, "Daily Budget (INR)": budget
        }
        
        comparative_table_data = [
            {"Metric": "Weight (kg)", "Actual": f"{weight:.1f}", "Ideal": f"{ideal_weight:.1f}", "Variance": f"{weight_variance:+.1f}"},
            {"Metric": "Height (cm)", "Actual": f"{height:.1f}", "Ideal": f"{ideal_height:.1f}", "Variance": f"{height_variance:+.1f}"},
            {"Metric": "BMI", "Actual": f"{actual_bmi:.1f}", "Ideal": f"{ideal_bmi:.1f}", "Variance": f"{bmi_variance:+.1f}"}
        ]

        initial_state = {
            "patient_data": patient_dict,
            "ml_prediction": ml_prediction,
            "messages": []
        }
        
        final_state = clinical_agent_app.invoke(initial_state)
        messages = final_state.get("messages", [])
        
        # Check for 2 messages instead of 3 since we removed the CMO critic
        if len(messages) >= 2:
            explainer_msg = messages[-2].content
            unicef_msg = messages[-1].content
            
            st.markdown("### Analysis & Interventions")
            
            # Display Outputs with common names
            with st.container(border=True):
                st.markdown("**Phase 1: Clinical Analysis**")
                st.info(explainer_msg)
            
            with st.container(border=True):
                st.markdown("**Phase 2: Dietary Intervention & Precautions**")
                st.write(unicef_msg)
                
            # Doctor Intervention UI Disclaimer
            st.error("**DOCTOR INTERVENTION REQUIRED:** This system provides initial dietary insights and precautions based on socio-economic constraints. It does NOT replace professional medical diagnosis. A thorough evaluation by a qualified pediatrician is strictly required.")
            
            # Generate PDF 
            pdf_bytes = generate_pdf_report(patient_dict, comparative_table_data, ml_prediction, explainer_msg, unicef_msg)
            
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
            st.error("System Failure: The Agentic framework failed to complete the analysis.")
else:
    # Empty State Instructions
    st.info("System Ready. Please complete the Patient Intake Form above and initialize the assessment.")
