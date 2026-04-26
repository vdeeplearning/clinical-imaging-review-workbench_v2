# Clinical Imaging Review Workbench

Clinical Imaging Review Workbench is a Python desktop application that simulates a simple clinical imaging review workflow.

The current version is focused on a V2-lite workflow:

- one patient can have many scans
- each scan has one image
- each scan can have one rectangular box annotation
- each scan can have free-text notes
- saved scans can be reviewed later in read-only historical mode

This is a portfolio project. It is designed to demonstrate a healthcare-adjacent desktop workflow using Python, PySide6, SQLite, local image loading, annotation interaction, and persistent review history. It is not a diagnostic medical device and does not process real DICOM data.

---

## What The App Does

The app lets a user maintain a small local imaging review database.

A typical workflow is:

1. Load or create a patient by Patient ID.
2. Start a new scan for that patient.
3. Choose a local PNG or JPG image for the scan.
4. Draw one rectangular box annotation on the image.
5. Enter optional notes.
6. Save the scan.
7. Review the saved scan later from the patient's scan history.

The saved scan stores:

- patient association
- scan date
- optional accession / study ID
- image path
- box coordinates
- notes

The app also includes demo patients and synthetic x-ray-like sample images so the workflow can be tested immediately.

---

## Current Scope

Included:

- PySide6 desktop GUI
- local SQLite database
- patient directory
- patient loading / creation by Patient ID
- scan history table
- image viewer pane
- local PNG/JPG image loading
- click-and-drag rectangle annotation
- scan-level notes
- read-only historical scan review
- remove selected scan
- remove selected patient
- seeded demo data
- unannotated sample images for new scan testing

Not included:

- DICOM support
- PACS integration
- real radiology viewer tools
- window / level controls
- multi-slice navigation
- lesion-level linking
- multiple boxes per scan
- diagnostic measurement tools

---

## Tech Stack

- Python 3.11+
- PySide6
- SQLite
- JSON demo data
- Local PNG/JPG image files

---

## Project Structure

```text
clinical-imaging-review-workbench/
+-- app/
¦   +-- database.py          # SQLite connection, schema creation, lightweight migrations
¦   +-- models.py            # Dataclasses used by the app
¦   +-- seed_data.py         # Demo data seeding and demo annotation refresh
¦   +-- services.py          # Patient, scan, save, load, and delete operations
¦   +-- utils.py             # Legacy measurement helpers retained for compatibility
¦   +-- ui/
¦       +-- image_viewer.py  # Image display and rectangle drawing widget
¦       +-- lesion_form.py   # Minimal legacy compatibility wrapper
¦       +-- main_window.py   # Main PySide6 window and workflow wiring
¦       +-- scan_detail.py   # Read-only historical scan detail view
+-- docs/
¦   +-- screenshots/
+-- sample_data/
¦   +-- demo_data.json       # Seeded demo patients, scans, boxes, and image paths
¦   +-- demo_xray_*.png      # Annotated demo scan images used by seeded scans
¦   +-- dummy_scan.png       # Default fallback synthetic x-ray-like image
¦   +-- unannotated/         # Sample images users can choose for new scans
+-- main.py                  # Application entry point
+-- requirements.txt
+-- README.md
```

---

## Setup

### 1. Open A Terminal In The Project Folder

```powershell
cd clinical-imaging-review-workbench
```

### 2. Create A Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
```

macOS / Linux / WSL:

```bash
python3 -m venv .venv
```

### 3. Activate The Virtual Environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation for the current session, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

macOS / Linux / WSL:

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run The App

```bash
python main.py
```

---

## First Launch

When the app starts, it runs two setup steps automatically:

1. It creates or updates the local SQLite database.
2. If the database is empty, it seeds demo data from `sample_data/demo_data.json`.

The local database file is:

```text
clinical_imaging_review.db
```

After first launch, the Patient Directory should contain demo patients such as `PT-001`, `PT-002`, and so on.

---

## How To Use The App

### 1. Load A Patient

There are two ways to load a patient.

Option A: select an existing patient:

1. Look at the Patient Directory table on the left.
2. Click a patient row.
3. The app loads that patient and shows their scan history.

Option B: load or create by Patient ID:

1. Type a Patient ID into the Patient ID field.
2. Click `Load New or Existing Patient by Patient ID`.
3. If the patient already exists, the app loads that patient.
4. If the patient does not exist, the app creates a new patient record with that ID.

### 2. Review Existing Scans

After a patient is loaded:

1. The Scan History table shows scans for that patient.
2. Click a scan row.
3. The image viewer loads the scan image.
4. If the scan has a saved box, the box appears on the image.
5. The historical review panel shows scan metadata and notes.

Saved scans are read-only in the historical review workflow.

### 3. Create A New Scan

1. Load a patient first.
2. Click `New Scan`.
3. A file picker opens.
4. Choose a PNG or JPG image.
5. The app loads the selected image into the viewer.
6. The New Scan form appears.

The file picker starts in:

```text
sample_data/unannotated/
```

That folder contains dummy unannotated images you can use for testing.

### 4. Draw A Box Annotation

1. Move the mouse over the image viewer.
2. Press and hold the left mouse button.
3. Drag over the lesion or region of interest.
4. Release the mouse button.
5. The rectangle remains visible.

Only one box is supported for now. Drawing a new box replaces the previous box for the current unsaved scan.

### 5. Add Notes

Use the Annotation Notes field in the New Scan form to enter optional scan-level notes.

Examples:

```text
Small right upper lung nodule.
```

```text
Follow-up scan after treatment. Box marks visible target lesion.
```

### 6. Save The Scan

Click `Save Scan`.

The app requires a box annotation before saving. If no box has been drawn, the app shows a warning explaining how to create one.

When the scan is saved, the app stores:

- selected patient
- scan date
- accession / study ID if provided
- selected image path
- box coordinates
- annotation notes

The app then refreshes the Patient Directory and Scan History.

### 7. Remove A Scan

1. Load a patient.
2. Select a scan in Scan History.
3. Click `Remove Selected Scan`.
4. Confirm the deletion.

This removes the selected scan from the local database.

### 8. Remove A Patient

1. Select a patient in the Patient Directory.
2. Click `Remove Selected Patient`.
3. Confirm the deletion.

This removes the patient and their scans from the local database.

---

## Demo Images

The project includes two kinds of sample images.

Seeded demo scan images:

```text
sample_data/demo_xray_01.png
sample_data/demo_xray_02.png
...
sample_data/demo_xray_14.png
```

These are referenced by `demo_data.json`. They are used for the preloaded demo patient scans and already have saved boxes.

Unannotated test images:

```text
sample_data/unannotated/unannotated_scan_01.png
sample_data/unannotated/unannotated_scan_02.png
sample_data/unannotated/unannotated_scan_03.png
sample_data/unannotated/unannotated_scan_04.png
```

These are intended for the New Scan workflow. They are image files only; they do not have saved annotations until a user chooses one, draws a box, and saves the scan.

All included images are synthetic demo images. They are not real patient studies.

---

## Resetting Demo Data

To reset the app to a clean demo state:

1. Close the app.
2. Delete the local database file:

```text
clinical_imaging_review.db
```

3. Run the app again:

```bash
python main.py
```

The app recreates the database and reseeds from `sample_data/demo_data.json`.

Important: deleting the database also deletes any patients or scans you manually created while testing.

---

## Data Model Overview

The current product workflow is scan-level annotation:

```text
Patient
+-- Scan
    +-- image_path
    +-- box_x
    +-- box_y
    +-- box_w
    +-- box_h
    +-- notes
```

The database still contains a legacy `lesions` table for compatibility with earlier versions of the project. New scans no longer depend on endpoint-based lesion entry. The active workflow stores the box and notes directly on the scan record.

---

## Validation Behavior

The current save validation is intentionally simple:

- a patient must be loaded
- an image must be selected through New Scan
- a box must be drawn before saving

If a required step is missing, the app shows a warning dialog with an explanation and next step.

---

## Local Persistence

All data is stored locally in SQLite. The app does not send data to a server.

The main database file is:

```text
clinical_imaging_review.db
```

The app also uses local image paths. If you choose an image inside the project folder, the app stores a project-relative path when possible. This keeps demo records easier to move with the project.

---

## Notes For Reviewers

This project is intentionally scoped as a lightweight workflow prototype, not a complete clinical imaging platform.

The main things it demonstrates are:

- desktop application structure with PySide6
- reusable image viewer widget
- mouse-based rectangle drawing
- SQLite persistence
- demo data seeding
- simple patient and scan management
- incremental migration away from an older endpoint-based lesion model

Future directions could include:

- lesion-level box linking
- multiple annotations per scan
- richer image viewer controls
- import/copy image management
- DICOM support
- measurement tools
- export/report generation
