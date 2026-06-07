from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class MessageSend(BaseModel):
    session_id: UUID4
    text: str

class DimensionScores(BaseModel):
    confianca: float
    frame: float
    calibracao: float
    polaridade: float
    assertividade: float
    overall: float

class CoachFeedback(BaseModel):
    feedback_text: str
    score_overall: float
    priority_issue: str
    concept_cited: str
    alternatives: list[str]

class MessageResponse(BaseModel):
    turn: int
    character_response: str
    interest_level: int
    interest_delta: int
    applied_test: bool
    coach_feedback: CoachFeedback
    xp_gained: int

class PreviewRequest(BaseModel):
    session_id: UUID4
    draft: str

class PreviewResponse(BaseModel):
    blocked: bool
    preview_feedback: Optional[str]
    score_preview: Optional[float]
    suggestions: Optional[list[str]]
