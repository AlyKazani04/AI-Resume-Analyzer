"""Service that ties parsing, AI, and persistence together."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from engine.semantic_engine import MatchReport, OllamaSemanticEngine
from models.analysis_session import AnalysisSession
from models.job_description import JobDescription
from models.resume import Resume
from parsers.docx_parser import DocxParser
from parsers.pdf_parser import PDFParser
from repository.resume_repo import ResumeRepository
from repository.session_repo import AnalysisSessionRepository


@dataclass
class AnalysisResult:
    resume_id: int
    jd_id: int
    report: MatchReport


class ResumeAnalyzerService:
    """Orchestrates parsing, analysis, and persistence."""

    def __init__(
        self,
        resume_repo: ResumeRepository,
        session_repo: AnalysisSessionRepository,
        engine: OllamaSemanticEngine,
    ) -> None:
        self.resume_repo = resume_repo
        self.session_repo = session_repo
        self.engine = engine
        self.pdf_parser = PDFParser()
        self.docx_parser = DocxParser()

    def parse_resume(self, file_path: str) -> Resume:
        """Parse a resume file into a Resume model."""
        if file_path.lower().endswith(".pdf"):
            parsed = self.pdf_parser.extract_text(file_path)
        elif file_path.lower().endswith(".docx"):
            parsed = self.docx_parser.extract_text(file_path)
        else:
            raise ValueError("Unsupported file type. Use PDF or DOCX.")
        return Resume(id=None, user_id=0, filename=parsed.filename, content=parsed.text)

    def analyze(
        self,
        resume: Resume,
        job_description: JobDescription,
        user_id: int,
    ) -> AnalysisResult:
        """Analyze resume vs job description and persist results."""
        resume.user_id = user_id
        resume_id = self.resume_repo.create(resume)

        report = self.engine.gap_analysis(resume.content, job_description.content)
        score = self.engine.similarity_score(resume.content, job_description.content)

        session = AnalysisSession(
            id=None,
            user_id=user_id,
            resume_id=resume_id,
            jd_id=job_description.id or 0,
            similarity_score=score,
            gap_report=report.critique,
        )
        session_id = self.session_repo.create(session)
        _ = session_id

        return AnalysisResult(
            resume_id=resume_id, jd_id=job_description.id or 0, report=report
        )
