"""Repository for resumes."""

from __future__ import annotations

from typing import Iterable, Optional

from models.resume import Resume
from repository.db import Database


class ResumeRepository:
    """CRUD operations for resumes."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, resume: Resume) -> int:
        """Insert a resume and return its new ID."""
        query = "INSERT INTO resumes (user_id, filename, content) VALUES (%s, %s, %s)"
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, (resume.user_id, resume.filename, resume.content))
            connection.commit()
            return int(cursor.lastrowid)

    def get_by_id(self, resume_id: int) -> Optional[Resume]:
        """Fetch a resume by ID."""
        query = "SELECT id, user_id, filename, content, uploaded_at FROM resumes WHERE id = %s"
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, (resume_id,))
            row = cursor.fetchone()
        if not row:
            return None
        return Resume(
            id=row[0],
            user_id=row[1],
            filename=row[2],
            content=row[3],
            uploaded_at=row[4],
        )

    def list_by_user(self, user_id: int) -> Iterable[Resume]:
        """List all resumes for a user."""
        query = (
            "SELECT id, user_id, filename, content, uploaded_at "
            "FROM resumes WHERE user_id = %s ORDER BY uploaded_at DESC"
        )
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
        for row in rows:
            yield Resume(
                id=row[0],
                user_id=row[1],
                filename=row[2],
                content=row[3],
                uploaded_at=row[4],
            )
