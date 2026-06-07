from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

OUTPUT = "d:/MEGABRAIN/artifacts/Spy-Universal-Benchmarking.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    rightMargin=2*cm,
    leftMargin=2*cm,
    topMargin=2*cm,
    bottomMargin=2*cm,
    title="Spy Squad — Universal Benchmarking",
    author="JARVIS / Mega Brain"
)

W, H = A4

# ── Cores
DARK    = colors.HexColor("#0D1117")
ACCENT  = colors.HexColor("#238636")
BLUE    = colors.HexColor("#1F6FEB")
GRAY    = colors.HexColor("#8B949E")
LIGHT   = colors.HexColor("#161B22")
WHITE   = colors.HexColor("#F0F6FC")
YELLOW  = colors.HexColor("#D29922")
RED     = colors.HexColor("#DA3633")
BG_ROW  = colors.HexColor("#21262D")

styles = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

title_style = S("Title2",
    fontSize=26, leading=32, textColor=WHITE,
    fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)

subtitle_style = S("Sub",
    fontSize=11, leading=14, textColor=GRAY,
    fontName="Helvetica", alignment=TA_CENTER, spaceAfter=20)

h1_style = S("H1",
    fontSize=16, leading=22, textColor=ACCENT,
    fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=6,
    borderPad=4)

h2_style = S("H2",
    fontSize=13, leading=18, textColor=BLUE,
    fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4)

h3_style = S("H3",
    fontSize=11, leading=15, textColor=YELLOW,
    fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3)

body_style = S("Body2",
    fontSize=9.5, leading=14, textColor=WHITE,
    fontName="Helvetica", spaceAfter=4)

code_style = S("Code2",
    fontSize=8.5, leading=13, textColor=colors.HexColor("#79C0FF"),
    fontName="Courier", spaceAfter=2,
    leftIndent=12, backColor=LIGHT)

note_style = S("Note",
    fontSize=8.5, leading=12, textColor=GRAY,
    fontName="Helvetica-Oblique", spaceAfter=3, leftIndent=12)

bullet_style = S("Bullet2",
    fontSize=9.5, leading=14, textColor=WHITE,
    fontName="Helvetica", leftIndent=16, spaceAfter=3,
    bulletIndent=6)

tag_style = S("Tag",
    fontSize=8, leading=11, textColor=ACCENT,
    fontName="Helvetica-Bold", alignment=TA_CENTER)

def HR(color=ACCENT, thickness=1):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=8, spaceBefore=4)

def sp(h=6):
    return Spacer(1, h)

def h1(txt):  return Paragraph(txt, h1_style)
def h2(txt):  return Paragraph(txt, h2_style)
def h3(txt):  return Paragraph(txt, h3_style)
def p(txt):   return Paragraph(txt, body_style)
def c(txt):   return Paragraph(txt, code_style)
def note(txt):return Paragraph(txt, note_style)
def b(txt):   return Paragraph(f"• {txt}", bullet_style)

def table(data, col_widths=None, header=True):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    cmds = [
        ("BACKGROUND", (0,0), (-1,0), ACCENT if header else LIGHT),
        ("TEXTCOLOR", (0,0), (-1,0), DARK if header else WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [LIGHT, DARK]),
        ("TEXTCOLOR", (0,1), (-1,-1), WHITE),
        ("GRID", (0,0), (-1,-1), 0.3, GRAY),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("RIGHTPADDING", (0,0), (-1,-1), 7),
    ]
    t.setStyle(TableStyle(cmds))
    return t

# ── Cover page background (fake via first element)
def cover_block():
    items = []
    items.append(sp(60))
    items.append(Paragraph("🕵️", S("Icon", fontSize=48, alignment=TA_CENTER, spaceAfter=8, textColor=WHITE, fontName="Helvetica")))
    items.append(Paragraph("SPY SQUAD", title_style))
    items.append(Paragraph("Universal Benchmarking", S("Sub2", fontSize=18, leading=22, textColor=ACCENT, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=6)))
    items.append(Paragraph("Guia Completo de Inteligência Competitiva", subtitle_style))
    items.append(sp(8))
    items.append(HR(ACCENT, 2))
    items.append(sp(4))
    items.append(Paragraph("Mega Brain AI  •  JARVIS v2.0  •  2026", S("Footer", fontSize=9, textColor=GRAY, fontName="Helvetica", alignment=TA_CENTER)))
    items.append(sp(80))
    return items

story = []

# ── COVER
story += cover_block()

# ══════════════════════════════════════
# SEÇÃO 1 — O que é
# ══════════════════════════════════════
story += [HR(ACCENT, 2), h1("1. O Que É o Universal Benchmarking"), HR(GRAY, 0.5)]
story.append(p("O <b>Bench Analyst</b> é um sistema de análise comparativa estruturada. A premissa central:"))
story.append(p("<b>Nunca usar opinião — só dados verificáveis com fonte citada e score quantitativo.</b>"))
story.append(sp())
story.append(h2("Dois princípios que o diferenciam"))
story.append(b("<b>Dual output obrigatório</b> — tudo gera <font color='#79C0FF'>.json</font> (para máquinas) + <font color='#79C0FF'>.md</font> (para humanos)"))
story.append(b("<b>Exhaustive over summary</b> — análise longa e detalhada supera resumo superficial"))

# ══════════════════════════════════════
# SEÇÃO 2 — 5 tipos
# ══════════════════════════════════════
story += [sp(10), HR(ACCENT, 2), h1("2. Os 5 Tipos de Comparação"), HR(GRAY, 0.5)]

data = [
    ["Tipo", "O que compara", "Dimensões de scoring"],
    ["codebase", "Frameworks, repositórios, sistemas", "Architecture, Testing, Automation, Extensibility, Code Quality"],
    ["llm", "Modelos de IA (Claude vs GPT vs Gemini…)", "Reasoning, Coding, Math, Speed, Cost, Context Window, Tool Use"],
    ["product", "SaaS, ferramentas, plataformas", "Features, UX/Design, Pricing, Integration, Support, Market Fit"],
    ["company", "Empresas, concorrentes diretos", "Revenue, Market Share, Team, Funding, Technology, Brand"],
    ["technology", "Linguagens, DBs, frameworks técnicos", "Maturity, Ecosystem, DX, Performance, Scalability, Community"],
]
story.append(table(data, col_widths=[3*cm, 6*cm, 8.5*cm]))

# ══════════════════════════════════════
# SEÇÃO 3 — Pipeline
# ══════════════════════════════════════
story += [sp(10), HR(ACCENT, 2), h1("3. O Pipeline Completo (10 Fases)"), HR(GRAY, 0.5)]

pipeline = [
    ["Fase", "Nome", "O que faz"],
    ["0", "DETECT", "Detecta automaticamente o tipo de comparação"],
    ["1", "INVENTORY A", "Escaneia baseline do sujeito A"],
    ["2", "INVENTORY B", "Escaneia baseline do sujeito B"],
    ["3", "MATRIX", "Tabela feature-a-feature com paridade (1–5)"],
    ["4", "SCORE", "Scoring ponderado multi-dimensão (0–100 por eixo)"],
    ["5", "GAP", "Gap analysis bidirecional (o que A tem e B não, e vice-versa)"],
    ["6", "DEEP DIVE", "Análise profunda tipo-específica (código, UX, financeiro…)"],
    ["7", "REPORT", "Relatório executivo com recomendações"],
    ["8", "BATTLE CARD", "1 página de comparação para decisão rápida"],
    ["9", "QUALITY GATE", "Validação: fontes citadas, JSONs válidos, evidências presentes"],
]
story.append(table(pipeline, col_widths=[1.5*cm, 3.5*cm, 12.5*cm]))

# ══════════════════════════════════════
# SEÇÃO 4 — Níveis de profundidade
# ══════════════════════════════════════
story += [sp(10), HR(ACCENT, 2), h1("4. Os 3 Níveis de Profundidade"), HR(GRAY, 0.5)]

niveis = [
    ["Nível", "Comando", "Artefatos", "Tempo", "Quando usar"],
    ["Quick", "*bench-quick X", "3", "~15 min", "Reconhecimento inicial"],
    ["Standard", "*bench-matrix + *bench-score + *bench-gap", "8", "~30 min", "Decisão estratégica"],
    ["Full", "*bench X vs Y", "16+", "~60 min", "Auditoria completa"],
]
story.append(table(niveis, col_widths=[2*cm, 5.5*cm, 2.5*cm, 2.5*cm, 5*cm]))

# ══════════════════════════════════════
# SEÇÃO 5 — Artefatos
# ══════════════════════════════════════
story += [sp(10), HR(ACCENT, 2), h1("5. Artefatos Gerados"), HR(GRAY, 0.5)]
story.append(p("Tudo salvo em <font color='#79C0FF'>docs/bench/{a}-vs-{b}/</font>"))
story.append(sp(4))

artefatos = [
    ["Arquivo", "Tipo", "Formato", "Para quem"],
    ["metadata.json", "Metadados", "JSON", "Sistema"],
    ["inventory-A.json / .md", "Inventário A", "JSON + MD", "Arquitetos"],
    ["inventory-B.json / .md", "Inventário B", "JSON + MD", "Arquitetos"],
    ["comparison-matrix.json / .md", "Matriz comparativa", "JSON + MD", "Todos"],
    ["scorecard.json / .md", "Scores 0–100 por dimensão", "JSON + MD", "Liderança"],
    ["gap-analysis.json / .md", "O que falta em cada lado", "JSON + MD", "Produto"],
    ["battle-card.md", "1 página para decidir na hora", "MD", "Decisores"],
    ["executive-report.md", "Relatório executivo completo", "MD", "C-Level"],
    ["deep/ (tipo-específico)", "Análise profunda", "MD", "Especialistas"],
]
story.append(table(artefatos, col_widths=[5*cm, 4*cm, 2.5*cm, 3*cm]))

story.append(sp(8))
story.append(h3("Deep artifacts por tipo"))
deep_data = [
    ["Tipo", "Artefatos deep"],
    ["codebase", "component-comparison, hooks-analysis, absorption-roadmap, migration-playbook"],
    ["llm", "reasoning-eval, coding-eval, cost-analysis, benchmark-compilation"],
    ["product", "feature-comparison, ux-analysis, pricing-analysis, reviews-sentiment"],
    ["company", "market-position, swot-analysis, financial-comparison, team-analysis"],
    ["technology", "maturity-assessment, ecosystem-analysis, dx-comparison, performance-benchmarks"],
]
story.append(table(deep_data, col_widths=[3*cm, 14.5*cm]))

# ══════════════════════════════════════
# SEÇÃO 6 — Sistema de paridade
# ══════════════════════════════════════
story += [sp(10), HR(ACCENT, 2), h1("6. Sistema de Paridade (Equivalência)"), HR(GRAY, 0.5)]
story.append(p("Cada feature comparada recebe uma classificação de equivalência:"))
story.append(sp(4))

paridade = [
    ["Score", "Label", "Significado"],
    ["5/5", "Forte", "Funcionalidade equivalente, mesma profundidade e cobertura"],
    ["4/5", "Parcial Alta", "Equivalente com pequenas diferenças de escopo"],
    ["3/5", "Parcial", "Diferenças significativas"],
    ["2/5", "Fraco", "Gap substancial"],
    ["1/5", "Sem equivalente", "Não existe correspondência direta"],
]
story.append(table(paridade, col_widths=[2*cm, 4*cm, 11.5*cm]))

# ══════════════════════════════════════
# SEÇÃO 7 — Comandos
# ══════════════════════════════════════
story += [sp(10), HR(ACCENT, 2), h1("7. Todos os Comandos Disponíveis"), HR(GRAY, 0.5)]

story.append(h2("Pipeline Completo"))
cmds_full = [
    ["Comando", "Descrição"],
    ["*bench {A} vs {B}", "Pipeline universal completo (10 fases, 16+ artefatos)"],
    ["*bench-matrix {A} vs {B}", "Matriz de comparação universal"],
    ["*bench-score {A} vs {B}", "Scoring quantitativo multi-dimensão"],
    ["*bench-gap {A} vs {B}", "Gap analysis bidirecional"],
    ["*bench-inventory", "Snapshot baseline do sistema atual"],
]
story.append(table(cmds_full, col_widths=[6*cm, 11.5*cm]))

story.append(sp(6))
story.append(h2("Comparações Tipo-Específicas"))
cmds_type = [
    ["Comando", "Tipo", "Dimensões principais"],
    ["*bench-llm {A} vs {B}", "LLM", "Reasoning, Coding, Speed, Cost, Context"],
    ["*bench-product {A} vs {B}", "Produto", "Features, UX, Pricing, Integration"],
    ["*bench-company {A} vs {B}", "Empresa", "Revenue, Market Share, Team, Funding"],
    ["*bench-tech {A} vs {B}", "Tecnologia", "Maturity, DX, Ecosystem, Performance"],
]
story.append(table(cmds_type, col_widths=[5.5*cm, 2.5*cm, 9.5*cm]))

story.append(sp(6))
story.append(h2("Análise Profunda de Codebase"))
cmds_code = [
    ["Comando", "Descrição"],
    ["*bench-quick {X}", "Comparação rápida (agentes + workflows) — 3 artefatos"],
    ["*bench-deep {X}", "Deep component-by-component com blocos de código"],
    ["*bench-hooks {X}", "Análise profunda de hooks/subsystems"],
    ["*bench-trace", "Mapa de rastreabilidade comando → task → artefato"],
    ["*bench-migrate {X}", "Playbook de migração do concorrente para o sistema"],
]
story.append(table(cmds_code, col_widths=[5*cm, 12.5*cm]))

# ══════════════════════════════════════
# SEÇÃO 8 — Casos de uso
# ══════════════════════════════════════
story += [sp(10), HR(ACCENT, 2), h1("8. Casos de Uso Concretos"), HR(GRAY, 0.5)]

casos = [
    ["Situação", "Comando recomendado"],
    ["Notion vs ClickUp — qual usar na operação?", "*bench-product Notion vs ClickUp"],
    ["Claude Opus 4 vs GPT-4o — qual no pipeline?", "*bench-llm claude-opus-4-7 vs gpt-4o"],
    ["O que meu concorrente faz melhor que eu?", "*bench-company MinhaEmpresa vs Concorrente"],
    ["React vs Vue para o próximo projeto?", "*bench-tech React vs Vue"],
    ["Absorver features do BMAD para o AIOX?", "*bench aiox vs bmad + *bench-gap bmad"],
    ["Entender gaps antes de uma decisão de produto?", "*bench-quick {framework} (Quick, 15 min)"],
    ["Relatório executivo para apresentar à liderança?", "*bench {A} vs {B} (Full pipeline, 60 min)"],
]
story.append(table(casos, col_widths=[8*cm, 9.5*cm]))

# ══════════════════════════════════════
# SEÇÃO 9 — Níveis de confiança
# ══════════════════════════════════════
story += [sp(10), HR(ACCENT, 2), h1("9. Níveis de Confiança dos Dados"), HR(GRAY, 0.5)]
story.append(p("Todo dado coletado recebe um nível de confiança explícito no output:"))
story.append(sp(4))

confianca = [
    ["Nível", "Threshold", "Fonte", "Ação"],
    ["High", ">= 0.9", "Repositório local / código real", "Usar diretamente"],
    ["Medium", "0.7 – 0.89", "Documentação oficial", "Verificar pontos críticos"],
    ["Low", "< 0.7", "Web / docs incompletos", "Validar manualmente antes de decidir"],
]
story.append(table(confianca, col_widths=[2.5*cm, 3*cm, 5.5*cm, 6.5*cm]))

story.append(sp(8))
story.append(note("Para comparações de codebase, o Bench Analyst exige clone local do repositório. "
                  "Nunca estima estrutura — conta os arquivos reais. Se não houver URL do repo, para e pede antes de continuar."))

# ══════════════════════════════════════
# SEÇÃO 10 — Anti-patterns
# ══════════════════════════════════════
story += [sp(10), HR(ACCENT, 2), h1("10. O Que Nunca Fazer (Anti-Patterns)"), HR(GRAY, 0.5)]

never = [
    ["❌ Nunca fazer", "✅ Sempre fazer"],
    ["Inflar scores para parecer melhor", "Reportar gaps honestamente"],
    ["Resumir quando deveria mostrar código lado a lado", "Evidência side-by-side com blocos reais"],
    ["Afirmar equivalência sem evidência", "Citar arquivo, URL ou artefato específico"],
    ["Ignorar vantagens do concorrente", "Documentar gaps E diferenciais"],
    ["Usar 'melhor/pior' sem delta quantificado", "Usar delta de scores numericamente"],
    ["Gerar só .md sem .json correspondente", "Dual output obrigatório (JSON + MD)"],
    ["Assumir comportamento do concorrente pelo nome", "Verificar na fonte (clone local ou docs)"],
]
story.append(table(never, col_widths=[8.5*cm, 9*cm]))

# ══════════════════════════════════════
# RODAPÉ
# ══════════════════════════════════════
story += [sp(16), HR(ACCENT, 2), sp(4)]
story.append(Paragraph(
    "Spy Squad v3.0  •  Bench Analyst v3.0  •  Mega Brain AI  •  JARVIS v2.0  •  2026",
    S("Foot", fontSize=8, textColor=GRAY, fontName="Helvetica", alignment=TA_CENTER)
))

# ── Build
doc.build(story)
print(f"PDF gerado: {OUTPUT}")
