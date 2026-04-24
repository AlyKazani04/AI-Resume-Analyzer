# AI Resume Analyzer - Agent Notes

## Overview
This repository is a layered architecture for a Streamlit-based resume analyzer.
The layers flow: UI -> Services -> Engine -> Repositories -> Models -> Parsers.

## Entry Points
- `app.py`: Streamlit UI entry point.
- `services/analyzer_service.py`: Orchestrates parsing, AI analysis, and DB writes.
- `services/auth_service.py`: Handles registration and login.
- `engine/semantic_engine.py`: Ollama embeddings + similarity + gap analysis.

## Configuration
- Environment variables are loaded in `config/settings.py`.
- Copy `.env.example` to `.env` and fill in secrets.

Required env vars:
- `OLLAMA_EMBEDDING_MODEL` (default: nomic-embed-text)
- `OLLAMA_CHAT_MODEL` (default: gemma3)
- `OLLAMA_HOST` (default: http://localhost:11434)
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`

## Database
Schema is expected to be MySQL and follow these tables:
- `users`
- `resumes`
- `job_descriptions`
- `analysis_sessions`

DB connection is wrapped in `repository/db.py`.

## Layer Responsibilities
- Parsers: `parsers/` (PDF/DOCX extraction via pdfplumber/python-docx).
- Models: `models/` (dataclasses for core entities).
- Repositories: `repository/` (CRUD on resumes + analysis sessions).
- Repositories: `repository/user_repo.py` (CRUD on users).
- Engine: `engine/semantic_engine.py` (Ollama + cosine similarity + gap report).
- Services: `services/analyzer_service.py` (main orchestration).
- UI: `app.py` (Streamlit components).

## Known Placeholders
- `engine/semantic_engine.py` expects JSON from the model response.
- Job descriptions are not yet persisted (future repo needed).
- User handling is mocked (user_id=1 in UI).
- UI now supports login/register and guest mode (no DB writes).

## Suggested Next Steps
1. Implement `JobDescriptionRepository` to persist job descriptions.
2. Store analysis sessions with resume + JD foreign keys.
3. Add tests for parsing and similarity ranking.
