Clinical Imaging Review Workbench
A desktop application for structured longitudinal lesion annotation across serial imaging studies.
This project simulates a radiology-style workflow for tracking lesions over time using RECIST-inspired measurements. Users can load patients, create new scan entries, enter multiple lesions per scan, review historical scan data in read-only mode, and manage records through a desktop GUI.
Built as a portfolio project to demonstrate modern Python desktop application development, data modeling, validation logic, and healthcare-adjacent workflow design.
> **Recommended for reviewers:** If you are on a Windows computer and have never used Python before, follow the **Step-by-Step Windows Setup (Beginner-Friendly)** section below exactly as written.
---
Screenshot
![Clinical Imaging Review Workbench](docs/screenshots/clinical-imaging-review-workbench_screenshot.png)
---
What This App Does
This app simulates a radiology-style lesion tracking workflow across multiple imaging studies.
A user can:
browse patients in a Patient Directory
load a patient by Patient ID
review that patient’s scan history
create a new scan
add multiple lesions to a scan
enter RECIST-style:
long-axis endpoints
short-axis endpoints
notes
review prior scans in read-only mode
remove scans or patients
start with preloaded demo data on first launch
---
Step-by-Step Windows Setup (Beginner-Friendly)
If you have never used Python before, follow these instructions exactly.
These steps are written for someone sitting at a Windows computer starting from zero.
Step 1 — Install Python
Open your web browser.
Go to:
```text
https://www.python.org/downloads/windows/
```
Download the latest Python 3 Windows installer (64-bit).
Run the installer.
On the first installer screen, make sure you check:
```text
Add Python to PATH
```
Click:
```text
Install Now
```
Wait for installation to finish, then close the installer.
Verify Python installed correctly
Open PowerShell (you can search for “PowerShell” in the Windows Start menu), then run:
```powershell
python --version
```
You should see something like:
```text
Python 3.12.3
```
If you instead see “Python was not found,” reinstall Python and make sure Add Python to PATH is checked.
---
Step 2 — Download This Project from GitHub
If you are not familiar with Git or GitHub command line tools, use the ZIP download method.
Open the GitHub page for this project.
Click the green Code button.
Click Download ZIP.
Save the ZIP file to your computer.
Right-click the ZIP file and choose:
```text
Extract All...
```
Extract it somewhere easy to find, such as:
```text
C:\Users\YourName\Documents\clinical-imaging-review-workbench
```
---
Step 3 — Open PowerShell in the Project Folder
Open File Explorer.
Go to the extracted project folder.
Open the folder:
```text
clinical-imaging-review-workbench
```
You should see files like:
`README.md`
`main.py`
`requirements.txt`
the `app` folder
Click the address bar at the top of File Explorer (where the folder path is shown).
Delete whatever text is there.
Type:
```text
powershell
```
Press Enter
A PowerShell window should open in the project folder.
It should look something like:
```text
PS C:\Users\YourName\Documents\clinical-imaging-review-workbench>
```
If you see something like that, you are in the right place.
---
Step 4 — Create a Virtual Environment
A virtual environment is just a private folder that keeps this project’s Python packages separate from everything else on your computer.
You do not need to understand it deeply — just run the command.
In the PowerShell window, run:
```powershell
python -m venv .venv
```
This creates a folder named:
```text
.venv
```
inside the project.
---
Step 5 — Activate the Virtual Environment
In the same PowerShell window, run:
```powershell
.venv\Scripts\Activate.ps1
```
If it works, your prompt should change and start with:
```text
(.venv)
```
Example:
```text
(.venv) PS C:\Users\YourName\Documents\clinical-imaging-review-workbench>
```
If PowerShell blocks the command
Sometimes Windows blocks script execution.
If that happens, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
Then run the activation command again:
```powershell
.venv\Scripts\Activate.ps1
```
---
Step 6 — Install the Required Packages
Now that the virtual environment is active, install the project’s required Python packages.
Run:
```powershell
pip install -r requirements.txt
```
Wait for it to finish.
This installs the GUI framework and any other required libraries.
---
Step 7 — Launch the App
Once installation is done, run:
```powershell
python main.py
```
The application window should open.
What should happen on first launch
On first launch:
the app creates a local SQLite database file
if the database is empty, it automatically loads demo data from:
```text
sample_data/demo_data.json
```
So the app should open with a populated Patient Directory.
That means a reviewer can see a working, pre-populated app immediately.
---
Quick Start (Windows PowerShell)
If you already understand the steps above, these are the exact commands:
```powershell
python --version
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```
---
How to Reopen the App Later
The next time you want to run the app, you do not need to reinstall everything.
Open PowerShell in the project folder again.
Run:
```powershell
.venv\Scripts\Activate.ps1
python main.py
```
If activation is blocked again, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
python main.py
```
---
How to Reset the Demo Data
If you want to restore the app to a fresh demo state:
Close the app.
In the project folder, delete the file:
```text
clinical_imaging_review.db
```
Then run the app again:
```powershell
python main.py
```
Because the database is empty again, the app will re-seed from:
```text
sample_data/demo_data.json
```
---
Troubleshooting (Windows)
Problem: `python --version` says Python is not found
Fix:
Reinstall Python from:
`https://www.python.org/downloads/windows/`
Make sure:
Add Python to PATH is checked
Close and reopen PowerShell
Problem: `.venv\Scripts\Activate.ps1` is blocked
Run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
Then run:
```powershell
.venv\Scripts\Activate.ps1
```
Problem: `pip install -r requirements.txt` fails
Common causes:
internet connection issue
Python not installed correctly
PowerShell not opened in the project folder
Make sure your prompt looks something like:
```text
PS C:\Users\YourName\Documents\clinical-imaging-review-workbench>
```
and that the folder contains:
`requirements.txt`
`main.py`
Problem: The app opens but there is no demo data
Close the app.
Delete:
```text
clinical_imaging_review.db
```
Run again:
```powershell
python main.py
```
The app should reload the demo JSON into a fresh database.
---
Core Features
Patient Management
Load a patient by Patient ID
Automatically create new patients on first load
Browse all patients in a Patient Directory
View:
patient ID
number of scans
latest scan date
Remove selected patient (with confirmation)
Scan Management
View full scan history for the selected patient
Each scan includes:
scan date
accession / study ID
lesion count
total burden (sum of long diameters)
Remove selected scan (with confirmation)
Structured Lesion Entry
Create a new scan for the current patient
Add multiple lesions per scan
Each lesion includes:
lesion label
long-axis endpoints: `(x1, y1, z1)` → `(x2, y2, z2)`
short-axis endpoints: `(x1, y1, z1)` → `(x2, y2, z2)`
computed long diameter
computed short diameter
free-text notes
Supports RECIST-style structured measurements using manually entered endpoints
Historical Review
Historical scans are displayed in read-only mode
Users can review all prior lesions and measurements for longitudinal comparison
Demo Data
App auto-seeds a demo JSON file on first launch if the database is empty
Makes the app immediately usable for GitHub reviewers / recruiters / demo users
---
Tech Stack
Python 3.11+
PySide6 (desktop GUI)
SQLite (local persistence)
JSON (demo data seeding)
---
Project Structure
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
```
---
Architecture Overview
```text
UI (PySide6)
  ├── Patient Directory / Controls
  ├── Scan History
  └── Scan Workspace (new entry or read-only detail)

Services Layer
  ├── create / load patient
  ├── save scan
  ├── load scan history
  ├── load scan detail
  ├── delete scan
  └── delete patient

Data Layer (SQLite)
  ├── patients
  ├── scans
  └── lesions
```
Data Model
```text
Patient
  └── many Scans
        └── many Lesions
```
---
Validation / UX Notes
Current validation includes:
lesion label required
long-axis endpoints cannot be identical
short-axis endpoints cannot be identical
warning for duplicate lesion labels
warning if short diameter exceeds long diameter
