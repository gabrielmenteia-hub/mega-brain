"""
Insight extraction: V4 Looking Ahead 2026 - Dia 2
Speakers: Flávio Augusto, Lázaro do Carmo, William Barnett (Professor Stanford)
"""
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
INSIGHTS_PATH = BASE_DIR / "processing" / "insights" / "INSIGHTS-STATE.json"
SOURCE_ID = "V4C002"
TODAY = "2026-03-07"

with open(INSIGHTS_PATH, encoding="utf-8") as f:
    state = json.load(f)

persons = state.setdefault("insights_state", {}).setdefault("persons", {})

# ─── FLÁVIO AUGUSTO ────────────────────────────────────────────────────────────
FA_INSIGHTS = [
    {
        "id": "V4C002_FA_001",
        "insight": "[FILOSOFIA] Toda empresa — independente do tamanho — precisa de um ritual de execução semanal. Toda segunda-feira: ritual de cobrança de plano tático. 'O que você fez semana passada que vai me levar pro resultado tal?' Sem plano, você vira culto, não empresa.",
        "tags": ["execução", "ritual", "gestão", "planejamento", "cultura"],
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_V4C002_021", "chunk_V4C002_022"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C002_FA_002",
        "insight": "[HEURISTICA] 50% de crescimento exige 50% de fatos novos. Para crescer 50%, você precisa de 50% de novidades: canais de distribuição novos, produto novo, estratégia nova, pessoas novas. Crescimento não vem da mesma equipe fazendo a mesma coisa mais rápido.",
        "tags": ["crescimento", "inovação", "escala", "estratégia", "heurística"],
        "priority": "HIGH",
        "confidence": 0.95,
        "chunks": ["chunk_V4C002_025"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C002_FA_003",
        "insight": "[HEURISTICA] 8 prioridades culturais inegociáveis no negócio — resultado final é a primeira. 'Porra, isso não é ONG.' Cultura de resultado não é cruel — é clareza. Quem confunde bondade com ausência de cobrança cria mediocridade.",
        "tags": ["cultura", "resultado", "cobrança", "liderança", "valores"],
        "priority": "HIGH",
        "confidence": 0.91,
        "chunks": ["chunk_V4C002_020"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C002_FA_004",
        "insight": "[METODOLOGIA] Referência com candidato presente: na hora de contratar, ligar para a referência no viva-voz com o candidato na sala. A referência fala mal? O candidato tem direito de réplica. Isso revela caráter e filtra quem não tem capacidade de se defender.",
        "tags": ["contratação", "referência", "seleção", "metodologia", "RH"],
        "priority": "HIGH",
        "confidence": 0.92,
        "chunks": ["chunk_V4C002_027"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C002_FA_005",
        "insight": "[MODELO-MENTAL] 'Cada um tem o competente que contrata e o incompetente que tolera.' Mediocridade no time é sempre uma escolha do líder. Intolerância com incompetência não é crueldade — é respeito pelo padrão que você prometeu.",
        "tags": ["liderança", "contratação", "padrão", "mediocridade", "tolerância"],
        "priority": "HIGH",
        "confidence": 0.94,
        "chunks": ["chunk_V4C002_025"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C002_FA_006",
        "insight": "[MODELO-MENTAL] Líder não precisa de reunião para saber da própria área. 'Se eu contratar um cara e precisar marcar reunião para ele me apresentar a área, tá ruim.' O gestor competente domina a área proativamente — não espera ser convocado.",
        "tags": ["gestão", "liderança", "accountability", "autonomia", "proatividade"],
        "priority": "MEDIUM",
        "confidence": 0.89,
        "chunks": ["chunk_V4C002_028"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C002_FA_007",
        "insight": "[HEURISTICA] Cabeça de dono: 5 atributos inegociáveis ao avaliar um gestor — cabeça de dono, disponibilidade, foco no processo, energia e atitude. Sem os 5, o cargo não sustenta.",
        "tags": ["contratação", "liderança", "cabeça-de-dono", "avaliação", "gestão"],
        "priority": "MEDIUM",
        "confidence": 0.88,
        "chunks": ["chunk_V4C002_019"],
        "source_id": SOURCE_ID,
    },
]

# ─── LÁZARO DO CARMO ──────────────────────────────────────────────────────────
LC_INSIGHTS = [
    {
        "id": "V4C002_LC_001",
        "insight": "[FILOSOFIA] O maior líder torce para ser superado. 'Eu sou o único homem que reza para você me superar todos os dias.' Liderança que não multiplica é egoísmo disfarçado de proteção. O critério de sucesso de um líder é criar líderes melhores que ele.",
        "tags": ["liderança", "multiplicação", "desenvolvimento", "filosofia", "sucessão"],
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_V4C002_033"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C002_LC_002",
        "insight": "[HEURISTICA] Identificar talento por atitude, não por currículo. A jovem que entrou na sala e disse direto o que queria — Lázaro contratou na hora. Talento declarado com clareza e coragem vale mais que experiência com timidez.",
        "tags": ["contratação", "talento", "atitude", "jovens", "identificação"],
        "priority": "HIGH",
        "confidence": 0.90,
        "chunks": ["chunk_V4C002_030", "chunk_V4C002_031"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C002_LC_003",
        "insight": "[MODELO-MENTAL] Liderança velha não se reforma — se substitui. 'Não tem tempo. Tenho que tirar a liderança e botar outra, a não ser que o cara seja jovem.' Depois de certa idade, padrões mentais estão cristalizados. Transformação real só vem de gente moldável.",
        "tags": ["liderança", "substituição", "cultura", "mudança", "gestão"],
        "priority": "HIGH",
        "confidence": 0.88,
        "chunks": ["chunk_V4C002_029"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C002_LC_004",
        "insight": "[METODOLOGIA] Multiplicar faturamento via distribuição. Lázaro multiplicou faturamento da Jequiti de R$X milhões para R$520 milhões via estratégia de distribuição e capital. O produto não mudou — a capacidade de chegar ao mercado mudou.",
        "tags": ["distribuição", "faturamento", "capital", "crescimento", "case"],
        "priority": "MEDIUM",
        "confidence": 0.87,
        "chunks": ["chunk_V4C002_035"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C002_LC_005",
        "insight": "[FILOSOFIA] Competir com irmão ou sócio familiar é perda de energia. 'Já que meu irmão vai fazer isso tudo, eu vou trabalhar para ele.' Complementaridade bate competição dentro da mesma família. Cada um ocupando o papel onde é melhor.",
        "tags": ["família", "sociedade", "complementaridade", "conflito", "sucessão"],
        "priority": "MEDIUM",
        "confidence": 0.85,
        "chunks": ["chunk_V4C002_033"],
        "source_id": SOURCE_ID,
    },
]

# ─── WILLIAM BARNETT ──────────────────────────────────────────────────────────
WB_INSIGHTS = [
    {
        "id": "V4C002_WB_001",
        "insight": "[FRAMEWORK] Dissidência vs Consenso — o padrão de todas as grandes empresas. Google, Alibaba, Apple, Spotify, Honda: todas eram 'loucas' no início. 'Crazy Jack' = Jack Ma. As empresas que definiram o futuro foram aquelas que quebraram o consenso, não as que o seguiram.",
        "tags": ["dissidência", "consenso", "inovação", "estratégia", "vantagem-competitiva"],
        "priority": "HIGH",
        "confidence": 0.96,
        "chunks": ["chunk_V4C002_068", "chunk_V4C002_073", "chunk_V4C002_081"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C002_WB_002",
        "insight": "[MODELO-MENTAL] Jack Ma criou Alipay para resolver o problema não-resolvido (chineses sem cartão de crédito) — não para ganhar dinheiro. Taobao foi criado para manter o eBay fora da China. Quando você resolve um problema que ninguém mais resolveu, você cria monopólio de fato.",
        "tags": ["Jack Ma", "Alibaba", "resolução-de-problemas", "monopólio", "inovação"],
        "priority": "HIGH",
        "confidence": 0.94,
        "chunks": ["chunk_V4C002_070", "chunk_V4C002_073"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C002_WB_003",
        "insight": "[FILOSOFIA] O próprio Barnett disse ao Jack Ma que ele iria fracassar — e errou. Os especialistas são ruins em prever o futuro dos dissidentes porque usam as regras do presente para avaliar quem está construindo o futuro. 'Nós somos ruins na parte de previsão.'",
        "tags": ["previsão", "fracasso", "Jack Ma", "especialistas", "epistemologia"],
        "priority": "HIGH",
        "confidence": 0.92,
        "chunks": ["chunk_V4C002_070"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C002_WB_004",
        "insight": "[METODOLOGIA] Liderar por design — não é seu trabalho prever o futuro. É criar as condições para que inovação aconteça. Punir falhas bloqueia o futuro. Permitir falhas no caminho certo abre o espaço para os dissidentes internos emergirem.",
        "tags": ["liderança", "inovação", "cultura", "falha", "design-organizacional"],
        "priority": "HIGH",
        "confidence": 0.91,
        "chunks": ["chunk_V4C002_083", "chunk_V4C002_085"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C002_WB_005",
        "insight": "[MODELO-MENTAL] Steve Jobs: 'Você não pode conectar os pontos olhando para frente — só olhando para trás.' O discurso de Stanford de Jobs: a narrativa coerente do sucesso só existe em retrospecto. Dissidentes não têm roadmap — têm convicção e tolerância ao caos.",
        "tags": ["Steve Jobs", "retrospecto", "narrativa", "convicção", "mindset"],
        "priority": "MEDIUM",
        "confidence": 0.90,
        "chunks": ["chunk_V4C002_087", "chunk_V4C002_119"],
        "source_id": SOURCE_ID,
    },
    {
        "id": "V4C002_WB_006",
        "insight": "[HEURISTICA] Quando KPIs viram punição, criatividade morre. 'Quando seu pessoal fracassa, vocês reprimem eles, vocês dão KPIs. Se não alcançam, têm problemas com salário ou são demitidos.' Esse sistema seleciona conformidade, não inovação.",
        "tags": ["KPI", "métricas", "inovação", "cultura", "punição"],
        "priority": "MEDIUM",
        "confidence": 0.89,
        "chunks": ["chunk_V4C002_083"],
        "source_id": SOURCE_ID,
    },
]

# ─── SAVE TO INSIGHTS-STATE ───────────────────────────────────────────────────
SPEAKER_MAP = {
    "Flávio Augusto": FA_INSIGHTS,
    "Lázaro do Carmo": LC_INSIGHTS,
    "William Barnett": WB_INSIGHTS,
}

total_added = 0
for person_name, insight_list in SPEAKER_MAP.items():
    if person_name not in persons:
        persons[person_name] = {"insights": []}

    # Handle both list and dict formats
    existing = persons[person_name]
    if isinstance(existing, list):
        persons[person_name] = {"insights": existing}

    existing_ids = {ins.get("id") for ins in persons[person_name].get("insights", [])}
    new = [ins for ins in insight_list if ins["id"] not in existing_ids]

    persons[person_name].setdefault("insights", []).extend(new)
    total_added += len(new)
    print(f"  {person_name}: +{len(new)} insights")

state["insights_state"].setdefault("change_log", []).append({
    "timestamp": datetime.now().isoformat(),
    "source_id": SOURCE_ID,
    "action": "INSIGHT_EXTRACTION",
    "persons_updated": list(SPEAKER_MAP.keys()),
    "insights_added": total_added,
})

with open(INSIGHTS_PATH, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

# Count total safely
total_in_state = 0
for p_data in persons.values():
    if isinstance(p_data, dict):
        total_in_state += len(p_data.get("insights", []))
    elif isinstance(p_data, list):
        total_in_state += len(p_data)

print(f"\nTotal insights added: {total_added}")
print(f"Total insights in state: {total_in_state}")
