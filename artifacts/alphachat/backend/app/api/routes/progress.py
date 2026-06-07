from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.progress import get_level_from_xp, LEVEL_NAMES, LEVEL_THRESHOLDS
from app.services.progress_tracker import compute_session_xp
import anthropic
from app.core.config import settings
import json
from datetime import datetime, date, timedelta

router = APIRouter()

_claude = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


@router.get("/session/{session_id}")
async def get_session_analysis(
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

    messages = db.table("messages").select("*").eq("session_id", session_id).order("turn").execute()
    msgs = messages.data or []

    created = datetime.fromisoformat(s.get("created_at", datetime.utcnow().isoformat()))
    ended = datetime.fromisoformat(s.get("ended_at", datetime.utcnow().isoformat()))
    duration_minutes = max(1, int((ended - created).total_seconds() / 60))

    all_scores: list[dict] = []
    concepts_seen: list[str] = []
    for m in msgs:
        if m.get("sender") == "assistant" and m.get("analysis"):
            analysis = m["analysis"] if isinstance(m["analysis"], dict) else json.loads(m["analysis"])
            all_scores.append(analysis.get("scores", {}))
            for flag in analysis.get("green_flags", []):
                if flag not in concepts_seen:
                    concepts_seen.append(flag)

    if all_scores:
        keys = ["confianca", "frame", "calibracao", "polaridade", "assertividade"]
        avg_scores = {k: round(sum(a.get(k, 5) for a in all_scores) / len(all_scores), 1) for k in keys}
        overall = round(sum(avg_scores.values()) / len(avg_scores), 1)
    else:
        avg_scores = {k: 5.0 for k in ["confianca", "frame", "calibracao", "polaridade", "assertividade"]}
        overall = 5.0

    xp_result = compute_session_xp(
        scores_average={**avg_scores, "overall": overall},
        mode=s.get("mode", "livre"),
        character=s.get("character", "casual_fun"),
        session_completed=True
    )

    user_msgs = [m["text"] for m in msgs if m.get("sender") == "user"]
    coach_summary = "Sessão registrada."
    top_moment = ""
    improvement_tip = ""

    if user_msgs:
        prompt = f"""Analise estas mensagens enviadas pelo usuário em uma simulação de conversa:
{json.dumps(user_msgs, ensure_ascii=False)}

Score geral da sessão: {overall}/10
Scores: {json.dumps(avg_scores, ensure_ascii=False)}

Responda APENAS com JSON válido:
{{
  "coach_summary": "resumo em 2 frases do desempenho",
  "top_moment": "o melhor momento específico",
  "improvement_tip": "uma dica concreta para melhorar"
}}"""
        try:
            resp = _claude.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            parsed = json.loads(resp.content[0].text)
            coach_summary = parsed.get("coach_summary", coach_summary)
            top_moment = parsed.get("top_moment", "")
            improvement_tip = parsed.get("improvement_tip", "")
        except Exception:
            pass

    return {
        "score_overall": overall,
        "duration_minutes": duration_minutes,
        "total_turns": s.get("turn_count", len(user_msgs)),
        "final_interest": s.get("interest_level", 50),
        "xp_gained": xp_result["xp_gained"],
        "level_up": False,
        "scores": avg_scores,
        "milestones": concepts_seen[:5],
        "concepts_encountered": list(set(concepts_seen))[:8],
        "coach_summary": coach_summary,
        "top_moment": top_moment,
        "improvement_tip": improvement_tip,
    }


@router.get("/overview")
async def get_progress(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db),
):
    user = db.table("users").select("total_xp, level").eq("id", user_id).single().execute()
    skills = db.table("user_skills").select("*").eq("user_id", user_id).execute()

    total_xp = user.data.get("total_xp", 0) if user.data else 0
    level = get_level_from_xp(total_xp)
    next_threshold = LEVEL_THRESHOLDS.get(level + 1, 9999)
    skills_map = {s["skill"]: {"xp": s["xp"], "nivel": s["nivel"]} for s in (skills.data or [])}

    sessions = db.table("training_sessions") \
        .select("last_coach_score, created_at") \
        .eq("user_id", user_id) \
        .eq("status", "ended") \
        .execute()
    session_list = sessions.data or []
    total_sessions = len(session_list)
    best_score = max((s.get("last_coach_score", 0) for s in session_list), default=0)

    session_dates = sorted(set(
        s["created_at"][:10] for s in session_list if s.get("created_at")
    ), reverse=True)
    streak = 0
    today = date.today()
    for i, d in enumerate(session_dates):
        if d == str(today - timedelta(days=i)):
            streak += 1
        else:
            break

    return {
        "xp": total_xp,
        "level": level,
        "level_name": LEVEL_NAMES[level],
        "xpNextLevel": next_threshold,
        "xp_to_next_level": next_threshold - total_xp,
        "skills": skills_map,
        "totalSessions": total_sessions,
        "bestScore": round(best_score, 1),
        "streak": streak,
    }
