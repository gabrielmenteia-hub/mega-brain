from app.models.progress import get_level_from_xp, LEVEL_NAMES, LEVEL_THRESHOLDS

MODE_MULTIPLIERS = {"livre": 1.0, "guiado": 1.2, "desafio": 1.5}
CHARACTER_MULTIPLIERS = {"high_value": 1.3, "intellectual": 1.1, "casual_fun": 1.0, "girl_next_door": 1.0}
SKILL_XP_TABLE = {(8, 10): 15, (6, 7): 8, (4, 5): 3, (0, 3): 0}

def compute_session_xp(
    scores_average: dict,
    mode: str,
    character: str,
    session_completed: bool
) -> dict:
    overall = scores_average.get("overall", 5.0)
    xp_base = overall * 10

    mult_mode = MODE_MULTIPLIERS.get(mode, 1.0)
    mult_char = CHARACTER_MULTIPLIERS.get(character, 1.0)
    mult_completion = 1.2 if session_completed else 0.8

    xp_final = int(xp_base * mult_mode * mult_char * mult_completion)

    skills_xp = {}
    for skill in ["confianca", "frame", "calibracao", "polaridade", "assertividade"]:
        score = scores_average.get(skill, 5.0)
        xp = 0
        for (low, high), gain in SKILL_XP_TABLE.items():
            if low <= score <= high:
                xp = gain
                break
        skills_xp[skill] = xp

    return {
        "xp_gained": xp_final,
        "skills_xp": skills_xp,
        "breakdown": {
            "base": round(xp_base),
            "multiplier_mode": mult_mode,
            "multiplier_character": mult_char,
            "multiplier_completion": mult_completion
        }
    }

def update_progress(
    current_xp: int,
    current_skills: dict,
    xp_gained: int,
    skills_xp: dict
) -> dict:
    new_total_xp = current_xp + xp_gained
    level_before = get_level_from_xp(current_xp)
    level_after = get_level_from_xp(new_total_xp)

    new_skills = {}
    milestones = []

    for skill, gained in skills_xp.items():
        old_xp = current_skills.get(skill, {}).get("xp", 0)
        new_xp = old_xp + gained
        old_level = get_level_from_xp(old_xp)
        new_level = get_level_from_xp(new_xp)

        new_skills[skill] = {"xp": new_xp, "nivel": new_level}

        if new_level > old_level:
            milestones.append(f"{skill} chegou ao nível {new_level}")

    return {
        "total_xp_new": new_total_xp,
        "level_new": level_after,
        "level_name": LEVEL_NAMES[level_after],
        "level_up": level_after > level_before,
        "milestones": milestones,
        "new_skills": new_skills
    }
