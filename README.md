# Clinical Imaging Review Workbench

A desktop application for structured longitudinal lesion annotation across serial imaging studies.

This project simulates a radiology-style workflow for tracking lesions over time using RECIST-inspired measurements. Users can load patients, create new scan entries, enter multiple lesions per scan, review historical scan data in read-only mode, and manage records through a desktop GUI.

Built as a portfolio project to demonstrate modern Python desktop application development, data modeling, validation logic, and healthcare-adjacent workflow design.

---

## Screenshot

> Add your screenshot file here:
> `docs/screenshots/patient-directory-and-history.png`

![Clinical Imaging Review Workbench](docs/screenshots/patient-directory-and-history.png)

---

## Why I Built This

I wanted to build a practical, domain-inspired desktop application that feels closer to real-world clinical software than a toy CRUD app.

This project demonstrates:

- **Python desktop GUI development** with PySide6
- **Relational data modeling** with SQLite
- **Longitudinal workflow design** (patients → scans → lesions)
- **Structured medical-style data entry**
- **Validation and UX guardrails**
- **Local demo data seeding for immediate usability**
- A foundation that can later be extended into:
  - image viewing
  - mouse-based lesion box annotation
  - DICOM support
  - AI-assisted measurement suggestions
  - agentic workflow orchestration

---

## Core Features

### Patient Management
- Load a patient by **Patient ID**
- Automatically create new patients on first load
- Browse all patients in a **Patient Directory**
- View:
  - patient ID
  - number of scans
  - latest scan date
- **Remove selected patient** (with confirmation)

### Scan Management
- View full **scan history** for the selected patient
- Each scan includes:
  - scan date
  - accession / study ID
  - lesion count
  - total burden (sum of long diameters)
- **Remove selected scan** (with confirmation)

### Structured Lesion Entry
- Create a **new scan** for the current patient
- Add **multiple lesions per scan**
- Each lesion includes:
  - lesion label
  - long-axis endpoints: `(x1, y1, z1)` → `(x2, y2, z2)`
  - short-axis endpoints: `(x1, y1, z1)` → `(x2, y2, z2)`
  - computed long diameter
  - computed short diameter
  - free-text notes
- Supports RECIST-style structured measurements using manually entered endpoints

### Historical Review
- Historical scans are displayed in **read-only mode**
- Users can review all prior lesions and measurements for longitudinal comparison

### Demo Data
- App auto-seeds a **demo JSON file** on first launch if the database is empty
- Makes the app immediately usable for GitHub reviewers / recruiters / demo users

---

## Tech Stack

- **Python 3.11+**
- **PySide6** (desktop GUI)
- **SQLite** (local persistence)
- **JSON** (demo data seeding)
- **WSL + VS Code** (development workflow)

---

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd clinical-imaging-review-workbench