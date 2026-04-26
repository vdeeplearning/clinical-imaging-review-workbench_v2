from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.models import Lesion
from app.utils import euclidean_distance_3d


class LesionFormWidget(QFrame):
    """
    Reusable lesion card widget.
    Supports:
    - editable mode (new scan entry)
    - read-only mode (historical review)
    """

    def __init__(
        self,
        lesion_number: int,
        lesion: Optional[Lesion] = None,
        read_only: bool = False,
        on_remove=None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self.lesion_number = lesion_number
        self.read_only = read_only
        self.on_remove = on_remove

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("lesionCard")
        self.setStyleSheet(
            """
            QFrame#lesionCard {
                border: 1px solid #3a3f4b;
                border-radius: 8px;
                background-color: #232833;
            }
            QLabel {
                color: #e8ecf1;
            }
            QGroupBox {
                color: #e8ecf1;
                font-weight: bold;
                border: 1px solid #3a3f4b;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px 0 4px;
            }
            """
        )

        self._build_ui()

        if lesion is not None:
            self.load_lesion(lesion)

        self._update_measurements()
        self._apply_read_only_state()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)

        header_layout = QHBoxLayout()
        self.title_label = QLabel(f"Lesion {self.lesion_number}")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        self.remove_button = QPushButton("Remove Lesion")
        self.remove_button.clicked.connect(self._handle_remove)
        header_layout.addWidget(self.remove_button)

        main_layout.addLayout(header_layout)

        # Lesion label
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("e.g. Target 1")
        self.label_edit.textChanged.connect(self._update_title_from_label)

        form_layout = QFormLayout()
        form_layout.addRow("Lesion Label:", self.label_edit)
        main_layout.addLayout(form_layout)

        # Long axis
        self.long_group = QGroupBox("Long Axis Endpoints")
        long_layout = QGridLayout()

        self.long_x1 = self._make_coord_spinbox()
        self.long_y1 = self._make_coord_spinbox()
        self.long_z1 = self._make_coord_spinbox()
        self.long_x2 = self._make_coord_spinbox()
        self.long_y2 = self._make_coord_spinbox()
        self.long_z2 = self._make_coord_spinbox()

        long_layout.addWidget(QLabel("Point A"), 0, 0)
        long_layout.addWidget(QLabel("X"), 0, 1)
        long_layout.addWidget(self.long_x1, 0, 2)
        long_layout.addWidget(QLabel("Y"), 0, 3)
        long_layout.addWidget(self.long_y1, 0, 4)
        long_layout.addWidget(QLabel("Z"), 0, 5)
        long_layout.addWidget(self.long_z1, 0, 6)

        long_layout.addWidget(QLabel("Point B"), 1, 0)
        long_layout.addWidget(QLabel("X"), 1, 1)
        long_layout.addWidget(self.long_x2, 1, 2)
        long_layout.addWidget(QLabel("Y"), 1, 3)
        long_layout.addWidget(self.long_y2, 1, 4)
        long_layout.addWidget(QLabel("Z"), 1, 5)
        long_layout.addWidget(self.long_z2, 1, 6)

        self.long_group.setLayout(long_layout)
        main_layout.addWidget(self.long_group)

        # Short axis
        self.short_group = QGroupBox("Short Axis Endpoints")
        short_layout = QGridLayout()

        self.short_x1 = self._make_coord_spinbox()
        self.short_y1 = self._make_coord_spinbox()
        self.short_z1 = self._make_coord_spinbox()
        self.short_x2 = self._make_coord_spinbox()
        self.short_y2 = self._make_coord_spinbox()
        self.short_z2 = self._make_coord_spinbox()

        short_layout.addWidget(QLabel("Point A"), 0, 0)
        short_layout.addWidget(QLabel("X"), 0, 1)
        short_layout.addWidget(self.short_x1, 0, 2)
        short_layout.addWidget(QLabel("Y"), 0, 3)
        short_layout.addWidget(self.short_y1, 0, 4)
        short_layout.addWidget(QLabel("Z"), 0, 5)
        short_layout.addWidget(self.short_z1, 0, 6)

        short_layout.addWidget(QLabel("Point B"), 1, 0)
        short_layout.addWidget(QLabel("X"), 1, 1)
        short_layout.addWidget(self.short_x2, 1, 2)
        short_layout.addWidget(QLabel("Y"), 1, 3)
        short_layout.addWidget(self.short_y2, 1, 4)
        short_layout.addWidget(QLabel("Z"), 1, 5)
        short_layout.addWidget(self.short_z2, 1, 6)

        self.short_group.setLayout(short_layout)
        main_layout.addWidget(self.short_group)

        # Measurements
        measurement_layout = QHBoxLayout()

        self.long_diameter_label = QLabel("Long Diameter: 0.00 mm")
        self.short_diameter_label = QLabel("Short Diameter: 0.00 mm")

        self.long_diameter_label.setStyleSheet("font-weight: bold;")
        self.short_diameter_label.setStyleSheet("font-weight: bold;")

        measurement_layout.addWidget(self.long_diameter_label)
        measurement_layout.addSpacing(24)
        measurement_layout.addWidget(self.short_diameter_label)
        measurement_layout.addStretch()

        main_layout.addLayout(measurement_layout)

        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter free-text notes...")
        self.notes_edit.setFixedHeight(80)

        notes_layout = QFormLayout()
        notes_layout.addRow("Notes:", self.notes_edit)
        main_layout.addLayout(notes_layout)

    def _make_coord_spinbox(self) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(-100000.0, 100000.0)
        spin.setDecimals(2)
        spin.setSingleStep(1.0)
        spin.setAlignment(Qt.AlignmentFlag.AlignRight)
        spin.valueChanged.connect(self._update_measurements)
        return spin

    def _update_title_from_label(self) -> None:
        label = self.label_edit.text().strip()
        if label:
            self.title_label.setText(f"Lesion {self.lesion_number}: {label}")
        else:
            self.title_label.setText(f"Lesion {self.lesion_number}")

    def _update_measurements(self) -> None:
        long_diameter = euclidean_distance_3d(
            self.long_x1.value(),
            self.long_y1.value(),
            self.long_z1.value(),
            self.long_x2.value(),
            self.long_y2.value(),
            self.long_z2.value(),
        )

        short_diameter = euclidean_distance_3d(
            self.short_x1.value(),
            self.short_y1.value(),
            self.short_z1.value(),
            self.short_x2.value(),
            self.short_y2.value(),
            self.short_z2.value(),
        )

        self.long_diameter_label.setText(f"Long Diameter: {long_diameter:.2f} mm")
        self.short_diameter_label.setText(f"Short Diameter: {short_diameter:.2f} mm")

    def _apply_read_only_state(self) -> None:
        widgets = [
            self.label_edit,
            self.long_x1,
            self.long_y1,
            self.long_z1,
            self.long_x2,
            self.long_y2,
            self.long_z2,
            self.short_x1,
            self.short_y1,
            self.short_z1,
            self.short_x2,
            self.short_y2,
            self.short_z2,
            self.notes_edit,
        ]

        for widget in widgets:
            widget.setEnabled(not self.read_only)

        self.remove_button.setVisible(not self.read_only)

    def _handle_remove(self) -> None:
        if self.on_remove is not None:
            self.on_remove(self)

    def load_lesion(self, lesion: Lesion) -> None:
        self.label_edit.setText(lesion.lesion_label)

        self.long_x1.setValue(lesion.long_x1)
        self.long_y1.setValue(lesion.long_y1)
        self.long_z1.setValue(lesion.long_z1)
        self.long_x2.setValue(lesion.long_x2)
        self.long_y2.setValue(lesion.long_y2)
        self.long_z2.setValue(lesion.long_z2)

        self.short_x1.setValue(lesion.short_x1)
        self.short_y1.setValue(lesion.short_y1)
        self.short_z1.setValue(lesion.short_z1)
        self.short_x2.setValue(lesion.short_x2)
        self.short_y2.setValue(lesion.short_y2)
        self.short_z2.setValue(lesion.short_z2)

        self.notes_edit.setPlainText(lesion.notes)

        self._update_title_from_label()
        self._update_measurements()

    def to_lesion(self) -> Lesion:
        """
        Build a Lesion dataclass from current widget values.
        """
        long_diameter = euclidean_distance_3d(
            self.long_x1.value(),
            self.long_y1.value(),
            self.long_z1.value(),
            self.long_x2.value(),
            self.long_y2.value(),
            self.long_z2.value(),
        )

        short_diameter = euclidean_distance_3d(
            self.short_x1.value(),
            self.short_y1.value(),
            self.short_z1.value(),
            self.short_x2.value(),
            self.short_y2.value(),
            self.short_z2.value(),
        )

        return Lesion(
            id=None,
            scan_fk=None,
            lesion_label=self.label_edit.text().strip(),

            long_x1=self.long_x1.value(),
            long_y1=self.long_y1.value(),
            long_z1=self.long_z1.value(),
            long_x2=self.long_x2.value(),
            long_y2=self.long_y2.value(),
            long_z2=self.long_z2.value(),

            short_x1=self.short_x1.value(),
            short_y1=self.short_y1.value(),
            short_z1=self.short_z1.value(),
            short_x2=self.short_x2.value(),
            short_y2=self.short_y2.value(),
            short_z2=self.short_z2.value(),

            long_diameter=long_diameter,
            short_diameter=short_diameter,

            notes=self.notes_edit.toPlainText().strip(),
        )

    def renumber(self, lesion_number: int) -> None:
        self.lesion_number = lesion_number
        self._update_title_from_label()