"""Analysis session domain model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AnalysisSession:
    id: Optional[int]
    resume_id: int
    similarity_score: float
    gap_report: str

    missing_keywords: list | None = None
