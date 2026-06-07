from __future__ import annotations
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AlphaChat"
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8081"]

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str

    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_INDEX: str = "alphachat-knowledge"
    PINECONE_ENVIRONMENT: str = "gcp-starter"

    # Anthropic Claude
    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL: str = "claude-sonnet-4-6"

    # OpenAI (embeddings only)
    OPENAI_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536

    # Voyage AI (embeddings)
    VOYAGE_API_KEY: str = ""

    # Supabase JWT (Settings → API → JWT Secret)
    SUPABASE_JWT_SECRET: str = ""

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_PRO: str = ""
    STRIPE_PRICE_MASTER: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
