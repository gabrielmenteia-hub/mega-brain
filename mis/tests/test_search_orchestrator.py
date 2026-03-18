"""RED tests for search_orchestrator.

These tests define the observable contract for:
  - run_manual_search: must be an async coroutine function
  - register_task / cancel_task: task registry for in-flight asyncio.Task objects

All tests FAIL with ImportError or ModuleNotFoundError because
mis.search_orchestrator does not yet exist. This is the expected RED state.
"""
import asyncio
import inspect

import pytest

# RED import — module does not exist yet.
# Expected failure: ModuleNotFoundError.
from mis.search_orchestrator import (  # noqa: F401
    cancel_task,
    register_task,
    run_manual_search,
)


# ---------------------------------------------------------------------------
# Contract: run_manual_search is a coroutine
# ---------------------------------------------------------------------------


def test_run_manual_search_is_coroutine():
    """run_manual_search must be an async function (coroutine function).

    This is a structural test — confirms the asyncio contract before
    any execution happens.
    """
    assert inspect.iscoroutinefunction(run_manual_search), (
        "run_manual_search must be declared 'async def'"
    )


# ---------------------------------------------------------------------------
# Contract: task registry
# ---------------------------------------------------------------------------


def test_cancel_task_returns_false_for_unknown():
    """cancel_task for a session_id that was never registered must return False.

    Ensures the registry handles unknown keys gracefully without raising.
    """
    result = cancel_task(session_id=9999)
    assert result is False


def test_register_and_cancel_task():
    """register_task stores an asyncio.Task; cancel_task cancels it and
    returns True.

    Uses a fresh event loop to avoid interference with other tests.
    The dummy coroutine sleeps for 10s so the task is guaranteed to be
    pending (not completed) when cancel_task is called.
    """
    async def _dummy():
        await asyncio.sleep(10)

    loop = asyncio.new_event_loop()
    try:
        task = loop.create_task(_dummy())
        register_task(1, task)
        result = cancel_task(1)
        assert result is True
    finally:
        loop.close()
