from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView
)
from PyQt5.QtCore import QTimer, Qt

from src.core.controller.app import AppController


class UploadProgress(QWidget):
    def __init__(self, app_controller: AppController):
        super().__init__()
        self.app_controller = app_controller
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Add title
        title = QLabel("Current Uploading Files")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["File", "Progress", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout.addWidget(self.table)

    def setup_timer(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_table)
        self.update_timer.start(1000)  # Update every second

    def refresh_table(self):
        # Get filtered status (non-existent files already removed)
        upload_status = self.app_controller.uploader_manager.get_upload_status()

        # Filter out completed uploads and keep only active ones
        active_uploads = [
            item
            for item in upload_status
            if item["status"] not in ("completed", "failed")
        ]

        # Sort by progress in descending order
        active_uploads.sort(key=lambda x: float(x["progress"]), reverse=True)

        # Only show first 6 items
        display_uploads = active_uploads[:6]

        self.table.setRowCount(len(display_uploads))

        for row, item in enumerate(display_uploads):
            self.table.setItem(row, 0, QTableWidgetItem(item["file"]))
            self.table.setItem(row, 1, QTableWidgetItem(f"{item['progress']}%"))
            self.table.setItem(row, 2, QTableWidgetItem(item["status"]))
