# src/core/manager/app_controller.py
from src.core.util.logger import logger

import sys
from time import sleep
from datetime import datetime
from typing import Optional
from src.core.util.colorizer import Colorizer
from src.core.manager.config import ConfigManager
from src.core.manager.recorder import RecorderManager
from src.core.manager.local_file import LocalFileManager
from src.core.manager.uploader import UploaderManager
from src.core.model.file import FileModel
from src.core.util.logger import logger


class AppController:
    """Main controller for the application"""

    def __init__(self):
        self.recorder_manager: Optional[RecorderManager] = None
        self.local_file_manager: Optional[LocalFileManager] = None
        self.uploader_manager: Optional[UploaderManager] = None
        self.config: Optional[ConfigManager] = None
        self.file_model: Optional[FileModel] = None
        self.is_gui_mode: bool = False
        self.is_polling: bool = False
        self.is_recording: bool = False

    def setup_config(self) -> None:
        """Initialize the configuration"""
        logger.debug("Initializing the configuration")
        try:
            self.config = ConfigManager()
            logger.info(Colorizer.green("✓ Configuration loaded successfully"))
        except Exception as e:
            logger.error(Colorizer.red(f"✗ Configuration loaded error: {e}"))
            sys.exit(1)

    def setup_components(self) -> None:
        """Initialize components"""
        logger.debug("Initializing components")
        try:
            # Initialize FileModel, LocalFileManager, and UploaderManager
            self.file_model = FileModel(db_path="db/file_tracker.db")
            self.local_file_manager = LocalFileManager(self.config, self.file_model)
            self.uploader_manager = UploaderManager(self.config, self.file_model)

            # Initialize the recorder manager
            self.recorder_manager = RecorderManager(self.config)

            logger.info(Colorizer.green("✓ Components initialized successfully"))
        except Exception as e:
            logger.error(Colorizer.red(f"✗ Components initialization failed: {e}"))
            sys.exit(1)

    def setup(self):
        if not self.config:
            self.setup_config()
        if not self.local_file_manager:
            self.setup_components()

    def start_recording(self) -> None:
        """Start recording only"""
        logger.info("Starting recording...")
        self.is_recording = True
        self.recorder_manager.start_recording()

    def stop_recording(self) -> None:
        """Stop recording"""
        logger.info("Stopping recording...")
        if self.recorder_manager:
            self.recorder_manager.stop_recording()
        self.is_recording = False
        logger.debug("All recording processes stopped")

    def start_polling(self) -> None:
        """Start upload polling"""
        logger.info("Starting upload polling...")
        self.is_polling = True
        self.poll_and_sync()

    def stop_polling(self) -> None:
        """Stop upload polling"""
        logger.info("Stopping upload polling...")
        self.is_polling = False

    def cleanup(self) -> None:
        """Clean up resources"""
        self.stop_recording()
        self.stop_polling()
        logger.debug("AppController: cleanup completed")

    def start_polling(self) -> None:
        """Start polling for new files and upload them"""
        self.poll_and_sync()

    def poll_and_sync(self) -> None:
        """Poll for new files and upload them"""
        while True:
            try:
                logger.info(
                    Colorizer.cyan(f"Polling for new files at {datetime.now()}...")
                )
                self.scan_and_sync()
                sleep(self.config.get_segment_duration())
            except Exception as e:
                logger.error(Colorizer.red(f"✗ Polling error: {e}"))
                sleep(30)  # Wait before retry

    def manual_upload(self) -> None:
        """Manually trigger file synchronization"""
        self.setup()
        try:
            logger.info(
                Colorizer.cyan(f"Manually sync for new files at {datetime.now()}...")
            )
            self.scan_and_sync()
        except Exception as e:
            logger.error(Colorizer.red(f"✗ Manual sync error: {e}"))

    def scan_and_sync(self) -> None:
        """Scan and sync files"""
        logger.debug(Colorizer.cyan("Scanning for new files..."))
        self.local_file_manager.scan_recordings()
        self.uploader_manager.sync_pending_files()

    def signal_handler(self, signum, frame) -> None:
        """Handle signals"""
        logger.warning(
            Colorizer.yellow("Received termination signal, cleaning up resources...")
        )
        self.cleanup()
