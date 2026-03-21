from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    query: str
    country: Optional[str]
    fields: Optional[List[str]]
    api_response: Optional[dict]
    final_answer: Optional[str]
    error: Optional[str]
