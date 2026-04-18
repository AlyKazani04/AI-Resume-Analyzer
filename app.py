"""Streamlit UI entry point."""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from config.settings import load_settings
from engine.semantic_engine import OllamaSemanticEngine
from models.job_description import JobDescription
from repository.db import Database
from repository.resume_repo import ResumeRepository
from repository.session_repo import AnalysisSessionRepository
from repository.user_repo import UserRepository
from services.auth_service import AuthService
from services.analyzer_service import ResumeAnalyzerService


def build_services() -> tuple[ResumeAnalyzerService, AuthService]:
    settings = load_settings()
    database = Database(settings["db"])
    resume_repo = ResumeRepository(database)
    session_repo = AnalysisSessionRepository(database)
    user_repo = UserRepository(database)
    engine = OllamaSemanticEngine(
        embedding_model=settings["embedding_model"],
        chat_model=settings["chat_model"],
        host=settings["ollama_host"],
    )
    analyzer = ResumeAnalyzerService(resume_repo, session_repo, engine)
    auth = AuthService(user_repo)
    return analyzer, auth


def main() -> None:
    st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
    st.title("AI Resume Analyzer")
    st.write("Upload a resume and paste a job description to analyze fit.")

    analyzer, auth = build_services()

    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "guest_mode" not in st.session_state:
        st.session_state.guest_mode = False

    if st.session_state.user_id is None and not st.session_state.guest_mode:
        st.subheader("Login or Register")
        login_tab, register_tab, guest_tab = st.tabs(
            ["Login", "Register", "Continue as Guest"]
        )

        with login_tab:
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_pw")
            if st.button("Login"):
                user = auth.authenticate_user(login_email, login_password)
                if user:
                    st.session_state.user_id = user.id
                    st.session_state.guest_mode = False
                    st.success("Logged in successfully.")
                else:
                    st.error("Invalid email or password.")

        with register_tab:
            reg_name = st.text_input("Name", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_pw")
            if st.button("Register"):
                if not reg_name or not reg_email or not reg_password:
                    st.error("Please provide name, email, and password.")
                else:
                    user_id = auth.register_user(reg_name, reg_email, reg_password)
                    st.session_state.user_id = user_id
                    st.session_state.guest_mode = False
                    st.success("Account created. You are now logged in.")

        with guest_tab:
            st.write("Continue without saving your analysis to the database.")
            if st.button("Continue as Guest"):
                st.session_state.guest_mode = True

        st.stop()

    if st.session_state.user_id is not None:
        if st.button("Logout"):
            st.session_state.user_id = None
            st.session_state.guest_mode = False
            st.success("Logged out.")
            st.stop()

    uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
    jd_text = st.text_area("Job Description", placeholder="Paste the job description here.", height=200)
    jd_title = st.text_input("Job Title", placeholder="Untitled Role")

    if st.button("Analyze"):
        if not uploaded_file or not jd_text.strip():
            st.error("Please upload a resume and provide a job description.")
            return

        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / uploaded_file.name
            file_path.write_bytes(uploaded_file.getbuffer())
            resume = analyzer.parse_resume(str(file_path))
            job_description = JobDescription(id=None, title=jd_title, content=jd_text)
            persist = st.session_state.user_id is not None
            result = analyzer.analyze(
                resume,
                job_description,
                user_id=st.session_state.user_id,
                persist=persist,
            )

        st.subheader("Match Report")
        st.metric("Score", f"{result.report.score:.1f}%")
        st.write("Missing Keywords")
        st.write(result.report.missing_keywords)
        st.write("Critique")
        st.write(result.report.critique)


if __name__ == "__main__":
    main()
