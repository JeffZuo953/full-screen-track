from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Tuple
import os
from src.core.model.dao.file_dao import FileDAO
from src.core.model.entity.file import File


class FileService:
    """Service layer for file-related operations"""

    def __init__(self, db_path: str) -> None:
        """
        Initializes the FileService with a database path.

        Args:
            db_path: The path to the SQLite database.
        """
        self.file_dao: FileDAO = FileDAO(db_path)

    def register_file(self, file_info: Dict[str, str | int | datetime | bool]) -> None:
        """
        Register a new file or update an existing one in the database.

        Args:
            file_info: A dictionary containing file information.
        """
        file: File = File.from_dict(file_info)
        self.file_dao.insert_or_update(file)

    def get_file(self, local_path: str) -> Optional[File]:
        """
        Get file information by its local path.

        Args:
            local_path: The local path of the file.

        Returns:
            The File object if found, None otherwise.
        """
        return self.file_dao.fetch_by_path(local_path)

    def get_pending_files(self) -> List[File]:
        """
        Get all pending files from the database.

        Returns:
            A list of File objects that are marked as pending.
        """
        return self.file_dao.fetch_pending_files()

    def update_file_status(
        self, local_path: str, status: str, upload_time: Optional[datetime] = None
    ) -> None:
        """
        Update the status of a file.

        Args:
            local_path: The local path of the file.
            status: The new status of the file.
            upload_time: The time the file was uploaded (optional).
        """
        self.file_dao.update_status(local_path, status, upload_time)

    def get_files_paginated(
        self, page: int, page_size: int, query: str = ""
    ) -> List[File]:
        """
        Get a paginated list of files, optionally filtered by a search query.

        Args:
            page: The page number.
            page_size: The number of files per page.
            query: A search query to filter files by local path (optional).

        Returns:
            A list of File objects for the requested page.
        """
        return self.file_dao.fetch_paginated(page, page_size, query)

    def get_total_count(self) -> int:
        """
        Get the total number of files in the database.

        Returns:
            The total number of files.
        """
        return self.file_dao.count_total()

    def check_file_exists(self, local_path: str) -> bool:
        """
        Check if a file exists locally (without updating the database).

        Args:
            local_path: The local path of the file.

        Returns:
            True if the file exists, False otherwise.
        """
        return os.path.exists(local_path)

    def update_file_existence(self, local_path: str, exists: bool) -> None:
        """
        Manually update the existence status of a file in the database.

        Args:
            local_path: The local path of the file.
            exists: True if the file exists locally, False otherwise.
        """
        self.file_dao.update_existence(local_path, exists)

    def batch_update_existence(self, file_paths: List[Tuple[bool, str]]) -> None:
        """
        Batch update the existence status of multiple files.

        Args:
            file_paths: A list of tuples, where each tuple contains
                         (exists: bool, local_path: str).
        """
        now: datetime = datetime.now()
        updates: List[Tuple[bool, str, datetime]] = [
            (exists, path, now) for exists, path in file_paths
        ]
        self.file_dao.batch_update_existence(updates)

    def delete_old_records(self, days: int) -> int:
        """
        Delete records older than a specified number of days.

        Args:
            days: The number of days to retain records.

        Returns: The number of deleted records.
        """
        return self.file_dao.delete_old_records(days)

    def get_old_files(self, days: int) -> List[File]:
        """
        Get files older than a specified number of days.

        Args:
            days: The number of days to consider a file "old".

        Returns:
            A list of File objects that are older than the specified days.
        """
        return self.file_dao.fetch_old_files(days)

    def check_and_update_existence(self, files: List[File]) -> None:
        """
        Check and update the existence status for multiple files.

        Args:
            files: A list of File objects.
        """
        updates: List[Tuple[bool, str]] = []
        for file in files:
            exists: bool = os.path.exists(file.local_path)
            updates.append((exists, file.local_path))
        self.batch_update_existence(updates)

    def update_files(self, file_paths: List[Tuple[bool, str]]) -> None:
        """
        Batch update multiple file existence statuses.  This is a convenience
        method that calls `batch_update_existence`.

        Args:
            file_paths: List of tuples containing (exists, local_path).
        """
        self.batch_update_existence(file_paths)
