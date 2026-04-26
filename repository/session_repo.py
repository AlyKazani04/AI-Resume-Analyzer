"""Repository for analysis sessions."""

from __future__ import annotations

from typing import Iterable

from models.analysis_session import AnalysisSession
from repository.db import Database
import json


class AnalysisSessionRepository:
    """CRUD operations for analysis sessions."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, session):
        query = """
        INSERT INTO analysis_sessions (user_id, resume_id, jd_id, similarity_score, gap_report, missing_keywords)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        missing_json = json.dumps(session.missing_keywords) if session.missing_keywords else None

        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, (
                session.user_id,
                session.resume_id,
                session.jd_id,
                session.similarity_score,
                session.gap_report,
                missing_json
            ))
            connection.commit()
            return int(cursor.lastrowid)
    
    def list_by_user(self, user_id: int) -> Iterable[AnalysisSession]:
        """List analysis sessions for a user."""
        query = (
            "SELECT id, user_id, resume_id, jd_id, similarity_score, gap_report, missing_keywords, analyzed_at "
            "FROM analysis_sessions WHERE user_id = %s ORDER BY analyzed_at DESC"
        )
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()

        for row in rows:
            session = AnalysisSession(
                id=row[0],
                user_id=row[1],
                resume_id=row[2],
                jd_id=row[3],
                similarity_score=float(row[4]),
                gap_report=row[5],
                analyzed_at=row[7],
            )
            session.missing_keywords = json.loads(row[6]) if row[6] else []
            yield session

    def list_all(self) -> Iterable[AnalysisSession]:
        """List all analysis sessions."""
        query = """
        SELECT id, user_id, resume_id, jd_id, similarity_score, missing_keywords, gap_report, analyzed_at
        FROM analysis_sessions
        ORDER BY analyzed_at DESC
        """

        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        for row in rows:
            session = AnalysisSession(
                id=row[0],
                user_id=row[1],
                resume_id=row[2],
                jd_id=row[3],
                similarity_score=float(row[4]),
                gap_report=row[6],
                analyzed_at=row[7],
            )
            session.missing_keywords = json.loads(row[5]) if row[5] else []
            yield session
