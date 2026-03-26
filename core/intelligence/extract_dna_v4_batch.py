"""
DNA Extraction - Batch para todos os speakers V4C001 + V4C002
Persons: Dener Lippert, Rami Goldratt, Thiago Nigro, Andre Kliousoff,
         Flávio Augusto, Lázaro do Carmo, William Barnett
"""
import json
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
INSIGHTS_PATH = BASE_DIR / "processing" / "insights" / "INSIGHTS-STATE.json"
DOSSIER_DIR = BASE_DIR / "knowledge" / "dossiers" / "persons"
DNA_DIR = BASE_DIR / "knowledge" / "dna" / "persons"

insights_state = json.loads(INSIGHTS_PATH.read_text(encoding="utf-8"))
persons_insights = insights_state["insights_state"]["persons"]

TODAY = "2026-03-07"

# ── Tag → DNA layer mapping ───────────────────────────────────────────────────
TAG_TO_LAYER = {
    "[FILOSOFIA]": "FILOSOFIAS",
    "[MODELO-MENTAL]": "MODELOS-MENTAIS",
    "[HEURISTICA]": "HEURISTICAS",
    "[FRAMEWORK]": "FRAMEWORKS",
    "[METODOLOGIA]": "METODOLOGIAS",
}

# ── Weight calculator ─────────────────────────────────────────────────────────
def calc_weight(insight: dict) -> float:
    w = 0.50
    text = insight.get("insight", "")
    # Has chunk reference
    if insight.get("chunks"):
        w += 0.15
    # High priority
    if insight.get("priority") == "HIGH":
        w += 0.10
    # Numeric threshold in text
    if re.search(r'\d+[%km]|\d+\s*(mil|bilh|vezes|dias|horas|meses)', text, re.I):
        w += 0.10
    # Prescriptive language
    if any(kw in text.lower() for kw in ["sempre", "nunca", "obrigatório", "exige", "precisa"]):
        w += 0.05
    # High confidence
    if insight.get("confidence", 0) >= 0.90:
        w += 0.05
    # Inferred / low confidence
    if insight.get("confidence", 1) < 0.70:
        w -= 0.20
    return round(min(w, 1.0), 2)


def detect_layer(insight_text: str) -> str:
    for tag, layer in TAG_TO_LAYER.items():
        if insight_text.startswith(tag):
            return layer
    return "FILOSOFIAS"  # fallback


def slugify(name: str) -> str:
    return name.lower().replace(" ", "-").replace("&", "and")


def extract_title(insight_text: str) -> str:
    """Extract a short title from the insight text."""
    # Remove layer tag
    text = re.sub(r'^\[[\w-]+\]\s*', '', insight_text)
    # Take first sentence or up to 60 chars
    first = text.split('.')[0].split(' — ')[0]
    return first[:80].strip()


# ── Process each person ───────────────────────────────────────────────────────
PERSONS = {
    "Dener Lippert": "dener-lippert",
    "Rami Goldratt": "rami-goldratt",
    "Thiago Nigro": "thiago-nigro",
    "Andre Kliousoff": "andre-kliousoff",
    "Flávio Augusto": "flavio-augusto",
    "Lázaro do Carmo": "lazaro-do-carmo",
    "William Barnett": "william-barnett",
}

all_stats = {}

for person_name, person_slug in PERSONS.items():
    print(f"\n{'='*60}")
    print(f"Processing: {person_name}")

    # Load insights
    raw = persons_insights.get(person_name, {})
    if isinstance(raw, dict):
        insight_list = raw.get("insights", [])
    else:
        insight_list = raw

    if not insight_list:
        print(f"  SKIP: no insights found")
        continue

    # Load dossier for narrative context
    dossier_path = DOSSIER_DIR / f"DOSSIER-{person_name.upper().replace(' ', '-')}.md"
    if not dossier_path.exists():
        # Try alternate naming
        slug_upper = person_slug.upper()
        dossier_path = DOSSIER_DIR / f"DOSSIER-{slug_upper}.md"

    dossier_text = dossier_path.read_text(encoding="utf-8") if dossier_path.exists() else ""

    # Bucket insights by layer
    layers = {
        "FILOSOFIAS": [],
        "MODELOS-MENTAIS": [],
        "HEURISTICAS": [],
        "FRAMEWORKS": [],
        "METODOLOGIAS": [],
    }

    for ins in insight_list:
        layer = detect_layer(ins.get("insight", ""))
        layers[layer].append(ins)

    # Create DNA directory
    dna_path = DNA_DIR / person_slug
    dna_path.mkdir(parents=True, exist_ok=True)

    layer_counts = {}

    for layer_name, items in layers.items():
        if not items:
            layer_counts[layer_name] = 0
            # Write empty yaml
            yaml_content = f"""versao: "1.0.0"
pessoa: "{person_name}"
camada: "{layer_name}"
total_itens: 0
itens: []
metadados:
  criado_em: "{TODAY}"
  protocolo: "DNA-EXTRACTION-PROTOCOL v1.0"
  pipeline: "extract_dna_v4_batch.py"
  source_ids: ["{insight_list[0].get('source_id', 'V4C001')}"]
"""
        else:
            yaml_items = []
            for i, ins in enumerate(items, 1):
                weight = calc_weight(ins)
                title = extract_title(ins.get("insight", ""))
                chunk_refs = ins.get("chunks", [])
                item_id = f"{ins.get('id', f'UNKNOWN_{i}')}"

                yaml_items.append(f"""  - id: "{item_id}"
    titulo: "{title.replace(chr(34), chr(39))}"
    descricao: >
      {ins.get('insight', '').replace(chr(34), chr(39))}
    peso: {weight}
    priority: "{ins.get('priority', 'MEDIUM')}"
    confidence: {ins.get('confidence', 0.85)}
    tags: {json.dumps(ins.get('tags', []), ensure_ascii=False)}
    chunks: {json.dumps(chunk_refs, ensure_ascii=False)}
    source_id: "{ins.get('source_id', '')}" """)

            source_ids = list(set(i.get("source_id", "") for i in items))
            items_yaml = "\n".join(yaml_items)
            yaml_content = f"""versao: "1.0.0"
pessoa: "{person_name}"
camada: "{layer_name}"
total_itens: {len(items)}
itens:
{items_yaml}
metadados:
  criado_em: "{TODAY}"
  protocolo: "DNA-EXTRACTION-PROTOCOL v1.0"
  pipeline: "extract_dna_v4_batch.py"
  source_ids: {json.dumps(source_ids, ensure_ascii=False)}
"""
            layer_counts[layer_name] = len(items)

        (dna_path / f"{layer_name}.yaml").write_text(yaml_content, encoding="utf-8")

    # Extract TL;DR from dossier
    tldr = ""
    if dossier_text:
        m = re.search(r'## TL;DR\s*\n(.*?)(?=\n---|\n##)', dossier_text, re.DOTALL)
        if m:
            tldr = m.group(1).strip()[:400]

    # CONFIG.yaml
    total_items = sum(layer_counts.values())
    all_weights = [calc_weight(ins) for ins in insight_list]
    avg_weight = round(sum(all_weights) / len(all_weights), 2) if all_weights else 0.0

    high_count = sum(1 for ins in insight_list if ins.get("priority") == "HIGH")
    source_ids_all = list(set(i.get("source_id", "") for i in insight_list))

    config = f"""versao: "1.0.0"
pessoa: "{person_name}"
nome_canonico: "{person_name}"
slug: "{person_slug}"

sintese_narrativa: >
  {tldr.replace(chr(34), chr(39)).replace(chr(10), ' ')}

estatisticas:
  filosofias: {layer_counts.get('FILOSOFIAS', 0)}
  modelos_mentais: {layer_counts.get('MODELOS-MENTAIS', 0)}
  heuristicas: {layer_counts.get('HEURISTICAS', 0)}
  frameworks: {layer_counts.get('FRAMEWORKS', 0)}
  metodologias: {layer_counts.get('METODOLOGIAS', 0)}
  total_itens: {total_items}
  insights_high: {high_count}
  peso_medio_geral: {avg_weight}

fontes:
  source_ids: {json.dumps(source_ids_all, ensure_ascii=False)}
  dossier: "knowledge/dossiers/persons/DOSSIER-{person_name.upper().replace(' ', '-')}.md"
  total_insights: {len(insight_list)}

metadados:
  criado_em: "{TODAY}"
  protocolo: "DNA-EXTRACTION-PROTOCOL v1.0"
  pipeline: "extract_dna_v4_batch.py"
  trigger: "manual + densidade >= 3/5"

changelog:
  - data: "{TODAY}"
    acao: "Criação automática do DNA"
    itens_adicionados: {total_items}
    versao: "1.0.0"
"""

    (dna_path / "CONFIG.yaml").write_text(config, encoding="utf-8")

    all_stats[person_name] = {
        "total": total_items,
        "layers": layer_counts,
        "avg_weight": avg_weight,
        "high": high_count,
    }

    print(f"  FILOSOFIAS:     {layer_counts.get('FILOSOFIAS', 0)}")
    print(f"  MODELOS-MENTAIS:{layer_counts.get('MODELOS-MENTAIS', 0)}")
    print(f"  HEURISTICAS:    {layer_counts.get('HEURISTICAS', 0)}")
    print(f"  FRAMEWORKS:     {layer_counts.get('FRAMEWORKS', 0)}")
    print(f"  METODOLOGIAS:   {layer_counts.get('METODOLOGIAS', 0)}")
    print(f"  TOTAL: {total_items} itens | peso médio: {avg_weight} | HIGH: {high_count}")
    print(f"  -> {dna_path}")

# ── Final report ──────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("DNA EXTRACTION COMPLETE")
print(f"{'='*60}")
for person, stats in all_stats.items():
    print(f"  {person:30s} {stats['total']:3d} itens | peso médio: {stats['avg_weight']}")
print(f"\nTotal pessoas: {len(all_stats)}")
print(f"Total itens DNA: {sum(s['total'] for s in all_stats.values())}")
