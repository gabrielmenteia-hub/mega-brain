"""Pydantic v2 data models for the NEXUS pipeline.

AgentScore  — structured output from a single review agent (LLM output boundary).
CreativeBundle — pipeline state for a single creative asset.
"""
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class AgentScore(BaseModel):
    """Structured output from a single review agent.

    Used by instructor to enforce schema compliance on LLM responses.
    Few-shot examples are embedded via json_schema_extra for instructor calibration.
    """

    dimension: str = Field(
        description="Review dimension: copy|tech|compliance|performance"
    )
    score: int = Field(ge=1, le=10, description="Quality score 1-10")
    approved: bool = Field(description="Meets minimum threshold for this dimension")
    feedback: str = Field(
        min_length=10, description="Specific actionable feedback (at least 10 chars)"
    )
    strengths: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "dimension": "copy",
                    "score": 8,
                    "approved": True,
                    "feedback": "Hook forte com urgencia temporal. CTA claro. Pode melhorar transicao do meio.",
                    "strengths": ["Hook com urgencia", "CTA direto"],
                    "issues": ["Transicao abrupta no segundo paragrafo"],
                },
                {
                    "dimension": "copy",
                    "score": 4,
                    "approved": False,
                    "feedback": "Hook generico sem diferenciacao. Sem CTA. Texto longo demais para formato video curto.",
                    "strengths": [],
                    "issues": ["Hook generico", "Sem CTA", "Texto excede 60 palavras"],
                },
            ]
        }
    )


class CreativeBundle(BaseModel):
    """Pipeline state for a single creative asset.

    Tracks the creative through all pipeline stages: generation, review,
    regeneration, and final approval or quarantine.
    """

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique creative ID (UUID4)",
    )
    niche: str = Field(min_length=1, description="Target niche")
    script_text: str = Field(min_length=1, description="Ad script content")
    audio_path: str | None = Field(default=None, description="Path to generated audio")
    video_path: str | None = Field(default=None, description="Path to generated video")
    image_path: str | None = Field(default=None, description="Path to source image")
    status: str = Field(
        default="pending",
        description="Pipeline status: pending|reviewing|approved|rejected|quarantined",
    )
    attempt: int = Field(default=1, ge=1, description="Current attempt number")
    reviews: list[AgentScore] = Field(
        default_factory=list,
        description="Review scores from agents",
    )
