"""Repository for analysis sessions."""

from __future__ import annotations

from typing import Iterable

from models.analysis_session import AnalysisSession
from repository.db import Database


class AnalysisSessionRepository:
    """CRUD operations for analysis sessions."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, session):
        query = """
        INSERT INTO analysis_sessions (resume_id, score, missing_keywords, critique)
        VALUES (%s, %s, %s, %s)
        """

        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, (
                session.resume_id,
                session.similarity_score,  # goes into score
                ", ".join(session.missing_keywords),  # list → string
                session.gap_report  # goes into critique
            ))
            connection.commit()
            return int(cursor.lastrowid)

    def list_all(self) -> Iterable[AnalysisSession]:
        """List all analysis sessions."""
        query = """
        SELECT id, resume_id, score, missing_keywords, critique, created_at
        FROM analysis_sessions
        ORDER BY created_at DESC
        """

        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        for row in rows:
            session = AnalysisSession(
                id=row[0],
                resume_id=row[1],
                similarity_score=float(row[2]),
                gap_report=row[4],
            )
            session.missing_keywords = row[3].split(",") if row[3] else []
            yield session