from fastapi import APIRouter, HTTPException, Depends
from app.models.session import SessionCreate
from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.character_engine import generate_character_response, PERSONAS
from app.services.progress_tracker import compute_session_xp
from app.models.progress import get_level_from_xp
import uuid
import json
from datetime import datetime

router = APIRouter()

FREE_DAILY_LIMIT = 3


@router.post("/create")
async def create_session(
    payload: SessionCreate,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db),
):
    user = db.table("users").select("subscription_tier").eq("id", user_id).single().execute()
    plan = user.data.get("subscription_tier", "free") if user.data else "free"

    if plan == "free":
        today_count = db.table("training_sessions") \
            .select("id", count="exact") \
            .eq("user_id", user_id) \
            .gte("created_at", datetime.utcnow().date().isoformat()) \
            .execute()
        if today_count.count >= FREE_DAILY_LIMIT:
            raise HTTPException(status_code=402, detail="daily_limit_reached")

    persona = PERSONAS[payload.character]
    session_id = str(uuid.uuid4())

    db.table("training_sessions").insert({
        "id": session_id,
        "user_id": user_id,
        "scenario": payload.scenario,
        "character": payload.character,
        "mode": payload.mode,
        "status": "active",
        "interest_level": persona["interest_initial"],
        "turn_count": 0,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    opening = await generate_character_response(
        character=payload.character,
        history=[],
        interest_level=persona["interest_initial"],
        turn_count=0
    )

    return {
        "session_id": session_id,
        "character_name": persona["name"],
        "character_age": persona["age"],
        "opening_message": opening["character_response"],
        "interest_level": persona["interest_initial"],
        "scenario": payload.scenario,
        "mode": payload.mode
    }


@router.post("/{session_id}/end")
async def end_session(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db),
):
    session = db.table("training_sessions").select("*").eq("id", session_id).single().execute()
    if not session.data:
        raise HTTPException(status_code=404, detail="session_not_found")
    s = session.data

    if s["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="forbidden")

    db.table("training_sessions").update({
        "status": "ended",
        "ended_at": datetime.utcnow().isoformat()
    }).eq("id", session_id).execute()

    messages = db.table("messages").select("analysis").eq("session_id", session_id).execute()
    all_scores = []
    for m in (messages.data or []):
        raw = m.get("analysis")
        if raw:
            analysis = raw if isinstance(raw, dict) else json.loads(raw)
            if "scores" in analysis:
                all_scores.append(analysis["scores"])

    if all_scores:
        keys = ["confianca", "frame", "calibracao", "polaridade", "assertividade"]
        avg = {k: sum(a.get(k, 5) for a in all_scores) / len(all_scores) for k in keys}
        overall = sum(avg.values()) / len(avg)
    else:
        avg = {k: 5.0 for k in ["confianca", "frame", "calibracao", "polaridade", "assertividade"]}
        overall = 5.0

    xp_result = compute_session_xp(
        scores_average={**avg, "overall": overall},
        mode=s.get("mode", "livre"),
        character=s.get("character", "casual_fun"),
        session_completed=True
    )

    db.table("training_sessions").update({
        "xp_gained": xp_result["xp_gained"],
        "last_coach_score": round(overall, 1),
    }).eq("id", session_id).execute()

    user = db.table("users").select("total_xp").eq("id", user_id).single().execute()
    current_xp = user.data.get("total_xp", 0) if user.data else 0
    new_xp = current_xp + xp_result["xp_gained"]
    new_level = get_level_from_xp(new_xp)

    db.table("users").update({"total_xp": new_xp, "level": new_level}).eq("id", user_id).execute()

    for skill, gained in xp_result["skills_xp"].items():
        if gained > 0:
            existing = db.table("user_skills").select("xp") \
                .eq("user_id", user_id).eq("skill", skill).single().execute()
            old_xp = existing.data.get("xp", 0) if existing.data else 0
            new_skill_xp = old_xp + gained
            db.table("user_skills").update({
                "xp": new_skill_xp,
                "nivel": get_level_from_xp(new_skill_xp)
            }).eq("user_id", user_id).eq("skill", skill).execute()

    return {
        "ended": True,
        "xp_gained": xp_result["xp_gained"],
        "level_up": new_level > get_level_from_xp(current_xp),
    }


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db),
):
    result = db.table("training_sessions").select("*").eq("id", session_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="session_not_found")
    if result.data["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="forbidden")
    return result.data
