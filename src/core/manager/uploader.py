from src.core.util.logger import logger

import os

from src.core.model.file import FileModel
from src.core.util.colorizer import Colorizer
from src.core.uploader.webdav_client import WebDAVClient


class UploaderManager:
    """Handles file uploads to the WebDAV server"""

    def __init__(self, config, file_model: FileModel):
        self.config = config
        self.file_model = file_model
        self.webdav = WebDAVClient(config)

    def sync_pending_files(self) -> None:
        """Sync pending files to WebDAV server"""
        pending_files = self.file_model.fetch_pending_files()
        if not pending_files:
            logger.info("No pending files to sync")
            return

        for file_info in pending_files:
            try:
                local_path = file_info["local_path"]
                remote_path = file_info["remote_path"]

                if not os.path.exists(local_path):
                    logger.warning(f"File no longer exists: {local_path}")
                    self.file_model.update_file_existence(local_path, False)
                    continue

                logger.debug(
                    f"Attempting to upload file: {local_path} to {remote_path}"
                )
                self.upload_file(remote_path, local_path)
            except Exception as e:
                logger.error(Colorizer.red(f"✗ Upload failed for {local_path}: {e}"))

        logger.info(Colorizer.green(f"✓ Synced {len(pending_files)} pending files"))

    def upload_file(self, remote_path: str, local_path: str) -> None:
        """Upload a single file to the WebDAV server"""
        if self.webdav.upload_file(remote_path, local_path):
            self.file_model.update_file_status(local_path, "uploaded")
            logger.info(Colorizer.green(f"✓ Uploaded {local_path}"))

    def get_upload_status(self):
        """Get current upload status with file existence check"""
        all_status = self.webdav.get_upload_status()
        # Filter out non-existent files
        return [
            status
            for status in all_status
            if self.file_model.check_file_exists(status["file"])
        ]
