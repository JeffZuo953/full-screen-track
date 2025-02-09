from __future__ import annotations

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)

from src.core.controller.app import AppController


class ThreadTable(QWidget):
    """
    A table widget to display information about running threads.
    """

    def __init__(self, app_controller: AppController) -> None:
        """
        Initializes the ThreadTable with the application controller.
        """
        super().__init__()
        self.app_controller: AppController = app_controller
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self) -> None:
        """
        Sets up the user interface elements and their layout.
        """
        layout: QVBoxLayout = QVBoxLayout()
        self.setLayout(layout)

        # Create table widget
        self.table: QTableWidget = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["PID", "Runtime", "Output"])
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set title
        title: QLabel = QLabel("Current Record Processed")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")

        layout.addWidget(title)
        layout.addWidget(self.table)

    def setup_timer(self) -> None:
        """
        Sets up a timer to refresh the table periodically.
        """
        self.update_timer: QTimer = QTimer()
        self.update_timer.timeout.connect(self.refresh_table)
        self.update_timer.start(1000)  # Update every second

    def refresh_table(self) -> None:
        """
        Refreshes the table with the latest process information.
        """
        processes: list[dict] = self.app_controller.recorder_manager.list_processes()
        self.table.setRowCount(len(processes))

        for row, process in enumerate(processes):
            self.table.setItem(row, 0, QTableWidgetItem(str(process["pid"])))
            self.table.setItem(row, 1, QTableWidgetItem(str(process["runtime"])))
            self.table.setItem(row, 2, QTableWidgetItem(process["output"]))
