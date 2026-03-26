"""
Chunking script for Dotcom Secrets (RB5D4)
Russell Brunson | BLUEPRINTS | 2026-03-08
"""
import json, re
from pathlib import Path

SOURCE_ID = "RB5D4"
SOURCE_PERSON = "Russell Brunson"
SOURCE_TITLE = "Dotcom Secrets"
SOURCE_PATH = "inbox/RUSSELL BRUNSON (Russell Brunson)/BLUEPRINTS/Dotcom Secrets.txt"
CHUNK_SIZE = 300  # words

ROOT = Path("c:/Users/Gabriel/MEGABRAIN")
FILE_PATH = ROOT / SOURCE_PATH
CHUNKS_STATE_PATH = ROOT / "processing/chunks/CHUNKS-STATE.json"

# Read content
with open(FILE_PATH, "r", encoding="utf-8") as f:
    raw = f.read()

# Clean up tab-separated text (PDF artifact)
text = re.sub(r'\t+', ' ', raw)
text = re.sub(r' {2,}', ' ', text)
text = re.sub(r'\n{3,}', '\n\n', text)

# Split into words
words = text.split()
total_words = len(words)

# Create chunks
chunks = []
chunk_num = 1
i = 0

while i < len(words):
    chunk_words = words[i:i+CHUNK_SIZE]
    chunk_text = ' '.join(chunk_words)

    chunk_id = f"chunk_{SOURCE_ID}_{chunk_num:03d}"

    chunk = {
        "id_chunk": chunk_id,
        "conteudo": chunk_text,
        "meta": {
            "source_id": SOURCE_ID,
            "source_person": SOURCE_PERSON,
            "source_title": SOURCE_TITLE,
            "source_path": SOURCE_PATH,
            "source_type": "doc",
            "scope": "personal",
            "corpus": "russell_brunson",
            "chunk_num": chunk_num,
            "word_count": len(chunk_words),
            "source_datetime": "2026-03-08"
        },
        "pessoas": ["Russell Brunson"],
        "temas": []
    }
    chunks.append(chunk)
    i += CHUNK_SIZE
    chunk_num += 1

print(f"Generated {len(chunks)} chunks from {total_words} words")

# Load existing CHUNKS-STATE
with open(CHUNKS_STATE_PATH, "r", encoding="utf-8") as f:
    state = json.load(f)

# Build set of existing chunk IDs (handle both id and id_chunk keys)
existing_ids = set()
for c in state.get("chunks", []):
    existing_ids.add(c.get('id_chunk') or c.get('id', ''))

# Filter out duplicates
new_chunks = [c for c in chunks if c["id_chunk"] not in existing_ids]
print(f"New chunks to add: {len(new_chunks)}")

# Merge
state["chunks"].extend(new_chunks)
state["meta"]["total_chunks"] = len(state["chunks"])
state["meta"]["last_updated"] = "2026-03-08"
if "source_ids" not in state["meta"]:
    state["meta"]["source_ids"] = []
if SOURCE_ID not in state["meta"]["source_ids"]:
    state["meta"]["source_ids"].append(SOURCE_ID)

# Save
with open(CHUNKS_STATE_PATH, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print(f"CHUNKS-STATE saved. Total chunks: {len(state['chunks'])}")
print(f"SOURCE_ID {SOURCE_ID} added: {len(new_chunks)} chunks")
