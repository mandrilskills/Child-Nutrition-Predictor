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
    """Explains the ML prediction based on the physical data."""
    prompt = HumanMessage(
        content=f"Act as a pediatric clinical AI. The ML model predicted the child is '{state['ml_prediction']}'. "
                f"Analyze this patient data: {state['patient_data']}. Explain briefly (2-3 sentences) why this prediction makes sense. "
                f"If the child is Healthy, explain what lifestyle factors are contributing to this positive outcome."
    )
    # 1. Invoke fresh to avoid Gemini Role Errors
    response = llm.invoke([prompt])
    return {"messages": [response]}

def unicef_guideline_agent(state: ClinicalState):
    """Provides geo-culturally aware and budget-constrained interventions."""
    data = state['patient_data']
    budget = data.get('Daily Budget (INR)', 'unspecified')
    region = data.get('Region', 'their local region')
    setting = data.get('Setting', 'standard')
    
    prompt = HumanMessage(
        content=f"Act as a public health economist and UNICEF pediatric expert. "
                f"The child is classified as '{state['ml_prediction']}' with these stats: {data}. "
                f"\n\nCRITICAL CONSTRAINTS:"
                f"\n1. Budget: All dietary recommendations MUST be strictly affordable within a daily food budget of {budget} INR."
                f"\n2. Geography: Only recommend indigenous, hyper-local foods native to {region} in a {setting} setting."
                f"\n\nINSTRUCTIONS:"
                f"\nProvide 3-4 specific, actionable measures. Keep it professional, bulleted, and highly concise."
    )
    # 2. Invoke fresh without appending the previous AIMessage
    response = llm.invoke([prompt]) 
    return {"messages": [response]}

def safety_critic_agent(state: ClinicalState):
    """Acts as the Chief Medical Officer to audit the AI's own recommendations."""
    data = state['patient_data']
    budget = data.get('Daily Budget (INR)', 'unspecified')
    
    # Extract the actual text plan from the previous UNICEF agent
    intervention_plan = state["messages"][-1].content if state["messages"] else "No plan provided."
    
    prompt = HumanMessage(
        content=f"Act as a strict Chief Medical Safety Officer. Review the following dietary intervention plan generated for a {data['Age']}-year-old child:\n\n"
                f"--- PROPOSED PLAN ---\n{intervention_plan}\n---------------------\n\n"
                f"Perform a strict clinical audit:"
                f"\n1. Are there any choking hazards, allergens, or age-inappropriate foods?"
                f"\n2. Does this realistically fit within a strict daily budget of {budget} INR in {data.get('Region', 'India')}?"
                f"\nProvide a 2-sentence 'Safety Audit Justification' followed by a final 'STATUS: VERIFIED SAFE' or 'STATUS: FLAGGED - REQUIRES HUMAN DOCTOR REVIEW'."
    )
    # 3. Invoke fresh with the injected plan
    response = llm.invoke([prompt]) 
    return {"messages": [response]}

# Build the Graph
workflow = StateGraph(ClinicalState)
workflow.add_node("explainer", clinical_explainer)
workflow.add_node("unicef_agent", unicef_guideline_agent)
workflow.add_node("safety_critic", safety_critic_agent)

# Linear execution with the safety guardrail
workflow.set_entry_point("explainer")
workflow.add_edge("explainer", "unicef_agent")
workflow.add_edge("unicef_agent", "safety_critic")
workflow.add_edge("safety_critic", END)

clinical_agent_app = workflow.compile()
