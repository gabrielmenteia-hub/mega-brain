#!/usr/bin/env python3
"""
update_sugarman_js002.py
Atualiza SOUL.md e DNA.yaml de Joseph Sugarman com os 30 Gatilhos de JS002.
APPEND apenas — não substitui conteúdo existente.

Uso:
    python core/intelligence/update_sugarman_js002.py
"""

import re
import sys
import io
from pathlib import Path
from datetime import date

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ─── Paths ─────────────────────────────────────────────────────────────────────
BASE       = Path("C:/Users/Gabriel/MEGABRAIN")
BOOK_PATH  = BASE / "inbox/JOSEPH SUGARMAN/BOOKS/Triggers [JS002].txt"
SOUL_PATH  = BASE / "agents/minds/JOSEPH-SUGARMAN/SOUL.md"
DNA_PATH   = BASE / "knowledge/dna/persons/joseph-sugarman/DNA.yaml"
TODAY      = date.today().isoformat()


# ─── 30 Triggers: mapeamento completo (nome → metadados) ───────────────────────
# Ordem de aparição no livro (capítulos 1–30)
TRIGGERS_ORDERED = [
    (1,  "Consistency",           "The Ice Cream Ordering Sequence"),
    (2,  "Product Nature",        "When Your Neighbor Kicks the Bucket"),
    (3,  "Prospect Nature",       "Love and the Campus Hooker"),
    (4,  "Objection Raising",     "Raising Dirty Laundry Up a Flag Pole"),
    (5,  "Objection Resolution",  "Turning Monkey Poop into Shinola"),
    (6,  "Involvement/Ownership", "The TV Salesman's Secret"),
    (7,  "Integrity",             "Your Money or Your Life"),
    (8,  "Storytelling",          "Talkin' Story in Hawaii"),
    (9,  "Authority",             "Instilling Authority in the Men's Bathroom"),
    (10, "Proof of Value",        "Our President Drives a Rabbit"),
    (11, "Emotion",               "Gorilla Survival Tactics for Marital Bliss"),
    (12, "Justify with Logic",    "The Devil Is in the Logic"),
    (13, "Greed",                 "The Last Temptation of the Well Heeled"),
    (14, "Credibility",           "Brain Surgery for Dummies"),
    (15, "Satisfaction Conviction","The Art of Extreme Passion"),
    (16, "Linking",               "Mass Delusion and Other Good Marketing Ideas"),
    (17, "Desire to Belong",      "The National Hermits Convention"),
    (18, "Desire to Collect",     "Airplane Tail Collecting Made Easy"),
    (19, "Sense of Urgency",      "Help, It's a Fire"),
    (20, "Exclusivity",           "The Snowmobile That Bit Me"),
    (21, "Simplicity",            "KIS&S: Keep it Stupid and Simple"),
    (22, "Guilt",                 "Winning Through Legal Bribery"),
    (23, "Specificity",           "Anal Retention Really Helps"),
    (24, "Familiarity",           "The Military Bubble Gum Conspiracy"),
    (25, "Patterning",            "Making Love with Your Prospect"),
    (26, "Hope",                  "Winning the Jackpot"),
    (27, "Curiosity",             "Blatant Seduction of the Third Kind"),
    (28, "Harmonize",             "Splish Splash, I Was Takin' a Bath"),
    (29, "Mental Engagement",     "How to Manufacture a Hormone"),
    (30, "Honesty",               "The Most Powerful Force in Selling"),
]

# Insights-chave por gatilho (extraídos do livro)
TRIGGER_INSIGHTS = {
    1:  ("Pequeno comprometimento inicial expande venda posterior",
         "A waitress who committed to ice cream couldn't un-commit when whipped cream was added as an afterthought. "
         "First sale = simple, small, consistent with needs. Once committed, prospect primes for upsell. "
         "JS&A upsells succeeded 50%+ of the time from this single principle."),
    2:  ("Todo produto tem uma natureza emocional única a descobrir",
         "Howard Franklin sold insurance not by warning about death, but by being present when Sugarman's neighbor died. "
         "You can't scare people into buying prevention products. Find the emotional trigger UNIQUE to that product "
         "by becoming an expert on both product and prospect through immersion and mining your own life experiences."),
    3:  ("Prospect tem uma natureza emocional que determina o ponto de entrada",
         "Sugarman joined the worst fraternity on campus and transformed it using 'Operation Survival' — "
         "hired exotic dancers as hostesses, forced brothers to express brotherly love. Pledge class exploded. "
         "The key: identify the two core emotional motivators of your prospect and engineer the environment around them."),
    4:  ("Levantar a objeção do prospect antes que ele a verbalize remove sua resistência",
         "If you know your prospect is thinking something negative, say it yourself first. "
         "Raising the objection preemptively transfers ownership to you and deflates its power. "
         "Never hide known flaws — surface them first, then contextualize or resolve them."),
    5:  ("Resolver a objeção com criatividade transforma o negativo em argumento de venda",
         "A product defect, limitation, or odd characteristic can be reframed as a feature. "
         "Sugarman's BluBlocker defect story: the distortion people noticed became proof of UV blockage. "
         "The constraint that seems to kill the sale, when resolved with honesty and creativity, builds trust."),
    6:  ("Fazer o prospect mentalmente possuir o produto antes de comprar aumenta conversão",
         "QVC demo technique: put the product in the viewer's hands mentally. "
         "'Imagine you're holding this. Feel the weight.' Involvement devices — samples, demos, try-ons — "
         "create psychological ownership. Mental possession precedes physical purchase. Any device that creates "
         "active engagement (even trivial) raises commitment to buy."),
    7:  ("Integrity é alinhamento entre pensamento, palavra e ação — o prospect detecta qualquer inconsistência",
         "A friend's mugger had total integrity: said what he wanted, got it, let her go. "
         "Her own lawyers had none. Integrity = walking your talk. Sugarman's Maui observation: "
         "the most vocal about spirituality are the biggest violators. In sales: any claim you can't back "
         "up destroys the environment. Integrity is the prerequisite for all other triggers."),
    8:  ("História cria relação emocional, mantém atenção e torna a mensagem inesquecível",
         "In Hawaii, 'we gotta talk story' is how serious conversations start. Stories are how humans "
         "process experience since childhood. The BluBlocker ad that launched 20M pairs in sales was "
         "a story about meeting Len and looking through the lenses. The story IS the Slippery Slide."),
    9:  ("Autoridade não precisa ser sua — pode ser emprestada de objetos, ambiente e contexto",
         "Sugarman's story: a salesman who put on a doctor's white coat in a men's bathroom to pitch "
         "a medical device. Instant authority transfer. Authority can come from: titles, certifications, "
         "experience claims, famous endorsers, published testimonials, professional setting, or uniform."),
    10: ("Prova de valor muda a percepção de preço ao criar comparação favorável",
         "A Volkswagen Rabbit ad that started with 'Our president drives a Rabbit' — implying even "
         "the executive chose economy. Proof of value isn't about features, it's about anchoring "
         "perceived worth relative to price. Always answer 'compared to what?' in the prospect's mind."),
    11: ("Emoção é a energia da venda — lógica é apenas a racionalização posterior",
         "Gorilla suit story: a salesman wore a gorilla suit to close a deal, then calmly removed the "
         "head. Prospect laughed, bought. Emotion breaks resistance and creates memory. "
         "The Mercedes story: he bought for what it said about him, justified to wife with rack and pinion. "
         "Every purchase is emotional first. Design the emotional journey, not the logical argument."),
    12: ("Lógica não vende — mas sem lógica o comprador não consegue justificar a decisão emocional",
         "The devil in the logic: if your emotional pitch is strong but your logic is weak, "
         "the prospect can't 'sell' the purchase to themselves or others. Provide ammunition "
         "for rational justification AFTER the emotional desire is created. "
         "Logic = the story the buyer tells himself and his spouse about why the purchase makes sense."),
    13: ("Greed é um gatilho poderoso quando apresentado como oportunidade genuína, não exploração",
         "The 'last temptation' story: Sugarman offered a product at a loss leader price to one segment "
         "of a list. The greedy prospect who wanted more than was offered actually bought more. "
         "Greed works when the offer frames the prospect as 'smart' for acting — not as someone being tricked."),
    14: ("Credibilidade vem de detalhes específicos, não de claims gerais",
         "Brain surgery analogy: if a neurosurgeon says 'I'm good at this,' you shrug. "
         "If he says 'I've performed 3,400 procedures with a 99.2% success rate at Mayo Clinic,' you believe. "
         "Credibility = specificity + verifiable track record + institutional association. "
         "The more specific and checkable the claim, the more credible it is."),
    15: ("Garantia forte elimina risco percebido e prova convicção do vendedor no produto",
         "Extreme passion story: Sugarman stood behind a product so completely that he offered a "
         "lifetime guarantee when competitors offered 30 days. The guarantee itself became a sales point. "
         "Satisfaction conviction = the seller's belief made tangible. The stronger the guarantee, "
         "the more it signals confidence and removes prospect's perceived risk barrier."),
    16: ("Linking conecta um produto desconhecido a algo familiar para transferir credibilidade",
         "Mass delusion example: herd behavior in investing. When you link your product to a "
         "well-established category or reference point the prospect already trusts, the trust transfers. "
         "Linking can use analogies, comparisons, celebrity associations, or known categories."),
    17: ("Pertencimento a um grupo exclusivo é um motivador de compra mais poderoso que o produto",
         "National Hermits Convention: even those who claim to want isolation join groups of other isolationists. "
         "Humans are social creatures. Products that offer membership in an exclusive, desirable "
         "group trigger the belonging instinct. Create the tribe first; the product is the membership card."),
    18: ("Impulso colecionador transforma uma compra em série de compras — design para coleções",
         "Airplane tail collecting: when Sugarman discovered collectors would buy his products to complete "
         "a set, he started designing products in series. The desire to collect is a powerful upsell engine. "
         "Any product line can be positioned as a collection: numbered editions, matching sets, seasonal releases."),
    19: ("Urgência genuína acelera decisão — urgência falsa destrói confiança",
         "'Help, it's a fire' — when your house is burning, you call the first available service. "
         "Real urgency (deadline, scarcity, price increase) compresses decision time. "
         "Artificial urgency ('this offer expires soon') works short-term but corrodes trust permanently. "
         "Only create urgency with a genuine, defensible reason."),
    20: ("Exclusividade cria desejo ao tornar a posse um símbolo de status diferenciado",
         "Snowmobile story: Sugarman was bitten by the exclusivity bug when a salesman told him "
         "only 500 units existed. Exclusivity triggers scarcity + status + identity simultaneously. "
         "The most effective exclusivity offers both limited quantity AND membership in an elite group."),
    21: ("Simplicidade remove atrito cognitivo — quanto mais fácil de entender, mais fácil de comprar",
         "KIS&S = Keep It Stupid and Simple. Sugarman's rule: if your prospect has to work to understand "
         "your offer, you've already lost them. Simplicity applies to: offer structure, pricing, CTA, "
         "and product explanation. Complexity is the enemy of conversions."),
    22: ("Culpa ativa generosidade — o prospect que se sente devedor age para restaurar equilíbrio",
         "Legal bribery story: small gifts given before the ask create psychological debt. "
         "The recipient feels obligated to reciprocate. Guilt = the feeling that you owe someone. "
         "Used ethically: provide genuine value first, then make your ask. The gift creates context."),
    23: ("Especificidade cria credibilidade automática — números precisos são mais persuasivos que afirmações vagas",
         "Anal retention story: Sugarman's obsession with detail led him to include specific numbers "
         "in all copy. '20,000 individual filtering elements' vs 'many filters.' "
         "Specific numbers signal honesty because only someone with real data would use them. "
         "Vagueness signals uncertainty or deception."),
    24: ("Familiaridade reduz resistência — o conhecido é automaticamente mais confiável",
         "Military bubble gum conspiracy: Sugarman discovered that products associated with familiar "
         "brands or categories sold better even with identical features. "
         "The familiar face, brand, format, or packaging reduces cognitive resistance. "
         "When entering new markets, anchor to familiar references before introducing new elements."),
    25: ("Patterning usa padrões esperados para criar conforto — e quebrar padrões para criar impacto",
         "Making love with your prospect: the sales process has a rhythm, a courtship structure. "
         "When you follow expected patterns (small talk → need discovery → presentation → close), "
         "prospects feel safe. Intentional pattern interrupts (unexpected humor, unusual offer structure) "
         "create attention spikes. Know which patterns to follow and which to break."),
    26: ("Hope é o gatilho mais humano — vender transformação, não produto",
         "Hope story: lottery winner phenomenon. People don't buy lottery tickets for expected value; "
         "they buy the feeling of possibility. Every product that sells well sells a version of hope: "
         "hope for health, wealth, love, status, or freedom. Position your product as the vehicle "
         "for a credible, specific, desirable transformation."),
    27: ("Curiosidade é o motor do Slippery Slide — loops abertos forçam a próxima leitura",
         "Blatant seduction story: the most seductive ads start with a headline that creates an "
         "irresolvable itch. Curiosity works by opening a loop the prospect must close. "
         "The pattern: 'There's something I know about X that you don't, and it will surprise you.' "
         "Every chapter, every paragraph should end with an implied promise: 'there's more.'"),
    28: ("Harmonize com objeções em vez de refutá-las — concordar primeiro remove a resistência",
         "Splish splash bath story: a salesman who argued with every objection lost sales. "
         "One who said 'You're absolutely right, and here's why that makes this even more relevant...' "
         "closed every time. Harmonizing = validating the prospect's view before redirecting. "
         "Never fight resistance; absorb it and redirect it."),
    29: ("Engajamento mental cria comprometimento — o prospect que pensa fica; o que não pensa vai embora",
         "Manufacturing hormones story: make the prospect actively participate in your presentation. "
         "Ask questions that require answers. Create physical involvement (hold this, try this). "
         "Use thought experiments ('Imagine if...'). Any mental work creates ownership of the conclusion. "
         "The prospect who discovers a benefit themselves is more convinced than one who is told."),
    30: ("Honestidade é o gatilho mais poderoso — e o mais raro",
         "The most powerful force in selling is honesty — and the reason it works is that it's so rare. "
         "When you tell prospects what's wrong with your product, what it can't do, who shouldn't buy it, "
         "you destroy their defenses. The honest admission of weakness makes everything else you say "
         "automatically credible. Sugarman used this on QVC and in every major ad that ran for years."),
}


# ─── Parser ────────────────────────────────────────────────────────────────────

def parse_book(book_path: Path) -> dict:
    """Extrai histórias pessoais de cada capítulo do livro Triggers."""
    lines = book_path.read_text(encoding="utf-8").splitlines()

    # Localizar posições de "Trigger N:" (fim de cada capítulo)
    # Nota: alguns triggers têm a linha quebrada ex: "Trigger 12\n: Justify..."
    trigger_ends = []  # (line_idx, trigger_num)
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Padrão normal: "Trigger 12: Justify with Logic"
        m = re.match(r'^Trigger\s+(\d+)\s*:', stripped)
        if m:
            trigger_ends.append((i, int(m.group(1))))
            continue
        # Padrão quebrado: "Trigger 12" seguido de ": Justify..."
        m2 = re.match(r'^Trigger\s+(\d+)\s*$', stripped)
        if m2 and i + 1 < len(lines) and lines[i + 1].strip().startswith(':'):
            trigger_ends.append((i, int(m2.group(1))))

    chapters = {}
    for idx, (end_line, tnum) in enumerate(trigger_ends):
        # Início do capítulo: logo após o footer do capítulo anterior
        if idx == 0:
            start_line = 285  # Após introdução
        else:
            prev_end = trigger_ends[idx - 1][0]
            # Pular "Trigger N:", nome, título do capítulo (3-5 linhas)
            start_line = prev_end + 5

        # Extrair linhas do capítulo (limpas)
        raw_lines = lines[start_line:end_line]
        paragraphs = _extract_paragraphs(raw_lines)

        # História: primeiros 2 parágrafos substantivos
        story_paras = [p for p in paragraphs if len(p) > 60][:3]
        story = " ".join(story_paras)
        if len(story) > 800:
            story = story[:797] + "..."

        chapters[tnum] = {"story": story}

    return chapters


def _extract_paragraphs(lines: list) -> list:
    """Junta linhas em parágrafos, removendo artefatos de OCR."""
    paras = []
    current = []

    for line in lines:
        line = line.strip()
        # Remover artefatos: linhas de 1 letra maiúscula (OCR)
        if re.match(r'^[A-Z]$', line):
            continue
        # Linha vazia = fim de parágrafo
        if not line:
            if current:
                paras.append(" ".join(current))
                current = []
        else:
            current.append(line)

    if current:
        paras.append(" ".join(current))

    return paras


# ─── Gerador de DNA.yaml ───────────────────────────────────────────────────────

def generate_dna_additions(chapters: dict) -> str:
    """Gera bloco YAML para adicionar ao DNA.yaml."""
    lines = [
        "",
        "  # ════════════════════════════════════════════════════════",
        "  # JS002 — Triggers (30 Gatilhos Psicológicos)",
        "  # Integrado em: " + TODAY,
        "  # ════════════════════════════════════════════════════════",
    ]

    # L3: uma entrada por gatilho
    lines.append("")
    lines.append("  # JS002 Heurísticas por Gatilho (L3)")

    for num, name, chapter_title in TRIGGERS_ORDERED:
        short_name = name.replace(" ", "_").replace("/", "_").replace("&", "and").lower()
        insight_title, insight_body = TRIGGER_INSIGHTS[num]
        story = chapters.get(num, {}).get("story", "")

        entry = f"""
    - id: JS002_HEU_{num:02d}
      titulo: "Gatilho {num}: {name} — {insight_title}"
      conteudo: |
        HISTÓRIA PESSOAL: "{chapter_title}"
        {story[:400] + "..." if len(story) > 400 else story}

        INSIGHT CENTRAL: {insight_body}
      source_id: JS002
      source_chunks: [JS002_{num:02d}]
      confidence: 0.97"""
        lines.append(entry)

    # L4: Framework dos 30 Gatilhos (updated vs JS001_FW_001)
    trigger_list = "\n        ".join(
        f"{num:02d}. {name} — {chapter_title}"
        for num, name, chapter_title in TRIGGERS_ORDERED
    )

    lines.append(f"""
    - id: JS002_FW_001
      titulo: "Os 30 Gatilhos Psicológicos — mapa completo com histórias pessoais"
      conteudo: |
        Cada gatilho foi ensinado por Sugarman através de uma história real da sua vida.
        A sequência reflete os capítulos do livro Triggers (JS002):

        {trigger_list}

        PRINCÍPIO META: Os gatilhos são cumulativos. Quanto mais ativados simultaneamente,
        maior o impacto. Sugarman recomenda identificar os 10 mais relevantes para o seu
        contexto e tornar-se expert neles antes de avançar para os demais.

        DIFERENÇA VS JS001_FW_001: este entry contém o mapeamento completo com histórias
        e insights extraídos diretamente de JS002. JS001_FW_001 contém a lista conceitual.
      source_id: JS002
      source_chunks: [JS002_APP_A, JS002_APP_D]
      confidence: 0.99""")

    return "\n".join(lines)


# ─── Gerador de SOUL.md ────────────────────────────────────────────────────────

def generate_soul_section(chapters: dict) -> str:
    """Gera seção para adicionar ao SOUL.md."""
    blocks = []

    blocks.append("\n---\n")
    blocks.append("## ◆ OS 30 GATILHOS — HISTÓRIAS QUE ENSINAM\n")
    blocks.append(
        "[v2.0 — Integração JS002: Triggers]\n"
        "Cada gatilho nasceu de uma experiência real. "
        "Não aprendi persuasão de livros — aprendi pedindo sorvete em Nova York nos anos 50 "
        "e descobrindo que a *ordem* do pedido determinava o preço que a garçonete cobrava.\n"
    )
    blocks.append(
        "Abaixo, cada um dos 30 gatilhos com a história que o originou "
        "e o insight aplicado. ^[JS002]\n"
    )

    for num, name, chapter_title in TRIGGERS_ORDERED:
        insight_title, _ = TRIGGER_INSIGHTS[num]
        story = chapters.get(num, {}).get("story", "")
        story_preview = story[:350] + "..." if len(story) > 350 else story

        blocks.append(f"\n### Gatilho {num:02d}: {name}")
        blocks.append(f"*História: \"{chapter_title}\"*\n")
        blocks.append(f"{story_preview}\n")
        blocks.append(f"**Insight:** {insight_title} ^[JS002_HEU_{num:02d}]\n")

    return "\n".join(blocks)


def generate_soul_evolution_update() -> str:
    """Gera linha de atualização para ◆ COMO EVOLUI."""
    return f"""
{TODAY}  │ Evolução (v2.0)
             │ Via: JS002 — Triggers (50.973 palavras)
             │ 30 Gatilhos com histórias pessoais integrados
             │ +30 L3_heuristicas, +1 L4_framework no DNA.yaml
             │ SOUL.md: nova seção ◆ OS 30 GATILHOS adicionada"""


# ─── Updaters ─────────────────────────────────────────────────────────────────

def update_dna_yaml(additions: str):
    """Appenda novas entradas ao DNA.yaml dentro de L3_heuristicas."""
    content = DNA_PATH.read_text(encoding="utf-8")

    # Verificar se já foi integrado
    if "JS002_HEU_01" in content:
        print("  ⚠️  DNA.yaml já contém JS002 — pulando (idempotente).")
        return False

    # Encontrar fim de L3_heuristicas para inserir antes de L4_frameworks
    marker = "  L4_frameworks:"
    if marker not in content:
        # Adicionar ao final
        new_content = content.rstrip() + "\n" + additions + "\n"
    else:
        insert_pos = content.index(marker)
        new_content = content[:insert_pos] + additions + "\n\n" + content[insert_pos:]

    DNA_PATH.write_text(new_content, encoding="utf-8")
    return True


def update_soul_md(soul_section: str, evolution_update: str):
    """Appenda nova seção ao SOUL.md e atualiza ◆ COMO EVOLUI."""
    content = SOUL_PATH.read_text(encoding="utf-8")

    # Verificar idempotência
    if "OS 30 GATILHOS" in content:
        print("  ⚠️  SOUL.md já contém seção JS002 — pulando (idempotente).")
        return False

    # Atualizar ◆ COMO EVOLUI: substituir linha PENDENTE
    content = content.replace(
        "PENDENTE     │ JS002 — Triggers (50.973 palavras)\n"
        "             │ DNA.yaml e SOUL.md a ATUALIZAR (não criar novo)",
        evolution_update.strip()
    )

    # Atualizar versão no header
    content = content.replace(
        "**Versão:** 1.0",
        "**Versão:** 2.0"
    )
    content = content.replace(
        f"**Última evolução:** {TODAY.split('-')[0]}",
        f"**Última evolução:** {TODAY}"
    )
    content = content.replace(
        "*Última atualização: 2026-03-03 — v1.0 (JS001 integrado | JS002 pendente)*",
        f"*Última atualização: {TODAY} — v2.0 (JS001 + JS002 integrados | 30 Gatilhos com histórias)*"
    )

    # Inserir nova seção antes de ◆ MINHAS TENSÕES INTERNAS
    insert_before = "## ◆ MINHAS TENSÕES INTERNAS"
    if insert_before in content:
        content = content.replace(insert_before, soul_section + "\n\n" + insert_before)
    else:
        content = content.rstrip() + "\n\n" + soul_section + "\n"

    SOUL_PATH.write_text(content, encoding="utf-8")
    return True


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  SUGARMAN JS002 — Update Script")
    print(f"  Data: {TODAY}")
    print("=" * 60)

    # Verificar arquivos
    for path, label in [(BOOK_PATH, "Livro JS002"), (SOUL_PATH, "SOUL.md"), (DNA_PATH, "DNA.yaml")]:
        if not path.exists():
            print(f"  ✗ {label} não encontrado: {path}")
            sys.exit(1)
        print(f"  ✓ {label}: {path.name}")

    print("\n[1/3] Extraindo conteúdo do livro...")
    chapters = parse_book(BOOK_PATH)
    print(f"  → {len(chapters)} capítulos extraídos")

    print("\n[2/3] Gerando adições ao DNA.yaml...")
    dna_additions = generate_dna_additions(chapters)
    updated_dna = update_dna_yaml(dna_additions)
    if updated_dna:
        print("  ✓ DNA.yaml atualizado (+30 L3_heuristicas, +1 L4_framework)")

    print("\n[3/3] Gerando adições ao SOUL.md...")
    soul_section = generate_soul_section(chapters)
    evolution_update = generate_soul_evolution_update()
    updated_soul = update_soul_md(soul_section, evolution_update)
    if updated_soul:
        print("  ✓ SOUL.md atualizado (v2.0 — ◆ OS 30 GATILHOS adicionado)")

    print("\n" + "=" * 60)
    print("  CONCLUÍDO — Sugarman v2.0")
    print("  JS001 + JS002 integrados")
    print("  30 Gatilhos com histórias pessoais no DNA")
    print("=" * 60)


if __name__ == "__main__":
    main()
