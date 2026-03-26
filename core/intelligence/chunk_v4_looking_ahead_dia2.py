"""
Chunking: V4 Looking Ahead 2026 - Dia 2
Speakers: Flávio Augusto, Lázaro do Carmo, William Barnett (Professor Stanford)
"""
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHUNKS_PATH = BASE_DIR / "processing" / "chunks" / "CHUNKS-STATE.json"
SOURCE_ID = "V4C002"
CHUNK_SIZE = 300
MAX_CHUNKS = 220

# Encoding fixes for auto-generated captions
FIXES = {
    "Fl vio": "Flávio",
    "L zaro": "Lázaro",
    "Barnet": "Barnett",
    "Barnets": "Barnett",
    "Bernet": "Barnett",
    "Bern ": "Barnett ",
    "Jequt": "Jequiti",
    "Jequ": "Jequiti",
    "iFood": "iFood",
    "V4": "V4",
    "Wise Up": "Wise Up",
}

SPEAKER_KEYWORDS = {
    "Flávio Augusto": [
        "wise up", "escola", "franqueados", "rodrigo santoro",
        "generosidade", "produtividade", "riqueza", "fortuna", "fortuna",
        "vender", "venda", "empreendedor", "flávio", "flavio",
        "resultado", "foco", "execução",
    ],
    "Lázaro do Carmo": [
        "jequiti", "capital upgrade", "lázaro", "lazaro",
        "faturamento", "multiplicou", "crescimento", "escala",
        "distribuição", "varejo",
    ],
    "William Barnett": [
        "stanford", "barnett", "bill", "competição entre", "dissidência",
        "inovação", "desempenho excepcional", "epdc", "growing companies",
        "google", "spotify", "facebook", "dissidente", "consenso",
        "vantagem competitiva", "competição",
    ],
}

THEME_KEYWORDS = {
    "empreendedorismo": ["empreend", "negócio", "empresa", "mercado", "produto"],
    "produtividade": ["produtiv", "foco", "execução", "rotina", "disciplina"],
    "crescimento": ["crescimento", "escala", "faturamento", "receita", "expansão"],
    "inovação": ["inovaç", "inovar", "tecnologia", "disruptiv", "startup"],
    "liderança": ["liderança", "líder", "gestão", "time", "equipe", "cultura"],
    "marketing": ["marketing", "posicionamento", "marca", "audiência", "conteúdo"],
    "competição": ["competição", "concorr", "vantagem", "dissidência", "consenso"],
    "mindset": ["mindset", "mentalidade", "crença", "atitude", "comportamento"],
}


def detect_speaker(text: str) -> str:
    text_lower = text.lower()
    scores = {name: 0 for name in SPEAKER_KEYWORDS}
    for name, keywords in SPEAKER_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                scores[name] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "V4 Company"


def detect_themes(text: str) -> list:
    text_lower = text.lower()
    themes = []
    for theme, keywords in THEME_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            themes.append(theme)
    return themes or ["geral"]


def apply_fixes(text: str) -> str:
    for wrong, correct in FIXES.items():
        text = text.replace(wrong, correct)
    return text


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list:
    words = text.split()
    chunks = []
    current = []
    for word in words:
        current.append(word)
        if len(current) >= chunk_size:
            # Try to break at sentence boundary
            chunk_str = " ".join(current)
            last_period = max(
                chunk_str.rfind(". "),
                chunk_str.rfind("! "),
                chunk_str.rfind("? "),
            )
            if last_period > chunk_size * 3 // 4 * 5:  # at least 75% full
                chunks.append(chunk_str[: last_period + 1].strip())
                remainder = chunk_str[last_period + 1:].strip()
                current = remainder.split() if remainder else []
            else:
                chunks.append(chunk_str)
                current = []
    if current:
        chunks.append(" ".join(current))
    return chunks


# ── Load transcript ────────────────────────────────────────────────────────────
inbox_dir = BASE_DIR / "inbox" / "V4 COMPANY" / "MASTERCLASS"
transcript_file = None
for f in inbox_dir.iterdir():
    if "wUTEUaDUwPI" in f.name or "Dia2" in f.name:
        transcript_file = f
        break

if not transcript_file:
    raise FileNotFoundError("Transcript file for Dia2 not found")

raw = transcript_file.read_text(encoding="utf-8")
# Remove header
if "---" in raw:
    raw = raw[raw.index("---") + 3:].strip()

raw = apply_fixes(raw)
print(f"Source file: {transcript_file.name}")
print(f"Total words: {len(raw.split())}")

# ── Chunk ──────────────────────────────────────────────────────────────────────
text_chunks = chunk_text(raw, CHUNK_SIZE)
if len(text_chunks) > MAX_CHUNKS:
    print(f"Truncating from {len(text_chunks)} to {MAX_CHUNKS} chunks")
    text_chunks = text_chunks[:MAX_CHUNKS]

print(f"Chunks to create: {len(text_chunks)}")

# ── Load existing state ────────────────────────────────────────────────────────
with open(CHUNKS_PATH, encoding="utf-8") as f:
    state = json.load(f)

existing_ids = {c["id_chunk"] for c in state.get("chunks", [])}
# Remove old V4C002 chunks if any
state["chunks"] = [c for c in state["chunks"] if c.get("meta", {}).get("source_id") != SOURCE_ID]

# ── Build new chunks ───────────────────────────────────────────────────────────
new_chunks = []
for i, text in enumerate(text_chunks):
    chunk_id = f"chunk_{SOURCE_ID}_{i+1:03d}"
    speaker = detect_speaker(text)
    themes = detect_themes(text)

    chunk = {
        "id_chunk": chunk_id,
        "conteudo": text,
        "pessoas": [speaker],
        "temas": themes,
        "meta": {
            "source_id": SOURCE_ID,
            "source_title": "Looking Ahead 2026 - Dia 2",
            "source_type": "masterclass",
            "source_path": str(transcript_file),
            "source_datetime": "2026-02-08",
            "scope": "marketing",
            "corpus": "v4_company",
            "speaker_detected": speaker,
        },
    }
    new_chunks.append(chunk)

state["chunks"].extend(new_chunks)
state.setdefault("meta", {})["last_updated"] = "2026-03-07"
state["meta"]["total_chunks"] = len(state["chunks"])

with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print(f"\nChunks created: {len(new_chunks)}")
print(f"Total chunks in state: {len(state['chunks'])}")

# Speaker distribution
from collections import Counter
speakers = Counter(c["pessoas"][0] for c in new_chunks)
for spk, count in speakers.most_common():
    print(f"  {spk}: {count} chunks")
