from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class CustomDialog(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setFixedSize(400, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar
        title_bar = QWidget()
        title_bar.setStyleSheet("background-color: #2e2e2e;")
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 5, 10, 5)

        # Title label
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()

        # Close button
        close_button = QPushButton()
        close_button.setIcon(QIcon("src/app/ui/resources/close.svg"))
        close_button.clicked.connect(self.reject)
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet(
            """
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
        )
        title_bar_layout.addWidget(close_button)
        layout.addWidget(title_bar)

        # Content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-size: 12px; color: white;")
        content_layout.addWidget(message_label)
        content_layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Common button style
        button_style = """
            QPushButton {
                background-color: #8bc34a;
                color: white;
                border: none;
                padding: 8px 16px;
                min-width: 80px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7cb342;
            }
            QPushButton:pressed {
                background-color: #689f38;
            }
        """

        self.yes_button = QPushButton("Yes")
        self.no_button = QPushButton("No")
        self.ok_button = QPushButton("OK")

        self.yes_button.setStyleSheet(button_style)
        self.no_button.setStyleSheet(button_style)
        self.ok_button.setStyleSheet(button_style)

        button_layout.addWidget(self.yes_button)
        button_layout.addWidget(self.no_button)
        button_layout.addWidget(self.ok_button)

        self.yes_button.clicked.connect(self.accept)
        self.no_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self.accept)

        content_layout.addLayout(button_layout)
        layout.addWidget(content)

        # For dragging
        self._drag_pos = None

    def show_question(self):
        """Show as a question dialog with Yes/No buttons"""
        self.yes_button.show()
        self.no_button.show()
        self.ok_button.hide()
        return self.exec_() == QDialog.DialogCode.Accepted

    def show_information(self):
        """Show as an information dialog with OK button"""
        self.yes_button.hide()
        self.no_button.hide()
        self.ok_button.show()
        return self.exec_() == QDialog.DialogCode.Accepted

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
