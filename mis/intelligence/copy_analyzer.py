"""
copy_analyzer — Etapa 1 do pipeline LLM de inteligência competitiva.

Recebe SpyData coletado pelos spies e analisa o framework de persuasão,
gatilhos emocionais, estrutura narrativa e elementos de prova social da copy.

Requirements: DOS-01
"""
import json
import os
from pathlib import Path

import structlog
from anthropic import APIConnectionError, AsyncAnthropic, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..spies.completeness_gate import SpyData

log = structlog.get_logger()

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "copy_analyzer.md"


class CopyAnalysisError(Exception):
    """Raised when copy analysis fails — gate, LLM error, or JSON decode error."""


async def analyze_copy(data: SpyData) -> dict:
    """Etapa 1: analisa copy e identifica framework de persuasão.

    Args:
        data: SpyData coletado pelos spies.

    Returns:
        dict com keys: framework_type, emotional_triggers,
        narrative_structure, social_proof_elements.

    Raises:
        CopyAnalysisError: Se copy_text ausente, LLM falha após retries,
            ou resposta não é JSON válido.
    """
    if not data.copy_text:
        raise CopyAnalysisError(
            "copy_text ausente — gate deve ter bloqueado antes de chegar aqui"
        )

    log.info("copy_analyzer.start", copy_len=len(data.copy_text))

    result_text = await _call_llm_with_retry(data)
    try:
        result = json.loads(result_text)
    except json.JSONDecodeError as e:
        raise CopyAnalysisError(
            f"LLM retornou não-JSON: {result_text[:200]}"
        ) from e

    log.info(
        "copy_analyzer.done",
        framework_type=result.get("framework_type"),
        triggers_count=len(result.get("emotional_triggers", [])),
    )
    return result


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((APIConnectionError, RateLimitError)),
    reraise=True,
)
async def _call_llm_with_retry(data: SpyData) -> str:
    """Call Anthropic API with tenacity retry on transient errors."""
    system_prompt = _PROMPT_PATH.read_text(encoding="utf-8")
    content = _build_user_content(data)
    client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": content}],
    )
    return response.content[0].text


def _build_user_content(data: SpyData) -> str:
    """Assemble user message content from SpyData."""
    parts = [f"# COPY DA PÁGINA DE VENDAS\n{data.copy_text}"]
    if data.offer_data:
        parts.append(
            f"\n# ESTRUTURA DA OFERTA\n"
            f"{json.dumps(data.offer_data, ensure_ascii=False)}"
        )
    if data.ads:
        parts.append(
            f"\n# ANÚNCIOS ATIVOS ({len(data.ads)})\n"
            f"{json.dumps(data.ads[:5], ensure_ascii=False)}"
        )
    if data.reviews:
        parts.append(
            f"\n# REVIEWS ({len(data.reviews)} coletados)\n"
            f"{json.dumps(data.reviews[:20], ensure_ascii=False)}"
        )
    return "\n".join(parts)
