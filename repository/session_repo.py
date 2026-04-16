"""Repository for analysis sessions."""

from __future__ import annotations

from typing import Iterable

from models.analysis_session import AnalysisSession
from repository.db import Database


class AnalysisSessionRepository:
    """CRUD operations for analysis sessions."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, session: AnalysisSession) -> int:
        """Insert an analysis session and return its new ID."""
        query = (
            "INSERT INTO analysis_sessions (user_id, resume_id, jd_id, similarity_score, gap_report) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                query,
                (
                    session.user_id,
                    session.resume_id,
                    session.jd_id,
                    session.similarity_score,
                    session.gap_report,
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def list_by_user(self, user_id: int) -> Iterable[AnalysisSession]:
        """List analysis sessions for a user."""
        query = (
            "SELECT id, user_id, resume_id, jd_id, similarity_score, gap_report, analyzed_at "
            "FROM analysis_sessions WHERE user_id = %s ORDER BY analyzed_at DESC"
        )
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
        for row in rows:
            yield AnalysisSession(
                id=row[0],
                user_id=row[1],
                resume_id=row[2],
                jd_id=row[3],
                similarity_score=float(row[4]),
                gap_report=row[5],
                analyzed_at=row[6],
            )
