from datetime import datetime
from typing import List, Optional, Dict, Tuple
import os
from src.core.model.dao.file_dao import FileDAO
from src.core.model.entity.file import File


class FileService:
    """Service layer for file-related operations"""

    def __init__(self, db_path: str):
        self.file_dao = FileDAO(db_path)

    def register_file(self, file_info: Dict) -> None:
        """Register a new file or update existing one"""
        file = File.from_dict(file_info)
        self.file_dao.insert_or_update(file)

    def get_file(self, local_path: str) -> Optional[File]:
        """Get file by local path"""
        return self.file_dao.fetch_by_path(local_path)

    def get_pending_files(self) -> List[File]:
        """Get all pending files"""
        return self.file_dao.fetch_pending_files()

    def update_file_status(self, local_path: str, status: str, upload_time: Optional[datetime] = None) -> None:
        """Update file status"""
        self.file_dao.update_status(local_path, status, upload_time)

    def get_files_paginated(self, page: int, page_size: int, query: str = "") -> List[File]:
        """Get paginated files with optional search"""
        return self.file_dao.fetch_paginated(page, page_size, query)

    def get_total_count(self) -> int:
        """Get total number of files"""
        return self.file_dao.count_total()

    def check_file_exists(self, local_path: str) -> bool:
        """Check if file exists and update database"""
        exists = os.path.exists(local_path)
        self.file_dao.update_existence(local_path, exists)
        return exists

    def batch_update_existence(self, file_paths: List[Tuple[bool, str]]) -> None:
        """Batch update file existence status"""
        now = datetime.now()
        updates = [(exists, path, now) for exists, path in file_paths]
        self.file_dao.batch_update_existence(updates)

    def delete_old_records(self, days: int) -> int:
        """Delete old records from database"""
        return self.file_dao.delete_old_records(days)

    def get_old_files(self, days: int) -> List[File]:
        """Get files older than specified days"""
        return self.file_dao.fetch_old_files(days)

    def check_and_update_existence(self, files: List[File]) -> None:
        """Check and update existence status for multiple files"""
        updates = []
        for file in files:
            exists = os.path.exists(file.local_path)
            updates.append((exists, file.local_path))
        self.batch_update_existence(updates)
