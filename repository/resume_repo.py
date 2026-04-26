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
        query = (
            "INSERT INTO resumes (user_id, filename, content, content_hash, file_type) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        with self.database.connect() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    query,
                    (
                        resume.user_id,
                        resume.filename,
                        resume.content,
                        resume.content_hash,
                        resume.file_type,
                    ),
                )
                connection.commit()
                return int(cursor.lastrowid)
            except Exception:
                connection.rollback()
                lookup_query = (
                    "SELECT id FROM resumes WHERE user_id = %s AND content_hash = %s"
                )
                cursor.execute(lookup_query, (resume.user_id, resume.content_hash))
                row = cursor.fetchone()
                if not row:
                    raise
                update_query = (
                    "UPDATE resumes SET uploaded_at = CURRENT_TIMESTAMP "
                    "WHERE user_id = %s AND content_hash = %s"
                )
                cursor.execute(update_query, (resume.user_id, resume.content_hash))
                connection.commit()
                return int(row[0])

    def get_by_id(self, resume_id: int) -> Optional[Resume]:
        """Fetch a resume by ID."""
        query = (
            "SELECT id, user_id, filename, content, content_hash, file_type, uploaded_at "
            "FROM resumes WHERE id = %s"
        )
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
            content_hash=row[4],
            file_type=row[5],
            uploaded_at=row[6],
        )

    def list_by_user(self, user_id: int) -> Iterable[Resume]:
        """List all resumes for a user."""
        query = (
            "SELECT id, user_id, filename, content, content_hash, file_type, uploaded_at "
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
                content_hash=row[4],
                file_type=row[5],
                uploaded_at=row[6],
            )
