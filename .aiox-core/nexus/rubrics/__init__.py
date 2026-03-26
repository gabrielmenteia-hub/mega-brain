"""Central export for all NEXUS review rubrics."""
from nexus.rubrics.copy_rubric import COPY_RUBRIC
from nexus.rubrics.tech_rubric import TECH_RUBRIC
from nexus.rubrics.compliance_rubric import COMPLIANCE_RUBRIC
from nexus.rubrics.performance_rubric import PERFORMANCE_RUBRIC

ALL_RUBRICS = [COPY_RUBRIC, TECH_RUBRIC, COMPLIANCE_RUBRIC, PERFORMANCE_RUBRIC]

__all__ = [
    "COPY_RUBRIC",
    "TECH_RUBRIC",
    "COMPLIANCE_RUBRIC",
    "PERFORMANCE_RUBRIC",
    "ALL_RUBRICS",
]
