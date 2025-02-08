from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
    QSpinBox,
    QCheckBox,
    QHeaderView,
    QFileDialog,
    QProgressDialog,
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QThreadPool
import pandas as pd
from datetime import datetime
from src.app.ui.custom_dialog import CustomDialog
from src.core.manager.local_file import LocalFileManager
from src.core.model.service.file_service import FileService 
import os
from src.core.util.logger import logger

class ExportThread(QThread):
    export_finished = pyqtSignal(str)

    def __init__(self, file_service: FileService, path, current_page, page_size, export_all=False):
        super().__init__()
        self.file_service = file_service
        self.path = path
        self.current_page = current_page
        self.page_size = page_size
        self.export_all = export_all

    def run(self):
        if self.export_all:
            files = self.file_service.get_files_paginated(
                1, self.file_service.get_total_count()
            )
        else:
            files = self.file_service.get_files_paginated(
                self.current_page, self.page_size
            )
        df = pd.DataFrame([file.to_dict() for file in files])
        df.to_csv(self.path, index=False)
        self.export_finished.emit(self.path)


class FileData(QWidget):
    def __init__(self, file_service: FileService, local_manager: LocalFileManager):
        super().__init__()

        self.file_service = file_service
        self.local_manager = local_manager
        self.current_page = 1
        self.page_size = 10
        self.thread_pool = QThreadPool()
        self.current_worker = None

        layout = QVBoxLayout(self)

        # Search bar and date range filters
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search file path...")
        search_layout.addWidget(self.search_bar)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.load_file_data)
        search_layout.addWidget(self.search_button)

        layout.addLayout(search_layout)

        # Column visibility controls
        column_controls_layout = QHBoxLayout()
        visibility_label = QLabel("Visibility:")
        column_controls_layout.addWidget(visibility_label)
        self.column_checkboxes = []
        for i, column_name in enumerate(
            [
                "ID",
                "Local Path",
                "Remote Path",
                "File Size",
                "Last Modified",
                "Status",
                "Upload Time",
                "Last Check",
                "Exists Locally",
            ]
        ):
            checkbox = QCheckBox(column_name)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(
                lambda state, col=i: self.toggle_column(col, state)
            )
            column_controls_layout.addWidget(checkbox)
            self.column_checkboxes.append(checkbox)
        layout.addLayout(column_controls_layout)

        # File data table
        self.file_table = QTableWidget()
        layout.addWidget(self.file_table)

        # Pagination controls
        pagination_layout = QHBoxLayout()
        self.first_button = QPushButton("First")
        self.first_button.clicked.connect(self.first_page)
        pagination_layout.addWidget(self.first_button)

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_page)
        pagination_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_button)

        self.last_button = QPushButton("Last")
        self.last_button.clicked.connect(self.last_page)
        pagination_layout.addWidget(self.last_button)

        self.page_input = QSpinBox()
        self.page_input.setMinimum(1)
        self.page_input.setValue(self.current_page)
        self.page_input.valueChanged.connect(self.set_page)
        self.page_input.setStyleSheet("color: white;")
        pagination_layout.addWidget(QLabel("Page Number:"))
        pagination_layout.addWidget(self.page_input)

        self.page_size_input = QSpinBox()
        self.page_size_input.setMinimum(1)
        self.page_size_input.setMaximum(500)
        self.page_size_input.setValue(self.page_size)
        self.page_size_input.valueChanged.connect(self.set_page_size)
        self.page_size_input.setStyleSheet("color: white;")
        pagination_layout.addWidget(QLabel("Page Size:"))
        pagination_layout.addWidget(self.page_size_input)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_file_data)
        pagination_layout.addWidget(self.refresh_button)

        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        pagination_layout.addWidget(self.export_button)

        self.export_all_button = QPushButton("Export All to CSV")
        self.export_all_button.clicked.connect(self.export_all_to_csv)
        pagination_layout.addWidget(self.export_all_button)

        # Add check existence buttons to pagination layout
        self.check_current_button = QPushButton("Check Current Page Files")
        self.check_current_button.clicked.connect(self.check_current_page_files)
        pagination_layout.addWidget(self.check_current_button)

        self.check_all_button = QPushButton("Check All Files")
        self.check_all_button.clicked.connect(self.check_all_files)
        pagination_layout.addWidget(self.check_all_button)

        # Add clear old records button to pagination layout
        self.clear_old_button = QPushButton("Clear Old Records")
        self.clear_old_button.clicked.connect(self.clear_old_records)
        pagination_layout.addWidget(self.clear_old_button)

        # Add delete old files button to pagination layout
        self.delete_old_files_button = QPushButton("Delete Old Files")
        self.delete_old_files_button.clicked.connect(self.delete_old_files)
        pagination_layout.addWidget(self.delete_old_files_button)

        layout.addLayout(pagination_layout)

        # Column width controls
        self.file_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )

        self.load_file_data()

    def load_file_data(self):
        """Load file data into the table."""
        query = self.search_bar.text()
        files = self.file_service.get_files_paginated(
            self.current_page,
            self.page_size,
            query
        )
        self.file_table.setRowCount(len(files))
        self.file_table.setColumnCount(9)
        self.file_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Local Path",
                "Remote Path",
                "File Size",
                "Last Modified",
                "Status",
                "Upload Time",
                "Last Check",
                "Exists Locally",
            ]
        )
        for row, file in enumerate(files):
            for col, key in enumerate(file.to_dict()):
                value = file.to_dict()[key]
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.file_table.setItem(row, col, item)

    def first_page(self):
        self.current_page = 1
        self.page_input.setValue(self.current_page)
        self.load_file_data()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.page_input.setValue(self.current_page)
            self.load_file_data()

    def next_page(self):
        total_files = self.file_service.get_total_count()
        if self.current_page * self.page_size < total_files:
            self.current_page += 1
            self.page_input.setValue(self.current_page)
            self.load_file_data()

    def last_page(self):
        total_files = self.file_service.get_total_count()
        self.current_page = (total_files + self.page_size - 1) // self.page_size
        self.page_input.setValue(self.current_page)
        self.load_file_data()

    def set_page(self, page: int):
        self.current_page = page
        self.load_file_data()

    def set_page_size(self, page_size: int):
        self.page_size = page_size
        self.load_file_data()

    def toggle_column(self, column: int, state: int):
        if state == 0:
            self.file_table.hideColumn(column)
        else:
            self.file_table.showColumn(column)

    def set_spinbox_text_color(self, spinbox: QSpinBox, color: QColor):
        palette = spinbox.palette()
        palette.setColor(QPalette.ColorRole.Text, color)
        spinbox.setPalette(palette)

    def export_to_csv(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", f"FullScreenTrackerData_{timestamp}", "CSV Files (*.csv)"
        )
        if path:
            self.export_thread = ExportThread(
                self.file_service, path, self.current_page, self.page_size
            )
            self.export_thread.export_finished.connect(
                self.show_export_finished_message
            )
            self.export_thread.start()

    def export_all_to_csv(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save CSV",
            f"AllFullScreenTrackerData_{timestamp}",
            "CSV Files (*.csv)",
        )
        if path:
            self.export_thread = ExportThread(
                self.file_service,
                path,
                self.current_page,
                self.page_size,
                export_all=True,
            )
            self.export_thread.export_finished.connect(
                self.show_export_finished_message
            )
            self.export_thread.start()

    def show_export_finished_message(self, path: str):
        dialog = CustomDialog(
            "Export Finished",
            f"The export has been completed successfully.\nFile saved at: {path}",
            self,
        )
        dialog.show_information()

    def check_current_page_files(self):
        """Check if files in current page exist locally"""
        rows = self.file_table.rowCount()
        progress = QProgressDialog("Checking files...", "Cancel", 0, rows, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)

        for row in range(rows):
            if progress.wasCanceled():
                break

            local_path = self.file_table.item(row, 1).text()  # Local Path column
            exists = self.file_service.check_file_exists(local_path)

            item = QTableWidgetItem(str(exists))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.file_table.setItem(row, 8, item)  # 8 is the Exists Locally column

            progress.setValue(row + 1)

        progress.close()
        dialog = CustomDialog("Complete", "File existence check completed", self)
        dialog.show_information()

    def check_all_files(self):
        """Check if all files in database exist locally"""
        # Create progress dialog
        progress = QProgressDialog("Checking all files...", "Cancel", 0, 100, self)
        progress.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)  # Show immediately

        total_files = self.file_service.get_total_count()
        batch_size = 100
        processed = 0

        page = 1
        while True:
            files = self.file_service.get_files_paginated(page, batch_size)
            if not files:
                break

            updates = []
            for file in files:
                if progress.wasCanceled():
                    break
                exists = os.path.exists(file.local_path)
                updates.append((exists, file.local_path))
                processed += 1
                progress.setValue(int(processed * 100 / total_files))

            # 批量更新存在状态
            if updates:
                self.file_service.batch_update_existence(updates)

            if progress.wasCanceled():
                break

            page += 1

        progress.close()
        self.load_file_data()  # Refresh the view
        dialog = CustomDialog("Complete", "All files existence check completed", self)
        dialog.show_information()

    def delete_old_files(self):
        """Delete local files older than 3 days"""
        message = (
            "This will permanently delete all local files older than 3 days.\n"
            "This operation cannot be undone.\n"
            "The database records will be kept.\n"
            "Continue?"
        )
        if CustomDialog("Confirm Delete Files", message, self).show_question():
            progress = QProgressDialog("Deleting old files...", "Cancel", 0, 100, self)
            progress.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)  # Show immediately

            deleted_count = 0
            failed_count = 0
            old_files = self.file_service.get_old_files(3)
            total_files = len(old_files)
            
            for i, file in enumerate(old_files):
                if progress.wasCanceled():
                    break
                try:
                    if os.path.exists(file.local_path):
                        os.remove(file.local_path)
                        self.file_service.check_file_exists(file.local_path)
                        deleted_count += 1
                        logger.info(f"Deleted old file: {file.local_path}")
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to delete {file.local_path}: {e}")
                progress.setValue(int((i + 1) * 100 / total_files))

            progress.close()
            self.load_file_data()  # Refresh the view

            result_message = (
                f"Successfully deleted {deleted_count} files.\n"
                f"Failed to delete {failed_count} files."
            )
            dialog = CustomDialog("Files Deleted", result_message, self)
            dialog.show_information()

    def clear_old_records(self):
        """Clear records older than 7 days"""
        message = (
            "This will delete all file records older than 7 days.\n"
            "The local files won't be deleted.\n"
            "You can delete files manually.\n"
            "Continue?"
        )
        dialog = CustomDialog(
            "Confirm Delete",
            message,
            self,
        )

        if dialog.show_question() == QMessageBox.StandardButton.Yes:
            deleted_count = self.file_service.delete_old_records(7)
            self.load_file_data()  # Refresh the table
            dialog = CustomDialog(
                "Records Deleted",
                f"Successfully deleted {deleted_count} old records.",
                self,
            )
            dialog.show_information()
