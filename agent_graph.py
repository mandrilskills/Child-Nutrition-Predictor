from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# Initialize the LLM (Ensure you have OPENAI_API_KEY in your .env file)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

# 1. Define the State (The shared memory for the agents)
class ClinicalState(TypedDict):
    patient_data: dict      # Raw input like Age, Weight, Height, etc.
    ml_prediction: str      # The output from model_logic.py (Healthy, At Risk, Malnourished)
    messages: Annotated[Sequence[BaseMessage], operator.add]  # Chat history

# 2. Define the Agent Nodes
def clinical_explainer(state: ClinicalState):
    """Explains why the ML model made its prediction."""
    prediction = state["ml_prediction"]
    data = state["patient_data"]
    
    sys_prompt = SystemMessage(
        content=f"You are a pediatric clinical AI. The Machine Learning model predicted the child is '{prediction}'. "
                f"Analyze this patient data: {data}. Explain briefly in simple terms why this prediction makes sense."
    )
    
    response = llm.invoke([sys_prompt] + state["messages"])
    return {"messages": [response]}

def dietitian_agent(state: ClinicalState):
    """Provides actionable dietary advice based on the ML prediction."""
    sys_prompt = SystemMessage(
        content="You are a pediatric dietitian. Based on the previous clinical explanation, "
                "suggest 3 low-cost, locally available foods to improve the child's nutrition. "
                "Keep it brief and bulleted."
    )
    
    response = llm.invoke([sys_prompt] + state["messages"])
    return {"messages": [response]}

# 3. Define Routing Logic
def route_patient(state: ClinicalState):
    """Routes the workflow based on the deterministic ML prediction."""
    if state["ml_prediction"] == "Healthy":
        return END  # If healthy, no intervention needed.
    return "explainer"

# 4. Build the Graph
workflow = StateGraph(ClinicalState)

# Add nodes
workflow.add_node("explainer", clinical_explainer)
workflow.add_node("dietitian", dietitian_agent)

# Add edges and conditional routing
workflow.set_conditional_entry_point(
    route_patient,
    {
        "explainer": "explainer",
        END: END
    }
)
workflow.add_edge("explainer", "dietitian")
workflow.add_edge("dietitian", END)

# Compile the agentic application
clinical_agent_app = workflow.compile()
