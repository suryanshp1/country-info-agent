from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import (
    extract_intent,
    validate,
    call_api,
    process_data,
    synthesize
)

builder = StateGraph(AgentState)

builder.add_node("extract", extract_intent)
builder.add_node("validate", validate)
builder.add_node("api", call_api)
builder.add_node("process", process_data)
builder.add_node("synthesize", synthesize)

builder.set_entry_point("extract")

builder.add_edge("extract", "validate")
builder.add_edge("validate", "api")
builder.add_edge("api", "process")
builder.add_edge("process", "synthesize")
builder.add_edge("synthesize", END)

graph = builder.compile()
