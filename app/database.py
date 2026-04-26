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
                FOREIGN KEY (patient_fk) REFERENCES patients(id)
            )
            """
        )

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

        conn.commit()