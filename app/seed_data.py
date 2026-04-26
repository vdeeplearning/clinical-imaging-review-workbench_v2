from __future__ import annotations

import json
from pathlib import Path

from app.database import get_connection
from app.utils import euclidean_distance_3d


def seed_demo_data_if_empty() -> None:
    """
    Seed demo JSON data into the SQLite database only if there are no patients yet.
    Safe to call at every startup.
    """
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM patients").fetchone()
        patient_count = row["count"]

    if patient_count > 0:
        return

    base_dir = Path(__file__).resolve().parent.parent
    json_path = base_dir / "sample_data" / "demo_data.json"

    if not json_path.exists():
        print("Demo JSON file not found. Skipping demo data seeding.")
        return

    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    patients = data.get("patients", [])
    if not isinstance(patients, list):
        print("Invalid demo JSON format: 'patients' must be a list.")
        return

    with get_connection() as conn:
        for patient_obj in patients:
            patient_id = str(patient_obj.get("patient_id", "")).strip()
            if not patient_id:
                continue

            # Insert patient
            patient_cursor = conn.execute(
                """
                INSERT INTO patients (patient_id)
                VALUES (?)
                """,
                (patient_id,),
            )
            patient_fk = patient_cursor.lastrowid

            scans = patient_obj.get("scans", [])
            if not isinstance(scans, list):
                continue

            for scan_obj in scans:
                scan_date = str(scan_obj.get("scan_date", "")).strip()
                accession_number = str(scan_obj.get("accession_number", "")).strip()

                if not scan_date:
                    continue

                # Insert scan
                scan_cursor = conn.execute(
                    """
                    INSERT INTO scans (patient_fk, scan_date, accession_number, created_at)
                    VALUES (?, ?, ?, datetime('now'))
                    """,
                    (patient_fk, scan_date, accession_number or None),
                )
                scan_fk = scan_cursor.lastrowid

                lesions = scan_obj.get("lesions", [])
                if not isinstance(lesions, list):
                    continue

                for lesion_obj in lesions:
                    lesion_label = str(lesion_obj.get("lesion_label", "")).strip()
                    notes = str(lesion_obj.get("notes", "")).strip()

                    long_axis = lesion_obj.get("long", {})
                    short_axis = lesion_obj.get("short", {})

                    try:
                        long_x1 = float(long_axis.get("x1", 0))
                        long_y1 = float(long_axis.get("y1", 0))
                        long_z1 = float(long_axis.get("z1", 0))
                        long_x2 = float(long_axis.get("x2", 0))
                        long_y2 = float(long_axis.get("y2", 0))
                        long_z2 = float(long_axis.get("z2", 0))

                        short_x1 = float(short_axis.get("x1", 0))
                        short_y1 = float(short_axis.get("y1", 0))
                        short_z1 = float(short_axis.get("z1", 0))
                        short_x2 = float(short_axis.get("x2", 0))
                        short_y2 = float(short_axis.get("y2", 0))
                        short_z2 = float(short_axis.get("z2", 0))
                    except (TypeError, ValueError):
                        continue

                    long_diameter = euclidean_distance_3d(
                        long_x1, long_y1, long_z1,
                        long_x2, long_y2, long_z2,
                    )

                    short_diameter = euclidean_distance_3d(
                        short_x1, short_y1, short_z1,
                        short_x2, short_y2, short_z2,
                    )

                    conn.execute(
                        """
                        INSERT INTO lesions (
                            scan_fk,
                            lesion_label,

                            long_x1, long_y1, long_z1,
                            long_x2, long_y2, long_z2,

                            short_x1, short_y1, short_z1,
                            short_x2, short_y2, short_z2,

                            long_diameter,
                            short_diameter,
                            notes
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            scan_fk,
                            lesion_label,

                            long_x1,
                            long_y1,
                            long_z1,
                            long_x2,
                            long_y2,
                            long_z2,

                            short_x1,
                            short_y1,
                            short_z1,
                            short_x2,
                            short_y2,
                            short_z2,

                            long_diameter,
                            short_diameter,
                            notes,
                        ),
                    )

        conn.commit()

    print("Demo data seeded successfully.")