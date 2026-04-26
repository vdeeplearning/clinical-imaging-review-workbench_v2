# Clinical Imaging Review Workbench

A desktop application for structured longitudinal lesion annotation across serial imaging studies.

This project simulates a radiology-style workflow for tracking lesions over time using RECIST-inspired measurements. Users can load patients, create new scan entries, enter multiple lesions per scan, review historical scan data in read-only mode, and manage records through a desktop GUI.

Built as a portfolio project to demonstrate modern Python desktop application development, data modeling, validation logic, and healthcare-adjacent workflow design.

> **Recommended for reviewers:** Download the project ZIP from GitHub, follow the **For First-Time Users on Windows** steps below, and run `python main.py`.

---

## Screenshot

![Clinical Imaging Review Workbench](docs/screenshots/clinical-imaging-review-workbench_screenshot.png)

---

## What This App Does

This app simulates a radiology-style lesion tracking workflow across multiple imaging studies.

A user can:

- browse patients in a **Patient Directory**
- load a patient by **Patient ID**
- review that patient’s **scan history**
- create a **new scan**
- add **multiple lesions** to a scan
- enter RECIST-style:
  - long-axis endpoints
  - short-axis endpoints
  - notes
- review prior scans in **read-only mode**
- remove scans or patients
- start with **preloaded demo data** on first launch

---

## For First-Time Users on Windows (Recommended)

If you have **never used Python before**, follow these steps exactly.

### Step 1 — Install Python on Windows

1. Go to the official Python download page:
   - https://www.python.org/downloads/windows/

2. Download the latest **Windows installer (64-bit)**

3. Run the installer

4. **IMPORTANT:** On the first installer screen, check:

```text
Add Python to PATH