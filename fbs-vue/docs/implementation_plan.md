# Booking Process Technical Documentation Plan

This plan outlines the creation of professional-grade technical documentation for the flight booking system. The goal is to provide a "panelist-ready" explanation of the system's sophisticated logic, highlighting both frontend state management and backend engineering.

## User Review Required

> [!IMPORTANT]
> The documentation will emphasize technical highlights such as:
> - **ML-Driven Pricing**: Use of Machine Learning for real-time fare prediction.
> - **Dynamic Pricing Engine**: Behavioral and demand-based price adjustments.
> - **Philippine Compliance**: Implementation of 12% VAT and Senior/PWD tax exemptions.
> - **State Management**: Using Pinia as the single source of truth.
> - **Secure Payments**: PayMongo integration with webhook synchronization.
> - **Simulation Grading**: Automated grading for student activities.

## Proposed Changes

### Documentation Content

#### [NEW] [Booking_Process_Documentation.md](file:///C:/Users/user/OneDrive/Desktop/Folders/Fbs/fbs-vue/Booking_Process_Documentation.md)
A comprehensive technical guide including:
- **Architecture Overview**: Decoupled frontend (Vue.js) and backend (Django REST Framework) communication via REST APIs.
- **Frontend State Management**:
    - **Pinia Store**: Centralized booking state (`bookingStore.js`) with persistence.
    - **Multi-Step Wizard**: Navigating through Search -> Passengers -> Add-ons -> Seats -> Review -> Payment.
- **Backend Core Logic**:
    - **Schedule & Search**: ML-predicted base prices and demand-based surges.
    - **Seat Management**: Real-time seat locking with `select_for_update` for concurrency control.
    - **Add-on System**: Segmented baggage, meals, and assistance services.
- **Financial & Regulatory Compliance**:
    - **Taxation**: Philippine 12% VAT logic applied to base fares and add-ons.
    - **Discounts**: 20% Senior Citizen and PWD discounts with VAT-exempt status.
    - **Fees**: Automated inclusion of Passenger Service Charge (DPSC).
- **Payment & Security**:
    - **PayMongo Integration**: Orchestrating Checkout Sessions and verifying payment intents.
    - **Data Integrity**: Server-side verification of transaction amounts.
- **Academic Simulation Features**:
    - **Activity Codes**: Secure validation and section-mapping.
    - **Automated Grading**: Logic that evaluates booking accuracy against activity requirements.

### Visual Architecture (Mermaid Diagrams)
- **Data Flow Diagram**: Student activity -> Booking Store -> Backend API.
- **Lifecycle Sequence**: Detailed flow from flight selection to PNR generation.
- **State Transition**: Booking statuses (Draft -> Pending -> Confirmed).

## Open Questions
- Should I include screenshots of the modern UI components (e.g., the "boarding pass" review page)?
- Should I expand on the ML model's specifics (XGBoost/Predictor) or keep it high-level for technical evaluators?

## Verification Plan

### Manual Verification
- Review the documentation content against `bookingStore.js` and `views.py` to ensure logic accuracy.
- Verify that financial calculations (VAT/Discounts) described match the code precisely.
- Validate that the final Markdown file renders correctly with Mermaid diagrams.





How the Machine Learning (ML) prediction works in your system is one of the "technical heavy hitters" for your capstone project. It doesn't just use static numbers; it mimics real-world airline economics using a two-step process: Predictive Modeling and Dynamic Logic.

Here is the breakdown you can use to explain it to your panelists:

1. The Base Price Prediction (The "Brain")
Our system uses a trained XGBoost (Extreme Gradient Boosting) model. Instead of pulling prices from an external API, the model makes an intelligent prediction based on historical data patterns.

When a user searches for a flight, the system feeds these features into the model:

Temporal Data: Journey day, month, and day of the week (e.g., Friday flights are naturally priced higher than Tuesdays).
Route Complexity: The number of stops, origin, and destination (One-Hot Encoded).
Time & Duration: Exact departure/arrival hours and the total flight duration.
Advace Booking: How many days before the flight the user is searching (advance_booking_days).
python
# Technical Snippet from predictor.py
def predict_price(self, flight_data):
    features_df = self.prepare_features(flight_data)
    # The XGBoost model predicts the base fare based on historical patterns
    predicted_price = self.model.predict(features_df)[0]
    return float(predicted_price)
2. The Dynamic Pricing Engine (The "Economist")
Once the ML model provides a "Base Price," our Dynamic Pricing Engine applies real-time fluctuations to mimic a live airline's supply and demand. It calculates a series of multipliers:

A. Seasonality & Fiestas (get_time_factor)
The system detects peak seasons (like December holidays or October fiestas). If a flight falls in these periods, a "surge" multiplier is applied.

Holiday Surge: Up to +30% for Christmas week flights.
Rush Hour: +12% for flights departing during peak morning/evening slots.
B. Supply & Urgency (get_demand_factor)
Just like real-world airlines, the price increases as the flight date approaches or as more people search for it.

Last Minute: +25% surge if booking less than 3 days before departure.
Occupancy: If the plane is 80% full, the price for the remaining seats increases automatically by 20%.
C. Psychological Rounding
To make the price look professional and "corporate," we apply Psychological Pricing. We force the final calculated amount to end in a "99" (e.g., ₱2,341.50 becomes ₱2,499.00).

Pro-Tip for the Panel:
"Panelist, our system combines Predictive AI with Business Intelligence. The XGBoost model establishes a statistically realistic 'floor price' based on historical data, while our Dynamic Engine simulates the 'urgency' and 'seasonality' of the Philippine travel market, ensuring our simulation is as close to reality as possible."