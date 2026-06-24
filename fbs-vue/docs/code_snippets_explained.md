# FBS — Most Relevant Code Snippets: Student Side & Booking Process

---

## 🎓 STUDENT SIDE

---

### 1. `filteredActivities` — Activity Tab Filter Logic
**File:** `bookingapp/src/views/Student/Student_dashboard.vue` (Lines 496–508)

```js
filteredActivities() {
  let filtered = this.activities;
  if (this.activeTab === 'active') {
    filtered = filtered.filter(a =>
      a.is_active && !['submitted', 'graded', 'unassigned'].includes(a.status) && !this.checkIsOverdue(a)
    );
  } else if (this.activeTab === 'missing') {
    filtered = filtered.filter(a => this.checkIsOverdue(a) || a.status === 'unassigned');
  } else if (this.activeTab === 'submitted') {
    filtered = filtered.filter(a => a.status === 'submitted');
  } else if (this.activeTab === 'graded') {
    filtered = filtered.filter(a => a.status === 'graded');
  }
  return filtered;
}
```

**Explanation 1 — Multi-Status Awareness:**
This computed property doesn't just split by a single status field. It combines three independent checks — `is_active` (boolean flag), `status` string, and the `checkIsOverdue()` time comparison — so that an activity can land in the correct tab even if its status hasn't been manually updated by the instructor yet.

**Explanation 2 — "Missing" Tab as a Safety Net:**
The `missing` tab catches two scenarios: activities that are *past due* (overdue) AND activities that are *unassigned* (instructor never assigned them). This prevents activities from silently disappearing into a "none of the above" void.

**Explanation 3 — Computed, Not Fetched:**
Because this is a Vue `computed` property, it re-runs reactively whenever `activeTab` or `activities` changes. There's no extra API call — all filtering happens on already-fetched data in memory, keeping the UI snappy.

---

### 2. `checkIsOverdue()` — Deadline Enforcement Logic
**File:** `bookingapp/src/views/Student/Student_dashboard.vue` (Lines 567–575)

```js
checkIsOverdue(activity) {
  if (!activity.due_date) return false;
  const now = new Date();
  const dueDate = new Date(activity.due_date);
  if (typeof activity.due_date === 'string' && activity.due_date.length <= 10) {
    dueDate.setHours(23, 59, 59, 999);
  }
  return now > dueDate && !activity.completed && activity.status !== 'submitted' && activity.status !== 'graded';
}
```

**Explanation 1 — Date-Only String Handling:**
Django's API may return a date like `"2026-04-15"` (no time). Without the `setHours(23,59,59,999)` fix, JavaScript would parse that as midnight UTC — making it appear overdue hours before it actually is for Philippine users (UTC+8). This line treats date-only strings as end-of-day.

**Explanation 2 — Respecting Terminal States:**
An activity marked `submitted` or `graded` can never become overdue from the student's perspective, even if the date has passed. The function returns `false` for those, so a graded activity doesn't re-appear in the "Missing" tab.

**Explanation 3 — Guard Clause First:**
The `if (!activity.due_date) return false` guard at the top means unlimited activities (those without a deadline) are never flagged as overdue. This is the correct academic behavior — no deadline, no penalty.

---

### 3. `startPracticeBooking()` — Launching Practice Mode
**File:** `bookingapp/src/views/Student/Student_dashboard.vue` (Lines 532–537)

```js
startPracticeBooking() {
  this.bookingStore.resetBooking();
  this.bookingStore.setPracticeMode();
  this.notificationStore.success('Practice mode enabled. Happy booking!');
  this.$router.push('/');
},
```

**Explanation 1 — Clean Slate Before Practice:**
`resetBooking()` is called first, ensuring any leftover state from a previous session (flights selected, passengers filled in, etc.) is fully cleared before the student enters practice mode. This prevents data contamination between graded and practice bookings.

**Explanation 2 — Practice vs. Graded Mode Separation:**
`setPracticeMode()` sets `isPractice = true` and `hasActivityCodeValidation = true` in the Pinia store. This flag propagates throughout the entire booking flow — the backend checks `is_practice` during booking creation to skip grading and avoid affecting the student's official submission record.

**Explanation 3 — Immediate Redirect:**
After setting the store flags, the student is immediately redirected to `/` (the booking home page). This design means the student doesn't have to navigate manually — one click in the dashboard launches the full simulation directly.

---

### 4. `openComparisonModal()` — Comparing Student Booking to Activity Requirements
**File:** `bookingapp/src/views/Student/Student_dashboard.vue` (Lines 538–557)

```js
async openComparisonModal(activity) {
  this.showComparison = true;
  this.comparisonActivity = activity;
  this.comparisonBooking = null;
  this.isLoadingBooking = true;
  this.comparisonError = null;

  try {
    const data = await comparisonService.getComparisonData(activity.id, activity.confirmed_booking_id);
    if (data.success) {
      if (data.activity) this.comparisonActivity = data.activity;
      this.comparisonBooking = data.booking;
    } else {
      this.comparisonError = data.error || "Could not find booking data.";
    }
  } catch (error) {
    this.comparisonError = "Failed to connect to the server.";
  } finally {
    this.isLoadingBooking = false;
  }
}
```

**Explanation 1 — Optimistic UI Opening:**
The modal is shown (`showComparison = true`) *before* the API call completes. The UI immediately shows a loading state, giving the student visual feedback instantly instead of waiting for the network. This is the "optimistic UI" pattern.

**Explanation 2 — Dual Data Source:**
Both `activity.id` and `activity.confirmed_booking_id` are sent to the `comparisonService`. This allows the backend to fetch both the original activity requirements AND the student's actual booking record in a single call, then match them side-by-side for scoring insight.

**Explanation 3 — Graceful Error Handling:**
Three distinct error states are handled: API success-but-not-found (`data.error`), network failure (`catch` block), and loading (`isLoadingBooking`). The `finally` block ensures `isLoadingBooking` is always reset even if the API throws an exception, preventing a permanent spinner.

---

### 5. `upcomingDeadlines` — Computed Deadline Sidebar
**File:** `bookingapp/src/views/Student/Student_dashboard.vue` (Lines 509–514)

```js
upcomingDeadlines() {
  return this.activities
    .filter(a => a.due_date && a.is_active && !a.completed && !['submitted', 'graded'].includes(a.status))
    .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
    .slice(0, 5);
}
```

**Explanation 1 — Chained Functional Pipeline:**
This is a clean, readable functional pipeline: filter → sort → slice. Each step narrows the data further. The filtering removes completed/submitted activities, sorting orders by urgency (soonest first), and slicing caps the sidebar at 5 items to avoid overflow.

**Explanation 2 — Date Comparison via Subtraction:**
`new Date(a.due_date) - new Date(b.due_date)` works because JavaScript coerces Date objects to their millisecond timestamp when used in arithmetic. Negative results mean `a` comes before `b`, which is exactly what `Array.sort` expects for ascending order.

**Explanation 3 — Never Shows Terminal Activities:**
Activities already `submitted` or `graded` are excluded. This means the deadline sidebar only shows actionable, pending items — the student isn't reminded about work already done, which keeps the dashboard clean and goal-focused.

---

---

## ✈️ BOOKING PROCESS

---

### 6. `useBookingStore` — Central Booking State Machine
**File:** `bookingapp/src/stores/booking.js` (Lines 6–79)

```js
export const useBookingStore = defineStore('booking', {
  state: () => ({
    booking_id: localStorage.getItem('current_booking_id') || null,
    selectedOutbound: null,
    selectedReturn: null,
    tripType: 'one_way',
    multiCitySegments: [],
    passengerCount: { adults: 1, children: 0, infants: 0 },
    passengers: [],
    contactInfo: { title:'', firstName:'', lastName:'', email:'', phone:'' },
    addons: { baggage:{}, meals:{}, wheelchair:{}, seats:{}, insurance:{} },
    activityCode: null,
    isPractice: false,
    sessionExpiry: null,
    // ...
  }),
  persist: { key: 'booking-store', storage: localStorage },
```

**Explanation 1 — Single Source of Truth for the Entire Flow:**
Every step of the booking (flight selection → passengers → addons → payment) reads from and writes to this single Pinia store. This eliminates the need to pass data via URL params or Vue props across 8+ route transitions, making the data flow robust and debuggable.

**Explanation 2 — LocalStorage Persistence:**
The `persist` configuration means the entire booking state survives page refreshes. If a student accidentally closes the tab mid-booking, they return to exactly where they left off. The `booking-store` key in localStorage is what the app checks on mount.

**Explanation 3 — Activity Code vs. Practice Mode as Independent Flags:**
`activityCode`, `isPractice`, and `hasActivityCodeValidation` are kept as separate state properties rather than a single "mode" string. This allows nuanced behavior — e.g., showing the timer only for real activity sessions, skipping grading for practice, and allowing the comparison modal only for confirmed graded bookings.

---

### 7. `grandTotal` & `authoritativeTotal` — Price Calculation Priority Chain
**File:** `bookingapp/src/stores/booking.js` (Lines 350–438)

```js
grandTotal(state) {
  const bPrice = parseFloat(this.combinedBasePriceTotal) || 0;
  const aPrice = parseFloat(this.totalAddonsPrice) || 0;
  const iPrice = parseFloat(this.insurancePrice) || 0;
  const tPrice = parseFloat(this.totalTaxes) || 0;
  const rawTotal = bPrice + aPrice + iPrice + tPrice;
  return Math.ceil(rawTotal);  // Always round UP
},

authoritativeTotal(state) {
  if (state.booking_total > 0) return state.booking_total;           // Priority 1: Confirmed backend total
  if (state.backendBreakdown?.total_amount !== undefined)
    return parseFloat(state.backendBreakdown.total_amount);           // Priority 2: Backend estimate
  // Priority 3: Frontend estimate fallback
  return Math.ceil(baseTotal + addonsTotal + insuranceTotal + taxesTotal);
}
```

**Explanation 1 — Three-Level Price Trust Hierarchy:**
`authoritativeTotal` operates on a priority chain: (1) the final server-confirmed `booking_total` after payment, (2) the backend's pre-payment estimate from `/calculate-price/`, and (3) the frontend's own calculation as a last resort. This prevents the user from ever seeing ₱0.00 even before the backend responds.

**Explanation 2 — `Math.ceil()` for Currency Safety:**
Rounding UP instead of the typical rounding ensures the system never under-charges due to floating-point imprecision. For example, ₱1,500.001 becomes ₱1,501 rather than ₱1,500. This is a common financial safety practice.

**Explanation 3 — VAT-Exempt Senior/PWD Logic:**
Inside `totalTaxes`, the code loops through individual passengers and checks `phDiscountType`. If a passenger is `'senior'` or `'pwd'`, their base fare is removed from the VAT-taxable amount. This faithfully implements Philippine VATABLE fare rules at the frontend before sending to backend for confirmation.

---

### 8. `validate_activity_code` — Backend Activity Gate
**File:** `fbs_backend/flightapp/views.py` (Lines 1319–1428)

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_activity_code(request):
    activity_code = request.data.get('activity_code', '').strip().upper()

    # 1. Find the activity
    activity = Activity.objects.get(activity_code=activity_code, is_code_active=True)

    # 2. Confirm student is enrolled in the section
    student = Students.objects.get(user=request.user)
    is_enrolled = SectionEnrollment.objects.filter(
        student=student, section=activity.section, is_active=True
    ).exists()

    if not is_enrolled:
        return Response({'success': False, 'error': '...'}, status=403)

    # 3. Prevent re-submission
    existing_booking = Booking.objects.filter(
        user=request.user, activity=activity,
        status='Confirmed', is_practice=False
    ).first()
    if existing_booking:
        return Response({'success': False, 'completed': True, ...}, status=403)

    # 4. Return full activity requirements
    return Response({'success': True, 'activity': { ... }})
```

**Explanation 1 — Three-Layer Security Gate:**
This endpoint is decorated with `@permission_classes([IsAuthenticated])`, so unauthenticated requests are rejected before even reaching the function code. Inside, it then checks (1) if the activity code is valid and active, (2) if the student is enrolled in the right section, and (3) if the student hasn't already completed this activity. All three must pass.

**Explanation 2 — Idempotency via Re-submission Block:**
The check for an existing `Confirmed` booking with `is_practice=False` prevents a student from doing the activity twice to get a higher score. The `completed: True` flag in the response lets the frontend show a specific, informative message rather than a generic "invalid code" error.

**Explanation 3 — Requirements Returned on Success:**
On success, the endpoint returns a detailed `requirements` object: `trip_type`, `origin`, `destination`, `travel_class`, `passengers`, and even specific `activity_addons`. The frontend booking flow uses these to pre-fill or lock fields, guiding the student toward the correct booking criteria for their assessment.

---

### 9. `create_booking` — Backend Booking Creation Engine
**File:** `fbs_backend/flightapp/views.py` (Lines 1433–1656)

```python
@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking(request):
    # 1. Serializer validation
    serializer = CreateBookingSerializer(data=request.data, ...)
    if not serializer.is_valid(): return Response({'error': ...}, 400)

    with transaction.atomic():
        # 2. Use authenticated user, NEVER trust frontend user ID
        user = request.user if request.user.is_authenticated else _get_or_create_user(data)

        # 3. Create Booking record — total starts at 0
        booking = Booking.objects.create(
            user=user, trip_type=trip_type, status='Pending',
            total_amount=Decimal('0.00'),  # SECURITY: never trust frontend total
            is_practice=is_practice, activity=activity_to_link
        )

        # 4. Create passengers, segments, booking details
        passengers = _create_passengers(data.get('passengers', []))
        # ... foreach passenger foreach segment: _create_booking_detail(...)

        # 5. Apply taxes, insurance, update totals
        _apply_taxes(booking, booking_details)
        _update_booking_totals(booking)

        # 6. Auto-grade if this is a real activity submission
        if booking.activity:
            score_data = calculate_submission_score(booking.activity, booking)
            binding.grade = score_data['total']
            binding.status = 'submitted'
            binding.save()

    return Response({'success': True, 'booking_id': ..., 'total_amount': float(booking.total_amount)}, 201)
```

**Explanation 1 — Server-Side Price Authority (SECURITY):**
The booking is always created with `total_amount=Decimal('0.00')`. The backend then calls `_update_booking_totals(booking)` which recalculates the price using actual database records (schedule prices, tax tables, addon prices). The frontend-supplied amount is **completely ignored**. This prevents price tampering.

**Explanation 2 — Atomic Transaction for Data Integrity:**
The entire creation process — user, booking, contact, passengers, segment details, taxes, insurance — is wrapped in `transaction.atomic()`. If any step fails (e.g., a segment references a non-existent schedule), ALL changes are rolled back and the database stays consistent. No partial bookings are left dangling.

**Explanation 3 — Inline Auto-Grading on Submission:**
Immediately after saving the booking, if `booking.activity` is set (it's a real activity, not practice), `calculate_submission_score()` is called. The score is stored in `ActivityStudentBinding` right away. This means the instructor sees the grade appear in real time as soon as the student submits — no cron job needed.

---

### 10. `process_payment_from_paymongo` — Post-Payment Confirmation Pipeline
**File:** `fbs_backend/flightapp/views.py` (Lines 1076–1173)

```python
def process_payment_from_paymongo(payment_id, payment_attrs, booking):
    with transaction.atomic():
        amount = Decimal(str(payment_attrs['amount'] / 100))  # centavos → PHP

        # 1. Create payment record
        payment = Payment.objects.create(
            booking=booking, amount=amount,
            method=payment_method, transaction_id=payment_id,
            status='Completed', payment_date=timezone.now()
        )

        # 2. Confirm booking + update all detail records
        booking.status = 'Confirmed'
        booking.submitted_at = timezone.now()
        booking.save()
        booking.details.all().update(status='confirmed')

        # 3. Lock seats
        for detail in booking.details.all():
            if detail.seat:
                detail.seat.is_available = False
                detail.seat.save()

        # 4. Trigger final grading
        if booking.activity:
            grade_booking(booking, booking.activity.id)

        # 5. Send confirmation email
        EmailService.send_booking_confirmation(booking, payment)
```

**Explanation 1 — Centavos-to-PHP Conversion:**
PayMongo always returns amounts in **centavos** (smallest currency unit). `payment_attrs['amount'] / 100` converts ₱150,000 centavos → ₱1,500. Using `Decimal(str(...))` avoids floating-point precision loss that could cause ₱1499.9999... instead of ₱1500.00 in the database.

**Explanation 2 — Cascading Status Updates in One Transaction:**
In a single atomic block, the code confirms the `Booking` record, updates all `BookingDetail` rows to `'confirmed'`, and marks all associated `Seat` records as unavailable. This ensures the seat inventory is atomically locked — no race condition can cause two bookings to claim the same seat.

**Explanation 3 — Post-Payment Auto-Grading:**
After payment succeeds, `grade_booking()` is called again. This is the **final grade** — at this point, the payment itself is a grading criterion (confirming that the student completed the full end-to-end booking workflow, including payment). Activities that only reach the "booking created" stage but never pay will receive a lower score.

---

### 11. `PassengerDetailsView` — `handleContinueToAddons()` with Fare-Based Routing
**File:** `bookingapp/src/views/booking/PassengerDetailsView.vue` (Lines 354–371)

```js
const handleContinueToAddons = async () => {
  if (await saveAllPassengersToStore()) {
    bookingStore.snapshotToServer();

    // If fare includes a seat (Standard, Flex, Business), go to Seat Selection first
    const hasIncludedSeat = Object.values(bookingStore.fareFamilies).some(fare =>
      ['standard', 'flex', 'business', 'business_plus', 'premium'].includes(fare)
    );

    if (hasIncludedSeat) {
      router.push({ name: 'SeatSelection' });
    } else {
      router.push({ name: 'Addons' });
    }
  }
};
```

**Explanation 1 — Intelligent Step Routing Based on Fare Class:**
The next step after passenger details isn't always `Addons` — it depends on the fare family selected. If the student chose Standard, Flex, or Business class (which include a free seat selection), they're routed to `SeatSelection` first. This mirrors real airline booking UX where higher fares have priority seat pick.

**Explanation 2 — Data Saved Before Navigation:**
`saveAllPassengersToStore()` is `async` and validates all required fields before saving to Pinia. Routing only happens if it returns `true`. This means the student can never proceed with incomplete or invalid passenger data — the validation acts as a final gate before the next step.

**Explanation 3 — `snapshotToServer()` for Session Recovery:**
After saving to the Pinia store, `bookingStore.snapshotToServer()` is called. This pushes the current state to the backend so that if the student's browser crashes or they lose connection, the session can be restored. It's not required for the happy path, but it makes the booking resilient.

---

### 12. `SearchResultsView` — Flight Selection Confirmation Modal (Round-Trip)
**File:** `bookingapp/src/views/booking/SearchResultsView.vue` (Lines 201–268)

```html
<div v-if="isRoundTrip && selectionPhase === 'return' && bookingStore.selectedOutbound">
  <!-- Round Trip Complete Summary -->
  <div class="bg-pink-50 rounded-lg p-4">
    <!-- Outbound flight summary -->
    <div class="border-l-4 border-pink-500 pl-4">
      Outbound • {{ bookingStore.selectedOutbound?.flight_number }}
      ₱{{ Number(bookingStore.selectedOutbound?.price).toLocaleString() }}
    </div>
    <!-- Return flight summary -->
    <div class="border-l-4 border-pink-300 pl-4">
      Return • {{ selectedFlight?.flight_number }}
      ₱{{ Number(selectedFlight?.price).toLocaleString() }}
    </div>
    <!-- Combined total -->
    ₱{{ (Number(bookingStore.selectedOutbound?.price) + Number(selectedFlight?.price)).toLocaleString() }}
  </div>
</div>
```

**Explanation 1 — Phase-Aware UI Rendering:**
The confirmation modal renders completely different content depending on `selectionPhase` — when choosing the return flight, it shows BOTH flights in a combined itinerary view. This gives the student the equivalent of a real airline's "review your complete trip" summary before confirming both legs.

**Explanation 2 — Pinia Store as the Outbound Source:**
For the round-trip summary, the outbound flight data comes from `bookingStore.selectedOutbound` (previously committed to the store when the student selected their first flight), while the return flight data comes from the locally-scoped `selectedFlight` reactive variable. This two-source design avoids re-fetching data.

**Explanation 3 — Price Transparency at the Point of Confirmation:**
The combined price `outbound.price + return.price` is shown directly in the confirmation modal before the student clicks "Confirm." This prevents sticker shock at the payment page — the student knows the total before committing to the itinerary.

---

## Summary Table

| # | Snippet | Layer | Purpose |
|---|---------|-------|---------|
| 1 | `filteredActivities` | Vue Computed | Tab-based activity filter |
| 2 | `checkIsOverdue()` | Vue Method | Deadline enforcement |
| 3 | `startPracticeBooking()` | Vue Method | Launch practice simulation |
| 4 | `openComparisonModal()` | Vue Method | Grade comparison viewer |
| 5 | `upcomingDeadlines` | Vue Computed | Deadline sidebar feed |
| 6 | `useBookingStore state` | Pinia Store | Global booking state machine |
| 7 | `grandTotal / authoritativeTotal` | Pinia Getters | Price calculation hierarchy |
| 8 | `validate_activity_code` | Django View | Activity gating + enrollment check |
| 9 | `create_booking` | Django View | Atomic booking creation engine |
| 10 | `process_payment_from_paymongo` | Django Function | Payment confirmation + grading |
| 11 | `handleContinueToAddons` | Vue Setup | Fare-aware step routing |
| 12 | Flight confirmation modal | Vue Template | Round-trip itinerary summary |
