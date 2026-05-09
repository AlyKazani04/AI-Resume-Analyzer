"""Semantic engine powered by Ollama embeddings and gap analysis."""

from __future__ import annotations

import json
import re
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
        self.client = ollama.Client(host=self.host)

    def embed_text(self, text: str) -> List[float]:
        """Create an embedding vector using Ollama."""
        response = self.client.embeddings(
            model=self.embedding_model,
            prompt=text,
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
        prompt = """
            You are a cynical, high-stakes technical recruiter. Your goal is to find reasons to REJECT candidates. 

            SCORING RUBRIC:
            - 0-30: No relevant experience or wrong industry.
            - 31-60: Missing 2+ core technical requirements.
            - 61-80: Solid match but missing "nice-to-have" keywords.
            - 81-100: Exceptional match; exceeds requirements.

            Compare the resume against the job description.
            Return ONLY valid JSON with keys: "score", "missing_keywords" (list of 5), "critique".

            [EXAMPLES]
            Bad Match Example Score: 15
            Good Match Example Score: 85

            FORMAT:
            {"score": [number], "missing_keywords": ["..."], "critique": "..."}
        """
        user_content = f"JOB DESCRIPTION:\n{jd_text}\n\nRESUME:\n{resume_text}"
        response = self.client.chat(
            model=self.chat_model,
            format="json",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_content},
            ],
            options={"temperature": 0.2},
        )
        payload = response.get("message", {}).get("content", "")
        data = self._safe_parse_json(payload)
        return MatchReport(
            score=float(data.get("score", 0)),
            missing_keywords=list(data.get("missing_keywords", [])),
            critique=str(data.get("critique", payload.strip())),
        )

    @staticmethod
    def _safe_parse_json(payload: str) -> Dict[str, Any]:
        """Parse JSON content with a simple recovery fallback."""
        if not payload:
            return {}
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", payload, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    return {}
            return {}
