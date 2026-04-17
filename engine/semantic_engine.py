"""Semantic engine powered by Ollama embeddings and gap analysis."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List

import ollama
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class MatchReport:
    score: float
    missing_keywords: List[str]
    critique: str


class OllamaSemanticEngine:
    """Generate embeddings, compute similarity, and create gap reports."""

    def __init__(self, embedding_model: str, chat_model: str, host: str) -> None:
        self.embedding_model = embedding_model
        self.chat_model = chat_model
        self.host = host

    def embed_text(self, text: str) -> List[float]:
        """Create an embedding vector using Ollama."""
        response = ollama.embeddings(
            model=self.embedding_model,
            prompt=text,
            host=self.host,
        )
        return response.get("embedding", [])

    def similarity_score(self, resume_text: str, jd_text: str) -> float:
        """Compute cosine similarity between resume and job description."""
        resume_vec = self.embed_text(resume_text)
        jd_vec = self.embed_text(jd_text)
        score = cosine_similarity([resume_vec], [jd_vec])[0][0]
        return float(score)

    def gap_analysis(self, resume_text: str, jd_text: str) -> MatchReport:
        """Generate a strict recruiter-style gap report."""
        prompt = (
            "You are a strict recruiter. Compare the resume against the job description. "
            "Return JSON with keys: score (0-100), missing_keywords (list of 5), critique."
        )
        user_content = f"JOB DESCRIPTION:\n{jd_text}\n\nRESUME:\n{resume_text}"
        response = ollama.chat(
            model=self.chat_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_content},
            ],
            options={"temperature": 0.2},
            host=self.host,
        )
        payload = response.get("message", {}).get("content", "{}")
        data: Dict[str, Any] = json.loads(payload)
        return MatchReport(
            score=float(data.get("score", 0)),
            missing_keywords=list(data.get("missing_keywords", [])),
            critique=str(data.get("critique", "")),
        )
