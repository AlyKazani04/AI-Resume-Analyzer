from models.job_description import JobDescription
from repository.db import Database


class JobDescriptionRepository:
    def __init__(self, database: Database):
        self.database = database

    def create(self, job_description: JobDescription) -> int:
        query = "INSERT INTO job_descriptions (title, content) VALUES (%s, %s)"
        
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, (job_description.title, job_description.content,))
            connection.commit()
            return int(cursor.lastrowid)