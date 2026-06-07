from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

OUTPUT = "c:/Users/Gabriel/MEGABRAIN/artifacts/MegaBrain-Premium-Guia-Completo.pdf"

# ── Cores ──────────────────────────────────────────────────────────────────
DARK_BG    = colors.HexColor("#0f172a")
ACCENT     = colors.HexColor("#6366f1")
ACCENT2    = colors.HexColor("#22c55e")
GOLD       = colors.HexColor("#f59e0b")
TEXT_WHITE = colors.HexColor("#f1f5f9")
TEXT_GRAY  = colors.HexColor("#94a3b8")
CARD_BG    = colors.HexColor("#1e293b")
BORDER     = colors.HexColor("#334155")

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2.5*cm, bottomMargin=2.5*cm,
    title="Mega Brain Premium — Guia Completo",
    author="JARVIS v2.0",
)

W, H = A4
CONTENT_W = W - 4*cm

# ── Estilos ────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

style_cover_title = S("CoverTitle",
    fontSize=28, leading=34, textColor=TEXT_WHITE,
    alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=8)

style_cover_sub = S("CoverSub",
    fontSize=13, leading=18, textColor=ACCENT,
    alignment=TA_CENTER, fontName="Helvetica", spaceAfter=4)

style_cover_meta = S("CoverMeta",
    fontSize=10, leading=14, textColor=TEXT_GRAY,
    alignment=TA_CENTER, fontName="Helvetica")

style_h1 = S("H1",
    fontSize=18, leading=24, textColor=ACCENT,
    fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=8)

style_h2 = S("H2",
    fontSize=13, leading=18, textColor=GOLD,
    fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=6)

style_h3 = S("H3",
    fontSize=11, leading=16, textColor=ACCENT2,
    fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=4)

style_body = S("Body",
    fontSize=9.5, leading=15, textColor=TEXT_WHITE,
    fontName="Helvetica", spaceAfter=4)

style_body_gray = S("BodyGray",
    fontSize=9, leading=14, textColor=TEXT_GRAY,
    fontName="Helvetica", spaceAfter=3)

style_bullet = S("Bullet",
    fontSize=9.5, leading=14, textColor=TEXT_WHITE,
    fontName="Helvetica", leftIndent=14, spaceAfter=2,
    bulletIndent=4, bulletText="•")

style_code = S("Code",
    fontSize=8.5, leading=13, textColor=ACCENT2,
    fontName="Courier", leftIndent=12, spaceAfter=2)

style_tag = S("Tag",
    fontSize=8, leading=12, textColor=ACCENT,
    fontName="Helvetica-Bold")

def hr(color=BORDER, thickness=0.5):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=6, spaceBefore=4)

def h1(text):
    return [Spacer(1, 6), Paragraph(text, style_h1), hr(ACCENT, 1)]

def h2(text):
    return [Spacer(1, 4), Paragraph(text, style_h2)]

def h3(text):
    return [Paragraph(text, style_h3)]

def body(text):
    return Paragraph(text, style_body)

def gray(text):
    return Paragraph(text, style_body_gray)

def bullet(text):
    return Paragraph(text, style_bullet)

def code(text):
    return Paragraph(text, style_code)

def spacer(h=6):
    return Spacer(1, h)

def table(data, col_widths=None, header=True):
    if col_widths is None:
        col_widths = [CONTENT_W / len(data[0])] * len(data[0])
    t = Table(data, colWidths=col_widths)
    ts = [
        ("BACKGROUND", (0,0), (-1,0 if header else -1), CARD_BG),
        ("TEXTCOLOR", (0,0), (-1,0), ACCENT if header else TEXT_WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [DARK_BG, CARD_BG]),
        ("TEXTCOLOR", (0,1), (-1,-1), TEXT_WHITE),
        ("FONTSIZE", (0,1), (-1,-1), 8.5),
        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("GRID", (0,0), (-1,-1), 0.3, BORDER),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]
    if header:
        ts.append(("LINEBELOW", (0,0), (-1,0), 1, ACCENT))
    t.setStyle(TableStyle(ts))
    return t

def card(flowables, bg=CARD_BG):
    inner = Table([[flowables]], colWidths=[CONTENT_W - 1.2*cm])
    inner.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 14),
        ("RIGHTPADDING", (0,0), (-1,-1), 14),
        ("ROUNDEDCORNERS", [6]),
        ("BOX", (0,0), (-1,-1), 0.5, BORDER),
    ]))
    return inner

# ── Background de página ───────────────────────────────────────────────────
def page_bg(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    # rodapé
    canvas.setFillColor(TEXT_GRAY)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(2*cm, 1.2*cm, "Mega Brain Premium — Guia Completo")
    canvas.drawRightString(W - 2*cm, 1.2*cm, f"Página {doc.page}")
    # linha rodapé
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.3)
    canvas.line(2*cm, 1.5*cm, W - 2*cm, 1.5*cm)
    canvas.restoreState()

# ── Conteúdo ───────────────────────────────────────────────────────────────
story = []

# ════ CAPA ════════════════════════════════════════════════════════════════
story += [
    Spacer(1, 3*cm),
    Paragraph("⚡ MEGA BRAIN PREMIUM", style_cover_title),
    Spacer(1, 0.3*cm),
    Paragraph("Guia Completo — Tudo que o Sistema Faz", style_cover_sub),
    Spacer(1, 0.6*cm),
    hr(ACCENT, 1.5),
    Spacer(1, 0.4*cm),
    Paragraph("J.A.R.V.I.S. v2.0  ·  Just A Rather Very Intelligent System", style_cover_meta),
    Paragraph("27 de março de 2026", style_cover_meta),
    Spacer(1, 2*cm),
]

# stats capa
capa_stats = table([
    ["267 Agentes", "7.472 Chunks", "733 Insights", "43 Especialistas"],
    ["Ativos no sistema", "Mapeados", "Estruturados", "Com DNA extraído"],
], col_widths=[CONTENT_W/4]*4)
story += [capa_stats, Spacer(1, 3*cm)]
story += [Paragraph("\"Os números não mentem, senhor. Embora às vezes sejam inconvenientes.\"", style_cover_meta)]
story += [Spacer(1, 0.3*cm), Paragraph("— JARVIS", style_cover_meta)]

# ════ 1. PIPELINE ══════════════════════════════════════════════════════════
story += h1("1. Pipeline de Processamento de Conhecimento")
story += [body("O núcleo do sistema. Transforma qualquer material bruto em conhecimento estruturado e acionável.")]
story += [spacer()]

story += h2("Entrada Aceita")
story += [
    bullet("Vídeos do YouTube — transcreve automaticamente via Whisper (OpenAI)"),
    bullet("PDFs, arquivos .txt, .md"),
    bullet("Google Drive — documentos, planilhas"),
    bullet("Arquivos locais de qualquer tipo legível"),
    spacer(),
]

story += h2("As 8 Fases do Pipeline  (/process-jarvis)")
phases = table([
    ["Fase", "Nome", "O que faz"],
    ["1", "Detecção de Fonte", "Identifica de quem é o material"],
    ["2", "Chunking", "Divide em blocos semânticos coerentes"],
    ["3", "Tagging", "Classifica por tema, tipo de insight, camada DNA"],
    ["4", "Extração de Insights", "Estrutura cada ponto com atribuição de fonte"],
    ["5", "Narrativa", "Gera narrativa coesa e legível dos chunks"],
    ["6", "Validação", "Verifica integridade, duplicatas, rastreabilidade"],
    ["7", "Agent Enrichment", "Alimenta os agentes com o novo conhecimento"],
    ["8", "Finalização", "Atualiza STATE.json, logs, índices"],
], col_widths=[1.2*cm, 4*cm, CONTENT_W - 5.2*cm])
story += [phases, spacer()]

story += h2("Scripts Python Ativos (core/intelligence/)")
story += [
    gray("autonomous_processor.py · dossier_updater.py · entity_normalizer.py · theme_analyzer.py"),
    gray("validate_layers.py · pipeline_utils.py · org_chain_detector.py · viability_scorer.py"),
    gray("+ scripts específicos por fonte: chunk_*, extract_*, narrative_*"),
    spacer(),
]

story += h2("Comandos do Pipeline")
story += [table([
    ["Comando", "Descrição"],
    ["/ingest [url/path]", "Porta de entrada — ingere qualquer material na inbox"],
    ["/process-jarvis", "Processa a inbox com as 8 fases completas"],
    ["/process-inbox", "Processamento em lote (--next, --all, --person)"],
    ["/process-video [url]", "Especializado em vídeos YouTube e arquivos locais"],
    ["/jarvis-full [url]", "Pipeline completo sem paradas: ingest + process + enrich"],
    ["/mission", "Orquestra missões longas via planilha Google Sheets"],
    ["/mission-autopilot", "Execução autônoma 100%, zero interrupções"],
    ["/scan-inbox", "Mostra o que está pendente de processamento"],
], col_widths=[4.5*cm, CONTENT_W - 4.5*cm]), spacer()]

# ════ 2. KNOWLEDGE BASE ════════════════════════════════════════════════════
story += h1("2. Knowledge Base Populada")
story += [body("Base de conhecimento estruturada em camadas, alimentada automaticamente pelo pipeline.")]
story += [spacer()]

story += h2("Estrutura de Diretórios")
story += [
    code("knowledge/sources/   → material processado bruto por fonte"),
    code("knowledge/dna/       → DNA Cognitivo de cada pessoa/domínio"),
    code("knowledge/dossiers/  → dossiês consolidados (pessoas + temas)"),
    code("knowledge/playbooks/ → playbooks operacionais prontos para uso"),
    spacer(),
]

story += h2("DNA Cognitivo — 5 Camadas por Pessoa")
story += [table([
    ["Camada", "Nome", "Conteúdo"],
    ["L1", "Filosofias", "Crenças centrais e visão de mundo"],
    ["L2", "Modelos Mentais", "Como a pessoa pensa e decide"],
    ["L3", "Heurísticas", "Regras práticas e atalhos de decisão"],
    ["L4", "Frameworks", "Metodologias estruturadas"],
    ["L5", "Metodologias", "Implementações passo a passo"],
], col_widths=[1.2*cm, 4*cm, CONTENT_W - 5.2*cm]), spacer()]

story += h2("43 Especialistas com DNA Extraído")
experts_data = [
    ["Alan Nicolas", "Ann Handley", "Chip Heath & Dan Heath", "Chris Anderson"],
    ["Dan Kennedy", "Donald Miller", "Eugene Schwartz", "Joe Pulizzi"],
    ["Joseph O'Connor", "Joseph Sugarman", "Nir Eyal", "Outlier Hub"],
    ["Peter Thiel", "Philip Kotler", "Richard Koch", "Robert Cialdini"],
    ["Russell Brunson", "Tallis Gomes", "Tim Ferriss", "Tony Robbins"],
    ["Alex Hormozi", "Cole Gordon", "Jeremy Haynes", "Jeremy Miner"],
    ["Sam Ovens", "Jordan Lee", "André Kliousoff", "Dener Lippert"],
    ["Flávio Augusto", "Lázaro do Carmo", "Rami Goldratt", "+ outros"],
]
story += [table(
    [[""] * 4] + experts_data,
    col_widths=[CONTENT_W/4]*4,
    header=False
), spacer()]

story += h2("Dossiês (34 de Pessoas + 6 Temáticos)")
story += [
    body("Cada dossiê consolida todo o conhecimento sobre uma pessoa ou tema em um único documento com rastreabilidade completa."),
    spacer(4),
    body("<b>Dossiês temáticos ativos:</b> Alta Performance · Modelo Hook · AIOS Sistema · AIOS Squad · Entropia Organizacional · Decisão de Alta Performance"),
    spacer(),
]

story += h2("Comandos da Knowledge Base")
story += [table([
    ["Comando", "Descrição"],
    ["/extract-knowledge [path]", "Transforma transcrições brutas em insights estruturados"],
    ["/extract-dna [pessoa]", "Extrai DNA Cognitivo nas 5 camadas de uma pessoa"],
    ["/view-dna [pessoa|domínio]", "Visualiza DNA extraído (com --camada para filtrar)"],
    ["/dossiers", "Status de todos os dossiês (--persons, --themes, --incomplete)"],
    ["/rag-search 'query'", "Busca semântica nos 7.472 chunks via Voyage AI"],
], col_widths=[5.5*cm, CONTENT_W - 5.5*cm]), spacer()]

# ════ 3. MIND CLONES ═══════════════════════════════════════════════════════
story += h1("3. Mind Clones — 7 Agentes Ativos")
story += [body("Cada Mind Clone possui SOUL (personalidade) + MEMORY (conhecimento atualizado) + DNA (5 camadas extraídas). Respondem como aquela pessoa responderia — baseado no conhecimento real processado, não em personagem genérico.")]
story += [spacer()]

story += [table([
    ["Agente", "Especialidade Principal", "Status"],
    ["Alex Hormozi", "Frameworks de oferta, aquisição, retenção e escala", "✓ Soul + Memory"],
    ["Cole Gordon", "Gestão de times de vendas, remote closing", "✓ Soul + Memory"],
    ["Jeremy Haynes", "Marketing de resposta direta, paid media", "✓ Soul + Memory"],
    ["Jeremy Miner", "NEPQ, vendas consultivas, psicologia do comprador", "✓ Soul + Memory"],
    ["Russell Brunson", "Funnels, copywriting, DotCom/Expert Secrets", "✓ Soul + Memory"],
    ["Richard Koch", "Princípio 80/20, estratégia de foco, alocação", "✓ Soul"],
    ["The Scalable Company", "Modelos de escala, sistemas operacionais", "✓ Soul + Memory"],
], col_widths=[4*cm, 8*cm, 3*cm]), spacer()]

story += [body("Comandos: "), spacer(3)]
story += [
    code("/ask hormozi 'Como estruturar compensação do time de vendas?'"),
    code("/ask cole 'Qual métrica mais importante para remote closing?'"),
    code("/compare hormozi,cole 'Modelo de comissão ideal para closers?'"),
    spacer(),
]

# ════ 4. CARGO AGENTS ══════════════════════════════════════════════════════
story += h1("4. Agentes de Cargo — 14 Ativos")
story += [body("Agentes funcionais que respondem pela perspectiva do cargo, integrando o DNA de múltiplos especialistas relevantes para aquela função.")]
story += [spacer()]

story += [table([
    ["Área", "Agente", "ID"],
    ["C-Level", "Chief Revenue Officer", "cro"],
    ["C-Level", "Chief Marketing Officer", "cmo"],
    ["C-Level", "Chief Financial Officer", "cfo"],
    ["C-Level", "Chief Operating Officer", "coo"],
    ["Sales", "Closer", "closer"],
    ["Sales", "Sales Development (outbound)", "sds"],
    ["Sales", "Lead Nurturing", "lns"],
    ["Sales", "Business Development", "bdr"],
    ["Sales", "NEPQ Specialist", "nepq-specialist"],
    ["Sales", "Sales Coordinator", "sales-coordinator"],
    ["Sales", "Sales Manager", "sales-manager"],
    ["Sales", "Sales Lead", "sales-lead"],
    ["Sales", "Customer Success", "customer-success"],
    ["Marketing", "Paid Media Specialist", "paid-media-specialist"],
], col_widths=[3*cm, 7*cm, 5*cm]), spacer()]

story += [
    code("/ask cro 'Estrutura ideal de time para faturar R$1M/mês?'"),
    code("/ask cfo 'Quando faz sentido levantar capital externo?'"),
    code("/debate cro,cfo 'Investir R$500k em expansão de time no Q1?'"),
    spacer(),
]

# ════ 5. CONCLAVE ══════════════════════════════════════════════════════════
story += h1("5. Conselho (Conclave) — 3 Agentes Deliberativos")
story += [body("Sistema de meta-avaliação para decisões estratégicas. Não responde diretamente — avalia o debate dos outros agentes.")]
story += [spacer()]

story += [table([
    ["Agente", "Função"],
    ["Crítico Metodológico", "Questiona premissas, identifica falhas lógicas, exige evidências"],
    ["Advogado do Diabo", "Assume posição oposta, força pensamento de segundo ordem"],
    ["Sintetizador", "Consolida pontos de tensão em recomendação acionável"],
], col_widths=[5*cm, CONTENT_W - 5*cm]), spacer()]

story += h2("Fluxo do /conclave")
story += [
    bullet("Fase 1 — Cargos relevantes debatem com base no DNA extraído"),
    bullet("Fase 2 — Conselho avalia o debate (Crítico + Advogado + Sintetizador)"),
    bullet("Fase 3 — Síntese final com recomendação e nível de confiança"),
    spacer(),
    code("/conclave 'Mudar modelo de comissão de closers de 10% para 15%?'"),
    code("/conclave 'Investir R$500k em expansão de time no Q1?'"),
    spacer(),
]

# ════ 6. SQUADS ═══════════════════════════════════════════════════════════
story += h1("6. Squads — 24 Times, 243 Agentes")
story += [body("Times especializados de múltiplos agentes para tarefas específicas. Cada squad tem orquestrador + especialistas.")]
story += [spacer()]

story += [table([
    ["Squad", "Especialidade"],
    ["hormozi-squad", "Frameworks Hormozi aplicados a negócios"],
    ["c-level-squad", "Deliberação executiva de alto nível"],
    ["copy-squad", "Copywriting e narrativa persuasiva"],
    ["traffic-masters", "Tráfego pago e estratégia de aquisição"],
    ["storytelling-squad", "Narrativa e estrutura de histórias"],
    ["brand-squad", "Identidade e posicionamento de marca"],
    ["movement-squad", "Construção de movimento e comunidade"],
    ["data-squad", "Análise de dados e métricas de negócio"],
    ["design-squad", "Design e identidade visual"],
    ["cybersecurity-squad", "Segurança e proteção de sistemas"],
    ["advisory-board", "Conselho consultivo estratégico"],
    ["espio-007", "Inteligência competitiva e análise de mercado"],
    ["aiox-copywriting", "Copywriting avançado com IA"],
    ["aiox-curator", "Curadoria e organização de conteúdo"],
    ["aiox-deep-research", "Pesquisa profunda e análise exaustiva"],
    ["aiox-design-pro", "Design profissional e produção visual"],
    ["aiox-dispatch", "Orquestração e roteamento de tarefas"],
    ["aiox-education", "Conteúdo educacional e didático"],
    ["aiox-kaizen", "Melhoria contínua e otimização de processos"],
    ["aiox-seo", "SEO e estratégia de busca orgânica"],
    ["aiox-squad-creator", "Criação e configuração de novos squads"],
    ["claude-code-mastery", "Desenvolvimento e automação com Claude Code"],
    ["garfield-time", "Otimização de tempo e produtividade"],
    ["pai-do-trafego", "Tráfego, conversão e funis de venda"],
], col_widths=[5*cm, CONTENT_W - 5*cm]), spacer()]

# ════ 7. EMPRESA ══════════════════════════════════════════════════════════
story += h1("7. Agente da Sua Empresa (agents/sua-empresa/)")
story += [
    body("Estrutura separada para dados organizacionais internos. Não mistura com o conhecimento dos especialistas externos."),
    spacer(),
    body("<b>Contém:</b> personas internas, job descriptions, processos operacionais, KPIs, organograma, contexto estratégico próprio."),
    spacer(),
    body("<b>Alimentado via:</b>"),
    code("/ingest-empresa ./organograma.pdf"),
    code("/ingest-empresa ./processos-de-vendas.md"),
    spacer(),
    body("Permite que os agentes de cargo respondam considerando o contexto real da empresa, não apenas teoria genérica."),
    spacer(),
]

# ════ 8. RAG ══════════════════════════════════════════════════════════════
story += h1("8. Busca Semântica (RAG)")
story += [
    body("Busca por significado nos 7.472 chunks usando embeddings Voyage AI. Não depende de palavra-chave exata — entende o contexto da pergunta e retorna trechos relevantes com citação de fonte."),
    spacer(),
    code("/rag-search 'Como estruturar compensação variável para closers?'"),
    code("/rag-search 'Qual framework de oferta tem maior conversão?'"),
    code("/rag-search 'Como identificar e eliminar crenças limitantes do time?'"),
    spacer(),
    body("Retorna os N chunks mais relevantes com: fonte, autor, contexto, nível de confiança."),
    spacer(),
]

# ════ 9. MISSÕES ══════════════════════════════════════════════════════════
story += h1("9. Gestão de Missões")
story += [
    body("Sistema para orquestrar missões longas com múltiplas fontes. Usa planilha Google Sheets como controle central."),
    spacer(),
]
story += [table([
    ["Subcomando", "Função"],
    ["/mission status", "Status completo da missão atual com progresso por fonte"],
    ["/mission resume", "Continuar de onde parou"],
    ["/mission pause", "Pausar após batch atual"],
    ["/mission new [id]", "Iniciar nova missão com planilha Google Sheets"],
    ["/mission sync-source [id]", "Sincronizar planilha com inbox (ler + comparar + baixar)"],
    ["/mission validate-source", "Validar completude da source atual"],
    ["/mission report", "Gerar relatório final da missão"],
    ["/mission-autopilot [id]", "Execução autônoma completa — 5 fases sem interrupção"],
], col_widths=[5.5*cm, CONTENT_W - 5.5*cm]), spacer()]

story += h2("Flags do /mission-autopilot")
story += [
    code("--from-phase N    → iniciar da fase N (1-5)"),
    code("--batch-size N    → tamanho do batch na Fase 4 (padrão: 8)"),
    code("--skip-download   → pular Fase 2 (já tem arquivos)"),
    code("--dry-run         → preview sem executar"),
    code("--verbose         → logs expandidos"),
    spacer(),
]

# ════ 10. MIS ═════════════════════════════════════════════════════════════
story += h1("10. MIS — Market Intelligence System")
story += [
    body("Módulo independente que monitora produtos campeões e dores de mercado por nicho. Integrado via mis_agent.py."),
    spacer(),
]
story += [table([
    ["Função", "Descrição"],
    ["Produtos Campeões", "Monitoramento de produtos com maior tração no mercado"],
    ["Radar de Dores", "Alertas de dores não atendidas por nicho"],
    ["Ciclos de Análise", "Histórico e comparação entre ciclos anteriores"],
    ["Export para KB", "Exporta dossiês completos para knowledge/mis/"],
], col_widths=[5*cm, CONTENT_W - 5*cm]), spacer()]
story += [
    code("/mis-briefing  → briefing visual completo do mercado"),
    spacer(),
]

# ════ 11. EVOLUÇÃO ═════════════════════════════════════════════════════════
story += h1("11. Evolução Autônoma e Benchmark")
story += [
    body("Ciclo de melhoria contínua do próprio sistema, coordenando 3 agentes especializados."),
    spacer(),
]
story += [table([
    ["Agente", "Função no /evolve"],
    ["EVOLVER", "Identifica gaps e implementa melhorias no sistema"],
    ["CRITIC", "Questiona e valida cada mudança proposta"],
    ["BENCHMARK", "Compara com melhores práticas do mercado"],
], col_widths=[4*cm, CONTENT_W - 4*cm]), spacer()]

story += [
    code("/evolve          → ativa ciclo de evolução autônoma"),
    code("/benchmark       → análise comparativa com Notion, Obsidian, CrewAI, etc."),
    spacer(),
]

# ════ 12. RESUMO FINAL ════════════════════════════════════════════════════
story += h1("Resumo — O que o Premium Entrega")
story += [spacer()]

summary_data = [
    ["Componente", "Quantidade", "Status"],
    ["Mind Clones (especialistas reais)", "7", "✓ Ativos"],
    ["Agentes de Cargo", "14", "✓ Ativos"],
    ["Agentes Conclave", "3", "✓ Ativos"],
    ["Squads especializados", "24", "✓ Ativos"],
    ["Agentes em squads", "243", "✓ Ativos"],
    ["Total de agentes", "267", "✓ Ativos"],
    ["Especialistas com DNA extraído", "43", "✓ Processados"],
    ["Insights estruturados", "733", "✓ Na KB"],
    ["Chunks semânticos mapeados", "7.472", "✓ Indexados"],
    ["Dossiês de pessoas", "34", "✓ Na KB"],
    ["Dossiês temáticos", "6", "✓ Na KB"],
    ["Playbooks operacionais", "2+", "✓ Na KB"],
    ["Scripts Python de processamento", "40+", "✓ Ativos"],
    ["Workflows YAML", "4", "✓ Ativos"],
]
story += [table(summary_data, col_widths=[8*cm, 3*cm, CONTENT_W - 11*cm]), spacer(12)]

story += [
    hr(ACCENT, 1),
    spacer(8),
    Paragraph("\"Preliminary tests indicate... success.\"", style_cover_meta),
    spacer(4),
    Paragraph("— JARVIS v2.0  ·  Mega Brain Premium", style_cover_meta),
]

# ── Build ──────────────────────────────────────────────────────────────────
doc.build(story, onFirstPage=page_bg, onLaterPages=page_bg)
print(f"PDF gerado: {OUTPUT}")
