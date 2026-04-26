from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.models import ScanDetail
from app.ui.lesion_form import LesionFormWidget


class ScanDetailWidget(QWidget):
    """
    Read-only detail view for a saved scan.
    Shows scan metadata and read-only lesion cards.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._lesion_widgets: list[LesionFormWidget] = []

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
        self.lesion_count_label = QLabel("")
        self.total_burden_label = QLabel("")

        metadata_labels = [
            self.patient_label,
            self.scan_date_label,
            self.accession_label,
            self.lesion_count_label,
            self.total_burden_label,
        ]

        for label in metadata_labels:
            label.setStyleSheet("color: #d5dbe3;")
            main_layout.addWidget(label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: 1px solid #3a3f4b;
                border-radius: 6px;
                background-color: #1b1f27;
            }
            """
        )

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(12)
        self.scroll_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

    def clear(self) -> None:
        self.title_label.setText("Historical Review")
        self.patient_label.setText("Patient ID: —")
        self.scan_date_label.setText("Scan Date: —")
        self.accession_label.setText("Accession Number: —")
        self.lesion_count_label.setText("Lesion Count: —")
        self.total_burden_label.setText("Total Lesion Burden: —")

        self._clear_lesions()

    def load_scan(self, scan_detail: ScanDetail) -> None:
        self.title_label.setText("Historical Review")
        self.patient_label.setText(f"Patient ID: {scan_detail.patient_id}")
        self.scan_date_label.setText(f"Scan Date: {scan_detail.scan_date}")
        self.accession_label.setText(
            f"Accession Number: {scan_detail.accession_number or '—'}"
        )
        self.lesion_count_label.setText(f"Lesion Count: {scan_detail.lesion_count}")
        self.total_burden_label.setText(
            f"Total Lesion Burden: {scan_detail.total_burden:.2f} mm"
        )

        self._clear_lesions()

        for index, lesion in enumerate(scan_detail.lesions, start=1):
            lesion_widget = LesionFormWidget(
                lesion_number=index,
                lesion=lesion,
                read_only=True,
            )
            self._lesion_widgets.append(lesion_widget)
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, lesion_widget)

    def _clear_lesions(self) -> None:
        for widget in self._lesion_widgets:
            self.scroll_layout.removeWidget(widget)
            widget.deleteLater()
        self._lesion_widgets.clear()