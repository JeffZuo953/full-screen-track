from __future__ import annotations

import os
from typing import List, Dict, Union

from src.core.model.entity.file import File
from src.core.util.logger import logger
from src.core.model.service.file_service import FileService
from src.core.util.colorizer import Colorizer
from src.core.uploader.webdav_client import WebDAVClient
from src.core.manager.config import ConfigManager


class UploaderManager:
    """Handles file uploads to the WebDAV server"""

    def __init__(self, config: ConfigManager,
                 file_service: FileService) -> None:
        """
        Initializes the UploaderManager.

        Args:
            config: The ConfigManager instance.
            file_service: The FileService instance.
        """
        self.config: ConfigManager = config
        self.file_service: FileService = file_service
        self.webdav: WebDAVClient = WebDAVClient(config)

    def sync_pending_files(self) -> None:
        """Sync pending files to WebDAV server"""
        pending_files: List[File] = self.file_service.get_pending_files()
        if not pending_files:
            logger.info("No pending files to sync")
            return

        for file in pending_files:
            try:
                if not os.path.exists(file.local_path):
                    logger.debug(f"File no longer exists: {file.local_path}")
                    continue

                logger.debug(
                    f"Attempting to upload file: {file.local_path} to {file.remote_path}"
                )
                self.upload_file(file.remote_path, file.local_path)
            except Exception as e:
                logger.error(
                    Colorizer.red(
                        f"✗ Upload failed for {file.local_path}: {e}"))

    def upload_file(self, remote_path: str, local_path: str) -> None:
        """Upload a single file to the WebDAV server"""
        if self.webdav.upload_file(remote_path, local_path):
            self.file_service.update_file_status(local_path, "uploaded")
            logger.info(Colorizer.green(f"✓ Uploaded {local_path}"))

    def get_upload_status(self) -> List[Dict[str, Union[str, float]]]:
        """Get current upload status without checking existence"""
        return self.webdav.get_upload_status()
