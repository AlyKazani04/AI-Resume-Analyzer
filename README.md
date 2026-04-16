# AI Resume Analyzer
Streamlit app that analyzes resumes against job descriptions using OpenAI embeddings.

## Quick Start
1. Create `.env` from `.env.example` and fill in values.
2. Install dependencies from `requirements.txt`.
3. Run the app: `streamlit run app.py`.

## Architecture
Layered flow: UI -> Services -> Engine -> Repositories -> Models -> Parsers.

See `AGENTS.md` for architecture details and ownership notes.

![Flow of the Project](demo/image.png)
