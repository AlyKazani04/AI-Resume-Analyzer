"""Load environment configuration for the app."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from repository.db import DBConfig


def load_settings() -> dict:
    """Load environment variables and return settings."""
    load_dotenv()

    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
        "embedding_model": os.getenv(
            "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
        ),
        "chat_model": os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        "db": DBConfig(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "resume_analyzer"),
        ),
    }
