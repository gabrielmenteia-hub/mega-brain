"""
PIPELINE UTILS — Funções reutilizáveis para todos os scripts de pipeline.
Elimina código duplicado entre chunk_*.py e extract_*.py

Uso em chunk_*.py:
    from core.intelligence.pipeline_utils import chunk_file, save_chunks

Uso em extract_*.py:
    from core.intelligence.pipeline_utils import load_insights, save_insights, register_source

"""
import json
import re
import hashlib
import datetime
from pathlib import Path
from typing import Any

ROOT = Path("c:/Users/Gabriel/MEGABRAIN")
CHUNKS_STATE = ROOT / "processing/chunks/CHUNKS-STATE.json"
INSIGHTS_STATE = ROOT / "processing/insights/INSIGHTS-STATE.json"
REGISTRY_PATH = ROOT / "system/REGISTRY/file-registry.json"
AUDIT_PATH = ROOT / "logs/AUDIT/audit.jsonl"


# ── CHUNKING ──────────────────────────────────────────────────────────────

def chunk_file(source_path: str, source_id: str, source_person: str,
               source_title: str, chunk_size: int = 300) -> list[dict]:
    """Read a text file and return list of chunk dicts."""
    full_path = ROOT / source_path
    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()
    text = re.sub(r'\ufffd+', ' ', raw)
    text = re.sub(r'\t+', ' ', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    words = text.split()

    chunks = []
    for i in range(0, len(words), chunk_size):
        n = i // chunk_size + 1
        chunk_words = words[i:i + chunk_size]
        chunks.append({
            "id_chunk": f"chunk_{source_id}_{n:03d}",
            "conteudo": ' '.join(chunk_words),
            "meta": {
                "source_id": source_id,
                "source_person": source_person,
                "source_title": source_title,
                "source_path": source_path,
                "source_type": "doc",
                "scope": "personal",
                "chunk_num": n,
                "word_count": len(chunk_words),
                "source_datetime": datetime.date.today().isoformat()
            },
            "pessoas": [source_person],
            "temas": []
        })
    print(f"Generated {len(chunks)} chunks from {len(words)} words")
    return chunks


def save_chunks(chunks: list[dict], source_id: str) -> int:
    """Append new chunks to CHUNKS-STATE.json. Returns count added."""
    with open(CHUNKS_STATE, "r", encoding="utf-8") as f:
        state = json.load(f)

    existing_ids = {c.get('id_chunk') or c.get('id', '') for c in state.get("chunks", [])}
    new_chunks = [c for c in chunks if c["id_chunk"] not in existing_ids]
    state["chunks"].extend(new_chunks)
    state["meta"]["total_chunks"] = len(state["chunks"])
    state["meta"]["last_updated"] = datetime.date.today().isoformat()
    state["meta"].setdefault("source_ids", [])
    if source_id not in state["meta"]["source_ids"]:
        state["meta"]["source_ids"].append(source_id)

    with open(CHUNKS_STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print(f"Added {len(new_chunks)} chunks. Total: {len(state['chunks'])}")
    return len(new_chunks)


# ── INSIGHTS ──────────────────────────────────────────────────────────────

def load_insights(person: str) -> list[dict]:
    """Load existing insights list for a person from INSIGHTS-STATE.json."""
    with open(INSIGHTS_STATE, "r", encoding="utf-8") as f:
        state = json.load(f)
    persons = state["insights_state"].get("persons", {})
    data = persons.get(person, [])
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return data.get("insights", [])
    return []


def save_insights(person: str, insights: list[dict],
                  source_id: str, source_title: str) -> int:
    """
    Add new insights for a person to INSIGHTS-STATE.json.
    Handles both list and dict formats.
    Returns count of new insights added.
    """
    with open(INSIGHTS_STATE, "r", encoding="utf-8") as f:
        state = json.load(f)

    state["insights_state"].setdefault("persons", {})
    person_data = state["insights_state"]["persons"].get(person, [])

    if isinstance(person_data, list):
        existing_list = person_data
    elif isinstance(person_data, dict):
        existing_list = person_data.get("insights", [])
    else:
        existing_list = []

    existing_ids = {i["id"] for i in existing_list}
    ts = datetime.datetime.now().isoformat()
    new_count = 0
    for insight in insights:
        if insight["id"] not in existing_ids:
            insight.setdefault("source_id", source_id)
            insight.setdefault("source_person", person)
            insight.setdefault("timestamp", ts)
            existing_list.append(insight)
            new_count += 1

    # Write back in same format
    if isinstance(state["insights_state"]["persons"].get(person), dict):
        state["insights_state"]["persons"][person]["insights"] = existing_list
    else:
        state["insights_state"]["persons"][person] = existing_list

    state["insights_state"].setdefault("change_log", []).append({
        "date": datetime.date.today().isoformat(),
        "source_id": source_id,
        "source_person": person,
        "action": "insights_added",
        "count": new_count
    })

    with open(INSIGHTS_STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    total = len(existing_list)
    print(f"Added {new_count} insights for {person} from {source_title}")
    print(f"Total insights for {person}: {total}")
    return new_count


# ── REGISTRY + AUDIT ──────────────────────────────────────────────────────

def register_source(source_path: str, source_id: str, person: str,
                    title: str, chunks: int, insights: int) -> None:
    """Add entry to file-registry.json and audit.jsonl."""
    full_path = ROOT / source_path
    with open(full_path, "rb") as f:
        md5 = hashlib.md5(f.read()).hexdigest()

    # Registry
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)
    files = registry.get("files", [])
    if source_id not in [x.get("source_id") for x in files]:
        files.append({
            "source_id": source_id, "path": source_path, "md5": md5,
            "status": "PROCESSED", "registered_at": datetime.date.today().isoformat(),
            "person": person, "title": title, "chunks": chunks, "insights": insights
        })
        registry["files"] = files
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
        print(f"✓ Registered: {source_id}")

    # Audit
    entry = json.dumps({
        "timestamp": datetime.datetime.now().isoformat(),
        "operation": "PIPELINE_COMPLETE",
        "source_id": source_id, "source_person": person, "source_title": title,
        "phases_completed": 8, "chunks": chunks, "insights": insights, "status": "SUCCESS"
    })
    with open(AUDIT_PATH, "a", encoding="utf-8") as f:
        f.write(entry + "\n")
    print(f"✓ Audit logged: {source_id}")


# ── INSIGHT DISTRIBUTION REPORT ──────────────────────────────────────────

def print_distribution(insights: list[dict]) -> None:
    """Print tipo distribution of an insights list."""
    from collections import Counter
    tipos = Counter(i.get("tipo", "?") for i in insights)
    print("\nDistribution:")
    for tipo, count in sorted(tipos.items()):
        print(f"  {tipo}: {count}")
