from __future__ import annotations

import json
import sys
from pathlib import Path

from app.database import get_connection
from app.models import Lesion
from app.services import get_or_create_patient, save_scan


def get_demo_data_path() -> Path | None:
    """
    Find demo_data.json in a robust way across:
    - source execution
    - PyInstaller one-dir
    - PyInstaller one-file
    """
    candidate_paths: list[Path] = []

    # PyInstaller runtime temp dir (especially important for one-file)
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        candidate_paths.append(Path(sys._MEIPASS) / "sample_data" / "demo_data.json")

    # Folder containing the executable (useful fallback for one-dir)
    if getattr(sys, "frozen", False):
        candidate_paths.append(Path(sys.executable).resolve().parent / "sample_data" / "demo_data.json")
        candidate_paths.append(Path(sys.executable).resolve().parent / "_internal" / "sample_data" / "demo_data.json")

    # Normal source mode: project root / sample_data / demo_data.json
    candidate_paths.append(Path(__file__).resolve().parent.parent / "sample_data" / "demo_data.json")

    for path in candidate_paths:
        if path.exists():
            return path

    return None


def database_is_empty() -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS count FROM patients")
        row = cur.fetchone()
        count = row["count"] if row is not None else 0
        return count == 0


def _lesion_from_json(lesion_json: dict) -> Lesion:
    long_axis = lesion_json["long"]
    short_axis = lesion_json["short"]

    return Lesion(
        id=None,
        scan_fk=None,
        lesion_label=lesion_json["lesion_label"],

        long_x1=float(long_axis["x1"]),
        long_y1=float(long_axis["y1"]),
        long_z1=float(long_axis["z1"]),
        long_x2=float(long_axis["x2"]),
        long_y2=float(long_axis["y2"]),
        long_z2=float(long_axis["z2"]),

        short_x1=float(short_axis["x1"]),
        short_y1=float(short_axis["y1"]),
        short_z1=float(short_axis["z1"]),
        short_x2=float(short_axis["x2"]),
        short_y2=float(short_axis["y2"]),
        short_z2=float(short_axis["z2"]),

        long_diameter=0.0,
        short_diameter=0.0,

        notes=lesion_json.get("notes", ""),
    )


def _annotation_box_from_json(scan_json: dict) -> tuple[float, float, float, float] | None:
    box_json = scan_json.get("box")
    if not isinstance(box_json, dict):
        return None

    try:
        return (
            float(box_json["x"]),
            float(box_json["y"]),
            float(box_json["w"]),
            float(box_json["h"]),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _annotation_notes_from_json(scan_json: dict) -> str:
    notes = str(scan_json.get("notes", "")).strip()
    if notes:
        return notes

    lesions = scan_json.get("lesions", [])
    if isinstance(lesions, list) and lesions:
        return str(lesions[0].get("notes", "")).strip()

    return ""


def _image_path_from_json(scan_json: dict) -> str:
    return str(scan_json.get("image_path", "sample_data/dummy_scan.png")).strip()


def seed_demo_data_if_needed() -> None:
    """
    Seed the database from sample_data/demo_data.json only if the DB is empty.
    Safe to call on every app startup.
    """
    demo_path = get_demo_data_path()

    if demo_path is None:
        print("[seed_data] Demo data file not found in any expected location.")
        return

    try:
        with demo_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception as exc:
        print(f"[seed_data] Failed to read demo data: {exc}")
        return

    patients = payload.get("patients", [])
    if not isinstance(patients, list):
        print("[seed_data] Invalid demo data format: 'patients' must be a list.")
        return

    if not database_is_empty():
        _update_existing_demo_annotations(patients)
        return

    for patient_json in patients:
        patient_id = str(patient_json.get("patient_id", "")).strip()
        if not patient_id:
            continue

        patient = get_or_create_patient(patient_id)

        scans = patient_json.get("scans", [])
        if not isinstance(scans, list):
            continue

        for scan_json in scans:
            scan_date = str(scan_json.get("scan_date", "")).strip()
            if not scan_date:
                continue

            accession_number = str(scan_json.get("accession_number", "")).strip()

            lesions_json = scan_json.get("lesions", [])
            if not isinstance(lesions_json, list) or not lesions_json:
                continue

            lesions: list[Lesion] = []
            for lesion_json in lesions_json:
                try:
                    lesion = _lesion_from_json(lesion_json)
                    lesions.append(lesion)
                except Exception as exc:
                    print(
                        f"[seed_data] Skipping invalid lesion for patient "
                        f"{patient_id}, scan {scan_date}: {exc}"
                    )

            if not lesions:
                continue

            try:
                save_scan(
                    patient_fk=patient.id,
                    scan_date=scan_date,
                    accession_number=accession_number,
                    lesions=lesions,
                    annotation_box=_annotation_box_from_json(scan_json),
                    notes=_annotation_notes_from_json(scan_json),
                    image_path=_image_path_from_json(scan_json),
                )
            except Exception as exc:
                print(
                    f"[seed_data] Failed to save scan for patient "
                    f"{patient_id}, scan {scan_date}: {exc}"
                )


def _update_existing_demo_annotations(patients: list[dict]) -> None:
    with get_connection() as conn:
        for patient_json in patients:
            patient_id = str(patient_json.get("patient_id", "")).strip()
            scans = patient_json.get("scans", [])
            if not patient_id or not isinstance(scans, list):
                continue

            for scan_json in scans:
                box = _annotation_box_from_json(scan_json)
                if box is None:
                    continue

                scan_date = str(scan_json.get("scan_date", "")).strip()
                accession_number = str(scan_json.get("accession_number", "")).strip()
                notes = _annotation_notes_from_json(scan_json)
                image_path = _image_path_from_json(scan_json)

                conn.execute(
                    """
                    UPDATE scans
                    SET
                        box_x = ?,
                        box_y = ?,
                        box_w = ?,
                        box_h = ?,
                        notes = COALESCE(NULLIF(notes, ''), ?),
                        image_path = ?
                    WHERE id IN (
                        SELECT s.id
                        FROM scans s
                        JOIN patients p ON p.id = s.patient_fk
                        WHERE p.patient_id = ?
                          AND s.scan_date = ?
                          AND COALESCE(s.accession_number, '') = ?
                    )
                    """,
                    (
                        box[0],
                        box[1],
                        box[2],
                        box[3],
                        notes or None,
                        image_path or None,
                        patient_id,
                        scan_date,
                        accession_number,
                    ),
                )

        conn.commit()
