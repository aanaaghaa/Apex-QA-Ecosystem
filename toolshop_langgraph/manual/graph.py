from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .state import QAState
from .nodes import fetch_html_node, compress_dom_node, audit_compression_node

def should_retry_compression(state: QAState) -> str:
    """Routes back to compressor if audit fails and retries remain."""
    if state.get("audit_passed"):
        return "approved"
    if state.get("retry_count", 0)>=3:
        return "max_retries_reached"
    return "retry"

builder = StateGraph(QAState)

builder.add_node("fetch_html", fetch_html_node)
builder.add_node("compress_dom", compress_dom_node)
builder.add_node("audit_compression", audit_compression_node)

builder.add_edge(START, "fetch_html")
builder.add_edge("fetch_html", "compress_dom")
builder.add_edge("compress_dom", "audit_compression")

builder.add_conditional_edges(
    "audit_compression",
    should_retry_compression,
    {
        "approved": END,
        "max_retries_reached": END,
        "retry": "compress_dom",
    }
)

memory = MemorySaver()
qa_graph = builder.compile(checkpointer=memory)    
