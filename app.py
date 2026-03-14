import streamlit as st
import json
import numpy as np
from dotenv import load_dotenv

# Import our modularized functions
from utils import generate_pdf_report

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

# --- UI LAYOUT ---
st.title("🧒 AI Pediatric Nutrition Dashboard")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Patient Intake")
    with st.container(border=True):
        age = st.number_input("Age (in years)", 0, 15, 5)
        gender_input = st.selectbox("Gender", ["Male", "Female"])
        weight = st.slider("Weight (in kg)", 2.0, 50.0, 16.65)
        height = st.slider("Height (in cm)", 40.0, 150.0, 95.0)
        meals_input = st.selectbox("Has Regular Meals?", ["Yes", "No"])
        fruits_input = st.selectbox("Eats Fruits/Vegetables Daily?", ["Yes", "No"])
        water_input = st.selectbox("Access to Clean Drinking Water?", ["Yes", "No"])
        
        analyze_btn = st.button("Run Clinical Analysis & Generate Report", type="primary", use_container_width=True)

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
            
            # Calculate BMI for the report
            height_m = height / 100
            bmi = weight / (height_m ** 2)
            
        except Exception as e:
            st.error(f"Error processing inputs: {e}")
            st.stop()

        # Display UI Status
        if ml_prediction == "Healthy":
            st.success(f"**ML Sensor Prediction:** {ml_prediction} ✅")
        else:
            st.error(f"**ML Sensor Prediction:** {ml_prediction} ⚠️")
            
        with st.spinner("Compiling Comprehensive Clinical Report (PDF)..."):
            patient_dict = {
                "Age": age, "Gender": gender_input, "Weight (kg)": weight, "Height (cm)": height,
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
                
                st.subheader("🌐 Preventative Care & UNICEF Guidelines")
                st.success(unicef_msg)
                
                # Generate and offer PDF Download using the utils function
                pdf_bytes = generate_pdf_report(patient_dict, bmi, ml_prediction, explainer_msg, unicef_msg)
                
                st.download_button(
                    label="📄 Download Official Clinical Report (PDF)",
                    data=pdf_bytes,
                    file_name=f"clinical_report_{ml_prediction.lower().replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
            else:
                st.warning("Failed to generate complete report.")
    else:
        st.write("Enter patient data to begin the assessment and generate a downloadable report.")
