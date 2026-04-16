"""Database connector and helper utilities."""

from __future__ import annotations

from dataclasses import dataclass

import mysql.connector


@dataclass
class DBConfig:
    host: str
    user: str
    password: str
    database: str


class Database:
    """Simple database wrapper for MySQL connections."""

    def __init__(self, config: DBConfig) -> None:
        self.config = config

    def connect(self) -> mysql.connector.MySQLConnection:
        """Create a new database connection."""
        return mysql.connector.connect(
            host=self.config.host,
            user=self.config.user,
            password=self.config.password,
            database=self.config.database,
        )
