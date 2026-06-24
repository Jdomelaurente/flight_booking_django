// src/services/bookingService.js
import api from './api'

export const bookingService = {
  async createBooking(bookingData) {
    try {
      console.log('📤 Sending booking data:', JSON.stringify(bookingData, null, 2))
      const response = await api.post('flightapp/create-booking/', bookingData)
      console.log('✅ API Response:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ Error creating booking:', error.response?.data || error.message)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to create booking'
      }
    }
  },

  async updateBooking(bookingId, bookingData) {
    try {
      console.log(`🔄 Updating existing booking ID: ${bookingId}`)
      console.log('📤 Update data:', JSON.stringify(bookingData, null, 2))

      // Use PATCH to update the booking
      const response = await api.patch(`flightapp/update-booking/${bookingId}/`, bookingData)
      console.log('✅ Update API Response:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ Error updating booking:', error.response?.data || error.message)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to update booking'
      };
    }
  },

  async processPayment(paymentData) {
    try {
      const response = await api.post('flightapp/process-payment/', paymentData)
      return response.data
    } catch (error) {
      console.error('Error processing payment:', error.response?.data || error.message)
      throw error
    }
  },

  async getBookingDetails(bookingId) {
    try {
      const response = await api.get(`flightapp/booking/${bookingId}/`)
      return response.data
    } catch (error) {
      console.error('Error fetching booking details:', error)
      throw error
    }
  },

  formatBookingData(bookingStore) {
    console.log('🔍 Formatting booking data from store...')
    console.log('Store trip type:', bookingStore.tripType)
    console.log('Is round trip:', bookingStore.isRoundTrip)
    console.log('Store addons structure:', bookingStore.addons)

    // Ensure store is in new format
    if (bookingStore.migrateAddonsToNewFormat) {
      bookingStore.migrateAddonsToNewFormat();
    }

    // Format passengers
    const formattedPassengers = bookingStore.passengers.map(p => ({
      first_name: p.firstName || '',
      last_name: p.lastName || '',
      middle_name: p.middleName || '',
      title: p.title || 'MR',
      date_of_birth: p.dateOfBirth || this.getDefaultDOB(),
      nationality: p.nationality || 'Philippines',
      passport_number: p.passportNumber || '',
      ph_discount_type: p.phDiscountType || 'none',
      ph_discount_id: p.phDiscountId || '',
      type: p.type || 'Adult',
      associated_adult: p.associatedAdult || null,
      key: p.key || `pax_${Math.random().toString(36).substr(2, 9)}`
    }))

    console.log('Formatted passengers:', formattedPassengers.length, 'passengers')

    // Contact info
    const contactInfo = {
      title: bookingStore.contactInfo?.title || 'MR',
      firstName: bookingStore.contactInfo?.firstName || '',
      lastName: bookingStore.contactInfo?.lastName || '',
      email: bookingStore.contactInfo?.email || '',
      phone: bookingStore.contactInfo?.phone || '',
      middleName: bookingStore.contactInfo?.middleName || ''
    }

    console.log('Formatted contact info:', contactInfo)

    // Format addons with new depart/return structure
    const formattedAddons = {
      baggage: {},
      meals: {},
      wheelchair: {},
      seats: {}
    };

    // Initialize returnAddons early to avoid ReferenceError
    let returnAddons = null;
    if (bookingStore.isRoundTrip) {
      returnAddons = {
        baggage: {},
        meals: {},
        wheelchair: {},
        seats: {}
      };
    }

    // Helper to get airport code
    const getAirportCode = (airport) => {
      if (!airport) return '';
      if (typeof airport === 'string') return airport;
      return airport.code || '';
    };

    // Extract baggage addons for depart flight
    if (bookingStore.addons?.baggage?.depart) {
      Object.entries(bookingStore.addons.baggage.depart).forEach(([key, baggage]) => {
        if (baggage) {
          const id = typeof baggage === 'object' ? baggage.id : baggage;
          if (id) {
            formattedAddons.baggage[key] = { 
              id: id, 
              is_included: typeof baggage === 'object' ? (baggage.is_included || false) : false, 
              price: typeof baggage === 'object' ? (baggage.price || 0) : 0 
            };
          }
        }
      });
    }

    // Extract meal addons for depart flight - UPDATED for multiple meals
    if (bookingStore.addons?.meals?.depart) {
      Object.entries(bookingStore.addons.meals.depart).forEach(([key, meals]) => {
        if (Array.isArray(meals) && meals.length > 0) {
          formattedAddons.meals[key] = meals.map(m => {
            const id = typeof m === 'object' ? m.id : m;
            return { 
              id: id, 
              is_included: typeof m === 'object' ? (m.is_included || false) : false, 
              price: typeof m === 'object' ? (m.price || 0) : 0 
            };
          }).filter(m => m.id);
        }
      });
    }

    // Extract assistance addons for depart flight
    if (bookingStore.addons?.wheelchair?.depart) {
      Object.entries(bookingStore.addons.wheelchair.depart).forEach(([key, serviceId]) => {
        if (serviceId) {
          formattedAddons.wheelchair[key] = serviceId;
        }
      });
    }

    // Extract seats (segmented) for depart
    if (bookingStore.addons?.seats?.depart) {
      Object.entries(bookingStore.addons.seats.depart).forEach(([key, seat]) => {
        if (seat) {
          const id = typeof seat === 'object' ? seat.id : seat;
          if (id) {
            formattedAddons.seats[key] = { 
              id: id, 
              is_included: typeof seat === 'object' ? (seat.is_included || false) : false, 
              price: typeof seat === 'object' ? (seat.price || 0) : 0 
            };
          }
        }
      });
    }

    // Extract addons for return flight if applicable
    if (bookingStore.isRoundTrip) {
      // Return baggage
      if (bookingStore.addons?.baggage?.return) {
        Object.entries(bookingStore.addons.baggage.return).forEach(([key, baggage]) => {
          if (baggage) {
            const id = typeof baggage === 'object' ? baggage.id : baggage;
            if (id) returnAddons.baggage[key] = { 
              id: id, 
              is_included: typeof baggage === 'object' ? (baggage.is_included || false) : false, 
              price: typeof baggage === 'object' ? (baggage.price || 0) : 0 
            };
          }
        });
      }
      // Return meals - UPDATED for multiple meals
      if (bookingStore.addons?.meals?.return) {
        Object.entries(bookingStore.addons.meals.return).forEach(([key, meals]) => {
          if (Array.isArray(meals) && meals.length > 0) {
            returnAddons.meals[key] = meals.map(m => {
              const id = typeof m === 'object' ? m.id : m;
              return { 
                id: id, 
                is_included: typeof m === 'object' ? (m.is_included || false) : false, 
                price: typeof m === 'object' ? (m.price || 0) : 0 
              };
            }).filter(m => m.id);
          }
        });
      }
      // Return assistance
      if (bookingStore.addons?.wheelchair?.return) {
        Object.entries(bookingStore.addons.wheelchair.return).forEach(([key, serviceId]) => {
          if (serviceId) returnAddons.wheelchair[key] = serviceId;
        });
      }
      // Return seats
      if (bookingStore.addons?.seats?.return) {
        Object.entries(bookingStore.addons.seats.return).forEach(([key, seat]) => {
          if (seat) {
            const id = typeof seat === 'object' ? seat.id : seat;
            if (id) returnAddons.seats[key] = { 
              id: id, 
              is_included: typeof seat === 'object' ? (seat.is_included || false) : false, 
              price: typeof seat === 'object' ? (seat.price || 0) : 0 
            };
          }
        });
      }
    }

    // Build complete booking data
    const tripType = bookingStore.tripType;
    const isMultiCity = tripType === 'multi_city' || tripType === 'multi-city';

    const bookingData = {
      trip_type: isMultiCity ? 'multi_city' : (bookingStore.isRoundTrip ? 'round_trip' : 'one_way'),
      passengers: formattedPassengers,
      contact_info: contactInfo,
      passengerCount: {
        adult: parseInt(bookingStore.passengerCount?.adults) || 1,
        children: parseInt(bookingStore.passengerCount?.children) || 0,
        infant: parseInt(bookingStore.passengerCount?.infants) || 0
      },
      insurance_plan_id: bookingStore.addons?.insurance?.selectedPlanId || null,
      activity_id: bookingStore.activityId || null,
      activity_code: bookingStore.activityCode || null,
      is_practice: bookingStore.isPractice || false,
      booking_session_id: bookingStore.bookingSessionId || null,
      fare_families: bookingStore.fareFamilies || {}
    };

    if (isMultiCity) {
      // Multi-city: Send as segments array
      bookingData.segments = bookingStore.multiCitySegments.map((seg, idx) => {
        const segKey = idx.toString();
        const segAddons = {
          baggage: {},
          meals: {},
          wheelchair: {},
          seats: {}
        };

        // Extract addons for this segment
        if (bookingStore.addons?.baggage?.[segKey]) {
          Object.entries(bookingStore.addons.baggage[segKey]).forEach(([paxKey, baggage]) => {
            if (baggage && baggage.id) segAddons.baggage[paxKey] = { id: baggage.id, is_included: baggage.is_included || false, price: baggage.price || 0 };
          });
        }
        if (bookingStore.addons?.meals?.[segKey]) {
          Object.entries(bookingStore.addons.meals[segKey]).forEach(([paxKey, meals]) => {
            if (Array.isArray(meals) && meals.length > 0) {
              segAddons.meals[paxKey] = meals.map(m => ({ id: m.id, is_included: m.is_included || false, price: m.price || 0 }));
            }
          });
        }
        if (bookingStore.addons?.wheelchair?.[segKey]) {
          Object.entries(bookingStore.addons.wheelchair[segKey]).forEach(([paxKey, svcId]) => {
            if (svcId) segAddons.wheelchair[paxKey] = svcId;
          });
        }
        if (bookingStore.addons?.seats?.[segKey]) {
          Object.entries(bookingStore.addons.seats[segKey]).forEach(([paxKey, seat]) => {
            if (seat && seat.id) segAddons.seats[paxKey] = { id: seat.id, is_included: seat.is_included || false, price: seat.price || 0 };
          });
        }

        return {
          selectedFlight: {
            id: seg.selectedFlight?.id,
            schedule_id: seg.selectedFlight?.id,
            flight_number: seg.selectedFlight?.flight_number,
            origin: getAirportCode(seg.origin),
            destination: getAirportCode(seg.destination),
            departure_time: seg.selectedFlight?.departure_time,
            class_type: seg.selectedFlight?.class_type || seg.selectedFlight?.selected_seat_class || 'Economy',
            price: parseFloat(seg.selectedFlight?.price) || 0,
            airline: seg.selectedFlight?.airline,
            airline_code: seg.selectedFlight?.airline_code,
            fare_family: bookingStore.fareFamilies?.[segKey] || 'basic',
            fare_family_name: bookingStore.fareFamilyNames?.[segKey] || ''
          },
          addons: segAddons
        };
      });
    }
    else {
      // One-way or Round-trip: Maintain existing structure for backward compatibility
      bookingData.selectedOutbound = bookingStore.selectedOutbound ? {
        id: bookingStore.selectedOutbound.id,
        schedule_id: bookingStore.selectedOutbound.schedule_id || bookingStore.selectedOutbound.id,
        flight_number: bookingStore.selectedOutbound.flight_number,
        price: parseFloat(bookingStore.selectedOutbound.price) || 0,
        class_type: bookingStore.selectedOutbound.class_type || bookingStore.selectedOutbound.selected_seat_class || 'Economy',
        origin: getAirportCode(bookingStore.selectedOutbound.origin),
        destination: getAirportCode(bookingStore.selectedOutbound.destination),
        departure_time: bookingStore.selectedOutbound.departure_time,
        airline: bookingStore.selectedOutbound.airline,
        airline_code: bookingStore.selectedOutbound.airline_code,
        fare_family: bookingStore.fareFamilies?.['depart'] || 'basic',
        fare_family_name: bookingStore.fareFamilyNames?.['depart'] || ''
      } : null;

      bookingData.selectedReturn = bookingStore.selectedReturn ? {
        id: bookingStore.selectedReturn.id,
        schedule_id: bookingStore.selectedReturn.schedule_id || bookingStore.selectedReturn.id,
        flight_number: bookingStore.selectedReturn.flight_number,
        price: parseFloat(bookingStore.selectedReturn.price) || 0,
        class_type: bookingStore.selectedReturn.class_type || bookingStore.selectedReturn.selected_seat_class || 'Economy',
        origin: getAirportCode(bookingStore.selectedReturn.origin),
        destination: getAirportCode(bookingStore.selectedReturn.destination),
        departure_time: bookingStore.selectedReturn.departure_time,
        fare_family: bookingStore.fareFamilies?.['return'] || 'basic',
        fare_family_name: bookingStore.fareFamilyNames?.['return'] || ''
      } : null;

      bookingData.addons = formattedAddons;
      bookingData.return_addons = returnAddons;
    }

    console.log('✅ Final formatted booking data:', JSON.stringify(bookingData, null, 2));
    return bookingData;
  },

  // Helper to get default date of birth (20 years ago)
  getDefaultDOB() {
    const date = new Date()
    date.setFullYear(date.getFullYear() - 20)
    return date.toISOString().split('T')[0]  // YYYY-MM-DD format
  },

  /**
   * Fetch the authoritative price from the backend before booking creation.
   * Use this on the Review Booking page to display the real total.
   */
  async calculatePrice(bookingStore) {
    try {
      const payload = this.formatBookingData(bookingStore)
      const response = await api.post('flightapp/calculate-price/', payload)
      if (response.data?.success) {
        return {
          success: true,
          total_amount: response.data.total_amount,
          breakdown: response.data.breakdown,
          tax_details: response.data.tax_details,
          currency: response.data.currency
        }
      }
      return { success: false, error: response.data?.error || 'Failed to calculate price' }
    } catch (error) {
      console.error('❌ Error calculating price:', error.response?.data || error.message)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to calculate price'
      }
    }
  },

  /**
   * Explicitly fail an activity when time is up
   * @param {number} activityId - The ID of the activity to fail
   */
  async failActivity(activityId) {
    try {
      console.log(`⏰ Failing activity ID: ${activityId} due to timeout`)
      const response = await api.post(`fbs_instructor/student/activity/fail/${activityId}/`)
      return response.data
    } catch (error) {
      console.error('❌ Error failing activity:', error.response?.data || error.message)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to mark activity as failed'
      }
    }
  }
}