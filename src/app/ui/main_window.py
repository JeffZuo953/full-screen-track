from __future__ import annotations

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

from PyQt5.QtCore import Qt, QRect, QPoint, QSize, QTimer
from PyQt5.QtGui import QCloseEvent, QMouseEvent, QShowEvent
from PyQt5.QtWidgets import QAction
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
    """
    A custom QPushButton that allows the main window to be resized.
    """

    def __init__(self, parent: QWidget = None):
        """
        Initializes the ResizableButton.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setMinimumSize(20, 20)  # Set the minimum size of the button
        self.dragging: bool = False  # Flag to indicate if the button is being dragged
        self.drag_start_pos: QPoint = QPoint(
        )  # Store the starting position of the drag

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handles the mouse press event.

        Args:
            event (QMouseEvent): The mouse press event.
        """
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_pos = event.globalPos() - self.parent().pos()
            # If the parent widget is not the direct parent, more complex calculations may be needed
            # self.drag_start_pos = event.globalPos() - self.mapToGlobal(self.pos())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Handles the mouse move event.

        Args:
            event (QMouseEvent): The mouse move event.
        """
        if self.dragging:
            new_pos: QPoint = event.globalPos() - self.drag_start_pos
            # Limit the minimum size of the window
            new_rect: QRect = QRect(self.parent().pos(), new_pos)
            if (new_rect.width() >= self.parent().minimumWidth()
                    and new_rect.height() >= self.parent().minimumHeight()):
                self.parent().setGeometry(new_rect)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Handles the mouse release event.

        Args:
            event (QMouseEvent): The mouse release event.
        """
        if event.button() == Qt.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)


class MainWindow(QMainWindow):
    """
    The main application window.
    """

    def __init__(self, app_controller: AppController):
        """
        Initializes the MainWindow.

        Args:
            app_controller (AppController): The application controller.
        """
        super().__init__()
        self.app_controller: AppController = app_controller

        # Get the application's root directory
        if getattr(sys, "frozen", False):
            # Running in PyInstaller bundle
            application_path: str = sys._MEIPASS
        else:
            # Running in normal Python environment
            application_path: str = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

        # Set resource paths
        self.resource_path: str = os.path.join(application_path, "resources")

        # Remove window frame
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Initialize always-on-top state
        self._is_always_on_top = False  # Default is not always on top
        self._first_show = True  # Track first show event

        self.setWindowTitle("Full Screen Tracer")
        self.setMinimumSize(800, 600)

        # Set window icon using absolute path
        icon_path: str = os.path.join(self.resource_path, "icon.svg")
        self.setWindowIcon(QIcon(icon_path))

        # Setup system tray
        self.setup_system_tray()

        main_widget: QWidget = QWidget()
        self.setCentralWidget(main_widget)
        layout: QVBoxLayout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Add custom title bar
        self.title_bar: QWidget = QWidget()
        title_bar_layout: QHBoxLayout = QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(10, 5, 10, 5)

        # Add window title with icon
        title_container: QWidget = QWidget()
        title_layout: QHBoxLayout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)

        title_icon: QLabel = QLabel()
        title_icon.setPixmap(
            QIcon(os.path.join(self.resource_path, "icon.svg")).pixmap(20, 20))
        title_layout.addWidget(title_icon)

        title_label: QLabel = QLabel("Full Screen Tracer")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        title_layout.addWidget(title_label)

        title_bar_layout.addWidget(title_container)
        title_bar_layout.addStretch()

        # Common button style for title bar buttons
        button_style: str = """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(173, 216, 230, 0.3);  /* 淡绿色 */
                border-radius: 3px;
            }
        """

        # Added stay-on-top toggle button
        self.always_on_top_button: QPushButton = QPushButton()
        self.always_on_top_button.setCheckable(True)
        self.always_on_top_button.setChecked(False)  # Default state
        self.update_always_on_top_button_icon()  # Set initial icon
        self.always_on_top_button.clicked.connect(self.toggle_always_on_top)
        self.always_on_top_button.setFixedSize(30, 30)
        self.always_on_top_button.setStyleSheet(button_style)
        title_bar_layout.addWidget(self.always_on_top_button)

        # Add window control buttons with custom icons
        min_button: QPushButton = QPushButton()
        min_button.setIcon(
            QIcon(os.path.join(self.resource_path, "minimize.svg")))
        min_button.clicked.connect(self.showMinimized)
        min_button.setFixedSize(30, 30)
        min_button.setStyleSheet(button_style)

        max_button: QPushButton = QPushButton()
        max_button.setIcon(
            QIcon(os.path.join(self.resource_path, "maximize.svg")))
        max_button.clicked.connect(self.toggle_maximize)
        max_button.setFixedSize(30, 30)
        max_button.setStyleSheet(button_style)

        close_button: QPushButton = QPushButton()
        close_button.setIcon(
            QIcon(os.path.join(self.resource_path, "close.svg")))
        close_button.clicked.connect(self.close)
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet(button_style)

        exit_button: QPushButton = QPushButton()
        exit_button.setIcon(
            QIcon(os.path.join(self.resource_path, "turnoff.svg")))
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
        tabs_container: QWidget = QWidget()
        tabs_layout: QHBoxLayout = QHBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(0, 0, 0, 0)

        self.tabs: QTabWidget = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setTabShape(QTabWidget.TabShape.Rounded)
        tabs_layout.addWidget(self.tabs)

        layout.addWidget(tabs_container)

        self.home: Home = Home(app_controller)
        # Connect home page signals to tray icon updates
        self.home.record_state_changed.connect(self._sync_record_checkbox)
        self.home.upload_state_changed.connect(self._sync_upload_checkbox)

        self.config_editor: ConfigEditor = ConfigEditor()
        self.file_data: FileData = FileData(app_controller.file_service,
                                            app_controller.local_file_manager)
        self.log: Log = Log()
        self.about: About = About()

        self.tabs.addTab(self.home, "Home")
        self.tabs.addTab(self.config_editor, "Config Editor")
        self.tabs.addTab(self.file_data, "File Data")
        self.tabs.addTab(self.log, "Log")
        self.tabs.addTab(self.about, "About")

        # Add resize related attributes
        self._resize_area_size: int = 10  # pixels for resize area detection
        self._is_resizing: bool = False  # Flag to indicate if the window is being resized
        self._resize_start_pos: QPoint = None  # Store the starting position of the resize
        self._window_start_geometry: QRect = (
            None  # Store the starting geometry of the window
        )

        # Create QSizeGrip and add to layout
        size_grip: QSizeGrip = QSizeGrip(self)
        layout.addWidget(
            size_grip, 0,
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        # The starting position of the window drag
        self._drag_pos: QPoint = None

    def showEvent(self, event: QShowEvent):
        """
        Override showEvent to handle initial window display.
        """
        super().showEvent(event)
        
        if self._first_show:
            # Temporarily set always on top for initial display
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.show()
            self.center_window()
            
            # Restore default state after showing
            QTimer.singleShot(100, self._restore_default_state)
            self._first_show = False
        else:
            self.center_window()
        
        # Sync the button state with the current window state
        self.always_on_top_button.setChecked(self._is_always_on_top)
        self.update_always_on_top_button_icon()

    def center_window(self):
        """
        Centers the window on the screen.
        """
        # Use availableGeometry to account for taskbars and other screen elements
        screen: QRect = QApplication.primaryScreen().availableGeometry()
        # OR, to center on a *specific* screen if you have multiple:
        # screen = QApplication.screenAt(QCursor.pos()).availableGeometry()

        # Get the window size.  Crucially, we do this *after* the window
        # and its widgets are laid out, but *before* we show it.  This
        # ensures we get the correct size.
        size: QSize = self.size()  # Use self.size() instead of self.geometry()

        x: int = (screen.width() - size.width()) // 2
        y: int = (screen.height() - size.height()) // 2
        self.move(x, y)

    def setup_system_tray(self):
        """
        Setup system tray icon and menu.
        """
        self.tray_icon: QSystemTrayIcon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())

        # Create tray menu with style
        tray_menu: QMenu = QMenu()

        # Create record toggle checkbox
        self.record_checkbox: QCheckBox = QCheckBox("On Record")
        self.record_checkbox.setChecked(False)
        self.record_checkbox.stateChanged.connect(self.toggle_record)

        self.upload_checkbox: QCheckBox = QCheckBox("Auto Upload")
        self.upload_checkbox.setChecked(False)
        self.upload_checkbox.stateChanged.connect(self.toggle_upload)

        # Create widget actions
        record_action: QWidgetAction = QWidgetAction(tray_menu)
        record_action.setDefaultWidget(self.record_checkbox)
        tray_menu.addAction(record_action)

        upload_action: QWidgetAction = QWidgetAction(tray_menu)
        upload_action.setDefaultWidget(self.upload_checkbox)
        tray_menu.addAction(upload_action)

        tray_menu.addSeparator()

        # Add show/hide window action
        restore_action: QAction = tray_menu.addAction("Show Window")
        restore_action.triggered.connect(self.showNormal)

        tray_menu.addSeparator()

        # Add exit action
        quit_action: QAction = tray_menu.addAction("Exit")
        quit_action.triggered.connect(self.quit_application)

        # Set the tray menu
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Connect double click to restore
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def isInResizeArea(self, pos: QPoint) -> bool:
        """
        Check if position is in the resize area (bottom-right corner).

        Args:
            pos (QPoint): The position to check.

        Returns:
            bool: True if the position is in the resize area, False otherwise.
        """
        window_rect: QRect = self.rect()
        bottom_right: QPoint = window_rect.bottomRight()
        resize_rect: QRect = QRect(
            bottom_right.x() - self._resize_area_size,
            bottom_right.y() - self._resize_area_size,
            self._resize_area_size,
            self._resize_area_size,
        )
        return resize_rect.contains(pos)

    def _sync_record_checkbox(self, checked: bool):
        """
        Sync tray record checkbox with home page state.

        Args:
            checked (bool): The state of the record checkbox on the home page.
        """
        if self.record_checkbox.isChecked() != checked:
            self.record_checkbox.setChecked(checked)

    def _sync_upload_checkbox(self, checked: bool):
        """
        Sync tray upload checkbox with home page state.

        Args:
            checked (bool): The state of the upload checkbox on the home page.
        """
        if self.upload_checkbox.isChecked() != checked:
            self.upload_checkbox.setChecked(checked)

    def toggle_record(self, checked: bool):
        """
        Handle record toggle from tray menu.

        Args:
            checked (bool): The state of the record checkbox in the tray menu.
        """
        if self.home.record_switch.isChecked() != checked:
            self.home.record_switch.setChecked(checked)

    def toggle_upload(self, checked: bool):
        """
        Handle upload toggle from tray menu.

        Args:
            checked (bool): The state of the upload checkbox in the tray menu.
        """
        if self.home.auto_upload_switch.isChecked() != checked:
            self.home.auto_upload_switch.setChecked(checked)

    def tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """
        Handle tray icon activation.

        Args:
            reason (QSystemTrayIcon.ActivationReason): The reason for the activation.
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()

    def closeEvent(self, event: QCloseEvent):
        """
        Override close event to minimize to tray instead of closing.

        Args:
            event (QCloseEvent): The close event.
        """
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.quit_application()

    def quit_application(self):
        """
        Cleanup and quit application.
        """
        dialog: CustomDialog = CustomDialog(
            "Exit Confirmation",
            "Are you sure you want to exit the application?", self)

        if dialog.show_question():
            self.app_controller.cleanup()
            self.tray_icon.hide()
            QApplication.quit()

    def mousePressEvent(self, event: QMouseEvent):
        """
        Handle mouse press for both dragging and resizing.
        Only allow dragging from the title bar.

        Args:
            event (QMouseEvent): The mouse press event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            if self.isInResizeArea(event.pos()):
                self._is_resizing = True
                self._resize_start_pos = event.globalPos()
                self._window_start_geometry = self.geometry()
            elif self.title_bar.rect().contains(
                    self.mapFromGlobal(event.globalPos())
            ):  # Check if it is in the title bar area
                self._drag_pos = event.globalPos() - self.pos()
            else:
                self._drag_pos = None  # Not in the title bar, dragging is not allowed
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Update cursor shape and handle move events.
        Only allow dragging if initiated from the title bar.

        Args:
            event (QMouseEvent): The mouse move event.
        """
        if self.isInResizeArea(event.pos()):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        if event.buttons() & Qt.MouseButton.LeftButton:
            if self._is_resizing:
                delta: QPoint = event.globalPos() - self._resize_start_pos
                new_geometry: QRect = self._window_start_geometry
                new_width: int = new_geometry.width() + delta.x()
                new_height: int = new_geometry.height() + delta.y()

                new_width = max(new_width, self.minimumWidth())
                new_height = max(new_height, self.minimumHeight())

                self.setGeometry(new_geometry.x(), new_geometry.y(), new_width,
                                 new_height)
            elif self._drag_pos:  # Only allow dragging if _drag_pos has a value
                self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Reset resize and drag states when mouse is released.

        Args:
            event (QMouseEvent): The mouse release event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_resizing = False
            self._resize_start_pos = None
            self._window_start_geometry = None
            self._drag_pos = None  # Reset _drag_pos when releasing the mouse
        event.accept()

    def toggle_maximize(self):
        """
        Toggle window maximize/restore state.
        """
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _update_always_on_top_state(self):
        """
        Update the window's always-on-top state without full refresh.
        """
        # Save current geometry and visibility
        geometry = self.geometry()
        is_visible = self.isVisible()
        
        # Update window flags
        if self._is_always_on_top:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        
        # Restore geometry and visibility
        self.setGeometry(geometry)
        if is_visible:
            self.show()

    def toggle_always_on_top(self):
        """
        Toggle window always-on-top state with minimal refresh.
        """
        self._is_always_on_top = not self._is_always_on_top
        self._update_always_on_top_state()
        # Update the button state and icon
        self.always_on_top_button.setChecked(self._is_always_on_top)
        self.update_always_on_top_button_icon()

    def update_always_on_top_button_icon(self):
        """
        Update the always-on-top button icon based on its state.
        """
        if self.always_on_top_button.isChecked():
            self.always_on_top_button.setIcon(
                QIcon(os.path.join(self.resource_path, "pin.svg")))  # Use appropriate icon
        else:
            self.always_on_top_button.setIcon(
                QIcon(os.path.join(self.resource_path, "unpin.svg")))  # Use appropriate icon

    def _restore_default_state(self):
        """
        Restore the window to its default state after initial display.
        """
        # Update window flags
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        # Ensure the state is consistent
        self._is_always_on_top = False
        self.always_on_top_button.setChecked(False)
        self.update_always_on_top_button_icon()
        # Show the window with new flags
        self.show()


if __name__ == "__main__":
    app: QApplication = QApplication([])
    window: MainWindow = MainWindow(
        None)  # Pass None or a mock AppController during testing
    window.show()
    app.exec_()
