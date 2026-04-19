"""Repository for users."""

from __future__ import annotations

from typing import Optional

from models.user import User
from repository.db import Database


class UserRepository:
    """CRUD operations for users."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, user: User) -> int:
        """Insert a user and return its new ID."""
        query = "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)"
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, (user.name, user.email, user.password_hash))
            connection.commit()
            return int(cursor.lastrowid)

    def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by email."""
        query = (
            "SELECT id, name, email, password_hash, created_at, last_login_at "
            "FROM users WHERE email = %s"
        )
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, (email,))
            row = cursor.fetchone()
        if not row:
            return None
        return User(
            id=row[0],
            name=row[1],
            email=row[2],
            password_hash=row[3],
            created_at=row[4],
            last_login_at=row[5],
        )

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Fetch a user by ID."""
        query = (
            "SELECT id, name, email, password_hash, created_at, last_login_at "
            "FROM users WHERE id = %s"
        )
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
        if not row:
            return None
        return User(
            id=row[0],
            name=row[1],
            email=row[2],
            password_hash=row[3],
            created_at=row[4],
            last_login_at=row[5],
        )

    def update_last_login(self, user_id: int) -> None:
        """Update last login timestamp for a user."""
        query = "UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = %s"
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, (user_id,))
            connection.commit()
