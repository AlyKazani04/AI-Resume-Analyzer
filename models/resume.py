"""Resume domain model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Resume:
    id: Optional[int]
    user_id: int
    filename: str
    content: str
    content_hash: Optional[str] = None
    file_type: Optional[str] = None
    uploaded_at: Optional[datetime] = None
