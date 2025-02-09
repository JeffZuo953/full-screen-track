from __future__ import annotations

import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QMainWindow,
)

from src.app.ui.custom_dialog import CustomDialog
from src.core.manager.config import ConfigManager


class ConfigEditor(QMainWindow):
    """Configuration editor window."""

    def __init__(self) -> None:
        """Initialize the ConfigEditor."""
        super().__init__()
        self.setup_config_ui()

    def setup_config_ui(self) -> None:
        """Setup the configuration interface."""

        main_widget: QWidget = QWidget()
        self.setCentralWidget(main_widget)
        layout: QVBoxLayout = QVBoxLayout(main_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        def createItem(label_text: str,
                       explanation_text: str) -> tuple[QHBoxLayout, QLineEdit]:
            """Create a labeled input item."""

            # Create label and input box
            label_layout: QHBoxLayout = QHBoxLayout()

            label_widget: QLabel = QLabel(label_text)
            label_widget.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label_layout.addWidget(label_widget)

            explanation_widget: QLabel = QLabel(explanation_text)
            explanation_widget.setAlignment(Qt.AlignmentFlag.AlignRight)
            label_layout.addWidget(explanation_widget)

            edit: QLineEdit = QLineEdit()
            edit.setStyleSheet("QLineEdit { color: white; }")

            return label_layout, edit

        self.device_name_label: QHBoxLayout
        self.device_name_edit: QLineEdit
        self.device_name_label, self.device_name_edit = createItem(
            "Device Name:", "Enter the name of the device. Example: Camera1")
        self.fps_label: QHBoxLayout
        self.fps_edit: QLineEdit
        self.fps_label, self.fps_edit = createItem(
            "FPS:", "Set the frames per second. Example: 30")
        self.segment_duration_label: QHBoxLayout
        self.segment_duration_edit: QLineEdit
        self.segment_duration_label, self.segment_duration_edit = createItem(
            "Segment Duration:",
            "Set the duration of each video segment in seconds. Example: 60",
        )
        self.webdav_url_label: QHBoxLayout
        self.webdav_url_edit: QLineEdit
        self.webdav_url_label, self.webdav_url_edit = createItem(
            "WebDAV URL:",
            "Enter the WebDAV server URL. Example: https://webdav.example.com",
        )
        self.webdav_username_label: QHBoxLayout
        self.webdav_username_edit: QLineEdit
        self.webdav_username_label, self.webdav_username_edit = createItem(
            "WebDAV Username:", "Enter the WebDAV username. Example: user123")
        self.webdav_password_label: QHBoxLayout
        self.webdav_password_edit: QLineEdit
        self.webdav_password_label, self.webdav_password_edit = createItem(
            "WebDAV Password:",
            "Enter the WebDAV password. Example: password123")
        self.remote_path_label: QHBoxLayout
        self.remote_path_edit: QLineEdit
        self.remote_path_label, self.remote_path_edit = createItem(
            "Remote Path:",
            "Set the remote path on the WebDAV server. Example: /videos",
        )
        self.local_path_label: QHBoxLayout
        self.local_path_edit: QLineEdit
        self.local_path_label, self.local_path_edit = createItem(
            "Local Path:",
            "Set the local path to store videos. Example: C:/videos")
        self.sample_rate_label: QHBoxLayout
        self.sample_rate_edit: QLineEdit
        self.sample_rate_label, self.sample_rate_edit = createItem(
            "Sample Rate:", "Set the audio sample rate. Example: 44100")
        self.log_level_label: QHBoxLayout
        self.log_level_edit: QLineEdit
        self.log_level_label, self.log_level_edit = createItem(
            "Log Level:",
            "Set the logging level. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL",
        )
        self.ffmpeg_label: QHBoxLayout
        self.ffmpeg_edit: QLineEdit
        self.ffmpeg_label, self.ffmpeg_edit = createItem(
            "FFmpeg Log:",
            "Enable or disable FFmpeg logging. Options: True, False")

        # Use the content_layout from BaseWindow instead of creating a new layout
        layout.addLayout(self.device_name_label)
        layout.addWidget(self.device_name_edit)
        layout.addLayout(self.fps_label)
        layout.addWidget(self.fps_edit)
        layout.addLayout(self.segment_duration_label)
        layout.addWidget(self.segment_duration_edit)
        layout.addLayout(self.webdav_url_label)
        layout.addWidget(self.webdav_url_edit)
        layout.addLayout(self.webdav_username_label)
        layout.addWidget(self.webdav_username_edit)
        layout.addLayout(self.webdav_password_label)
        layout.addWidget(self.webdav_password_edit)
        layout.addLayout(self.remote_path_label)
        layout.addWidget(self.remote_path_edit)
        layout.addLayout(self.local_path_label)
        layout.addWidget(self.local_path_edit)
        layout.addLayout(self.sample_rate_label)
        layout.addWidget(self.sample_rate_edit)
        layout.addLayout(self.log_level_label)
        layout.addWidget(self.log_level_edit)
        layout.addLayout(self.ffmpeg_label)
        layout.addWidget(self.ffmpeg_edit)

        # Add save button
        self.save_button: QPushButton = QPushButton("Save")
        self.save_button.clicked.connect(self.save_config)
        layout.addWidget(self.save_button)

        try:
            self.load_config()
        except Exception as e:
            dialog: CustomDialog = CustomDialog(
                "Error", f"Failed to load configuration: {e}", self)
            dialog.show_information()

    def load_config(self) -> None:
        """Load configuration from file."""
        config_manager: ConfigManager = ConfigManager()
        config: dict = config_manager.config

        self.device_name_edit.setText(config.get("device_name", ""))
        self.fps_edit.setText(str(config.get("fps", "")))
        self.segment_duration_edit.setText(
            str(config.get("segment_duration", "")))
        self.webdav_url_edit.setText(config.get("webdav", {}).get("url", ""))
        self.webdav_username_edit.setText(
            config.get("webdav", {}).get("username", ""))
        self.webdav_password_edit.setText(
            config.get("webdav", {}).get("password", ""))
        self.remote_path_edit.setText(
            config.get("webdav", {}).get("remote_path", ""))
        self.local_path_edit.setText(
            config.get("storage", {}).get("local_path", ""))
        self.sample_rate_edit.setText(
            str(config.get("audio", {}).get("sample_rate", "")))
        self.log_level_edit.setText(config.get("log", {}).get("level", ""))
        self.ffmpeg_edit.setText(str(config.get("log", {}).get("ffmpeg", "")))

    def save_config(self) -> None:
        """Save configuration to file."""
        config: dict = {}
        try:
            config["device_name"] = self.device_name_edit.text()
            config["fps"] = int(self.fps_edit.text())
            config["segment_duration"] = int(self.segment_duration_edit.text())
            config["webdav"] = {
                "url": self.webdav_url_edit.text(),
                "username": self.webdav_username_edit.text(),
                "password": self.webdav_password_edit.text(),
                "remote_path": self.remote_path_edit.text(),
            }
            config["storage"] = {"local_path": self.local_path_edit.text()}
            config["audio"] = {
                "sample_rate": int(self.sample_rate_edit.text())
            }
            config["log"] = {
                "level": self.log_level_edit.text(),
                "ffmpeg": self.ffmpeg_edit.text() == "True",
            }

            try:
                with open("config.json", "w") as f:
                    json.dump(config, f, indent=4)
                dialog: CustomDialog = CustomDialog(
                    "Success", "Configuration saved successfully!", self)
                dialog.show_information()

            except Exception as e:
                dialog: CustomDialog = CustomDialog(
                    "Error", f"Failed to save configuration: {e}", self)
                dialog.show_information()

        except ValueError as e:
            dialog: CustomDialog = CustomDialog("Error", f"Invalid input: {e}",
                                                self)
            dialog.show_information()
        except Exception as e:
            dialog: CustomDialog = CustomDialog(
                "Error", f"Failed to set configuration: {e}", self)
            dialog.show_information()
