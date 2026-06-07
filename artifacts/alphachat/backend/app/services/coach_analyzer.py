import anthropic
import json
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

COACH_SYSTEM = """Você é um Coach de comunicação masculina. Analisa mensagens em 5 dimensões.

DIMENSÕES (score 0-10 cada):
- confianca: tonalidade assertiva, ausência de hedging, certeza nas palavras
- frame: manutenção de liderança, não ceder à pressão, estabelecer realidade
- calibracao: timing correto, leitura da situação, adaptação ao contexto
- polaridade: energia masculina presente, tensão, diferenciação clara
- assertividade: clareza de intenção, diretividade, sem desculpas

Retorne APENAS JSON válido neste formato exato:
{
  "scores": {
    "confianca": 7,
    "frame": 5,
    "calibracao": 8,
    "polaridade": 4,
    "assertividade": 6
  },
  "overall": 6.0,
  "diagnoses": {
    "confianca": "diagnóstico específico",
    "frame": "diagnóstico específico",
    "calibracao": "diagnóstico específico",
    "polaridade": "diagnóstico específico",
    "assertividade": "diagnóstico específico"
  },
  "red_flags": ["flag1", "flag2"],
  "green_flags": ["flag1", "flag2"],
  "priority_issue": "nome_da_dimensao_com_maior_problema"
}"""

async def analyze_message(
    user_message: str,
    history: list[dict],
    concepts: list[dict],
    character_state: dict,
    user_level: int
) -> dict:
    concepts_context = "\n".join([
        f"- {c['nome']}: {c['principio']}"
        for c in concepts[:3]
    ])

    prompt = f"""Mensagem do usuário para analisar:
"{user_message}"

Contexto da conversa (últimas 3 trocas):
{json.dumps(history[-6:], ensure_ascii=False, indent=2)}

Personagem atual: interesse {character_state.get('interest_level', 50)}/100

Conceitos relevantes da base:
{concepts_context}

Nível do usuário: {user_level}/6

Analise a mensagem e retorne o JSON."""

    response = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=600,
        system=COACH_SYSTEM,
        messages=[{"role": "user", "content": prompt}]
    )

    analysis = json.loads(response.content[0].text)
    analysis["overall"] = round(
        sum(analysis["scores"].values()) / len(analysis["scores"]), 1
    )
    return analysis
