"""Health route for the MIS dashboard."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


def is_htmx(request: Request) -> bool:
    """Return True if the request was made by HTMX."""
    return request.headers.get("HX-Request") == "true"


@router.get("/health", response_class=HTMLResponse)
async def health(request: Request) -> HTMLResponse:
    """Return system health page."""
    templates = request.app.state.templates

    jobs = []
    try:
        from mis.scheduler import get_scheduler
        scheduler = get_scheduler()
        jobs = list(scheduler.get_jobs())
    except Exception:
        pass

    return templates.TemplateResponse(
        request=request,
        name="health.html",
        context={"jobs": jobs},
    )
