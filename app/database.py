from __future__ import annotations

import sqlite3
from pathlib import Path


DB_FILENAME = "clinical_imaging_review.db"


def get_db_path() -> Path:
    """
    Return the path to the SQLite database file in the project root.
    """
    return Path(__file__).resolve().parent.parent / DB_FILENAME


def get_connection() -> sqlite3.Connection:
    """
    Create and return a SQLite connection with row access by column name.
    """
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database() -> None:
    """
    Create database tables if they do not already exist.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY,
                patient_id TEXT UNIQUE NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY,
                patient_fk INTEGER NOT NULL,
                scan_date TEXT NOT NULL,
                accession_number TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (patient_fk) REFERENCES patients(id) ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS lesions (
                id INTEGER PRIMARY KEY,
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

                FOREIGN KEY (scan_fk) REFERENCES scans(id) ON DELETE CASCADE
            )
            """
        )

        conn.commit()