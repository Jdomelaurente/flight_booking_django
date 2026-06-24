# Flight Booking System (FBS-Vue)

A comprehensive flight booking system with a Vue 3 frontend and Django REST API backend. Features ML-based dynamic pricing, student activity grading for instructors, and full booking workflow.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Data Models](#data-models)
5. [API Endpoints](#api-endpoints)
6. [Key Features](#key-features)
7. [Frontend Components](#frontend-components)
8. [ML Pricing System](#ml-pricing-system)
9. [Payment Integration](#payment-integration)
10. [Instructor Grading System](#instructor-grading-system)
11. [Setup & Installation](#setup--installation)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Vue 3 Frontend                         │
│  (bookingapp/)                                              │
│  ├── Views: Booking, Student, Instructor, Profile           │
│  ├── Components: Flight Search, Seat Selection, Forms       │
│  └── State: Pinia stores                                    │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API (Axios)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Django REST Backend                       │
│  (fbs_backend/)                                            │
│  ├── flightapp: Flights, Bookings, ML Pricing              │
│  ├── fbs_instructor: Sections, Activities, Grading          │
│  └── app: Users, Core Models                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Frontend
- **Vue 3** - Progressive JavaScript framework
- **Vite** - Next-generation build tool
- **Vue Router** - Client-side routing
- **Pinia** - Intuitive state management
- **TailwindCSS** - Utility-first CSS framework
- **Axios** - HTTP client

### Backend
- **Django 5.x** - Python web framework
- **Django REST Framework** - RESTful API
- **Python 3.13** - Runtime
- **XGBoost/Random Forest** - ML pricing models

---

## Project Structure

```
fbs-vue/
├── bookingapp/                    # Vue 3 Frontend
│   ├── src/
│   │   ├── views/                 # Page components
│   │   │   ├── booking/           # Booking flow pages
│   │   │   ├── Student/           # Student dashboard
│   │   │   ├── Instructor/       # Instructor dashboard
│   │   │   └── Profile/          # User profile
│   │   ├── components/           # Reusable components
│   │   │   ├── booking/          # Booking components
│   │   │   ├── Student/          # Student components
│   │   │   └── common/           # Shared components
│   │   ├── stores/                # Pinia stores
│   │   └── router/                # Vue Router config
│   └── package.json
│
├── fbs_backend/                   # Django Backend
│   ├── fbs_backend/              # Django project settings
│   ├── flightapp/                # Main booking app
│   │   ├── views.py              # API views
│   │   ├── models.py             # Booking models
│   │   ├── serializers.py        # DRF serializers
│   │   ├── urls.py                # URL routing
│   │   ├── ml/                   # ML Pricing
│   │   │   ├── predictor.py       # Price prediction
│   │   │   └── dynamic_pricing.py # Dynamic pricing service
│   │   └── services/             # Business logic
│   │       ├── paymongo_service.py
│   │       ├── email_service.py
│   │       ├── pdf_service.py
│   │       └── grading_service.py
│   ├── fbs_instructor/           # Instructor app
│   │   ├── views.py
│   │   ├── models.py
│   │   └── urls.py
│   └── app/                      # Core app
│       ├── models.py             # Core models (Airports, etc.)
│       └── views.py
│
├── requirements.txt
└── README.md
```

---

## Data Models

### Core Models (`app/models.py`)

#### User & Authentication
- **UserProfile** - Extended user with roles (student/instructor/admin)
- **UserSession** - Custom session management with tokens

#### Student Management
- **Students** - Student records linked to User model

#### Flight Data
- **Country** - Countries with currency info
- **Airline** - Airlines with IATA codes
- **Aircraft** - Aircraft models with capacity
- **Airport** - Airports (domestic/international)
- **Route** - Origin-destination pairs with base pricing
- **Flight** - Flight number + airline + route
- **Schedule** - Flight schedules with times and status
- **SeatClass** - Cabin classes (Economy, Business, etc.)
- **Seat** - Individual seats with features (window, aisle, exit row)

#### Booking
- **Booking** - Main booking with PNR, status, totals
- **BookingDetail** - Per-passenger booking info
- **PassengerInfo** - Passenger details
- **BookingContact** - Contact information
- **AddOn** - Add-ons (insurance, meals, baggage)

#### Add-ons & Services
- **MealOption** - In-flight meals with dietary info
- **BaggageOption** - Extra baggage options
- **AssistanceService** - Special assistance (wheelchair, etc.)

#### Insurance System
- **InsuranceProvider** - Insurance companies
- **TravelInsurancePlan** - Insurance plans
- **InsuranceBenefit** - Plan benefits
- **InsuranceCoverageType** - Coverage types
- **PlanCoverage** - Coverage amounts per plan
- **BookingInsuranceRecord** - Purchased insurance records

### Instructor Models (`fbs_instructor/models.py`)

- **Instructor** - Instructor profiles
- **Section** - Class sections
- **SectionEnrollment** - Student enrollments
- **Activity** - Graded activities with requirements
- **ActivityPassenger** - Required passenger details
- **ActivityAddOn** - Required add-ons for grading
- **ActivityStudentBinding** - Activity-student assignments

---

## API Endpoints

### Flight Data (Read-only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/airports/` | List all airports |
| GET | `/api/airports/{id}/` | Get airport details |
| GET | `/api/airlines/` | List all airlines |
| GET | `/api/routes/` | List all routes |
| GET | `/api/schedules/` | Search flights |

### Schedule Search Parameters
```
/api/schedules/?origin=MNL&destination=CEB&departure=2024-12-25
```

### Booking
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/bookings/` | List user's bookings |
| POST | `/api/bookings/` | Create new booking |
| GET | `/api/bookings/{id}/` | Get booking details |
| PUT | `/api/bookings/{id}/` | Update booking |

### Payment
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/payment/create-intent/` | Create payment intent |
| POST | `/api/payment/verify/` | Verify payment |

### Instructor
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/instructor/sections/` | List instructor sections |
| POST | `/api/instructor/sections/` | Create section |
| POST | `/api/instructor/activities/` | Create activity |
| POST | `/api/instructor/activities/{id}/generate-code/` | Generate activity code |
| POST | `/api/instructor/activities/{id}/grade/` | Grade student booking |

### Insurance
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/insurance/plans/` | List insurance plans |
| GET | `/api/insurance/providers/` | List providers |

---

## Key Features

### 1. Flight Search & Booking Flow
1. **Search** - Origin, destination, date, passengers
2. **Results** - Filterable flight list with pricing
3. **Seat Selection** - Interactive seat map
4. **Passenger Details** - Passenger information forms
5. **Add-ons** - Insurance, meals, baggage selection
6. **Review** - Booking summary
7. **Payment** - PayMongo integration
8. **Confirmation** - Email + PDF ticket

### 2. ML-Based Dynamic Pricing

The pricing system uses multiple factors:

```python
# Price Factors
final_price = base_ml_price × user_factor × session_factor × demand_factor × time_factor × inventory_factor × randomization
```

**ML Model (XGBoost/Random Forest)**
- Input: Flight data, dates, route info
- Output: Base predicted price

**Dynamic Factors:**
- **User Factor** - New users get higher prices, loyal customers get discounts
- **Session Factor** - Repeated searches increase price
- **Demand Factor** - High search volume increases price
- **Time Factor** - Peak hours/weekends/holidays increase price
- **Inventory Factor** - High occupancy increases price
- **Randomization** - Prevents price matching

### 3. Student Activity System

Instructors create graded activities:

```python
Activity:
  - title, description, instructions
  - required_trip_type (one_way/round_trip/multi_city)
  - required_origin, required_destination
  - required_departure_date, required_return_date
  - required_travel_class
  - required_passengers, children, infants
  - total_points, due_date
  - activity_code (generated 8-char code)
```

Students enter the activity code during booking. The system:
1. Validates the booking matches requirements
2. Calculates a grade based on add-ons purchased
3. Links the booking to the activity for instructor review

### 4. Insurance Integration

- Multiple insurance providers
- Different plan tiers (Basic, Standard, Premium, Comprehensive)
- Coverage types: Medical, Baggage, Cancellation
- Automatic policy number generation
- Coverage period tracking

---

## Frontend Components

### Booking Flow
| Component | Description |
|-----------|-------------|
| `HomeView.vue` | Landing page with flight search |
| `SearchResultsView.vue` | Flight results with filters |
| `SeatSelectionView.vue` | Interactive seat map |
| `PassengerDetailsView.vue` | Passenger forms |
| `AddonsView.vue` | Insurance, meals, baggage |
| `ReviewBookingView.vue` | Booking summary |
| `PaymentView.vue` | Payment processing |
| `BookingSuccessView.vue` | Confirmation page |

### Student Dashboard
| Component | Description |
|-----------|-------------|
| `Student_dashboard.vue` | Main student dashboard |
| `ActivityCard.vue` | Activity display card |
| `UpcomingDeadlines.vue` | Due date reminders |

### Instructor Dashboard
| Component | Description |
|-----------|-------------|
| `instructor_dashboard.vue` | Main instructor dashboard |
| `Section_details.vue` | Section management |
| `Activity_details.vue` | Activity creation/editing |

### Common Components
| Component | Description |
|-----------|-------------|
| `FlightSearch.vue` | Flight search form |
| `FlightCard.vue` | Flight result card |
| `FlightFilterSidebar.vue` | Search filters |
| `BookingTimer.vue` | Payment countdown |
| `Header.vue` | Navigation header |

---

## ML Pricing System

### Files
- `flightapp/ml/predictor.py` - ML model wrapper
- `flightapp/ml/dynamic_pricing.py` - Dynamic pricing service

### Model Loading
```python
from flightapp.ml.predictor import predictor

# Load model on startup
predictor.load_model()

# Predict price
price = predictor.predict_price(flight_data)
```

### Pricing Configuration

The system can be configured via Django admin with settings for:
- User factors (new, returning, loyal)
- Demand thresholds
- Time-based factors (peak hours, weekends, holidays)
- Inventory thresholds
- Randomization ranges

---

## Payment Integration

### PayMongo Service (`flightapp/services/paymongo_service.py`)

```python
from flightapp.services.paymongo_service import paymongo_service

# Create payment intent
intent = paymongo_service.create_paymentIntent(amount, currency)

# Verify payment
result = paymongo_service.verify_payment(payment_id)
```

### Payment Flow
1. Create payment intent on backend
2. Send client secret to frontend
3. Frontend completes payment via PayMongo
4. Webhook callback verifies payment
5. Booking status updated to confirmed

---

## Instructor Grading System

### Activity Code Workflow
1. Instructor creates activity with requirements
2. Instructor generates unique activity code
3. Student enters code during booking
4. System validates booking meets requirements
5. Auto-calculates grade based on add-ons
6. Instructor reviews and can adjust grade

### Grading Service (`flightapp/services/grading_service.py`)
```python
from flightapp.services.grading_service import grade_booking

# Grade a booking against an activity
result = grade_booking(booking, activity)
```

---

## Setup & Installation

### Backend Setup
```bash
cd fbs_backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Frontend Setup
```bash
cd bookingapp

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Environment Variables

Create `.env` file in `fbs_backend/`:
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
PAYMONGO_SECRET_KEY=your-paymongo-key
```

---

## Development Notes

### Running ML Price Updates
```bash
# Update ML prices for all schedules
python manage.py update_ml_prices
```

### Seeding Data
```bash
# Populate initial data
python populate_data.py
```

### Testing Grading
```bash
# Test grading functionality
python scripts/verify_grading.py
```

---


---

## Supplementary Documentation
- 📘 **[Admin Operations Guide](file:///c:/Users/user/OneDrive/Desktop/Folders/Fbs/fbs-vue/docs/ADMIN_GUIDE.md)** - Guide for managing flights, assets, and imports.
- 🔄 **[System Workflow](file:///c:/Users/user/OneDrive/Desktop/Folders/Fbs/fbs-vue/docs/workflow.md)** - Operational flow diagrams and lifecycle.
- 📋 **[Booking Process](file:///c:/Users/user/OneDrive/Desktop/Folders/Fbs/fbs-vue/docs/Booking%20Process%20Documentation)** - Detailed step-by-step booking logic.

