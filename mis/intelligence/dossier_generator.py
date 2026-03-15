"""
dossier_generator — Etapa 2 do pipeline LLM de inteligência competitiva.

Recebe SpyData + output do copy_analyzer e gera dossiê completo em pt-BR
com why_it_sells, pains_addressed (com fonte), modeling_template e
opportunity_score. Registra cada chamada LLM na tabela llm_calls.

Requirements: DOS-02, DOS-03, DOS-04
"""
import json
import os
from datetime import datetime
from pathlib import Path

import structlog
from anthropic import APIConnectionError, AsyncAnthropic, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..db import get_db
from ..spies.completeness_gate import SpyData

log = structlog.get_logger()

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "dossier_generator.md"


class DossierGenerationError(Exception):
    """Raised when dossier generation fails — LLM error or JSON decode error."""


async def generate_dossier(
    data: SpyData,
    copy_analysis: dict,
    dossier_id: int,
    db_path: str,
) -> dict:
    """Etapa 2: gera dossiê completo em pt-BR. Registra chamada LLM no banco.

    Args:
        data: SpyData coletado pelos spies.
        copy_analysis: Output de analyze_copy() (Etapa 1).
        dossier_id: ID do dossiê no banco (para logging).
        db_path: Caminho para o arquivo SQLite.

    Returns:
        dict com keys: why_it_sells, pains_addressed, modeling_template,
        opportunity_score.

    Raises:
        DossierGenerationError: Se LLM falha após retries ou resposta não é JSON.
    """
    content = _build_user_content(data, copy_analysis)
    system_prompt = _PROMPT_PATH.read_text(encoding="utf-8")

    log.info(
        "dossier_generator.start",
        dossier_id=dossier_id,
        has_reviews=len(data.reviews) > 0,
        has_ads=len(data.ads) > 0,
    )

    client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = await _call_llm_with_retry(client, system_prompt, content)

    # Registrar tokens e custo no banco
    cost_usd = (
        response.usage.input_tokens * 0.000003
        + response.usage.output_tokens * 0.000015
    )
    db = get_db(db_path)
    db["llm_calls"].insert({
        "dossier_id": dossier_id,
        "model": "claude-sonnet-4-6",
        "stage": "dossier_generator",
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "cost_usd": round(cost_usd, 6),
        "created_at": datetime.utcnow().isoformat(),
    })

    result_text = response.content[0].text
    try:
        result = json.loads(result_text)
    except json.JSONDecodeError as e:
        raise DossierGenerationError(
            f"LLM retornou não-JSON: {result_text[:200]}"
        ) from e

    log.info(
        "dossier_generator.done",
        dossier_id=dossier_id,
        opportunity_score=result.get("opportunity_score", {}).get("score"),
        cost_usd=round(cost_usd, 6),
    )
    return result


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((APIConnectionError, RateLimitError)),
    reraise=True,
)
async def _call_llm_with_retry(client: AsyncAnthropic, system_prompt: str, content: str):
    """Call Anthropic API with tenacity retry on transient errors."""
    return await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": content}],
    )


def _build_user_content(data: SpyData, copy_analysis: dict) -> str:
    """Assemble user message content from SpyData and copy_analysis."""
    parts = [
        f"# ANÁLISE DE COPY (Etapa 1)\n{json.dumps(copy_analysis, ensure_ascii=False)}",
        f"\n# COPY ORIGINAL DA PÁGINA DE VENDAS\n{data.copy_text or ''}",
    ]
    if data.offer_data:
        parts.append(
            f"\n# ESTRUTURA DA OFERTA\n"
            f"{json.dumps(data.offer_data, ensure_ascii=False)}"
        )
    if data.reviews:
        parts.append(
            f"\n# REVIEWS DE COMPRADORES ({len(data.reviews)} coletados)\n"
            f"{json.dumps(data.reviews[:30], ensure_ascii=False)}"
        )
    if data.ads:
        parts.append(
            f"\n# ANÚNCIOS ATIVOS NO META ({len(data.ads)} anúncios)\n"
            f"{json.dumps(data.ads[:10], ensure_ascii=False)}"
        )
    return "\n".join(parts)
