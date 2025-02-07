from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QLabel,
    QSystemTrayIcon,
    QMenu,
    QPushButton,
    QHBoxLayout,
    QCheckBox,
    QWidgetAction,
)

from PyQt5.QtCore import Qt, QRect
from src.app.ui.page.about import About
from src.app.ui.page.config_editor import ConfigEditor
from src.app.ui.page.file_data import FileData
from src.app.ui.page.home.page import Home
from src.app.ui.page.log import Log
from src.core.controller.app import AppController
from src.app.ui.custom_dialog import CustomDialog
from PyQt5.QtGui import QIcon
import os
import sys


class MainWindow(QMainWindow):
    def __init__(self, app_controller: AppController):
        super().__init__()
        self.app_controller = app_controller

        # Get the application's root directory
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            application_path = sys._MEIPASS
        else:
            # Running in normal Python environment
            application_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

        # Set resource paths
        self.resource_path = os.path.join(application_path, "resources")

        # Remove window frame
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.setWindowTitle("Full Screen Tracer")
        self.setMinimumSize(800, 600)

        # Set window icon using absolute path
        icon_path = os.path.join(self.resource_path, "icon.svg")
        self.setWindowIcon(QIcon(icon_path))

        # Setup system tray
        self.setup_system_tray()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Add custom title bar
        title_bar = QWidget()
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 5, 10, 5)

        # Add window title with icon
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)

        title_icon = QLabel()
        title_icon.setPixmap(QIcon(os.path.join(self.resource_path, "icon.svg")).pixmap(20, 20))
        title_layout.addWidget(title_icon)

        title_label = QLabel("Full Screen Tracer")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        title_layout.addWidget(title_label)

        title_bar_layout.addWidget(title_container)
        title_bar_layout.addStretch()

        # Common button style for title bar buttons
        button_style = """
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

        # Add window control buttons with custom icons
        min_button = QPushButton()
        min_button.setIcon(QIcon(os.path.join(self.resource_path, "minimize.svg")))
        min_button.clicked.connect(self.showMinimized)
        min_button.setFixedSize(30, 30)
        min_button.setStyleSheet(button_style)

        max_button = QPushButton()
        max_button.setIcon(QIcon(os.path.join(self.resource_path, "maximize.svg")))
        max_button.clicked.connect(self.toggle_maximize)
        max_button.setFixedSize(30, 30)
        max_button.setStyleSheet(button_style)

        close_button = QPushButton()
        close_button.setIcon(QIcon(os.path.join(self.resource_path, "close.svg")))
        close_button.clicked.connect(self.close)
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet(button_style)

        exit_button = QPushButton()
        exit_button.setIcon(QIcon(os.path.join(self.resource_path, "turnoff.svg")))
        exit_button.clicked.connect(self.quit_application)
        exit_button.setFixedSize(30, 30)
        exit_button.setStyleSheet(button_style)

        # Add buttons to layout
        title_bar_layout.addWidget(min_button)
        title_bar_layout.addWidget(max_button)
        title_bar_layout.addWidget(close_button)
        title_bar_layout.addWidget(exit_button)

        layout.addWidget(title_bar)

        # Add tabs container without exit button
        tabs_container = QWidget()
        tabs_layout = QHBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setTabShape(QTabWidget.TabShape.Rounded)
        tabs_layout.addWidget(self.tabs)

        layout.addWidget(tabs_container)

        self.home = Home(app_controller)
        # Connect home page signals to tray icon updates
        self.home.record_state_changed.connect(self._sync_record_checkbox)
        self.home.upload_state_changed.connect(self._sync_upload_checkbox)

        self.config_editor = ConfigEditor()
        self.file_data = FileData(
            app_controller.file_model, app_controller.local_file_manager
        )
        self.log = Log()
        self.about = About()

        self.tabs.addTab(self.home, "Home")
        self.tabs.addTab(self.config_editor, "Config Editor")
        self.tabs.addTab(self.file_data, "File Data")
        self.tabs.addTab(self.log, "Log")
        self.tabs.addTab(self.about, "About")

        # Add resize related attributes
        self._resize_area_size = 10  # pixels for resize area detection
        self._is_resizing = False
        self._resize_start_pos = None
        self._window_start_geometry = None

    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())

        # Create tray menu with style
        tray_menu = QMenu()

        # Create record toggle checkbox
        self.record_checkbox = QCheckBox("On Record")
        self.record_checkbox.setChecked(False)
        self.record_checkbox.stateChanged.connect(self.toggle_record)

        self.upload_checkbox = QCheckBox("Auto Upload")
        self.upload_checkbox.setChecked(False)
        self.upload_checkbox.stateChanged.connect(self.toggle_upload)

        # Create widget actions
        record_action = QWidgetAction(tray_menu)
        record_action.setDefaultWidget(self.record_checkbox)
        tray_menu.addAction(record_action)

        upload_action = QWidgetAction(tray_menu)
        upload_action.setDefaultWidget(self.upload_checkbox)
        tray_menu.addAction(upload_action)

        tray_menu.addSeparator()

        # Add show/hide window action
        restore_action = tray_menu.addAction("Show Window")
        restore_action.triggered.connect(self.showNormal)

        tray_menu.addSeparator()

        # Add exit action
        quit_action = tray_menu.addAction("Exit")
        quit_action.triggered.connect(self.quit_application)

        # Set the tray menu
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Connect double click to restore
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def isInResizeArea(self, pos):
        """Check if position is in the resize area (bottom-right corner)"""
        window_rect = self.rect()
        bottom_right = window_rect.bottomRight()
        resize_rect = QRect(
            bottom_right.x() - self._resize_area_size,
            bottom_right.y() - self._resize_area_size,
            self._resize_area_size,
            self._resize_area_size,
        )
        return resize_rect.contains(pos)

    def _sync_record_checkbox(self, checked):
        """Sync tray record checkbox with home page state"""
        if self.record_checkbox.isChecked() != checked:
            self.record_checkbox.setChecked(checked)

    def _sync_upload_checkbox(self, checked):
        """Sync tray upload checkbox with home page state"""
        if self.upload_checkbox.isChecked() != checked:
            self.upload_checkbox.setChecked(checked)

    def toggle_record(self, checked):
        """Handle record toggle from tray menu"""
        if self.home.record_switch.isChecked() != checked:
            self.home.record_switch.setChecked(checked)

    def toggle_upload(self, checked):
        """Handle upload toggle from tray menu"""
        if self.home.auto_upload_switch.isChecked() != checked:
            self.home.auto_upload_switch.setChecked(checked)

    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()

    def closeEvent(self, event):
        """Override close event to minimize to tray instead of closing"""
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.quit_application()

    def quit_application(self):
        """Cleanup and quit application"""
        dialog = CustomDialog(
            "Exit Confirmation", "Are you sure you want to exit the application?", self
        )

        if dialog.show_question():
            self.app_controller.cleanup()
            self.tray_icon.hide()
            QApplication.quit()

    def mousePressEvent(self, event):
        """Handle mouse press for both dragging and resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.isInResizeArea(event.pos()):
                self._is_resizing = True
                self._resize_start_pos = event.globalPos()
                self._window_start_geometry = self.geometry()
            else:
                # Original window dragging code
                self._drag_pos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        """Update cursor shape and handle move events"""
        # Update cursor shape based on position
        if self.isInResizeArea(event.pos()):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        # Handle actual move events
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self._is_resizing:
                delta = event.globalPos() - self._resize_start_pos
                new_geometry = self._window_start_geometry
                new_width = new_geometry.width() + delta.x()
                new_height = new_geometry.height() + delta.y()

                new_width = max(new_width, self.minimumWidth())
                new_height = max(new_height, self.minimumHeight())

                self.setGeometry(
                    new_geometry.x(), new_geometry.y(), new_width, new_height
                )
            else:
                self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Reset resize state when mouse is released"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_resizing = False
            self._resize_start_pos = None
            self._window_start_geometry = None
        event.accept()

    def toggle_maximize(self):
        """Toggle window maximize/restore state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
