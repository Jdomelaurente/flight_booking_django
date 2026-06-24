# Flight Booking Simulation Platform (FBS)

A comprehensive **Smart Flight Booking Simulation Platform** designed for **CTHM-CSUCC** (College of Tourism and Hospitality Management). This interactive training tool simulates a real-world airline booking system where students search flights, book tickets, select seats, and check in — all as part of graded academic activities.

---

## Features

### Booking & Check-In
- Flight search with multi-step booking wizard (Search → Passengers → Add-ons → Seats → Review → Payment)
- Interactive seat maps with real-time availability
- Add-on selection: insurance, meals, baggage, assistance services
- PDF itinerary/receipt and QR-coded boarding pass generation
- DCS (Departure Control System) check-in simulation

### Student Portal
- View assigned activities and enter activity codes
- Complete booking missions with specific requirements (route, class, passengers, dates)
- View grades and assessment analysis
- Booking and check-in registries

### Instructor Portal
- Create sections and enroll students
- Create graded activities with custom requirements
- Generate unique activity codes for students
- Auto-grade student bookings against activity requirements
- Review scores and generate reports

### Admin Panel
- Executive dashboard with live radar, stats, and network health
- Flight operations: routes, flights, schedules, seat management
- Asset management: airlines, aircraft, airports, seat classes
- Add-on catalog: meals, baggage, assistance, insurance
- Tax & fee management (Philippine VAT, airport fees, travel tax)
- Student/instructor management with audit logs
- Bulk CSV import for fleet, operations, and ancillaries
- Dynamic pricing configuration

### Machine Learning Pricing
- XGBoost model trained on historical flight data for base fare prediction
- Dynamic pricing engine with multipliers: demand, time, occupancy, loyalty, randomization
- Psychological price rounding

---

## Tech Stack

### Backend
| Technology | Version |
|---|---|
| Django | 6.0 |
| Django REST Framework | 3.16.1 |
| PostgreSQL | 16 |
| XGBoost / scikit-learn | 3.1.3 / 1.6.1 |
| Djoser (auth) | 2.3.3 |
| ReportLab (PDF) | 4.4.9 |
| PayMongo (payment) | — |

### Frontend
| Technology | Version |
|---|---|
| Vue 3 (Composition API) | ^3.5.26 |
| Vite | ^7.3.0 |
| Pinia | ^3.0.4 |
| Tailwind CSS | ^4.1.18 |
| Axios | ^1.13.2 |
| Chart.js | ^4.5.1 |
| Leaflet | ^1.9.4 |

---

## Project Structure

```
Fbs/
├── fbs-vue/                          # Main project
│   ├── fbs_backend/                  # Django backend
│   │   ├── fbs_backend/              # Project settings, root URLs
│   │   ├── app/                      # Core app: airports, airlines, routes, countries
│   │   ├── flightapp/                # Flight booking, ML pricing, payments, PDF, email
│   │   ├── fbs_instructor/           # Sections, activities, grading
│   │   ├── manage.py
│   │   ├── populate_data.py          # Database seeding
│   │   └── .env                      # Environment variables
│   │
│   ├── bookingapp/                   # Vue 3 frontend
│   │   ├── src/
│   │   │   ├── views/                # Page components
│   │   │   │   ├── booking/          # Booking flow pages
│   │   │   │   ├── Student/          # Student dashboard, activities
│   │   │   │   ├── Instructor/       # Instructor dashboard, grading
│   │   │   │   ├── admin/            # Admin panels
│   │   │   │   └── dcs/              # Check-in system
│   │   │   ├── components/           # Reusable components
│   │   │   ├── stores/               # Pinia state management
│   │   │   ├── router/               # Vue Router config
│   │   │   └── services/             # API service layer
│   │   ├── package.json
│   │   └── vite.config.js
│   │
│   └── docs/                         # Documentation
│
├── requirements.txt
└── .venv/
```

---

## Setup

### Prerequisites
- **Python** 3.10+
- **Node.js** ^20.19.0 or >=22.12.0
- **PostgreSQL** (or SQLite for dev)
- **Git**

### Backend

```bash
cd fbs-vue/fbs_backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set up database
python manage.py migrate

# (Optional) Seed demo data
python populate_data.py

# Create admin user
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Frontend

```bash
cd fbs-vue/bookingapp
npm install
npm run dev
```

The app runs at **http://localhost:5173/** (frontend) and **http://localhost:8000/** (API).

---

## Environment Variables

### Backend (`fbs-vue/fbs_backend/.env`)
| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Debug mode (True/False) |
| `FRONTEND_URL` | Frontend URL for CORS/redirects |
| `CORS_ALLOWED_ORIGINS` | Comma-separated allowed origins |
| `EMAIL_HOST_USER` | SMTP email username |
| `EMAIL_HOST_PASSWORD` | SMTP email app password |
| `PAYMONGO_SECRET_KEY` | PayMongo secret API key |
| `PAYMONGO_PUBLIC_KEY` | PayMongo public API key |

### Frontend (`fbs-vue/bookingapp/.env`)
| Variable | Description |
|---|---|
| `VITE_API_URL` | Backend API base URL |
