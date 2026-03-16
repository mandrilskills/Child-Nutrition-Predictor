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
    """Explains the ML prediction based on physical data and BMI-for-Age."""
    prompt = HumanMessage(
        content=f"Act as a helpful pediatric assistant. The system predicted the child's status is '{state['ml_prediction']}'. "
                f"Analyze this patient data: {state['patient_data']}. "
                f"CRITICAL: Evaluate their 'Calculated BMI' against their 'Age' using standard WHO pediatric guidelines. "
                f"Write a 3-sentence explanation of why the system gave this result. Use very simple, jargon-free everyday English so a common person can understand."
    )
    response = llm.invoke([prompt])
    return {"messages": [response]}

def unicef_guideline_agent(state: ClinicalState):
    """Provides geo-culturally aware, budget-constrained, and safe interventions."""
    data = state['patient_data']
    budget = data.get('Daily Budget (INR)', 'unspecified')
    region = data.get('Region', 'their local region')
    zone = data.get('Zone', '')
    season = data.get('Season', 'current season')
    setting = data.get('Setting', 'standard')
    
    prompt = HumanMessage(
        content=f"Act as a practical public health nutritionist. The child is classified as '{state['ml_prediction']}' with these stats: {data}. "
                f"\n\nCONTEXT:"
                f"\n1. Budget: Daily food budget of {budget} INR."
                f"\n2. Environment: {zone}, {region} ({setting} setting). Season: {season}."
                f"\n\nINSTRUCTIONS:"
                f"\n- Provide 3-4 specific, actionable, and hyper-local dietary measures using seasonal and affordable ingredients."
                f"\n- CRITICAL: Explain *why* these foods help in simple, easy-to-understand everyday language (NO medical jargon)."
                f"\n- CRITICAL SAFETY: Include preparation precautions directly in the suggestions (e.g., 'mash well to avoid choking', 'boil lentils thoroughly for easier digestion')."
                f"\n- Note if the budget is highly restrictive, but provide the best possible options within it."
                f"\n- Conclude the response with a bold note stating: '**Doctor intervention is required for a formal clinical diagnosis and treatment plan.**'"
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
