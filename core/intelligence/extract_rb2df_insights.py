"""Extract insights from Marketing Secrets Blackbook (RB2DF) — Russell Brunson"""
import json, datetime
from pathlib import Path

ROOT = Path("c:/Users/Gabriel/MEGABRAIN")
SOURCE_ID = "RB2DF"
SOURCE_PERSON = "Russell Brunson"
SOURCE_TITLE = "Marketing Secrets Blackbook"

insights = [
    # ─── FILOSOFIAS ───────────────────────────────────────────────────────
    {
        "id": "RB2DF-001",
        "tipo": "[FILOSOFIA]",
        "titulo": "Sua Opinião Não Importa — O Mercado Decide",
        "insight": "A opinião do empreendedor sobre sua oferta, copy ou produto é irrelevante. Apenas o mercado tem autoridade para validar. Testar e medir os dados reais é a única forma de saber o que funciona.",
        "priority": "HIGH",
        "confidence": 0.92,
        "chunks": ["chunk_RB2DF_010"],
        "tags": ["mercado", "teste", "validação", "dados"]
    },
    {
        "id": "RB2DF-002",
        "tipo": "[FILOSOFIA]",
        "titulo": "Vender É a Única Coisa que Importa",
        "insight": "Todo o marketing, conteúdo e branding serve apenas uma função: gerar vendas. Empreendedores que confundem 'criar conteúdo' com 'fazer negócio' ficam ocupados mas quebrados.",
        "priority": "HIGH",
        "confidence": 0.94,
        "chunks": ["chunk_RB2DF_044"],
        "tags": ["vendas", "foco", "resultado"]
    },
    {
        "id": "RB2DF-003",
        "tipo": "[FILOSOFIA]",
        "titulo": "Polarity — Polarizar é Necessário para Liderança",
        "insight": "Tentar agradar a todos é o caminho mais rápido para a invisibilidade. Líderes de mercado polarizam: têm fãs ardentes E críticos. A neutralidade não gera movimento nem compras.",
        "priority": "HIGH",
        "confidence": 0.91,
        "chunks": ["chunk_RB2DF_063"],
        "tags": ["posicionamento", "liderança", "movimento"]
    },
    {
        "id": "RB2DF-004",
        "tipo": "[FILOSOFIA]",
        "titulo": "Foco Composto — Um Negócio até Escalar",
        "insight": "95% dos empreendedores têm 3+ negócios simultaneamente. Isso é fatal. O foco em um único negócio cria efeito composto: cada lançamento, tráfego e oferta se acumula em um único ativo que cresce exponencialmente.",
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_RB2DF_133"],
        "tags": ["foco", "composto", "escala", "negócio"]
    },

    # ─── MODELOS MENTAIS ─────────────────────────────────────────────────
    {
        "id": "RB2DF-005",
        "tipo": "[MODELO-MENTAL]",
        "titulo": "Proteção de Prateleira — Ocupar Posição Antes do Concorrente",
        "insight": "Em toda categoria de mercado há espaço limitado de 'prateleira mental' nos clientes. O primeiro a ocupar uma posição específica se torna a referência padrão. Demorar a agir é ceder prateleira.",
        "priority": "HIGH",
        "confidence": 0.90,
        "chunks": ["chunk_RB2DF_060"],
        "tags": ["posicionamento", "categoria", "prateleira"]
    },
    {
        "id": "RB2DF-006",
        "tipo": "[MODELO-MENTAL]",
        "titulo": "Frame — Tudo em Vendas Começa com o Frame",
        "insight": "O frame (enquadramento) determina como o prospect interpreta toda comunicação. Um professor apresentado como 'caloroso' vs 'frio' recebe avaliações opostas pela mesma aula. Quem controla o frame controla a percepção e a venda.",
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_RB2DF_119"],
        "tags": ["frame", "percepção", "copy", "vendas"]
    },
    {
        "id": "RB2DF-007",
        "tipo": "[MODELO-MENTAL]",
        "titulo": "Oportunidade A vs B — Focar Apenas em A",
        "insight": "Oportunidades de nível B parecem atraentes mas roubam tempo de oportunidades A que realmente movem a empresa. A disciplina de dizer não para B define quem chega ao A. A maioria dos empreendedores é rica em oportunidades B e pobre em execução A.",
        "priority": "HIGH",
        "confidence": 0.89,
        "chunks": ["chunk_RB2DF_020"],
        "tags": ["priorização", "foco", "oportunidade"]
    },
    {
        "id": "RB2DF-008",
        "tipo": "[MODELO-MENTAL]",
        "titulo": "Semeadura + Colheita — Lei do Retorno do Marketing",
        "insight": "Todo marketing segue a lei da semeadura e colheita: você colhe apenas o que planta, e o retorno demora. Empreendedores que esperam colher sem semear (criar conteúdo, nutrir lista, construir relacionamentos) ficam frustrados.",
        "priority": "HIGH",
        "confidence": 0.88,
        "chunks": ["chunk_RB2DF_067"],
        "tags": ["marketing", "conteúdo", "relacionamento", "paciência"]
    },
    {
        "id": "RB2DF-009",
        "tipo": "[MODELO-MENTAL]",
        "titulo": "KPIs do Funil — 4 Métricas que Tudo Determinam",
        "insight": "Todo funil tem 4 KPIs fundamentais: (1) Tráfego — quantas pessoas entram; (2) Assinantes — quantas viram leads; (3) Vendas — quantas compram; (4) Membros Ativos — quantas consomem mais. Monitorar os 4 semanalmente é o único jeito de otimizar.",
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_RB2DF_086"],
        "tags": ["KPI", "métricas", "funil", "otimização"]
    },

    # ─── HEURISTICAS ─────────────────────────────────────────────────────
    {
        "id": "RB2DF-010",
        "tipo": "[HEURISTICA]",
        "titulo": "Zona Prolífica — Publicar Diariamente sem Perfeccionismo",
        "insight": "A 'Zona Prolífica' é o estado de criar e publicar conteúdo consistentemente sem esperar perfeição. Criadores que publicam diariamente por 1 ano superam criadores perfeccionistas que publicam mensalmente. Quantidade gera qualidade.",
        "threshold": "Publicar diariamente por 30 dias mínimo para encontrar a zona",
        "priority": "HIGH",
        "confidence": 0.91,
        "chunks": ["chunk_RB2DF_030"],
        "tags": ["conteúdo", "consistência", "zona prolífica", "publicar"]
    },
    {
        "id": "RB2DF-011",
        "tipo": "[HEURISTICA]",
        "titulo": "Urgência + Escassez — Obrigatório para Fechar",
        "insight": "Sem urgência ou escassez genuína, qualquer apresentação vira conteúdo educativo. A escassez artificial (fechar carrinho) consistentemente aumenta conversões. Experimento das cartas: a carta com escassez artificial vendeu mais que sem.",
        "threshold": "Urgência obrigatória. Sem ela, conversão cai 60%+",
        "priority": "HIGH",
        "confidence": 0.95,
        "chunks": ["chunk_RB2DF_073"],
        "tags": ["urgência", "escassez", "conversão", "fechamento"]
    },
    {
        "id": "RB2DF-012",
        "tipo": "[HEURISTICA]",
        "titulo": "Precificação Chamariz (Decoy Pricing) — 3 Opções com Âncora",
        "insight": "Oferecer 3 opções de preço onde a do meio é o alvo. A opção cara (chamariz) faz a do meio parecer razoável. A opção básica serve de âncora baixa. Sem chamariz, clientes comparam só com a opção cara e sentem resistência.",
        "threshold": "3 opções: básica (âncora baixa), alvo (lucro real), premium (chamariz). Converte 30-40% mais que 1 opção.",
        "priority": "HIGH",
        "confidence": 0.92,
        "chunks": ["chunk_RB2DF_165"],
        "tags": ["pricing", "precificação", "chamariz", "ancoragem"]
    },
    {
        "id": "RB2DF-013",
        "tipo": "[HEURISTICA]",
        "titulo": "Empilhar não Trocar — Sempre Adicionar Nova Oportunidade",
        "insight": "Quando uma oferta para de funcionar, a solução nunca é 'melhorar o mesmo produto' — é apresentar uma nova oportunidade. Melhorar o produto atual é troca de oportunidade (o cliente sente que errou antes). Nova oportunidade é empilhamento.",
        "threshold": "Oferta nova > Oferta melhorada. Melhoria da oferta existente aumenta resistência.",
        "priority": "HIGH",
        "confidence": 0.91,
        "chunks": ["chunk_RB2DF_142"],
        "tags": ["nova oportunidade", "oferta", "resistência", "empilhar"]
    },
    {
        "id": "RB2DF-014",
        "tipo": "[HEURISTICA]",
        "titulo": "O Que Você Mede Cresce — KPI Semanal Obrigatório",
        "insight": "Peter Drucker: o que não é medido não é gerenciado. Em marketing, métricas que você rastreia semanalmente melhoram automaticamente porque você inconscientemente adapta comportamentos para melhorá-las.",
        "threshold": "Revisar KPIs 1x por semana mínimo. Sem revisão semanal, as métricas não melhoram.",
        "priority": "HIGH",
        "confidence": 0.90,
        "chunks": ["chunk_RB2DF_017"],
        "tags": ["métricas", "KPI", "crescimento", "gestão"]
    },
    {
        "id": "RB2DF-015",
        "tipo": "[HEURISTICA]",
        "titulo": "Power of Continuity — Receita Recorrente no Backend",
        "insight": "Todo negócio precisa de um produto de continuidade (assinatura) porque gera receita previsível e aumenta LTV. Frontend converte; continuidade retém. Sem continuidade, o negócio reinicia do zero todo mês.",
        "threshold": "Continuidade = 3-5x LTV vs venda única. Sem continuidade, escala é instável.",
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_RB2DF_148"],
        "tags": ["continuidade", "assinatura", "LTV", "backend"]
    },
    {
        "id": "RB2DF-016",
        "tipo": "[HEURISTICA]",
        "titulo": "Guru na Montanha — Distância Cria Percepção de Valor",
        "insight": "Quanto mais acessível você é, menos você é percebido como autoridade. O modelo de Dan Kennedy: criar distância entre você e o público faz as pessoas pagarem mais para se aproximar. Cada nível da Value Ladder aproxima um pouco mais.",
        "threshold": "Acessibilidade irrestrita reduz percepção de valor em 40-60%.",
        "priority": "HIGH",
        "confidence": 0.89,
        "chunks": ["chunk_RB2DF_033"],
        "tags": ["autoridade", "distância", "valor", "Dan Kennedy"]
    },

    # ─── FRAMEWORKS ──────────────────────────────────────────────────────
    {
        "id": "RB2DF-017",
        "tipo": "[FRAMEWORK]",
        "titulo": "Attractive Character — 4 Elementos da Persona do Fundador",
        "insight": "O Attractive Character tem 4 elementos: (1) Backstory — origem e jornada; (2) Parabolismo — ensinar com histórias, não dados; (3) Falhas/fraquezas — humanizar; (4) Polaridade — ter posições definidas. Sem AC, o negócio é uma commodity sem rosto.",
        "priority": "HIGH",
        "confidence": 0.95,
        "chunks": ["chunk_RB2DF_077"],
        "tags": ["attractive character", "persona", "storytelling", "polaridade"]
    },
    {
        "id": "RB2DF-018",
        "tipo": "[FRAMEWORK]",
        "titulo": "As Duas Jornadas do Herói — Interna + Externa",
        "insight": "Todo cliente vive duas jornadas: (1) Externa — o problema visível (perder peso, ganhar dinheiro); (2) Interna — a identidade que quer construir (ser visto como alguém de sucesso). Vender apenas para a jornada externa é insuficiente. O produto deve entregar ambas.",
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_RB2DF_080"],
        "tags": ["jornada do herói", "identidade", "transformação", "storytelling"]
    },
    {
        "id": "RB2DF-019",
        "tipo": "[FRAMEWORK]",
        "titulo": "Underachiever Method — Criar Expectativas Baixas, Surpreender com Alto",
        "insight": "Crie expectativas abaixo do que você vai entregar. O cliente que espera 'B' e recebe 'A' evangeliza. O cliente que espera 'A' e recebe 'A' fica satisfeito. A surpresa positiva é o motor do boca-a-boca e retenção.",
        "priority": "HIGH",
        "confidence": 0.88,
        "chunks": ["chunk_RB2DF_054"],
        "tags": ["expectativa", "retenção", "surpresa", "boca-a-boca"]
    },
    {
        "id": "RB2DF-020",
        "tipo": "[FRAMEWORK]",
        "titulo": "Posicionamento Mortal — 3 Crimes que Matam Negócios",
        "insight": "Os 3 crimes do posicionamento: (1) Ser 'igual ao concorrente mas melhor' — commodity; (2) Não ter posicionamento específico — invisível; (3) Mudar o posicionamento com frequência — confunde o mercado. Posicionamento claro e consistente = autoridade.",
        "priority": "HIGH",
        "confidence": 0.91,
        "chunks": ["chunk_RB2DF_089"],
        "tags": ["posicionamento", "diferenciação", "autoridade", "commodity"]
    },
    {
        "id": "RB2DF-021",
        "tipo": "[FRAMEWORK]",
        "titulo": "Construção de Cultura — 3 Elementos do Movimento",
        "insight": "Para construir cultura (movimento) é necessário: (1) Futuro profético — visão do mundo que o líder quer criar; (2) Identidade compartilhada — quem 'nós' somos; (3) Causa além do produto — por que importa. Clientes que compram o movimento não precisam ser re-vendidos.",
        "priority": "HIGH",
        "confidence": 0.90,
        "chunks": ["chunk_RB2DF_084"],
        "tags": ["cultura", "movimento", "identidade", "causa"]
    },

    # ─── METODOLOGIAS ────────────────────────────────────────────────────
    {
        "id": "RB2DF-022",
        "tipo": "[METODOLOGIA]",
        "titulo": "Tornar-se Comprador para Tornar-se Vendedor",
        "insight": "Para dominar qualquer mercado, o empreendedor deve primeiro estudar os melhores como comprador: comprar os produtos dos concorrentes, entrar nos funis deles, observar a experiência completa. Só assim você consegue modelar e superar.",
        "priority": "HIGH",
        "confidence": 0.89,
        "chunks": ["chunk_RB2DF_024"],
        "tags": ["pesquisa", "modelagem", "funil", "concorrente"]
    },
    {
        "id": "RB2DF-023",
        "tipo": "[METODOLOGIA]",
        "titulo": "Década em Um Dia — Aprender com Mentores vs Experiência",
        "insight": "Em vez de aprender por tentativa e erro (leva décadas), estudar mentores que já passaram pelo caminho comprime o aprendizado. 1 dia com o mentor certo = 10 anos de experiência. A seleção do mentor é a decisão mais alavancada.",
        "priority": "HIGH",
        "confidence": 0.88,
        "chunks": ["chunk_RB2DF_109"],
        "tags": ["mentoria", "aprendizado", "alavancagem", "modelagem"]
    },
    {
        "id": "RB2DF-024",
        "tipo": "[METODOLOGIA]",
        "titulo": "O Que Fazer ANTES de Criar — Validar com Pré-venda",
        "insight": "Antes de criar qualquer produto, validar com pré-venda: vender a ideia antes de existir. Se não vende como ideia, não vai vender como produto. Isso elimina o risco de criar algo que ninguém quer e força o empreendedor a dominar o pitch.",
        "priority": "HIGH",
        "confidence": 0.92,
        "chunks": ["chunk_RB2DF_027"],
        "tags": ["validação", "pré-venda", "produto", "lançamento"]
    },
    {
        "id": "RB2DF-025",
        "tipo": "[METODOLOGIA]",
        "titulo": "Controle de Estado — Gerenciar Energia Antes de Vender",
        "insight": "O estado emocional do vendedor/apresentador contamina o estado do público. Antes de qualquer apresentação ou lançamento, gerenciar o estado (energia, foco, crença) é pré-requisito. Tony Robbins: estado precede resultado.",
        "priority": "HIGH",
        "confidence": 0.87,
        "chunks": ["chunk_RB2DF_120"],
        "tags": ["estado", "energia", "apresentação", "convicção", "Tony Robbins"]
    }
]

# Load and update INSIGHTS-STATE.json
insights_path = ROOT / "processing/insights/INSIGHTS-STATE.json"
with open(insights_path, "r", encoding="utf-8") as f:
    state = json.load(f)

if "persons" not in state["insights_state"]:
    state["insights_state"]["persons"] = {}

person_key = SOURCE_PERSON
if person_key not in state["insights_state"]["persons"]:
    state["insights_state"]["persons"][person_key] = []

person_data = state["insights_state"]["persons"][person_key]
if isinstance(person_data, list):
    existing_list = person_data
elif isinstance(person_data, dict):
    existing_list = person_data.get("insights", [])
else:
    existing_list = []

existing_ids = {i["id"] for i in existing_list}

new_count = 0
for insight in insights:
    if insight["id"] not in existing_ids:
        insight["source_id"] = SOURCE_ID
        insight["source_person"] = SOURCE_PERSON
        insight["timestamp"] = datetime.datetime.now().isoformat()
        existing_list.append(insight)
        new_count += 1

if isinstance(state["insights_state"]["persons"][person_key], list):
    state["insights_state"]["persons"][person_key] = existing_list
else:
    state["insights_state"]["persons"][person_key]["insights"] = existing_list

if "change_log" not in state["insights_state"]:
    state["insights_state"]["change_log"] = []

state["insights_state"]["change_log"].append({
    "date": "2026-03-09",
    "source_id": SOURCE_ID,
    "source_person": SOURCE_PERSON,
    "action": "insights_added",
    "count": new_count
})

with open(insights_path, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print(f"Added {new_count} insights for {SOURCE_PERSON} from {SOURCE_TITLE}")
total = len(existing_list)
print(f"Total insights for {SOURCE_PERSON}: {total}")

# Print distribution
from collections import Counter
tipos = Counter(i["tipo"] for i in insights)
print("\nDistribution:")
for tipo, count in sorted(tipos.items()):
    print(f"  {tipo}: {count}")
