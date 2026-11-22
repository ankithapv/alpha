# Borrow Board — Python Full-Stack Project

A responsive equipment lending and return tracking prototype for ALPHA Lab, NIE Mysuru.

## Technology

- Frontend: HTML, CSS, vanilla JavaScript
- Backend: Python 3.12 + Flask REST API
- Persistent database: **Google Sheets only** (required by the TECH-01 brief)
- Container: Docker / Docker Compose
- CI/CD: GitHub Actions builds and validates the app, then publishes a Docker image to GHCR on pushes to `main`.

## Project layout

```text
borrow-board-python/
├── app/
│   ├── __init__.py
│   ├── routes.py                 # Backend API routes and business rules
│   ├── sheets.py                 # Google Sheets database adapter + data mapping
│   ├── templates/index.html      # Frontend page
│   └── static/
│       ├── css/style.css         # UI design
│       └── js/app.js             # Frontend behaviour/API calls
├── credentials/                  # Put service-account.json here (do not commit)
├── data/                          # Place your dataset copy / CSV prep files here
├── .github/workflows/ci-cd.yml
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── run.py
```

## 1. Run locally in VS Code (demo mode)

1. Install Python 3.12+ and Git.
2. Extract this folder and open it in VS Code.
3. Open Terminal in VS Code.
4. Create and activate a virtual environment:

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

5. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
6. Copy `.env.example` to `.env`. Keep `DEMO_MODE=true` for the first run.
7. Start the server:
   ```bash
   python run.py
   ```
8. Open http://127.0.0.1:5000

Demo mode is only for UI and workflow testing. It uses temporary in-memory sample rows and resets when the server restarts. It is not a persistent database.

## 2. Connect your actual Google Sheets dataset

The instructor's requirement says Google Sheets must be the only database. The app's real-data mode uses Google Sheets; it does not use SQLite, Firebase or SQL.

### A. Create / prepare the Google Sheet

1. Upload `ALPHA_BorrowBoard_Dataset_Template.xlsx` to Google Drive and open it as a Google Sheet, or create a new Google Sheet.
2. Keep these worksheet names exactly:
   - `Inventory`
   - `Users`
   - `Borrow_Transactions`
   - `Reservations`
   - `Damage_Reports`
   - `Rules_Config`
   - `Research_Requirements`
3. Row 1 in each worksheet must contain the exact column names below. Keep the spelling and underscores unchanged.
4. Replace sample rows with verified information from your team. Do not add real phone numbers or sensitive information unless the lab has approved collecting it.

### B. Dataset update area — where you add your data

**You normally update data in Google Sheets, not in Python code.** The backend reads the rows from those tabs each time it handles an operation.

- Add / edit equipment in the `Inventory` tab.
- Add approved students / staff in the `Users` tab.
- Checkout and return history is appended to `Borrow_Transactions` automatically.
- Reservation requests are appended to `Reservations` automatically.
- Damage reports can be recorded in `Damage_Reports` when the inspection workflow is extended.
- Policy values belong in `Rules_Config`.

The mapping and header definitions are in **`app/sheets.py` → `SHEET_HEADERS`**. If you receive a dataset with different column names, update that mapping and the relevant field names in `app/routes.py`.

### C. Expected sheet headers

Copy these as row 1 (one column per field).

**Inventory**
```text
Item_ID, Item_Name, Category, Tracking_Method, Total_Quantity, Available_Quantity, Borrowed_Quantity, Condition, Location, Specifications, Compatibility_Notes, Item_Status, Last_Verified, Remarks
```

**Users**
```text
User_ID, Full_Name, USN_or_Staff_ID, Email, Role, Department, Account_Status, Block_Reason, Outstanding_Fine
```

**Borrow_Transactions**
```text
Transaction_ID, User_ID, Item_ID, Quantity, Issue_Date, Due_Date, Return_Date, Return_Condition, Inspection_Notes, Issued_By, Received_By, Transaction_Status, Overdue_Flag, Fine_Status, Fine_Amount, Purpose, Request_Reason, Remarks
```

**Reservations**
```text
Reservation_ID, User_ID, Item_ID, Quantity, Request_Date, Expected_Availability_Date, Approved_By, Reservation_Status, Priority_Number, Notification_Status, Purpose, Booking_Notes, Remarks
```

**Damage_Reports**
```text
Damage_Report_ID, Transaction_ID, Item_ID, Issue_Type, Reported_At, Condition_On_Return, Inspection_Status, Description, Photo_Link, Resolution_Status, Reported_By, Reviewed_By, Fine_Decision, Fine_Amount, Remarks
```

**Rules_Config**
```text
Rule_ID, Setting_Name, Setting_Value, Unit, Description, Updated_By, Updated_At, Remarks
```

**Research_Requirements**
```text
Requirement_ID, Type, Source_Role_or_Name, User_Quote_or_Observation, Need_Identified, Proposed_Design_Response, Priority, Status, Owner, Evidence_Link, Remarks
```

### D. Google API setup

1. In Google Cloud Console, create a project and enable **Google Sheets API**.
2. Create a service account and generate a JSON key.
3. Save the key as `credentials/service-account.json` in this project.
4. Open the JSON and copy the `client_email` value.
5. Share your Google Sheet with that service-account email as an **Editor**.
6. Copy the spreadsheet ID from the Google Sheet URL:
   `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
7. In `.env`, set:
   ```env
   DEMO_MODE=false
   GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
   GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service-account.json
   ADMIN_API_KEY=choose-a-long-secret
   SECRET_KEY=choose-a-long-random-secret
   ```
8. Restart the server.

Never upload `.env` or `credentials/service-account.json` to GitHub. `.gitignore` already excludes them.

## 3. Main workflows

- **Checkout:** enter a student/staff ID, choose equipment, purpose and due date. The backend checks the Users tab, account status, outstanding fine and available quantity before writing a transaction and adjusting inventory.
- **Return:** enter the transaction ID and condition. A good return restores available quantity. Damaged, incomplete or non-working returns are marked for inspection and are not automatically made available.
- **Reservation:** if equipment is unavailable, submit a request. Requests are assigned a simple increasing queue number.
- **Admin inspection API:** after inspection, an administrator can mark an item functional, under repair or retired.

Prototype note: the current UI provides the core checkout, return and reservation journeys. Admin inspection and adding inventory are backend endpoints intended for an authenticated admin screen in the next iteration. The admin API key is a prototype safeguard, not production-grade role-based authentication.

## 4. API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/bootstrap` | Dashboard, inventory and records |
| POST | `/api/borrow` | Issue equipment |
| POST | `/api/return` | Record return condition |
| POST | `/api/reservations` | Add reservation |
| POST | `/api/admin/items` | Add inventory item (admin key) |
| POST | `/api/admin/inspect` | Complete item inspection (admin key) |

For admin POST requests, send header `X-Admin-Key: <ADMIN_API_KEY>`.

## 5. Docker

Create `.env` and add the Google credentials file first (or keep demo mode on).

```bash
docker compose up --build
```

Open http://localhost:5000

Stop:
```bash
docker compose down
```

## 6. Git and GitHub CI/CD

Create a new empty GitHub repository, then from the project folder:

```bash
git init
git add .
git commit -m "Initial Borrow Board Python application"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

The workflow in `.github/workflows/ci-cd.yml` runs on pull requests and pushes to `main`:
1. Installs Python dependencies.
2. Compiles Python source files.
3. Builds the Docker image.
4. On a push to `main`, publishes `ghcr.io/YOUR-USERNAME/borrow-board:latest` to GitHub Container Registry.

In GitHub repository settings, make sure Actions are enabled and the workflow has package write permission (the workflow requests it). The image publication is the CI/CD delivery step. It does not automatically deploy to a hosting provider; to deploy publicly, connect GHCR to a hosting service or add that provider's deployment step and secrets.

## 7. Important prototype limitations / next steps

- The provided student list is a sample. The app does not connect to NIE's official identity system. Add only authorized college records to `Users`.
- Browser-based automatic reminders, email/SMS notifications, photo uploads and automated fine collection are not implemented yet. The current dashboard highlights overdue records; reminders can be added after choosing an approved notification channel.
- Fine amounts are not automatically charged. Lab staff should inspect returns and approve any fine policy before applying it.
- The app uses a simple USN/staff-ID lookup for the prototype, not secure user login. Before public deployment, add proper authentication, authorization, CSRF protection, input validation, audit logging and HTTPS.
- Google Sheets has API quotas and is suitable for this prototype scale; avoid simultaneous conflicting edits to the same stock row.

## 8. Presentation checklist

- Demonstrate a student with an active account checking out an available component.
- Show inventory quantity decreasing.
- Show the transaction and due date.
- Record a good return and show stock increase.
- Record a damaged return and show it remains unavailable for inspection.
- Show a reservation request and the queue number.
- Explain that the Google Sheet is readable by lab staff and is the only persistent database.
