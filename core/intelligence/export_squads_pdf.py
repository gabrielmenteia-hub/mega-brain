#!/usr/bin/env python3
"""Exporta todos os squads e agentes para PDF usando fpdf2."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
from fpdf import FPDF

BASE = Path('c:/Users/Gabriel/MEGABRAIN/agents/squads')
OUTPUT = Path('c:/Users/Gabriel/MEGABRAIN/docs/SQUADS-CATALOG.pdf')
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

SQUAD_ORDER = [
    'advisory-board', 'brand-squad', 'c-level-squad', 'copy-squad',
    'cybersecurity-squad', 'data-squad', 'design-squad', 'hormozi-squad',
    'movement-squad', 'storytelling-squad', 'traffic-masters',
]

SQUAD_NAMES = {
    'advisory-board': 'Advisory Board',
    'brand-squad': 'Brand Squad',
    'c-level-squad': 'C-Level Squad',
    'copy-squad': 'Copy Squad',
    'cybersecurity-squad': 'Cybersecurity Squad',
    'data-squad': 'Data Squad',
    'design-squad': 'Design Squad',
    'hormozi-squad': 'Hormozi Squad',
    'movement-squad': 'Movement Squad',
    'storytelling-squad': 'Storytelling Squad',
    'traffic-masters': 'Traffic Masters',
}

def clean(text):
    """Replace non-latin-1 chars for fpdf core fonts."""
    replacements = {
        '\u2022': '-', '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '--', '\u00e9': 'e', '\u00e3': 'a', '\u00e7': 'c',
        '\u00f5': 'o', '\u00ea': 'e', '\u00e2': 'a', '\u00f3': 'o', '\u00fa': 'u',
        '\u00ed': 'i', '\u00e0': 'a', '\u00e1': 'a', '\u00fc': 'u', '\u00f4': 'o',
        '\u00f6': 'o', '\u00e4': 'a', '\u00f1': 'n', '\u00ef': 'i', '\u00ee': 'i',
        '\u00e8': 'e', '\u00eb': 'e', '\u00f9': 'u', '\u00fb': 'u', '\u00ec': 'i',
        '\u00e6': 'ae', '\u00f8': 'o', '\u00e5': 'a',
        '\u00c9': 'E', '\u00c3': 'A', '\u00c7': 'C', '\u00d5': 'O', '\u00ca': 'E',
        '\u00c2': 'A', '\u00d3': 'O', '\u00da': 'U', '\u00cd': 'I', '\u00c0': 'A',
        '\u00c1': 'A', '\u00dc': 'U', '\u00d4': 'O', '\u00d6': 'O', '\u00c4': 'A',
        '\u00d1': 'N',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('latin-1', errors='replace').decode('latin-1')

def parse_agent_md(path):
    """Parse AGENT.md and return dict with fields."""
    text = path.read_text(encoding='utf-8')
    lines = text.split('\n')
    data = {'name': '', 'command': '', 'bio': '', 'specialties': [], 'when_to_use': '', 'catchphrase': ''}

    section = None
    buf = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# AGENT:'):
            data['name'] = stripped.replace('# AGENT:', '').strip()
        elif stripped.startswith('> **Squad:**'):
            # Extract command
            if '`' in stripped:
                cmd = stripped.split('`')[1] if '`' in stripped else ''
                data['command'] = cmd
        elif stripped == '## Biografia':
            section = 'bio'
            buf = []
        elif stripped == '## Especialidades':
            if section == 'bio':
                data['bio'] = ' '.join(buf).strip()
            section = 'specialties'
            buf = []
        elif stripped == '## Quando Usar':
            if section == 'specialties':
                data['specialties'] = [b.lstrip('- ').strip() for b in buf if b.strip().startswith('-')]
            section = 'when'
            buf = []
        elif stripped == '## Catchphrase':
            if section == 'when':
                data['when_to_use'] = ' '.join(buf).strip()
            section = 'catchphrase'
            buf = []
        elif stripped.startswith('---'):
            if section == 'catchphrase':
                # Extract catchphrase from > "..." line
                for b in buf:
                    if b.strip().startswith('>'):
                        data['catchphrase'] = b.strip().lstrip('> ').strip('"')
            section = None
        elif section and stripped:
            buf.append(stripped)

    return data


class SquadPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 20, 20)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, 'MEGABRAIN - Catalogo de Squads Xquads', align='L')
        self.ln(2)
        self.set_draw_color(220, 220, 220)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(4)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Pagina {self.page_no()}', align='C')

    def cover_page(self, total_squads, total_agents):
        self.add_page()
        # Dark header block
        self.set_fill_color(15, 15, 30)
        self.rect(0, 0, 210, 80, 'F')

        self.set_y(20)
        self.set_font('Helvetica', 'B', 32)
        self.set_text_color(255, 255, 255)
        self.cell(0, 14, 'MEGABRAIN', align='C')
        self.ln(16)
        self.set_font('Helvetica', '', 16)
        self.set_text_color(180, 200, 255)
        self.cell(0, 8, 'Catalogo de Squads Xquads', align='C')
        self.ln(20)

        # Stats block
        self.set_y(95)
        self.set_text_color(0, 0, 0)

        # 3 stat boxes
        stats = [
            (str(total_squads), 'Squads'),
            (str(total_agents), 'Agentes'),
            ('19', 'Workflows'),
        ]
        box_w = 50
        gap = 10
        start_x = (210 - (box_w * 3 + gap * 2)) / 2

        for i, (val, label) in enumerate(stats):
            x = start_x + i * (box_w + gap)
            self.set_fill_color(240, 245, 255)
            self.set_draw_color(100, 120, 200)
            self.set_line_width(0.5)
            self.rect(x, self.get_y(), box_w, 28, 'FD')
            self.set_xy(x, self.get_y() + 4)
            self.set_font('Helvetica', 'B', 22)
            self.set_text_color(30, 60, 160)
            self.cell(box_w, 12, val, align='C')
            self.set_xy(x, self.get_y() + 12)
            self.set_font('Helvetica', '', 9)
            self.set_text_color(80, 80, 80)
            self.cell(box_w, 8, label, align='C')

        self.ln(40)

        # Squad list
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, 'Squads incluidos:', align='C')
        self.ln(12)

        squads_display = [
            ('Advisory Board', 11, 'Ray Dalio, Charlie Munger, Naval, Peter Thiel...'),
            ('Brand Squad', 15, 'Al Ries, David Aaker, Marty Neumeier, Donald Miller...'),
            ('C-Level Squad', 6, 'CEO, COO, CMO, CTO, CIO, CAIO'),
            ('Copy Squad', 23, 'Dan Kennedy, David Ogilvy, Gary Halbert, Eugene Schwartz...'),
            ('Cybersecurity Squad', 15, 'Red team, blue team, AppSec, incident response'),
            ('Data Squad', 7, 'Kaushik, Peter Fader, Sean Ellis, Nick Mehta...'),
            ('Design Squad', 8, 'Brad Frost, UX Designer, UI Engineer, Visual Generator...'),
            ('Hormozi Squad', 16, 'Offers, leads, pricing, copy, hooks, launch, scale...'),
            ('Movement Squad', 7, 'Identidade, manifestos, fenomenologia, impacto...'),
            ('Storytelling Squad', 12, 'Campbell, Snyder, Duarte, Klaff, Harmon...'),
            ('Traffic Masters', 16, 'Facebook, Google, YouTube Ads, scaling, tracking...'),
        ]

        for name, count, desc in [(clean(n), c, clean(d)) for n,c,d in squads_display]:
            self.set_fill_color(248, 248, 252)
            self.set_draw_color(220, 220, 230)
            self.set_line_width(0.3)
            y = self.get_y()
            self.rect(20, y, 170, 14, 'FD')

            self.set_xy(24, y + 2)
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(20, 40, 120)
            self.cell(60, 5, name)

            self.set_font('Helvetica', '', 8)
            self.set_text_color(100, 100, 100)
            self.cell(20, 5, f'{count} agentes')

            self.set_font('Helvetica', 'I', 7.5)
            self.set_text_color(120, 120, 120)
            self.cell(0, 5, desc)

            self.ln(14)

        self.ln(8)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 6, 'Gerado por MEGABRAIN | 2026-03-12 | Xquads Catalog Import', align='C')
        # squads_display uses clean inside squad_header

    def squad_header(self, squad_name, agents_count, description):
        self.add_page()
        # Header bar
        self.set_fill_color(15, 15, 30)
        self.rect(0, 0, 210, 35, 'F')

        self.set_y(8)
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, squad_name, align='C')
        self.ln(11)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(180, 200, 255)
        self.cell(0, 6, f'{agents_count} Agentes  |  Xquads', align='C')

        self.set_y(42)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(60, 60, 80)
        self.multi_cell(0, 5, description, align='C')
        self.ln(4)
        self.set_draw_color(100, 120, 200)
        self.set_line_width(0.8)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(6)
        self.set_text_color(0, 0, 0)

    def agent_card(self, agent):
        name = clean(agent.get('name', ''))
        command = clean(agent.get('command', ''))
        bio = clean(agent.get('bio', ''))
        specialties = [clean(s) for s in agent.get('specialties', [])]
        when_to_use = clean(agent.get('when_to_use', ''))
        catchphrase = clean(agent.get('catchphrase', ''))

        # Check if we need a new page (need at least 55mm)
        if self.get_y() > 240:
            self.add_page()

        y_start = self.get_y()

        # Card border
        self.set_draw_color(180, 190, 220)
        self.set_line_width(0.3)

        # Name header
        self.set_fill_color(230, 235, 255)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(15, 30, 100)
        self.cell(0, 8, name, fill=True, ln=1)

        # Command tag
        self.set_font('Helvetica', 'I', 7.5)
        self.set_text_color(80, 100, 160)
        self.cell(0, 5, command, ln=1)
        self.ln(1)

        # Bio
        if bio:
            self.set_font('Helvetica', '', 8.5)
            self.set_text_color(40, 40, 40)
            self.multi_cell(0, 4.5, bio[:280] + ('...' if len(bio) > 280 else ''))
            self.ln(1)

        # Specialties
        if specialties:
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(30, 60, 130)
            self.cell(0, 5, 'Especialidades:', ln=1)
            self.set_font('Helvetica', '', 8)
            self.set_text_color(50, 50, 50)
            spec_text = '  |  '.join(specialties[:5])
            self.multi_cell(0, 4, spec_text)
            self.ln(1)

        # When to use
        if when_to_use:
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(30, 100, 60)
            self.cell(0, 5, 'Quando usar:', ln=1)
            self.set_font('Helvetica', '', 8)
            self.set_text_color(50, 70, 50)
            self.multi_cell(0, 4, when_to_use[:200] + ('...' if len(when_to_use) > 200 else ''))
            self.ln(1)

        # Catchphrase
        if catchphrase:
            self.set_fill_color(245, 245, 255)
            self.set_font('Helvetica', 'I', 8.5)
            self.set_text_color(60, 60, 120)
            self.cell(0, 6, f'"{catchphrase}"', fill=True, ln=1)

        # Bottom separator
        self.set_draw_color(200, 210, 240)
        self.line(20, self.get_y() + 2, 190, self.get_y() + 2)
        self.ln(6)


def build_pdf():
    pdf = SquadPDF()
    pdf.set_title('MEGABRAIN - Catalogo de Squads Xquads')
    pdf.set_author('MEGABRAIN / JARVIS')

    # Collect all agents count
    total_agents = 0
    for squad_id in SQUAD_ORDER:
        squad_dir = BASE / squad_id
        total_agents += len(list(squad_dir.glob('*/AGENT.md')))

    # Cover
    pdf.cover_page(len(SQUAD_ORDER), total_agents)

    # Each squad
    for squad_id in SQUAD_ORDER:
        squad_dir = BASE / squad_id
        squad_yaml = squad_dir / 'SQUAD.yaml'

        # Parse basic info from SQUAD.yaml
        description = ''
        agents_count = 0
        if squad_yaml.exists():
            content = squad_yaml.read_text(encoding='utf-8')
            for line in content.split('\n'):
                if line.startswith('description:'):
                    description = line.replace('description:', '').strip().strip('"')
                if line.strip().startswith('agents:') and ':' in line and 'agents:' == line.strip().split(':')[0]:
                    try:
                        agents_count = int(line.split(':')[1].strip())
                    except:
                        pass

        # Count agents from dirs
        agent_dirs = sorted([d for d in squad_dir.iterdir() if d.is_dir() and (d / 'AGENT.md').exists()])
        agents_count = len(agent_dirs)

        squad_name = SQUAD_NAMES.get(squad_id, squad_id)
        pdf.squad_header(clean(squad_name), agents_count, clean(description))

        for agent_dir in agent_dirs:
            agent_md = agent_dir / 'AGENT.md'
            agent_data = parse_agent_md(agent_md)
            pdf.agent_card(agent_data)

        print(f'OK {squad_name}: {agents_count} agentes')

    pdf.output(str(OUTPUT))
    print(f'\nPDF gerado: {OUTPUT}')
    print(f'Paginas: {pdf.page}')

if __name__ == '__main__':
    build_pdf()
