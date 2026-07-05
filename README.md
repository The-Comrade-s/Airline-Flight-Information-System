# SkyWings — Airline Flight Information System

A production-quality, full-stack Airline Flight Information System built with **Python** and **Streamlit**, featuring a modern aviation-inspired interface, role-based authentication, flight and passenger management, a complete booking workflow with digital boarding passes, and professional analytics/reporting.

---

## Features

- **Secure authentication** with bcrypt password hashing, session management, and role-based access (Administrator / Staff)
- **Dashboard** with live statistics (flights, bookings, passengers, revenue) and interactive Plotly charts
- **Flight management**: add, edit, delete, search, and filter flights
- **Passenger management**: register, update, delete, and search passengers
- **End-to-end booking workflow**: search flights → select passenger → choose seat on a visual seat map → confirm → generate a digital boarding pass with QR code and downloadable PDF ticket
- **Reports**: flight, passenger, booking, revenue, daily, and monthly reports, exportable to PDF and CSV
- **Aircraft & Airport management**
- **Staff management** (Administrator only)
- **Settings** with a dark mode toggle
- Realistic seed data: 48 flights, 130 passengers, 170 bookings, 20 airports, 8 aircraft types, 10 airlines

---

## Technology Stack

| Layer            | Technology         |
|-------------------|--------------------|
| Frontend          | Streamlit          |
| Backend           | Python             |
| Database          | SQLite (MySQL-ready schema) |
| ORM               | SQLAlchemy         |
| Charts            | Plotly             |
| Data processing   | Pandas             |
| PDF generation    | ReportLab          |
| QR codes          | qrcode             |
| Password hashing  | bcrypt             |

---

## Project Structure

```
skywings/
├── app.py                     # Main entry point (streamlit run app.py)
├── pages_login.py             # Login screen (rendered pre-authentication)
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml            # Streamlit theme configuration
├── authentication/
│   └── auth.py                # Password hashing, login, session/role guards
├── database/
│   ├── connection.py          # SQLAlchemy engine/session setup
│   ├── init_db.py             # Table creation
│   ├── seed_data.py           # Realistic sample data generator
│   └── queries.py             # Data access layer (all DB queries/mutations)
├── models/
│   ├── user.py
│   ├── airport.py
│   ├── aircraft.py
│   ├── flight.py
│   ├── passenger.py
│   └── booking.py
├── pages/
│   ├── dashboard.py
│   ├── flights.py
│   ├── booking.py              # Booking workflow (search → seat → confirm)
│   ├── passengers.py
│   ├── bookings.py
│   ├── reports.py
│   ├── aircraft.py
│   ├── airports.py
│   ├── staff.py
│   └── settings.py
├── utils/
│   ├── styling.py              # Design system (palette, CSS, cards, badges)
│   ├── navigation.py           # Sidebar navigation
│   ├── charts.py                # Plotly chart builders
│   ├── helpers.py               # Formatting utilities
│   ├── qr_utils.py              # QR code generation
│   ├── pdf_utils.py             # PDF ticket & report generation
│   └── export_utils.py          # CSV export
└── assets/                      # Static assets (logos, images)
```

---

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the application

```bash
streamlit run app.py
```

The database (`skywings.db`) and sample data are created automatically on first launch — no manual setup script needs to be run.

If you ever want to reset the database, simply delete `skywings.db` and restart the app.

### 3. Log in

Two demo accounts are seeded automatically:

| Role           | Username | Password    |
|----------------|----------|-------------|
| Administrator  | `admin`  | `Admin@123` |
| Staff          | `staff`  | `Staff@123` |

**Administrators** can add/edit/delete flights, passengers, aircraft, airports, and manage staff accounts.
**Staff** can search flights, register passengers, and make bookings, but cannot delete records or manage other users.

---

## Migrating to MySQL

The schema was written to be MySQL-compatible from the start. To migrate:

1. Install a MySQL driver: `pip install pymysql`
2. In `database/connection.py`, change:
   ```python
   DATABASE_URL = f"sqlite:///{DB_PATH}"
   ```
   to:
   ```python
   DATABASE_URL = "mysql+pymysql://user:password@host:3306/skywings"
   ```
3. Run the app once — `init_db()` will create all tables in MySQL.
4. Optionally re-run `database/seed_data.py` to populate sample data.

---

## Deployment (Render)

1. Push this project to a GitHub repository.
2. On Render, create a **Web Service** and connect the repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Render will provision a persistent disk if you want the SQLite file to survive restarts; otherwise, consider migrating to a managed MySQL/PostgreSQL database for production use.

---

## Notes for Academic Submission

This project follows a clean, modular architecture: models, database access, authentication, utilities, and pages are all separated into their own modules for readability and maintainability. All database mutations happen through the `database/queries.py` data-access layer rather than directly inside UI code, making the system easier to test, extend, and explain during a viva/defense.
