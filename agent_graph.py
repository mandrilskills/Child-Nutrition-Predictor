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
# --------------------------------------------

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

class ClinicalState(TypedDict):
    patient_data: dict      
    ml_prediction: str      
    messages: Annotated[Sequence[BaseMessage], operator.add] 

def clinical_explainer(state: ClinicalState):
    """Explains the ML prediction based on the data."""
    # CHANGED: Using HumanMessage instead of SystemMessage to satisfy Gemini's payload requirements
    prompt = HumanMessage(
        content=f"Act as a pediatric clinical AI. The ML model predicted the child is '{state['ml_prediction']}'. "
                f"Analyze this patient data: {state['patient_data']}. Explain briefly (2-3 sentences) why this prediction makes sense. "
                f"If the child is Healthy, explain what lifestyle factors are contributing to this positive outcome."
    )
    response = llm.invoke([prompt])
    return {"messages": [response]}

def unicef_guideline_agent(state: ClinicalState):
    """Provides UNICEF-aligned interventions or preventative care based on status."""
    # CHANGED: Using HumanMessage instead of SystemMessage
    prompt = HumanMessage(
        content=f"Act as a public health expert specialized in UNICEF pediatric guidelines. "
                f"The child is classified as '{state['ml_prediction']}' with these stats: {state['patient_data']}. "
                f"If 'At Risk' or 'Malnourished': Provide 3-4 specific, actionable measures to overcome this (e.g., WASH guidelines, RUTFs). "
                f"If 'Healthy': Provide 3 preventative care guidelines, dietary recommendations, and developmental milestones to maintain their health. "
                f"Keep it professional, bulleted, and formatted for a clinical medical report."
    )
    
    # We append the new HumanMessage to the existing conversation history
    # Converting state["messages"] to a list ensures clean concatenation
    response = llm.invoke(list(state["messages"]) + [prompt]) 
    return {"messages": [response]}

# Build the Graph (Linear execution for all patients now)
workflow = StateGraph(ClinicalState)
workflow.add_node("explainer", clinical_explainer)
workflow.add_node("unicef_agent", unicef_guideline_agent)

# No conditional routing needed; all patients get a report
workflow.set_entry_point("explainer")
workflow.add_edge("explainer", "unicef_agent")
workflow.add_edge("unicef_agent", END)

clinical_agent_app = workflow.compile()
