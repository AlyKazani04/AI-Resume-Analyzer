"""Service that ties parsing, AI, and persistence together."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

from engine.semantic_engine import MatchReport, OllamaSemanticEngine
from models.analysis_session import AnalysisSession
from models.job_description import JobDescription
from models.resume import Resume
from parsers.docx_parser import DocxParser
from parsers.pdf_parser import PDFParser
from repository.job_description_repo import JobDescriptionRepository
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
        jd_repo: JobDescriptionRepository,
        engine: OllamaSemanticEngine,
    ) -> None:
        self.resume_repo = resume_repo
        self.session_repo = session_repo
        self.jd_repo = jd_repo
        self.engine = engine
        self.pdf_parser = PDFParser()
        self.docx_parser = DocxParser()

    def parse_resume(self, file_path: str) -> Resume:
        """Parse a resume file into a Resume model."""
        if file_path.lower().endswith(".pdf"):
            parsed = self.pdf_parser.extract_text(file_path)
            file_type = "pdf"
        elif file_path.lower().endswith(".docx"):
            parsed = self.docx_parser.extract_text(file_path)
            file_type = "docx"
        else:
            raise ValueError("Unsupported file type. Use PDF or DOCX.")
        return Resume(
            id=None,
            user_id=0,
            filename=parsed.filename,
            content=parsed.text,
            content_hash=self._hash_content(parsed.text),
            file_type=file_type,
        )

    @staticmethod
    def _hash_content(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def analyze(
        self,
        resume: Resume,
        job_description: JobDescription,
        user_id: int | None,
        persist: bool = True,
    ) -> AnalysisResult:
        """Analyze resume vs job description and optionally persist results."""
        report = self.engine.gap_analysis(resume.content, job_description.content)
        score = self.engine.similarity_score(resume.content, job_description.content)

        resume_id = 0
        jd_id = job_description.id or 0

        if persist and user_id is not None:
            resume.user_id = user_id
            if not resume.content_hash:
                resume.content_hash = self._hash_content(resume.content)
            if not resume.file_type:
                resume.file_type = (
                    "pdf" if resume.filename.lower().endswith(".pdf") else "docx"
                )
            resume_id = self.resume_repo.create(resume)

            job_description.user_id = user_id
            if not job_description.content_hash:
                job_description.content_hash = self._hash_content(
                    job_description.content
                )
            jd_id = self.jd_repo.create(job_description)

            session = AnalysisSession(
                id=None,
                user_id=user_id,
                resume_id=resume_id,
                jd_id=jd_id,
                similarity_score=score,
                llm_score=report.score,
                gap_report=report.critique,
            )
            session.missing_keywords = report.missing_keywords

            session_id = self.session_repo.create(session)
            _ = session_id

        return AnalysisResult(resume_id=resume_id, jd_id=jd_id, report=report)
