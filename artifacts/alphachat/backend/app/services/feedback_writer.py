import anthropic
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

LEVEL_TONES = {
    1: "Seja didático, explique o porquê de cada ponto.",
    2: "Seja didático, explique o porquê de cada ponto.",
    3: "Seja direto, menos explicação, mais exemplos concretos.",
    4: "Seja brutalmente direto, foco em nuances finas.",
    5: "Seja brutalmente direto, foco em nuances finas.",
    6: "Tom peer-to-peer, questione escolhas estratégicas."
}

FEEDBACK_SYSTEM = """Você é um Coach de comunicação masculina — direto, brutal quando necessário, educativo.
Nunca use eufemismos. Sempre dê alternativa concreta.
Cite o conceito pelo nome. Uma só crítica principal por análise.

Formato obrigatório:
Score geral: X.X/10

PROBLEMA PRINCIPAL
→ [Dimensão]: [O que aconteceu especificamente]
→ [Por que importa para o interesse dela]

📖 [Nome do Conceito] — [Livro(s)]
"[Princípio em 1 linha]"

COMO CORRIGIR
Em vez de: "[trecho problemático]"
Tente:
  1. "[alternativa 1]"
  2. "[alternativa 2]"
  3. "[alternativa 3]"

O QUE FUNCIONOU
✅ [green flags — apenas se existirem]"""

async def write_feedback(
    analysis: dict,
    user_message: str,
    user_level: int,
    concepts: list[dict]
) -> dict:
    concept = concepts[0] if concepts else {}
    tone = LEVEL_TONES.get(user_level, LEVEL_TONES[3])

    prompt = f"""Tom para este usuário (nível {user_level}): {tone}

Análise:
- Score geral: {analysis['overall']}
- Problema principal: {analysis['priority_issue']}
- Diagnóstico: {analysis['diagnoses'].get(analysis['priority_issue'], '')}
- Red flags: {', '.join(analysis.get('red_flags', []))}
- Green flags: {', '.join(analysis.get('green_flags', []))}

Conceito mais relevante:
- Nome: {concept.get('nome', 'Frame Control')}
- Princípio: {concept.get('principio', '')}
- Livros: {', '.join(concept.get('livros', []))}

Mensagem original do usuário:
"{user_message}"

Gere o feedback no formato especificado."""

    response = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=500,
        system=FEEDBACK_SYSTEM,
        messages=[{"role": "user", "content": prompt}]
    )

    feedback_text = response.content[0].text
    alternatives = _extract_alternatives(feedback_text)

    return {
        "feedback_text": feedback_text,
        "score_overall": analysis["overall"],
        "priority_issue": analysis["priority_issue"],
        "concept_cited": concept.get("id", ""),
        "alternatives": alternatives
    }

def _extract_alternatives(text: str) -> list[str]:
    lines = text.split("\n")
    alternatives = []
    for line in lines:
        line = line.strip()
        if line.startswith(("1.", "2.", "3.")):
            alternatives.append(line[2:].strip().strip('"'))
    return alternatives[:3]
