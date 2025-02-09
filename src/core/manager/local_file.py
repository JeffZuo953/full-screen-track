from __future__ import annotations
import os
import re
import time
from typing import Dict
import threading

from src.core.util.logger import logger
from src.core.manager.config import ConfigManager
from src.core.model.service.file_service import FileService

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class RecordingFileHandler(FileSystemEventHandler):
    """
    Handles file system events for recording files.
    """

    def __init__(self, manager: "LocalFileManager"):
        """
        Initializes the handler with a LocalFileManager instance.
        """
        self.manager = manager
        self.processing_files = set()
        self.file_stable_time = 1  # File stable detection time (seconds)

    def on_created(self, event):
        """
        Called when a file or directory is created.

        This method is triggered when a file is created, and it checks if the
        created file is a recording file (mp4 or mp3). If so, it moves all other files
        in the same directory to the target directory.
        """
        if not event.is_directory and event.src_path.endswith(
            (".mp4", ".mp3")):
            directory = os.path.dirname(event.src_path)
            self.manager.move_all_files_in_directory(
                directory, exclude_file=event.src_path)

    def on_modified(self, event):
        """
        Called when a file or directory is modified.

        This method is triggered when a file is changed, and it checks if the
        modified file is a recording file (mp4 or mp3). If so, it starts a
        thread to check the file's stability.
        """
        # 注释掉 on_modified 中的代码，因为移动文件的逻辑已移至 on_created
        # if not event.is_directory and event.src_path.endswith(
        #     (".mp4", ".mp3")):

        #     if event.src_path not in self.processing_files:
        #         self.processing_files.add(event.src_path)
        #         threading.Thread(target=self._check_file_stable,
        #                          args=(event.src_path, )).start()
        pass

    # def _check_file_stable(self, filepath):
    #     """
    #     Checks if a file has stopped being written to.

    #     This method periodically checks the file size to determine if it has
    #     stopped growing, indicating that the recording is complete.
    #     """
    #     try:
    #         initial_size = os.path.getsize(filepath)
    #         while True:
    #             time.sleep(self.file_stable_time)
    #             current_size = os.path.getsize(filepath)
    #             if current_size == initial_size:
    #                 self.manager.move_tmp_file(filepath)
    #                 break
    #             initial_size = current_size
    #     except Exception as e:
    #         logger.error(f"File monitoring error: {e}")
    #     finally:
    #         self.processing_files.discard(filepath)


class LocalFileManager:
    """
    Manages local recording files, including monitoring, moving, and
    database updates.
    """

    def __init__(self, config: ConfigManager, file_service: FileService):
        """
        Initializes the manager with configuration and a file service.
        """
        logger.debug("Initializing LocalFileManager")
        self.config = config
        self.file_service = file_service
        self.db_path = "db/file_tracker.db"
        self._setup_file_watcher()
        self._scan_lock = threading.Lock()
        self._last_scan_time = 0
        self._scan_interval = 3  # Throttling interval (seconds)

    def _device_name_to_path(self, name: str) -> str:
        """
        Sanitizes a device name for use in file paths.
        """
        sanitized = re.sub(r'[\\/*?:"<>|]', "", name).strip()
        return sanitized

    def _setup_file_watcher(self) -> None:
        """
        Sets up a file watcher to monitor the temporary directory for
        new recording files.
        """
        logger.debug("Setting up file monitoring")
        base_path = self.config.get_storage_config()["local_path"]
        tmp_path = ".tmp"
        logger.debug(f"Creating temporary directory: {tmp_path}")
        os.makedirs(tmp_path, exist_ok=True)

        self.event_handler = RecordingFileHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, tmp_path, recursive=True)
        logger.debug("Starting file monitoring")
        self.observer.start()

    def scan_recordings(self) -> None:
        """
        Scans the recording directory for new or modified files, with
        throttling to prevent excessive scanning.
        """
        with self._scan_lock:
            current_time = time.time()
            if current_time - self._last_scan_time < self._scan_interval:
                return

            logger.debug(
                "Scanning recording directory for new or modified files")

            new_files = []
            base_path = self.config.get_storage_config()["local_path"]
            device_path = os.path.join(base_path,
                                       self.config.get_device_name()).replace(
                                           "\\", "/")

            for root, _, files in os.walk(device_path):
                for file in files:
                    local_path = os.path.join(root, file).replace("\\", "/")
                    file_info = self._get_file_info(local_path)

                    if self._should_process_file(file_info):
                        new_files.append(file_info)
                        self.file_service.register_file(file_info)

            logger.debug(f"Found {len(new_files)} new or modified files")

            self._last_scan_time = current_time
            return

    def move_tmp_file(self, filepath):
        """
        Moves a completed recording file to its final destination.

        This method constructs the destination path by replacing the ".tmp"
        directory in the filepath with the configured local storage path.
        """
        try:
            if os.path.exists(filepath):
                # Construct target path
                target_path = filepath.replace(
                    ".tmp",
                    self.config.get_storage_config()["local_path"])

                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                os.rename(filepath, target_path)
                logger.info(
                    f"Moved completed file: {filepath} -> {target_path}")
        except Exception as e:
            logger.error(f"Failed to move file: {e}")

    def move_all_files_in_directory(self, directory, exclude_file=None):
        """
        Moves all files in the specified directory to their final locations,
        excluding the specified file.
        """
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path) and file_path != exclude_file:
                    # Construct target path
                    target_path = file_path.replace(
                        ".tmp",
                        self.config.get_storage_config()["local_path"])

                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    os.rename(file_path, target_path)
                    logger.info(
                        f"Moved completed file: {file_path} -> {target_path}")
        except Exception as e:
            logger.error(f"Failed to move files in directory: {e}")

    def _get_file_info(self, local_path: str) -> Dict:
        """
        Extracts file information for a given local file path.
        """
        logger.debug(f"Getting file information for {local_path}")
        rel_path = os.path.relpath(
            local_path,
            self.config.get_storage_config()["local_path"]).replace("\\", "/")
        web_dav_path = self.config.get_webdav_config()["remote_path"]
        remote_path = f"{web_dav_path.rstrip('/')}/{rel_path}"

        return {
            "local_path": local_path,
            "remote_path": remote_path,
            "file_size": os.path.getsize(local_path),
            "last_modified": os.path.getmtime(local_path),
        }

    def _should_process_file(self, file_info: Dict) -> bool:
        """
        Determines whether a file should be processed based on its
        database record.
        """
        logger.debug(
            f"Determining if file {file_info['local_path']} should be processed"
        )
        record = self.file_service.get_file(file_info["local_path"])

        # If file exists but was marked as non-existent, update its status
        if record and not record.exists_locally:
            self.file_service.check_file_exists(file_info["local_path"])

        if not record:
            return True

        should_process = record.status != "uploaded"
        return should_process

    def delete_old_files(self, days: int) -> tuple[int, int]:
        """
        Deletes local files older than a specified number of days.
        
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

    def move_all_tmp_files(self):
        """
        Moves all files from the temporary directory and its subdirectories to their final locations.
        """
        tmp_path = ".tmp"
        for root, dirs, files in os.walk(tmp_path):
            for file in files:
                print(file)
                if file.endswith((".mp4", ".mp3")):
                    temp_file = os.path.join(root, file)
                    self.move_tmp_file(temp_file)

    def __del__(self):
        """
        Stops the file monitoring observer when the manager is deleted.
        """
        if hasattr(self, "observer"):
            self.observer.stop()
            self.observer.join()
