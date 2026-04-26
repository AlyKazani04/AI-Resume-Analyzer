"""Streamlit UI entry point."""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from config.settings import load_settings
from engine.semantic_engine import OllamaSemanticEngine
from models.job_description import JobDescription
from repository.db import Database
from repository.job_description_repo import JobDescriptionRepository
from repository.resume_repo import ResumeRepository
from repository.session_repo import AnalysisSessionRepository
from repository.user_repo import UserRepository
from services.auth_service import AuthService
from services.analyzer_service import ResumeAnalyzerService
from dotenv import load_dotenv
import os

load_dotenv()
os.getenv("DB_NAME")


def inject_css() -> None:
    st.html(
        """
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
        <style>
        /* ── Base Reset ── */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0d0f14 !important;
            color: #e8eaf0 !important;
            font-family: 'DM Sans', sans-serif !important;
        }

        [data-testid="stSidebar"] { display: none; }
        [data-testid="stToolbar"] { display: none; }
        [data-testid="stDecoration"] { display: none; }
        footer { display: none; }
        #MainMenu { display: none; }

        /* ── Main container ── */
        .main .block-container {
            max-width: 860px !important;
            padding: 2.5rem 2rem 4rem 2rem !important;
            margin: 0 auto !important;
        }

        /* ── Hero Header ── */
        .hero-header {
            text-align: center;
            padding: 3.5rem 0 2.5rem 0;
            position: relative;
        }
        .hero-eyebrow {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            color: #2dd4a0;
            margin-bottom: 1rem;
            display: block;
        }
        .hero-title {
            font-family: 'Syne', sans-serif !important;
            font-size: clamp(2.4rem, 5vw, 3.6rem) !important;
            font-weight: 800 !important;
            line-height: 1.08 !important;
            letter-spacing: -0.03em !important;
            color: #f0f2f8 !important;
            margin: 0 0 1.1rem 0 !important;
        }
        .hero-title span {
            color: #2dd4a0;
        }
        .hero-subtitle {
            font-size: 1.05rem;
            color: #8891a8;
            font-weight: 400;
            max-width: 500px;
            margin: 0 auto;
            line-height: 1.65;
        }
        .hero-divider {
            width: 48px;
            height: 3px;
            background: linear-gradient(90deg, #2dd4a0, #1a9e74);
            border-radius: 2px;
            margin: 2rem auto 0 auto;
        }

        /* ── Section Label ── */
        .section-label {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: #2dd4a0;
            margin: 2.4rem 0 0.6rem 0;
            display: block;
        }

        /* ── Auth Card ── */
        .auth-card {
            background: #13161e;
            border: 1px solid #1e2330;
            border-radius: 16px;
            padding: 2.2rem 2rem;
            margin: 1.5rem 0;
        }

        /* ── Streamlit Tabs override ── */
        [data-testid="stTabs"] button {
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
            color: #8891a8 !important;
            border-bottom: 2px solid transparent !important;
            padding: 0.6rem 1.2rem !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stTabs"] button[aria-selected="true"] {
            color: #2dd4a0 !important;
            border-bottom-color: #2dd4a0 !important;
        }
        [data-testid="stTabs"] [role="tablist"] {
            border-bottom: 1px solid #1e2330 !important;
            gap: 0.2rem !important;
        }

        /* ── Input Fields ── */
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea {
            background: #0d0f14 !important;
            border: 1.5px solid #1e2330 !important;
            border-radius: 10px !important;
            color: #e8eaf0 !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.95rem !important;
            padding: 0.75rem 1rem !important;
            transition: border-color 0.2s ease !important;
        }
        [data-testid="stTextInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus {
            border-color: #2dd4a0 !important;
            box-shadow: 0 0 0 3px rgba(45, 212, 160, 0.08) !important;
        }
        [data-testid="stTextInput"] input::placeholder,
        [data-testid="stTextArea"] textarea::placeholder {
            color: #3d4558 !important;
        }
        [data-testid="stTextInput"] label,
        [data-testid="stTextArea"] label {
            color: #8891a8 !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            margin-bottom: 0.4rem !important;
        }

        /* ── File Uploader ── */
        [data-testid="stFileUploader"] {
            background: #13161e !important;
            border: 2px dashed #1e2330 !important;
            border-radius: 14px !important;
            transition: border-color 0.2s ease !important;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: #2dd4a0 !important;
        }
        [data-testid="stFileUploader"] label {
            color: #8891a8 !important;
            font-family: 'DM Sans', sans-serif !important;
        }
        [data-testid="stFileUploaderDropzoneInstructions"] {
            color: #5a6480 !important;
            font-family: 'DM Sans', sans-serif !important;
        }

        /* ── Primary Button ── */
        [data-testid="stButton"] button[kind="primary"],
        [data-testid="stButton"] > button {
            background: linear-gradient(135deg, #2dd4a0 0%, #1ab584 100%) !important;
            color: #0a0c10 !important;
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            letter-spacing: 0.01em !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.7rem 1.8rem !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 20px rgba(45, 212, 160, 0.2) !important;
        }
        [data-testid="stButton"] > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 28px rgba(45, 212, 160, 0.32) !important;
        }
        [data-testid="stButton"] > button:active {
            transform: translateY(0px) !important;
        }

        /* Logout button — muted style */
        .logout-btn [data-testid="stButton"] > button {
            background: transparent !important;
            color: #5a6480 !important;
            border: 1px solid #1e2330 !important;
            box-shadow: none !important;
            font-size: 0.82rem !important;
            padding: 0.4rem 1rem !important;
        }
        .logout-btn [data-testid="stButton"] > button:hover {
            color: #e8eaf0 !important;
            border-color: #3d4558 !important;
            transform: none !important;
            box-shadow: none !important;
        }

        /* ── Results Card ── */
        .result-card {
            background: #13161e;
            border: 1px solid #1e2330;
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
        }
        .result-card-header {
            font-family: 'Syne', sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            color: #f0f2f8;
            margin-bottom: 1.2rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* ── Score Ring ── */
        .score-container {
            display: flex;
            align-items: center;
            gap: 2rem;
            background: #0d0f14;
            border: 1px solid #1e2330;
            border-radius: 14px;
            padding: 1.8rem 2rem;
            margin: 1.5rem 0;
        }
        .score-ring-wrap {
            position: relative;
            width: 110px;
            height: 110px;
            flex-shrink: 0;
        }
        .score-ring-wrap svg {
            transform: rotate(-90deg);
        }
        .score-number {
            position: absolute;
            inset: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: 'Syne', sans-serif;
            font-size: 1.6rem;
            font-weight: 800;
            color: #2dd4a0;
            line-height: 1;
        }
        .score-number small {
            font-size: 0.7rem;
            color: #5a6480;
            font-family: 'DM Sans', sans-serif;
            font-weight: 500;
            margin-top: 2px;
        }
        .score-meta {
            flex: 1;
        }
        .score-label {
            font-family: 'Syne', sans-serif;
            font-size: 1.3rem;
            font-weight: 700;
            color: #f0f2f8;
            margin-bottom: 0.35rem;
        }
        .score-desc {
            font-size: 0.9rem;
            color: #8891a8;
            line-height: 1.55;
        }

        /* ── Keyword Pills ── */
        .keyword-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.8rem;
        }
        .keyword-pill {
            background: rgba(220, 60, 60, 0.1);
            border: 1px solid rgba(220, 60, 60, 0.25);
            color: #f08080;
            font-family: 'DM Sans', sans-serif;
            font-size: 0.8rem;
            font-weight: 500;
            padding: 0.28rem 0.75rem;
            border-radius: 100px;
        }

        /* ── Critique Block ── */
        .critique-text {
            font-size: 0.95rem;
            color: #b0bac8;
            line-height: 1.75;
            border-left: 3px solid #2dd4a0;
            padding-left: 1.2rem;
            margin-top: 0.8rem;
        }

        /* ── Alert / Message overrides ── */
        [data-testid="stAlert"] {
            border-radius: 10px !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.9rem !important;
        }

        /* ── Metric override ── */
        [data-testid="stMetric"] {
            background: #13161e !important;
            border: 1px solid #1e2330 !important;
            border-radius: 12px !important;
            padding: 1.2rem 1.5rem !important;
        }
        [data-testid="stMetricLabel"] {
            color: #8891a8 !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.8rem !important;
        }
        [data-testid="stMetricValue"] {
            color: #2dd4a0 !important;
            font-family: 'Syne', sans-serif !important;
            font-size: 2rem !important;
            font-weight: 800 !important;
        }

        /* ── Spinner ── */
        [data-testid="stSpinner"] {
            font-family: 'DM Sans', sans-serif !important;
            color: #8891a8 !important;
        }

        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: #0d0f14; }
        ::-webkit-scrollbar-thumb { background: #1e2330; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #2dd4a0; }

        /* ── Separator ── */
        hr {
            border: none !important;
            border-top: 1px solid #1e2330 !important;
            margin: 2rem 0 !important;
        }

        /* ── User badge ── */
        .user-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: #13161e;
            border: 1px solid #1e2330;
            border-radius: 100px;
            padding: 0.35rem 1rem 0.35rem 0.5rem;
            font-size: 0.82rem;
            color: #8891a8;
            font-family: 'DM Sans', sans-serif;
            margin-bottom: 1.5rem;
        }
        .user-badge-dot {
            width: 8px;
            height: 8px;
            background: #2dd4a0;
            border-radius: 50%;
        }
        </style>
        """
    )


def score_label(score: float) -> str:
    if score >= 80:
        return "Excellent Match"
    elif score >= 60:
        return "Good Match"
    elif score >= 40:
        return "Moderate Match"
    else:
        return "Low Match"


def score_description(score: float) -> str:
    if score >= 80:
        return (
            "Your resume strongly aligns with this role. You're a compelling candidate."
        )
    elif score >= 60:
        return "Solid alignment. A few targeted tweaks could make you a top applicant."
    elif score >= 40:
        return "There's a reasonable fit, but several key gaps need to be addressed."
    else:
        return (
            "Significant gaps detected. Consider tailoring your resume for this role."
        )


def render_score_card(score: float) -> None:
    pct = min(max(score, 0), 100)
    circumference = 2 * 3.14159 * 44
    dash = (pct / 100) * circumference
    gap = circumference - dash

    if pct >= 80:
        color = "#2dd4a0"
    elif pct >= 60:
        color = "#f5c842"
    elif pct >= 40:
        color = "#f0955a"
    else:
        color = "#e05c5c"

    st.markdown(
        f"""
        <div class="score-container">
            <div class="score-ring-wrap">
                <svg width="110" height="110" viewBox="0 0 110 110">
                    <circle cx="55" cy="55" r="44" fill="none" stroke="#1e2330" stroke-width="9"/>
                    <circle cx="55" cy="55" r="44" fill="none" stroke="{color}" stroke-width="9"
                        stroke-dasharray="{dash:.1f} {gap:.1f}"
                        stroke-linecap="round"/>
                </svg>
                <div class="score-number">
                    {pct:.0f}<small>/ 100</small>
                </div>
            </div>
            <div class="score-meta">
                <div class="score-label">{score_label(pct)}</div>
                <div class="score-desc">{score_description(pct)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_keywords(keywords: list | str) -> None:
    if isinstance(keywords, str):
        items = [
            k.strip() for k in keywords.replace(",", "\n").splitlines() if k.strip()
        ]
    elif isinstance(keywords, list):
        items = [str(k).strip() for k in keywords if str(k).strip()]
    else:
        items = []

    if not items:
        st.markdown(
            '<p style="color:#5a6480;font-size:0.9rem;">No missing keywords detected.</p>',
            unsafe_allow_html=True,
        )
        return

    pills = "".join(f'<span class="keyword-pill">{k}</span>' for k in items)
    st.markdown(f'<div class="keyword-grid">{pills}</div>', unsafe_allow_html=True)


def build_services() -> tuple[ResumeAnalyzerService, AuthService]:
    settings = load_settings()

    database = Database(settings["db"])

    resume_repo = ResumeRepository(database)
    session_repo = AnalysisSessionRepository(database)
    user_repo = UserRepository(database)

    jd_repo = JobDescriptionRepository(database)

    engine = OllamaSemanticEngine(
        embedding_model=settings["embedding_model"],
        chat_model=settings["chat_model"],
        host=settings["ollama_host"],
    )

    analyzer = ResumeAnalyzerService(resume_repo, session_repo, jd_repo, engine)

    auth = AuthService(user_repo)

    return analyzer, auth


def main() -> None:
    st.set_page_config(
        page_title="AI Resume Analyzer",
        page_icon="📄",
        layout="centered",
    )
    inject_css()

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="hero-header">
            <span class="hero-eyebrow">Powered by AI</span>
            <h1 class="hero-title">Resume <span>Analyzer</span></h1>
            <p class="hero-subtitle">
                Upload your resume and a job description. Get an instant match score,
                missing keywords, and actionable feedback.
            </p>
            <div class="hero-divider"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    analyzer, auth = build_services()

    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "guest_mode" not in st.session_state:
        st.session_state.guest_mode = False

    # ── Auth ──────────────────────────────────────────────────────────────────
    if st.session_state.user_id is None and not st.session_state.guest_mode:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        login_tab, register_tab, guest_tab = st.tabs(["Login", "Register", "Guest"])

        with login_tab:
            st.markdown(
                '<span class="section-label">Email</span>', unsafe_allow_html=True
            )
            login_email = st.text_input(
                " ",
                key="login_email",
                label_visibility="collapsed",
                placeholder="you@example.com",
            )
            st.markdown(
                '<span class="section-label">Password</span>', unsafe_allow_html=True
            )
            login_password = st.text_input(
                " ",
                type="password",
                key="login_pw",
                label_visibility="collapsed",
                placeholder="••••••••",
            )
            if st.button("Login", key="btn_login"):
                user = auth.authenticate_user(login_email, login_password)
                if user:
                    st.session_state.user_id = user.id
                    st.session_state.guest_mode = False
                    st.success("Welcome back!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        with register_tab:
            st.markdown(
                '<span class="section-label">Full Name</span>', unsafe_allow_html=True
            )
            reg_name = st.text_input(
                " ",
                key="reg_name",
                label_visibility="collapsed",
                placeholder="Jane Doe",
            )
            st.markdown(
                '<span class="section-label">Email</span>', unsafe_allow_html=True
            )
            reg_email = st.text_input(
                " ",
                key="reg_email",
                label_visibility="collapsed",
                placeholder="you@example.com",
            )
            st.markdown(
                '<span class="section-label">Password</span>', unsafe_allow_html=True
            )
            reg_password = st.text_input(
                " ",
                type="password",
                key="reg_pw",
                label_visibility="collapsed",
                placeholder="Choose a strong password",
            )
            if st.button("Create Account", key="btn_register"):
                if not reg_name or not reg_email or not reg_password:
                    st.error("Please fill in all fields.")
                else:
                    user_id = auth.register_user(reg_name, reg_email, reg_password)
                    st.session_state.user_id = user_id
                    st.session_state.guest_mode = False
                    st.success("Account created. You are now logged in.")
                    st.rerun()

        with guest_tab:
            st.markdown(
                '<p style="color:#8891a8;font-size:0.92rem;line-height:1.65;margin-bottom:1.2rem;">'
                "Continue without an account. Your analysis won't be saved to the database."
                "</p>",
                unsafe_allow_html=True,
            )
            if st.button("Continue as Guest", key="btn_guest"):
                st.session_state.guest_mode = True
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    # ── Logged-in user bar ────────────────────────────────────────────────────
    top_left, top_right = st.columns([5, 1])
    with top_left:
        label = "Guest Session" if st.session_state.guest_mode else f"Signed in"
        st.markdown(
            f'<div class="user-badge"><div class="user-badge-dot"></div>{label}</div>',
            unsafe_allow_html=True,
        )
    with top_right:
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.user_id = None
            st.session_state.guest_mode = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Upload ────────────────────────────────────────────────────────────────
    st.markdown('<span class="section-label">Resume</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        " ",
        type=["pdf", "docx"],
        label_visibility="collapsed",
        help="Supported formats: PDF, DOCX",
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            '<span class="section-label">Job Description</span>', unsafe_allow_html=True
        )
        jd_text = st.text_area(
            " ",
            placeholder="Paste the job description here…",
            height=220,
            label_visibility="collapsed",
        )
    with col2:
        st.markdown(
            '<span class="section-label">Job Title</span>', unsafe_allow_html=True
        )
        jd_title = st.text_input(
            " ",
            placeholder="e.g. Senior Backend Engineer",
            label_visibility="collapsed",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    analyze_clicked = st.button("✦  Analyze Resume", key="btn_analyze")

    # ── Analysis ──────────────────────────────────────────────────────────────
    if analyze_clicked:
        if not uploaded_file or not jd_text.strip():
            st.error("Please upload a resume and provide a job description.")
            return

        with st.spinner("Analyzing your resume…"):
            with tempfile.TemporaryDirectory() as tmp_dir:
                file_path = Path(tmp_dir) / uploaded_file.name
                file_path.write_bytes(uploaded_file.getbuffer())
                resume = analyzer.parse_resume(str(file_path))
                job_description = JobDescription(
                    id=None,
                    user_id=None,
                    title=jd_title or "Untitled Role",
                    content=jd_text,
                )
                persist = st.session_state.user_id is not None
                result = analyzer.analyze(
                    resume,
                    job_description,
                    user_id=st.session_state.user_id,
                    persist=persist,
                )

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown(
            "<h2 style=\"font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;"
            'color:#f0f2f8;margin:0 0 0.2rem 0;">Match Report</h2>'
            f'<p style="color:#5a6480;font-size:0.85rem;margin:0 0 1.5rem 0;">For: {jd_title or "Untitled Role"}</p>',
            unsafe_allow_html=True,
        )

        # Score card
        render_score_card(result.report.score)

        # Missing keywords
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="result-card-header">⚠ Missing Keywords</div>',
            unsafe_allow_html=True,
        )
        render_keywords(result.report.missing_keywords)
        st.markdown("</div>", unsafe_allow_html=True)

        # Critique
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="result-card-header">🔍 AI Critique</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="critique-text">{result.report.critique}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
