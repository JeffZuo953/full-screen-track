from __future__ import annotations
import os
import time
from typing import Dict, List

from src.core.util.logger import logger
from src.core.manager.config import ConfigManager
from src.core.model.service.file_service import FileService  # 新导入

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class RecordingFileHandler(FileSystemEventHandler):
    def __init__(self, manager: "LocalFileManager"):
        self.manager: LocalFileManager = manager
        self.processing_files = set()

    def on_modified(self, event) -> None:
        if not event.is_directory and event.src_path.endswith((".mp4", ".wav")):
            if event.src_path not in self.processing_files:
                self.processing_files.add(event.src_path)
                self._handle_file_completion(event.src_path)

    def _handle_file_completion(self, filepath) -> None:
        time.sleep(1)  # Wait for file to be fully written
        if os.path.exists(filepath):
            try:
                final_dir = os.path.dirname(os.path.dirname(filepath))
                self.manager._move_completed_recording(filepath, final_dir)
            finally:
                self.processing_files.remove(filepath)


class LocalFileManager:
    """Handles file monitoring and database updates locally"""

    def __init__(self, config: ConfigManager, file_service: FileService):
        self.config = config
        self.file_service = file_service  # 更改为 file_service
        self.db_path = "db/file_tracker.db"
        self._setup_file_watcher()

    def _setup_file_watcher(self) -> None:
        base_path = self.config.get_storage_config()["local_path"]
        device_path = os.path.join(base_path, self.config.get_device_name())
        tmp_path = os.path.join(device_path, ".tmp")
        os.makedirs(tmp_path, exist_ok=True)

        self.event_handler = RecordingFileHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, tmp_path, recursive=False)
        self.observer.start()

    def _move_completed_recording(self, temp_path: str, final_dir: str) -> None:
        try:
            if os.path.exists(temp_path):
                filename = os.path.basename(temp_path)
                final_path = os.path.join(final_dir, filename)
                os.rename(temp_path, final_path)
                logger.info(f"Moved recording: {temp_path} -> {final_path}")
                self.scan_recordings()  # Refresh file list
        except Exception as e:
            logger.error(f"Failed to move recording: {e}")

    def scan_recordings(self) -> List[Dict]:
        """Scan recording directory for new or modified files"""
        logger.debug("Scanning recording directory for new or modified files")

        new_files = []
        base_path = self.config.get_storage_config()["local_path"]
        device_path = os.path.join(base_path, self.config.get_device_name()).replace(
            "\\", "/"
        )

        for root, _, files in os.walk(device_path):
            for file in files:
                local_path = os.path.join(root, file).replace("\\", "/")
                file_info = self._get_file_info(local_path)

                if self._should_process_file(file_info):
                    new_files.append(file_info)
                    self.file_service.register_file(file_info)

        logger.debug(f"Found {len(new_files)} new or modified files")
        return new_files

    def _get_file_info(self, local_path: str) -> Dict:
        """Get file information and status"""
        logger.debug(f"Getting file information for {local_path}")
        rel_path = os.path.relpath(
            local_path, self.config.get_storage_config()["local_path"]
        ).replace("\\", "/")
        web_dav_path = self.config.get_webdav_config()["remote_path"]
        remote_path = f"{web_dav_path.rstrip('/')}/{rel_path}"

        return {
            "local_path": local_path,
            "remote_path": remote_path,
            "file_size": os.path.getsize(local_path),
            "last_modified": os.path.getmtime(local_path),
        }

    def _should_process_file(self, file_info: Dict) -> bool:
        """Determine if file should be processed based on database records"""
        logger.debug(
            f"Determining if file {file_info['local_path']} should be processed"
        )
        record = self.file_service.get_file(file_info["local_path"])

        # If file exists but was marked as non-existent, update its status
        if record and not record.exists_locally:
            self.file_service.check_file_exists(file_info["local_path"])

        if not record:
            return True

        return record.status != "uploaded"

    def delete_old_files(self, days: int) -> tuple[int, int]:
        """Delete local files older than specified days
        
        Args:
            days: Number of days to keep files
            
        Returns:
            Tuple of (deleted_count, failed_count)
        """
        deleted_count = 0
        failed_count = 0
        
        old_files = self.file_service.get_old_files(days)
        for file in old_files:
            try:
                if os.path.exists(file.local_path):
                    os.remove(file.local_path)
                    self.file_service.check_file_exists(file.local_path)
                    deleted_count += 1
                    logger.info(f"Deleted old file: {file.local_path}")
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to delete {file.local_path}: {e}")
                
        return deleted_count, failed_count

    def __del__(self):
        if hasattr(self, "observer"):
            self.observer.stop()
            self.observer.join()
