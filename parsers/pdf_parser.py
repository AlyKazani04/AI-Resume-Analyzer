"""PDF parser implementation."""

from __future__ import annotations

from pathlib import Path

import pdfplumber

from parsers.base_parser import FileParser, ParseResult


class PDFParser(FileParser):
    """Extract text from PDF files using pdfplumber."""

    def extract_text(self, file_path: str) -> ParseResult:
        path = Path(file_path)
        with pdfplumber.open(path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        self.validate_text(text)
        return ParseResult(text=text, filename=path.name, file_type="pdf")
