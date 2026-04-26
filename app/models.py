from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Patient:
    id: int
    patient_id: str


@dataclass
class Lesion:
    id: Optional[int]
    scan_fk: Optional[int]
    lesion_label: str

    long_x1: float
    long_y1: float
    long_z1: float
    long_x2: float
    long_y2: float
    long_z2: float

    short_x1: float
    short_y1: float
    short_z1: float
    short_x2: float
    short_y2: float
    short_z2: float

    long_diameter: float
    short_diameter: float

    notes: str = ""


@dataclass
class ScanSummary:
    id: int
    patient_fk: int
    scan_date: str
    accession_number: str
    created_at: str
    annotation_present: bool
    notes_present: bool


@dataclass
class ScanDetail:
    id: int
    patient_fk: int
    patient_id: str
    scan_date: str
    accession_number: str
    created_at: str
    box_x: Optional[float] = None
    box_y: Optional[float] = None
    box_w: Optional[float] = None
    box_h: Optional[float] = None
    notes: str = ""
    image_path: str = ""
    lesions: list[Lesion] = field(default_factory=list)

    @property
    def lesion_count(self) -> int:
        return 1 if self._has_scan_box() else len(self.lesions)

    @property
    def total_burden(self) -> float:
        return sum(lesion.long_diameter for lesion in self.lesions)

    def _has_scan_box(self) -> bool:
        return all(
            value is not None
            for value in (self.box_x, self.box_y, self.box_w, self.box_h)
        )
