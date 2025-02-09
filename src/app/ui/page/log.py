from __future__ import annotations

import html
import os
import re
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from src.app.ui.custom_dialog import CustomDialog
from datetime import datetime, timedelta


class LogFileViewer(QTextEdit):
    """A custom QTextEdit for viewing log files with colored output."""

    def __init__(self) -> None:
        """Initializes the LogFileViewer."""
        super().__init__()
        self.setReadOnly(True)
        self.setAcceptRichText(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

    def load_file(self, filename: str, chunk_size: int = 4096) -> None:
        """
        Loads and displays a log file.  Reads the file in reverse to show
        the latest logs first.

        Args:
            filename: The path to the log file.
            chunk_size: The size of chunks to read (in bytes).
        """
        self.clear()
        try:
            with open(filename, "rb") as f:
                f.seek(0, 2)
                filesize: int = f.tell()

                chunks: list[bytes] = []
                pos: int = filesize
                while pos > 0:
                    chunk_size = min(chunk_size, pos)
                    pos -= chunk_size
                    f.seek(pos)
                    chunks.append(f.read(chunk_size))

            content: str = b"".join(reversed(chunks)).decode("utf-8")
            colored_html: str = self.parse_color_text(content)
            self.setHtml(colored_html)

            # Move scrollbar to bottom
            scrollbar = self.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

        except Exception as e:
            self.setPlainText(f"Error loading file: {str(e)}")

    def parse_color_text(self, text: str) -> str:
        """
        Parses ANSI escape codes for colors and converts them to HTML.

        Args:
            text: The text containing ANSI escape codes.

        Returns:
            The HTML-formatted text with colors.
        """
        color_pattern = re.compile(r"\033\[(\d+)m(.*?)\033\[0m")
        result: list[str] = ["<pre>"]  # Use <pre> to preserve formatting
        start: int = 0

        for match in color_pattern.finditer(text):
            # Escape HTML in non-colored text
            non_colored_part: str = html.escape(text[start:match.start()])
            result.append(non_colored_part)

            color_code: int = int(match.group(1))
            # Escape HTML in colored text
            colored_text: str = html.escape(match.group(2))
            color: QColor = self.get_color_from_code(color_code)
            result.append(
                f'<span style="color: {color.name()};">{colored_text}</span>')
            start = match.end()

        # Append remaining text
        result.append(html.escape(text[start:]))
        result.append("</pre>")
        return "".join(result)

    def get_color_from_code(self, color_code: int) -> QColor:
        """
        Maps ANSI color codes to QColor objects.

        Args:
            color_code: The ANSI color code.

        Returns:
            The corresponding QColor object.
        """
        color_map: dict[int, QColor] = {
            31: QColor(255, 0, 0),  # 红色
            32: QColor(0, 255, 0),  # 绿色
            33: QColor(255, 255, 0),  # 黄色
            34: QColor(0, 0, 255),  # 蓝色
            35: QColor(255, 0, 255),  # 紫色
            36: QColor(0, 255, 255),  # 青色
            37: QColor(255, 255, 255),  # 白色
        }
        return color_map.get(color_code, QColor(0, 0, 0))


class Log(QWidget):
    """A widget for displaying and managing log files."""

    def __init__(self, log_path: str = ".\\log") -> None:
        """
        Initializes the Log widget.

        Args:
            log_path: The directory containing the log files.
        """
        super().__init__()
        self.log_path: str = log_path
        self.initUI()

    def initUI(self) -> None:
        """Initializes the user interface."""
        # Create outer layout with margins
        outer_layout: QVBoxLayout = QVBoxLayout(self)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        outer_layout.setSpacing(10)

        # Create main content widget
        content_widget: QWidget = QWidget()
        layout: QGridLayout = QGridLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # File selection combo and controls layout
        controls_layout: QHBoxLayout = QHBoxLayout()

        # Left side: File combo box
        self.file_combo: QComboBox = QComboBox()
        self.file_combo.setMinimumWidth(300)
        self.file_combo.setStyleSheet("""
            QComboBox {
                color: white;
                background-color: #2b2b2b;
                border: 1px solid #3c3c3c;
                padding: 5px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { color: white; }
            QComboBox QAbstractItemView {
                color: white;
                background-color: #2b2b2b;
                selection-background-color: #3c3c3c;
            }
            """)

        # Right side: Buttons container
        buttons_layout: QHBoxLayout = QHBoxLayout()

        # Button style
        pushButtonStyle: str = """
            QPushButton {
                color: white;
                background-color: #2b2b2b;
                border: 1px solid #3c3c3c;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
            }
        """

        # Create buttons
        self.refresh_btn: QPushButton = QPushButton("Load Logs")
        self.refresh_btn.setStyleSheet(pushButtonStyle)
        self.refresh_btn.clicked.connect(self.scan_log_files)

        self.refresh_current_btn: QPushButton = QPushButton("Refresh Log")
        self.refresh_current_btn.setStyleSheet(pushButtonStyle)
        self.refresh_current_btn.clicked.connect(self.refresh_current_log)

        self.clear_old_btn: QPushButton = QPushButton("Clear Old")
        self.clear_old_btn.setStyleSheet(pushButtonStyle)
        self.clear_old_btn.clicked.connect(self.clear_old_logs)

        # Add buttons to buttons layout
        buttons_layout.addWidget(self.refresh_btn)
        buttons_layout.addWidget(self.refresh_current_btn)
        buttons_layout.addWidget(self.clear_old_btn)
        buttons_layout.addStretch()  # Push buttons to the left

        # Add widgets to controls layout with proper proportions
        controls_layout.addWidget(self.file_combo,
                                  stretch=1)  # Takes 50% of space
        controls_layout.addLayout(buttons_layout,
                                  stretch=1)  # Takes 50% of space

        self.viewer: LogFileViewer = LogFileViewer()

        # Update grid layout
        layout.addLayout(controls_layout, 0, 0, 1, 2)
        layout.addWidget(self.viewer, 1, 0, 1, 2)

        # Set column stretching
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 0)
        layout.setRowStretch(1, 1)

        # Add content widget to outer layout
        outer_layout.addWidget(content_widget)

        # Connect signals
        self.file_combo.currentTextChanged.connect(self.load_selected_file)

        # Initial file scan
        self.scan_log_files()

    def scan_log_files(self) -> None:
        """Scans the log directory and populates the file selection combo box."""
        self.file_combo.clear()

        for root, _, files in os.walk(self.log_path):
            for file in files:
                if file.endswith(".log"):
                    full_path: str = os.path.join(root, file)
                    self.file_combo.addItem(full_path)

    def load_selected_file(self, filename: str) -> None:
        """
        Loads the selected log file into the viewer.

        Args:
            filename: The path to the log file.
        """
        if filename:
            self.viewer.load_file(filename)

    def clear_old_logs(self) -> None:
        """Clears log files older than 30 days."""
        message: str = ("This will delete all log files older than 30 days.\n"
                        "This operation cannot be undone.\n"
                        "Continue?")
        dialog: CustomDialog = CustomDialog("Confirm Delete", message, self)

        if dialog.show_question():
            deleted_count: int = 0
            thirty_days_ago: datetime = datetime.now() - timedelta(days=30)

            for root, _, files in os.walk(self.log_path):
                for file in files:
                    if file.endswith(".log"):
                        file_path: str = os.path.join(root, file)
                        file_time: datetime = datetime.fromtimestamp(
                            os.path.getmtime(file_path))

                        if file_time < thirty_days_ago:
                            try:
                                os.remove(file_path)
                                deleted_count += 1
                            except Exception as e:
                                print(f"Error deleting {file_path}: {e}")

            self.scan_log_files()  # Refresh file list

            dialog = CustomDialog(
                "Logs Deleted",
                f"Successfully deleted {deleted_count} old log files.",
                self,
            )
            dialog.show_information()

    def refresh_current_log(self) -> None:
        """Refresh the currently selected log file."""
        current_file: str = self.file_combo.currentText()
        if current_file:
            self.viewer.load_file(current_file)
