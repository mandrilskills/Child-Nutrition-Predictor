from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

# Initialize the Gemini LLM 
# Ensure you have GOOGLE_API_KEY in your .env file or Streamlit Secrets
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

# 1. Define the State
class ClinicalState(TypedDict):
    patient_data: dict      
    ml_prediction: str      
    messages: Annotated[Sequence[BaseMessage], operator.add] 

# 2. Define the Agent Nodes
def clinical_explainer(state: ClinicalState):
    """Explains the ML prediction based on the data."""
    sys_prompt = SystemMessage(
        content=f"You are a pediatric clinical AI. The ML model predicted the child is '{state['ml_prediction']}'. "
                f"Analyze this patient data: {state['patient_data']}. Explain briefly (2-3 sentences) why this prediction makes sense."
    )
    response = llm.invoke([sys_prompt])
    return {"messages": [response]}

def unicef_guideline_agent(state: ClinicalState):
    """Provides UNICEF-aligned interventions based on the specific failing metrics."""
    sys_prompt = SystemMessage(
        content=f"You are a public health expert specialized in UNICEF pediatric guidelines. "
                f"The child is classified as '{state['ml_prediction']}' with these stats: {state['patient_data']}. "
                f"Provide 3-4 specific, actionable measures to overcome this malnutrition. "
                f"Address the exact deficits (e.g., if clean water is 'No', mention WASH guidelines. If meals are irregular, mention RUTFs or calorie density). "
                f"Keep it professional, bulleted, and directly applicable."
    )
    # Pass previous messages so the agent has full context
    response = llm.invoke([sys_prompt] + state["messages"]) 
    return {"messages": [response]}

# 3. Define Routing Logic
def route_patient(state: ClinicalState):
    """Routes the workflow based on the deterministic ML prediction."""
    if state["ml_prediction"] == "Healthy":
        return END  
    return "explainer"

# 4. Build the Graph
workflow = StateGraph(ClinicalState)

# Add nodes
workflow.add_node("explainer", clinical_explainer)
workflow.add_node("unicef_agent", unicef_guideline_agent)

# Add edges and conditional routing
workflow.set_conditional_entry_point(
    route_patient, 
    {
        "explainer": "explainer", 
        END: END
    }
)
workflow.add_edge("explainer", "unicef_agent")
workflow.add_edge("unicef_agent", END)

# Compile the agentic application
clinical_agent_app = workflow.compile()
