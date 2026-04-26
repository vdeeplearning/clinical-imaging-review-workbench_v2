from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QTextEdit, QVBoxLayout, QWidget

from app.models import Lesion


class LesionFormWidget(QWidget):
    """
    Legacy compatibility wrapper.
    The active app now stores one scan-level box annotation plus notes; this widget
    remains only so older imports/tests do not fail during the transition.
    """

    def __init__(
        self,
        lesion_number: int,
        lesion: Optional[Lesion] = None,
        read_only: bool = False,
        simplified_entry: bool = False,
        on_remove=None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self.lesion_number = lesion_number
        self.read_only = read_only
        self.on_remove = on_remove

        self._build_ui()

        if lesion is not None:
            self.load_lesion(lesion)

        self.label_edit.setEnabled(not read_only)
        self.notes_edit.setEnabled(not read_only)

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        self.title_label = QLabel(f"Legacy Annotation {self.lesion_number}")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(self.title_label)

        form_layout = QFormLayout()
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("Annotation")
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Annotation notes...")
        self.notes_edit.setFixedHeight(100)

        form_layout.addRow("Label:", self.label_edit)
        form_layout.addRow("Notes:", self.notes_edit)
        main_layout.addLayout(form_layout)

    def load_lesion(self, lesion: Lesion) -> None:
        self.label_edit.setText(lesion.lesion_label)
        self.notes_edit.setPlainText(lesion.notes)
        self._update_title()

    def to_lesion(self) -> Lesion:
        return Lesion(
            id=None,
            scan_fk=None,
            lesion_label=self.label_edit.text().strip() or "Annotation",
            long_x1=0.0,
            long_y1=0.0,
            long_z1=0.0,
            long_x2=10.0,
            long_y2=0.0,
            long_z2=0.0,
            short_x1=0.0,
            short_y1=0.0,
            short_z1=0.0,
            short_x2=0.0,
            short_y2=5.0,
            short_z2=0.0,
            long_diameter=10.0,
            short_diameter=5.0,
            notes=self.notes_text(),
        )

    def notes_text(self) -> str:
        return self.notes_edit.toPlainText().strip()

    def renumber(self, lesion_number: int) -> None:
        self.lesion_number = lesion_number
        self._update_title()

    def _update_title(self) -> None:
        label = self.label_edit.text().strip()
        self.title_label.setText(
            f"Legacy Annotation {self.lesion_number}: {label}"
            if label
            else f"Legacy Annotation {self.lesion_number}"
        )
