"""
MASTER CHUNKING SCRIPT — Colecao Mente Lendaria
Processa todas as fontes ainda nao chunked no CHUNKS-STATE.json
Criado: 2026-03-06
"""

import json
import re
from pathlib import Path
from datetime import datetime

MEGABRAIN = Path("C:/Users/Gabriel/MEGABRAIN")
CHUNKS_STATE_PATH = MEGABRAIN / "processing/chunks/CHUNKS-STATE.json"
CHUNK_SIZE = 300  # palavras por chunk

# ── MAPEAMENTO DE FONTES ──────────────────────────────────────────────────────
SOURCES = [
    {
        "source_id": "AN-BP001",
        "person": "Alan Nicolas",
        "company": "AIOX",
        "type": "blueprint",
        "title": "AIOX Squad System Blueprint",
        "path": "inbox/ALAN NICOLAS/BLUEPRINTS/AIOX-Squad-System [AN-BLUEPRINT-001].txt",
        "corpus": "aiox",
        "datetime": "2026-01-01",
        "scope": "personal",
        "temas": ["AIOS-SQUAD", "AI-AGENTS", "NEGOCIOS"],
        "pessoas": ["Alan Nicolas"],
    },
    {
        "source_id": "BF001",
        "person": "Brad Frost",
        "company": "AIOX",
        "type": "book",
        "title": "Atomic Design - Brad Frost",
        "path": "inbox/ALAN NICOLAS/BOOKS/Atomic Design - Brad Frost.txt",
        "corpus": "design",
        "datetime": "2025-01-01",
        "scope": "personal",
        "temas": ["DESIGN-SYSTEM", "FRONTEND", "METODOLOGIA"],
        "pessoas": ["Brad Frost"],
    },
    {
        "source_id": "AN007",
        "person": "Alan Nicolas",
        "company": "AIOX",
        "type": "masterclass",
        "title": "Reprise direto do Vale do Silicio - O futuro do software ja foi decidido",
        "path": "inbox/ALAN NICOLAS/MASTERCLASS/Reprise direto do Vale do Silicio O futuro do software ja foi decidido e nao esta no seu HD [youtube.com_watch_v=d4xLP-GxJMM].txt",
        "corpus": "aiox",
        "datetime": "2026-02-01",
        "scope": "personal",
        "temas": ["AI-MODELOS", "NEGOCIOS", "TECH"],
        "pessoas": ["Alan Nicolas"],
    },
    {
        "source_id": "AH001",
        "person": "Ann Handley",
        "company": None,
        "type": "book",
        "title": "Everybody Writes",
        "path": "inbox/ANN HANDLEY/BOOKS/Everybody Writes [AH001].txt",
        "corpus": "marketing",
        "datetime": "2014-01-01",
        "scope": "personal",
        "temas": ["COPYWRITING", "CONTENT-MARKETING", "ESCRITA"],
        "pessoas": ["Ann Handley"],
    },
    {
        "source_id": "CH001",
        "person": "Chip Heath & Dan Heath",
        "company": None,
        "type": "book",
        "title": "Made to Stick",
        "path": "inbox/CHIP HEATH & DAN HEATH/BOOKS/Made to Stick [CH001].txt",
        "corpus": "marketing",
        "datetime": "2007-01-01",
        "scope": "personal",
        "temas": ["COMUNICACAO", "MENSAGEM", "PERSUASAO", "MARKETING"],
        "pessoas": ["Chip Heath", "Dan Heath"],
    },
    {
        "source_id": "CA001",
        "person": "Chris Anderson",
        "company": "Wired",
        "type": "book",
        "title": "The Long Tail",
        "path": "inbox/CHRIS ANDERSON/BLUEPRINTS/The Long Tail - Chris Anderson [livro].txt",
        "corpus": "marketing",
        "datetime": "2006-01-01",
        "scope": "personal",
        "temas": ["NEGOCIOS", "MERCADO", "ESTRATEGIA", "ECOMMERCE"],
        "pessoas": ["Chris Anderson"],
    },
    {
        "source_id": "DK001",
        "person": "Dan Kennedy",
        "company": None,
        "type": "book",
        "title": "Magnetic Marketing",
        "path": "inbox/DAN KENNEDY/BOOKS/Magnetic Marketing [DK001].txt",
        "corpus": "marketing",
        "datetime": "2018-01-01",
        "scope": "personal",
        "temas": ["MARKETING", "ATRACAO", "COPYWRITING", "VENDAS"],
        "pessoas": ["Dan Kennedy"],
    },
    {
        "source_id": "ES001",
        "person": "Eugene Schwartz",
        "company": None,
        "type": "book",
        "title": "Breakthrough Advertising",
        "path": "inbox/EUGENE SCHWARTZ/BOOKS/Breakthrough Advertising [ES001].txt",
        "corpus": "copywriting",
        "datetime": "1966-01-01",
        "scope": "personal",
        "temas": ["COPYWRITING", "PERSUASAO", "MARKETING", "PUBLICIDADE"],
        "pessoas": ["Eugene Schwartz"],
    },
    {
        "source_id": "JP001",
        "person": "Joe Pulizzi",
        "company": "Content Marketing Institute",
        "type": "book",
        "title": "Marketing de Conteudo Epico",
        "path": "inbox/JOE PULIZZI/BLUEPRINTS/Marketing de Conteudo Epico - Joe Pulizzi [livro].txt",
        "corpus": "marketing",
        "datetime": "2013-01-01",
        "scope": "personal",
        "temas": ["CONTENT-MARKETING", "MARKETING", "ESTRATEGIA"],
        "pessoas": ["Joe Pulizzi"],
    },
    {
        "source_id": "JS001",
        "person": "Joseph Sugarman",
        "company": "JS&A",
        "type": "book",
        "title": "The Adweek Copywriting Handbook",
        "path": "inbox/JOSEPH SUGARMAN/BOOKS/The Adweek Copywriting Handbook [JS001].txt",
        "corpus": "copywriting",
        "datetime": "1998-01-01",
        "scope": "personal",
        "temas": ["COPYWRITING", "PERSUASAO", "DIRECT-RESPONSE", "MARKETING"],
        "pessoas": ["Joseph Sugarman"],
    },
    {
        "source_id": "JS002",
        "person": "Joseph Sugarman",
        "company": "JS&A",
        "type": "book",
        "title": "Triggers - 30 Sales Tools You Can Use to Control the Mind of Your Prospect",
        "path": "inbox/JOSEPH SUGARMAN/BOOKS/Triggers [JS002].txt",
        "corpus": "copywriting",
        "datetime": "1999-01-01",
        "scope": "personal",
        "temas": ["COPYWRITING", "PERSUASAO", "GATILHOS-MENTAIS", "VENDAS"],
        "pessoas": ["Joseph Sugarman"],
    },
    {
        "source_id": "RC001",
        "person": "Robert Cialdini",
        "company": None,
        "type": "book",
        "title": "The Psychology of Persuasion (Influence)",
        "path": "inbox/ROBERT CIALDINI/BOOKS/The Psychology of Persuasion [RC001].txt",
        "corpus": "persuasao",
        "datetime": "1984-01-01",
        "scope": "personal",
        "temas": ["PERSUASAO", "PSICOLOGIA", "VENDAS", "MARKETING"],
        "pessoas": ["Robert Cialdini"],
    },
    {
        "source_id": "PK002",
        "person": "Philip Kotler",
        "company": None,
        "type": "book",
        "title": "Principles of Marketing 17th Edition",
        "path": "inbox/PHILIP KOTLER/BLUEPRINTS/Principles of Marketing 17e - Kotler Armstrong [livro].txt",
        "corpus": "marketing",
        "datetime": "2018-01-01",
        "scope": "personal",
        "temas": ["MARKETING", "ESTRATEGIA", "MERCADO", "NEGOCIOS"],
        "pessoas": ["Philip Kotler"],
        "max_chunks": 200,  # Limite para arquivo gigante (3.5MB)
    },
]

# ── CARREGA STATE ATUAL ───────────────────────────────────────────────────────
print("Carregando CHUNKS-STATE.json...")
state = json.loads(CHUNKS_STATE_PATH.read_text(encoding="utf-8"))
existing_sources = set(
    c.get("meta", {}).get("source_id", "")
    for c in state["chunks"]
)
print(f"Fontes ja no state: {sorted(existing_sources)}")
print(f"Total chunks atual: {len(state['chunks'])}")
print()

# ── FUNCAO DE CHUNKING ────────────────────────────────────────────────────────
def chunk_text(text, source_id, source_config, max_chunks=None):
    # Limpa header de metadados se houver
    content = re.sub(r'^#.*\n', '', text, flags=re.MULTILINE)
    content = content.strip().lstrip('-').strip()

    words = content.split()
    chunks = []
    i = 0

    while i < len(words):
        if max_chunks and len(chunks) >= max_chunks:
            print(f"  Limite de {max_chunks} chunks atingido para {source_id}")
            break

        chunk_words = words[i:i+CHUNK_SIZE]
        chunk_text_str = ' '.join(chunk_words)

        # Tenta terminar em ponto final
        if i + CHUNK_SIZE < len(words):
            extended = words[i:i+CHUNK_SIZE+50]
            ext_text = ' '.join(extended)
            last_period = max(ext_text.rfind('. '), ext_text.rfind('? '), ext_text.rfind('! '))
            if last_period > len(chunk_text_str) * 0.7:
                chunk_text_str = ext_text[:last_period+1]
                chunk_words = chunk_text_str.split()

        idx = len(chunks) + 1
        chunk_id = f"{source_id}_{idx:03d}"

        chunk = {
            "id_chunk": chunk_id,
            "conteudo": chunk_text_str.strip(),
            "pessoas": source_config["pessoas"],
            "temas": source_config["temas"],
            "meta": {
                "source_id": source_id,
                "source_person": source_config["person"],
                "source_type": source_config["type"],
                "source_title": source_config["title"],
                "source_path": source_config["path"],
                "source_datetime": source_config["datetime"],
                "scope": source_config["scope"],
                "corpus": source_config["corpus"],
                "chunk_index": idx,
                "word_count": len(chunk_text_str.split()),
            }
        }
        chunks.append(chunk)
        i += len(chunk_words)

    return chunks

# ── PROCESSA CADA FONTE ───────────────────────────────────────────────────────
new_sources_processed = 0
total_new_chunks = 0

for src in SOURCES:
    source_id = src["source_id"]

    if source_id in existing_sources:
        print(f"[SKIP] {source_id} ja esta no state ({sum(1 for c in state['chunks'] if c.get('meta',{}).get('source_id') == source_id)} chunks)")
        continue

    file_path = MEGABRAIN / src["path"]
    if not file_path.exists():
        print(f"[MISS] {source_id}: arquivo nao encontrado em {src['path']}")
        continue

    print(f"[PROC] {source_id}: {src['title'][:60]}...")

    # Le arquivo
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  ERRO ao ler: {e}")
        continue

    max_chunks = src.get("max_chunks")
    chunks = chunk_text(text, source_id, src, max_chunks)

    print(f"  -> {len(chunks)} chunks gerados")

    # Remove existentes (precaucao) e adiciona
    state["chunks"] = [c for c in state["chunks"] if c.get("meta", {}).get("source_id") != source_id]
    state["chunks"].extend(chunks)

    new_sources_processed += 1
    total_new_chunks += len(chunks)

# ── ATUALIZA META E SALVA ─────────────────────────────────────────────────────
if "meta" not in state:
    state["meta"] = {}
state["meta"]["last_updated"] = datetime.now().isoformat()
state["meta"]["total_chunks"] = len(state["chunks"])
state["meta"]["version"] = "v2"

CHUNKS_STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

print()
print("=" * 60)
print(f"CONCLUIDO")
print(f"Fontes novas processadas: {new_sources_processed}")
print(f"Chunks novos adicionados: {total_new_chunks}")
print(f"Total geral de chunks: {len(state['chunks'])}")
print("=" * 60)
