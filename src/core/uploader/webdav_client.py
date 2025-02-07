from __future__ import annotations

from src.core.util.logger import logger
import os
from typing import Dict, List, Optional
from webdav3.client import Client
from src.core.manager.config import ConfigManager
from src.core.util.colorizer import Colorizer


class WebDAVClient:
    """Simple WebDAV client wrapper"""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager: ConfigManager = config_manager
        self.client: Optional[Client] = self._setup_client()
        self.progress_interval = 1  # seconds between progress updates
        self._last_status = ""
        self.current_uploads = {}

    def _setup_client(self) -> Optional[Client]:
        """Initialize WebDAV client"""
        webdav_config = self.config_manager.get_webdav_config()
        os.environ["no_proxy"] = webdav_config.get("url")

        options: Dict[str, str] = {
            "webdav_hostname": webdav_config.get("url"),
            "webdav_login": webdav_config.get("username"),
            "webdav_password": webdav_config.get("password"),
        }
        try:
            logger.debug(f"Initializing WebDAV client with options: {options}")
            return Client(options)
        except Exception as e:
            logger.error(Colorizer.red(f"✗ WebDAV client initialization failed: {e}"))
            return None

    def _progress_callback(self, current: int, total: int) -> None:
        """Progress callback for file upload"""
        if current == total:
            return

        # Calculate percentage
        percentage = (current / total) * 100

        # Update current uploads status
        self.current_uploads[self._last_file] = {
            "progress": round(percentage, 2),
            "status": "uploading",
        }

    def _check_path_exists(self, remote_path: str) -> bool:
        try:
            return self.client.check(remote_path)
        except Exception as e:
            logger.debug(f"Path check failed for {remote_path}: {str(e)}")
            return False

    def upload_file(self, remote_path: str, local_path: str) -> bool:
        if not self.client:
            logger.error(Colorizer.red("✗ WebDAV client is not initialized"))
            return False

        try:
            self._last_file = local_path
            self.current_uploads[local_path] = {"progress": 0, "status": "starting"}
            file_size = os.path.getsize(local_path)
            logger.info(
                f"⏳ Starting upload: {local_path} -> {remote_path} ({file_size} bytes)"
            )

            # Ensure directory exists
            remote_dir = os.path.dirname(remote_path)
            self.create_directory(remote_dir)

            # Upload with progress bar
            self.client.upload_file(
                remote_path=remote_path,
                local_path=local_path,
                progress=self._progress_callback,
            )

            logger.info(Colorizer.green(f"✓ Upload successful: {local_path}"))
            self.current_uploads[local_path]["status"] = "completed"
            self.current_uploads[local_path]["progress"] = 100
            return True

        except Exception as e:
            self.current_uploads[local_path]["status"] = "failed"
            logger.error(Colorizer.red(f"✗ Upload failed: {str(e)}"))
            logger.debug(
                f"Failed upload details - Local: {local_path}, Remote: {remote_path}"
            )
            return False

    def create_directory(self, remote_path: str) -> bool:
        """Create remote directory and all necessary parent directories."""
        if not self.client:
            logger.error(Colorizer.red("✗ WebDAV client is not initialized"))
            return False

        try:
            # Check if path already exists
            if self._check_path_exists(remote_path):
                logger.debug(f"Path already exists: {remote_path}")
                return True

            # Split path and get parent
            parts: List[str] = remote_path.split("/")
            parent_path = "/".join(parts[:-1])

            # If parent exists, create target directly
            if self._check_path_exists(parent_path):
                logger.debug(f"Parent directory exists: {parent_path}")
                self.client.mkdir(remote_path)
                logger.info(Colorizer.green(f"✓ Directory created: {remote_path}"))
                return True

            # Create full path structure
            logger.info(f"⏳ Creating directory structure: {remote_path}")
            current_path: str = ""

            for part in parts:
                if not part:
                    continue
                current_path += f"/{part}"
                try:
                    if not self.client.check(current_path):
                        self.client.mkdir(current_path)
                        logger.info(
                            Colorizer.green(f"✓ Directory created: {current_path}")
                        )
                    else:
                        logger.debug(f"Directory exists: {current_path}")
                except Exception as e:
                    logger.error(
                        Colorizer.red(
                            f"✗ Failed to create directory {current_path}: {str(e)}"
                        )
                    )
                    return False

            logger.info(
                Colorizer.green(
                    f"✓ Directory structure created successfully: {remote_path}"
                )
            )
            return True

        except Exception as e:
            logger.error(Colorizer.red(f"✗ Directory creation failed: {str(e)}"))
            return False

    def check_exists(self, remote_path: str) -> bool:
        logger.debug(f"Checking if file exists: {remote_path}")
        exists = self.client.check(remote_path)
        if exists:
            logger.info(Colorizer.green(f"✓ File exists: {remote_path}"))
        else:
            logger.info(f"File not found: {remote_path}")
        return exists

    def delete_file(self, remote_path: str) -> bool:
        try:
            logger.info(f"⏳ Deleting file: {remote_path}")
            self.client.clean(remote_path)
            logger.info(Colorizer.green(f"✓ File deleted successfully: {remote_path}"))
            return True
        except Exception as e:
            logger.error(
                Colorizer.red(f"✗ Failed to delete file {remote_path}: {str(e)}")
            )
            return False

    def get_upload_status(self):
        """Get current upload status"""
        return [
            {"file": file, **status} for file, status in self.current_uploads.items()
        ]
