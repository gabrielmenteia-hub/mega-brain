"""Synthesizer LLM — consolida sinais brutos em relatórios de dores por nicho.

Transforma centenas de posts/trends/comentários coletados num ciclo
em 5 dores acionáveis com evidências e nível de interesse.
Idempotente: re-execução substitui via ON CONFLICT(niche_id, cycle_at).

Requirements: RADAR-05, RADAR-06
"""
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

import anthropic
import sqlite_utils
import structlog

log = structlog.get_logger()

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "pain_synthesis_prompt.txt"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_cycle_signals(db_path: str, niche_slug: str, cycle_start_iso: str) -> list[dict]:
    """Busca sinais coletados a partir de cycle_start_iso para o nicho.

    Args:
        db_path: Caminho para o arquivo SQLite.
        niche_slug: Slug do nicho (ex: 'emagrecimento').
        cycle_start_iso: Timestamp ISO-8601 — retorna sinais com collected_at >= este valor.

    Returns:
        Lista de dicts com todos os campos de pain_signals.
    """
    db = sqlite_utils.Database(db_path)
    if "pain_signals" not in db.table_names():
        return []
    return list(db["pain_signals"].rows_where(
        "niche_slug = ? AND collected_at >= ?",
        [niche_slug, cycle_start_iso],
    ))


async def synthesize_niche_pains(
    niche_id: int,
    niche_name: str,
    niche_slug: str,
    cycle_at: str,
    db_path: str,
) -> dict | None:
    """Sintetiza sinais do ciclo atual em relatório de dores via LLM.

    Janela do ciclo: sinais coletados nas 2 horas anteriores a cycle_at.
    Idempotente: re-execução substitui via upsert em (niche_id, cycle_at).

    Args:
        niche_id: ID numérico do nicho em niches.
        niche_name: Nome legível do nicho (ex: 'Emagrecimento').
        niche_slug: Slug do nicho (ex: 'emagrecimento').
        cycle_at: ISO-8601 timestamp representando o momento do ciclo.
        db_path: Caminho para o arquivo SQLite.

    Returns:
        dict com chaves pains, niche, cycle_at, sources_used, cost_usd, signals_count.
        None se não houver sinais no ciclo.
    """
    # Janela do ciclo: sinais das últimas 2 horas antes de cycle_at
    cycle_dt = datetime.fromisoformat(cycle_at)
    cycle_start = (cycle_dt - timedelta(hours=2)).isoformat()
    signals = fetch_cycle_signals(db_path, niche_slug, cycle_start)

    if not signals:
        log.warning(
            "radar.synthesizer.no_signals",
            niche=niche_slug,
            cycle_at=cycle_at,
            alert="radar_synthesizer_no_signals",
        )
        return None

    # Montar sources_used
    sources_used: dict[str, int] = {}
    for s in signals:
        sources_used[s["source"]] = sources_used.get(s["source"], 0) + 1

    # Formatar sinais para o prompt
    signals_text = _format_signals_for_prompt(signals)

    # Montar prompt
    template = _PROMPT_PATH.read_text(encoding="utf-8")
    prompt = template.format(
        niche_name=niche_name,
        total_signals=len(signals),
        signals_text=signals_text,
    )

    # Chamar LLM
    client = anthropic.AsyncAnthropic()
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw_text = response.content[0].text
    cost_usd = (
        response.usage.input_tokens * 0.000003
        + response.usage.output_tokens * 0.000015
    )

    # Parse JSON do LLM (com fallback para JSON embutido em texto)
    try:
        llm_data = json.loads(raw_text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        llm_data = json.loads(match.group()) if match else {"pains": []}

    report = {
        "pains": llm_data.get("pains", []),
        "niche": niche_slug,
        "cycle_at": cycle_at,
        "sources_used": sources_used,
        "cost_usd": cost_usd,
        "signals_count": len(signals),
    }

    # Upsert idempotente via SQL raw (ON CONFLICT)
    _upsert_report(db_path, niche_id, cycle_at, report)

    log.info(
        "radar.synthesizer.report_generated",
        niche=niche_slug,
        cycle_at=cycle_at,
        signals_count=len(signals),
        cost_usd=cost_usd,
        pains_count=len(report["pains"]),
    )
    return report


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _upsert_report(db_path: str, niche_id: int, cycle_at: str, report: dict) -> None:
    """Upsert pain_reports row via ON CONFLICT — idempotente para (niche_id, cycle_at)."""
    import sqlite3
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO pain_reports (niche_id, cycle_at, report_json, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(niche_id, cycle_at) DO UPDATE SET
                report_json = excluded.report_json,
                created_at  = excluded.created_at
            """,
            [niche_id, cycle_at, json.dumps(report), datetime.utcnow().isoformat()],
        )
        conn.commit()
    finally:
        conn.close()


def _format_signals_for_prompt(signals: list[dict]) -> str:
    """Formata sinais brutos como texto estruturado para o LLM."""
    lines = []
    for s in signals:
        try:
            extra = json.loads(s.get("extra_json") or "{}")
        except json.JSONDecodeError:
            extra = {}

        line = f"[{s['source'].upper()}] {s['title']}"
        if s.get("score"):
            line += f" (score: {s['score']})"
        top_comments = extra.get("top_comments", [])
        if top_comments:
            line += f"\n  Comentários: {'; '.join(top_comments[:3])}"
        lines.append(line)
    return "\n".join(lines)
