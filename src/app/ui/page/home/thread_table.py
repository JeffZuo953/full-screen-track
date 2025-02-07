from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from PyQt5.QtCore import QTimer, Qt

from src.core.controller.app import AppController


class ThreadTable(QWidget):
    def __init__(self, app_controller: AppController):
        super().__init__()
        self.app_controller = app_controller
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create table widget
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["PID", "Runtime", "Output"])
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set title
        title = QLabel("Current Record Processed")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")

        layout.addWidget(title)
        layout.addWidget(self.table)

    def setup_timer(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_table)
        self.update_timer.start(1000)  # Update every second

    def refresh_table(self):
        processes = self.app_controller.recorder_manager.list_processes()
        self.table.setRowCount(len(processes))

        for row, process in enumerate(processes):
            self.table.setItem(row, 0, QTableWidgetItem(str(process["pid"])))
            self.table.setItem(row, 1, QTableWidgetItem(str(process["runtime"])))
            self.table.setItem(row, 2, QTableWidgetItem(process["output"]))
