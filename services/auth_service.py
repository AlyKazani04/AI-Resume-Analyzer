"""Authentication service for registering and logging in users."""

from __future__ import annotations

import bcrypt

from models.user import User
from repository.user_repo import UserRepository


class AuthService:
    """Handle registration and authentication."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against a bcrypt hash."""
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    def register_user(self, name: str, email: str, password: str) -> int:
        """Register a new user and return their ID."""
        password_hash = self.hash_password(password)
        user = User(id=None, name=name, email=email, password_hash=password_hash)
        return self.user_repo.create(user)

    def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate a user by email and password."""
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        self.user_repo.update_last_login(user.id or 0)
        return user
