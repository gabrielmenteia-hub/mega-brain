"""
Script para popular o Pinecone com os 231 conceitos da base de conhecimento.
Usa Voyage AI (voyage-large-2, 1536 dims) para embeddings.

Uso:
  python scripts/populate_pinecone.py --input ../knowledge/unified_knowledge_base.json
"""

import json
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv
import os
import urllib.request

load_dotenv()

from pinecone import Pinecone, ServerlessSpec

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX", "alphachat-knowledge")
VOYAGE_MODEL = "voyage-large-2"
EMBEDDING_DIM = 1536

pc = Pinecone(api_key=PINECONE_API_KEY)


def create_index_if_not_exists():
    existing = [i.name for i in pc.list_indexes()]
    if INDEX_NAME not in existing:
        print(f"Criando index '{INDEX_NAME}'...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        time.sleep(10)
        print("Index criado.")
    else:
        print(f"Index '{INDEX_NAME}' já existe.")


def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    payload = json.dumps({
        "input": texts,
        "model": VOYAGE_MODEL,
    }).encode()
    req = urllib.request.Request(
        "https://api.voyageai.com/v1/embeddings",
        data=payload,
        headers={
            "Authorization": f"Bearer {VOYAGE_API_KEY}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    return [item["embedding"] for item in data["data"]]


def build_embedding_text(concept: dict) -> str:
    parts = [
        concept.get("nome", ""),
        concept.get("principio", ""),
        concept.get("aplicacao_pratica", ""),
        " ".join(concept.get("red_flags", [])),
        " ".join(concept.get("green_flags", [])),
    ]
    return " ".join(filter(None, parts))


def populate(input_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    concepts = data if isinstance(data, list) else data.get("concepts", [])
    print(f"{len(concepts)} conceitos encontrados.")

    create_index_if_not_exists()
    index = pc.Index(INDEX_NAME)

    BATCH_SIZE = 10
    for i in range(0, len(concepts), BATCH_SIZE):
        batch_concepts = concepts[i:i + BATCH_SIZE]
        texts = [build_embedding_text(c) for c in batch_concepts]

        print(f"[{i+1}-{min(i+BATCH_SIZE, len(concepts))}/{len(concepts)}] Gerando embeddings...")
        embeddings = generate_embeddings_batch(texts)

        vectors = []
        for j, (concept, embedding) in enumerate(zip(batch_concepts, embeddings)):
            vectors.append({
                "id": concept.get("id", f"concept_{i+j}"),
                "values": embedding,
                "metadata": {
                    "nome": concept.get("nome", ""),
                    "categoria": concept.get("categoria", ""),
                    "principio": concept.get("principio", ""),
                    "aplicacao_pratica": concept.get("aplicacao_pratica", ""),
                    "red_flags": concept.get("red_flags", []),
                    "green_flags": concept.get("green_flags", []),
                    "livros": concept.get("livros", []),
                    "nivel_minimo": concept.get("nivel_minimo", 1),
                    "cenarios": concept.get("cenarios", []),
                    "prioridade": concept.get("prioridade", "media")
                }
            })

        index.upsert(vectors=vectors)
        print(f"  → Batch inserido.")
        time.sleep(0.3)

    stats = index.describe_index_stats()
    print(f"\nPopulação concluída. Total no index: {stats.total_vector_count} vetores.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="../knowledge/unified_knowledge_base.json")
    args = parser.parse_args()
    populate(args.input)
