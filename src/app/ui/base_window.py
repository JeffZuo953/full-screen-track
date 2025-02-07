from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class BaseWindow(QMainWindow):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Set window icons
        icon_path = "src/app/ui/resources/icon.svg"
        self.setWindowIcon(QIcon(icon_path))
        
        # Common button style
        self.button_style = """
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
        
        # Setup custom title bar
        self.setup_title_bar(title)

    def setup_title_bar(self, title):

        # Title bar
        title_bar = QWidget()
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 5, 10, 5)

        # Window title with icon
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)

        title_icon = QLabel()
        title_icon.setPixmap(QIcon("src/app/ui/resources/icon.svg").pixmap(20, 20))
        title_layout.addWidget(title_icon)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        title_layout.addWidget(title_label)

        title_bar_layout.addWidget(title_container)
        title_bar_layout.addStretch()

        # Window controls
        min_button = QPushButton()
        min_button.setIcon(QIcon("src/app/ui/resources/minimize.svg"))
        min_button.clicked.connect(self.showMinimized)
        min_button.setFixedSize(30, 30)
        min_button.setStyleSheet(self.button_style)

        close_button = QPushButton()
        close_button.setIcon(QIcon("src/app/ui/resources/close.svg"))
        close_button.clicked.connect(self.close)
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet(self.button_style)

        title_bar_layout.addWidget(min_button)
        title_bar_layout.addWidget(close_button)

        self.main_layout.addWidget(title_bar)



    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
