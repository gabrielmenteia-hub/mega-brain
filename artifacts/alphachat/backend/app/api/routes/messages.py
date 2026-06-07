from fastapi import APIRouter, HTTPException, Depends
from app.models.message import MessageSend, MessageResponse, PreviewRequest
from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.character_engine import generate_character_response
from app.services.knowledge_retriever import retrieve_concepts
from app.services.coach_analyzer import analyze_message
from app.services.feedback_writer import write_feedback
from app.services.progress_tracker import compute_session_xp
import asyncio

router = APIRouter()


@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db),
):
    # Ownership check
    session = db.table("training_sessions").select("user_id").eq("id", session_id).single().execute()
    if not session.data or session.data["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="forbidden")
    result = db.table("messages").select("*").eq("session_id", session_id).order("turn").execute()
    return {"messages": result.data or []}


@router.post("/send", response_model=MessageResponse)
async def send_message(
    payload: MessageSend,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db),
):
    session = db.table("training_sessions").select("*").eq("id", str(payload.session_id)).single().execute()
    if not session.data or session.data["status"] != "active":
        raise HTTPException(status_code=400, detail="session_not_active")
    if session.data["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="forbidden")

    s = session.data
    history = db.table("messages").select("*").eq("session_id", str(payload.session_id)).order("turn").execute()
    messages = history.data or []

    new_turn = s["turn_count"] + 1
    db.table("messages").insert({
        "session_id": str(payload.session_id),
        "turn": new_turn,
        "sender": "user",
        "text": payload.text
    }).execute()

    user = db.table("users").select("level, subscription_tier").eq("id", user_id).single().execute()
    user_level = user.data.get("level", 1) if user.data else 1

    char_task = generate_character_response(
        character=s["character"],
        history=messages + [{"sender": "user", "text": payload.text}],
        interest_level=s["interest_level"],
        turn_count=new_turn
    )
    concepts_task = retrieve_concepts(
        user_message=payload.text,
        history_last_3=messages[-6:] if len(messages) > 6 else messages,
        user_level=user_level,
        scenario=s["scenario"]
    )

    char_result, concepts = await asyncio.gather(char_task, concepts_task)

    analysis = await analyze_message(
        user_message=payload.text,
        history=messages,
        concepts=concepts,
        character_state={"interest_level": s["interest_level"]},
        user_level=user_level
    )

    feedback = await write_feedback(
        analysis=analysis,
        user_message=payload.text,
        user_level=user_level,
        concepts=concepts
    )

    score = analysis["overall"]
    if score >= 8:
        delta = 10
    elif score >= 6:
        delta = 5
    elif score >= 4:
        delta = -3
    else:
        delta = -10

    new_interest = max(0, min(100, char_result["interest_level"] + delta))

    db.table("training_sessions").update({
        "turn_count": new_turn,
        "interest_level": new_interest,
        "last_coach_score": score
    }).eq("id", str(payload.session_id)).execute()

    db.table("messages").insert({
        "session_id": str(payload.session_id),
        "turn": new_turn,
        "sender": "assistant",
        "text": char_result["character_response"],
        "analysis": analysis
    }).execute()

    xp_result = compute_session_xp(
        scores_average={**analysis["scores"], "overall": score},
        mode=s["mode"],
        character=s["character"],
        session_completed=False
    )

    return MessageResponse(
        turn=new_turn,
        character_response=char_result["character_response"],
        interest_level=new_interest,
        interest_delta=delta,
        applied_test=char_result.get("applied_test", False),
        coach_feedback=feedback,
        xp_gained=xp_result["xp_gained"]
    )


@router.post("/preview")
async def preview_message(
    payload: PreviewRequest,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db),
):
    user = db.table("users").select("subscription_tier, level").eq("id", user_id).single().execute()
    plan = user.data.get("subscription_tier", "free") if user.data else "free"

    if plan == "free":
        return {"blocked": True, "upgrade_url": "/upgrade"}

    session = db.table("training_sessions").select("*").eq("id", str(payload.session_id)).single().execute()
    if not session.data or session.data["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="forbidden")

    s = session.data
    history = db.table("messages").select("*").eq("session_id", str(payload.session_id)).order("turn").execute()
    user_level = user.data.get("level", 1)
    concepts = await retrieve_concepts(payload.draft, history.data[-6:], user_level, s["scenario"])
    analysis = await analyze_message(payload.draft, history.data, concepts, {"interest_level": s["interest_level"]}, user_level)
    feedback = await write_feedback(analysis, payload.draft, user_level, concepts)

    return {
        "blocked": False,
        "preview_feedback": feedback["feedback_text"],
        "score_preview": feedback["score_overall"],
        "suggestions": feedback["alternatives"]
    }
