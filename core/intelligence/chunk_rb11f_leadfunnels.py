"""Chunking for Lead Funnels (RB11F) — Russell Brunson"""
import json, re
from pathlib import Path

SOURCE_ID = "RB11F"
SOURCE_PERSON = "Russell Brunson"
SOURCE_TITLE = "Lead Funnels"
SOURCE_PATH = "inbox/RUSSELL BRUNSON (Russell Brunson)/BLUEPRINTS/Lead Funnels.txt"
CHUNK_SIZE = 300

ROOT = Path("c:/Users/Gabriel/MEGABRAIN")

with open(ROOT / SOURCE_PATH, "r", encoding="utf-8", errors="replace") as f:
    raw = f.read()

text = re.sub(r'\ufffd+', ' ', raw)
text = re.sub(r'\t+', ' ', text)
text = re.sub(r' {2,}', ' ', text)
text = re.sub(r'\n{3,}', '\n\n', text)
words = text.split()

chunks = []
for i in range(0, len(words), CHUNK_SIZE):
    n = i // CHUNK_SIZE + 1
    chunk_words = words[i:i+CHUNK_SIZE]
    chunks.append({
        "id_chunk": f"chunk_{SOURCE_ID}_{n:03d}",
        "conteudo": ' '.join(chunk_words),
        "meta": {
            "source_id": SOURCE_ID, "source_person": SOURCE_PERSON,
            "source_title": SOURCE_TITLE, "source_path": SOURCE_PATH,
            "source_type": "doc", "scope": "personal",
            "corpus": "russell_brunson", "chunk_num": n,
            "word_count": len(chunk_words), "source_datetime": "2026-03-09"
        },
        "pessoas": ["Russell Brunson"], "temas": []
    })

print(f"Generated {len(chunks)} chunks from {len(words)} words")

with open(ROOT / "processing/chunks/CHUNKS-STATE.json", "r", encoding="utf-8") as f:
    state = json.load(f)

existing_ids = set(c.get('id_chunk') or c.get('id', '') for c in state.get("chunks", []))
new_chunks = [c for c in chunks if c["id_chunk"] not in existing_ids]
state["chunks"].extend(new_chunks)
state["meta"]["total_chunks"] = len(state["chunks"])
state["meta"]["last_updated"] = "2026-03-09"
if SOURCE_ID not in state["meta"].get("source_ids", []):
    state["meta"].setdefault("source_ids", []).append(SOURCE_ID)

with open(ROOT / "processing/chunks/CHUNKS-STATE.json", "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print(f"Added {len(new_chunks)} chunks. Total: {len(state['chunks'])}")
