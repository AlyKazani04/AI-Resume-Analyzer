"""User domain model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: Optional[int]
    name: str
    email: str
    password_hash: str
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
