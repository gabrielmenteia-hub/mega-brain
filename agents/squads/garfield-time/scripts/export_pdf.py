#!/usr/bin/env python3
"""Exporta o squad garfield-time para PDF usando fpdf2."""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
from fpdf import FPDF

BASE    = Path('c:/Users/Gabriel/MEGABRAIN/agents/squads/garfield-time')
OUTPUT  = Path('c:/Users/Gabriel/MEGABRAIN/docs/GARFIELD-TIME-SQUAD.pdf')
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

# ─── helpers ────────────────────────────────────────────────────────────────

def clean(text: str) -> str:
    """Normaliza caracteres para latin-1 (fontes core do FPDF)."""
    rep = {
        '\u2022': '-', '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '--',
        '\u00e9': 'e', '\u00e3': 'a', '\u00e7': 'c', '\u00f5': 'o', '\u00ea': 'e',
        '\u00e2': 'a', '\u00f3': 'o', '\u00fa': 'u', '\u00ed': 'i', '\u00e0': 'a',
        '\u00e1': 'a', '\u00fc': 'u', '\u00f4': 'o', '\u00e4': 'a', '\u00f1': 'n',
        '\u00ef': 'i', '\u00ee': 'i', '\u00e8': 'e', '\u00eb': 'e', '\u00f9': 'u',
        '\u00fb': 'u', '\u00ec': 'i',
        '\u00c9': 'E', '\u00c3': 'A', '\u00c7': 'C', '\u00d5': 'O', '\u00ca': 'E',
        '\u00c2': 'A', '\u00d3': 'O', '\u00da': 'U', '\u00cd': 'I', '\u00c0': 'A',
        '\u00c1': 'A', '\u00dc': 'U', '\u00d4': 'O', '\u00d6': 'O', '\u00c4': 'A',
        '\u00d1': 'N','\u00ba': 'o', '\u00aa': 'a',
        '\u2026': '...', '\u00b7': '-', '\u00ae': '(R)', '\u2122': '(TM)',
        '\u00bf': '?', '\u00a1': '!',
    }
    for k, v in rep.items():
        text = text.replace(k, v)
    return text.encode('latin-1', errors='replace').decode('latin-1')

def extract_yaml_field(text: str, field: str) -> str:
    """Extrai valor simples de campo YAML."""
    m = re.search(rf'^\s*{field}:\s*["\']?(.+?)["\']?\s*$', text, re.MULTILINE)
    return m.group(1).strip() if m else ''

def extract_list_field(text: str, field: str, max_items: int = 8) -> list[str]:
    """Extrai lista YAML após um campo."""
    pattern = rf'{field}:\s*\n((?:\s+-\s+.+\n?)+)'
    m = re.search(pattern, text)
    if not m:
        return []
    items = re.findall(r'-\s+"?([^"\n]+)"?', m.group(1))
    return [i.strip() for i in items[:max_items]]

def extract_block(text: str, start_marker: str, end_markers: list[str]) -> str:
    """Extrai bloco de texto entre marcadores."""
    idx = text.find(start_marker)
    if idx == -1:
        return ''
    idx += len(start_marker)
    end = len(text)
    for em in end_markers:
        pos = text.find(em, idx)
        if pos != -1 and pos < end:
            end = pos
    return text[idx:end].strip()

def parse_agent(path: Path) -> dict:
    """Parseia agente garfield-time e retorna estrutura."""
    raw = path.read_text(encoding='utf-8')

    agent = {
        'id':           extract_yaml_field(raw, 'id'),
        'name':         extract_yaml_field(raw, 'name'),
        'title':        extract_yaml_field(raw, 'title'),
        'icon':         extract_yaml_field(raw, 'icon').replace('"', '').replace("'", ''),
        'tier':         extract_yaml_field(raw, 'tier'),
        'dna_source':   extract_yaml_field(raw, 'dna_source'),
        'role':         extract_yaml_field(raw, 'role'),
        'catchphrase':  extract_yaml_field(raw, 'catchphrase').strip('"\''),
        'vocab_use':    extract_list_field(raw, 'always_use', 8),
        'principles':   [],
        'examples':     [],
        'raw':          raw,
    }

    # principles: linhas com `name:` dentro de core_principles
    principles_block = extract_block(raw, 'core_principles:', ['objection_algorithms:', 'voice_dna:', 'thinking_dna:', 'output_examples:'])
    agent['principles'] = re.findall(r'name:\s+"?([^"\n]+)"?', principles_block)[:5]

    # exemplos de output: primeiros inputs
    examples_raw = re.findall(r'input:\s+"([^"]+)"', raw)
    agent['examples'] = [e[:120] for e in examples_raw[:2]]

    # identity: primeiro parágrafo do bloco identity
    id_match = re.search(r'identity:\s*\|\s*\n((?:\s{4}.+\n?)+)', raw)
    if id_match:
        lines = [l.strip() for l in id_match.group(1).strip().split('\n') if l.strip()]
        agent['identity'] = ' '.join(lines[:3])
    else:
        agent['identity'] = agent['role']

    return agent

# ─── AGENTS METADATA ────────────────────────────────────────────────────────

AGENTS = [
    {'file': 'garfield-chief.md',       'tier_label': 'ORCHESTRATOR', 'color': (15, 15, 60)},
    {'file': 'product-diagnostician.md','tier_label': 'TIER 0',       'color': (20, 80, 120)},
    {'file': 'offer-architect.md',      'tier_label': 'TIER 1',       'color': (40, 100, 40)},
    {'file': 'launch-strategist.md',    'tier_label': 'TIER 1',       'color': (40, 100, 40)},
    {'file': 'ask-methodologist.md',    'tier_label': 'TIER 2',       'color': (100, 60, 140)},
    {'file': 'market-seducer.md',       'tier_label': 'TIER 2',       'color': (100, 60, 140)},
    {'file': 'copy-decoder.md',         'tier_label': 'TIER 3',       'color': (140, 80, 20)},
    {'file': 'br-market-strategist.md', 'tier_label': 'TIER 3',       'color': (140, 80, 20)},
]

# ─── PDF CLASS ──────────────────────────────────────────────────────────────

class GarfieldPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=22)
        self.set_margins(20, 20, 20)
        self._current_agent = ''

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 6, clean('GARFIELD TIME | Squad de Info Produtos Milionarios'), align='L')
        self.ln(2)
        self.set_draw_color(220, 220, 220)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(4)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-14)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 8, f'Pagina {self.page_no()}', align='C')

    # ── Cover ──────────────────────────────────────────────────────────────
    def cover_page(self):
        self.add_page()

        # Dark header
        self.set_fill_color(10, 10, 30)
        self.rect(0, 0, 210, 90, 'F')

        self.set_y(18)
        self.set_font('Helvetica', 'B', 36)
        self.set_text_color(255, 220, 50)
        self.cell(0, 16, 'GARFIELD TIME', align='C')
        self.ln(18)
        self.set_font('Helvetica', '', 14)
        self.set_text_color(180, 200, 255)
        self.cell(0, 7, clean('Squad de Modelagem e Engenharia Reversa'), align='C')
        self.ln(8)
        self.set_font('Helvetica', '', 11)
        self.set_text_color(140, 160, 210)
        self.cell(0, 7, clean('de Info Produtos Milionarios'), align='C')
        self.ln(20)

        # Stat boxes
        self.set_y(105)
        self.set_text_color(0, 0, 0)
        stats = [('8', 'Agentes'), ('5', 'Tasks'), ('5', 'Quality Gates')]
        box_w, gap = 48, 8
        start_x = (210 - (box_w * 3 + gap * 2)) / 2
        for i, (val, label) in enumerate(stats):
            x = start_x + i * (box_w + gap)
            self.set_fill_color(240, 245, 255)
            self.set_draw_color(80, 100, 200)
            self.set_line_width(0.5)
            self.rect(x, self.get_y(), box_w, 30, 'FD')
            self.set_xy(x, self.get_y() + 5)
            self.set_font('Helvetica', 'B', 24)
            self.set_text_color(20, 50, 160)
            self.cell(box_w, 12, val, align='C')
            self.set_xy(x, self.get_y() + 12)
            self.set_font('Helvetica', '', 9)
            self.set_text_color(80, 80, 80)
            self.cell(box_w, 8, label, align='C')
        self.ln(45)

        # Squad summary
        self.section_title(clean('O Squad'), (10, 10, 30))
        summary_lines = [
            clean('Especializado em dissecar produtos campeos, desmontar estruturas de oferta e'),
            clean('copy, mapear funis de alta conversao e criar produtos modelados baseados nos'),
            clean('padroes que realmente funcionam no mercado de info produtos.'),
        ]
        self.set_font('Helvetica', '', 11)
        self.set_text_color(40, 40, 40)
        for line in summary_lines:
            self.cell(0, 7, line, align='L')
            self.ln(7)
        self.ln(4)

        # Agent table
        self.section_title(clean('Agentes do Squad'), (10, 10, 30))
        tier_colors = {
            'ORCHESTRATOR': (10, 10, 40),
            'TIER 0':       (20, 80, 120),
            'TIER 1':       (40, 100, 40),
            'TIER 2':       (100, 60, 140),
            'TIER 3':       (140, 80, 20),
        }
        rows = [
            ('garfield-chief',       'ORCHESTRATOR', '--',           'Orquestracao, triagem, sintese'),
            ('product-diagnostician','TIER 0',       '--',           'Diagnostico e classificacao de produtos'),
            ('offer-architect',      'TIER 1',       'Alex Hormozi', 'Value Equation, Grand Slam Offer'),
            ('launch-strategist',    'TIER 1',       'Jeff Walker',  'Product Launch Formula, funis'),
            ('ask-methodologist',    'TIER 2',       'Ryan Levesque','Ask Method, survey funnels'),
            ('market-seducer',       'TIER 2',       'Frank Kern',   'Core Influence, story selling'),
            ('copy-decoder',         'TIER 3',       'Classicos',    'Engenharia reversa de copy'),
            ('br-market-strategist', 'TIER 3',       'Icaro / Naro', 'Posicionamento e autoridade BR'),
        ]
        col_w = [52, 24, 34, 60]
        headers = ['Agente', 'Tier', 'DNA', 'Especialidade']

        # Header row
        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(30, 30, 60)
        self.set_text_color(255, 255, 255)
        for w, h in zip(col_w, headers):
            self.cell(w, 7, h, border=1, fill=True, align='C')
        self.ln()

        self.set_font('Helvetica', '', 8)
        for row in rows:
            tier = row[1]
            r, g, b = tier_colors.get(tier, (60, 60, 60))
            # tier badge cell
            self.set_fill_color(230, 240, 255)
            self.set_text_color(30, 30, 30)
            self.cell(col_w[0], 6, row[0], border=1, fill=True)
            self.set_fill_color(r, g, b)
            self.set_text_color(255, 255, 255)
            self.cell(col_w[1], 6, row[1], border=1, fill=True, align='C')
            self.set_fill_color(248, 248, 248)
            self.set_text_color(60, 60, 60)
            self.cell(col_w[2], 6, clean(row[2]), border=1, fill=True, align='C')
            self.cell(col_w[3], 6, clean(row[3]), border=1, fill=True)
            self.ln()

    # ── Helpers ────────────────────────────────────────────────────────────
    def section_title(self, text: str, color=(30, 30, 80)):
        self.set_font('Helvetica', 'B', 13)
        r, g, b = color
        self.set_text_color(r, g, b)
        self.cell(0, 9, clean(text), align='L')
        self.ln(4)
        self.set_draw_color(r, g, b)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(5)
        self.set_text_color(0, 0, 0)

    def subsection(self, text: str):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(60, 60, 100)
        self.cell(0, 7, clean(text), align='L')
        self.ln(5)
        self.set_text_color(30, 30, 30)

    def body_text(self, text: str, size=9):
        self.set_font('Helvetica', '', size)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, clean(text))
        self.ln(2)

    def bullet_list(self, items: list[str], indent=4):
        self.set_font('Helvetica', '', 9)
        self.set_text_color(40, 40, 40)
        for item in items:
            self.set_x(20 + indent)
            self.multi_cell(170 - indent, 5.5, clean('- ' + item))
        self.ln(2)

    def tag_row(self, items: list[str], bg=(230, 240, 255), fg=(20, 50, 160)):
        """Renderiza lista de tags inline."""
        self.set_font('Helvetica', 'B', 8)
        r, g, b = bg
        fr, fg2, fb = fg
        self.set_fill_color(r, g, b)
        self.set_text_color(fr, fg2, fb)
        for item in items:
            w = self.get_string_width(clean(item)) + 6
            if self.get_x() + w > 185:
                self.ln(7)
                self.set_x(20)
            self.cell(w, 6, clean(item), border=1, fill=True)
            self.cell(2)
        self.ln(10)
        self.set_text_color(0, 0, 0)

    # ── Agent page ─────────────────────────────────────────────────────────
    def agent_page(self, agent: dict, tier_label: str, color: tuple):
        self.add_page()
        r, g, b = color

        # Agent header banner
        self.set_fill_color(r, g, b)
        self.rect(0, 0, 210, 42, 'F')

        # Tier badge
        self.set_xy(20, 8)
        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(255, 220, 50)
        self.set_text_color(20, 20, 20)
        badge = f' {tier_label} '
        self.cell(self.get_string_width(badge) + 2, 6, badge, fill=True)
        self.ln(8)

        # Agent name + title
        self.set_x(20)
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, clean(agent['name']), align='L')
        self.ln(10)
        self.set_x(20)
        self.set_font('Helvetica', '', 11)
        self.set_text_color(200, 220, 255)
        self.cell(0, 7, clean(agent['title']), align='L')
        self.ln(14)

        # DNA source
        if agent.get('dna_source'):
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 6, clean('DNA Source: ' + agent['dna_source']), align='L')
            self.ln(7)

        # Role / Identity
        self.subsection('Identidade')
        self.body_text(agent.get('identity', agent['role']))

        # Catchphrase
        if agent.get('catchphrase'):
            self.set_font('Helvetica', 'I', 10)
            self.set_fill_color(245, 245, 255)
            self.set_draw_color(r, g, b)
            self.set_text_color(r, g, b)
            self.set_line_width(0.8)
            msg = clean('"' + agent['catchphrase'] + '"')
            self.multi_cell(0, 7, msg, border='L', fill=True)
            self.set_line_width(0.2)
            self.ln(4)

        # Core vocabulary
        if agent.get('vocab_use'):
            self.subsection('Vocabulario Core')
            self.tag_row(agent['vocab_use'], bg=(230, 240, 255), fg=(r, g, b))

        # Principles
        if agent.get('principles'):
            self.subsection('Principios Operacionais')
            self.bullet_list(agent['principles'])

        # Use cases / examples
        if agent.get('examples'):
            self.subsection('Casos de Uso')
            for ex in agent['examples']:
                self.set_font('Helvetica', 'I', 9)
                self.set_fill_color(248, 248, 255)
                self.set_text_color(60, 60, 60)
                self.multi_cell(0, 5.5, clean('> ' + ex), fill=True)
                self.ln(3)

    # ── Tasks page ─────────────────────────────────────────────────────────
    def tasks_page(self):
        self.add_page()
        self.section_title('Tasks do Squad', (10, 10, 60))

        tasks = [
            ('GT-TP-001', 'benchmark-product',
             'Analise completa de produto campeo',
             'diagnostician + offer-architect',
             ['Tipo e mecanismo classificados', 'Value Equation score', 'Padroes reproduziveis']),
            ('GT-TP-002', 'reverse-offer',
             'Engenharia reversa de oferta e copy',
             'offer-architect + copy-decoder + market-seducer',
             ['Value stack desmontado', 'Formula de copy identificada', 'Domino mapeado']),
            ('GT-TP-003', 'model-funnel',
             'Modelagem de funil de alta conversao',
             'launch-strategist + ask-methodologist',
             ['Buckets de avatar definidos', 'Sequencia PLC estruturada', 'Close cart planejado']),
            ('GT-TP-004', 'create-product',
             'Criar produto modelado completo',
             'garfield-chief (orquestra todos)',
             ['Grand Slam Offer completa', 'Blueprint de produto entregue', 'Funil completo definido']),
            ('GT-TP-005', 'reverse-copy',
             'Engenharia reversa de copy especifico',
             'copy-decoder',
             ['Formula identificada', 'Score de specificity', 'Blueprint reproduzivel']),
        ]

        for task_id, name, desc, executor, criteria in tasks:
            self.set_fill_color(245, 247, 255)
            self.set_draw_color(80, 100, 200)
            self.set_line_width(0.3)
            start_y = self.get_y()
            self.rect(20, start_y, 170, 42, 'FD')

            self.set_xy(24, start_y + 3)
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(20, 40, 140)
            self.cell(30, 6, clean(task_id))
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(20, 20, 60)
            self.cell(0, 6, clean(name))
            self.ln(7)

            self.set_x(24)
            self.set_font('Helvetica', '', 9)
            self.set_text_color(50, 50, 50)
            self.cell(0, 5, clean(desc))
            self.ln(5)

            self.set_x(24)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(80, 80, 120)
            self.cell(0, 5, clean('Executor: ' + executor))
            self.ln(6)

            self.set_x(24)
            self.set_font('Helvetica', '', 8)
            self.set_text_color(40, 80, 40)
            self.cell(0, 5, clean('Entrega: ' + ' | '.join(criteria[:2])))
            self.ln(10)

    # ── KB page ────────────────────────────────────────────────────────────
    def kb_page(self):
        self.add_page()
        self.section_title(clean('Knowledge Base — Frameworks Core'), (10, 10, 60))

        frameworks = [
            ('Value Equation (Hormozi)',
             'Valor = (Dream Outcome x Perceived Likelihood) / (Time Delay x Effort)',
             'Para aumentar valor: amplificar outcome + aumentar credibilidade + reduzir tempo + reduzir esforco'),
            ('Grand Slam Offer (Hormozi)',
             'Uma oferta tao boa que o prospect se sente idiota em dizer nao.',
             'Promessa com numero+prazo+mecanismo | Value stack 5+ itens | Garantia | Preco = 10% do valor'),
            ('Product Launch Formula (Jeff Walker)',
             'Pre Pre-Launch > PLC1 (Autoridade) > PLC2 (Comunidade) > PLC3 (Antecipacao) > Open Cart > Close Cart',
             'Pre-launch aumenta conversao em 3-10x vs. direto ao carrinho'),
            ('Ask Method (Ryan Levesque)',
             'Perguntar antes de vender. SMIQ > Buckets > Mensagem por segmento > Conversao personalizada',
             'Survey funnel tem conversao 2-5x maior que landing page tradicional'),
            ('Core Influence / Story Selling (Frank Kern)',
             'Result in Advance + O Domino + Story Selling + Open Loops + Future Pacing',
             'O Domino: o argumento que torna todas as objacoes irrelevantes'),
            ('Copy Frameworks (Classicos)',
             'AIDA | PAS (Problema-Agitacao-Solucao) | BAB (Antes-Depois-Ponte)',
             'Specificity sells. Vagueness kills. Numeros reais > adjetivos genericos'),
        ]

        for name, formula, note in frameworks:
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(20, 40, 130)
            self.cell(0, 7, clean(name))
            self.ln(5)

            self.set_fill_color(235, 240, 255)
            self.set_font('Courier', '', 8)
            self.set_text_color(30, 30, 80)
            self.multi_cell(0, 5, clean(formula), fill=True)
            self.ln(2)

            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(70, 70, 70)
            self.multi_cell(0, 5, clean(note))
            self.ln(5)

        # Conversion benchmarks
        self.section_title(clean('Benchmarks de Conversao'), (10, 10, 60))
        rows = [
            ('Lead magnet opt-in',         '< 20%', '30-50%', '> 60%'),
            ('Email open rate',            '< 15%', '20-35%', '> 40%'),
            ('Cart open (lista quente)',    '< 5%',  '10-20%', '> 25%'),
            ('Cart open (lista fria)',      '< 1%',  '2-5%',   '> 8%'),
            ('Webinar live attendance',    '< 20%', '30-40%', '> 50%'),
        ]
        headers = ['Metrica', 'Fraco', 'Bom', 'Excelente']
        col_w = [80, 30, 30, 30]
        colors = [(200, 80, 80), (200, 160, 40), (60, 150, 60)]

        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(30, 30, 60)
        self.set_text_color(255, 255, 255)
        for w, h in zip(col_w, headers):
            self.cell(w, 6, clean(h), border=1, fill=True, align='C')
        self.ln()

        for row in rows:
            self.set_fill_color(248, 248, 255)
            self.set_text_color(30, 30, 30)
            self.set_font('Helvetica', '', 8)
            self.cell(col_w[0], 5.5, clean(row[0]), border=1, fill=True)
            for i, val in enumerate(row[1:]):
                r, g, b = colors[i]
                self.set_fill_color(min(r + 80, 255), min(g + 80, 255), min(b + 80, 255))
                self.set_text_color(max(r - 20, 0), max(g - 20, 0), max(b - 20, 0))
                self.cell(col_w[i + 1], 5.5, val, border=1, fill=True, align='C')
            self.ln()


# ─── MAIN ───────────────────────────────────────────────────────────────────

def main():
    pdf = GarfieldPDF()
    pdf.set_title('Garfield Time — Squad de Info Produtos Milionarios')
    pdf.set_author('MEGABRAIN')

    # Cover
    pdf.cover_page()

    # Agent pages
    for meta in AGENTS:
        path = BASE / 'agents' / meta['file']
        if not path.exists():
            print(f'[SKIP] {meta["file"]} nao encontrado')
            continue
        agent = parse_agent(path)
        pdf.agent_page(agent, meta['tier_label'], meta['color'])
        print(f'[OK] {agent["name"]}')

    # Tasks
    pdf.tasks_page()
    print('[OK] Tasks page')

    # Knowledge Base
    pdf.kb_page()
    print('[OK] Knowledge Base page')

    pdf.output(str(OUTPUT))
    print(f'\n[DONE] PDF gerado: {OUTPUT}')
    print(f'       Paginas: {pdf.page}')


if __name__ == '__main__':
    main()
