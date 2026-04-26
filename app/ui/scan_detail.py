from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.models import ScanDetail


class ScanDetailWidget(QWidget):
    """
    Read-only detail view for a saved scan.
    Shows scan metadata and scan-level annotation notes.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._build_ui()
        self.clear()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)

        self.title_label = QLabel("Historical Review")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e8ecf1;")
        main_layout.addWidget(self.title_label)

        self.patient_label = QLabel("")
        self.scan_date_label = QLabel("")
        self.accession_label = QLabel("")
        self.box_label = QLabel("")
        self.notes_label = QLabel("")
        self.notes_label.setWordWrap(True)

        metadata_labels = [
            self.patient_label,
            self.scan_date_label,
            self.accession_label,
            self.box_label,
            self.notes_label,
        ]

        for label in metadata_labels:
            label.setStyleSheet("color: #d5dbe3;")
            main_layout.addWidget(label)
        main_layout.addStretch()

    def clear(self) -> None:
        self.title_label.setText("Historical Review")
        self.patient_label.setText("Patient ID: -")
        self.scan_date_label.setText("Scan Date: -")
        self.accession_label.setText("Accession Number: -")
        self.box_label.setText("Box Annotation: -")
        self.notes_label.setText("Annotation Notes: -")

    def load_scan(self, scan_detail: ScanDetail) -> None:
        self.title_label.setText("Historical Review")
        self.patient_label.setText(f"Patient ID: {scan_detail.patient_id}")
        self.scan_date_label.setText(f"Scan Date: {scan_detail.scan_date}")
        self.accession_label.setText(
            f"Accession Number: {scan_detail.accession_number or '-'}"
        )
        self.box_label.setText(
            f"Box Annotation: {'Yes' if self._has_box(scan_detail) else 'No'}"
        )
        self.notes_label.setText(f"Annotation Notes: {scan_detail.notes or '-'}")

    def _has_box(self, scan_detail: ScanDetail) -> bool:
        return all(
            value is not None
            for value in (
                scan_detail.box_x,
                scan_detail.box_y,
                scan_detail.box_w,
                scan_detail.box_h,
            )
        )
