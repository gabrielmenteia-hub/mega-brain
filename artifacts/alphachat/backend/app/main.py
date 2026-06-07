from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import sessions, messages, progress, knowledge, subscription
from app.core.config import settings

app = FastAPI(
    title="AlphaChat API",
    version="1.0.0",
    description="Conversation Simulator with AI Coach"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(subscription.router, prefix="/api/subscription", tags=["subscription"])

@app.get("/health")
def health():
    return {"status": "ok"}
