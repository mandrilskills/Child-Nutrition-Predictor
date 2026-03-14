import streamlit as st
import json
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables (API Keys)
load_dotenv()

# Set page config
st.set_page_config(page_title="Neuro-Symbolic Nutrition AI", layout="wide")

# 1. Safely load the generated model logic and encoders
try:
    from model_logic import score
    with open('label_encoders.json', 'r') as f:
        encoders = json.load(f)
except ImportError:
    st.error("⚠️ `model_logic.py` not found. Please run `model_pipeline.ipynb` first.")
    st.stop()
except FileNotFoundError:
    st.error("⚠️ `label_encoders.json` not found. Please run `model_pipeline.ipynb` first.")
    st.stop()

# Import the LangGraph App
from agent_graph import clinical_agent_app

# --- UI LAYOUT ---
st.title("🧒 AI Pediatric Nutrition Dashboard")
st.markdown("A Neuro-Symbolic AI tool combining deterministic Machine Learning with Generative AI Agents.")

col1, col2 = st.columns([1, 2])

# --- LEFT PANEL: ML SENSOR (Deterministic) ---
with col1:
    st.header("Patient Intake")
    with st.container(border=True):
        age = st.number_input("Age (in years)", min_value=0, max_value=15, value=5)
        gender_input = st.selectbox("Gender", ["Male", "Female"])
        weight = st.slider("Weight (in kg)", 2.0, 50.0, 14.0)
        height = st.slider("Height (in cm)", 40.0, 150.0, 95.0)
        meals_input = st.selectbox("Has Regular Meals?", ["Yes", "No"])
        fruits_input = st.selectbox("Eats Fruits/Vegetables Daily?", ["Yes", "No"])
        water_input = st.selectbox("Access to Clean Drinking Water?", ["Yes", "No"])
        
        analyze_btn = st.button("Run Clinical Analysis", type="primary", use_container_width=True)

# --- RIGHT PANEL: AGENTIC DASHBOARD (Generative) ---
with col2:
    st.header("AI Clinical Report")
    
    if analyze_btn:
        # 2. Encode inputs for the model
        try:
            # Match the exact column order from the dataframe
            input_features = [
                float(age),
                float(encoders['Gender'][gender_input]),
                float(weight),
                float(height),
                float(encoders['Has_Regular_Meals'][meals_input]),
                float(encoders['Eats_Fruits_Veggies'][fruits_input]),
                float(encoders['Clean_Drinking_Water'][water_input])
            ]
            
            # 3. Get deterministic prediction from m2cgen code
            ml_scores = score(input_features)
            predicted_index = int(np.argmax(ml_scores))
            
            # Reverse lookup the label string from the JSON mapping
            status_map = {v: k for k, v in encoders['Nutrition_Status'].items()}
            ml_prediction = status_map[predicted_index]
            
        except Exception as e:
            st.error(f"Error processing inputs: {e}")
            st.stop()

        # 4. Display ML Result
        if ml_prediction == "Healthy":
            st.success(f"**ML Sensor Prediction:** {ml_prediction} ✅")
            st.info("No further agentic intervention required.")
        else:
            st.error(f"**ML Sensor Prediction:** {ml_prediction} ⚠️")
            
            # 5. Trigger LangGraph Agents
            with st.spinner("Initializing AI Multi-Agent Panel..."):
                patient_dict = {
                    "Age": age, "Gender": gender_input, "Weight": weight, "Height": height,
                    "Regular Meals": meals_input, "Eats Veggies": fruits_input, "Clean Water": water_input
                }
                
                # Setup the initial state for LangGraph
                initial_state = {
                    "patient_data": patient_dict,
                    "ml_prediction": ml_prediction,
                    "messages": []
                }
                
                # Execute the graph
                final_state = clinical_agent_app.invoke(initial_state)
                
                # 6. Display Agent Outputs
                # The graph appended two messages: [Explainer Message, Dietitian Message]
                messages = final_state.get("messages", [])
                
                if len(messages) >= 2:
                    st.subheader("👨‍⚕️ Clinical Explainer Agent")
                    st.info(messages[-2].content)
                    
                    st.subheader("🥗 Dietitian Agent")
                    st.success(messages[-1].content)
                else:
                    st.warning("Agents did not return the expected report. Check API keys and graph logic.")
    else:
        st.write("Enter patient data on the left and click **Run Clinical Analysis** to begin.")
