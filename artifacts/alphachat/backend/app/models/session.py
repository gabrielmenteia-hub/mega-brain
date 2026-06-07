from pydantic import BaseModel, UUID4
from typing import Optional, Literal
from datetime import datetime

ScenarioType = Literal["match_no_app", "primeira_mensagem", "primeiro_encontro", "testes_e_objecoes", "escalacao"]
CharacterType = Literal["casual_fun", "intellectual", "high_value", "girl_next_door"]
ModeType = Literal["livre", "guiado", "desafio"]
PlanType = Literal["free", "pro", "master"]

class SessionCreate(BaseModel):
    scenario: ScenarioType
    character: CharacterType
    mode: ModeType

class SessionState(BaseModel):
    session_id: UUID4
    status: Literal["active", "ended", "archived"]
    scenario: ScenarioType
    character: CharacterType
    mode: ModeType
    interest_level: int
    turn_count: int
    created_at: datetime

class SessionSummary(BaseModel):
    session_id: UUID4
    duration_minutes: int
    total_turns: int
    final_interest: int
    score_overall: float
    xp_gained: int
    level_up: bool
    milestones: list[str]
    concepts_encountered: list[str]
