from time import sleep
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QFrame,
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

from src.app.ui.page.home.thread_table import ThreadTable
from src.app.ui.page.home.upload_progress import UploadProgress
from src.core.util.logger import logger
from src.app.app_controller_singleton import AppController


class Home(QMainWindow):
    record_state_changed = pyqtSignal(bool)  # Add signal for record state
    upload_state_changed = pyqtSignal(bool)  # Add signal for upload state

    def __init__(self, app_controller: AppController):
        super().__init__()

        self.app_controller = app_controller
        self.setup_ui()
        # Thread management
        self.record_thread = None
        self.upload_thread = None
        self.polling_thread = None  # New thread for polling

        # Switch states
        self.is_recording = False
        self.is_auto_upload = False

    def setup_ui(self):
        self.setWindowTitle("Run Page")
        self.setMinimumSize(400, 300)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QGridLayout(main_widget)

        vline = QFrame()
        vline.setFrameShape(QFrame.Shape.VLine)
        vline.setFrameShadow(QFrame.Shadow.Sunken)

        hline = QFrame()
        hline.setFrameShape(QFrame.Shape.HLine)
        hline.setFrameShadow(QFrame.Shadow.Sunken)

        # Create and configure UI elements
        self.start_button = QPushButton("Start All")
        self.stop_button = QPushButton("Stop All")
        self.upload_once_button = QPushButton("Upload Once")
        self.abort_upload_button = QPushButton("Abort Upload")

        self.stop_button.setEnabled(False)
        self.abort_upload_button.setEnabled(False)

        # Create horizontal layouts for each checkbox row
        record_layout = QHBoxLayout()
        record_label = QLabel("On Record")
        record_label.setFixedWidth(80)
        self.record_switch = QCheckBox()
        record_layout.addWidget(record_label)
        record_layout.addWidget(self.record_switch)
        record_layout.addStretch()

        upload_layout = QHBoxLayout()
        upload_label = QLabel("Auto Upload")
        upload_label.setFixedWidth(80)
        self.auto_upload_switch = QCheckBox()
        upload_layout.addWidget(upload_label)
        upload_layout.addWidget(self.auto_upload_switch)
        upload_layout.addStretch()

        self.thread_table = ThreadTable(self.app_controller)
        self.upload_process = UploadProgress(self.app_controller)

        # Add widgets to main layout with adjusted row spans
        layout.addLayout(record_layout, 0, 0, 1, 2)
        layout.addLayout(upload_layout, 1, 0, 1, 2)
        layout.addWidget(self.start_button, 2, 0, 1, 1)
        layout.addWidget(self.stop_button, 3, 0, 1, 1)

        layout.addWidget(vline, 0, 1, 12, 1)

        # Increase thread_table height by adjusting row span from 4 to 6
        layout.addWidget(self.thread_table, 0, 2, 5, 8)

        layout.addWidget(hline, 6, 2, 1, 8)

        # Move upload buttons down
        layout.addWidget(self.upload_once_button, 7, 0, 1, 1)
        layout.addWidget(self.abort_upload_button, 8, 0, 1, 1)

        # Reduce upload_process height by adjusting row span from 4 to 2
        layout.addWidget(self.upload_process, 7, 2, 3, 8)

        # Connect signals
        self.start_button.clicked.connect(self.on_start)
        self.stop_button.clicked.connect(self.on_stop)
        self.record_switch.stateChanged.connect(self.on_record_switch_change)
        self.auto_upload_switch.stateChanged.connect(self.on_auto_upload_switch_change)
        self.upload_once_button.clicked.connect(self.on_upload_once)
        self.abort_upload_button.clicked.connect(self.on_abort_upload_once)

    def on_record_switch_change(self, state):
        """Handle record switch state change"""
        try:
            logger.debug(f"Record switch state changed: {state}")
            if state == Qt.CheckState.Checked:
                if not self.app_controller.is_recording:
                    self.app_controller.start_recording()
                    logger.debug("Recording started")
            else:
                if self.app_controller.is_recording:
                    self.app_controller.stop_recording()
                    logger.debug("Recording stopped")
            # Sync tray menu state
            window = self.parent().parent()
            if hasattr(window, '_update_record_icon'):
                window._update_record_icon(state == Qt.CheckState.Checked)
            # Emit signal
            self.record_state_changed.emit(state == Qt.CheckState.Checked)
        except Exception as e:
            logger.error(f"Error in record switch: {e}")
            # Reset switch state to match actual recording state
            self.record_switch.setChecked(self.app_controller.is_recording)
            self.handle_error(str(e), "record_thread")
        self.update_button_states()

    def on_auto_upload_switch_change(self, state):
        """Handle auto upload switch state change"""
        try:
            if state == Qt.CheckState.Checked:
                if not self.polling_thread or not self.polling_thread.isRunning():
                    self.polling_thread = UploadPollingThread(self.app_controller)
                    self.polling_thread.error.connect(
                        lambda msg: self.handle_error(msg, "polling_thread")
                    )
                    self.polling_thread.start()
            else:
                if self.polling_thread and self.polling_thread.isRunning():
                    self.app_controller.stop_polling()
                    self.polling_thread.terminate()
                    self.polling_thread.wait()
                    self.polling_thread = None
            # Sync tray menu state
            window = self.parent().parent()
            if hasattr(window, '_update_upload_icon'):
                window._update_upload_icon(state == Qt.CheckState.Checked)
            # Emit signal
            self.upload_state_changed.emit(state == Qt.CheckState.Checked)
        except Exception as e:
            self.handle_error(str(e), "polling_thread")
        self.update_button_states()

    def update_button_states(self):
        record_on = self.record_switch.isChecked()
        upload_on = self.auto_upload_switch.isChecked()

        if not record_on and not upload_on:
            # Both off - only enable Start
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
        elif record_on and upload_on:
            # Both on - only enable Stop
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            # One on - enable both buttons
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(True)

    def on_start(self):
        """Start recording and/or uploading based on switch states"""
        self.record_switch.setChecked(True)
        self.auto_upload_switch.setChecked(True)
        self.update_button_states()
        logger.info(f"Started Recoring")

    def on_stop(self):
        """Stop all operations"""
        logger.info("Stopping all operations")
        self.record_switch.setChecked(False)
        self.auto_upload_switch.setChecked(False)
        self.update_button_states()
        logger.info("All operations stopped")

    def on_upload_once(self):
        """Trigger one-time upload"""

        if not self.upload_thread or not self.upload_thread.isRunning():
            self.upload_thread = UploadThread(self.app_controller)
            self.upload_thread.error.connect(self._on_upload_once_error)
            self.upload_thread.finished.connect(self._on_upload_once_complete)
            self.upload_thread.start()

            # Update UI
            self.upload_once_button.setEnabled(False)
            self.abort_upload_button.setEnabled(True)

    def _on_upload_once_complete(self):
        self.upload_once_button.setEnabled(True)
        self.abort_upload_button.setEnabled(False)

    def on_abort_upload_once(self):
        if self.upload_thread and self.upload_thread.isRunning():
            self.upload_thread.terminate()
            self.upload_thread.wait()
            self._on_upload_once_complete()

    def _on_upload_once_error(self, message):
        self.handle_error(message, "upload once")
        self.upload_once_button.setEnabled(True)

    def clean_up(self):
        self.app_controller.cleanup()

    def handle_error(self, error_msg, name=""):
        logger.error(f"{name} Thread error: {error_msg}")


class UploadPollingThread(QThread):
    error = pyqtSignal(str)

    def __init__(self, app_controller: AppController):
        super().__init__()
        self.app_controller = app_controller

    def run(self):
        try:
            self.app_controller.start_polling()
        except Exception as e:
            self.error.emit(str(e))


class UploadThread(QThread):
    error = pyqtSignal(str)

    def __init__(self, app_controller: AppController):
        super().__init__()
        self.app_controller = app_controller

    def run(self):
        try:
            self.app_controller.manual_upload()
        except Exception as e:
            self.error.emit(str(e))
