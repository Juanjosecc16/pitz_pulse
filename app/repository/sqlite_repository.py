"""SQLite implementation of RequestRepository.

A new connection per operation keeps it safe to use from FastAPI's thread pool.
Column names match the StoredRequest attribute names, so rows map 1:1 to the model.
"""

import sqlite3
from contextlib import closing
from pathlib import Path

from app.domain.enums import Category, Priority
from app.domain.models import StoredRequest
from app.repository.base import RequestRepository

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS requests (
    id                 TEXT PRIMARY KEY,
    category           TEXT NOT NULL,
    priority           TEXT NOT NULL,
    suggested_area     TEXT NOT NULL,
    language           TEXT NOT NULL,
    summary            TEXT NOT NULL,
    needs_info         INTEGER NOT NULL,
    follow_up_question TEXT,
    message            TEXT NOT NULL,
    source_area        TEXT,
    created_at         TEXT NOT NULL
)
"""

COLUMNS = list(StoredRequest.model_fields)


class SQLiteRequestRepository(RequestRepository):
    def __init__(self, database_path: str | Path):
        self._database_path = str(database_path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(CREATE_TABLE_SQL)

    def save(self, request: StoredRequest) -> None:
        row = request.model_dump(mode="json", by_alias=False)
        placeholders = ", ".join(f":{column}" for column in COLUMNS)
        with closing(self._connect()) as connection, connection:
            connection.execute(f"INSERT INTO requests ({', '.join(COLUMNS)}) VALUES ({placeholders})", row)

    def list(self, category: Category | None = None, priority: Priority | None = None) -> list[StoredRequest]:
        conditions, parameters = [], {}
        if category:
            conditions.append("category = :category")
            parameters["category"] = category.value
        if priority:
            conditions.append("priority = :priority")
            parameters["priority"] = priority.value

        query = "SELECT * FROM requests"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC, rowid DESC"  # rowid breaks ties between identical timestamps

        with closing(self._connect()) as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [StoredRequest.model_validate(dict(row)) for row in rows]
