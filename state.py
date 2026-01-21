from pydantic import BaseModel
from typing import Optional

class LearnerState(BaseModel):
    current_checkpoint_index: int = 0
    explanation: Optional[str] = None
    score: float = 0.0
    relevance_score: float = 0.0
    context_ready: bool = False

def start_checkpoint(state: LearnerState) -> LearnerState:
    state.explanation = None
    state.score = 0.0
    state.relevance_score = 0.0
    state.context_ready = False
    return state

def gather_context(state: LearnerState) -> LearnerState:
    return state

def validate_context(state: LearnerState) -> bool:
    #if state.explanation is None:
        return True
    #return state.relevance_score >= 60
