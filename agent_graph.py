import asyncio
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

# --- ASYNCIO EVENT LOOP FIX FOR STREAMLIT ---
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

class ClinicalState(TypedDict):
    patient_data: dict      
    ml_prediction: str      
    messages: Annotated[Sequence[BaseMessage], operator.add] 

def clinical_explainer(state: ClinicalState):
    """Explains the ML prediction based on physical data and BMI-for-Age using simple language."""
    prompt = HumanMessage(
        content=f"Act as a helpful health assistant. The system predicted the child's status is '{state['ml_prediction']}'. "
                f"Analyze this patient data: {state['patient_data']}. "
                f"You must evaluate their 'Calculated BMI' against their 'Age' based on WHO guidelines. "
                f"Write a 3-sentence explanation of why the child received this prediction. "
                f"CRITICAL: Use very simple, everyday English. Avoid heavy medical jargon. Explain it so any common person can understand clearly."
    )
    response = llm.invoke([prompt])
    return {"messages": [response]}

def unicef_guideline_agent(state: ClinicalState):
    """Provides geo-culturally aware, budget-constrained interventions with built-in safety precautions."""
    data = state['patient_data']
    budget = data.get('Daily Budget (INR)', 'unspecified')
    region = data.get('Region', 'their local region')
    district = data.get('District', 'their local district')
    setting = data.get('Setting', 'standard')
    season = data.get('Season', 'current')
    diet_pref = data.get('Dietary Preference', 'None')
    market_shocks = data.get('Market Shocks', 'None')
    
    prompt = HumanMessage(
        content=f"Act as a helpful public health nutritionist. The child is classified as '{state['ml_prediction']}' with these stats: {data}. "
                f"\n\nCRITICAL CONSTRAINTS:"
                f"\n1. Budget: All dietary recommendations MUST be strictly affordable within a daily food budget of {budget} INR."
                f"\n2. Geography & Season: Only recommend hyper-local foods native to the {district} district of {region}, specifically suitable for the {season} season in a {setting} setting."
                f"\n3. Dietary Restrictions: The patient's diet is strictly '{diet_pref}'. Do NOT recommend any foods that violate this restriction."
                f"\n4. Market Shocks: The following foods are currently too expensive or unavailable: '{market_shocks}'. DO NOT recommend them. Suggest affordable local alternatives."
                f"\n5. Format: You MUST be extremely concise. Use SHORT BULLET POINTS only. Do NOT write long paragraphs. Keep explanations to 1-2 lines per bullet."
                f"\n6. Language: Use very simple, precise, and jargon-free English."
                f"\n7. Safety & Precautions: You MUST embed short, practical precautions inside the bullet points (e.g., 'mash well to avoid choking', 'boil water properly', 'substitute with...')."
                f"\n\nINSTRUCTIONS:"
                f"\nProvide exactly 3 to 4 specific, actionable, and ultra-short bulleted dietary steps."
    )
    response = llm.invoke([prompt]) 
    return {"messages": [response]}

# Build the Graph (2-Tier Architecture now)
workflow = StateGraph(ClinicalState)
workflow.add_node("explainer", clinical_explainer)
workflow.add_node("unicef_agent", unicef_guideline_agent)

# Linear execution 
workflow.set_entry_point("explainer")
workflow.add_edge("explainer", "unicef_agent")
workflow.add_edge("unicef_agent", END)

clinical_agent_app = workflow.compile()
