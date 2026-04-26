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


def seed_demo_data_if_needed() -> None:
    """
    Seed the database from sample_data/demo_data.json only if the DB is empty.
    Safe to call on every app startup.
    """
    if not database_is_empty():
        return

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
                )
            except Exception as exc:
                print(
                    f"[seed_data] Failed to save scan for patient "
                    f"{patient_id}, scan {scan_date}: {exc}"
                )