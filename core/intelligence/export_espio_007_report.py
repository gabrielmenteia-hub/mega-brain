"""
Espião 007 — Exportar Relatório de Inteligência para PDF
Gerado por: Espião 007 Squad / JARVIS v2.0
Data: 2026-03-19
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.platypus import PageBreak
from reportlab.lib.colors import HexColor
import os

# ── Cores ──────────────────────────────────────────────────────────────────
BLACK       = HexColor("#0D0D0D")
WHITE       = HexColor("#FFFFFF")
GOLD        = HexColor("#C9A84C")
DARK_BG     = HexColor("#1A1A2E")
DARK_CARD   = HexColor("#16213E")
ACCENT_RED  = HexColor("#E63946")
ACCENT_GRN  = HexColor("#2DC653")
ACCENT_YLW  = HexColor("#FFD60A")
GREY_LIGHT  = HexColor("#E8E8E8")
GREY_MID    = HexColor("#AAAAAA")
SECTION_BG  = HexColor("#F5F5F5")

# ── Estilos ────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

style_title = S("title",
    fontName="Helvetica-Bold", fontSize=22, textColor=WHITE,
    alignment=TA_CENTER, spaceAfter=4)

style_subtitle = S("subtitle",
    fontName="Helvetica", fontSize=11, textColor=GOLD,
    alignment=TA_CENTER, spaceAfter=2)

style_section = S("section",
    fontName="Helvetica-Bold", fontSize=13, textColor=WHITE,
    spaceBefore=8, spaceAfter=4, backColor=DARK_BG,
    borderPad=6)

style_product_title = S("product_title",
    fontName="Helvetica-Bold", fontSize=12, textColor=GOLD,
    spaceBefore=6, spaceAfter=3)

style_label = S("label",
    fontName="Helvetica-Bold", fontSize=9, textColor=DARK_BG)

style_body = S("body",
    fontName="Helvetica", fontSize=9, textColor=BLACK,
    leading=14, spaceAfter=3, alignment=TA_JUSTIFY)

style_body_white = S("body_white",
    fontName="Helvetica", fontSize=9, textColor=WHITE,
    leading=14, spaceAfter=3)

style_alert = S("alert",
    fontName="Helvetica-BoldOblique", fontSize=8.5,
    textColor=ACCENT_RED, spaceAfter=3)

style_badge_ok = S("badge_ok",
    fontName="Helvetica-Bold", fontSize=8, textColor=WHITE,
    backColor=ACCENT_GRN, borderPad=3)

style_caption = S("caption",
    fontName="Helvetica-Oblique", fontSize=7.5, textColor=GREY_MID,
    alignment=TA_CENTER, spaceAfter=2)

style_toc = S("toc",
    fontName="Helvetica", fontSize=9, textColor=DARK_BG,
    leading=16, leftIndent=10)

# ── Helpers ────────────────────────────────────────────────────────────────
def hr(color=GOLD, thickness=1):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=4, spaceBefore=4)

def spacer(h=4):
    return Spacer(1, h * mm)

def section_header(text):
    data = [[Paragraph(text, style_section)]]
    t = Table(data, colWidths=[170 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    return t

def card(content_rows, bg=SECTION_BG, col_widths=None):
    """Cria um card com fundo colorido."""
    if col_widths is None:
        col_widths = [170 * mm]
    t = Table(content_rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), bg),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [bg]),
    ]))
    return t

def metric_row(items):
    """Row de métricas lado a lado."""
    cells = []
    for label, value, color in items:
        inner = Table([
            [Paragraph(f"<b>{value}</b>", ParagraphStyle("mv",
                fontName="Helvetica-Bold", fontSize=14, textColor=WHITE,
                alignment=TA_CENTER))],
            [Paragraph(label, ParagraphStyle("ml",
                fontName="Helvetica", fontSize=7.5, textColor=GREY_LIGHT,
                alignment=TA_CENTER))],
        ], colWidths=[38 * mm])
        inner.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), color),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        cells.append(inner)
    row = Table([cells], colWidths=[40 * mm] * len(items))
    row.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    return row

def kv_table(rows, col1=55, col2=115):
    """Tabela key:value simples."""
    data = [[
        Paragraph(f"<b>{k}</b>", style_label),
        Paragraph(v, style_body)
    ] for k, v in rows]
    t = Table(data, colWidths=[col1 * mm, col2 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), SECTION_BG),
        ("BACKGROUND",    (1, 0), (1, -1), WHITE),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("GRID",          (0, 0), (-1, -1), 0.3, GREY_MID),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    return t

def score_bar(label, score, max_score, color=ACCENT_GRN):
    pct = score / max_score
    filled = int(pct * 20)
    bar = "█" * filled + "░" * (20 - filled)
    text = f"<b>{label}</b>   {bar}  {score}/{max_score}"
    return Paragraph(text, ParagraphStyle("bar",
        fontName="Courier-Bold", fontSize=8, textColor=color,
        spaceAfter=3))

# ── Documento ──────────────────────────────────────────────────────────────
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "ESPIO-007-RELATORIO.pdf")
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    topMargin=15 * mm,
    bottomMargin=15 * mm,
    leftMargin=20 * mm,
    rightMargin=20 * mm,
    title="Espião 007 — Relatório de Inteligência de Mercado",
    author="Espião 007 Squad / JARVIS v2.0",
)

story = []

# ══════════════════════════════════════════════════════════════════
# CAPA
# ══════════════════════════════════════════════════════════════════
cover = Table([
    [Paragraph("🕵️  ESPIÃO 007", style_title)],
    [Paragraph("RELATÓRIO DE INTELIGÊNCIA DE MERCADO", style_subtitle)],
    [Spacer(1, 3 * mm)],
    [hr(GOLD, 2)],
    [Spacer(1, 3 * mm)],
    [Paragraph("Operação: Triple Play", S("op",
        fontName="Helvetica-Bold", fontSize=10, textColor=GOLD, alignment=TA_CENTER))],
    [Paragraph("Data: 19/03/2026  |  Plataforma: ClickBank  |  Mercado: US → BR",
        S("meta", fontName="Helvetica", fontSize=9, textColor=GREY_LIGHT, alignment=TA_CENTER))],
    [Spacer(1, 5 * mm)],
    [Paragraph(
        "Espionagem sistemática de 3 produtos campeões no mercado americano de infoprodutos.<br/>"
        "Inclui: Análise de funil · Copy · Oferta · Brief de adaptação para o mercado brasileiro.",
        S("desc", fontName="Helvetica", fontSize=10, textColor=WHITE,
          alignment=TA_CENTER, leading=16))],
], colWidths=[170 * mm])
cover.setStyle(TableStyle([
    ("BACKGROUND",    (0, 0), (-1, -1), DARK_BG),
    ("TOPPADDING",    (0, 0), (-1, -1), 12),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ("LEFTPADDING",   (0, 0), (-1, -1), 15),
    ("RIGHTPADDING",  (0, 0), (-1, -1), 15),
    ("ROUNDEDCORNERS", (0,0), (-1,-1), [6,6,6,6]),
]))
story.append(cover)
story.append(spacer(6))

# Métricas da operação
story.append(metric_row([
    ("Produtos Analisados", "3", DARK_BG),
    ("Nichos Cobertos",     "3", HexColor("#2C3E6B")),
    ("Plataforma",    "ClickBank", HexColor("#1A6B3C")),
    ("Oportunidade BR", "🔥🔥🔥", HexColor("#7B2D00")),
]))
story.append(spacer(6))

# ══════════════════════════════════════════════════════════════════
# ÍNDICE
# ══════════════════════════════════════════════════════════════════
story.append(section_header("  ÍNDICE"))
story.append(spacer(2))
toc_items = [
    "1.  Scout Report — Varredura de Mercado",
    "2.  Alvo 1: CitrusBurn — Saúde / Emagrecimento Feminino",
    "    2.1  Funil Mapeado",
    "    2.2  Análise de Copy",
    "    2.3  Decodificação de Oferta",
    "    2.4  Brief de Adaptação BR",
    "3.  Alvo 2: His Secret Obsession — Relacionamentos",
    "    3.1  Funil Mapeado",
    "    3.2  Análise de Copy",
    "    3.3  Decodificação de Oferta",
    "    3.4  Brief de Adaptação BR",
    "4.  Alvo 3: Billionaire Brain Wave — Riqueza + Espiritualidade",
    "    4.1  Funil Mapeado",
    "    4.2  Análise de Copy",
    "    4.3  Decodificação de Oferta",
    "    4.4  Brief de Adaptação BR",
    "5.  Síntese Final — Ranking e Próximos Passos",
    "6.  Links e Recursos",
]
for item in toc_items:
    story.append(Paragraph(item, style_toc))
story.append(spacer(4))

# ══════════════════════════════════════════════════════════════════
# 1. SCOUT REPORT
# ══════════════════════════════════════════════════════════════════
story.append(PageBreak())
story.append(section_header("  1. SCOUT REPORT — VARREDURA DE MERCADO"))
story.append(spacer(3))
story.append(Paragraph(
    "Varredura realizada em 19/03/2026 cobrindo ClickBank e JVZoo. "
    "9 alvos identificados em 7 nichos. Abaixo os 3 selecionados para missão completa.",
    style_body))
story.append(spacer(2))

scout_data = [
    [
        Paragraph("<b>#</b>", style_label),
        Paragraph("<b>Produto</b>", style_label),
        Paragraph("<b>Nicho</b>", style_label),
        Paragraph("<b>Plataforma</b>", style_label),
        Paragraph("<b>Métrica</b>", style_label),
        Paragraph("<b>Opor. BR</b>", style_label),
    ],
    [
        Paragraph("🥇", style_body),
        Paragraph("<b>CitrusBurn</b>", style_body),
        Paragraph("Saúde / Emagrecimento", style_body),
        Paragraph("ClickBank", style_body),
        Paragraph("#1 fev/2026 · EPC $9", style_body),
        Paragraph("🔥🔥🔥 Alta", style_body),
    ],
    [
        Paragraph("🥈", style_body),
        Paragraph("<b>His Secret Obsession</b>", style_body),
        Paragraph("Relacionamentos", style_body),
        Paragraph("ClickBank", style_body),
        Paragraph("Conv. 7% · APV $54", style_body),
        Paragraph("🔥🔥🔥 Alta", style_body),
    ],
    [
        Paragraph("🥉", style_body),
        Paragraph("<b>Billionaire Brain Wave</b>", style_body),
        Paragraph("Riqueza + Espiritualidade", style_body),
        Paragraph("ClickBank", style_body),
        Paragraph("EPC $0.58 · Conv. 1.35%", style_body),
        Paragraph("🔥🔥 Média-Alta", style_body),
    ],
]
scout_t = Table(scout_data, colWidths=[10*mm, 38*mm, 38*mm, 28*mm, 32*mm, 24*mm])
scout_t.setStyle(TableStyle([
    ("BACKGROUND",    (0, 0), (-1, 0), DARK_BG),
    ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
    ("BACKGROUND",    (0, 1), (-1, 1), HexColor("#FFF3E0")),
    ("BACKGROUND",    (0, 2), (-1, 2), HexColor("#FCE4EC")),
    ("BACKGROUND",    (0, 3), (-1, 3), HexColor("#E8F5E9")),
    ("ROWBACKGROUNDS",(0, 1), (-1, -1), [HexColor("#FFF3E0"), HexColor("#FCE4EC"), HexColor("#E8F5E9")]),
    ("GRID",          (0, 0), (-1, -1), 0.3, GREY_MID),
    ("TOPPADDING",    (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING",   (0, 0), (-1, -1), 5),
    ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN",         (0, 0), (0, -1), "CENTER"),
]))
story.append(scout_t)

# ══════════════════════════════════════════════════════════════════
# Função reutilizável para cada alvo
# ══════════════════════════════════════════════════════════════════
def product_report(story, number, emoji, name, niche, platform,
                   funnel, copy_data, offer_data, brief_data, links):

    story.append(PageBreak())

    # Título do produto
    header_t = Table([
        [Paragraph(f"{emoji}  {number}. {name}", S("ph",
            fontName="Helvetica-Bold", fontSize=16, textColor=WHITE,
            alignment=TA_LEFT))],
        [Paragraph(f"Nicho: {niche}  |  Plataforma: {platform}", S("phs",
            fontName="Helvetica", fontSize=9, textColor=GOLD,
            alignment=TA_LEFT))],
    ], colWidths=[170 * mm])
    header_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DARK_CARD),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
    ]))
    story.append(header_t)
    story.append(spacer(4))

    # 2.1 Funil
    story.append(Paragraph(f"  {number}.1  FUNIL MAPEADO", S("sh2",
        fontName="Helvetica-Bold", fontSize=10, textColor=WHITE,
        backColor=HexColor("#2C3E6B"), spaceBefore=4, spaceAfter=3,
        borderPad=5, leftIndent=0)))
    story.append(spacer(1))
    story.append(kv_table(funnel))
    story.append(spacer(4))

    # 2.2 Copy
    story.append(Paragraph(f"  {number}.2  ANÁLISE DE COPY", S("sh2",
        fontName="Helvetica-Bold", fontSize=10, textColor=WHITE,
        backColor=HexColor("#1A6B3C"), spaceBefore=4, spaceAfter=3,
        borderPad=5)))
    story.append(spacer(1))
    for label, value in copy_data:
        if label == "---":
            story.append(hr(GREY_MID, 0.5))
        else:
            story.append(kv_table([(label, value)]))
    story.append(spacer(4))

    # 2.3 Oferta
    story.append(Paragraph(f"  {number}.3  DECODIFICAÇÃO DE OFERTA", S("sh2",
        fontName="Helvetica-Bold", fontSize=10, textColor=WHITE,
        backColor=HexColor("#7B2D00"), spaceBefore=4, spaceAfter=3,
        borderPad=5)))
    story.append(spacer(1))
    story.append(kv_table(offer_data))
    story.append(spacer(4))

    # 2.4 Brief BR
    story.append(Paragraph(f"  {number}.4  BRIEF DE ADAPTAÇÃO — MERCADO BR", S("sh2",
        fontName="Helvetica-Bold", fontSize=10, textColor=WHITE,
        backColor=HexColor("#5D1A7A"), spaceBefore=4, spaceAfter=3,
        borderPad=5)))
    story.append(spacer(1))
    for section, content in brief_data:
        if section == "---":
            story.append(hr(ACCENT_RED, 0.5))
        else:
            story.append(Paragraph(f"<b>{section}</b>", S("bh",
                fontName="Helvetica-Bold", fontSize=9, textColor=HexColor("#5D1A7A"),
                spaceAfter=2)))
            story.append(Paragraph(content, style_body))
    story.append(spacer(2))

    # Links
    if links:
        story.append(Paragraph("  LINKS", S("lh",
            fontName="Helvetica-Bold", fontSize=9, textColor=DARK_BG,
            backColor=GREY_LIGHT, spaceBefore=2, spaceAfter=2, borderPad=4)))
        for lk in links:
            story.append(Paragraph(f"→ {lk}", S("lk",
                fontName="Helvetica", fontSize=8.5, textColor=HexColor("#1A0DAB"),
                spaceAfter=2)))

# ══════════════════════════════════════════════════════════════════
# ALVO 1: CITRUSBURNA
# ══════════════════════════════════════════════════════════════════
product_report(
    story,
    number="2",
    emoji="🍊",
    name="CitrusBurn",
    niche="Saúde / Emagrecimento Feminino",
    platform="ClickBank · Suplemento Físico",
    funnel=[
        ("Formato VSL",     "VSL + Long-form copy | Mecanismo: 'The Orange Peel Trick'"),
        ("Preço Principal", "2 bottles: $79/un ($158) · 3 bottles: $69/un ($207) · 6 bottles: $49/un ($294)"),
        ("Order Bump",      "Não identificado publicamente"),
        ("OTO 1",           "Não identificado publicamente"),
        ("Bônus no Core",   "Guia: '15-Day Mediterranean Cleanse'"),
        ("Garantia",        "180 dias — incondicional (3× a média do mercado)"),
        ("Ticket Médio Est.","$140–$180 (foco em kit 3–6 meses)"),
        ("Comissão Afil.",  "Até 85% · EPC ~$9 · AOV $250+"),
    ],
    copy_data=[
        ("Headline",        "\"The Orange Peel Trick Doctors Are Finally Admitting About This Citrus-Based Fat Loss\""),
        ("Padrão",          "Curiosity + Authority (doctors admitting) — elimina resistência à compra"),
        ("Mecanismo Único", "Thermogenic Citrus Resistance — enquadra o problema como resistência metabólica, não falta de esforço. Elimina culpa da buyer."),
        ("Geo-branding",    "Seville Orange Peel · Spanish Red Apple Vinegar · Andalusian Red Pepper · Himalayan Mountain Ginger · Ceremonial Green Tea — exotismo = percepção premium"),
        ("Prova Social",    "29.432 reviews verificados · 4.7/5"),
        ("Garantia como Copy","180 dias destacado como argumento principal de conversão"),
        ("Nota Copy",       "8.5 / 10"),
    ],
    offer_data=[
        ("Produto",         "Suplemento físico (cápsulas) — produzido em FDA-registered facility, EUA"),
        ("Stack de Bônus",  "1 bônus: '15-Day Mediterranean Cleanse Guide' — ponto fraco (concorrência tem 3–5 bônus)"),
        ("Ancoragem de Preço","Lógica de quantidade: 6 bottles = âncora principal, empurra alto volume → maior LTV"),
        ("Garantia",        "180 dias incondicional — diferencial fortíssimo no mercado"),
        ("Escassez",        "Implícita (produto físico com limitação de estoque por produção)"),
        ("Ponto Forte",     "180 dias de garantia + geo-branding premium dos ingredientes"),
        ("Ponto Fraco",     "Stack de bônus fraco — apenas 1 item"),
        ("Nota Oferta",     "9.0 / 10"),
    ],
    brief_data=[
        ("Oportunidade BR", "🔥🔥🔥 ALTA — Emagrecimento feminino é o maior nicho de suplementos do Brasil. Concorrência: Morosil, Ozempic natural, Moringa stacks."),
        ("Produto Adaptado","Nome sugerido: 'CitrusSlim' ou 'Fórmula Cítrica Feminina'\nFormato: Suplemento físico (manter) · Preço: 1fr R$197 · 3fr R$497 · 6fr R$797"),
        ("Copy BR",         "Headline: 'O Truque da Laranja que Endocrinologistas Brasileiros Finalmente Estão Admitindo'\nTom: Mais emocional — narrativa de luta e superação\nGeo-branding: Substituir nomes estrangeiros por referências nacionais conhecidas"),
        ("Oferta BR",       "Ampliar stack de bônus (ponto fraco do original):\n• Bônus 1: Receitas de culinária detox (valor percebido R$97)\n• Bônus 2: Protocolo de 21 dias de hábitos (R$67)\n• Bônus 3: Grupo VIP no WhatsApp (percepção alta, custo zero)\nManter garantia de 180 dias — diferencial fortíssimo no BR"),
        ("⚠️ Alertas BR",   "• ANVISA: Não fazer claims de cura/tratamento\n• CONAR: Evitar 'emagrecimento X kg em Y dias'\n• Produto físico importado tem barreira fiscal — produzir localmente ou buscar parceiro de manufatura"),
        ("Próximos Passos", "□ Mapear fornecedores de ingredientes no Brasil\n□ Verificar registro ANVISA para compostos\n□ Produzir VSL com doutora/nutróloga brasileira como porta-voz"),
    ],
    links=[
        "Sales Page: https://citrusburn.com/",
        "Programa de Afiliados: https://citrusburn.com/affiliates/",
        "Vendor Nickname ClickBank: citrusburn",
    ]
)

# ══════════════════════════════════════════════════════════════════
# ALVO 2: HIS SECRET OBSESSION
# ══════════════════════════════════════════════════════════════════
product_report(
    story,
    number="3",
    emoji="💕",
    name="His Secret Obsession",
    niche="Relacionamentos / Psicologia Masculina",
    platform="ClickBank · Produto Digital",
    funnel=[
        ("Autor",           "James Bauer — relationship expert"),
        ("Formato VSL",     "VSL criado por marketer com ~$100M em vendas · funil exaustivamente testado"),
        ("Taxa de Conv.",   "7% consistente — uma das mais altas do nicho"),
        ("Front-end",       "$47 (de $197 — desconto 76%) · eBook 200+ pgs + áudio + workbook + 17 módulos"),
        ("OTO / Upsell",    "Uptake de ~60% — conteúdo avançado (não detalhado publicamente)"),
        ("Garantia",        "60 dias · reembolso em 48h sem perguntas"),
        ("Ticket Médio",    "$54.55 (APV oficial ClickBank)"),
        ("EPC / Comissão",  "EPC $0.39 · 75% base → 90% após 1ª venda · $4.8M pagos em comissões"),
    ],
    copy_data=[
        ("Mecanismo Único", "Hero Instinct — gatilho psicológico primitivo. Posiciona a mulher como detentora do poder sem manipulação explícita."),
        ("Enquadramento",   "Elimina culpa: 'não é você, é a psicologia dele' — remove objeção principal"),
        ("Tom",             "Íntimo e confessional — 'como uma amiga revelando um segredo de mulher para mulher'"),
        ("Âncora Emocional","Medo de perder o relacionamento / homem emocionalmente distante"),
        ("Formato",         "Multi-formato (ebook + áudio + módulos) → justifica preço + serve diferentes perfis de aprendizado"),
        ("Prova Social",    "$4.8M pagos em comissões de afiliados (prova indireta de volume massivo de vendas)"),
        ("Nota Copy",       "9.0 / 10"),
    ],
    offer_data=[
        ("Produto Principal","Digital: eBook 200+ pgs + áudio + workbook + cheat sheets de frases"),
        ("Âncora de Preço", "$197 → $47 (76% off) — desconto agressivo que cria urgência imediata"),
        ("Bônus no Core",   "Áudio do livro + workbook + cheat sheets de frases prontas (alto valor percebido)"),
        ("Upsell",          "~60% uptake — oferta extremamente bem calibrada ao público"),
        ("Garantia",        "60 dias · reembolso 48h — reduz fricção de compra"),
        ("Ponto Forte",     "Upsell uptake de 60% + conversão 7% = funil mais eficiente dos 3 alvos"),
        ("Ponto Fraco",     "Produto digital puro — susceptível a pirataria"),
        ("Nota Oferta",     "9.5 / 10"),
    ],
    brief_data=[
        ("Oportunidade BR", "🔥🔥🔥 ALTA — Relacionamento é nicho evergreen no Brasil com público feminino enorme. Concorrência direta com esse nível de funil: inexistente."),
        ("Produto Adaptado","Nome: 'O Instinto Herói' ou 'O Segredo da Obsessão Dele'\nFormato: Digital (ebook + áudio) — manter, custo de produção zero\nPreço: R$97 (de R$497 — 80% off)"),
        ("Copy BR",         "Headline: 'O Psicólogo Americano Revelou o Gatilho Mental que Faz Qualquer Homem Brasileiro Sentir que Não Consegue Viver Sem Você'\nMecanismo: 'Instinto Herói' — traduz perfeitamente para o PT-BR\nTom: Mais quente e próximo que o original — 'entre nós, mulher'"),
        ("Oferta BR",       "• Ampliar módulos para contexto BR (ex: 'o homem brasileiro')\n• Bônus 1: '12 Frases que Reativam o Instinto Herói' (R$47)\n• Bônus 2: Áudio de meditação guiada para casais (R$37)\n• Bônus 3: Masterclass ao vivo mensal (urgência + comunidade)\n• Upsell: Programa avançado 90 dias (R$197) — replicar 60% uptake"),
        ("⚠️ Alertas BR",   "• Linguagem: Evitar qualquer tom que soe manipulação — CONAR pode acionar\n• Verificar necessidade de licença de James Bauer OU criar versão própria original\n• Coletar 50+ depoimentos BR antes do lançamento — prova social local é indispensável"),
        ("Próximos Passos", "□ Negociar licença com James Bauer OU criar produto próprio inspirado\n□ Produzir VSL com especialista em relacionamentos BR\n□ Coletar 50+ depoimentos reais de mulheres brasileiras antes do lançamento"),
    ],
    links=[
        "Sales Page: https://hissecretobsession.com/",
        "Programa de Afiliados: https://hissecretobsession.com/aff/linksA.php",
        "Vendor Nickname ClickBank: hissecret",
        "Hoplink padrão: hop.clickbank.net/?vendor=hissecret&affiliate=SEU_ID",
    ]
)

# ══════════════════════════════════════════════════════════════════
# ALVO 3: BILLIONAIRE BRAIN WAVE
# ══════════════════════════════════════════════════════════════════
product_report(
    story,
    number="4",
    emoji="🧠",
    name="Billionaire Brain Wave",
    niche="Riqueza + Espiritualidade",
    platform="ClickBank · Produto Digital (Áudio)",
    funnel=[
        ("Criador",         "Dr. Thomas Summers — 8-figure ClickBank marketer (~$100M em vendas)"),
        ("Formato VSL",     "VSL otimizado para paid traffic · Scaling ativo em paid media"),
        ("Front-end",       "$39 (de 'milhares') — price anchoring extremo · Áudio digital 7 min/dia"),
        ("Bônus no Core",   "4 bônus: 'Warren Buffett Pyramid' · 'Quick Cash Manifestation' · '7 Lazy Millionaire Habits' · Bônus 4 (n/d)"),
        ("OTO / Upsell",    "Não detalhado publicamente — presumivelmente áudios premium ou programa 30 dias"),
        ("Garantia",        "90 dias money-back — incondicional"),
        ("Ticket Médio",    "$49.94 (APV ClickBank)"),
        ("EPC",             "$0.58 · Hop Conversion: 1.35% — melhor conversão dos 3 alvos"),
    ],
    copy_data=[
        ("Mecanismo Único", "Theta Brain Wave Activation — credibilidade via Columbia University / hippocampus. Ciência como âncora para público cético."),
        ("Posicionamento",  "Espiritualidade com verniz científico — serve agnósticos E crenças new age simultaneamente"),
        ("Problema Central","'Seu cérebro foi programado para sobrevivência, não para riqueza' — elimina culpa pessoal"),
        ("Gatilho Principal","Preguiça socialmente aceita: '7 Lazy Millionaire Habits' no próprio bônus"),
        ("Barreira de Ação","7 minutos por dia — menor fricção possível para adesão"),
        ("Risco Copy",      "Expectativas irreais → churn alto. Principal reclamação: resultados financeiros imediatos não aparecem."),
        ("Nota Copy",       "8.0 / 10"),
    ],
    offer_data=[
        ("Produto Principal","Arquivo de áudio digital (7 min/dia) · Custo de produção mínimo → margem máxima"),
        ("Âncora de Preço", "'De milhares para $39' — ancoragem de status, não de preço original real"),
        ("Stack de Bônus",  "4 bônus digitais inclusos: Warren Buffett Pyramid · Quick Cash Manifestation · 7 Lazy Millionaire Habits · (4º não identificado)"),
        ("Garantia",        "90 dias — acima da média do mercado (padrão ClickBank é 60 dias)"),
        ("Ponto Forte",     "$39 low-ticket = impulso de compra · EPC $0.58 = melhor dos 3"),
        ("Ponto Fraco",     "Expectativas irreais geram reclamações e reembolsos acima da média"),
        ("Nota Oferta",     "7.5 / 10"),
    ],
    brief_data=[
        ("Oportunidade BR", "🔥🔥 MÉDIA-ALTA — Espiritualidade + prosperidade é nicho gigante no BR (lei da atração, frequências, manifestação já validados). Concorrência existe mas sem posicionamento científico."),
        ("Produto Adaptado","Nome: 'Onda Bilionária' ou 'A Frequência dos Milionários'\nFormato: Áudio digital — manter, custo zero\nPreço: R$37 (same feeling do $39 americano)"),
        ("Copy BR",         "Headline: 'Neurocientistas da USP Confirmam: Existe Uma Frequência Cerebral que os Bilionários Ativam Inconscientemente — e Você Pode Ativar Agora'\nAdaptação: Trocar 'Columbia University' por referência BR (USP, UNICAMP)\nTom: Científico mas acessível — 'você não é preguiçoso, seu cérebro foi programado para sobrevivência'"),
        ("Oferta BR",       "• Bônus 1: 'A Pirâmide de Neto' (adaptação Warren Buffett Pyramid para BR)\n• Bônus 2: 'Manifestação Rápida — 7 Técnicas Comprovadas'\n• Bônus 3: 'Os 7 Hábitos dos Milionários Silenciosos BR'\n• Upsell: Programa 30 dias com meditações guiadas (R$97)\n• Garantia: 90 dias — supera o mercado BR"),
        ("⚠️ Alertas BR",   "• Risco de expectativas irreais = reembolso alto → mitigar com sequência de e-mail de onboarding\n• Não prometer ganho financeiro específico (PROCON / CONAR)\n• Verificar se 'Onda Bilionária' ou 'Frequência dos Milionários' já estão registrados como marca no BR"),
        ("Próximos Passos", "□ Produzir áudio PT-BR com locutor profissional\n□ Buscar endosso de neurocientista BR para VSL\n□ Criar sequência de e-mail de onboarding para gerenciar expectativas e reduzir refunds"),
    ],
    links=[
        "Sales Page: https://www.thebillionairebrainwave-us.com/",
        "Programa de Afiliados: https://billionairebrainwave.com/Affiliates/",
        "Contato: affiliates@binauraltechnologies.com",
        "ClickBank Marketplace: https://www.clickbank.com/view-marketplace/ (buscar: Billionaire Brain Wave)",
    ]
)

# ══════════════════════════════════════════════════════════════════
# 5. SÍNTESE FINAL
# ══════════════════════════════════════════════════════════════════
story.append(PageBreak())
story.append(section_header("  5. SÍNTESE FINAL — RANKING E PRÓXIMOS PASSOS"))
story.append(spacer(3))

story.append(Paragraph(
    "Análise consolidada dos 3 alvos. Ranking de prioridade para execução no mercado BR:",
    style_body))
story.append(spacer(3))

ranking_data = [
    [
        Paragraph("<b>Rank</b>", style_label),
        Paragraph("<b>Produto</b>", style_label),
        Paragraph("<b>Por Quê?</b>", style_label),
        Paragraph("<b>Prazo Est.</b>", style_label),
        Paragraph("<b>Nota</b>", style_label),
    ],
    [
        Paragraph("🥇 1º", style_body),
        Paragraph("<b>His Secret Obsession</b>", style_body),
        Paragraph("Digital puro · sem ANVISA · funil maduro · upsell 60%", style_body),
        Paragraph("30 dias", style_body),
        Paragraph("9.5/10", style_body),
    ],
    [
        Paragraph("🥈 2º", style_body),
        Paragraph("<b>CitrusBurn</b>", style_body),
        Paragraph("Maior receita potencial · nicho massivo · requer manufatura", style_body),
        Paragraph("60–90 dias", style_body),
        Paragraph("9.0/10", style_body),
    ],
    [
        Paragraph("🥉 3º", style_body),
        Paragraph("<b>Billionaire Brain Wave</b>", style_body),
        Paragraph("Mais rápido de produzir · gestão de expectativas é o desafio", style_body),
        Paragraph("15–20 dias", style_body),
        Paragraph("7.5/10", style_body),
    ],
]
rank_t = Table(ranking_data, colWidths=[18*mm, 42*mm, 65*mm, 22*mm, 18*mm])
rank_t.setStyle(TableStyle([
    ("BACKGROUND",    (0, 0), (-1, 0), DARK_BG),
    ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
    ("ROWBACKGROUNDS",(0, 1), (-1, -1), [HexColor("#FCE4EC"), HexColor("#FFF3E0"), HexColor("#E8F5E9")]),
    ("GRID",          (0, 0), (-1, -1), 0.3, GREY_MID),
    ("TOPPADDING",    (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
]))
story.append(rank_t)
story.append(spacer(5))

story.append(Paragraph("<b>Ações Imediatas Recomendadas:</b>", style_label))
story.append(spacer(2))
acoes = [
    "□  Acessar ClickBank Marketplace e analisar os 3 produtos diretamente",
    "□  Comprar os 3 produtos como cliente para mapear funil completo de pós-compra",
    "□  Iniciar produção da versão BR de His Secret Obsession (mais rápido ao mercado)",
    "□  Consultar advogado de PI sobre licenciamento vs. produto próprio inspirado",
    "□  Para CitrusBurn: contatar laboratórios BR para viabilidade de manufatura",
    "□  Para Billionaire Brain Wave: contratar locutor e neurocientista BR para VSL",
]
for a in acoes:
    story.append(Paragraph(a, S("acao",
        fontName="Helvetica", fontSize=9, textColor=DARK_BG,
        leading=14, spaceAfter=3, leftIndent=5)))

# ══════════════════════════════════════════════════════════════════
# 6. LINKS E RECURSOS
# ══════════════════════════════════════════════════════════════════
story.append(PageBreak())
story.append(section_header("  6. LINKS E RECURSOS"))
story.append(spacer(3))

links_data = [
    [Paragraph("<b>Recurso</b>", style_label), Paragraph("<b>URL</b>", style_label)],
    [Paragraph("CitrusBurn — Sales Page", style_body), Paragraph("https://citrusburn.com/", style_body)],
    [Paragraph("CitrusBurn — Afiliados", style_body), Paragraph("https://citrusburn.com/affiliates/", style_body)],
    [Paragraph("His Secret Obsession — Sales Page", style_body), Paragraph("https://hissecretobsession.com/", style_body)],
    [Paragraph("His Secret Obsession — Afiliados", style_body), Paragraph("https://hissecretobsession.com/aff/linksA.php", style_body)],
    [Paragraph("Billionaire Brain Wave — Sales Page", style_body), Paragraph("https://www.thebillionairebrainwave-us.com/", style_body)],
    [Paragraph("Billionaire Brain Wave — Afiliados", style_body), Paragraph("https://billionairebrainwave.com/Affiliates/", style_body)],
    [Paragraph("ClickBank Marketplace", style_body), Paragraph("https://www.clickbank.com/view-marketplace/", style_body)],
    [Paragraph("CBEngine — Top Gravity", style_body), Paragraph("https://cbengine.com/clickbank-top-gravity.html", style_body)],
    [Paragraph("JVZoo Featured Products", style_body), Paragraph("https://www.jvzoo.com/products/featured", style_body)],
]
links_t = Table(links_data, colWidths=[65*mm, 105*mm])
links_t.setStyle(TableStyle([
    ("BACKGROUND",    (0, 0), (-1, 0), DARK_BG),
    ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
    ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, SECTION_BG] * 10),
    ("GRID",          (0, 0), (-1, -1), 0.3, GREY_MID),
    ("TOPPADDING",    (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
]))
story.append(links_t)
story.append(spacer(6))

# Rodapé
story.append(hr(GOLD, 1))
story.append(Paragraph(
    "Gerado por Espião 007 Squad · JARVIS v2.0 · MEGABRAIN · 19/03/2026<br/>"
    "<i>\"A missão não termina até o brief estar na mão.\" — Bond</i>",
    S("footer", fontName="Helvetica-Oblique", fontSize=8,
      textColor=GREY_MID, alignment=TA_CENTER, spaceAfter=2)))

# ── Build ──────────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF gerado: {os.path.abspath(OUTPUT)}")
