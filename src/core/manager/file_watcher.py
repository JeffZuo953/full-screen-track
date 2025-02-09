from __future__ import annotations

import os
import time
from typing import Dict, List, Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent, DirCreatedEvent, FileCreatedEvent, DirDeletedEvent, FileDeletedEvent

from src.core.util.logger import logger
from src.core.uploader.webdav_client import WebDAVClient
from src.core.util.colorizer import Colorizer


class FileWatcher:
    """Watches a directory for file changes and uploads new files to WebDAV."""

    def __init__(self,
                 watch_dir: str,
                 webdav_client: WebDAVClient,
                 process_existing_files: bool = False) -> None:
        """
        Initializes the FileWatcher.

        Args:
            watch_dir: The directory to watch.
            webdav_client: The WebDAVClient instance to use for uploading.
            process_existing_files: Whether to process existing files on startup.
        """
        self.watch_dir: str = watch_dir
        self.webdav_client: WebDAVClient = webdav_client
        self.event_handler: WatchdogHandler = WatchdogHandler(
            self.webdav_client, self.watch_dir
        )
        self.observer: Observer = Observer()
        self.process_existing_files: bool = process_existing_files
        self.is_running: bool = False

    def start(self) -> None:
        """Starts the file watcher."""
        if self.is_running:
            logger.warning("FileWatcher is already running.")
            return

        self.observer.schedule(
            self.event_handler, self.watch_dir, recursive=True  # type: ignore
        )
        self.observer.start()
        self.is_running = True
        logger.info(f"FileWatcher started watching directory: {self.watch_dir}")

        if self.process_existing_files:
            self.process_existing()

    def stop(self) -> None:
        """Stops the file watcher."""
        if not self.is_running:
            logger.warning("FileWatcher is not running.")
            return

        self.observer.stop()
        self.observer.join()
        self.is_running = False
        logger.info("FileWatcher stopped.")

    def process_existing(self) -> None:
        """Processes existing files in the watched directory."""
        logger.info(f"Processing existing files in {self.watch_dir}")
        for root, _, files in os.walk(self.watch_dir):
            for file in files:
                local_path: str = os.path.join(root, file)
                relative_path: str = os.path.relpath(local_path, self.watch_dir)
                self.event_handler.upload_file(local_path, relative_path)

    def get_upload_status(self) -> List[Dict[str, str | float]]:
        """Gets the current upload status from the WebDAV client."""
        return self.webdav_client.get_upload_status()


class WatchdogHandler(FileSystemEventHandler):
    """Handles file system events."""

    def __init__(self, webdav_client: WebDAVClient, watch_dir: str) -> None:
        """
        Initializes the WatchdogHandler.

        Args:
            webdav_client: The WebDAVClient instance.
            watch_dir: The directory being watched.
        """
        super().__init__()
        self.webdav_client: WebDAVClient = webdav_client
        self.watch_dir: str = watch_dir
        self.last_event_time: float = 0.0
        self.throttle_delay: int = 1  # seconds

    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        """
        Called when a file or directory is created.

        Args:
            event: The event object.
        """
        if self._is_throttled():
            return

        if event.is_directory:
            logger.debug(f"Directory created: {event.src_path}")
        else:
            logger.info(Colorizer.blue(f"File created: {event.src_path}"))
            local_path: str = event.src_path
            relative_path: str = os.path.relpath(local_path, self.watch_dir)
            self.upload_file(local_path, relative_path)

    def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
        """
        Called when a file or directory is deleted. (Not used for now)

        Args:
            event: The event object.
        """
        if self._is_throttled():
            return

        if event.is_directory:
            logger.debug(f"Directory deleted: {event.src_path}")
        else:
            logger.info(Colorizer.blue(f"File deleted: {event.src_path}"))

    def on_modified(self, event: FileSystemEvent) -> None:
        """Called when a file is modified.

        Args:
            event: The FileSystemEvent object.
        """

        # on_modified is called when a file is created, so we only need to handle modification
        if self._is_throttled() or event.is_directory:
            return

        logger.info(Colorizer.blue(f"File modified: {event.src_path}"))
        local_path: str = event.src_path
        relative_path: str = os.path.relpath(local_path, self.watch_dir)
        self.upload_file(local_path, relative_path)

    def upload_file(self, local_path: str, relative_path: str) -> None:
        """
        Uploads a file to the WebDAV server.

        Args:
            local_path: The full local path of the file.
            relative_path: The path of the file relative to the watch directory.
        """
        remote_path: str = relative_path.replace("\\", "/")
        if self.webdav_client.upload_file(remote_path, local_path):
            logger.info(
                Colorizer.green(f"✓ File uploaded: {local_path} -> {remote_path}")
            )
        else:
            logger.error(Colorizer.red(f"✗ Failed to upload file: {local_path}"))

    def _is_throttled(self) -> bool:
        """Checks if the event should be throttled."""
        current_time: float = time.time()
        if current_time - self.last_event_time < self.throttle_delay:
            return True
        self.last_event_time = current_time
        return False 