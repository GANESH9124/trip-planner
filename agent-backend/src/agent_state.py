from typing import TypedDict, List
from pydantic import BaseModel

class AgentState(TypedDict, total=False):
    """
    Represents the state of an agent, including its task, plan, draft and history.
    Using total=False allows partial state initialization.
    """
    task: str
    plan: str
    draft: str
    critique: str
    queries: List[str]
    answers: List[str]
    revision_number: int
    max_revisions: int
    count: int

class Queries(BaseModel):
    """
    Represents a list of queries made by the agent.
    """
    queries: List[str]