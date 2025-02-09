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
    QSizeGrip,
)

from PyQt5.QtCore import Qt, QRect, QPoint, QSize
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


class ResizableButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(20, 20)  # 设置按钮的最小尺寸
        self.dragging = False
        self.drag_start_pos = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_pos = event.globalPos() - self.parent().pos()
            # 如果父部件不是直接的父级，可能需要更复杂的计算
            # self.drag_start_pos = event.globalPos() - self.mapToGlobal(self.pos())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = event.globalPos() - self.drag_start_pos
            # 限制窗口的最小尺寸
            new_rect = QRect(self.parent().pos(), new_pos)
            if new_rect.width() >= self.parent().minimumWidth() and \
               new_rect.height() >= self.parent().minimumHeight():
                self.parent().setGeometry(new_rect)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)


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

        # Remove window frame AND set stay-on-top
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

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
        self.title_bar = QWidget()
        title_bar_layout = QHBoxLayout(self.title_bar)
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

        layout.addWidget(self.title_bar)

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
            app_controller.file_service, app_controller.local_file_manager
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

        # Create QSizeGrip and add to layout
        size_grip = QSizeGrip(self)
        layout.addWidget(size_grip, 0, Qt.AlignBottom | Qt.AlignRight)

        # 窗口拖动的起始位置
        self._drag_pos = None

    def showEvent(self, event):
        """Override showEvent to center the window after it's shown."""
        super().showEvent(event)
        self.center_window()

    def center_window(self):
        """Centers the window on the screen."""
        # Use availableGeometry to account for taskbars and other screen elements
        screen = QApplication.primaryScreen().availableGeometry()
        # OR, to center on a *specific* screen if you have multiple:
        # screen = QApplication.screenAt(QCursor.pos()).availableGeometry()

        # Get the window size.  Crucially, we do this *after* the window
        # and its widgets are laid out, but *before* we show it.  This
        # ensures we get the correct size.
        size = self.size()  # Use self.size() instead of self.geometry()

        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

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
        """
        Handle mouse press for both dragging and resizing.
        Only allow dragging from the title bar.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            if self.isInResizeArea(event.pos()):
                self._is_resizing = True
                self._resize_start_pos = event.globalPos()
                self._window_start_geometry = self.geometry()
            elif self.title_bar.rect().contains(
                    self.mapFromGlobal(event.globalPos())):  # 检查是否在标题栏区域
                self._drag_pos = event.globalPos() - self.pos()
            else:
                self._drag_pos = None  # 不在标题栏，则不允许拖动
            event.accept()

    def mouseMoveEvent(self, event):
        """
        Update cursor shape and handle move events.
        Only allow dragging if initiated from the title bar.
        """
        if self.isInResizeArea(event.pos()):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        if event.buttons() & Qt.MouseButton.LeftButton:
            if self._is_resizing:
                delta = event.globalPos() - self._resize_start_pos
                new_geometry = self._window_start_geometry
                new_width = new_geometry.width() + delta.x()
                new_height = new_geometry.height() + delta.y()

                new_width = max(new_width, self.minimumWidth())
                new_height = max(new_height, self.minimumHeight())

                self.setGeometry(
                    new_geometry.x(), new_geometry.y(), new_width, new_height)
            elif self._drag_pos:  # 只有当 _drag_pos 有值时才允许拖动
                self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Reset resize and drag states when mouse is released"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_resizing = False
            self._resize_start_pos = None
            self._window_start_geometry = None
            self._drag_pos = None  # 释放鼠标时重置 _drag_pos
        event.accept()

    def toggle_maximize(self):
        """Toggle window maximize/restore state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow(None)  # Pass None or a mock AppController during testing
    window.show()
    app.exec_()
