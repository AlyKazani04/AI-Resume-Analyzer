"""Analysis session domain model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AnalysisSession:
    id: Optional[int]
    user_id: int
    resume_id: int
    jd_id: int
    similarity_score: float
    gap_report: str
    analyzed_at: Optional[datetime] = None
    missing_keywords: list | None = None
