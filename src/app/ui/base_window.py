from __future__ import annotations

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon, QMouseEvent


class BaseWindow(QMainWindow):
    """Base class for main windows with a custom title bar."""

    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        """
        Initializes the BaseWindow.

        Args:
            title: The title of the window.
            parent: The parent widget (optional).
        """
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Set window icons
        icon_path: str = "src/app/ui/resources/icon.svg"
        self.setWindowIcon(QIcon(icon_path))

        # Common button style
        self.button_style: str = """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(139, 195, 74, 0.2);
                border-radius: 3px;
            }
        """
        self.main_layout = QVBoxLayout()  # Initialize main_layout
        central_widget = QWidget()  # Create a central widget
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)
        # Setup custom title bar
        self.setup_title_bar(title)
        self._drag_pos: QPoint | None = None

    def setup_title_bar(self, title: str) -> None:
        """Sets up the custom title bar."""

        # Title bar
        title_bar: QWidget = QWidget()
        title_bar_layout: QHBoxLayout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 5, 10, 5)

        # Window title with icon
        title_container: QWidget = QWidget()
        title_layout: QHBoxLayout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)

        title_icon: QLabel = QLabel()
        title_icon.setPixmap(
            QIcon("src/app/ui/resources/icon.svg").pixmap(20, 20))
        title_layout.addWidget(title_icon)

        title_label: QLabel = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        title_layout.addWidget(title_label)

        title_bar_layout.addWidget(title_container)
        title_bar_layout.addStretch()

        # Window controls
        min_button: QPushButton = QPushButton()
        min_button.setIcon(QIcon("src/app/ui/resources/minimize.svg"))
        min_button.clicked.connect(self.showMinimized)
        min_button.setFixedSize(30, 30)
        min_button.setStyleSheet(self.button_style)

        close_button: QPushButton = QPushButton()
        close_button.setIcon(QIcon("src/app/ui/resources/close.svg"))
        close_button.clicked.connect(self.close)
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet(self.button_style)

        title_bar_layout.addWidget(min_button)
        title_bar_layout.addWidget(close_button)

        self.main_layout.addWidget(title_bar)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handles mouse press events for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handles mouse move events for dragging."""
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
