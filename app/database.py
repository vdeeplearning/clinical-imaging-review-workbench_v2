from __future__ import annotations

import sqlite3
import sys
from pathlib import Path


DB_FILENAME = "clinical_imaging_review.db"


def get_base_path() -> Path:
    """
    Return the correct writable base path for both:
    - normal source execution -> project root
    - PyInstaller bundled execution -> folder containing the .exe
    """
    if getattr(sys, "frozen", False):
        # Running as a bundled executable
        return Path(sys.executable).resolve().parent

    # Running from source: app/database.py -> app -> project root
    return Path(__file__).resolve().parent.parent


def get_database_path() -> Path:
    return get_base_path() / DB_FILENAME


def get_connection() -> sqlite3.Connection:
    db_path = get_database_path()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Enable foreign key support (important for correctness, even if
    # current delete logic is explicit/manual).
    conn.execute("PRAGMA foreign_keys = ON;")

    return conn


def initialize_database() -> None:
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL UNIQUE
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_fk INTEGER NOT NULL,
                scan_date TEXT NOT NULL,
                accession_number TEXT,
                created_at TEXT,
                demo_box_x REAL,
                demo_box_y REAL,
                demo_box_w REAL,
                demo_box_h REAL,
                box_x REAL,
                box_y REAL,
                box_w REAL,
                box_h REAL,
                notes TEXT,
                image_path TEXT,
                FOREIGN KEY (patient_fk) REFERENCES patients(id)
            )
            """
        )
        _ensure_scan_columns(conn)

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS lesions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_fk INTEGER NOT NULL,
                lesion_label TEXT NOT NULL,

                long_x1 REAL NOT NULL,
                long_y1 REAL NOT NULL,
                long_z1 REAL NOT NULL,
                long_x2 REAL NOT NULL,
                long_y2 REAL NOT NULL,
                long_z2 REAL NOT NULL,

                short_x1 REAL NOT NULL,
                short_y1 REAL NOT NULL,
                short_z1 REAL NOT NULL,
                short_x2 REAL NOT NULL,
                short_y2 REAL NOT NULL,
                short_z2 REAL NOT NULL,

                long_diameter REAL NOT NULL,
                short_diameter REAL NOT NULL,

                notes TEXT,

                FOREIGN KEY (scan_fk) REFERENCES scans(id)
            )
            """
        )

        _backfill_scan_annotations(conn)
        conn.commit()


def _ensure_scan_columns(conn: sqlite3.Connection) -> None:
    existing_columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(scans)").fetchall()
    }

    migrations = {
        "created_at": "ALTER TABLE scans ADD COLUMN created_at TEXT",
        "demo_box_x": "ALTER TABLE scans ADD COLUMN demo_box_x REAL",
        "demo_box_y": "ALTER TABLE scans ADD COLUMN demo_box_y REAL",
        "demo_box_w": "ALTER TABLE scans ADD COLUMN demo_box_w REAL",
        "demo_box_h": "ALTER TABLE scans ADD COLUMN demo_box_h REAL",
        "box_x": "ALTER TABLE scans ADD COLUMN box_x REAL",
        "box_y": "ALTER TABLE scans ADD COLUMN box_y REAL",
        "box_w": "ALTER TABLE scans ADD COLUMN box_w REAL",
        "box_h": "ALTER TABLE scans ADD COLUMN box_h REAL",
        "notes": "ALTER TABLE scans ADD COLUMN notes TEXT",
        "image_path": "ALTER TABLE scans ADD COLUMN image_path TEXT",
    }

    for column_name, sql in migrations.items():
        if column_name not in existing_columns:
            conn.execute(sql)


def _backfill_scan_annotations(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        UPDATE scans
        SET
            box_x = COALESCE(box_x, demo_box_x),
            box_y = COALESCE(box_y, demo_box_y),
            box_w = COALESCE(box_w, demo_box_w),
            box_h = COALESCE(box_h, demo_box_h)
        WHERE
            box_x IS NULL
            AND box_y IS NULL
            AND box_w IS NULL
            AND box_h IS NULL
        """
    )

    conn.execute(
        """
        UPDATE scans
        SET notes = (
            SELECT l.notes
            FROM lesions l
            WHERE l.scan_fk = scans.id
              AND COALESCE(l.notes, '') != ''
            ORDER BY l.id ASC
            LIMIT 1
        )
        WHERE COALESCE(notes, '') = ''
          AND EXISTS (
              SELECT 1
              FROM lesions l
              WHERE l.scan_fk = scans.id
                AND COALESCE(l.notes, '') != ''
          )
        """
    )
