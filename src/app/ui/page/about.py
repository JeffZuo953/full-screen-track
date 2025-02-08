from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QMainWindow
from PyQt5.QtCore import Qt

class About(QMainWindow):
    def __init__(self):
        super().__init__()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        about_text = """
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
                <td><a href="https://github.com/JeffZuo953/full-screen-track">https://github.com/JeffZuo953/full-screen-track</a></td>
            </tr>
        </table>
        """

        about_text_edit = QTextEdit(self)
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