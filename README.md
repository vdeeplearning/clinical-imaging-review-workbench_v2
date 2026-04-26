# Clinical Imaging Review Workbench

A desktop application for structured longitudinal lesion annotation across serial imaging studies.

This project simulates a radiology-style workflow for tracking lesions over time using RECIST-inspired measurements. Users can browse patients, create new scan entries, add multiple lesions per scan, review historical scan data in read-only mode, and manage records through a desktop GUI.

Built as a portfolio project to demonstrate modern Python desktop application development, data modeling, validation logic, and healthcare-adjacent workflow design.

---

## Screenshot

![Clinical Imaging Review Workbench](docs/screenshots/clinical-imaging-review-workbench_screenshot.png)

---

## Features

- **Patient Directory**
  - View all patients in a table
  - See number of scans and latest scan date
  - Load a patient by selecting from the directory or entering a Patient ID

- **Scan History**
  - Review all scans for the selected patient
  - See scan date, accession / study ID, lesion count, and total burden

- **Structured Lesion Entry**
  - Create a new scan with multiple lesions
  - Record:
    - lesion label
    - long-axis endpoints `(x1, y1, z1) → (x2, y2, z2)`
    - short-axis endpoints `(x1, y1, z1) → (x2, y2, z2)`
    - computed long diameter
    - computed short diameter
    - free-text notes

- **Historical Review**
  - Past scans are displayed in read-only mode after save
  - Supports longitudinal comparison across serial studies

- **Record Management**
  - Remove selected scan
  - Remove selected patient

- **Demo Data**
  - On first launch, the app auto-loads sample data if the database is empty
  - Makes the project immediately usable for demos / portfolio review

---

## Tech Stack

- **Python 3.11+**
- **PySide6** (desktop GUI)
- **SQLite** (local persistence)
- **JSON** (demo data seeding)

---

## Project Structure

```text
clinical-imaging-review-workbench/
├── app/
│   ├── database.py
│   ├── models.py
│   ├── seed_data.py
│   ├── services.py
│   ├── utils.py
│   └── ui/
│       ├── lesion_form.py
│       ├── main_window.py
│       └── scan_detail.py
├── docs/
│   └── screenshots/
│       └── clinical-imaging-review-workbench_screenshot.png
├── sample_data/
│   └── demo_data.json
├── main.py
├── requirements.txt
└── README.md