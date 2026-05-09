"""Load environment configuration for the app."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from repository.db import DBConfig


def load_settings() -> dict:
    """Load environment variables and return settings."""
    load_dotenv()

    return {
        "embedding_model": os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
        "chat_model": os.getenv("OLLAMA_CHAT_MODEL", "gemma3:latest"),
        "ollama_host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        "db": DBConfig(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "resume_analyzer"),
        ),
    }
