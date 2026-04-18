"""Streamlit UI entry point."""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from config.settings import load_settings
from engine.semantic_engine import OpenAISemanticEngine
from models.job_description import JobDescription
from repository.db import Database
from repository.resume_repo import ResumeRepository
from repository.session_repo import AnalysisSessionRepository
from services.analyzer_service import ResumeAnalyzerService
from dotenv import load_dotenv
import os
load_dotenv()
os.getenv("DB_NAME")

def build_service() -> ResumeAnalyzerService:
    settings = load_settings()
    database = Database(settings["db"])
    resume_repo = ResumeRepository(database)
    session_repo = AnalysisSessionRepository(database)
    engine = OpenAISemanticEngine(
        api_key=settings["openai_api_key"],
        embedding_model=settings["embedding_model"],
        chat_model=settings["chat_model"],
    )
    return ResumeAnalyzerService(resume_repo, session_repo, engine)


def main() -> None:
    st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
    st.title("AI Resume Analyzer")
    st.write("Upload a resume and paste a job description to analyze fit.")

    service = build_service()

    uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
    jd_text = st.text_area("Job Description", height=200)
    jd_title = st.text_input("Job Title", value="Untitled Role")

    if st.button("Analyze"):
        if not uploaded_file or not jd_text.strip():
            st.error("Please upload a resume and provide a job description.")
            return

        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / uploaded_file.name
            file_path.write_bytes(uploaded_file.getbuffer())
            resume = service.parse_resume(str(file_path))
            job_description = JobDescription(id=None, title=jd_title, content=jd_text)

            result = service.analyze(resume, job_description, user_id=1)

        st.subheader("Match Report")
        st.metric("Score", f"{result.report.score:.1f}%")
        st.write("Missing Keywords")
        st.write(result.report.missing_keywords)
        st.write("Critique")
        st.write(result.report.critique)


if __name__ == "__main__":
    main()
