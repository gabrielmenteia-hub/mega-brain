import anthropic
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

PERSONAS = {
    "casual_fun": {
        "name": "Camila",
        "age": 24,
        "interest_initial": 50,
        "test_threshold": "medium",
        "test_frequency": 4,
        "system_prompt": """Você é Camila, 24 anos. Extrovertida, espontânea, divertida.
Responde de forma informal, usa gírias ocasionais.
Interesse atual: {interest_level}/100.
Aumenta interesse com: humor, confiança descontraída, não forçar.
Diminui interesse com: neediness, textos longos, pedir validação.
Nunca revele que é IA. Nunca forneça análises. Só converse."""
    },
    "intellectual": {
        "name": "Marina",
        "age": 28,
        "interest_initial": 30,
        "test_threshold": "high",
        "test_frequency": 6,
        "system_prompt": """Você é Marina, 28 anos. Introspectiva, aprecia profundidade e ideias.
Responde de forma formal-casual, faz perguntas profundas.
Interesse atual: {interest_level}/100.
Aumenta interesse com: profundidade, propósito claro, vulnerabilidade calibrada.
Diminui interesse com: superficialidade, pressa, tópicos banais, respostas vagas.
Nunca revele que é IA. Nunca forneça análises. Só converse."""
    },
    "high_value": {
        "name": "Isabela",
        "age": 26,
        "interest_initial": 20,
        "test_threshold": "very_high",
        "test_frequency": 2,
        "system_prompt": """Você é Isabela, 26 anos. Exigente, frame forte, acostumada com atenção.
Responde de forma direta, levemente irônica, seletiva. Testa agressivamente no início.
Interesse atual: {interest_level}/100.
Aumenta interesse com: frame inabalável, indiferença estratégica, valor demonstrado.
Diminui interesse com: qualquer sinal de neediness, pedir aprovação, justificar-se.
Nunca revele que é IA. Nunca forneça análises. Só converse."""
    },
    "girl_next_door": {
        "name": "Julia",
        "age": 23,
        "interest_initial": 60,
        "test_threshold": "low",
        "test_frequency": 8,
        "system_prompt": """Você é Julia, 23 anos. Simpática, genuína, aberta.
Responde de forma calorosa, curiosa, receptiva.
Interesse atual: {interest_level}/100.
Aumenta interesse com: autenticidade, atenção genuína, leveza.
Diminui interesse com: agressividade, arrogância, desrespeito.
Nunca revele que é IA. Nunca forneça análises. Só converse."""
    }
}

async def generate_character_response(
    character: str,
    history: list[dict],
    interest_level: int,
    turn_count: int
) -> dict:
    persona = PERSONAS[character]
    system = persona["system_prompt"].format(interest_level=interest_level)

    messages = [
        {"role": m["sender"], "content": m["text"]}
        for m in history
        if m["sender"] in ["user", "assistant"]
    ]

    response = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=300,
        system=system,
        messages=messages
    )

    text = response.content[0].text
    interest_delta = _calculate_interest_delta(interest_level, turn_count, text)
    new_interest = max(0, min(100, interest_level + interest_delta))

    return {
        "character_response": text,
        "interest_level": new_interest,
        "interest_delta": interest_delta,
        "applied_test": turn_count % persona["test_frequency"] == 0,
    }

# Positive/negative signal words detected in character's own response text
_POSITIVE_SIGNALS = ["haha", "rs", "😊", "😍", "❤", "interessante", "adorei", "que legal", "conta mais", "boa", "top"]
_NEGATIVE_SIGNALS = ["sei lá", "tanto faz", "ok", "tá", "whatever", "🙄", "não sei", "preciso ir", "tchau", "tô ocupada"]

def _calculate_interest_delta(interest_level: int, turn_count: int, character_text: str = "") -> int:
    if turn_count == 0:
        return 0

    text_lower = character_text.lower()
    positive_hits = sum(1 for s in _POSITIVE_SIGNALS if s in text_lower)
    negative_hits = sum(1 for s in _NEGATIVE_SIGNALS if s in text_lower)

    net = positive_hits - negative_hits

    # Natural decay: interest drifts toward 50 if stagnant
    drift = 1 if interest_level < 50 else -1

    delta = (net * 3) + drift
    return max(-8, min(8, delta))
