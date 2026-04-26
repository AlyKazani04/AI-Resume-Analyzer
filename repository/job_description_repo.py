"""Repository for persisting job descriptions."""

from models.job_description import JobDescription
from repository.db import Database


class JobDescriptionRepository:
    def __init__(self, database: Database):
        self.database = database

    def create(self, job_description: JobDescription) -> int:
        query = (
            "INSERT INTO job_descriptions (user_id, title, content, content_hash) "
            "VALUES (%s, %s, %s, %s)"
        )

        with self.database.connect() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    query,
                    (
                        job_description.user_id,
                        job_description.title,
                        job_description.content,
                        job_description.content_hash,
                    ),
                )
                connection.commit()
                return int(cursor.lastrowid)
            except Exception:
                connection.rollback()
                lookup_query = "SELECT id FROM job_descriptions WHERE user_id = %s AND content_hash = %s"
                cursor.execute(
                    lookup_query,
                    (job_description.user_id, job_description.content_hash),
                )
                row = cursor.fetchone()
                if not row:
                    raise
                update_query = (
                    "UPDATE job_descriptions SET created_at = CURRENT_TIMESTAMP "
                    "WHERE user_id = %s AND content_hash = %s"
                )
                cursor.execute(
                    update_query,
                    (job_description.user_id, job_description.content_hash),
                )
                connection.commit()
                return int(row[0])
