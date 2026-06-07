import json
import urllib.request
from pinecone import Pinecone
from app.core.config import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX)

VOYAGE_MODEL = "voyage-large-2"


def _generate_embedding(text: str) -> list[float]:
    payload = json.dumps({"input": [text], "model": VOYAGE_MODEL}).encode()
    req = urllib.request.Request(
        "https://api.voyageai.com/v1/embeddings",
        data=payload,
        headers={
            "Authorization": f"Bearer {settings.VOYAGE_API_KEY}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    return data["data"][0]["embedding"]


async def retrieve_concepts(
    user_message: str,
    history_last_3: list[dict],
    user_level: int,
    scenario: str,
    top_k: int = 3
) -> list[dict]:
    context = user_message + " " + " ".join([
        m.get("text", "") for m in history_last_3
    ])

    try:
        vector = _generate_embedding(context)

        results = index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            filter={"nivel_minimo": {"$lte": user_level}}
        )

        return [
            {
                "id": match.id,
                "nome": match.metadata.get("nome", ""),
                "score_similaridade": round(match.score, 3),
                "principio": match.metadata.get("principio", ""),
                "aplicacao_pratica": match.metadata.get("aplicacao_pratica", ""),
                "red_flags": match.metadata.get("red_flags", []),
                "green_flags": match.metadata.get("green_flags", []),
                "livros": match.metadata.get("livros", [])
            }
            for match in results.matches
        ]

    except Exception:
        return _fallback_concepts(user_message)


async def get_concept_by_id(concept_id: str) -> dict:
    try:
        result = index.fetch(ids=[concept_id])
        vectors = result.get("vectors", {})
        if concept_id in vectors:
            meta = vectors[concept_id].get("metadata", {})
            return {"id": concept_id, **meta}
    except Exception:
        pass
    return {"id": concept_id, "nome": concept_id, "error": "not_found"}


def _fallback_concepts(query: str) -> list[dict]:
    return [{
        "id": "frame_control_basic",
        "nome": "Frame Control",
        "score_similaridade": 0.0,
        "principio": "Manter sua realidade enquanto respeita a dela.",
        "aplicacao_pratica": "Não se justifique sob pressão.",
        "red_flags": ["justificar-se", "pedir aprovação"],
        "green_flags": ["manter posição", "redirecionar"],
        "livros": ["Deida", "Manson"]
    }]
