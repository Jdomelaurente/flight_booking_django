# Flight Booking Simulation Platform (FBS)

A comprehensive Smart Flight Booking Simulation Platform designed for CTHM-CSUCC. This project features a robust Django backend with machine learning capabilities for pricing simulations and a modern Vue.js frontend for a seamless user experience.

## 🚀 Features

- **Flight Management**: Search, book, and manage flight schedules.
- **Dynamic Pricing**: ML-powered flight price prediction using XGBoost.
- **Seat Management**: Real-time seat selection and availability tracking.
- **User Authentication**: Secure login and registration via Djoser.
- **Interactive Dashboards**: Data visualization using Chart.js.
- **Flight Tracking**: Map-based flight visualization using Leaflet.
- **Report Generation**: PDF itinerary and invoice generation using ReportLab.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.2, Django Rest Framework (DRF)
- **Database**: SQLite (Default) / PostgreSQL support
- **ML/Data**: Pandas, NumPy, Scikit-learn, XGBoost
- **Auth**: Djoser, Token-based authentication
- **Reporting**: ReportLab

### Frontend
- **Framework**: Vue 3 (Composition API), Vite
- **State Management**: Pinia
- **Styling**: Tailwind CSS
- **Components**: Axios, Vue Datepicker, Chart.js, Leaflet

---

## 📋 Prerequisites

- **Node.js**: `^20.19.0` or `>=22.12.0`
- **Python**: `3.10` or higher
- **Git**: Installed and configured

---

## 🔧 Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-github-repo-url>
cd fbs-vue
```

### 2. Backend Setup (`fbs_backend`)
Navigate to the backend directory and set up the Python environment.

```bash
cd fbs_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# (Copy .env.example if available, or create manually)

# Run migrations
python manage.py migrate

# (Optional) Seed the database
python populate_data.py

# Start the server
python manage.py runserver
```

### 3. Frontend Setup (`bookingapp`)
Navigate to the frontend directory and install dependencies.

```bash
cd ../bookingapp

# Install dependencies
npm install

# Start dev server
npm run dev
```

---

## 📂 Project Structure

```text
fbs-vue/
├── bookingapp/          # Vue.js Frontend
│   ├── src/             # Frontend source code
│   ├── public/          # Static assets
│   └── package.json     # Frontend dependencies
├── fbs_backend/         # Django Backend
│   ├── fbs_backend/     # Main project settings
│   ├── flightapp/       # Core flight logic
│   ├── app/             # Application logic
│   ├── manage.py        # Django CLI
│   └── requirements.txt # Backend dependencies
└── README.md            # Documentation
```

---

## 🤝 Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
