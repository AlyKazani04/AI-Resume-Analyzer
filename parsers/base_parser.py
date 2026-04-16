"""Abstract base class for file parsers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ParseResult:
    """Container for parsed file content and metadata."""

    text: str
    filename: str
    file_type: str


class FileParser(ABC):
    """Define a standard interface for file parsing."""

    @abstractmethod
    def extract_text(self, file_path: str) -> ParseResult:
        """Extract plain text from a file path."""
        raise NotImplementedError

    @staticmethod
    def validate_text(text: str) -> None:
        """Validate that extracted text is not empty."""
        if not text or not text.strip():
            raise ValueError("Parsed text is empty.")
