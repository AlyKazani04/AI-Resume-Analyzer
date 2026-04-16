"""DOCX parser implementation."""

from __future__ import annotations

from pathlib import Path

import docx

from parsers.base_parser import FileParser, ParseResult


class DocxParser(FileParser):
    """Extract text from DOCX files using python-docx."""

    def extract_text(self, file_path: str) -> ParseResult:
        path = Path(file_path)
        document = docx.Document(path)
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        self.validate_text(text)
        return ParseResult(text=text, filename=path.name, file_type="docx")
