from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.database import get_connection
from app.models import Lesion, Patient, ScanDetail, ScanSummary


def get_patient_by_patient_id(patient_id: str) -> Optional[Patient]:
    """
    Return a Patient if found, otherwise None.
    """
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, patient_id
            FROM patients
            WHERE patient_id = ?
            """,
            (patient_id,),
        ).fetchone()

        if row is None:
            return None

        return Patient(
            id=row["id"],
            patient_id=row["patient_id"],
        )


def get_or_create_patient(patient_id: str) -> Patient:
    """
    Return an existing patient or create a new one.
    """
    existing = get_patient_by_patient_id(patient_id)
    if existing is not None:
        return existing

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO patients (patient_id)
            VALUES (?)
            """,
            (patient_id,),
        )
        conn.commit()

        return Patient(
            id=cursor.lastrowid,
            patient_id=patient_id,
        )


def get_all_patients_with_summary() -> list[dict]:
    """
    Return all patients with summary info for the Patient Directory table.

    Each dict contains:
    - patient_id
    - scan_count
    - latest_scan_date
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                p.patient_id AS patient_id,
                COUNT(s.id) AS scan_count,
                MAX(s.scan_date) AS latest_scan_date
            FROM patients p
            LEFT JOIN scans s ON s.patient_fk = p.id
            GROUP BY p.id, p.patient_id
            ORDER BY p.patient_id ASC
            """
        ).fetchall()

        results: list[dict] = []
        for row in rows:
            results.append(
                {
                    "patient_id": row["patient_id"],
                    "scan_count": row["scan_count"],
                    "latest_scan_date": row["latest_scan_date"],
                }
            )

        return results


def get_scan_history_for_patient(patient_fk: int) -> list[ScanSummary]:
    """
    Return scan history for a patient ordered by most recent scan date first.
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                s.id,
                s.patient_fk,
                s.scan_date,
                COALESCE(s.accession_number, '') AS accession_number,
                s.created_at,
                CASE
                    WHEN s.box_x IS NOT NULL
                     AND s.box_y IS NOT NULL
                     AND s.box_w IS NOT NULL
                     AND s.box_h IS NOT NULL THEN 1
                    WHEN COUNT(l.id) > 0 THEN 1
                    ELSE 0
                END AS annotation_present,
                CASE
                    WHEN COALESCE(s.notes, '') != '' THEN 1
                    WHEN EXISTS (
                        SELECT 1
                        FROM lesions ln
                        WHERE ln.scan_fk = s.id
                          AND COALESCE(ln.notes, '') != ''
                    ) THEN 1
                    ELSE 0
                END AS notes_present
            FROM scans s
            LEFT JOIN lesions l ON l.scan_fk = s.id
            WHERE s.patient_fk = ?
            GROUP BY s.id
            ORDER BY s.scan_date DESC, s.id DESC
            """,
            (patient_fk,),
        ).fetchall()

        history: list[ScanSummary] = []
        for row in rows:
            history.append(
                ScanSummary(
                    id=row["id"],
                    patient_fk=row["patient_fk"],
                    scan_date=row["scan_date"],
                    accession_number=row["accession_number"],
                    created_at=row["created_at"],
                    annotation_present=bool(row["annotation_present"]),
                    notes_present=bool(row["notes_present"]),
                )
            )

        return history


def save_scan(
    patient_fk: int,
    scan_date: str,
    accession_number: str,
    lesions: Optional[list[Lesion]] = None,
    demo_box: Optional[tuple[float, float, float, float]] = None,
    annotation_box: Optional[tuple[float, float, float, float]] = None,
    notes: str = "",
    image_path: str = "",
) -> int:
    """
    Save a new scan and optional compatibility lesions. Returns the new scan ID.
    """
    created_at = datetime.utcnow().isoformat(timespec="seconds")
    box = annotation_box if annotation_box is not None else demo_box
    box_x, box_y, box_w, box_h = (
        box if box is not None else (None, None, None, None)
    )
    demo_box_x, demo_box_y, demo_box_w, demo_box_h = (
        demo_box if demo_box is not None else (None, None, None, None)
    )

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO scans (
                patient_fk,
                scan_date,
                accession_number,
                created_at,
                demo_box_x,
                demo_box_y,
                demo_box_w,
                demo_box_h,
                box_x,
                box_y,
                box_w,
                box_h,
                notes,
                image_path
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                patient_fk,
                scan_date,
                accession_number.strip() or None,
                created_at,
                demo_box_x,
                demo_box_y,
                demo_box_w,
                demo_box_h,
                box_x,
                box_y,
                box_w,
                box_h,
                notes.strip() or None,
                image_path.strip() or None,
            ),
        )
        scan_id = cursor.lastrowid

        for lesion in lesions or []:
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
                    scan_id,
                    lesion.lesion_label,

                    lesion.long_x1,
                    lesion.long_y1,
                    lesion.long_z1,
                    lesion.long_x2,
                    lesion.long_y2,
                    lesion.long_z2,

                    lesion.short_x1,
                    lesion.short_y1,
                    lesion.short_z1,
                    lesion.short_x2,
                    lesion.short_y2,
                    lesion.short_z2,

                    lesion.long_diameter,
                    lesion.short_diameter,
                    lesion.notes.strip(),
                ),
            )

        conn.commit()

        return scan_id


def delete_scan(scan_id: int) -> bool:
    """
    Delete a scan and any legacy associated lesion rows.
    Returns True if the scan existed and was deleted, otherwise False.
    """
    with get_connection() as conn:
        scan_exists = conn.execute(
            """
            SELECT id
            FROM scans
            WHERE id = ?
            """,
            (scan_id,),
        ).fetchone()

        if scan_exists is None:
            return False

        conn.execute(
            """
            DELETE FROM lesions
            WHERE scan_fk = ?
            """,
            (scan_id,),
        )

        conn.execute(
            """
            DELETE FROM scans
            WHERE id = ?
            """,
            (scan_id,),
        )

        conn.commit()
        return True


def delete_patient(patient_fk: int) -> bool:
    """
    Delete a patient and all associated scans plus any legacy lesion rows.
    Returns True if the patient existed and was deleted, otherwise False.
    """
    with get_connection() as conn:
        patient_exists = conn.execute(
            """
            SELECT id
            FROM patients
            WHERE id = ?
            """,
            (patient_fk,),
        ).fetchone()

        if patient_exists is None:
            return False

        scan_rows = conn.execute(
            """
            SELECT id
            FROM scans
            WHERE patient_fk = ?
            """,
            (patient_fk,),
        ).fetchall()

        scan_ids = [row["id"] for row in scan_rows]

        for scan_id in scan_ids:
            conn.execute(
                """
                DELETE FROM lesions
                WHERE scan_fk = ?
                """,
                (scan_id,),
            )

        conn.execute(
            """
            DELETE FROM scans
            WHERE patient_fk = ?
            """,
            (patient_fk,),
        )

        conn.execute(
            """
            DELETE FROM patients
            WHERE id = ?
            """,
            (patient_fk,),
        )

        conn.commit()
        return True


def get_scan_detail(scan_id: int) -> Optional[ScanDetail]:
    """
    Return scan-level annotation detail, plus legacy lesions if present.
    """
    with get_connection() as conn:
        scan_row = conn.execute(
            """
            SELECT
                s.id,
                s.patient_fk,
                p.patient_id,
                s.scan_date,
                COALESCE(s.accession_number, '') AS accession_number,
                s.created_at,
                COALESCE(s.box_x, s.demo_box_x) AS box_x,
                COALESCE(s.box_y, s.demo_box_y) AS box_y,
                COALESCE(s.box_w, s.demo_box_w) AS box_w,
                COALESCE(s.box_h, s.demo_box_h) AS box_h,
                COALESCE(
                    s.notes,
                    (
                        SELECT l.notes
                        FROM lesions l
                        WHERE l.scan_fk = s.id
                          AND COALESCE(l.notes, '') != ''
                        ORDER BY l.id ASC
                        LIMIT 1
                    ),
                    ''
                ) AS notes,
                COALESCE(s.image_path, '') AS image_path
            FROM scans s
            JOIN patients p ON p.id = s.patient_fk
            WHERE s.id = ?
            """,
            (scan_id,),
        ).fetchone()

        if scan_row is None:
            return None

        lesion_rows = conn.execute(
            """
            SELECT *
            FROM lesions
            WHERE scan_fk = ?
            ORDER BY id ASC
            """,
            (scan_id,),
        ).fetchall()

        lesions: list[Lesion] = []
        for row in lesion_rows:
            lesions.append(
                Lesion(
                    id=row["id"],
                    scan_fk=row["scan_fk"],
                    lesion_label=row["lesion_label"],

                    long_x1=row["long_x1"],
                    long_y1=row["long_y1"],
                    long_z1=row["long_z1"],
                    long_x2=row["long_x2"],
                    long_y2=row["long_y2"],
                    long_z2=row["long_z2"],

                    short_x1=row["short_x1"],
                    short_y1=row["short_y1"],
                    short_z1=row["short_z1"],
                    short_x2=row["short_x2"],
                    short_y2=row["short_y2"],
                    short_z2=row["short_z2"],

                    long_diameter=row["long_diameter"],
                    short_diameter=row["short_diameter"],

                    notes=row["notes"] or "",
                )
            )

        return ScanDetail(
            id=scan_row["id"],
            patient_fk=scan_row["patient_fk"],
            patient_id=scan_row["patient_id"],
            scan_date=scan_row["scan_date"],
            accession_number=scan_row["accession_number"],
            created_at=scan_row["created_at"],
            box_x=scan_row["box_x"],
            box_y=scan_row["box_y"],
            box_w=scan_row["box_w"],
            box_h=scan_row["box_h"],
            notes=scan_row["notes"],
            image_path=scan_row["image_path"],
            lesions=lesions,
        )
