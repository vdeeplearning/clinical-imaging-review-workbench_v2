from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.database import get_base_path
from app.models import Patient
from app.services import (
    delete_patient,
    delete_scan,
    get_all_patients_with_summary,
    get_or_create_patient,
    get_patient_by_patient_id,
    get_scan_detail,
    get_scan_history_for_patient,
    save_scan,
)
from app.ui.image_viewer import ImageViewerWidget
from app.ui.scan_detail import ScanDetailWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Clinical Imaging Review Workbench (V1)")
        self.resize(1700, 950)

        self.current_patient: Optional[Patient] = None
        self.project_root = get_base_path()

        self._apply_app_style()
        self._build_ui()
        self._refresh_patient_table()

    def _show_warning(self, title: str, message: str) -> None:
        body = (
            message.strip()
            or (
                "The requested action could not be completed. "
                "Please check the current selection and try again."
            )
        )

        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle(title or "Warning")
        dialog.setText(body)
        dialog.setStyleSheet(self._message_box_style())
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.exec()

    def _show_info(self, title: str, message: str) -> None:
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setStyleSheet(self._message_box_style())
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.exec()

    def _confirm(self, title: str, message: str) -> bool:
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setStyleSheet(self._message_box_style())
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        dialog.setDefaultButton(QMessageBox.StandardButton.No)
        return dialog.exec() == QMessageBox.StandardButton.Yes

    def _message_box_style(self) -> str:
        return """
            QMessageBox {
                background-color: #1f2430;
            }
            QMessageBox QLabel {
                color: #e8ecf1;
                font-size: 13px;
            }
            QMessageBox QPushButton {
                background-color: #2f6fed;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                color: white;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #3a7bff;
            }
        """

    def _apply_app_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #161a22;
            }
            QWidget {
                color: #e8ecf1;
                font-size: 13px;
            }
            QFrame#panel {
                background-color: #1f2430;
                border: 1px solid #323846;
                border-radius: 8px;
            }
            QLabel#sectionHeader {
                font-size: 16px;
                font-weight: bold;
                color: #f0f4f8;
            }
            QLabel#subHeader {
                font-size: 14px;
                font-weight: bold;
                color: #dfe6ee;
                margin-top: 8px;
            }
            QLineEdit, QDateEdit, QTextEdit, QTableWidget, QDoubleSpinBox {
                background-color: #232833;
                border: 1px solid #3a3f4b;
                border-radius: 6px;
                padding: 6px;
                color: #e8ecf1;
                selection-background-color: #2f6fed;
                selection-color: #ffffff;
            }
            QTableWidget {
                gridline-color: #3a3f4b;
            }
            QHeaderView::section {
                background-color: #2a3140;
                color: #e8ecf1;
                padding: 6px;
                border: 1px solid #3a3f4b;
                font-weight: bold;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                background-color: #2a3140;
                border-left: 1px solid #3a3f4b;
                width: 18px;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #364055;
            }
            QPushButton {
                background-color: #2f6fed;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a7bff;
            }
            QPushButton:disabled {
                background-color: #5b6270;
                color: #c7ccd4;
            }
            QMessageBox {
                background-color: #1f2430;
            }
            QMessageBox QLabel {
                color: #e8ecf1;
            }
            """
        )

    def _build_ui(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.left_panel = self._build_left_panel()
        self.center_panel = self._build_center_panel()
        self.right_panel = self._build_right_panel()

        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.center_panel)
        splitter.addWidget(self.right_panel)

        splitter.setSizes([420, 430, 950])

        self.setCentralWidget(splitter)

    def _build_left_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)

        header = QLabel("Patient Controls")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        form_layout = QFormLayout()

        self.patient_id_input = QLineEdit()
        self.patient_id_input.setPlaceholderText("Enter Patient ID")
        form_layout.addRow("Patient ID:", self.patient_id_input)

        layout.addLayout(form_layout)

        self.load_patient_button = QPushButton("Load New or Existing Patient by Patient ID")
        self.load_patient_button.clicked.connect(self._load_patient)
        layout.addWidget(self.load_patient_button)

        self.current_patient_label = QLabel("Current Patient: —")
        layout.addWidget(self.current_patient_label)

        self.new_scan_button = QPushButton("New Scan")
        self.new_scan_button.setEnabled(False)
        self.new_scan_button.clicked.connect(self._start_new_scan)
        layout.addWidget(self.new_scan_button)

        patient_directory_header = QLabel("Patient Directory")
        patient_directory_header.setObjectName("subHeader")
        layout.addWidget(patient_directory_header)

        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(3)
        self.patient_table.setHorizontalHeaderLabels(
            ["Patient ID", "Scans", "Latest Scan"]
        )

        for col in range(3):
            item = self.patient_table.horizontalHeaderItem(col)
            if item is not None:
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.patient_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.patient_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.patient_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.patient_table.verticalHeader().setVisible(False)
        self.patient_table.itemSelectionChanged.connect(self._handle_patient_selection)

        layout.addWidget(self.patient_table)

        self.remove_patient_button = QPushButton("Remove Selected Patient")
        self.remove_patient_button.clicked.connect(self._remove_selected_patient)
        layout.addWidget(self.remove_patient_button)

        return panel

    def _build_center_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)

        header = QLabel("Scan History")
        header.setObjectName("sectionHeader")
        layout.addWidget(header)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(
            ["Scan Date", "Accession #", "Box", "Notes"]
        )
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.itemSelectionChanged.connect(self._handle_history_selection)

        layout.addWidget(self.history_table)

        self.remove_scan_button = QPushButton("Remove Selected Scan")
        self.remove_scan_button.clicked.connect(self._remove_selected_scan)
        layout.addWidget(self.remove_scan_button)

        return panel

    def _build_right_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)

        workspace_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.current_image_path = "sample_data/dummy_scan.png"
        self.image_viewer = ImageViewerWidget()
        self.image_viewer.load_image(self.current_image_path)
        self.workspace_stack = QStackedWidget()

        self.new_scan_widget = self._build_new_scan_widget()
        self.scan_detail_widget = ScanDetailWidget()

        self.workspace_stack.addWidget(self.new_scan_widget)
        self.workspace_stack.addWidget(self.scan_detail_widget)

        workspace_splitter.addWidget(self.image_viewer)
        workspace_splitter.addWidget(self.workspace_stack)
        workspace_splitter.setSizes([560, 380])

        layout.addWidget(workspace_splitter)

        return panel

    def _build_new_scan_widget(self) -> QWidget:
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(12)

        header = QLabel("New Single-Lesion Scan")
        header.setObjectName("sectionHeader")
        main_layout.addWidget(header)

        form_layout = QFormLayout()

        self.new_scan_patient_label = QLabel("—")
        form_layout.addRow("Patient ID:", self.new_scan_patient_label)

        self.scan_date_edit = QDateEdit()
        self.scan_date_edit.setCalendarPopup(True)
        self.scan_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.scan_date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Scan Date:", self.scan_date_edit)

        self.accession_input = QLineEdit()
        self.accession_input.setPlaceholderText("Optional accession / study ID")
        form_layout.addRow("Accession #:", self.accession_input)

        self.selected_image_label = QLabel("No image selected")
        self.selected_image_label.setWordWrap(True)
        form_layout.addRow("Image:", self.selected_image_label)

        main_layout.addLayout(form_layout)

        button_row = QHBoxLayout()
        self.save_scan_button = QPushButton("Save Scan")
        self.save_scan_button.clicked.connect(self._save_scan)

        button_row.addWidget(self.save_scan_button)
        button_row.addStretch()

        main_layout.addLayout(button_row)

        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: #ffcc66; font-weight: bold;")
        main_layout.addWidget(self.warning_label)

        notes_header = QLabel("Annotation Notes")
        notes_header.setObjectName("subHeader")
        main_layout.addWidget(notes_header)

        self.annotation_notes_edit = QTextEdit()
        self.annotation_notes_edit.setPlaceholderText("Enter notes for this scan annotation...")
        self.annotation_notes_edit.setMinimumHeight(180)
        main_layout.addWidget(self.annotation_notes_edit)
        main_layout.addStretch()

        return container

    def _refresh_patient_table(self) -> None:
        self.patient_table.blockSignals(True)
        self.patient_table.setRowCount(0)

        patient_rows = get_all_patients_with_summary()
        self.patient_table.setRowCount(len(patient_rows))

        for row_index, row in enumerate(patient_rows):
            patient_id_item = QTableWidgetItem(row["patient_id"])
            patient_id_item.setData(Qt.ItemDataRole.UserRole, row["patient_id"])

            scan_count_item = QTableWidgetItem(str(row["scan_count"]))
            latest_scan_item = QTableWidgetItem(row["latest_scan_date"] or "—")

            self.patient_table.setItem(row_index, 0, patient_id_item)
            self.patient_table.setItem(row_index, 1, scan_count_item)
            self.patient_table.setItem(row_index, 2, latest_scan_item)

        self.patient_table.setColumnWidth(0, 120)   # Patient ID
        self.patient_table.setColumnWidth(1, 70)    # Scans
        self.patient_table.setColumnWidth(2, 140)   # Latest Scan

        self.patient_table.blockSignals(False)

        if self.current_patient is not None:
            self._select_patient_row_by_patient_id(self.current_patient.patient_id)

    def _select_patient_row_by_patient_id(self, patient_id: str) -> None:
        for row in range(self.patient_table.rowCount()):
            item = self.patient_table.item(row, 0)
            if item is None:
                continue

            row_patient_id = item.data(Qt.ItemDataRole.UserRole)
            if row_patient_id == patient_id:
                self.patient_table.selectRow(row)
                return

    def _handle_patient_selection(self) -> None:
        selected_items = self.patient_table.selectedItems()
        if not selected_items:
            return

        first_item = selected_items[0]
        patient_id = first_item.data(Qt.ItemDataRole.UserRole)

        if not patient_id:
            return

        self.patient_id_input.setText(patient_id)
        self._load_patient(from_table_selection=True)

    def _load_patient(self, from_table_selection: bool = False) -> None:
        patient_id = self.patient_id_input.text().strip()
        if not patient_id:
            self._show_warning(
                "Missing Patient ID",
                "Enter a Patient ID before loading a patient.\n\n"
                "You can type an existing ID or a new demo-style ID.",
            )
            return

        self.current_patient = get_or_create_patient(patient_id)
        self.current_patient_label.setText(f"Current Patient: {self.current_patient.patient_id}")
        self.new_scan_button.setEnabled(True)

        if not from_table_selection:
            self._refresh_patient_table()
        else:
            self._select_patient_row_by_patient_id(self.current_patient.patient_id)

        self._refresh_history_table()

        if self.history_table.rowCount() > 0:
            self.history_table.selectRow(0)
        else:
            self.scan_detail_widget.clear()
            self.image_viewer.set_annotation_rect(None)
            self.workspace_stack.setCurrentWidget(self.scan_detail_widget)

    def _refresh_history_table(self) -> None:
        self.history_table.setRowCount(0)

        if self.current_patient is None:
            return

        history = get_scan_history_for_patient(self.current_patient.id)
        self.history_table.setRowCount(len(history))

        for row_index, scan in enumerate(history):
            date_item = QTableWidgetItem(scan.scan_date)
            date_item.setData(Qt.ItemDataRole.UserRole, scan.id)

            accession_item = QTableWidgetItem(scan.accession_number or "—")
            box_item = QTableWidgetItem("Yes" if scan.annotation_present else "No")
            notes_item = QTableWidgetItem("Yes" if scan.notes_present else "No")

            self.history_table.setItem(row_index, 0, date_item)
            self.history_table.setItem(row_index, 1, accession_item)
            self.history_table.setItem(row_index, 2, box_item)
            self.history_table.setItem(row_index, 3, notes_item)

        self.history_table.resizeColumnsToContents()

    def _handle_history_selection(self) -> None:
        selected_items = self.history_table.selectedItems()
        if not selected_items:
            return

        first_item = selected_items[0]
        scan_id = first_item.data(Qt.ItemDataRole.UserRole)

        if scan_id is None:
            return

        scan_detail = get_scan_detail(scan_id)
        if scan_detail is None:
            self._show_warning(
                "Unable to Load Scan",
                "The selected scan could not be found in the local database.\n\n"
                "Refresh the patient or select another scan.",
            )
            return

        self.scan_detail_widget.load_scan(scan_detail)
        self.current_image_path = scan_detail.image_path or "sample_data/dummy_scan.png"
        self.image_viewer.load_image(self.current_image_path)
        self.image_viewer.set_annotation_rect(
            self._get_scan_box(scan_detail)
        )
        self.workspace_stack.setCurrentWidget(self.scan_detail_widget)

    def _start_new_scan(self) -> None:
        if self.current_patient is None:
            self._show_warning(
                "No Patient Loaded",
                "Load or select a patient before starting a new scan.",
            )
            return

        selected_image_path = self._prompt_for_scan_image()
        if selected_image_path is None:
            return

        self.history_table.clearSelection()
        self.new_scan_patient_label.setText(self.current_patient.patient_id)
        self.scan_date_edit.setDate(QDate.currentDate())
        self.accession_input.clear()
        self.warning_label.clear()
        self.annotation_notes_edit.clear()
        self.current_image_path = selected_image_path
        self.image_viewer.load_image(self.current_image_path)
        self.selected_image_label.setText(self.current_image_path)
        self.image_viewer.set_annotation_rect(None)
        self.workspace_stack.setCurrentWidget(self.new_scan_widget)

    def _prompt_for_scan_image(self) -> Optional[str]:
        initial_dir = self.project_root / "sample_data" / "unannotated"
        if not initial_dir.exists():
            initial_dir = self.project_root / "sample_data"

        dialog = QFileDialog(self, "Choose Image for New Scan", str(initial_dir))
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("Image Files (*.png *.jpg *.jpeg)")
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setStyleSheet(self._file_dialog_style())

        if dialog.exec() != QFileDialog.DialogCode.Accepted:
            return None

        selected_files = dialog.selectedFiles()
        if not selected_files:
            return None

        image_path = selected_files[0]
        portable_path = self._to_project_relative_path(image_path)
        if not self.image_viewer.load_image(portable_path):
            self._show_warning(
                "Unable to Load Image",
                "The selected image could not be opened.\n\n"
                "Choose a local PNG or JPG image.",
            )
            return None

        return portable_path

    def _to_project_relative_path(self, image_path: str) -> str:
        path = Path(image_path)
        try:
            return path.resolve().relative_to(self.project_root).as_posix()
        except ValueError:
            return image_path

    def _file_dialog_style(self) -> str:
        return """
            QFileDialog {
                background-color: #1f2430;
                color: #e8ecf1;
            }
            QFileDialog QWidget {
                background-color: #1f2430;
                color: #e8ecf1;
            }
            QFileDialog QLabel {
                color: #e8ecf1;
            }
            QFileDialog QLineEdit,
            QFileDialog QComboBox,
            QFileDialog QListView,
            QFileDialog QTreeView {
                background-color: #232833;
                color: #e8ecf1;
                border: 1px solid #3a3f4b;
                border-radius: 4px;
                padding: 4px;
                selection-background-color: #2f6fed;
                selection-color: #ffffff;
            }
            QFileDialog QHeaderView::section {
                background-color: #2a3140;
                color: #e8ecf1;
                border: 1px solid #3a3f4b;
                padding: 4px;
            }
            QFileDialog QPushButton {
                background-color: #2f6fed;
                border: none;
                border-radius: 6px;
                padding: 7px 12px;
                color: white;
                font-weight: bold;
                min-width: 72px;
            }
            QFileDialog QPushButton:hover {
                background-color: #3a7bff;
            }
            QFileDialog QComboBox QAbstractItemView {
                background-color: #232833;
                color: #e8ecf1;
                selection-background-color: #2f6fed;
            }
        """

    def _clear_current_patient_context(self) -> None:
        self.current_patient = None
        self.patient_id_input.clear()
        self.current_patient_label.setText("Current Patient: —")
        self.new_scan_button.setEnabled(False)

        self.history_table.clearSelection()
        self.history_table.setRowCount(0)

        self.warning_label.clear()
        self.accession_input.clear()
        self.new_scan_patient_label.setText("—")
        self.selected_image_label.setText("No image selected")
        self.annotation_notes_edit.clear()

        self.scan_detail_widget.clear()
        self.image_viewer.set_annotation_rect(None)
        self.workspace_stack.setCurrentWidget(self.scan_detail_widget)

    def _validate_before_save(self) -> tuple[bool, str, str]:
        if self.current_patient is None:
            return False, "No patient loaded.", ""

        if self.image_viewer.get_annotation_rect() is None:
            return (
                False,
                "Draw a box on the image before saving the scan.\n\n"
                "Click and drag over the image viewer to create the annotation box.",
                "",
            )

        return True, "", ""

    def _select_scan_row_by_id(self, scan_id: int) -> None:
        for row in range(self.history_table.rowCount()):
            item = self.history_table.item(row, 0)
            if item is None:
                continue

            item_scan_id = item.data(Qt.ItemDataRole.UserRole)
            if item_scan_id == scan_id:
                self.history_table.selectRow(row)
                return

    def _get_selected_scan_id(self) -> Optional[int]:
        selected_items = self.history_table.selectedItems()
        if not selected_items:
            return None

        first_item = selected_items[0]
        scan_id = first_item.data(Qt.ItemDataRole.UserRole)

        if scan_id is None:
            return None

        return int(scan_id)

    def _get_selected_patient_id_from_table(self) -> Optional[str]:
        selected_items = self.patient_table.selectedItems()
        if not selected_items:
            return None

        first_item = selected_items[0]
        patient_id = first_item.data(Qt.ItemDataRole.UserRole)

        if not patient_id:
            return None

        return str(patient_id)

    def _remove_selected_patient(self) -> None:
        patient_id = self._get_selected_patient_id_from_table()
        if patient_id is None:
            self._show_warning(
                "No Patient Selected",
                "Select a patient row in the Patient Directory before removing it.",
            )
            return

        patient = get_patient_by_patient_id(patient_id)
        if patient is None:
            self._show_warning(
                "Delete Failed",
                "The selected patient no longer exists in the database.\n\n"
                "The patient list will be refreshed.",
            )
            self._refresh_patient_table()
            self._clear_current_patient_context()
            return

        if not self._confirm(
            "Confirm Delete",
            "Delete the selected patient and all associated scans?",
        ):
            return

        deleted = delete_patient(patient.id)
        if not deleted:
            self._show_warning(
                "Delete Failed",
                "The selected patient could not be deleted from the local database.",
            )
            return

        self._show_info("Deleted", "Patient removed successfully.")

        self._refresh_patient_table()
        self._clear_current_patient_context()

    def _remove_selected_scan(self) -> None:
        if self.current_patient is None:
            self._show_warning(
                "No Patient Loaded",
                "Load or select a patient before removing a scan.",
            )
            return

        scan_id = self._get_selected_scan_id()
        if scan_id is None:
            self._show_warning(
                "No Scan Selected",
                "Select a scan row in Scan History before removing it.",
            )
            return

        if not self._confirm(
            "Confirm Delete",
            "Delete the selected scan?",
        ):
            return

        deleted = delete_scan(scan_id)
        if not deleted:
            self._show_warning(
                "Delete Failed",
                "The selected scan could not be deleted from the local database.\n\n"
                "It may have already been removed.",
            )
            return

        self._show_info("Deleted", "Scan removed successfully.")

        self._refresh_patient_table()
        self._refresh_history_table()

        if self.history_table.rowCount() > 0:
            self.history_table.selectRow(0)
        else:
            self.scan_detail_widget.clear()
            self.image_viewer.set_annotation_rect(None)
            self.workspace_stack.setCurrentWidget(self.scan_detail_widget)

    def _save_scan(self) -> None:
        is_valid, error_message, warning_message = self._validate_before_save()

        if not is_valid:
            self._show_warning(
                "Cannot Save Scan",
                error_message,
            )
            return

        if self.current_patient is None:
            self._show_warning(
                "No Patient Loaded",
                "Load or select a patient before saving a scan.",
            )
            return

        annotation_notes = self.annotation_notes_edit.toPlainText().strip()
        scan_date = self.scan_date_edit.date().toString("yyyy-MM-dd")
        accession_number = self.accession_input.text().strip()

        new_scan_id = save_scan(
            patient_fk=self.current_patient.id,
            scan_date=scan_date,
            accession_number=accession_number,
            lesions=[],
            annotation_box=self.image_viewer.get_annotation_rect(),
            notes=annotation_notes,
            image_path=self.current_image_path,
        )

        self.warning_label.setText(warning_message)
        self._show_info("Saved", "Scan saved successfully.")

        self._refresh_patient_table()
        self._refresh_history_table()
        self._select_scan_row_by_id(new_scan_id)

    def _get_scan_box(
        self,
        scan_detail,
    ) -> Optional[tuple[float, float, float, float]]:
        values = (
            scan_detail.box_x,
            scan_detail.box_y,
            scan_detail.box_w,
            scan_detail.box_h,
        )

        if any(value is None for value in values):
            return None

        return tuple(float(value) for value in values)

    def closeEvent(self, event) -> None:
        super().closeEvent(event)
