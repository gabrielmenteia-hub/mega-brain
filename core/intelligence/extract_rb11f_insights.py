"""Extract insights from Lead Funnels (RB11F) — Russell Brunson"""
import json, datetime
from pathlib import Path

ROOT = Path("c:/Users/Gabriel/MEGABRAIN")
SOURCE_ID = "RB11F"
SOURCE_PERSON = "Russell Brunson"
SOURCE_TITLE = "Lead Funnels"

insights = [
    # ─── FILOSOFIAS ───────────────────────────────────────────────────────
    {
        "id": "RB11F-001",
        "tipo": "[FILOSOFIA]",
        "titulo": "Todo Negócio Precisa de Leads ou Clientes",
        "insight": "Toda empresa tem apenas dois problemas: falta de leads ou falta de clientes. Um lead funnel resolve o primeiro. Se o negócio tem leads mas não clientes, o problema é o funil de conversão, não o lead magnet. Esta é a única divisão diagnóstica que importa.",
        "priority": "HIGH",
        "confidence": 0.92,
        "chunks": ["chunk_RB11F_001"],
        "tags": ["leads", "clientes", "diagnóstico", "funil"]
    },
    {
        "id": "RB11F-002",
        "tipo": "[FILOSOFIA]",
        "titulo": "Lista é o Único Ativo que Você Controla",
        "insight": "Tráfego pago depende de plataformas. SEO depende de algoritmos. Mas a lista de email é um ativo próprio — você pode enviar uma mensagem para toda a lista a qualquer momento, independente de algoritmos ou custos de anúncio. Construir a lista é construir o negócio.",
        "priority": "HIGH",
        "confidence": 0.95,
        "chunks": ["chunk_RB11F_004"],
        "tags": ["lista", "email", "ativo próprio", "tráfego"]
    },

    # ─── MODELOS MENTAIS ─────────────────────────────────────────────────
    {
        "id": "RB11F-003",
        "tipo": "[MODELO-MENTAL]",
        "titulo": "Lead Magnet — Atrair com Valor para Capturar Permissão",
        "insight": "Lead magnet não é isca gratuita — é a primeira troca de valor. O lead dá o email; você entrega algo que resolve uma dor específica imediata. Quanto mais específico o lead magnet (para um problema real de uma pessoa real), maior a taxa de opt-in.",
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_RB11F_010"],
        "tags": ["lead magnet", "opt-in", "valor", "especificidade"]
    },
    {
        "id": "RB11F-004",
        "tipo": "[MODELO-MENTAL]",
        "titulo": "Hook, Story, Offer — Estrutura da Squeeze Page",
        "insight": "Toda página de captura tem 3 partes: (1) Hook — título que captura atenção e promete resultado específico; (2) Story — por que isso é credível e urgente; (3) Offer — o lead magnet em si. Páginas sem hook claro têm opt-in rate < 20%. Com hook otimizado: 40-60%.",
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_RB11F_015"],
        "tags": ["squeeze page", "hook", "opt-in rate", "headline"]
    },
    {
        "id": "RB11F-005",
        "tipo": "[MODELO-MENTAL]",
        "titulo": "Thank You Page como Primeira Venda — OTO Imediato",
        "insight": "A página de obrigado após opt-in é o momento de maior receptividade: o lead acabou de dizer 'sim' pela primeira vez. Uma OTO (One-Time Offer) na thank you page converte 5-15% dos leads imediatamente, recuperando custo de aquisição antes de qualquer email.",
        "priority": "HIGH",
        "confidence": 0.92,
        "chunks": ["chunk_RB11F_018"],
        "tags": ["thank you page", "OTO", "SLO", "custo de aquisição"]
    },
    {
        "id": "RB11F-006",
        "tipo": "[MODELO-MENTAL]",
        "titulo": "Custo por Lead como Métrica Central",
        "insight": "O negócio que sabe exatamente quanto paga por lead e quanto cada lead vale (LTV) pode escalar ilimitadamente. Brunson: 'Em nosso mercado, custa $1-$3 por lead.' Sem essa clareza, anunciar é apostar. Com ela, é investimento com retorno calculável.",
        "priority": "HIGH",
        "confidence": 0.91,
        "chunks": ["chunk_RB11F_046"],
        "tags": ["CPL", "custo por lead", "LTV", "escala", "anúncios"]
    },

    # ─── HEURISTICAS ─────────────────────────────────────────────────────
    {
        "id": "RB11F-007",
        "tipo": "[HEURISTICA]",
        "titulo": "Custo de Lead Típico — Benchmark de Mercado",
        "insight": "Em mercados de info-produto e coaching, o custo típico por lead é $1-$3. Se você paga mais que $5/lead sem ter um SLO que recupera o custo, o funil está quebrado. O objetivo do SLO na thank you page é zerear o custo de aquisição.",
        "threshold": "CPL saudável: $1-$3. Acima de $5 sem SLO = funil quebrado.",
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_RB11F_046"],
        "tags": ["CPL", "benchmark", "SLO", "funil"]
    },
    {
        "id": "RB11F-008",
        "tipo": "[HEURISTICA]",
        "titulo": "Opt-in Rate — Benchmark de Squeeze Page",
        "insight": "Uma squeeze page saudável converte 30-60% dos visitantes em leads. Abaixo de 20% = problema no hook/headline. Acima de 60% = lead magnet altamente específico para audiência já qualificada. Testar headline é a maior alavanca.",
        "threshold": "Opt-in rate alvo: 30-60%. Abaixo de 20% = revisar hook imediatamente.",
        "priority": "HIGH",
        "confidence": 0.91,
        "chunks": ["chunk_RB11F_015"],
        "tags": ["opt-in rate", "squeeze page", "benchmark", "headline"]
    },
    {
        "id": "RB11F-009",
        "tipo": "[HEURISTICA]",
        "titulo": "114 Tipos de Lead Magnet — Todo Formato Funciona",
        "insight": "Lead magnets podem ser: ebooks, checklists, swipe files, mini-cursos, webinars, desafios, ferramentas, templates, quizzes, amostras de produto, trial de software, acesso gratuito. O formato é secundário; a especificidade do problema que resolve é primária.",
        "threshold": "Especificidade > Formato. Lead magnet genérico converte 5x menos que específico.",
        "priority": "HIGH",
        "confidence": 0.90,
        "chunks": ["chunk_RB11F_025"],
        "tags": ["lead magnet", "formato", "especificidade"]
    },
    {
        "id": "RB11F-010",
        "tipo": "[HEURISTICA]",
        "titulo": "7 Maiores Erros — Formula de Lead Magnet de Alto Opt-in",
        "insight": "Fórmula de lead magnet comprovada: 'Os (N) Maiores Erros que (Seu Público) Comete.' Esta estrutura funciona porque: (1) apela para a dor existente; (2) o número cria especificidade; (3) 'erros' implica que o problema não é culpa deles — é falta de informação.",
        "threshold": "Usar número específico (7, 8, 12). Fórmula converte 2-3x mais que headline genérico.",
        "priority": "HIGH",
        "confidence": 0.89,
        "chunks": ["chunk_RB11F_026"],
        "tags": ["lead magnet", "fórmula", "headline", "erros", "especificidade"]
    },
    {
        "id": "RB11F-011",
        "tipo": "[HEURISTICA]",
        "titulo": "SLO — Self-Liquidating Offer para Zerar Custo de Anúncio",
        "insight": "O SLO é um produto de $7-$47 oferecido imediatamente após o opt-in (na thank you page). Se 10% dos leads compram o SLO a $27 e o custo por lead é $2, o funil é self-liquidating: você adquire leads de graça e ainda tem a lista para monetizar no backend.",
        "threshold": "SLO ideal: $7-$47. Taxa de conversão 5-15%. CPL recuperado quando: SLO_price × conv_rate ≥ CPL.",
        "priority": "HIGH",
        "confidence": 0.94,
        "chunks": ["chunk_RB11F_050"],
        "tags": ["SLO", "self-liquidating", "thank you page", "backend"]
    },

    # ─── FRAMEWORKS ──────────────────────────────────────────────────────
    {
        "id": "RB11F-012",
        "tipo": "[FRAMEWORK]",
        "titulo": "Anatomia do Lead Funnel — 4 Componentes",
        "insight": "Todo lead funnel tem 4 partes: (1) Lead Magnet — a isca de valor; (2) Squeeze Page — página de captura com hook; (3) Thank You Page — entrega + OTO imediato; (4) Follow-up Sequence — emails para converter leads em clientes (Soap Opera + Daily Seinfeld).",
        "priority": "HIGH",
        "confidence": 0.95,
        "chunks": ["chunk_RB11F_008"],
        "tags": ["lead funnel", "anatomia", "squeeze page", "follow-up", "OTO"]
    },
    {
        "id": "RB11F-013",
        "tipo": "[FRAMEWORK]",
        "titulo": "4 Tipos de Lead Magnet por Formato de Entrega",
        "insight": "4 categorias por formato: (1) Informação — reports, ebooks, checklists, mini-cursos; (2) Ferramentas/Templates — swipe files, scripts, calculadoras; (3) Acesso — trial de software, membership gratuita; (4) Experiência — webinar, challenge, consultoria gratuita.",
        "priority": "HIGH",
        "confidence": 0.91,
        "chunks": ["chunk_RB11F_022"],
        "tags": ["lead magnet", "categorias", "formato", "webinar", "trial"]
    },
    {
        "id": "RB11F-014",
        "tipo": "[FRAMEWORK]",
        "titulo": "Value Ladder no Contexto de Lead Funnels",
        "insight": "O lead funnel é o degrau zero da Value Ladder. Estrutura: Grátis (lead magnet) → SLO ($7-47) → Core Offer ($97-$997) → High-ticket ($2k+) → Continuidade (mensal). Cada degrau serve o cliente E apresenta o próximo. Sem o degrau zero, a escada não tem entrada.",
        "priority": "HIGH",
        "confidence": 0.95,
        "chunks": ["chunk_RB11F_055"],
        "tags": ["value ladder", "lead funnel", "SLO", "core offer", "upsell"]
    },
    {
        "id": "RB11F-015",
        "tipo": "[FRAMEWORK]",
        "titulo": "Swipe File como Método de Aprendizado — 114 Modelos",
        "insight": "Em vez de criar do zero, estudar os 114 melhores lead funnels existentes e modelar o que funciona. Processo: (1) identificar o hook usado; (2) entender o lead magnet oferecido; (3) observar a thank you page; (4) entrar no follow-up e mapear a sequência. Modelar antes de inovar.",
        "priority": "HIGH",
        "confidence": 0.89,
        "chunks": ["chunk_RB11F_002"],
        "tags": ["swipe file", "modelagem", "hook", "implementação"]
    },

    # ─── METODOLOGIAS ────────────────────────────────────────────────────
    {
        "id": "RB11F-016",
        "tipo": "[METODOLOGIA]",
        "titulo": "Implementar Lead Funnel em Menos de 1 Hora",
        "insight": "Com o swipe file e um funil de referência escolhido: (1) Criar headline adaptada para seu mercado (10 min); (2) Criar/adaptar lead magnet (20-30 min); (3) Montar squeeze page em ClickFunnels (10 min); (4) Configurar thank you page com OTO (10 min). Total: < 1 hora.",
        "priority": "HIGH",
        "confidence": 0.88,
        "chunks": ["chunk_RB11F_003"],
        "tags": ["implementação", "velocidade", "squeeze page", "ClickFunnels"]
    },
    {
        "id": "RB11F-017",
        "tipo": "[METODOLOGIA]",
        "titulo": "Criar Lead Magnet de Alto Valor em 30 Minutos",
        "insight": "Método Myron Golden: (1) Listar 12 erros/dores do seu público; (2) Gravar vídeo no iPhone ensinando esses erros (20 min); (3) Transcrever e criar PDF (10 min). Resultado: lead magnet percebido como valioso sem produção cara. Velocidade de criação > perfeição.",
        "priority": "HIGH",
        "confidence": 0.90,
        "chunks": ["chunk_RB11F_026"],
        "tags": ["lead magnet", "criação rápida", "iPhone", "Myron Golden"]
    },
    {
        "id": "RB11F-018",
        "tipo": "[METODOLOGIA]",
        "titulo": "Sequência de Follow-up Pós-Opt-in — 5 Emails Soap Opera",
        "insight": "Após o opt-in, a sequência Soap Opera converte leads em compradores: Email 1: Open loop + confirmação; Email 2: Backstory + vilão; Email 3: Epifania + virada; Email 4: Benefício oculto + prova social; Email 5: CTA urgente + bônus com prazo. Essa sequência converte antes do lead reesfriar.",
        "priority": "HIGH",
        "confidence": 0.94,
        "chunks": ["chunk_RB11F_060"],
        "tags": ["soap opera", "follow-up", "email", "conversão", "sequência"]
    },
    {
        "id": "RB11F-019",
        "tipo": "[METODOLOGIA]",
        "titulo": "Recoup Ad Cost — Calcular Break-Even do Funil",
        "insight": "Para validar se um funil é escalável: (1) Calcular CPL (custo por lead); (2) Calcular receita média por lead (LTV 30 dias); (3) Se LTV > CPL, o funil escala. Se o SLO na thank you page gera receita ≥ CPL, o tráfego pago é gratuito. Esse cálculo deve ser feito antes de qualquer escala.",
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_RB11F_050"],
        "tags": ["break-even", "CPL", "LTV", "escala", "ROI"]
    },
    {
        "id": "RB11F-020",
        "tipo": "[METODOLOGIA]",
        "titulo": "Modelar Funil Existente — 4 Passos",
        "insight": "Para modelar qualquer lead funnel do swipe file: (1) Escolher funil do mesmo nicho ou com mesmo público-alvo; (2) Opt-in e entrar no funil para observar a experiência completa; (3) Capturar screenshots da squeeze page, thank you page e emails; (4) Adaptar hook e lead magnet para seu mercado. Não copiar — modelar.",
        "priority": "HIGH",
        "confidence": 0.88,
        "chunks": ["chunk_RB11F_005"],
        "tags": ["modelagem", "swipe file", "implementação", "nicho"]
    },

    # ─── HEURISTICAS ADICIONAIS ──────────────────────────────────────────
    {
        "id": "RB11F-021",
        "tipo": "[HEURISTICA]",
        "titulo": "Headline de Lead Magnet — Fórmula com Segredo",
        "insight": "Fórmula de headline comprovada por Eben Pagan: 'Você Está Prestes a Aprender um Segredo Sobre (TÓPICO) Que a Maioria das Pessoas Nunca Vai Conhecer.' Funciona porque cria curiosidade + exclusividade + promessa. Plugável em qualquer nicho.",
        "threshold": "Headline com 'Segredo' converte 20-30% mais. Especificidade do tópico aumenta opt-in rate.",
        "priority": "HIGH",
        "confidence": 0.89,
        "chunks": ["chunk_RB11F_009"],
        "tags": ["headline", "segredo", "curiosidade", "Eben Pagan", "fórmula"]
    },
    {
        "id": "RB11F-022",
        "tipo": "[HEURISTICA]",
        "titulo": "Objetivo da Squeeze Page — Apenas Uma Ação",
        "insight": "Uma squeeze page efetiva tem ZERO distrações: sem menu de navegação, sem links externos, sem múltiplas CTAs. Apenas: headline + lead magnet visual + campo de email + botão. Cada elemento adicional reduz opt-in rate. Menos é mais — de forma comprovada.",
        "threshold": "Squeeze page com menu reduz opt-in rate em 30-50% vs. página sem distrações.",
        "priority": "HIGH",
        "confidence": 0.92,
        "chunks": ["chunk_RB11F_016"],
        "tags": ["squeeze page", "distração", "opt-in rate", "foco", "CTA"]
    },
    {
        "id": "RB11F-023",
        "tipo": "[HEURISTICA]",
        "titulo": "Lista de Email — Valor de $1/Mês/Assinante",
        "insight": "Benchmark de mercado: lista de email bem gerenciada gera $1/mês por assinante. Com 10.000 leads, você deveria gerar $10.000/mês em receita (através de ofertas, promoções, continuidade). Se está abaixo, o problema está no relacionamento/sequência, não na lista.",
        "threshold": "$1/mês/assinante como benchmark. Abaixo disso = sequência fraca ou lead magnet errado (lista não qualificada).",
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_RB11F_048"],
        "tags": ["lista", "benchmark", "$1/mês", "monetização", "email"]
    },
    {
        "id": "RB11F-024",
        "tipo": "[HEURISTICA]",
        "titulo": "Ascensão na Value Ladder — 3 Objetivos do Lead Funnel",
        "insight": "O lead funnel serve 3 objetivos simultâneos: (1) Construir lista (ativo próprio); (2) Recuperar custo de anúncio (SLO na thank you page); (3) Identificar compradores prontos (quem compra SLO compra o core offer). Leads que não compram SLO → nurture → core offer.",
        "threshold": "Lead que compra SLO tem 5-7x mais chance de comprar core offer. Separar esses leads para nurture prioritário.",
        "priority": "HIGH",
        "confidence": 0.93,
        "chunks": ["chunk_RB11F_055"],
        "tags": ["value ladder", "SLO", "ascensão", "lead funnel", "compradores"]
    },
    {
        "id": "RB11F-025",
        "tipo": "[MODELO-MENTAL]",
        "titulo": "Reciprocidade como Motor do Opt-in",
        "insight": "O lead magnet ativa reciprocidade (Cialdini): ao receber algo valioso de graça, o prospect se sente psicologicamente inclinado a retribuir. A retribuição inicial é o email. A retribuição maior é a compra. Quanto mais valiosa é a entrega gratuita, maior é a pressão de reciprocidade.",
        "priority": "HIGH",
        "confidence": 0.90,
        "chunks": ["chunk_RB11F_010"],
        "tags": ["reciprocidade", "Cialdini", "lead magnet", "psicologia", "opt-in"]
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

from collections import Counter
tipos = Counter(i["tipo"] for i in insights)
print("\nDistribution:")
for tipo, count in sorted(tipos.items()):
    print(f"  {tipo}: {count}")
