# ✈️ TourSim: Admin Operations Guide
## Flight & Aviation Management System (FAMS)

Welcome to the **TourSim Admin Operations Guide**. This document outlines the core functional modules of the administrative suite, providing instructions on how to manage the airline’s network, assets, and operational data.

---

## 1. Executive Dashboard (Radar Hub)
The Dashboard provides a real-time snapshot of the entire aviation network.

*   **Planes In-Air**: Reflects the exact number of aircraft currently in flight (Status: *On Flight*). This metric is synchronized across the Live Radar and Schedule Manager.
*   **Open for Booking**: Shows the total number of upcoming flight schedules available for customer purchase (Status: *Open*).
*   **Network Health**: A radar chart visualizing the distribution of flights (Ground, Air, Delayed, Cancelled).
*   **Live Plane List**: A real-time tracking list of aircraft currently broadcasting telemetry.

---

## 2. Universal Bulk Import System
To reduce manual data entry, the system features a robust CSV ingestion pipeline.

### How to Import Data:
1.  Navigate to **Bulk Import**.
2.  Select the **Module** you wish to update (e.g., *Aircraft Fleet*, *Schedules*, *Taxes*).
3.  Upload your CSV file using the standardized templates.
4.  **Error Handling**: If an import contains invalid data (e.g., missing registration numbers or invalid airport codes), the system will generate a **Detailed Failure Report**. Download this report to identify exact rows that failed and the reason for failure.

### Supported Modules:
*   **Fleet**: Aircraft, Seat Classes.
*   **Operations**: Airlines, Airports, Flights, Routes, Schedules.
*   **Ancillaries**: Baggage Options, Meal Catalogs, Taxes & Fees.

---

## 3. Flight Operations Management

### 🛰️ Route & Flight Setup
*   **Routes**: Define the path between two airports (Origin → Destination) including the base price.
*   **Flights**: Bind a specific Flight Number (e.g., *PR101*) to a Route, an Airline, and a specific Aircraft type.

### 📅 Schedule Manager (Planes In-Air)
The Schedule Manager is the heart of the operation. 
*   **Status Lifecycle**: 
    *   `Open`: Visible to students for booking.
    *   `Closed`: Boarding complete; no more tickets can be sold.
    *   `On Flight`: The aircraft is currently in the air.
    *   `Arrived`: Flight completed.
*   **Sync**: All status changes immediately reflect on the **Live Radar Map**.

---

## 4. Asset & Ancillary Management

### 💺 Seat Class Configuration
*   Define different cabins (Economy, Business, First Class).
*   Managed via the **Pricing & Assets** module. 
*   Configurations are used to auto-generate seat maps when creating new flight schedules.

### 🍱 Catalog Management
*   **Meal Catalogs**: Manage available in-flight dining options.
*   **Baggage Options**: Define weight limits and pricing for checked bags.
*   **Booking Taxes**: Set up mandatory fees and taxes applied per passenger.

---

## 5. Security & Authentication
The Admin controls the security protocols for the airline employees and instructors.

*   **Password Resets**: Uses a 6-digit Secure OTP system.
*   **Design**: Reset emails are delivered in a premium HTML format, featuring the TourSim branding and security alerts to ensure a professional user experience.

---

## 🏗️ Technical Architecture
*   **Backend**: Django REST Framework (Port 8000).
*   **Frontend**: Vue.js 3 + Vite (TailwindCSS + Phosphor Icons).
*   **Database**: Atomic PostgreSQL (or standard SQLite for dev) with transaction safety for booking and imports.

---

## 🛠️ Technical Dependencies & Libraries
The TourSim Admin Suite leverages industry-standard libraries to provide a premium, real-time operational experience.

### Frontend (Vue 3 Stack)
*   **Leaflet.js**: Powering the **Live Operations Radar** with interactive MAP mapping and aircraft interpolation.
*   **Chart.js**: Handles all **Data Analytics** and revenue visualization on the Executive Dashboard.
*   **Phosphor Icons**: Provides the high-fidelity, consistent iconography used throughout the Admin UI.
*   **Pinia**: Manage global state, including synchronization of flight metrics across different modules.
*   **Axios**: Secure communication with the Django REST API.
*   **TailwindCSS**: Responsible for the modern, "Airline OPS" aesthetics and responsive layouts.

### Backend (Django Stack)
*   **Django REST Framework**: Provides the secure API endpoints for all admin operations.
*   **XGBoost / Random Forest**: (Integrated for ML Pricing) Used to calculate the baseline fares during flight creation.
*   **Pandas / CSV**: Powers the **Universal Bulk Import System**, handling high-volume data ingestion.
*   **Django-CORS-Headers**: Ensures secure cross-origin resource sharing between the frontend and backend.
*   **ReportLab**: Generates professional PDF manifests and tickets from the admin side.

---
*Last Updated: April 2026*
