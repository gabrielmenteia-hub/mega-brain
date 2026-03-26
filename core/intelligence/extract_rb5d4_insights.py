"""
Insight extraction for Dotcom Secrets (RB5D4)
Russell Brunson | BLUEPRINTS | 2026-03-08
"""
import json
from pathlib import Path

SOURCE_ID = "RB5D4"
SOURCE_PERSON = "Russell Brunson"
SOURCE_TITLE = "Dotcom Secrets"

ROOT = Path("c:/Users/Gabriel/MEGABRAIN")
INSIGHTS_PATH = ROOT / "processing/insights/INSIGHTS-STATE.json"

insights = [
    # =========================================================================
    # FRAMEWORKS
    # =========================================================================
    {
        "id": "INS-RB5D4-001",
        "titulo": "Value Ladder — Escada de Valor Ascendente",
        "insight": "Toda empresa deve ter uma Value Ladder: sequência de produtos/serviços em ordem crescente de valor e preço. O prospect entra pelo nível mais baixo (bait) e é conduzido gradualmente até o backend de alto valor. Sem Value Ladder, a empresa limita o LTV e deixa dinheiro na mesa. A maioria das empresas só tem parte da escada — falta o frontend (bait) e o backend (high-ticket).",
        "priority": "HIGH",
        "confidence": 0.97,
        "tags": ["[FRAMEWORK]", "vendas", "funil", "LTV"],
        "dna_tag": "[FRAMEWORK]",
        "chunks": ["chunk_RB5D4_015", "chunk_RB5D4_016", "chunk_RB5D4_017"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["VENDAS", "FUNNEL", "PRODUTO"]
    },
    {
        "id": "INS-RB5D4-002",
        "titulo": "Dream Customer Avatar — WHO + Where + Bait + Result",
        "insight": "Antes de qualquer funil, definir 4 elementos: (1) WHO — o cliente ideal específico (não qualquer pessoa); (2) Where — onde esse cliente está online agora; (3) Bait — o que atrai esse cliente específico; (4) Result — onde você quer levá-lo. Vender para qualquer pessoa = cansaço e frustração. O avatar específico determina copy, funil e oferta.",
        "priority": "HIGH",
        "confidence": 0.95,
        "tags": ["[FRAMEWORK]", "avatar", "ICP", "marketing"],
        "dna_tag": "[FRAMEWORK]",
        "chunks": ["chunk_RB5D4_030", "chunk_RB5D4_031"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["MARKETING", "AVATAR", "POSICIONAMENTO"]
    },
    {
        "id": "INS-RB5D4-003",
        "titulo": "3 Tipos de Tráfego — Own, Control, Earn",
        "insight": "Três tipos de tráfego: (1) TRÁFEGO QUE VOCÊ CONTROLA (anúncios pagos) — caro, mas previsível; (2) TRÁFEGO QUE VOCÊ NÃO CONTROLA (SEO, social, PR) — grátis, mas imprevisível; (3) TRÁFEGO QUE VOCÊ POSSUI (sua lista) — zero custo, máximo controle. Objetivo de todo funil: converter qualquer tipo de tráfego em tráfego próprio (lista). A lista é o único ativo de tráfego que ninguém pode tirar de você.",
        "priority": "HIGH",
        "confidence": 0.96,
        "tags": ["[FRAMEWORK]", "tráfego", "lista", "email"],
        "dna_tag": "[FRAMEWORK]",
        "chunks": ["chunk_RB5D4_045", "chunk_RB5D4_046", "chunk_RB5D4_047"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["TRÁFEGO", "MARKETING", "EMAIL"]
    },
    {
        "id": "INS-RB5D4-004",
        "titulo": "Hot/Warm/Cold Traffic — Temperatura e Consciência do Prospect",
        "insight": "Tráfego quente (sua lista), morno (audiências similares) e frio (cold) exigem copy e funis diferentes. Gene Schwartz: (1) Prospect ciente do produto → headline começa com produto; (2) Só ciente do desejo → headline começa com desejo; (3) Ciente apenas do problema → headline começa com o problema. Temperatura determina onde no funil o prospect entra e qual mensagem recebe.",
        "priority": "HIGH",
        "confidence": 0.94,
        "tags": ["[MODELO-MENTAL]", "tráfego", "copy", "consciência"],
        "dna_tag": "[MODELO-MENTAL]",
        "chunks": ["chunk_RB5D4_058", "chunk_RB5D4_059"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["TRÁFEGO", "COPY", "FUNIL"]
    },
    {
        "id": "INS-RB5D4-005",
        "titulo": "Dream 100 — Parceiros Estratégicos em Audiências Existentes",
        "insight": "O tráfego já existe — está concentrado em 100 pessoas/plataformas que já têm seus clientes ideais. Dream 100: identificar os 100 influenciadores, podcasts, blogs, canais, newsletters que atendem seu avatar. Estratégia dupla: (1) comprar acesso via anúncios; (2) conquistar parceria via relacionamento (publicar, engajar, oferecer valor). Mais eficiente criar audiência emprestada do que audiência própria do zero.",
        "priority": "HIGH",
        "confidence": 0.95,
        "tags": ["[METODOLOGIA]", "tráfego", "parceria", "distribuição"],
        "dna_tag": "[METODOLOGIA]",
        "chunks": ["chunk_RB5D4_040", "chunk_RB5D4_041"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["TRÁFEGO", "PARCERIA", "DISTRIBUIÇÃO"]
    },
    # =========================================================================
    # METODOLOGIAS
    # =========================================================================
    {
        "id": "INS-RB5D4-006",
        "titulo": "Soap Opera Sequence — 5 Emails para Criar Vínculo com Prospect",
        "insight": "Sequência de boas-vindas obrigatória em 5 emails: Email 1 — Configurar boas-vindas + abrir loop (cliffhanger); Email 2 — Backstory de alta dramaturgia + revelar vilão; Email 3 — Epifania + virada; Email 4 — Benefício oculto + surpresa; Email 5 — Urgência + CTA. Cada email termina com um open loop que força a abertura do próximo. Modelado em telenovelas: não há saída voluntária.",
        "priority": "HIGH",
        "confidence": 0.95,
        "tags": ["[METODOLOGIA]", "email", "sequência", "engajamento"],
        "dna_tag": "[METODOLOGIA]",
        "chunks": ["chunk_RB5D4_070", "chunk_RB5D4_071", "chunk_RB5D4_072"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["EMAIL", "NURTURE", "COPY"]
    },
    {
        "id": "INS-RB5D4-007",
        "titulo": "Daily Seinfeld Sequence — Email Diário de Entretenimento",
        "insight": "Após a Soap Opera Sequence, emails diários no estilo Seinfeld: 90% entretenimento, 10% conteúdo. O objetivo não é educar — é manter relacionamento e fazer o prospect querer ler. Emails devem ser sobre NADA (como o show Seinfeld) — histórias pessoais que conectam a uma oferta de forma oblíqua. A tentação de ser educativo mata a abertura. Audiência que lê = audiência que compra.",
        "priority": "HIGH",
        "confidence": 0.93,
        "tags": ["[METODOLOGIA]", "email", "entretenimento", "lista"],
        "dna_tag": "[METODOLOGIA]",
        "chunks": ["chunk_RB5D4_078", "chunk_RB5D4_079"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["EMAIL", "ENGAJAMENTO", "COPY"]
    },
    {
        "id": "INS-RB5D4-008",
        "titulo": "Reverse Engineering de Funil — Modelar o que Já Funciona",
        "insight": "Antes de criar qualquer funil, identificar concorrente lucrativo e reverse-engineer: (1) onde compram anúncios; (2) qual landing page usam; (3) qual sequência de emails enviam; (4) quais upsells oferecem; (5) qual tráfego converte. Não reinventar a roda — modelar o que já funciona, depois testar e melhorar. Um funil que já gasta dinheiro em anúncios é funil lucrativo (quem paga por tráfego tem que estar convertendo).",
        "priority": "HIGH",
        "confidence": 0.94,
        "tags": ["[METODOLOGIA]", "funil", "concorrência", "estratégia"],
        "dna_tag": "[METODOLOGIA]",
        "chunks": ["chunk_RB5D4_082", "chunk_RB5D4_083"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["FUNIL", "ESTRATÉGIA", "PESQUISA"]
    },
    {
        "id": "INS-RB5D4-009",
        "titulo": "Two-Step Free-Plus-Shipping Funnel — Aquisição de Clientes no Zero",
        "insight": "Funil de frontend: oferecer produto físico (livro, DVD, kit) grátis — prospect paga apenas o frete. Resultado: adquirir cliente comprando sem gastar capital. Lógica: quem paga frete virou comprador (ID psicológica diferente de lead). Após o checkout, upsells de 1-3 ofertas maiores. O objetivo não é lucrar no frontend — é liquidar o custo de aquisição e adquirir clientes pagantes para o backend.",
        "priority": "HIGH",
        "confidence": 0.96,
        "tags": ["[FRAMEWORK]", "funil", "aquisição", "frontend"],
        "dna_tag": "[FRAMEWORK]",
        "chunks": ["chunk_RB5D4_115", "chunk_RB5D4_116"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["FUNIL", "AQUISIÇÃO", "PRODUTO"]
    },
    {
        "id": "INS-RB5D4-010",
        "titulo": "Invisible Funnel Webinar — Vender Antes de Revelar o Preço",
        "insight": "Funil de webinar invisível: prospect assiste ao webinar acreditando que é grátis. No final, revela-se que o conteúdo custava X (valor âncora alto) e o prospect paga ou não paga dependendo se achou que valeu. Gera: credibilidade máxima (deu valor antes de pedir dinheiro), zero risco percebido, alta conversão em compradores qualificados. Aplicação: quando o produto é o próprio conteúdo do webinar.",
        "priority": "HIGH",
        "confidence": 0.91,
        "tags": ["[FRAMEWORK]", "webinar", "funil", "conversão"],
        "dna_tag": "[FRAMEWORK]",
        "chunks": ["chunk_RB5D4_125", "chunk_RB5D4_126"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["FUNIL", "WEBINAR", "CONVERSÃO"]
    },
    # =========================================================================
    # HEURÍSTICAS
    # =========================================================================
    {
        "id": "INS-RB5D4-011",
        "titulo": "SLO — Self-Liquidating Offer: Frontend Deve Pagar o Custo de Aquisição",
        "insight": "O frontend de qualquer funil deve ser self-liquidating: gerar receita suficiente para cobrir o custo do anúncio. Se o SLO paga o custo de aquisição, o backend é 100% lucro. Funil lucrativo não é aquele que ganha dinheiro no primeiro produto — é aquele que escala sem queimar capital. Upsells imediatos (OTO — One Time Offer) são o mecanismo para tornar o frontend lucrativo.",
        "priority": "HIGH",
        "confidence": 0.95,
        "tags": ["[HEURISTICA]", "funil", "SLO", "upsell"],
        "dna_tag": "[HEURISTICA]",
        "threshold": "Frontend deve cobrir CAC (custo de aquisição de cliente)",
        "chunks": ["chunk_RB5D4_118", "chunk_RB5D4_119"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["FUNIL", "FINANCEIRO", "ESCALA"]
    },
    {
        "id": "INS-RB5D4-012",
        "titulo": "Quem Paga Anúncio Vence — Outspend Your Competitors",
        "insight": "A empresa que pode gastar mais para adquirir um cliente vence. Se o concorrente consegue gastar $1 para adquirir cliente e você consegue gastar $2, você ganha. O segredo é ter um backend (Value Ladder) suficientemente robusto para justificar gasto maior no frontend. Brunson cita Dan Kennedy: 'Whoever can spend the most to acquire a customer wins.' Escala = resolver o math do funil antes de escalar o ad spend.",
        "priority": "HIGH",
        "confidence": 0.96,
        "tags": ["[HEURISTICA]", "tráfego", "escala", "CAC"],
        "dna_tag": "[HEURISTICA]",
        "threshold": "Ganhar = poder gastar mais por cliente que o concorrente",
        "chunks": ["chunk_RB5D4_014", "chunk_RB5D4_015"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["ESCALA", "FINANCEIRO", "TRÁFEGO"]
    },
    {
        "id": "INS-RB5D4-013",
        "titulo": "Pre-frame — Preparar o Prospect Antes do Funil",
        "insight": "O que acontece ANTES do prospect entrar no funil determina o estado emocional e a taxa de conversão. Pre-frame eficaz: artigo de blog, vídeo no YouTube, email de parceiro ou ad que contextualiza e aquece o prospect antes da landing page. Prospect que chega pré-aquecido converte 2-5x mais que prospect frio na mesma página. O pre-frame empresta credibilidade de fonte neutra antes da venda.",
        "priority": "HIGH",
        "confidence": 0.93,
        "tags": ["[HEURISTICA]", "tráfego", "conversão", "pre-frame"],
        "dna_tag": "[HEURISTICA]",
        "threshold": "Pre-frame adequado = 2-5x conversão vs. cold traffic direto",
        "chunks": ["chunk_RB5D4_062", "chunk_RB5D4_063"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["TRÁFEGO", "FUNIL", "COPY"]
    },
    {
        "id": "INS-RB5D4-014",
        "titulo": "Backend É Onde o Dinheiro Está — Frontend Só Abre a Porta",
        "insight": "O verdadeiro lucro de qualquer negócio online está no backend (high-ticket, continuidade, mastermind). A maioria dos empreendedores foca no produto frontend e ignora o backend — deixando 80%+ da receita potencial na mesa. Value Ladder corretamente construída: frontend $0-$100 → mid $100-$1K → backend $1K-$25K+. Cada nível deve existir porque o anterior já qualificou e serviu o cliente.",
        "priority": "HIGH",
        "confidence": 0.95,
        "tags": ["[HEURISTICA]", "backend", "high-ticket", "LTV"],
        "dna_tag": "[HEURISTICA]",
        "threshold": "80%+ da receita vem do backend (< 20% do volume de clientes)",
        "chunks": ["chunk_RB5D4_016", "chunk_RB5D4_017"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["PRODUTO", "ESCALA", "FUNIL"]
    },
    {
        "id": "INS-RB5D4-015",
        "titulo": "Continuidade — A Única Receita que Vem Todo Mês",
        "insight": "Continuidade (assinatura mensal) deve estar em toda Value Ladder. É a única receita que o empreendedor pode prever com certeza. Sem continuidade, o faturamento é sempre zero no começo de cada mês. Posicionamento estratégico: incluir oferta de continuidade como upsell imediato (OTO) após qualquer compra frontend. O ponto ideal na Value Ladder: entre o frontend e o mid-ticket.",
        "priority": "HIGH",
        "confidence": 0.92,
        "tags": ["[HEURISTICA]", "continuidade", "assinatura", "receita recorrente"],
        "dna_tag": "[HEURISTICA]",
        "threshold": "Toda Value Ladder deve ter continuidade — receita zero no dia 1 sem ela",
        "chunks": ["chunk_RB5D4_021", "chunk_RB5D4_022"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["PRODUTO", "RECEITA", "RETENÇÃO"]
    },
    {
        "id": "INS-RB5D4-016",
        "titulo": "7 Fases de um Funil — Onde Cada Prospect Está",
        "insight": "Todo funil tem 7 fases: (1) Determinar temperatura do tráfego; (2) Criar pre-frame bridge; (3) Qualificar subscribers; (4) Qualificar compradores; (5) Identificar compradores hiperativos (fanáticos que compram tudo); (6) Gerar relacionamento com quem não comprou; (7) Fazer ascender na Value Ladder. Funil incompleto = perder receita em alguma dessas 7 fases.",
        "priority": "HIGH",
        "confidence": 0.91,
        "tags": ["[FRAMEWORK]", "funil", "fases", "processo"],
        "dna_tag": "[FRAMEWORK]",
        "chunks": ["chunk_RB5D4_090", "chunk_RB5D4_091"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["FUNIL", "PROCESSO", "VENDAS"]
    },
    {
        "id": "INS-RB5D4-017",
        "titulo": "Compradores Hiperativos — Janela de 5 Minutos Após Compra",
        "insight": "Nos primeiros 5-15 minutos após uma compra, o prospect está no maior estado de predisposição para comprar mais. O estado mental de comprador ativo cria abertura para upsells imediatos (OTOs). Regra: ter 1-3 OTOs após qualquer compra frontend. Pessoa que acabou de comprar produto de $27 está psicologicamente pré-disposta a adicionar produto de $97-$297 se for relevante e apresentado imediatamente.",
        "priority": "HIGH",
        "confidence": 0.94,
        "tags": ["[HEURISTICA]", "upsell", "OTO", "psicologia"],
        "dna_tag": "[HEURISTICA]",
        "threshold": "Janela de compradores hiperativos: 5-15 min pós-compra",
        "chunks": ["chunk_RB5D4_110", "chunk_RB5D4_111"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["FUNIL", "UPSELL", "PSICOLOGIA"]
    },
    {
        "id": "INS-RB5D4-018",
        "titulo": "Attractive Character — Persona de Comunicação da Marca",
        "insight": "O Attractive Character (AC) é a persona através da qual a empresa se comunica — pode ser o fundador ou alguém criado. Elementos: (1) Backstory identificável; (2) Falas e parábolas recorrentes; (3) Falhas admitidas (humaniza); (4) Polarização (posições claras que dividem). O AC deve ser relatable, não perfeito. Pessoas não compram de marcas — compram de pessoas com quem se identificam. (Conceito aprofundado no Expert Secrets.)",
        "priority": "HIGH",
        "confidence": 0.93,
        "tags": ["[FRAMEWORK]", "personagem", "marca pessoal", "storytelling"],
        "dna_tag": "[FRAMEWORK]",
        "chunks": ["chunk_RB5D4_055", "chunk_RB5D4_056"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["MARCA", "COPY", "COMUNICAÇÃO"]
    },
    # =========================================================================
    # FILOSOFIAS
    # =========================================================================
    {
        "id": "INS-RB5D4-019",
        "titulo": "Funil = Vendedor que Trabalha 24/7 Sem Salário",
        "insight": "Um funil bem construído replica o processo de um vendedor humano: atrai, qualifica, apresenta, supera objeções e fecha. Mas funciona 24 horas, não tira férias, não pede comissão e escala ilimitadamente. O trabalho do empreendedor é construir e otimizar o funil uma vez — depois ele trabalha indefinidamente. Mentalidade de funil substitui a mentalidade de 'produto': não se lança um produto, se constrói um funil.",
        "priority": "HIGH",
        "confidence": 0.94,
        "tags": ["[FILOSOFIA]", "funil", "escala", "automação"],
        "dna_tag": "[FILOSOFIA]",
        "chunks": ["chunk_RB5D4_007", "chunk_RB5D4_008"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["FUNIL", "ESCALA", "FILOSOFIA"]
    },
    {
        "id": "INS-RB5D4-020",
        "titulo": "Modelo vs. Invenção — Comprimir uma Década em um Dia",
        "insight": "Modelar o que já funciona (de concorrente lucrativo) é a forma mais eficiente de criar um funil. Brunson cita Tony Robbins: encontre alguém que já faz o que você quer e modele. Não reinvente a roda. Um funil que alguém já testou com dinheiro real comprova que o modelo funciona. Depois de estar ganhando dinheiro, aí sim testar melhorias. Sequência correta: Model → Earn → Test → Innovate.",
        "priority": "HIGH",
        "confidence": 0.93,
        "tags": ["[FILOSOFIA]", "modelagem", "estratégia", "eficiência"],
        "dna_tag": "[FILOSOFIA]",
        "chunks": ["chunk_RB5D4_082", "chunk_RB5D4_083"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["ESTRATÉGIA", "FUNIL", "FILOSOFIA"]
    },
    {
        "id": "INS-RB5D4-021",
        "titulo": "Lista de Email — O Único Ativo Que Você Realmente Possui",
        "insight": "Todo tráfego deve ser convertido em lista de email — o único ativo digital que não depende de algoritmos, plataformas ou parceiros. Redes sociais mudam, algoritmos mudam, plataformas fecham. Lista de email é sua e permanente. Métricas: $1/mês por subscriber é o benchmark básico para lista de email ativa. Objetivo de todo funil: construir lista e ascender subscribers na Value Ladder.",
        "priority": "HIGH",
        "confidence": 0.95,
        "tags": ["[HEURISTICA]", "lista", "email", "ativo"],
        "dna_tag": "[HEURISTICA]",
        "threshold": "$1/mês/subscriber = benchmark mínimo de lista saudável",
        "chunks": ["chunk_RB5D4_046", "chunk_RB5D4_047"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["EMAIL", "ATIVO", "LISTA"]
    },
    # =========================================================================
    # MODELOS MENTAIS
    # =========================================================================
    {
        "id": "INS-RB5D4-022",
        "titulo": "Funil vs. Website — Website É Museu, Funil É Vendedor",
        "insight": "Website tradicional dá ao visitante infinitas opções → paralisia → saída. Funil dá apenas uma opção em cada passo → decisão binária → movimento. A diferença fundamental: website serve o visitante com informação; funil conduz o visitante a uma decisão. Toda página de um funil tem um único objetivo, um único CTA. Trocar website por funil é a maior alavanca para empresas que já têm tráfego mas não convertem.",
        "priority": "HIGH",
        "confidence": 0.94,
        "tags": ["[MODELO-MENTAL]", "funil", "website", "conversão"],
        "dna_tag": "[MODELO-MENTAL]",
        "chunks": ["chunk_RB5D4_006", "chunk_RB5D4_007"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["FUNIL", "CONVERSÃO", "DESIGN"]
    },
    {
        "id": "INS-RB5D4-023",
        "titulo": "Tráfego Não Se Cria — Se Redireciona",
        "insight": "O tráfego já existe — está concentrado em lugares onde seu avatar passa o tempo. A função do empreendedor não é criar tráfego novo, mas identificar onde o tráfego já está e redirecioná-lo. Implicação: antes de qualquer ad, mapear Dream 100 (os 100 lugares onde seu avatar está). Dream 100 define estratégia de tráfego pago e orgânico simultaneamente.",
        "priority": "HIGH",
        "confidence": 0.93,
        "tags": ["[MODELO-MENTAL]", "tráfego", "distribuição", "estratégia"],
        "dna_tag": "[MODELO-MENTAL]",
        "chunks": ["chunk_RB5D4_040", "chunk_RB5D4_041"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["TRÁFEGO", "ESTRATÉGIA", "DISTRIBUIÇÃO"]
    },
    {
        "id": "INS-RB5D4-024",
        "titulo": "High-Ticket Application Funnel — 4 Comprometimentos",
        "insight": "Funil de alta ticket (consultoria, mastermind, coaching): (1) Página de aplicação com perguntas de qualificação; (2) Call de vendas com script de 4 comprometimentos — Tempo: pode comprometer X horas/semana? Decisão: consegue decidir hoje? Dinheiro: pode investir $X? Sucesso: está comprometido a implementar? Fechar apenas quem passa nos 4. Cada comprometimento é binário — não passe adiante sem 'sim'.",
        "priority": "HIGH",
        "confidence": 0.92,
        "tags": ["[METODOLOGIA]", "high-ticket", "vendas", "aplicação"],
        "dna_tag": "[METODOLOGIA]",
        "chunks": ["chunk_RB5D4_145", "chunk_RB5D4_146"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["VENDAS", "HIGH-TICKET", "FUNIL"]
    },
    {
        "id": "INS-RB5D4-025",
        "titulo": "Continuidade de Funil — Retargeting e Follow-up dos Não-Compradores",
        "insight": "70-95% dos visitantes de qualquer funil não compram. Retargeting e follow-up via email são obrigatórios para maximizar a receita. Para não-compradores: sequência de 5-7 emails com re-apresentação de oferta, abordagem diferente, bônus adicionais. Para compradores: sequência de ascensão na Value Ladder. Funil que não tem follow-up de não-compradores deixa 70%+ da receita potencial na mesa.",
        "priority": "HIGH",
        "confidence": 0.91,
        "tags": ["[HEURISTICA]", "retargeting", "follow-up", "email"],
        "dna_tag": "[HEURISTICA]",
        "threshold": "70-95% dos visitantes não compram na primeira visita — follow-up obrigatório",
        "chunks": ["chunk_RB5D4_132", "chunk_RB5D4_133"],
        "fonte": SOURCE_ID,
        "source_title": SOURCE_TITLE,
        "dominio": ["FUNIL", "EMAIL", "RETENÇÃO"]
    },
]

# Load existing INSIGHTS-STATE
with open(INSIGHTS_PATH, "r", encoding="utf-8") as f:
    state = json.load(f)

# Ensure persons structure
if "persons" not in state["insights_state"]:
    state["insights_state"]["persons"] = {}

person_key = SOURCE_PERSON
if person_key not in state["insights_state"]["persons"]:
    state["insights_state"]["persons"][person_key] = []

# Handle both list and dict formats
person_data = state["insights_state"]["persons"][person_key]
if isinstance(person_data, list):
    existing_list = person_data
elif isinstance(person_data, dict):
    existing_list = person_data.get("insights", [])
else:
    existing_list = []

# Check existing insight IDs
existing_ids = {i["id"] for i in existing_list}

# Add new insights
import datetime
new_count = 0
for insight in insights:
    if insight["id"] not in existing_ids:
        insight["source_id"] = SOURCE_ID
        insight["source_person"] = SOURCE_PERSON
        insight["timestamp"] = datetime.datetime.now().isoformat()
        existing_list.append(insight)
        new_count += 1

# Store back
if isinstance(state["insights_state"]["persons"][person_key], list):
    state["insights_state"]["persons"][person_key] = existing_list
else:
    state["insights_state"]["persons"][person_key]["insights"] = existing_list

# Add to change log
if "change_log" not in state["insights_state"]:
    state["insights_state"]["change_log"] = []

state["insights_state"]["change_log"].append({
    "date": "2026-03-08",
    "source_id": SOURCE_ID,
    "action": "added",
    "count": new_count,
    "person": SOURCE_PERSON
})

# Save
with open(INSIGHTS_PATH, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

# Stats
high = sum(1 for i in insights if i["priority"] == "HIGH")
medium = sum(1 for i in insights if i["priority"] == "MEDIUM")
low = sum(1 for i in insights if i["priority"] == "LOW")

# DNA tags
from collections import Counter
dna_counts = Counter(i["dna_tag"] for i in insights)

print(f"Source: {SOURCE_PERSON} ({SOURCE_ID})")
print(f"Title: {SOURCE_TITLE}")
print(f"Insights added: {new_count}/{len(insights)}")
print(f"Priority: HIGH={high}, MEDIUM={medium}, LOW={low}")
print("DNA distribution:")
for tag, count in sorted(dna_counts.items()):
    print(f"  {tag}: {count}")
print(f"INSIGHTS-STATE saved: {INSIGHTS_PATH}")
