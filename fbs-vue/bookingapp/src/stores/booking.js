import { defineStore } from 'pinia';
import { bookingService } from '@/services/booking/bookingService';
import { seatService } from '@/services/booking/seatService';
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
      meals: {},       // { segmentIndexOrKey: { passengerKey: [mealObject1, mealObject2, ...] } }
      wheelchair: {},  // { segmentIndexOrKey: { passengerKey: assistanceId } }
      seats: {},       // { segmentIndexOrKey: { passengerKey: seatObject } }
      insurance: {
        selectedPlanId: null,
        price: 0
      }
    },

    // Activity Code & Practice Mode
    activityCode: null,           // Activity code entered by student
    activityId: null,             // ID of the activity
    isPractice: false,            // Whether this is a practice booking
    hasActivityCodeValidation: false, // Whether student has completed activity code step
    activityExpiresAt: null,      // ISO string from backend

    nonStopOnly: false,
    stopPreference: 'all', // 'all', 'nonstop', 'direct', 'connecting'
    sessionExpiry: null,
    isFreshSession: true,
    bookingSessionId: localStorage.getItem('booking_session_id') || `sess_${Math.random().toString(36).substr(2, 9)}_${Date.now()}`,

    // Fare Families (Basic vs Premium)
    fareFamilies: {
      depart: 'basic', // fare family code: 'basic', 'standard', 'flex', etc.
      return: 'basic'
    },
    // Branded fare family display names (e.g. 'GO Basic', 'Value Pack')
    fareFamilyNames: {
      depart: '',
      return: ''
    },
    backendBreakdown: null, // Authoritative Backend Pricing Breakdown
    backendTaxDetails: null, // Specific Tax & Fees breakdown
    currentTime: Date.now()   // Reactive timestamp for timers
  }),

  persist: {
    key: 'booking-store',
    storage: localStorage,
  },

  getters: {
    isRoundTrip: (state) => state.tripType === 'round-trip' || state.tripType === 'round_trip',
    isMultiCity: (state) => state.tripType === 'multi-city' || state.tripType === 'multi_city',

    isInternational() {
      // Check if any flight is not domestic (PH -> PH)
      const segments = this.allSegments;
      if (segments.length === 0) return false;

      // Comprehensive list of PH airport codes
      const phAirports = [
        'MNL', 'CEB', 'DVO', 'ILO', 'BCD', 'PPS', 'TAC', 'LGP', 'CGY', 'MPH', 'USU', 'GES', 
        'KLO', 'ZAM', 'CYP', 'DPL', 'TUG', 'SFS', 'LAO', 'VAC', 'BHL', 'TAG', 'DGT', 'SJI',
        'RVN', 'SFE', 'BQA', 'BSO', 'CBO', 'CRM', 'CYP', 'DPL', 'MBT', 'NLO', 'OZC', 'PAG',
        'RXS', 'SGL', 'SNC', 'SUG', 'TDP', 'TUG', 'VGA', 'WNP', 'XCN', 'IAO', 'CRM', 'SIA'
      ];

      return segments.some(seg => {
        const flight = seg.selectedFlight;
        if (!flight) return false;

        // Priority 1: Use explicit is_domestic flag from backend if available
        if (flight.is_domestic === true) return false;
        if (flight.is_domestic === false) return true;

        // Priority 2: Fallback to airport code check
        // Check multiple possible field names used across different parts of the app
        const origin = (flight.origin || flight.origin_code || flight.origin_airport_code || '').toString().toUpperCase();
        const destination = (flight.destination || flight.destination_code || flight.destination_airport_code || '').toString().toUpperCase();

        const fromPH = phAirports.includes(origin) || origin.startsWith('PH-');
        const toPH = phAirports.includes(destination) || destination.startsWith('PH-');
        
        // If both are PH, it's domestic (return false for international)
        if (fromPH && toPH) return false;
        
        // Default to international if we can't confirm it's domestic
        return true;
      });
    },

    payingPassengerCount: (state) => {
      const { adults = 0, children = 0 } = state.passengerCount || {};
      return adults + children;
    },

    // Flexible segments getter
    allSegments() {
      if (this.isMultiCity) {
        return this.multiCitySegments;
      }

      const segments = [];
      if (this.selectedOutbound) {
        segments.push({
          type: 'depart',
          selectedFlight: this.selectedOutbound
        });
      }
      if (this.isRoundTrip && this.selectedReturn) {
        segments.push({
          type: 'return',
          selectedFlight: this.selectedReturn
        });
      }
      return segments;
    },

    totalSeatsPrice(state) {
      const seats = state.addons?.seats || {};
      let total = 0;
      const activeSegments = this.allSegments;

      activeSegments.forEach((seg, index) => {
        const segKey = this.isMultiCity ? index.toString() : seg.type;

        // Skip seat pricing if Premium fare is selected for this segment
        if (state.fareFamilies[segKey] === 'premium') {
          return;
        }

        const segmentSeats = seats[segKey] || {};
        Object.values(segmentSeats).forEach(seat => {
          if (seat) {
            // Support both internal property names and backend-serialized names
            const price = seat.final_price ?? seat.seat_price ?? seat.price ?? 0;
            total += parseFloat(price) || 0;
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
        const segKey = this.isMultiCity ? index.toString() : seg.type;
        const segmentBaggage = baggage[segKey] || {};

        const isPremium = state.fareFamilies[segKey] === 'premium';

        Object.values(segmentBaggage).forEach(baggageItem => {
          if (baggageItem && typeof baggageItem === 'object') {
            const rawPrice = baggageItem.sale_price ?? baggageItem.price ?? 0;
            let price = parseFloat(rawPrice) || 0;

            if (isPremium && baggageItem.weight_kg <= 20) {
              price = 0;
            } else if (isPremium && baggageItem.weight_kg > 20) {
              price = 0;
            }

            total += price;
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
        const segKey = this.isMultiCity ? index.toString() : seg.type;
        const segmentMeals = meals[segKey] || {};
        Object.values(segmentMeals).forEach(mealArray => {
          if (Array.isArray(mealArray)) {
            mealArray.forEach(meal => {
              if (meal && typeof meal === 'object') {
                const price = meal.sale_price ?? meal.price ?? 0;
                total += (parseFloat(price) || 0);
              }
            });
          }
        });
      });
      return total;
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

    departBaseFare(state) {
      if (state.tripType === 'multi_city' || state.tripType === 'multi-city') {
        return state.multiCitySegments[0]?.selectedFlight?.price || 0;
      }
      return state.selectedOutbound?.price || 0;
    },

    returnBaseFare(state) {
      if (state.tripType === 'round_trip' || state.tripType === 'round-trip') {
        return state.selectedReturn?.price || 0;
      }
      return 0;
    },

    grandTotalForAdults(state) {
      const base = this.combinedBasePrice;
      let total = 0;

      const adults = state.passengers.filter(p => p.type === 'Adult');

      // If passengers list is empty, fallback to simple multiplication
      if (adults.length === 0) {
        const count = state.passengerCount.adults || 0;
        return base * count;
      }

      adults.forEach(adult => {
        // Apply 20% discount for Senior Citizens and PWDs on base fare
        if (adult.phDiscountType === 'senior' || adult.phDiscountType === 'pwd') {
          total += base * 0.8;
        } else {
          total += base;
        }
      });

      return total;
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

    // Total Base Fare for all passengers EXACTLY AS DISPLAYED IN SUBTOTAL (WITH DISCOUNTS)
    combinedBasePriceTotal(state) {
      return (this.grandTotalForAdults || 0) + (this.grandTotalForChildren || 0) + (this.grandTotalForInfants || 0);
    },

    // Standard 12% tax applied ONLY to taxable Base Fare 
    // Senior/PWD base fares are VAT EXEMPT in the Philippines
    // Also includes Terminal Fee (DPSC) of ₱200/segment per pax
    totalTaxes(state) {
      const base = parseFloat(this.combinedBasePrice) || 0;
      let taxableBaseTotal = 0;

      // Calculate taxable base fare (Seniors and PWDs are VAT-exempt in the Philippines)
      if (state.passengers && state.passengers.length > 0) {
        state.passengers.forEach(p => {
          if (p.type === 'Infant') {
            if (p.phDiscountType !== 'senior' && p.phDiscountType !== 'pwd') {
              taxableBaseTotal += (base * 0.5);
            }
          } else {
            if (p.phDiscountType !== 'senior' && p.phDiscountType !== 'pwd') {
              taxableBaseTotal += base;
            }
          }
        });
      } else {
        // Fallback: Use counts if passenger objects are not yet created
        const { adults = 0, children = 0, infants = 0 } = state.passengerCount || {};
        taxableBaseTotal = (base * adults) + (base * children) + ((base * 0.5) * infants);
      }

      const baseVat = taxableBaseTotal * 0.12;

      // Addons are also taxable (12% VAT)
      const addonsVat = (this.totalAddonsPrice || 0) * 0.12;

      // Terminal Fee (DPSC) - ₱200 per segment per paying passenger (Adult/Child)
      const activeSegmentsCount = (this.allSegments || []).length;
      const payingPaxCount = (parseInt(state.passengerCount?.adults) || 0) + (parseInt(state.passengerCount?.children) || 0);
      const terminalFees = activeSegmentsCount * payingPaxCount * 200;

      return baseVat + addonsVat + terminalFees;
    },

    // Total for all selected add-ons (Active segments only)
    totalAddonsPrice(state) {
      return (this.totalBaggagePrice || 0) + (this.totalMealsPrice || 0) + (this.totalSeatsPrice || 0) + (this.totalAssistancePrice || 0);
    },

    // Insurance price (per passenger: Adult + Child)
    insurancePrice(state) {
      const perPerson = parseFloat(state.addons?.insurance?.price) || 0;
      const count = (state.passengerCount.adults || 0) + (state.passengerCount.children || 0);
      return perPerson * count;
    },

    // Assistance price (active segments only)
    totalAssistancePrice(state) {
      let total = 0;
      const wheelchairData = state.addons.wheelchair || {};

      Object.keys(wheelchairData).forEach(segKey => {
        const segmentAssistance = wheelchairData[segKey] || {};
        Object.values(segmentAssistance).forEach(assistance => {
          if (assistance && typeof assistance === 'object' && assistance.price) {
            total += parseFloat(assistance.price) || 0;
          }
        });
      });
      return total;
    },

    // Final aggregated amount (Rounded UP)
    grandTotal(state) {
      const bPrice = parseFloat(this.combinedBasePriceTotal) || 0;
      const aPrice = parseFloat(this.totalAddonsPrice) || 0;
      const iPrice = parseFloat(this.insurancePrice) || 0;
      const tPrice = parseFloat(this.totalTaxes) || 0;

      const rawTotal = bPrice + aPrice + iPrice + tPrice;
      return Math.ceil(rawTotal);
    },

    // Authoritative Taxes (includes priorities)
    authoritativeTaxes(state) {
      if (state.backendBreakdown?.breakdown?.taxes !== undefined) {
        return parseFloat(state.backendBreakdown.breakdown.taxes);
      }
      if (state.backendBreakdown?.taxes !== undefined) {
        return parseFloat(state.backendBreakdown.taxes);
      }
      return this.totalTaxes || 0;
    },

    // Authoritative Base Fare
    authoritativeBaseFare(state) {
      if (state.backendBreakdown?.breakdown?.base_fare !== undefined) {
        return parseFloat(state.backendBreakdown.breakdown.base_fare);
      }
      if (state.backendBreakdown?.base_fare !== undefined) {
        return parseFloat(state.backendBreakdown.base_fare);
      }
      return this.combinedBasePriceTotal || 0;
    },

    // Authoritative Adult Base
    authoritativeAdultBase(state) {
      if (state.backendBreakdown?.breakdown?.adult_base !== undefined) {
        return parseFloat(state.backendBreakdown.breakdown.adult_base);
      }
      if (state.backendBreakdown?.adult_base !== undefined) {
        return parseFloat(state.backendBreakdown.adult_base);
      }
      return this.grandTotalForAdults || 0;
    },

    // Authoritative Child Base
    authoritativeChildBase(state) {
      if (state.backendBreakdown?.breakdown?.child_base !== undefined) {
        return parseFloat(state.backendBreakdown.breakdown.child_base);
      }
      if (state.backendBreakdown?.child_base !== undefined) {
        return parseFloat(state.backendBreakdown.child_base);
      }
      return this.grandTotalForChildren || 0;
    },

    // Authoritative Infant Base
    authoritativeInfantBase(state) {
      if (state.backendBreakdown?.breakdown?.infant_base !== undefined) {
        return parseFloat(state.backendBreakdown.breakdown.infant_base);
      }
      if (state.backendBreakdown?.infant_base !== undefined) {
        return parseFloat(state.backendBreakdown.infant_base);
      }
      return this.grandTotalForInfants || 0;
    },

    // Authoritative Addons
    authoritativeAddons(state) {
      if (state.backendBreakdown?.breakdown?.addons !== undefined) {
        return parseFloat(state.backendBreakdown.breakdown.addons);
      }
      if (state.backendBreakdown?.addons !== undefined) {
        return parseFloat(state.backendBreakdown.addons);
      }
      return this.totalAddonsPrice || 0;
    },

    // Authoritative Seats
    authoritativeSeats(state) {
      if (state.backendBreakdown?.breakdown?.seats !== undefined) {
        return parseFloat(state.backendBreakdown.breakdown.seats);
      }
      return this.totalSeatsPrice || 0;
    },

    // Authoritative Baggage
    authoritativeBaggage(state) {
      if (state.backendBreakdown?.breakdown?.baggage !== undefined) {
        return parseFloat(state.backendBreakdown.breakdown.baggage);
      }
      return this.totalBaggagePrice || 0;
    },

    // Authoritative Meals
    authoritativeMeals(state) {
      if (state.backendBreakdown?.breakdown?.meals !== undefined) {
        return parseFloat(state.backendBreakdown.breakdown.meals);
      }
      return this.totalMealsPrice || 0;
    },

    // Authoritative Assistance
    authoritativeAssistance(state) {
      if (state.backendBreakdown?.breakdown?.assistance !== undefined) {
        return parseFloat(state.backendBreakdown.breakdown.assistance);
      }
      return this.totalAssistancePrice || 0;
    },

    // Authoritative Insurance
    authoritativeInsurance(state) {
      if (state.backendBreakdown?.breakdown?.insurance !== undefined) {
        return parseFloat(state.backendBreakdown.breakdown.insurance);
      }
      if (state.backendBreakdown?.insurance !== undefined) {
        return parseFloat(state.backendBreakdown.insurance);
      }
      return this.insurancePrice || 0;
    },

    // Authoritative Grand Total (The "Payable" Amount)
    authoritativeTotal(state) {
      // Priority 1: Confirmed backend total (Finalized after create-booking)
      if (state.booking_total > 0) {
        return state.booking_total;
      }
      // Priority 2: Estimated backend total (from Review page calculate-price)
      if (state.backendBreakdown?.total_amount !== undefined) {
        return parseFloat(state.backendBreakdown.total_amount);
      }
      if (state.backendBreakdown?.breakdown?.grand_total !== undefined) {
        return parseFloat(state.backendBreakdown.breakdown.grand_total);
      }
      // Priority 3: Frontend Estimate Fallback
      const baseTotal = this.authoritativeBaseFare || 0;
      const addonsTotal = this.authoritativeAddons || 0;
      const insuranceTotal = this.authoritativeInsurance || 0;
      const taxesTotal = this.authoritativeTaxes || 0;
      return Math.ceil(baseTotal + addonsTotal + insuranceTotal + taxesTotal);
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
      const expiry = state.activityExpiresAt ? new Date(state.activityExpiresAt).getTime() : state.sessionExpiry;
      if (!expiry) return '00:00';
      const diff = Math.max(0, Math.round((expiry - state.currentTime) / 1000));
      const mins = Math.floor(diff / 60);
      const secs = diff % 60;
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    },

    secondsLeft(state) {
      const expiry = state.activityExpiresAt ? new Date(state.activityExpiresAt).getTime() : state.sessionExpiry;
      if (!expiry) return 0;
      return Math.max(0, Math.round((expiry - state.currentTime) / 1000));
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

    // NEW: Get the date of the last flight segment for document validation
    lastTravelDate(state) {
      const segments = this.allSegments;
      if (segments.length === 0) return null;
      const lastSeg = segments[segments.length - 1];
      return lastSeg.selectedFlight?.departure_time || null;
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
      if (this.activityExpiresAt) {
        this.sessionExpiry = new Date(this.activityExpiresAt).getTime();
        console.log(`🔄 Activity Session started, strictly tied to instructor limits. Expires at:`, new Date(this.sessionExpiry).toLocaleString());
      } else {
        const expiryMinutes = (this.isPractice || this.activityCode) ? 30 : 15;
        this.sessionExpiry = Date.now() + (expiryMinutes * 60 * 1000);
        console.log(`🔄 Standard Session started (${expiryMinutes}m), expires at:`, new Date(this.sessionExpiry).toLocaleString());
      }
      this.isFreshSession = true;

      setTimeout(() => {
        this.isFreshSession = false;
      }, 1000);
    },

    checkSession() {
      // Update reactive timestamp
      this.currentTime = Date.now();

      const expiryTime = this.activityExpiresAt ? new Date(this.activityExpiresAt).getTime() : this.sessionExpiry;

      if (!expiryTime) {
        if (!this.sessionExpiry && !this.activityExpiresAt) {
          console.log('❌ No active session or activity found');
          this.resetBooking();
          return { valid: false, reason: 'No active session', expired: true };
        }
        return { valid: true };
      }

      const timeLeft = expiryTime - this.currentTime;
      const minutesLeft = Math.floor(timeLeft / (60 * 1000));
      const secondsLeftValue = Math.floor((timeLeft % (60 * 1000)) / 1000);

      if (timeLeft <= 0) {
        const type = this.activityExpiresAt ? 'Activity' : 'Session';
        console.log(`⏰ ${type} expired`);
        return {
          valid: false,
          reason: `${type} expired`,
          expired: true
        };
      }

      return {
        valid: true,
        timeLeft,
        minutesLeft,
        secondsLeft: secondsLeftValue,
        expiresAt: new Date(expiryTime).toLocaleString()
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
      this.passengerCount.adults = counts.adult !== undefined ? counts.adult : (counts.adults || 1);
      this.passengerCount.children = counts.children !== undefined ? counts.children : 0;
      this.passengerCount.infants = counts.infant !== undefined ? counts.infant : (counts.infants || 0);
    },

    // Activity Code & Practice Mode Actions
    setActivityCode(code, activityData = null) {
      this.activityCode = code;
      if (activityData && activityData.id) {
        this.activityId = activityData.id;
        this.activityExpiresAt = activityData.expires_at || null;
        console.log('🆔 Activity info stored in booking store:', {
          id: this.activityId,
          expires: this.activityExpiresAt
        });
      }
      this.isPractice = false;
      this.hasActivityCodeValidation = true;
      this.startSession();
      console.log('✅ Activity code set:', code);
    },

    setPracticeMode() {
      this.activityCode = null;
      this.activityId = null;
      this.activityExpiresAt = null;
      this.isPractice = true;
      this.hasActivityCodeValidation = true;
      this.startSession();
      console.log('✅ Practice mode enabled');
    },

    clearActivityCodeValidation() {
      this.activityCode = null;
      this.activityId = null;
      this.activityExpiresAt = null;
      this.isPractice = false;
      this.hasActivityCodeValidation = false;
      console.log('🔄 Activity code validation cleared');
    },

    async failActivity() {
      if (this.activityId && !this.isPractice) {
        try {
          const result = await bookingService.failActivity(this.activityId);
          console.log('⏰ Activity failed via API:', result);
          return result;
        } catch (error) {
          console.error('❌ Error calling failActivity API:', error);
        }
      }
      return { success: false };
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

    setStopPreference(pref) {
      console.log('🛑 Setting stop preference in Pinia:', pref);
      this.stopPreference = pref;
      this.nonStopOnly = (pref === 'nonstop');
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
          seat_class_features: flight.seat_class_features,
          fare_family: flight.fare_family || 'basic'
        };

        this.multiCitySegments[index].selectedFlight = {
          ...flight,
          ...seatClassInfo,
          class_type: flight.class_type || flight.selected_seat_class || flight.seat_class || 'Economy'
        };

        // Store fare family code and branded name for this segment
        this.fareFamilies[index.toString()] = flight.fare_family || 'basic';
        this.fareFamilyNames[index.toString()] = flight.fare_family_name || flight.name || '';

        console.log(`✅ Flight selected for segment ${index}:`, flight.flight_number, '| Fare:', flight.fare_family);
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
        seat_class_features: flight.seat_class_features,
        fare_family: flight.fare_family || 'basic'
      };

      const flightWithSeatClass = {
        ...flight,
        ...seatClassInfo,
        price: flight.price,
        class_type: flight.class_type || flight.selected_seat_class || flight.seat_class || 'Economy'
      };

      const segKey = type === 'outbound' ? 'depart' : 'return';
      this.fareFamilies[segKey] = flight.fare_family || 'basic';
      this.fareFamilyNames[segKey] = flight.fare_family_name || flight.name || '';

      if (type === 'outbound') {
        this.selectedOutbound = flightWithSeatClass;
        console.log('✅ Outbound flight selected with seat class:', {
          flight: flight.flight_number,
          seat_class: flight.selected_seat_class,
          fare_family: flight.fare_family,
          price: flight.price
        });
      } else {
        if (this.tripType === 'round_trip') {
          this.selectedReturn = flightWithSeatClass;
          console.log('✅ Return flight selected with seat class:', {
            flight: flight.flight_number,
            seat_class: flight.selected_seat_class,
            fare_family: flight.fare_family,
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
          title: passenger.title || (passenger.type === 'Infant' ? 'INF' : passenger.type === 'Child' ? 'CHD' : 'MR'),
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

      // Initialize as array if not already
      if (!Array.isArray(this.addons.meals[segment][passengerKey])) {
        this.addons.meals[segment][passengerKey] = [];
      }

      // Check if meal already exists (to avoid exact duplicates)
      const existingIdx = this.addons.meals[segment][passengerKey].findIndex(m => m.id === mealData.id);
      if (existingIdx === -1) {
        this.addons.meals[segment][passengerKey].push(mealData);
        console.log(`🍽️ Meal added for ${segment}:`, mealData.name);
      } else {
        console.log(`🍽️ Meal ${mealData.name} already selected.`);
      }
    },

    removeMealAddon(passengerKey, mealId, segment = 'depart') {
      if (this.addons.meals[segment] && Array.isArray(this.addons.meals[segment][passengerKey])) {
        const idx = this.addons.meals[segment][passengerKey].findIndex(m => m.id === mealId);
        if (idx !== -1) {
          const removed = this.addons.meals[segment][passengerKey].splice(idx, 1);
          console.log(`❌ Meal removed for ${segment}:`, removed[0].name);
        }
      }
    },

    clearMealsForPassenger(passengerKey, segment = 'depart') {
      if (this.addons.meals[segment]) {
        this.addons.meals[segment][passengerKey] = [];
      }
    },

    // Assistance methods
    updateAssistanceAddon(passengerKey, assistanceObj, segment = 'depart') {
      if (!this.addons.wheelchair[segment]) {
        this.addons.wheelchair[segment] = {};
      }
      this.addons.wheelchair[segment][passengerKey] = assistanceObj;
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

    // Copy seats from depart to return with server-side locking
    async copySeatsToReturn() {
      if (!this.isRoundTrip) return { success: true };

      console.log('📋 Copying seats from depart to return segment & locking on server');
      const departSeats = this.addons.seats.depart || {};
      const returnSeats = JSON.parse(JSON.stringify(departSeats));
      const sessionId = this.bookingSessionId;
      const returnScheduleId = this.selectedReturn?.id;

      if (!returnScheduleId) {
        console.error('❌ Cannot copy seats: No return flight selected');
        return { success: false, error: 'No return flight selected' };
      }

      const results = [];
      const passengerKeys = Object.keys(returnSeats);

      for (const passengerKey of passengerKeys) {
        const seat = returnSeats[passengerKey];
        if (seat && seat.id) {
          // Attempt to lock this seat for the return flight
          // NOTE: In a real system, the 'seat.id' for the departure flight 
          // might not be the same ID for the return flight even if it's the 
          // same physical plane. However, the frontend logic seems to assume 
          // seat objects are mapped. 
          // CRITICAL: We need to find the seat ID in the RETURN flight map that 
          // matches the seat_code from the departure flight.

          try {
            // First, find the matching seat in the return flight
            const res = await seatService.getSeatsBySchedule(returnScheduleId, sessionId);
            if (res.success) {
              const matchingSeat = res.seats.find(s => s.seat_code === seat.seat_code);
              if (matchingSeat && matchingSeat.is_available) {
                const lockRes = await seatService.lockSeat(matchingSeat.id, sessionId);
                if (lockRes.success) {
                  returnSeats[passengerKey] = {
                    ...seat,
                    id: matchingSeat.id,
                    flight_segment: 'return',
                    schedule_id: returnScheduleId,
                    locked_until: lockRes.locked_until
                  };
                  results.push({ passengerKey, success: true });
                } else {
                  console.warn(`⚠️ Could not lock seat ${seat.seat_code} for return:`, lockRes.error);
                  delete returnSeats[passengerKey];
                  results.push({ passengerKey, success: false, error: lockRes.error });
                }
              } else {
                console.warn(`⚠️ Seat ${seat.seat_code} not available or not found in return flight`);
                delete returnSeats[passengerKey];
                results.push({ passengerKey, success: false, error: 'Seat not available' });
              }
            }
          } catch (err) {
            console.error(`❌ Error copying seat for ${passengerKey}:`, err);
            delete returnSeats[passengerKey];
          }
        }
      }

      this.addons.seats.return = returnSeats;
      return {
        success: results.every(r => r.success),
        results
      };
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

    // Clear seats for a specific segment with server-side unlocking
    async clearSeatsForSegment(segment = 'depart') {
      const seatsToUnlock = this.addons.seats[segment] || {};
      const sessionId = this.bookingSessionId;

      console.log(`🧹 Clearing and unlocking all seats for ${segment} flight`);

      const unlockPromises = Object.values(seatsToUnlock)
        .filter(seat => seat && seat.id)
        .map(seat => seatService.unlockSeat(seat.id, sessionId));

      // We don't necessarily need to wait for all to finish if we want to be fast,
      // but for reliability we'll await them all.
      await Promise.allSettled(unlockPromises);

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

      // Force update backendBreakdown total to match confirmed total if they differ
      if (this.backendBreakdown && this.backendBreakdown.total_amount !== this.booking_total) {
        console.log('🔄 Syncing backendBreakdown total with confirmed total:', this.booking_total);
        this.backendBreakdown.total_amount = this.booking_total;
      }

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

    setBackendBreakdown(response) {
      // If full response object is passed (with success, total_amount, breakdown, etc)
      if (response && response.breakdown) {
        this.backendBreakdown = response;
        if (response.tax_details) {
          this.backendTaxDetails = response.tax_details;
        }
      } else {
        // Fallback for simple breakdown object
        this.backendBreakdown = response;
      }
      console.log('📊 Authoritative backend breakdown stored');
    },

    // UPDATED: Reset booking with optional session preservation
    resetBooking(clearSession = true) {
      console.log(`🧹 Resetting booking store (clearSession: ${clearSession})`);

      // Preserve activity session data if requested
      const preservedData = clearSession ? {} : {
        activityCode: this.activityCode,
        isPractice: this.isPractice,
        hasActivityCodeValidation: this.hasActivityCodeValidation,
        activityId: this.activityId,
        activityExpiresAt: this.activityExpiresAt,
        activityTimeLimitMinutes: this.activityTimeLimitMinutes,
      };

      const keysToRemove = [
        'current_booking_id',
        'current_booking_reference',
        'current_booking_total',
        'current_booking_status',
        'booking_session_id',
        'payment_session',
        'booking',
        'current_booking',
        'last_booking_ref',
        ...Array.from({ length: 10 }, (_, i) => `pax_${i + 1}`),
        ...Array.from({ length: 15 }, (_, i) => `passenger_${i + 1}_details`),
      ];

      keysToRemove.forEach(key => {
        try {
          localStorage.removeItem(key);
        } catch (error) {
          console.warn(`Could not remove ${key}:`, error);
        }
      });

      try {
        sessionStorage.clear();
      } catch (error) {
        console.warn('Could not clear sessionStorage:', error);
      }

      const newSessionId = `sess_${Math.random().toString(36).substr(2, 9)}_${Date.now()}`;
      localStorage.setItem('booking_session_id', newSessionId);

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
        // Preserve or reset activity session
        activityCode: clearSession ? null : preservedData.activityCode,
        isPractice: clearSession ? false : preservedData.isPractice,
        hasActivityCodeValidation: clearSession ? false : preservedData.hasActivityCodeValidation,
        activityId: clearSession ? null : preservedData.activityId,
        activityExpiresAt: clearSession ? null : preservedData.activityExpiresAt,
        activityTimeLimitMinutes: clearSession ? null : preservedData.activityTimeLimitMinutes,
        
        sessionExpiry: null,
        isFreshSession: true,
        bookingSessionId: newSessionId,
        fareFamilies: {
          depart: 'basic',
          return: 'basic'
        },
        fareFamilyNames: {
          depart: '',
          return: ''
        },
        nonStopOnly: false,
        stopPreference: 'all',
        backendBreakdown: null,
        backendTaxDetails: null
      });

      console.log(`✅ Booking Store has been ${clearSession ? 'completely' : 'partially'} reset.`);
    },

    forceCompleteReset() {
      console.log('💥 FORCE RESETTING ALL STORAGE...');

      Object.keys(localStorage).forEach(key => {
        if (
          key !== 'booking-store' && (
            key.includes('booking') ||
            key.includes('pax') ||
            key.includes('flight') ||
            key.includes('pinia') ||
            key.includes('session')
          )
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
    },

    // Insurance Actions
    selectInsurancePlan(planId, price) {
      console.log('🛡️ Insurance Plan Selected:', planId, price);
      this.addons.insurance = {
        id: planId, // Added id field for backwards compatibility with some views
        selectedPlanId: planId,
        price: parseFloat(price) || 0
      };
    },

    clearInsurance() {
      console.log('🛡️ Insurance Cleared');
      this.addons.insurance = {
        id: null,
        selectedPlanId: null,
        price: 0
      };
    }
  }
});