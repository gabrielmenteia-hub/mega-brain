"""
Chunking script: V4 Company - Looking Ahead 2026 (Dia 1)
Source: inbox/V4 COMPANY/MASTERCLASS/...
Speakers: Dener Lippert (V4), Thiago Nigro, Andre Kliousoff (BTG), Rami Goldratt
"""
import json
import re
import os
from pathlib import Path
from datetime import datetime

# ─── CONFIG ─────────────────────────────────────────────────────────────────
SOURCE_ID   = "V4C001"
SOURCE_FILE = "inbox/V4 COMPANY/MASTERCLASS/Thiago Nigro, Rami Goldratt, Andre Kliousoff do BTG e Dener Lippert - Dia1 Looking Ahead 2026 [youtube.com_watch_v=Z5u0plptBnw].txt"
CHUNK_SIZE  = 300   # words per chunk
MAX_CHUNKS  = 250   # safety limit

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHUNKS_PATH = BASE_DIR / "processing" / "chunks" / "CHUNKS-STATE.json"

# ─── LOAD ────────────────────────────────────────────────────────────────────
with open(BASE_DIR / SOURCE_FILE, encoding="utf-8") as f:
    raw = f.read()

# Fix common encoding artifacts from YouTube auto-captions
fixes = {
    "\ufffd": "a",  # replacement char
    "D4 ": "V4 ",
    "Cliosof": "Kliousoff",
    "Denerin": "Dener",
    "Negro": "Nigro",
    "Nigo": "Nigro",
    "Lipert": "Lippert",
}
for bad, good in fixes.items():
    raw = raw.replace(bad, good)

# Clean up >> speaker change markers (keep but normalize)
# Join short lines into paragraphs
lines = raw.split("\n")
paragraphs = []
current = []
for line in lines:
    line = line.strip()
    if not line:
        if current:
            paragraphs.append(" ".join(current))
            current = []
    else:
        current.append(line)
if current:
    paragraphs.append(" ".join(current))

full_text = "\n\n".join(paragraphs)

# ─── DETECT SPEAKERS (heuristic) ─────────────────────────────────────────────
# The transcript uses >> for speaker changes but rarely names them inline
# We'll tag sections based on known content keywords
SPEAKER_KEYWORDS = {
    "Dener Lippert": ["V4", "franchise", "franquia", "restrição", "Theory of Constraints",
                      "alavanca", "parceiro", "CMO", "CEO", "DRX"],
    "Thiago Nigro": ["investidor", "educação financeira", "reserva", "patrimônio",
                     "renda", "independência financeira", "Primo Rico", "bolsa"],
    "Andre Kliousoff": ["BTG", "banco", "M&A", "valuation", "equity", "investimento",
                        "private equity", "venture", "due diligence"],
    "Rami Goldratt": ["TOC", "Theory of Constraints", "Goldratt", "constraint",
                      "buffer", "drum", "DBR", "critical chain", "flow"],
}

# ─── CHUNK ───────────────────────────────────────────────────────────────────
words = full_text.split()
total_words = len(words)
print(f"Total words: {total_words:,}")

chunks = []
chunk_idx = 0
i = 0

while i < len(words) and chunk_idx < MAX_CHUNKS:
    # Grab ~CHUNK_SIZE words, extend to sentence boundary
    end = min(i + CHUNK_SIZE, len(words))
    # Try to end at sentence boundary
    chunk_words = words[i:end]
    while end < len(words) and not re.search(r'[.!?]$', words[end-1]):
        end += 1
        chunk_words = words[i:end]
        if end - i > CHUNK_SIZE + 50:
            break

    chunk_text = " ".join(chunk_words)

    # Detect likely speaker based on keywords
    detected_speaker = "V4 Company Event"
    for speaker, keywords in SPEAKER_KEYWORDS.items():
        if any(kw.lower() in chunk_text.lower() for kw in keywords):
            detected_speaker = speaker
            break

    # Detect themes
    themes = []
    theme_map = {
        "marketing": ["marketing", "tráfego", "conversão", "funil", "CPA", "ROAS"],
        "vendas": ["vendas", "venda", "sales", "fechar", "cliente", "proposta"],
        "gestão": ["gestão", "liderança", "time", "equipe", "contratação", "cultura"],
        "financeiro": ["financeiro", "margem", "lucro", "faturamento", "caixa", "BTG"],
        "crescimento": ["crescimento", "escala", "expansão", "franquia", "restrição"],
        "investimento": ["investimento", "patrimônio", "ativo", "renda", "bolsa"],
        "teoria-restricoes": ["restrição", "constraint", "TOC", "Goldratt", "gargalo"],
        "estrategia": ["estratégia", "posicionamento", "mercado", "competição", "nicho"],
    }
    for theme, keywords in theme_map.items():
        if any(kw.lower() in chunk_text.lower() for kw in keywords):
            themes.append(theme)

    chunk_id = f"chunk_{SOURCE_ID}_{chunk_idx+1:03d}"

    chunks.append({
        "id_chunk": chunk_id,
        "conteudo": chunk_text,
        "meta": {
            "source_id": SOURCE_ID,
            "source_title": "Looking Ahead 2026 - Dia 1",
            "source_path": SOURCE_FILE,
            "source_type": "MASTERCLASS",
            "scope": "personal",
            "corpus": "v4_company",
            "source_datetime": "2026-02-07",
        },
        "pessoas": [detected_speaker],
        "temas": themes if themes else ["negócios"],
        "palavras": len(chunk_words),
    })

    i = end
    chunk_idx += 1
    if chunk_idx % 50 == 0:
        print(f"  {chunk_idx} chunks...")

print(f"Total chunks created: {len(chunks)}")

# ─── MERGE INTO CHUNKS-STATE ─────────────────────────────────────────────────
with open(CHUNKS_PATH, encoding="utf-8") as f:
    state = json.load(f)

existing_ids = {c["id_chunk"] for c in state.get("chunks", [])}
new_chunks = [c for c in chunks if c["id_chunk"] not in existing_ids]

state["chunks"].extend(new_chunks)
state.setdefault("meta", {})
state["meta"]["last_updated"] = datetime.now().isoformat()
state["meta"]["total_chunks"] = len(state["chunks"])
state["meta"].setdefault("source_ids", [])
if SOURCE_ID not in state["meta"]["source_ids"]:
    state["meta"]["source_ids"].append(SOURCE_ID)

with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print(f"New chunks added: {len(new_chunks)}")
print(f"Total chunks in state: {len(state['chunks'])}")
