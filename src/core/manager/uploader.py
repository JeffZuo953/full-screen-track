from src.core.util.logger import logger

import os

from src.core.model.service.file_service import FileService  # 新导入
from src.core.util.colorizer import Colorizer
from src.core.uploader.webdav_client import WebDAVClient
from src.core.manager.config import ConfigManager


class UploaderManager:
    """Handles file uploads to the WebDAV server"""

    def __init__(self, config: ConfigManager, file_service: FileService):
        self.config = config
        self.file_service = file_service  # 更改为 file_service
        self.webdav = WebDAVClient(config)

    def sync_pending_files(self) -> None:
        """Sync pending files to WebDAV server"""
        pending_files = self.file_service.get_pending_files()
        if not pending_files:
            logger.info("No pending files to sync")
            return

        for file in pending_files:
            try:
                if not os.path.exists(file.local_path):
                    logger.warning(f"File no longer exists: {file.local_path}")
                    continue

                logger.debug(f"Attempting to upload file: {file.local_path} to {file.remote_path}")
                self.upload_file(file.remote_path, file.local_path)
            except Exception as e:
                logger.error(Colorizer.red(f"✗ Upload failed for {file.local_path}: {e}"))

    def upload_file(self, remote_path: str, local_path: str) -> None:
        """Upload a single file to the WebDAV server"""
        if self.webdav.upload_file(remote_path, local_path):
            self.file_service.update_file_status(local_path, "uploaded")
            logger.info(Colorizer.green(f"✓ Uploaded {local_path}"))

    def get_upload_status(self):
        """Get current upload status without checking existence"""
        return self.webdav.get_upload_status()
