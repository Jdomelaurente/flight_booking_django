import { defineStore } from 'pinia';
import { bookingService } from '@/services/booking/bookingService';
import { useNotificationStore } from './notification';

export const useBookingStore = defineStore('booking', {
  state: () => ({
    booking_id: localStorage.getItem('current_booking_id') || null,
    booking_reference: null,
    booking_status: null,
    booking_total: 0,
    selectedOutbound: null,
    selectedReturn: null,
    tripType: 'one_way',

    // Multi-city Segments
    multiCitySegments: [], // Array of { origin: {code, city}, destination: {code, city}, date: 'YYYY-MM-DD', selectedFlight: null }
    currentSegmentIndex: 0,

    passengerCount: {
      adults: 1,
      children: 0,
      infants: 0,
    },
    passengers: [],
    infantAdultMapping: {},
    contactInfo: {
      title: '',
      firstName: '',
      middleName: '',
      lastName: '',
      email: '',
      phone: ''
    },

    // UPDATED: Segments are now keys (0, 1, 2... or 'depart', 'return')
    addons: {
      baggage: {},     // { segmentIndexOrKey: { passengerKey: baggageObject } }
      meals: {},       // { segmentIndexOrKey: { passengerKey: mealObject } }
      wheelchair: {},  // { segmentIndexOrKey: { passengerKey: assistanceId } }
      seats: {},       // { segmentIndexOrKey: { passengerKey: seatObject } }
      insurance: {
        selectedPlanId: null,
        price: 0
      }
    },

    // Activity Code & Practice Mode
    activityCode: null,           // Activity code entered by student
    isPractice: false,            // Whether this is a practice booking
    hasActivityCodeValidation: false, // Whether student has completed activity code step

    sessionExpiry: null,
    isFreshSession: true,
  }),

  persist: {
    key: 'booking-store',
    storage: localStorage,
  },

  getters: {
    isRoundTrip: (state) => state.tripType === 'round-trip' || state.tripType === 'round_trip',
    isMultiCity: (state) => state.tripType === 'multi-city' || state.tripType === 'multi_city',

    payingPassengerCount: (state) => {
      const { adults = 0, children = 0 } = state.passengerCount || {};
      return adults + children;
    },

    // Flexible segments getter
    allSegments: (state) => {
      if (state.isMultiCity) {
        return state.multiCitySegments;
      }

      const segments = [];
      if (state.selectedOutbound) {
        segments.push({
          type: 'depart',
          selectedFlight: state.selectedOutbound
        });
      }
      if (state.isRoundTrip && state.selectedReturn) {
        segments.push({
          type: 'return',
          selectedFlight: state.selectedReturn
        });
      }
      return segments;
    },

    totalSeatsPrice(state) {
      const seats = state.addons?.seats || {};
      let total = 0;
      const activeSegments = this.allSegments;

      activeSegments.forEach((seg, index) => {
        const segKey = state.isMultiCity ? index.toString() : seg.type;
        const segmentSeats = seats[segKey] || {};
        Object.values(segmentSeats).forEach(seat => {
          if (seat && seat.seat_price !== undefined) {
            total += (parseFloat(seat.seat_price) || 0);
          }
        });
      });
      return total;
    },

    totalBaggagePrice(state) {
      let total = 0;
      const baggage = state.addons?.baggage || {};
      const activeSegments = this.allSegments;

      activeSegments.forEach((seg, index) => {
        const segKey = state.isMultiCity ? index.toString() : seg.type;
        const segmentBaggage = baggage[segKey] || {};
        Object.values(segmentBaggage).forEach(baggageItem => {
          if (baggageItem && typeof baggageItem === 'object' && baggageItem.price !== undefined) {
            total += (parseFloat(baggageItem.price) || 0);
          }
        });
      });
      return total;
    },

    totalMealsPrice(state) {
      let total = 0;
      const meals = state.addons?.meals || {};
      const activeSegments = this.allSegments;

      activeSegments.forEach((seg, index) => {
        const segKey = state.isMultiCity ? index.toString() : seg.type;
        const segmentMeals = meals[segKey] || {};
        Object.values(segmentMeals).forEach(meal => {
          if (meal && typeof meal === 'object' && meal.price !== undefined) {
            total += (parseFloat(meal.price) || 0);
          }
        });
      });
      return total;
    },

    totalAssistancePrice(state) {
      return 0; // Assistance is typically free
    },

    combinedBasePrice(state) {
      let base = 0;
      if (state.tripType === 'multi_city' || state.tripType === 'multi-city') {
        state.multiCitySegments.forEach(seg => {
          if (seg.selectedFlight?.price) {
            base += parseFloat(seg.selectedFlight.price);
          }
        });
      } else {
        const outboundPrice = parseFloat(state.selectedOutbound?.price) || 0;
        const returnPrice = (state.tripType === 'round_trip' || state.tripType === 'round-trip') && state.selectedReturn?.price
          ? parseFloat(state.selectedReturn.price)
          : 0;
        base = outboundPrice + returnPrice;
      }
      return base;
    },

    grandTotalForAdults(state) {
      const base = this.combinedBasePrice;
      const count = state.passengerCount.adults || 0;
      return base * count;
    },

    grandTotalForChildren(state) {
      const base = this.combinedBasePrice;
      const count = state.passengerCount.children || 0;
      return base * count;
    },

    grandTotalForInfants(state) {
      const base = this.combinedBasePrice;
      const count = state.passengerCount.infants || 0;
      return (base * 0.5) * count;
    },

    // Total Base Fare for all passengers
    combinedBasePriceTotal(state) {
      const adultsCount = state.passengerCount.adults || 0;
      const childrenCount = state.passengerCount.children || 0;
      const infantsCount = state.passengerCount.infants || 0;
      const base = this.combinedBasePrice;

      return (base * (adultsCount + childrenCount)) + ((base * 0.5) * infantsCount);
    },

    // Total for all selected add-ons (Active segments only)
    totalAddonsPrice(state) {
      return this.totalBaggagePrice + this.totalMealsPrice + this.totalSeatsPrice + this.totalAssistancePrice;
    },

    // Standard 12% tax applied ONLY to the Base Fare (matches backend)
    totalTaxes(state) {
      return this.combinedBasePriceTotal * 0.12;
    },

    // Insurance price (covers all passengers once)
    insurancePrice(state) {
      return parseFloat(state.addons?.insurance?.price) || 0;
    },

    // Assistance price (active segments only)
    totalAssistancePrice(state) {
      let total = 0;
      const activeSegments = this.allSegments;
      activeSegments.forEach((seg, index) => {
        const segKey = this.isMultiCity ? index.toString() : seg.type;
        const assistance = state.addons.wheelchair?.[segKey];
        // If assistance is an object with a price
        if (assistance && typeof assistance === 'object' && assistance.price) {
          total += parseFloat(assistance.price) || 0;
        }
      });
      return total;
    },

    // Final aggregated amount
    grandTotal(state) {
      return this.combinedBasePriceTotal + this.totalTaxes + this.totalAddonsPrice + this.insurancePrice;
    },

    // Backward compatibility or internal use
    subtotal(state) {
      return this.combinedBasePriceTotal;
    },

    isFlightSelectionComplete(state) {
      if (this.isMultiCity) {
        return state.multiCitySegments.length > 0 &&
          state.multiCitySegments.every(seg => !!seg.selectedFlight);
      }

      if (state.tripType === 'one_way') {
        return state.selectedOutbound !== null;
      } else if (this.isRoundTrip) {
        return state.selectedOutbound !== null && state.selectedReturn !== null;
      }
      return false;
    },

    isSessionValid: (state) => {
      if (!state.sessionExpiry) return false;
      return Date.now() < state.sessionExpiry;
    },

    timeLeftFormatted(state) {
      if (!state.sessionExpiry) return '00:00';
      const diff = Math.max(0, Math.round((state.sessionExpiry - Date.now()) / 1000));
      const mins = Math.floor(diff / 60);
      const secs = diff % 60;
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    },

    secondsLeft(state) {
      if (!state.sessionExpiry) return 0;
      return Math.max(0, Math.round((state.sessionExpiry - Date.now()) / 1000));
    },

    // NEW: Get seats by segment
    getSeatsBySegment(state) {
      return (segmentKey = 'depart') => {
        return state.addons.seats[segmentKey] || {};
      };
    },

    // NEW: Check if all passengers have seats for a segment
    allPassengersHaveSeatsForSegment(state) {
      return (segmentKey = 'depart') => {
        const segmentSeats = state.addons.seats[segmentKey] || {};
        return state.passengers.every(p => segmentSeats[p.key]);
      };
    },

    // NEW: Check if all passengers have seats for all segments
    allPassengersHaveAllSeats(state) {
      const segments = this.allSegments;
      if (segments.length === 0) return false;

      return segments.every((seg, index) => {
        const segmentKey = this.isMultiCity ? index.toString() : seg.type;
        const segmentSeats = state.addons.seats[segmentKey] || {};
        return state.passengers.every(p => segmentSeats[p.key]);
      });
    },

    // NEW: Check if session should be cleared for home page
    shouldClearSessionForHome(state) {
      const sessionValid = this.isSessionValid;
      const hasBookingData = state.passengers.length > 0 || state.selectedOutbound || state.booking_id || state.multiCitySegments.length > 0;

      return {
        shouldClear: sessionValid && hasBookingData,
        hasBookingData,
        sessionValid
      };
    }
  },

  actions: {
    loadBookingFromStorage() {
      try {
        const savedBooking = JSON.parse(localStorage.getItem('current_booking'));
        if (savedBooking) {
          this.booking_id = savedBooking.id;
          this.booking_reference = savedBooking.pnr || savedBooking.reference || `CSUCC${String(savedBooking.id).padStart(8, '0')}`;
          this.booking_status = savedBooking.status || 'pending';
          this.booking_total = savedBooking.total || 0;
          console.log('📥 Loaded booking from storage:', {
            id: this.booking_id,
            reference: this.booking_reference,
            status: this.booking_status,
            total: this.booking_total
          });
        }
      } catch (error) {
        console.error('Error loading booking from storage:', error);
      }
    },

    startSession() {
      this.sessionExpiry = Date.now() + (15 * 60 * 1000);
      this.isFreshSession = true;
      console.log('🔄 Session started, expires at:', new Date(this.sessionExpiry).toLocaleString());

      setTimeout(() => {
        this.isFreshSession = false;
      }, 1000);
    },

    checkSession() {
      if (!this.sessionExpiry) {
        console.log('❌ No active session found');
        this.resetBooking();
        return { valid: false, reason: 'No active session', expired: true };
      }

      const now = Date.now();
      const timeLeft = this.sessionExpiry - now;
      const minutesLeft = Math.floor(timeLeft / (60 * 1000));
      const secondsLeft = Math.floor((timeLeft % (60 * 1000)) / 1000);

      if (timeLeft <= 0) {
        console.log('⏰ Session expired, resetting booking');
        this.clearActivityCodeValidation();
        this.resetBooking();
        return {
          valid: false,
          reason: 'Session expired',
          expired: true
        };
      }

      return {
        valid: true,
        timeLeft,
        minutesLeft,
        secondsLeft,
        expiresAt: new Date(this.sessionExpiry).toLocaleString()
      };
    },

    initSession() {
      if (!this.sessionExpiry || Date.now() >= this.sessionExpiry) {
        this.startSession();
      } else {
        console.log('✅ Existing session found, expires:', new Date(this.sessionExpiry).toLocaleString());
        this.isFreshSession = false;
      }
    },

    // NEW: Method to clear session when visiting home
    clearSessionForHome() {
      const session = this.checkSession();

      if (session.valid) {
        console.log('⚠️ Active booking session found. Clearing for home page...');

        // Check if there's actual booking data
        if (this.passengers.length > 0 || this.selectedOutbound) {
          console.log('📋 User has booking data. Session will be cleared.');
          this.resetBooking();
          return true;
        } else {
          // Just reset silently if no real data
          this.resetBooking();
          return true;
        }
      } else {
        // Make sure store is clean
        this.resetBooking();
        return true;
      }
    },

    async clearSessionWithConfirmation() {
      const modalStore = useModalStore();
      const session = this.checkSession();

      if (session.valid) {
        // Show confirmation if user has unsaved data
        if (this.passengers.length > 0 || this.selectedOutbound || this.booking_id) {
          const userConfirmed = await modalStore.confirm({
            title: 'Active Session Found',
            message: 'We found an active booking session. Would you like to start a new search? Your current booking data will be cleared.',
            confirmText: 'Start New Search',
            cancelText: 'Resume Current'
          });

          if (userConfirmed) {
            this.resetBooking();
            console.log('✅ User confirmed clearing session');
            return { cleared: true, userConfirmed: true };
          } else {
            console.log('❌ User cancelled session clearing');
            return { cleared: false, userConfirmed: false };
          }
        } else {
          // Just reset silently if no real data
          this.resetBooking();
          console.log('✅ Session cleared (no real data)');
          return { cleared: true, userConfirmed: true };
        }
      } else {
        // Make sure store is clean
        this.resetBooking();
        console.log('✅ Session expired, store cleaned');
        return { cleared: true, userConfirmed: true };
      }
    },

    setTripType(type) {
      console.log('🟢 Setting trip type in Pinia:', type);
      const normalizedType = type === 'round-trip' ? 'round_trip' : type;
      this.tripType = normalizedType;

      if (normalizedType === 'one_way' && this.selectedReturn) {
        console.log('Clearing return flight due to trip type change');
        this.selectedReturn = null;

        // Clear return add-ons
        this.addons.baggage.return = {};
        this.addons.meals.return = {};
        this.addons.wheelchair.return = {};
        this.addons.seats.return = {};
      }
    },

    setPassengerCount(counts) {
      this.passengerCount.adults = counts.adult;
      this.passengerCount.children = counts.children;
      this.passengerCount.infants = counts.infant;
    },

    // Activity Code & Practice Mode Actions
    setActivityCode(code, activityData = null) {
      this.activityCode = code;
      this.isPractice = false;
      this.hasActivityCodeValidation = true;
      this.startSession();
      console.log('✅ Activity code set:', code);
      if (activityData) {
        console.log('📋 Activity details:', activityData);
      }
    },

    setPracticeMode() {
      this.activityCode = null;
      this.isPractice = true;
      this.hasActivityCodeValidation = true;
      this.startSession();
      console.log('✅ Practice mode enabled');
    },

    clearActivityCodeValidation() {
      this.activityCode = null;
      this.isPractice = false;
      this.hasActivityCodeValidation = false;
      console.log('🔄 Activity code validation cleared');
    },

    setTripType(type) {
      console.log('🟢 Setting trip type in Pinia:', type);
      const normalizedType = type === 'round-trip' ? 'round_trip' :
        (type === 'multi-city' ? 'multi_city' : type);

      // If trip type actually changes, clear all non-insurance add-ons to prevent stale data
      if (this.tripType !== normalizedType) {
        console.log(`🧹 Trip type changed from ${this.tripType} to ${normalizedType}. Clearing add-ons.`);
        this.addons.baggage = {};
        this.addons.meals = {};
        this.addons.wheelchair = {};
        this.addons.seats = {};
      }

      this.tripType = normalizedType;

      if (normalizedType === 'one_way') {
        this.selectedReturn = null;
        this.multiCitySegments = [];
      } else if (normalizedType === 'round_trip') {
        this.multiCitySegments = [];
      } else if (normalizedType === 'multi_city') {
        this.selectedOutbound = null;
        this.selectedReturn = null;
      }
    },

    setMultiCitySegments(segments) {
      console.log('🟢 Setting Multi-city segments:', segments);
      this.multiCitySegments = segments.map(s => ({
        origin: s.origin,
        destination: s.destination,
        date: s.date,
        selectedFlight: null
      }));
      this.currentSegmentIndex = 0;
      this.tripType = 'multi_city';
    },

    selectSegmentFlight(index, flight) {
      if (this.multiCitySegments[index]) {
        // Apply seat class info if it's a raw flight object
        const seatClassInfo = {
          seat_class: flight.seat_class || flight.selected_seat_class,
          selected_seat_class: flight.selected_seat_class,
          seat_class_price: flight.price,
          original_base_price: flight.original_price || flight.base_price,
          seat_class_features: flight.seat_class_features
        };

        this.multiCitySegments[index].selectedFlight = {
          ...flight,
          ...seatClassInfo
        };
        console.log(`✅ Flight selected for segment ${index}:`, flight.flight_number);
      }
    },

    // NEW: Minimum Connecting Time (MCT) Validation
    validateMultiCityConnection(index, flight) {
      if (index === 0) return { valid: true }; // First segment is always valid

      const previousSegment = this.multiCitySegments[index - 1];
      if (!previousSegment || !previousSegment.selectedFlight) {
        return { valid: true }; // No previous flight to compare against
      }

      const prevFlight = previousSegment.selectedFlight;

      // Basic check that dates exist
      if (!prevFlight.arrival_time || !flight.departure_time) {
        return { valid: true };
      }

      const prevArrival = new Date(prevFlight.arrival_time);
      const nextDeparture = new Date(flight.departure_time);

      // Calculate difference in milliseconds, convert to hours
      const diffMs = nextDeparture - prevArrival;
      const diffHours = diffMs / (1000 * 60 * 60);

      const isValid = diffHours >= 1.5;

      return {
        valid: isValid,
        diffHours: diffHours,
        message: isValid
          ? 'Valid connection'
          : 'Connection Too Short: You need at least 1.5 hours between flights.'
      };
    },

    nextSegment() {
      if (this.currentSegmentIndex < this.multiCitySegments.length - 1) {
        this.currentSegmentIndex++;
      }
    },

    prevSegment() {
      if (this.currentSegmentIndex > 0) {
        this.currentSegmentIndex--;
      }
    },

    selectFlight(flight, type = 'outbound') {
      const seatClassInfo = {
        seat_class: flight.seat_class || flight.selected_seat_class,
        selected_seat_class: flight.selected_seat_class,
        seat_class_price: flight.price,
        original_base_price: flight.original_price || flight.base_price,
        seat_class_features: flight.seat_class_features
      };

      const flightWithSeatClass = {
        ...flight,
        ...seatClassInfo,
        price: flight.price
      };

      if (type === 'outbound') {
        this.selectedOutbound = flightWithSeatClass;
        console.log('✅ Outbound flight selected with seat class:', {
          flight: flight.flight_number,
          seat_class: flight.selected_seat_class,
          price: flight.price
        });
      } else {
        if (this.tripType === 'round_trip') {
          this.selectedReturn = flightWithSeatClass;
          console.log('✅ Return flight selected with seat class:', {
            flight: flight.flight_number,
            seat_class: flight.selected_seat_class,
            price: flight.price
          });
        } else {
          console.warn('Cannot select return flight for one-way trip');
        }
      }
    },

    setInfantAdultAssociation(infantKey, adultKey) {
      if (!infantKey || !adultKey) {
        console.error('Infant and adult keys are required');
        return;
      }

      const infant = this.passengers.find(p => p.key === infantKey);
      if (!infant || infant.type !== 'Infant') {
        console.error('Invalid infant key:', infantKey);
        return;
      }

      const adult = this.passengers.find(p => p.key === adultKey);
      if (!adult || adult.type !== 'Adult') {
        console.error('Invalid adult key:', adultKey);
        return;
      }

      const currentInfantCount = Object.values(this.infantAdultMapping)
        .filter(key => key === adultKey).length;

      if (currentInfantCount >= 1) {
        console.warn('Adult already has an infant assigned:', adultKey);
        Object.keys(this.infantAdultMapping).forEach(key => {
          if (this.infantAdultMapping[key] === adultKey) {
            delete this.infantAdultMapping[key];
          }
        });
      }

      this.infantAdultMapping[infantKey] = adultKey;
      console.log(`✅ Infant ${infantKey} assigned to adult ${adultKey}`);
    },

    setPassengers(passengerList) {
      console.log('🟢 STORING PASSENGERS IN PINIA:');

      this.infantAdultMapping = {};

      const processedPassengers = passengerList.map((passenger, index) => {
        const key = passenger.key || `pax_${index + 1}`;

        if (passenger.type === 'Infant' && passenger.associatedAdult) {
          const adultKey = `pax_${passenger.associatedAdult}`;
          this.infantAdultMapping[key] = adultKey;
          console.log(`👶 Stored infant association: ${key} -> ${adultKey}`);
        }

        return {
          key: key,
          firstName: passenger.firstName || '',
          lastName: passenger.lastName || '',
          middleName: passenger.middleName || '',
          title: passenger.title || (passenger.type === 'Infant' ? 'CHD' : 'MR'),
          dateOfBirth: passenger.dateOfBirth || this.getDefaultDOB(passenger.type),
          nationality: passenger.nationality || 'Philippines',
          passportNumber: passenger.passportNumber || '',
          type: passenger.type || 'Adult'
        };
      });

      this.passengers = processedPassengers;
    },

    getDefaultDOB() {
      const date = new Date();
      date.setFullYear(date.getFullYear() - 20);
      return date.toISOString().split('T')[0];
    },

    setContactInfo(info) {
      this.contactInfo = { ...this.contactInfo, ...info };
    },

    // ========== UPDATED ADD-ON METHODS WITH SEGMENTED SEATS ==========

    setAddons(addonData) {
      this.addons = {
        baggage: addonData.baggage || {},
        meals: addonData.meals || {},
        wheelchair: addonData.wheelchair || {},
        seats: addonData.seats || {},
        insurance: addonData.insurance || { selectedPlanId: null, price: 0 }
      };
    },

    // Baggage methods
    updateBaggageAddon(passengerKey, baggageData, segment = 'depart') {
      if (!this.addons.baggage[segment]) {
        this.addons.baggage[segment] = {};
      }
      this.addons.baggage[segment][passengerKey] = baggageData;
    },

    removeBaggageAddon(passengerKey, segment = 'depart') {
      if (this.addons.baggage[segment] && this.addons.baggage[segment][passengerKey]) {
        delete this.addons.baggage[segment][passengerKey];
      }
    },

    // Meal methods
    updateMealAddon(passengerKey, mealData, segment = 'depart') {
      if (!this.addons.meals[segment]) {
        this.addons.meals[segment] = {};
      }
      this.addons.meals[segment][passengerKey] = mealData;
    },

    removeMealAddon(passengerKey, segment = 'depart') {
      if (this.addons.meals[segment] && this.addons.meals[segment][passengerKey]) {
        delete this.addons.meals[segment][passengerKey];
      }
    },

    // Assistance methods
    updateAssistanceAddon(passengerKey, serviceId, segment = 'depart') {
      if (!this.addons.wheelchair[segment]) {
        this.addons.wheelchair[segment] = {};
      }
      this.addons.wheelchair[segment][passengerKey] = serviceId;
    },

    removeAssistanceAddon(passengerKey, segment = 'depart') {
      if (this.addons.wheelchair[segment] && this.addons.wheelchair[segment][passengerKey]) {
        delete this.addons.wheelchair[segment][passengerKey];
      }
    },

    // UPDATED: Seat methods with segment support
    assignSeat(passengerKey, seatData, segment = 'depart') {
      if (!this.addons.seats[segment]) {
        this.addons.seats[segment] = {};
      }

      this.addons.seats[segment][passengerKey] = {
        id: seatData.id,
        seat_code: seatData.seat_code,
        seat_price: parseFloat(seatData.seat_price) || 0,
        seat_total_price: parseFloat(seatData.seat_total_price) || 0,
        seat_class: {
          name: seatData.seat_class_name || seatData.seat_class?.name
        },
        flight_segment: segment,
        schedule_id: segment === 'depart' ? this.selectedOutbound?.id : this.selectedReturn?.id
      };

      console.log(`💺 Seat assigned for ${segment} flight:`, {
        passengerKey,
        seat_code: seatData.seat_code,
        seat_price: seatData.seat_price,
        segment
      });
    },

    removeSeat(passengerKey, segment = 'depart') {
      if (this.addons.seats[segment] && this.addons.seats[segment][passengerKey]) {
        delete this.addons.seats[segment][passengerKey];
        console.log(`❌ Seat removed for ${segment} flight:`, passengerKey);
      }
    },

    // Copy seats from depart to return
    copySeatsToReturn() {
      if (!this.isRoundTrip) return;

      console.log('📋 Copying seats from depart to return segment');
      this.addons.seats.return = JSON.parse(JSON.stringify(this.addons.seats.depart || {}));

      // Update flight segment info for return seats
      Object.keys(this.addons.seats.return).forEach(passengerKey => {
        if (this.addons.seats.return[passengerKey]) {
          this.addons.seats.return[passengerKey].flight_segment = 'return';
          this.addons.seats.return[passengerKey].schedule_id = this.selectedReturn?.id;
        }
      });
    },

    // NEW: Copy all add-ons to return
    copyAllAddonsToReturn() {
      if (!this.isRoundTrip) return;

      console.log('📋 Copying all add-ons from depart to return segment');

      // Copy baggage
      this.addons.baggage.return = JSON.parse(JSON.stringify(this.addons.baggage.depart || {}));

      // Copy meals
      this.addons.meals.return = JSON.parse(JSON.stringify(this.addons.meals.depart || {}));

      // Copy assistance
      this.addons.wheelchair.return = JSON.parse(JSON.stringify(this.addons.wheelchair.depart || {}));

      // Copy seats
      this.copySeatsToReturn();
    },

    /**
     * Propagates an add-on selection from a source segment to all other active segments.
     * Useful for Multi-city trips where users want the same baggage/meal for all flights.
     * 
     * @param {String} type - 'baggage', 'meals', or 'wheelchair'
     * @param {String} passengerKey - The key of the passenger
     * @param {String} sourceSegmentKey - The key of the segment to copy FROM (e.g., 'depart' or '0')
     */
    copyAddonToAllSegments(type, passengerKey, sourceSegmentKey) {
      if (!this.addons[type]) return;

      const sourceValue = this.addons[type][sourceSegmentKey]?.[passengerKey];
      if (!sourceValue) return;

      console.log(`📋 Copying ${type} for passenger ${passengerKey} from segment ${sourceSegmentKey} to all active segments`);

      const activeSegments = this.allSegments;
      activeSegments.forEach((seg, index) => {
        const segKey = this.isMultiCity ? index.toString() : seg.type;

        // Skip the source segment itself
        if (segKey === sourceSegmentKey) return;

        // Ensure segment exists in store
        if (!this.addons[type][segKey]) {
          this.addons[type][segKey] = {};
        }

        // Deep copy the selection
        this.addons[type][segKey][passengerKey] = JSON.parse(JSON.stringify(sourceValue));
        console.log(`   -> Copied to ${segKey}`);
      });
    },

    // Clear all addons
    clearAllAddons() {
      this.addons = {
        baggage: { depart: {}, return: {} },
        meals: { depart: {}, return: {} },
        wheelchair: { depart: {}, return: {} },
        seats: { depart: {}, return: {} },
        insurance: { selectedPlanId: null, price: 0 }
      };
    },

    // Clear only return add-ons
    clearReturnAddons() {
      this.addons.baggage.return = {};
      this.addons.meals.return = {};
      this.addons.wheelchair.return = {};
      this.addons.seats.return = {};
    },

    // Clear seats for a specific segment
    clearSeatsForSegment(segment = 'depart') {
      this.addons.seats[segment] = {};
    },

    // Insurance helpers
    selectInsurancePlan(planId, price) {
      this.addons.insurance.selectedPlanId = planId;
      this.addons.insurance.price = parseFloat(price) || 0;
    },

    clearInsurance() {
      this.addons.insurance.selectedPlanId = null;
      this.addons.insurance.price = 0;
    },

    saveBookingConfirmation(bookingData) {
      console.log('💾 Saving booking confirmation to store:', bookingData);

      this.booking_id = bookingData.booking_id;
      this.booking_reference = bookingData.pnr || bookingData.booking_reference || `CSUCC${String(bookingData.booking_id).padStart(8, '0')}`;
      this.booking_status = bookingData.status || 'pending';
      // Backend-calculated total is the source of truth for Payment.
      // Never prefer local grandTotal over an explicit backend total_amount.
      const backendTotal = parseFloat(bookingData.total_amount);
      this.booking_total = Number.isFinite(backendTotal) && backendTotal > 0
        ? backendTotal
        : (this.grandTotal || 0);
      this.sessionExpiry = Date.now() + (30 * 60 * 1000);

      localStorage.setItem('current_booking_id', this.booking_id);
      localStorage.setItem('current_booking_reference', this.booking_reference);
      localStorage.setItem('current_booking_status', this.booking_status);
      localStorage.setItem('current_booking_total', this.booking_total);

      console.log('✅ Booking confirmation saved:', {
        booking_id: this.booking_id,
        booking_reference: this.booking_reference,
        booking_status: this.booking_status,
        store_grand_total: this.grandTotal,
        saved_booking_total: this.booking_total
      });
    },

    setBookingId(id) {
      this.booking_id = id;
      this.booking_reference = `CSUCC${String(id).padStart(8, '0')}`;
      localStorage.setItem('current_booking_id', id);
      console.log('✅ Booking ID and reference set:', id, this.booking_reference);
    },

    // UPDATED: Reset booking with segmented seats
    resetBooking() {
      console.log('🧹 Resetting booking store...');
      localStorage.removeItem('current_booking_id');

      this.$patch({
        booking_id: null,
        booking_reference: null,
        booking_status: null,
        booking_total: 0,
        selectedOutbound: null,
        selectedReturn: null,
        multiCitySegments: [],
        currentSegmentIndex: 0,
        tripType: 'one_way',
        passengerCount: {
          adults: 1,
          children: 0,
          infants: 0,
        },
        passengers: [],
        infantAdultMapping: {},
        contactInfo: {
          title: '',
          firstName: '',
          middleName: '',
          lastName: '',
          email: '',
          phone: ''
        },
        addons: {
          baggage: {},
          meals: {},
          wheelchair: {},
          seats: {},
          insurance: {
            selectedPlanId: null,
            price: 0
          }
        },
        sessionExpiry: null,
        isFreshSession: true,
      });

      const keysToRemove = [
        'booking',
        'current_booking',
        'payment_session',
        'booking-store',
        'pinia-booking',
        'current_booking_id',
        'current_booking_reference',
        'current_booking_status',
        'current_booking_total',
        'last_booking_ref',
        ...Array.from({ length: 10 }, (_, i) => `pax_${i + 1}`),
        ...Array.from({ length: 15 }, (_, i) => `passenger_${i + 1}_details`),
      ];

      keysToRemove.forEach(key => {
        try {
          localStorage.removeItem(key);
          console.log(`🗑️ Removed from localStorage: ${key}`);
        } catch (error) {
          console.warn(`Could not remove ${key}:`, error);
        }
      });

      try {
        sessionStorage.clear();
        console.log('🗑️ Cleared sessionStorage');
      } catch (error) {
        console.warn('Could not clear sessionStorage:', error);
      }

      console.log("✅ Booking Store has been completely reset.");

      if (typeof this.$persist === 'function') {
        this.$persist();
      }
    },

    forceCompleteReset() {
      console.log('💥 FORCE RESETTING ALL STORAGE...');

      Object.keys(localStorage).forEach(key => {
        if (
          key.includes('booking') ||
          key.includes('pax') ||
          key.includes('flight') ||
          key.includes('pinia') ||
          key.includes('passenger') ||
          key.includes('seat')
        ) {
          localStorage.removeItem(key);
          console.log(`🗑️ Removed: ${key}`);
        }
      });

      sessionStorage.clear();
      this.resetBooking();
      console.log('✅ All storage has been force-cleared.');
    },

    // UPDATED: Migration helper for new seat structure
    migrateAddonsToNewFormat() {
      // Check if seats are in old flat structure
      if (this.addons.seats && !this.addons.seats.depart) {
        console.log('🔄 Migrating seats to new segmented format...');

        const oldSeats = this.addons.seats;

        // Move old seats to depart segment
        this.addons.seats = {
          depart: { ...oldSeats },
          return: {}
        };

        // Update flight segment info
        Object.keys(this.addons.seats.depart).forEach(passengerKey => {
          if (this.addons.seats.depart[passengerKey]) {
            this.addons.seats.depart[passengerKey].flight_segment = 'depart';
            this.addons.seats.depart[passengerKey].schedule_id = this.selectedOutbound?.id;
          }
        });

        // If round trip, copy to return
        if (this.isRoundTrip) {
          this.copySeatsToReturn();
        }

        console.log('✅ Seat migration complete');
      }
    },

    shouldLoadSavedPassengerData() {
      const session = this.checkSession();
      return session.valid && !this.isFreshSession;
    },

    // NEW: Get seat for a specific passenger and segment
    getSeatForPassenger(passengerKey, segment = 'depart') {
      return this.addons.seats[segment]?.[passengerKey] || null;
    },

    // NEW: Check if passenger has seat for segment
    hasSeatForSegment(passengerKey, segment = 'depart') {
      return !!this.addons.seats[segment]?.[passengerKey];
    },

    /**
     * Incremental save to server (Draft model).
     * Creates or updates a booking record on the backend in the background.
     */
    async snapshotToServer() {
      if (!this.selectedOutbound && !this.isMultiCity) return null;
      if (this.isMultiCity && this.multiCitySegments.every(s => !s.selectedFlight)) return null;

      try {
        console.log('🔄 Taking booking snapshot for server...');
        const payload = bookingService.formatBookingData(this);

        let res;
        if (this.booking_id) {
          res = await bookingService.updateBooking(this.booking_id, payload);
          console.log('✅ Snapshot updated (ID:', this.booking_id, ')');
        } else {
          res = await bookingService.createBooking(payload);
          if (res.success && res.booking_id) {
            this.booking_id = res.booking_id;
            localStorage.setItem('current_booking_id', res.booking_id);
            console.log('✅ Snapshot created (New ID:', res.booking_id, ')');
          }
        }
        return res;
      } catch (err) {
        console.error('❌ Snapshot failed:', err);
        return { success: false, error: err.message };
      }
    },

    /**
     * Restore state from backend using booking_id.
     * Full state recovery for cross-device or session recovery.
     */
    async syncFromServer() {
      if (!this.booking_id) return;

      try {
        console.log('📡 Syncing booking from server (ID:', this.booking_id, ')...');
        const res = await bookingService.getBookingDetails(this.booking_id);

        if (res && res.id) {
          this.booking_reference = res.booking_reference;
          this.booking_status = res.status;
          console.log('✅ Sync complete');
        }
      } catch (err) {
        console.error('❌ Sync failed:', err);
      }
    },

    // NEW: Get current booking state for debugging
    getCurrentState() {
      return {
        hasBookingId: !!this.booking_id,
        hasPassengers: this.passengers.length,
        hasOutbound: !!this.selectedOutbound,
        hasReturn: !!this.selectedReturn,
        sessionValid: this.isSessionValid,
        sessionExpiry: this.sessionExpiry ? new Date(this.sessionExpiry).toLocaleString() : 'No expiry',
        grandTotal: this.grandTotal
      };
    }
  }
});