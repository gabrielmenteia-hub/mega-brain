from fastapi import APIRouter, Depends, Query
from app.services.knowledge_retriever import retrieve_concepts, get_concept_by_id
from app.core.database import get_db
from app.core.auth import get_current_user

router = APIRouter()


@router.get("/search")
async def search_concepts(
    query: str = Query(...),
    top_k: int = Query(5),
    user_id: str = Depends(get_current_user),
    db=Depends(get_db),
):
    user = db.table("users").select("level").eq("id", user_id).single().execute()
    user_level = user.data.get("level", 1) if user.data else 1

    concepts = await retrieve_concepts(
        user_message=query,
        history_last_3=[],
        user_level=user_level,
        scenario="all",
        top_k=top_k
    )
    return {"concepts": concepts, "total": len(concepts)}


@router.get("/concept/{concept_id}")
async def get_concept(
    concept_id: str,
    _: str = Depends(get_current_user),
):
    return await get_concept_by_id(concept_id)
