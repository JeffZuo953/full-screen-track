import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple

from src.core.model.entity.file import File


class FileDAO:
    """Data Access Object for file-related database operations"""

    def __init__(self, db_path: str) -> None:
        """
        Initializes the FileDAO with a database path.

        Args:
            db_path: The path to the SQLite database.
        """
        self.db_path: str = db_path
        self._create_table()

    def _create_table(self) -> None:
        """Create the files table if it doesn't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    local_path TEXT UNIQUE,
                    remote_path TEXT,
                    file_size INTEGER,
                    last_modified TIMESTAMP,
                    status TEXT,
                    upload_time TIMESTAMP,
                    last_check TIMESTAMP,
                    exists_locally BOOLEAN DEFAULT 1
                )
            """
            )

    def insert_or_update(self, file: File) -> None:
        """Insert or update a file record"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO files 
                (local_path, remote_path, file_size, last_modified, 
                status, last_check, exists_locally)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    file.local_path,
                    file.remote_path,
                    file.file_size,
                    file.last_modified,
                    file.status,
                    datetime.now(),
                    file.exists_locally,
                ),
            )

    def fetch_by_path(self, local_path: str) -> Optional[File]:
        """Fetch a file record by local path"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM files WHERE local_path = ?", (local_path,))
            row = cursor.fetchone()
            if row:
                return File.from_dict(dict(row))  # Convert Row to dict
            return None

    def fetch_pending_files(self) -> List[File]:
        """Fetch all pending files that exist locally"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT * FROM files 
                WHERE status = 'pending' AND exists_locally = 1"""
            )
            rows = cursor.fetchall()
            return [File.from_dict(dict(row)) for row in rows]  # Convert Row to dict

    def update_status(
        self, local_path: str, status: str, upload_time: Optional[datetime] = None
    ) -> None:
        """Update file status and upload time"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE files SET status = ?, upload_time = ? WHERE local_path = ?",
                (status, upload_time or datetime.now(), local_path),
            )

    def fetch_paginated(self, page: int, page_size: int, query: str = "") -> List[File]:
        """Fetch files with pagination and optional search"""
        offset: int = (page - 1) * page_size
        sql: str = "SELECT * FROM files"
        params: List[str | int] = []

        if query:
            sql += " WHERE local_path LIKE ?"
            params.append(f"%{query}%")

        sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            return [File.from_dict(dict(row)) for row in rows]  # Convert Row to dict

    def count_total(self) -> int:
        """Count total number of files"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM files")
            count: int = cursor.fetchone()[0]
            return count

    def update_existence(self, local_path: str, exists: bool) -> None:
        """Update file's local existence status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE files SET exists_locally = ? WHERE local_path = ?",
                (exists, local_path),
            )

    def batch_update_existence(
        self, updates: List[Tuple[bool, str, datetime]]
    ) -> None:
        """Batch update files existence status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                """UPDATE files 
                SET exists_locally = ?, last_check = ? 
                WHERE local_path = ?""",
                updates,
            )

    def delete_old_records(self, days: int) -> int:
        """Delete records older than specified days"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """DELETE FROM files 
                WHERE last_check < datetime('now', '-' || ? || ' days')""",
                (days,),
            )
            rowcount: int = cursor.rowcount
            return rowcount

    def fetch_old_files(self, days: int) -> List[File]:
        """Fetch files older than specified days"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT * FROM files 
                WHERE last_modified < datetime('now', '-' || ? || ' days')
                AND exists_locally = 1""",
                (days,),
            )
            rows = cursor.fetchall()
            return [File.from_dict(dict(row)) for row in rows]  # Convert Row to dict
