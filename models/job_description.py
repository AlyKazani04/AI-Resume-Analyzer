"""Job description domain model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class JobDescription:
    id: Optional[int]
    user_id: Optional[int]
    title: str
    content: str
    content_hash: Optional[str] = None
