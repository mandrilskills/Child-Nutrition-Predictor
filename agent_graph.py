import asyncio
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

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
    """Explains the ML prediction based on the data."""
    prompt = HumanMessage(
        content=f"Act as a pediatric clinical AI. The ML model predicted the child is '{state['ml_prediction']}'. "
                f"Analyze this patient data: {state['patient_data']}. Explain briefly (2-3 sentences) why this prediction makes sense. "
                f"If the child is Healthy, explain what lifestyle factors are contributing to this positive outcome."
    )
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
                f"\n2. Geography: Only recommend indigenous, hyper-local, and easily accessible foods native to {region} in a {setting} setting. Do NOT suggest expensive, westernized, or imported items."
                f"\n\nINSTRUCTIONS:"
                f"\nIf 'At Risk' or 'Malnourished': Provide 3-4 specific, actionable measures to overcome this (e.g., WASH guidelines, and localized cost-effective RUTF alternatives). "
                f"\nIf 'Healthy': Provide 3 preventative care guidelines and budget-friendly local dietary maintenance tips. "
                f"\nKeep it professional, bulleted, and formatted for a clinical medical report."
    )
    response = llm.invoke(list(state["messages"]) + [prompt]) 
    return {"messages": [response]}

workflow = StateGraph(ClinicalState)
workflow.add_node("explainer", clinical_explainer)
workflow.add_node("unicef_agent", unicef_guideline_agent)

workflow.set_entry_point("explainer")
workflow.add_edge("explainer", "unicef_agent")
workflow.add_edge("unicef_agent", END)

clinical_agent_app = workflow.compile()
