from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtCore import Qt


class About(QWidget):  # Inherit from QWidget, not QMainWindow
    """A simple 'About' page displaying application information."""

    def __init__(self) -> None:
        """Initializes the About page."""
        super().__init__()

        # Use self as the main widget, no need for a central widget in QWidget
        layout: QVBoxLayout = QVBoxLayout(self)

        about_text: str = """
        <table style="border-collapse: collapse;">
            <tr>
                <td style="padding-right: 30px;">Full Screen Tracer:</td>
                <td>Record screen and audio, then upload to WebDAV</td>
            </tr>
            <tr>
                <td style="padding-right: 30px;">Version:</td>
                <td>0.0.1</td>
            </tr>
            <tr>
                <td style="padding-right: 30px;">Author:</td>
                <td>Jeff Zuo</td>
            </tr>
            <tr>
                <td style="padding-right: 30px;">Email:</td>
                <td>jeffordszuo@gmail.com</td>
            </tr>
            <tr>
                <td style="padding-right: 30px;">GitHub:</td>
                <td>https://github.com/JeffZuo953/full-screen-track</td>
            </tr>
        </table>
        """

        about_text_edit: QTextEdit = QTextEdit(self)
        about_text_edit.setHtml(about_text)
        about_text_edit.setReadOnly(True)
        about_text_edit.setStyleSheet("""
            QTextEdit {
                color: white;
                font-size: 26px;
                border: none;
                background-color: transparent;
            }
        """)
        about_text_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addStretch(1)
        layout.addWidget(about_text_edit)
        layout.addStretch(1)
