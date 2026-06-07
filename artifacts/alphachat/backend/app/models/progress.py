from pydantic import BaseModel, UUID4

class SkillState(BaseModel):
    xp: int
    nivel: int
    xp_next_milestone: int

class ProgressOverview(BaseModel):
    user_id: UUID4
    total_xp: int
    level: int
    level_name: str
    xp_to_next_level: int
    skills: dict[str, SkillState]
    total_sessions: int
    sessions_this_week: int

LEVEL_NAMES = {
    1: "INICIANTE",
    2: "APRENDIZ",
    3: "PRATICANTE",
    4: "AVANÇADO",
    5: "EXPERT",
    6: "MESTRE"
}

LEVEL_THRESHOLDS = {
    1: 0,
    2: 100,
    3: 300,
    4: 700,
    5: 1500,
    6: 3000
}

def get_level_from_xp(xp: int) -> int:
    level = 1
    for lvl, threshold in LEVEL_THRESHOLDS.items():
        if xp >= threshold:
            level = lvl
    return level
