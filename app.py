"""Streamlit UI entry point."""

from __future__ import annotations

import tempfile
import time
from pathlib import Path

from repository import user_repo
import streamlit as st

from config.settings import load_settings
from engine.semantic_engine import OllamaSemanticEngine
from models.job_description import JobDescription
from repository.db import Database
from repository.resume_repo import ResumeRepository
from repository.session_repo import AnalysisSessionRepository
from repository.user_repo import UserRepository
from repository.job_description_repo import JobDescriptionRepository
from services.auth_service import AuthService
from services.analyzer_service import ResumeAnalyzerService
from dotenv import load_dotenv
import os

load_dotenv()


# ── CSS ───────────────────────────────────────────────────────────────────────


def inject_css() -> None:
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

    /* ── Base ── */
    [data-testid="stAppViewContainer"] {
        background-color: #0a0f1e !important;
        color: #e2e8f0 !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    /* ── Nav button fix — no text wrapping ── */
    [data-testid="stButton"] > button {
        white-space: nowrap !important;
        min-width: fit-content !important;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 840px !important;
        padding: 2rem 2rem 5rem 2rem !important;
        margin: 0 auto !important;
    }

    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    footer { display: none !important; }


    /* ── Hero ── */
    .hero-header {
        text-align: center;
        padding: 3.2rem 0 2rem 0;
        justify-content: center;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .hero-eyebrow {
        font-size: 0.67rem; font-weight: 600; letter-spacing: 0.22em;
        text-transform: uppercase; color: #60a5fa; display: block; margin-bottom: 0.8rem;
    }
    .hero-title {
        font-family: 'Syne', sans-serif !important;
        font-size: clamp(2.2rem, 5vw, 3.4rem) !important;
        font-weight: 800 !important; line-height: 1.08 !important;
        letter-spacing: -0.03em !important; color: #f0f6ff !important;
        margin: 0 0 1rem 0 !important;
    }
    .hero-title span { color: #3b82f6; }
    .hero-subtitle {
        text-align: center;
        font-size: 1rem; color: #94a3b8;
        max-width: 480px; margin: 0 auto; line-height: 1.65;
    }
    .hero-divider {
        width: 44px; height: 3px;
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
        border-radius: 2px; margin: 1.8rem auto 0;
    }

    /* ── Nav ── */
    .nav-logo {
        font-family: 'Syne', sans-serif; font-size: 1.1rem;
        font-weight: 800; color: #f0f6ff; letter-spacing: -0.02em; padding: 0.35rem 0;
    }
    .nav-logo span { color: #3b82f6; }
    .nav-badge {
        display: inline-flex; align-items: center; gap: 0.4rem;
        background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.3);
        border-radius: 100px; padding: 0.28rem 0.85rem 0.28rem 0.5rem;
        font-size: 0.75rem; color: #93c5fd; font-weight: 500; margin-top: 0.3rem;
    }
    .nav-dot {
        width: 7px; height: 7px; background: #3b82f6;
        border-radius: 50%; display: inline-block;
    }

    /* ── Section label ── */
    .section-label {
        font-size: 0.64rem; font-weight: 600; letter-spacing: 0.2em;
        text-transform: uppercase; color: #60a5fa;
        display: block; margin-bottom: 0.45rem; margin-top: 0.3rem;
    }

    /* ── Cards ── */
    .auth-card {
        background: #0f172a; border: 1px solid #1e3a5f;
        border-radius: 16px; padding: 2rem 2rem 1.5rem;
        margin: 1.5rem 0; box-shadow: 0 4px 24px rgba(0,0,0,0.35);
    }
    .result-card {
        background: #0f172a; border: 1px solid #1e3a5f;
        border-radius: 14px; padding: 1.6rem; margin: 1rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.25);
    }
    .result-card-header {
        font-family: 'Syne', sans-serif; font-size: 1rem;
        font-weight: 700; color: #e2e8f0; margin-bottom: 1rem;
    }

    /* ── Tabs ── */
    [data-testid="stTabs"] button {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important; font-size: 0.88rem !important;
        color: #64748b !important;
        border-bottom: 2px solid transparent !important;
        padding: 0.55rem 1.1rem !important;
        background: transparent !important;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #60a5fa !important; border-bottom-color: #3b82f6 !important;
    }
    [data-testid="stTabs"] [role="tablist"] {
        border-bottom: 1px solid #1e3a5f !important; gap: 0 !important;
    }

    /* ── Inputs — FIXED cursor visibility ── */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background: #111827 !important;
        border: 1.5px solid #1e3a5f !important;
        border-radius: 10px !important;
        color: #f0f6ff !important;
        caret-color: #60a5fa !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.93rem !important;
        padding: 0.72rem 1rem !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
        outline: none !important;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {
        color: #334155 !important;
    }
    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label {
        color: #64748b !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.83rem !important; font-weight: 500 !important;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background: #111827 !important;
        border: 2px dashed #1e3a5f !important;
        border-radius: 14px !important;
    }
    [data-testid="stFileUploader"]:hover { border-color: #3b82f6 !important; }
    [data-testid="stFileUploaderDropzoneInstructions"] { color: #475569 !important; }

    /* ── Primary button ── */
    [data-testid="stButton"] > button {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
        color: #ffffff !important;
        font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
        font-size: 0.93rem !important; border: none !important;
        border-radius: 10px !important; padding: 0.68rem 1.8rem !important;
        box-shadow: 0 2px 16px rgba(59,130,246,0.28) !important;
        transition: all 0.2s ease !important; cursor: pointer !important;
    }
    [data-testid="stButton"] > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
        box-shadow: 0 4px 24px rgba(59,130,246,0.42) !important;
        transform: translateY(-1px) !important;
    }

    /* Ghost button */
    .ghost-btn [data-testid="stButton"] > button {
        background: transparent !important; color: #60a5fa !important;
        border: 1.5px solid #1e3a5f !important;
        box-shadow: none !important;
    }
    .ghost-btn [data-testid="stButton"] > button:hover {
        background: rgba(59,130,246,0.08) !important;
        border-color: #3b82f6 !important;
        transform: none !important; box-shadow: none !important;
    }

    /* Logout button */
    .logout-btn [data-testid="stButton"] > button {
        background: transparent !important; color: #475569 !important;
        border: 1px solid #1e293b !important;
        box-shadow: none !important;
        font-size: 0.79rem !important; padding: 0.32rem 0.85rem !important;
    }
    .logout-btn [data-testid="stButton"] > button:hover {
        color: #e2e8f0 !important; border-color: #334155 !important;
        background: #1e293b !important; transform: none !important;
        box-shadow: none !important;
    }

    /* ── Score ring ── */
    .score-container {
        display: flex; align-items: center; gap: 2rem;
        background: linear-gradient(135deg, #0f172a 0%, #0d1b2e 100%);
        border: 1px solid #1e3a5f; border-radius: 16px;
        padding: 2rem; margin: 1rem 0;
        box-shadow: inset 0 1px 0 rgba(59,130,246,0.1);
    }
    .score-ring-wrap { position: relative; width: 115px; height: 115px; flex-shrink: 0; }
    .score-ring-wrap svg { transform: rotate(-90deg); }
    .score-number {
        position: absolute; inset: 0; display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        font-family: 'Syne', sans-serif; font-size: 1.75rem;
        font-weight: 800; color: #60a5fa; line-height: 1;
    }
    .score-number small {
        font-size: 0.62rem; color: #475569;
        font-family: 'DM Sans', sans-serif; margin-top: 3px;
    }
    .score-label {
        font-family: 'Syne', sans-serif; font-size: 1.2rem;
        font-weight: 700; color: #f0f6ff; margin-bottom: 0.3rem;
    }
    .score-desc { font-size: 0.88rem; color: #94a3b8; line-height: 1.6; }

    /* ── Keyword pills ── */
    .keyword-grid { display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.6rem; }
    .keyword-pill {
        background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.25);
        color: #fca5a5; font-size: 0.78rem; font-weight: 500;
        padding: 0.25rem 0.72rem; border-radius: 100px;
    }

    /* ── Critique ── */
    .critique-wrap {
        border-left: 3px solid #3b82f6;
        padding-left: 1.1rem; margin-top: 0.6rem;
        color: #94a3b8; font-size: 0.93rem; line-height: 1.75;
    }

    /* ── Info strip ── */
    .info-strip {
        background: rgba(59,130,246,0.07);
        border: 1px solid rgba(59,130,246,0.2);
        border-radius: 10px; padding: 0.7rem 1rem; margin: 0.8rem 0;
        font-size: 0.81rem; color: #93c5fd; line-height: 1.5;
    }

    /* ── Session rows ── */
    .session-row {
        display: flex; align-items: center; justify-content: space-between;
        padding: 1rem 1.3rem; background: #0f172a;
        border: 1px solid #1e3a5f; border-radius: 12px; margin-bottom: 0.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.2);
    }
    .session-score {
        font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 800;
    }
    .session-date { font-size: 0.75rem; color: #475569; margin-top: 0.1rem; }
    .session-badge {
        font-size: 0.71rem; font-weight: 600;
        padding: 0.2rem 0.65rem; border-radius: 100px;
    }

    /* ── Page titles ── */
    .page-title {
        font-family: 'Syne', sans-serif; font-size: 1.55rem;
        font-weight: 800; color: #f0f6ff; margin: 0 0 0.2rem 0;
    }
    .page-sub { color: #64748b; font-size: 0.87rem; margin: 0 0 1.4rem 0; }

    /* ── Misc ── */
    hr { border: none !important; border-top: 1px solid #1e293b !important; margin: 1.4rem 0 !important; }
    [data-testid="stAlert"] { border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important; }
    [data-testid="stSpinner"] > div { color: #64748b !important; }
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: #0a0f1e; }
    ::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #3b82f6; }
    </style>
    """,
        unsafe_allow_html=True,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────


def score_color(score: float) -> str:
    if score >= 80:
        return "#22c55e"
    elif score >= 60:
        return "#3b82f6"
    elif score >= 40:
        return "#f59e0b"
    else:
        return "#ef4444"


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
        return "Solid alignment. A few targeted tweaks could make you stand out."
    elif score >= 40:
        return "Reasonable fit, but several key gaps need to be addressed."
    else:
        return (
            "Significant gaps detected. Consider tailoring your resume for this role."
        )


def stream_text(text: str):
    for word in text.split():
        yield word + " "
        time.sleep(0.03)


def render_score_card(score: float) -> None:
    pct = min(max(score, 0), 100)
    circumference = 2 * 3.14159 * 46
    dash = (pct / 100) * circumference
    gap = circumference - dash
    color = score_color(pct)
    st.markdown(
        f"""
    <div class="score-container">
        <div class="score-ring-wrap">
            <svg width="115" height="115" viewBox="0 0 115 115">
                <circle cx="57.5" cy="57.5" r="46" fill="none" stroke="#1e293b" stroke-width="9"/>
                <circle cx="57.5" cy="57.5" r="46" fill="none" stroke="{color}" stroke-width="9"
                    stroke-dasharray="{dash:.1f} {gap:.1f}" stroke-linecap="round"/>
            </svg>
            <div class="score-number">{pct:.0f}<small>/ 100</small></div>
        </div>
        <div>
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
            '<p style="color:#475569;font-size:0.88rem;">No missing keywords detected.</p>',
            unsafe_allow_html=True,
        )
        return
    pills = "".join(f'<span class="keyword-pill">{k}</span>' for k in items)
    st.markdown(f'<div class="keyword-grid">{pills}</div>', unsafe_allow_html=True)


def session_badge_html(score: float) -> str:
    if score >= 80:
        return '<span class="session-badge" style="background:rgba(34,197,94,0.12);color:#86efac;">Excellent</span>'
    elif score >= 60:
        return '<span class="session-badge" style="background:rgba(59,130,246,0.12);color:#93c5fd;">Good</span>'
    elif score >= 40:
        return '<span class="session-badge" style="background:rgba(245,158,11,0.12);color:#fcd34d;">Moderate</span>'
    else:
        return '<span class="session-badge" style="background:rgba(239,68,68,0.12);color:#fca5a5;">Low</span>'


# ── Nav ───────────────────────────────────────────────────────────────────────


def render_nav() -> None:
    label = "Guest Session" if st.session_state.guest_mode else "Signed in"
    c1, c2, c3, c4 = st.columns([3, 2.5, 1, 1])
    with c1:
        st.markdown('<div class="nav-logo">Resume<span>AI</span></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="nav-badge"><span class="nav-dot"></span>{label}</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("History", key="nav_history"):
            st.session_state.page = "sessions"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Logout", key="nav_logout"):
            st.session_state.user_id = None
            st.session_state.guest_mode = False
            st.session_state.page = "auth"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)


# ── Pages ─────────────────────────────────────────────────────────────────────


def page_auth(auth: AuthService) -> None:
    st.markdown(
        """
    <div class="hero-header">
        <span class="hero-eyebrow">AI-Powered Career Tool</span>
        <h1 class="hero-title">Resume <span>Analyzer</span></h1>
        <p class="hero-subtitle">
            Match your resume to any job description instantly.
            Get a score, missing keywords, and AI-written feedback.
        </p>
        <div class="hero-divider"></div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    login_tab, register_tab, guest_tab = st.tabs(["Login", "Register", "Guest"])

    with login_tab:
        st.markdown('<span class="section-label">Email</span>', unsafe_allow_html=True)
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
        if st.button("Login →", key="btn_login"):
            user = auth.authenticate_user(login_email, login_password)
            if user:
                st.session_state.user_id = user.id
                st.session_state.guest_mode = False
                st.session_state.page = "analyze"
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with register_tab:
        st.markdown(
            '<span class="section-label">Full Name</span>', unsafe_allow_html=True
        )
        reg_name = st.text_input(
            " ", key="reg_name", label_visibility="collapsed", placeholder="Jane Doe"
        )
        st.markdown('<span class="section-label">Email</span>', unsafe_allow_html=True)
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
        if st.button("Create Account →", key="btn_register"):
            if not reg_name or not reg_email or not reg_password:
                st.error("Please fill in all fields.")
            else:
                user_id = auth.register_user(reg_name, reg_email, reg_password)
                st.session_state.user_id = user_id
                st.session_state.guest_mode = False
                st.session_state.page = "analyze"
                st.rerun()

    with guest_tab:
        st.markdown(
            '<p style="color:#64748b;font-size:0.9rem;line-height:1.65;margin-bottom:1rem;">'
            "Continue without an account. Your analysis won't be saved to history.</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="info-strip">⚡ Guest sessions are temporary and won\'t appear in history.</div>',
            unsafe_allow_html=True,
        )
        if st.button("Continue as Guest →", key="btn_guest"):
            st.session_state.guest_mode = True
            st.session_state.page = "analyze"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def page_analyze(analyzer: ResumeAnalyzerService) -> None:
    render_nav()
    st.markdown(
        '<h2 class="page-title">Analyze your Resume</h2>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="page-sub">Upload your resume and paste a job description to get your match report.</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<span class="section-label">Resume — PDF or DOCX</span>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        " ", type=["pdf", "docx"], label_visibility="collapsed"
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            '<span class="section-label">Job Description</span>', unsafe_allow_html=True
        )
        jd_text = st.text_area(
            " ",
            placeholder="Paste the full job description here…",
            height=210,
            label_visibility="collapsed",
        )
    with col2:
        st.markdown(
            '<span class="section-label">Job Title</span>', unsafe_allow_html=True
        )
        jd_title = st.text_input(
            " ", placeholder="e.g. Product Manager", label_visibility="collapsed"
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.session_state.guest_mode:
            st.markdown(
                '<div class="info-strip">⚡ Results won\'t be saved in guest mode.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="info-strip">💾 Results will be saved to your history.</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("✦  Analyze Resume", key="btn_analyze"):
        if not uploaded_file or not jd_text.strip():
            st.error("Please upload a resume and provide a job description.")
            return

        with st.spinner("Analyzing your resume… this may take a moment."):
            try:
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
                st.session_state.result = result
                st.session_state.jd_title = jd_title or "Untitled Role"
                st.session_state.page = "results"
                st.rerun()
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                st.info(
                    "Make sure Ollama is running (`ollama serve`) and models are pulled."
                )


def page_results() -> None:
    render_nav()
    result = st.session_state.get("result")
    jd_title = st.session_state.get("jd_title", "Untitled Role")

    if result is None:
        st.warning("No results found. Please run an analysis first.")
        if st.button("← Back to Analyzer"):
            st.session_state.page = "analyze"
            st.rerun()
        return

    st.markdown('<h2 class="page-title">Match Report</h2>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="page-sub">Role: <strong style="color:#93c5fd;">{jd_title}</strong></p>',
        unsafe_allow_html=True,
    )

    render_score_card(result.report.score)

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="result-card-header">⚠ Missing Keywords</div>',
        unsafe_allow_html=True,
    )
    render_keywords(result.report.missing_keywords)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="result-card-header">🔍 AI Critique</div>', unsafe_allow_html=True
    )
    st.markdown('<div class="critique-wrap">', unsafe_allow_html=True)
    st.write_stream(stream_text(result.report.critique))
    st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("← Analyze Another", key="back_analyze"):
            st.session_state.result = None
            st.session_state.page = "analyze"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        if st.session_state.user_id is not None:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("View History →", key="go_sessions"):
                st.session_state.page = "sessions"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def page_sessions(session_repo: AnalysisSessionRepository) -> None:
    render_nav()
    st.markdown('<h2 class="page-title">Analysis History</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">All your past resume analyses, newest first.</p>',
        unsafe_allow_html=True,
    )

    user_id = st.session_state.user_id
    if user_id is None:
        st.markdown(
            '<div class="info-strip">⚡ History is only available for registered users.</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button("← Back"):
            st.session_state.page = "analyze"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    try:
        sessions = list(session_repo.list_by_user(user_id))
    except Exception as e:
        st.error(f"Could not load sessions: {e}")
        return

    if not sessions:
        st.markdown(
            '<div class="info-strip">📂 No sessions yet. Run your first analysis to see results here.</div>',
            unsafe_allow_html=True,
        )
    else:
        for s in sessions:
            score = s.similarity_score
            color = score_color(score)
            date_str = (
                s.analyzed_at.strftime("%b %d, %Y  %H:%M") if s.analyzed_at else "—"
            )
            badge = session_badge_html(score)
            st.markdown(
                f"""
            <div class="session-row">
                <div>
                    <div style="font-size:0.87rem;font-weight:600;color:#e2e8f0;">Session #{s.id}</div>
                    <div class="session-date">{date_str}</div>
                </div>
                <div style="display:flex;align-items:center;gap:1rem;">
                    {badge}
                    <div class="session-score" style="color:{color};">{score:.1f}%</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<p style="color:#334155;font-size:0.75rem;margin-top:0.6rem;">{len(sessions)} session(s) total</p>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("← New Analysis", key="back_from_sessions"):
        st.session_state.page = "analyze"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ── Services ──────────────────────────────────────────────────────────────────


def build_services() -> tuple[ResumeAnalyzerService, AuthService]:
    settings = load_settings()
    database = Database(settings["db"])
    resume_repo = ResumeRepository(database)
    session_repo = AnalysisSessionRepository(database)
    user_repo = UserRepository(database)
    # ── FIXED: added jd_repo which teammates added in their update ──
    jd_repo = JobDescriptionRepository(database)
    engine = OllamaSemanticEngine(
        embedding_model=settings["embedding_model"],
        chat_model=settings["chat_model"],
        host=settings["ollama_host"],
    )
    analyzer = ResumeAnalyzerService(resume_repo, session_repo, jd_repo, engine)
    auth = AuthService(user_repo)
    return analyzer, auth


# ── Entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    st.set_page_config(
        page_title="AI Resume Analyzer", page_icon="📄", layout="centered"
    )
    inject_css()

    for key, default in [
        ("user_id", None),
        ("guest_mode", False),
        ("page", "auth"),
        ("result", None),
        ("jd_title", ""),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    if st.session_state.page == "auth" and (
        st.session_state.user_id or st.session_state.guest_mode
    ):
        st.session_state.page = "analyze"

    try:
        analyzer, auth = build_services()
        session_repo = analyzer.session_repo
    except Exception as e:
        st.error(f"⚠️ Could not connect to backend services: {e}")
        st.info("Make sure your database and Ollama are running, then refresh.")
        st.stop()

    page = st.session_state.page
    if page == "auth":
        page_auth(auth)
    elif page == "analyze":
        page_analyze(analyzer)
    elif page == "results":
        page_results()
    elif page == "sessions":
        page_sessions(session_repo)


if __name__ == "__main__":
    main()
