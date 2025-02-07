import sys
import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from qt_material import apply_stylesheet
from src.app.ui.main_window import MainWindow
from src.core.controller.app import AppController


def start_gui(app_controller: AppController) -> None:
    """Main entry point for the application"""
    # Set app ID for Windows taskbar
    if sys.platform == 'win32':
        myappid = 'mycompany.fullscreentracer.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    app = QApplication([])
    
    # Set icon for all windows and taskbar
    icon = QIcon("src/app/ui/resources/icon.ico")
    app.setWindowIcon(icon)
    
    # Set application properties
    app.setQuitOnLastWindowClosed(False)
    
    mainWin = MainWindow(app_controller)
    apply_stylesheet(app, theme="dark_lightgreen.xml")
    
    # Ensure taskbar icon shows up
    if sys.platform == 'win32':
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
