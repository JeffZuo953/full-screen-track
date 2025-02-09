import os
import sys
import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from qt_material import apply_stylesheet
from src.app.ui.main_window import MainWindow
from src.core.controller.app import AppController


def start_gui(app_controller: AppController) -> None:
    """
    Starts the graphical user interface for the application.

    This function initializes the PyQt application, sets the application icon,
    applies a stylesheet, and creates the main window.
    """
    # Set app ID for Windows taskbar
    if sys.platform == "win32":
        myappid = "jeffzuo953.fullscreentracer.v1.0.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication([])

    # Get the correct resource path whether running from source or frozen executable
    if getattr(sys, "frozen", False):
        # Running in PyInstaller bundle
        application_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        application_path = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )

    # Set icon path using absolute path
    icon_path = os.path.join(application_path, "resources", "icon.ico")
    icon = QIcon(icon_path)
    app.setWindowIcon(icon)

    # Set application properties
    app.setQuitOnLastWindowClosed(False)

    mainWin = MainWindow(app_controller)
    apply_stylesheet(app, theme="dark_lightgreen.xml")

    # Ensure taskbar icon shows up
    if sys.platform == "win32":
        # Force Windows to use the icon
        mainWin.setWindowIcon(icon)
        # Set icon for window handle
        mainWin.show()
        window = mainWin.windowHandle()
        if window:
            window.setIcon(icon)
    else:
        mainWin.show()

    sys.exit(app.exec_())
