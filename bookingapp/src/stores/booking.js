import { defineStore } from 'pinia';

export const useBookingStore = defineStore('booking', {
  state: () => ({
    booking_id: localStorage.getItem('current_booking_id') || null,
    booking_reference: null,
    booking_status: null,
    booking_total: 0,
    selectedOutbound: null,
    selectedReturn: null,
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

    // UPDATED: Seats now support depart and return segments
    addons: {
      baggage: {
        depart: {},  // { passengerKey: baggageObject }
        return: {}   // { passengerKey: baggageObject }
      },
      meals: {
        depart: {},  // { passengerKey: mealObject }
        return: {}   // { passengerKey: mealObject }
      },
      wheelchair: {
        depart: {},  // { passengerKey: assistanceId }
        return: {}   // { passengerKey: assistanceId }
      },
      seats: {       // UPDATED: Now supports segments
        depart: {},  // { passengerKey: seatObject }
        return: {}   // { passengerKey: seatObject }
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
    isRoundTrip: (state) => state.tripType === 'round-trip',

    payingPassengerCount: (state) => {
      const { adults = 0, children = 0 } = state.passengerCount || {};
      return adults + children;
    },

    departBaseFare: (state) => {
      const outboundPrice = parseFloat(state.selectedOutbound?.price) || 0;
      return outboundPrice * ((state.passengerCount?.adults || 0) + (state.passengerCount?.children || 0));
    },

    returnBaseFare: (state) => {
      if (!state.selectedReturn) return 0;
      const returnPrice = parseFloat(state.selectedReturn?.price) || 0;
      return returnPrice * ((state.passengerCount?.adults || 0) + (state.passengerCount?.children || 0));
    },

    totalSeatsPrice: (state) => {
      const seats = state.addons?.seats || {};
      let total = 0;
      // Iterate over depart and return segments
      for (const segmentKey in seats) {
        if (Object.prototype.hasOwnProperty.call(seats, segmentKey)) {
          const segmentSeats = seats[segmentKey];
          Object.values(segmentSeats).forEach(seat => {
            if (seat && seat.seat_price !== undefined) {
              total += (parseFloat(seat.seat_price) || 0);
            }
          });
        }
      }
      return total;
    },

    totalBaggagePrice: (state) => {
      let total = 0;
      const segments = state.tripType === 'round_trip' ? ['depart', 'return'] : ['depart'];
      segments.forEach(segment => {
        const baggage = state.addons?.baggage?.[segment] || {};
        Object.values(baggage).forEach(baggageItem => {
          if (!baggageItem) return;
          if (typeof baggageItem === 'object' && baggageItem.price !== undefined) {
            total += (parseFloat(baggageItem.price) || 0);
          }
          // Note: If baggageItem is just an ID, we'd need baggageOptions which are in the component.
          // However, for the Review page, they are often objects if already selected.
        });
      });
      return total;
    },

    totalMealsPrice: (state) => {
      let total = 0;
      const segments = state.tripType === 'round_trip' ? ['depart', 'return'] : ['depart'];
      segments.forEach(segment => {
        const meals = state.addons?.meals?.[segment] || {};
        Object.values(meals).forEach(meal => {
          if (!meal) return;
          if (typeof meal === 'object' && meal.price !== undefined) {
            total += (parseFloat(meal.price) || 0);
          }
        });
      });
      return total;
    },

    totalAssistancePrice: (state) => {
      // This getter might still need option lists to be authoritative if only IDs are stored,
      // but if objects are stored it works.
      return 0; // Fallback or handle separately
    },

    calculatedGrandTotal: (state) => {
      // Prioritize backend-calculated total if available in state
      if (state.booking_total) return parseFloat(state.booking_total);

      const outboundPrice = parseFloat(state.selectedOutbound?.price) || 0;
      const returnPrice = state.selectedReturn ? parseFloat(state.selectedReturn?.price) : 0;
      const paxCount = (state.passengerCount?.adults || 0) + (state.passengerCount?.children || 0);

      const baseFare = (outboundPrice + returnPrice) * paxCount;

      // Calculate add-ons from state
      let addonsTotal = 0;

      // Seats
      const seats = state.addons?.seats || {};
      for (const segmentKey in seats) {
        if (Object.prototype.hasOwnProperty.call(seats, segmentKey)) {
          const segmentSeats = seats[segmentKey];
          addonsTotal += Object.values(segmentSeats).reduce((sum, s) => sum + (parseFloat(s?.seat_price) || 0), 0);
        }
      }

      // Baggage, Meals, Wheelchair (Assuming objects with price are stored)
      const segments = state.tripType === 'round_trip' ? ['depart', 'return'] : ['depart'];
      segments.forEach(seg => {
        ['baggage', 'meals', 'wheelchair'].forEach(type => {
          const items = state.addons?.[type]?.[seg] || {};
          Object.values(items).forEach(item => {
            if (typeof item === 'object' && item?.price) {
              addonsTotal += parseFloat(item.price);
            }
          });
        });
      });

      return baseFare + addonsTotal;
    },
    isOneWay: (state) => state.tripType === 'one_way',

    adultPassengers: (state) => {
      return state.passengers.filter(p => p.type === 'Adult');
    },

    allInfantsAssigned: (state) => {
      const infants = state.passengers.filter(p => p.type === 'Infant');
      if (infants.length === 0) return true;

      return infants.every(infant => state.infantAdultMapping[infant.key]);
    },

    infantAssignmentValid: (state) => {
      const infants = state.passengers.filter(p => p.type === 'Infant');
      const adults = state.passengers.filter(p => p.type === 'Adult');

      if (!infants.every(infant => state.infantAdultMapping[infant.key])) {
        return false;
      }

      const infantCountPerAdult = {};
      Object.values(state.infantAdultMapping).forEach(adultKey => {
        infantCountPerAdult[adultKey] = (infantCountPerAdult[adultKey] || 0) + 1;
      });

      return Object.values(infantCountPerAdult).every(count => count <= 1);
    },

    combinedBasePrice: (state) => {
      const outbound = parseFloat(state.selectedOutbound?.price || 0);
      const returnPrice = state.tripType === 'round_trip' ? parseFloat(state.selectedReturn?.price || 0) : 0;
      return outbound + returnPrice;
    },

    grandTotalForAdults(state) {
      return this.combinedBasePrice * state.passengerCount.adults;
    },

    grandTotalForChildren(state) {
      return this.combinedBasePrice * state.passengerCount.children;
    },

    grandTotalForInfants(state) {
      return (this.combinedBasePrice * 0.5) * state.passengerCount.infants;
    },

    // UPDATED: Grand total calculation with segmented seats
    grandTotal: (state) => {
      let total = 0;

      // 1. Base Flight Prices
      if (state.selectedOutbound?.price) {
        total += parseFloat(state.selectedOutbound.price);
      }

      if (state.tripType === 'round_trip' && state.selectedReturn?.price) {
        total += parseFloat(state.selectedReturn.price);
      }

      // Multiply by number of paying passengers (adults + children)
      const travelerCount = (state.passengerCount.adults || 0) + (state.passengerCount.children || 0);
      total = total * travelerCount;

      // 2. Add Baggage (depart + return for round trips)
      const baggageSegments = state.tripType === 'round_trip' ? ['depart', 'return'] : ['depart'];
      baggageSegments.forEach(segment => {
        Object.values(state.addons.baggage[segment] || {}).forEach(item => {
          if (item?.price) total += parseFloat(item.price);
        });
      });

      // 3. Add Meals (depart + return for round trips)
      baggageSegments.forEach(segment => {
        Object.values(state.addons.meals[segment] || {}).forEach(item => {
          if (item?.price) total += parseFloat(item.price);
        });
      });

      // 4. Add Assistance (depart + return for round trips)
      baggageSegments.forEach(segment => {
        Object.values(state.addons.wheelchair[segment] || {}).forEach(serviceId => {
          // Assistance services are free, but if they had price:
          // const service = findServiceById(serviceId);
          // if (service?.price) total += parseFloat(service.price);
        });
      });

      // 5. Add Seats (UPDATED: Include both segments for round trips)
      const seatSegments = state.tripType === 'round_trip' ? ['depart', 'return'] : ['depart'];
      seatSegments.forEach(segment => {
        Object.values(state.addons.seats[segment] || {}).forEach(seat => {
          if (seat?.seat_price) {
            total += parseFloat(seat.seat_price);
            console.log(`📊 Adding seat price for ${segment}: ₱${seat.seat_price} for seat ${seat.seat_code}`);
          }
        });
      });

      return total;
    },

    isFlightSelectionComplete: (state) => {
      if (state.tripType === 'one_way') {
        return state.selectedOutbound !== null;
      } else if (state.tripType === 'round_trip') {
        return state.selectedOutbound !== null && state.selectedReturn !== null;
      }
      return false;
    },

    // UPDATED: Helper to get total add-ons price with segmented seats
    totalAddonsPrice: (state) => {
      let total = 0;
      const segments = state.tripType === 'round_trip' ? ['depart', 'return'] : ['depart'];

      // Baggage
      segments.forEach(segment => {
        Object.values(state.addons.baggage[segment] || {}).forEach(item => {
          if (item?.price) total += parseFloat(item.price);
        });
      });

      // Meals
      segments.forEach(segment => {
        Object.values(state.addons.meals[segment] || {}).forEach(item => {
          if (item?.price) total += parseFloat(item.price);
        });
      });

      // Seats (UPDATED: Include both segments)
      segments.forEach(segment => {
        Object.values(state.addons.seats[segment] || {}).forEach(seat => {
          if (seat?.seat_price) {
            total += parseFloat(seat.seat_price);
            console.log(`📊 Adding seat price to totalAddonsPrice for ${segment}: ₱${seat.seat_price} for seat ${seat.seat_code}`);
          }
        });
      });

      return total;
    },

    isSessionValid: (state) => {
      if (!state.sessionExpiry) return false;
      return Date.now() < state.sessionExpiry;
    },

    // NEW: Get seats by segment
    getSeatsBySegment: (state) => (segment = 'depart') => {
      return state.addons.seats[segment] || {};
    },

    // NEW: Check if all passengers have seats for a segment
    allPassengersHaveSeatsForSegment: (state) => (segment = 'depart') => {
      const segmentSeats = state.addons.seats[segment] || {};
      return state.passengers.every(p => segmentSeats[p.key]);
    },

    // NEW: Check if all passengers have seats for all segments
    allPassengersHaveAllSeats: (state) => {
      if (!state.isRoundTrip) {
        return state.passengers.every(p => state.addons.seats.depart?.[p.key]);
      } else {
        return state.passengers.every(p =>
          state.addons.seats.depart?.[p.key] &&
          state.addons.seats.return?.[p.key]
        );
      }
    },

    // NEW: Check if session should be cleared for home page
    shouldClearSessionForHome: (state) => {
      const sessionValid = state.isSessionValid;
      const hasBookingData = state.passengers.length > 0 || state.selectedOutbound || state.booking_id;

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
          this.booking_reference = savedBooking.reference || `CSUCC${String(savedBooking.id).padStart(8, '0')}`;
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
        baggage: addonData.baggage || { depart: {}, return: {} },
        meals: addonData.meals || { depart: {}, return: {} },
        wheelchair: addonData.wheelchair || { depart: {}, return: {} },
        seats: addonData.seats || { depart: {}, return: {} }
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

    // Clear all addons
    clearAllAddons() {
      this.addons = {
        baggage: { depart: {}, return: {} },
        meals: { depart: {}, return: {} },
        wheelchair: { depart: {}, return: {} },
        seats: { depart: {}, return: {} }
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

    saveBookingConfirmation(bookingData) {
      console.log('💾 Saving booking confirmation to store:', bookingData);

      this.booking_id = bookingData.booking_id;
      this.booking_reference = bookingData.booking_reference || `CSUCC${String(bookingData.booking_id).padStart(8, '0')}`;
      this.booking_status = bookingData.status || 'pending';
      this.booking_total = this.grandTotal || parseFloat(bookingData.total_amount) || 0;
      this.sessionExpiry = Date.now() + (30 * 60 * 1000);

      localStorage.setItem('current_booking_id', this.booking_id);

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
          baggage: {
            depart: {},
            return: {}
          },
          meals: {
            depart: {},
            return: {}
          },
          wheelchair: {
            depart: {},
            return: {}
          },
          seats: {
            depart: {},
            return: {}
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
        ...Array.from({ length: 10 }, (_, i) => `pax_${i + 1}`),
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