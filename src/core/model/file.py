# src/core/manager/file_model.py
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import os


class FileModel:
    """Handles database operations related to files"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
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

    def insert_or_update_file(self, file_info: Dict) -> None:
        """Insert or update file record in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO files 
                (local_path, remote_path, file_size, last_modified, 
                status, last_check, exists_locally)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    file_info["local_path"],
                    file_info["remote_path"],
                    file_info["file_size"],
                    file_info["last_modified"],
                    "pending",
                    datetime.now(),
                ),
            )

    def fetch_file(self, local_path: str) -> Optional[Dict]:
        """Fetch a file's record by local path"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM files WHERE local_path = ?",
                (local_path,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def fetch_pending_files(self) -> List[Dict]:
        """Fetch all pending files that exist locally"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT local_path, remote_path FROM files 
                   WHERE status = 'pending' AND exists_locally = 1"""
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_file_status(
        self, local_path: str, status: str, upload_time: Optional[str] = None
    ) -> None:
        """Update file status and upload time"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE files 
                   SET status = ?, upload_time = ? 
                   WHERE local_path = ?""",
                (status, upload_time or datetime.now(), local_path),
            )

    def fetch_files_paginated(self, page: int = 1, page_size: int = 10) -> List[Dict]:
        """Fetch files with pagination"""
        offset = (page - 1) * page_size
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM files
                LIMIT ? OFFSET ?
                """,
                (page_size, offset),
            )
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def search_files(
        self,
        query: str,
        page: int = 1,
        page_size: int = 10,
    ) -> List[Dict]:
        """Search files by local_path with pagination and date range"""
        offset = (page - 1) * page_size
        sql = "SELECT * FROM files"
        params = []

        # Add WHERE clause conditions
        conditions = []
        if query:
            conditions.append("local_path LIKE ?")
            params.append("%" + query + "%")

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        # Add pagination
        sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    def fetch_total_file_count(self) -> int:
        """Fetch the total count of files in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM files")
            return cursor.fetchone()[0]

    def update_file_existence(self, local_path: str, exists: bool) -> None:
        """Update file's local existence status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE files SET exists_locally = ? WHERE local_path = ?",
                (exists, local_path),
            )

    def check_file_exists(self, local_path: str) -> bool:
        """Check if file exists in filesystem and update db"""
        exists = os.path.exists(local_path)
        self.update_file_existence(local_path, exists)
        return exists

    def update_files(self, file_paths: List[tuple]) -> None:
        """Batch update files existence status and last check time
        
        Args:
            file_paths: List of tuples containing (exists, local_path)
        """
        with sqlite3.connect(self.db_path) as conn:
            # Create temporary table
            conn.execute("""
                CREATE TEMP TABLE IF NOT EXISTS temp_updates (
                    exists_locally BOOLEAN,
                    local_path TEXT,
                    last_check TIMESTAMP
                )
            """)
            
            # Prepare data with current timestamp
            now = datetime.now()
            update_data = [(exists, path, now) for exists, path in file_paths]
            
            # Insert into temp table
            conn.executemany(
                """
                INSERT INTO temp_updates (exists_locally, local_path, last_check)
                VALUES (?, ?, ?)
                """, 
                update_data
            )
            
            # Update main table using temp table
            conn.execute("""
                UPDATE files 
                SET exists_locally = (
                    SELECT exists_locally 
                    FROM temp_updates 
                    WHERE temp_updates.local_path = files.local_path
                ),
                last_check = (
                    SELECT last_check 
                    FROM temp_updates 
                    WHERE temp_updates.local_path = files.local_path
                )
                WHERE local_path IN (SELECT local_path FROM temp_updates)
            """)
            
            # Drop temporary table
            conn.execute("DROP TABLE temp_updates")

    def delete_old_records(self, days: int) -> int:
        """Delete records older than specified days
        
        Args:
            days: Number of days to keep records for
            
        Returns:
            Number of records deleted
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                DELETE FROM files 
                WHERE last_check < datetime('now', '-' || ? || ' days')
                """,
                (days,)
            )
            return cursor.rowcount

    def fetch_old_files(self, days: int) -> List[Dict]:
        """Fetch files older than specified days
        
        Args:
            days: Number of days to keep files for
            
        Returns:
            List of file records
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT local_path FROM files 
                WHERE last_modified < datetime('now', '-' || ? || ' days')
                AND exists_locally = 1
                """,
                (days,)
            )
            return [dict(row) for row in cursor.fetchall()]
