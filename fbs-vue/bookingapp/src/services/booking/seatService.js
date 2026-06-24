// services/booking/seatService.js
import api from './api';

export const seatService = {
  /**
   * Temporarily lock a seat for a user session
   * @param {Number|String} seatId 
   * @param {String} sessionId 
   * @param {Number} duration - Duration in minutes
   */
  async lockSeat(seatId, sessionId, duration = 15) {
    try {
      const response = await api.post(`flightapp/api/seats/${seatId}/lock/`, {
        session_id: sessionId,
        duration: duration
      });
      return response.data;
    } catch (error) {
      console.error(`❌ Failed to lock seat ${seatId}:`, error.response?.data || error.message);
      return {
        success: false,
        error: error.response?.data?.error || 'Could not lock seat',
        status: error.response?.status
      };
    }
  },

  /**
   * Unlock a seat manually
   * @param {Number|String} seatId 
   * @param {String} sessionId 
   */
  async unlockSeat(seatId, sessionId) {
    try {
      const response = await api.post(`flightapp/api/seats/${seatId}/unlock/`, {
        session_id: sessionId
      });
      return response.data;
    } catch (error) {
      console.error(`❌ Failed to unlock seat ${seatId}:`, error.response?.data || error.message);
      return {
        success: false,
        error: error.response?.data?.error || 'Could not unlock seat'
      };
    }
  },

  /**
   * Fetches all seats for a specific flight schedule with schedule info
   * @param {Number|String} scheduleId 
   * @param {String} sessionId
   */
  async getSeatsBySchedule(scheduleId, sessionId = null) {
    try {
      console.log(`🔍 Fetching seats for schedule ${scheduleId}...`);

      // Try the new endpoint first (recommended)
      const response = await api.get(`flightapp/api/schedules/${scheduleId}/seats-with-info/`, {
        params: { session_id: sessionId }
      });

      if (response.data.success) {
        console.log('✅ Seat data loaded with new endpoint:', {
          scheduleId: response.data.schedule_id,
          schedulePrice: response.data.schedule_price,
          aircraftModel: response.data.aircraft_model,
          totalSeats: response.data.total_seats,
          availableSeats: response.data.available_seats,
          sampleSeat: response.data.seats[0] ? {
            seat_code: response.data.seats[0].seat_code,
            final_price: response.data.seats[0].final_price,
            seat_class: response.data.seats[0].seat_class?.name,
            features: response.data.seats[0].features || []
          } : null
        });
        return response.data;
      } else {
        console.log('⚠️ New endpoint returned error:', response.data.error);
        return await this.getSeatsByScheduleOld(scheduleId);
      }
    } catch (error) {
      console.error(`❌ Error with new endpoint:`, error.message);
      console.log('🔄 Falling back to old endpoint...');
      return await this.getSeatsByScheduleOld(scheduleId);
    }
  },

  /**
   * Fallback: Use the old endpoint
   */
  async getSeatsByScheduleOld(scheduleId) {
    try {
      console.log(`🔄 Trying old endpoint for schedule ${scheduleId}...`);
      const response = await api.get('flightapp/api/seats/', {
        params: {
          schedule: scheduleId,
          session_id: sessionId
        }
      });

      console.log('Old endpoint response:', response.data);

      // Check response structure
      let seatsData = [];
      let schedulePrice = 0;
      let totalSeats = 0;
      let availableSeats = 0;

      if (response.data && response.data.seats) {
        // New structure from updated SeatViewSet
        seatsData = response.data.seats;
        schedulePrice = response.data.schedule_price || 0;
        totalSeats = response.data.total_seats || seatsData.length;
        availableSeats = response.data.available_seats || 0;
      } else if (Array.isArray(response.data)) {
        // Old structure (array of seats)
        seatsData = response.data;
        totalSeats = seatsData.length;
        availableSeats = seatsData.filter(seat => seat.is_available).length;

        // Try to get schedule price separately
        try {
          const scheduleResponse = await api.get(`flightapp/api/schedules/${scheduleId}/`);
          schedulePrice = scheduleResponse.data.price || 0;
        } catch (e) {
          console.warn('Could not get schedule price:', e.message);
          schedulePrice = 1000; // Default
        }
      } else {
        throw new Error('Invalid response format from seat endpoint');
      }

      console.log('✅ Seat data loaded with old endpoint:', {
        seatsCount: seatsData.length,
        schedulePrice: schedulePrice,
        hasFinalPrice: seatsData[0] && 'final_price' in seatsData[0]
      });

      return {
        success: true,
        seats: seatsData,
        schedule_price: schedulePrice,
        total_seats: totalSeats,
        available_seats: availableSeats
      };
    } catch (error) {
      console.error(`❌ Error with old endpoint for schedule ${scheduleId}:`, error);

      // Create mock data as last resort
      console.log('⚠️ Creating mock seats for development');
      return this.createMockSeats(scheduleId);
    }
  },

  /**
   * Create mock seats for development/testing
   */
  createMockSeats(scheduleId) {
    const mockSeats = [];
    const basePrice = 1500; // Default base price
    const seatClasses = [
      { id: 1, name: 'Business', price_multiplier: 2.0 },
      { id: 2, name: 'Comfort', price_multiplier: 1.5 },
      { id: 3, name: 'Economy', price_multiplier: 1.0 }
    ];

    let seatId = 1;
    for (let row = 1; row <= 37; row++) {
      let seatClass;
      if (row <= 4) {
        seatClass = seatClasses[0]; // Business
      } else if (row <= 9) {
        seatClass = seatClasses[1]; // Comfort
      } else {
        seatClass = seatClasses[2]; // Economy
      }

      const columns = ['A', 'B', 'C', 'D', 'E', 'F'];

      for (const col of columns) {
        const seatCode = `${row}${col}`;
        const multiplier = seatClass.price_multiplier;
        const adjustment = row <= 9 ? 100 : 0;
        const finalPrice = (basePrice * multiplier) + adjustment;

        mockSeats.push({
          id: seatId++,
          seat_code: seatCode,
          seat_number: seatCode,
          row: row,
          column: col,
          is_available: Math.random() > 0.3, // 70% available
          final_price: finalPrice,
          price_adjustment: adjustment,
          has_extra_legroom: row === 1 || row === 11 || row === 26,
          is_exit_row: row === 11 || row === 26,
          is_bulkhead: row === 1,
          is_window: col === 'A' || col === 'F',
          is_aisle: col === 'C' || col === 'D',
          features: [],
          seat_class: seatClass
        });
      }
    }

    console.log(`Created ${mockSeats.length} mock seats`);

    return {
      success: true,
      seats: mockSeats,
      schedule_price: basePrice,
      schedule_id: scheduleId,
      total_seats: mockSeats.length,
      available_seats: mockSeats.filter(seat => seat.is_available).length
    };
  },

  /**
   * Debug: Get seat price calculation details
   */
  async debugSeatPrices(scheduleId) {
    try {
      console.log('🔍 DEBUG: Checking seat prices...');

      // First get schedule
      const scheduleResponse = await api.get(`flightapp/api/schedules/${scheduleId}/`);
      const schedule = scheduleResponse.data;

      console.log('Schedule info:', {
        id: schedule.id,
        price: schedule.price,
        flight_number: schedule.flight?.flight_number
      });

      // Then get seats
      const seatsResponse = await api.get('flightapp/api/seats/', {
        params: { schedule: scheduleId }
      });

      console.log('Seats response:', {
        count: Array.isArray(seatsResponse.data) ? seatsResponse.data.length : 'unknown',
        structure: Array.isArray(seatsResponse.data) ? 'array' : typeof seatsResponse.data
      });

      if (Array.isArray(seatsResponse.data) && seatsResponse.data.length > 0) {
        const sampleSeat = seatsResponse.data[0];
        console.log('Sample Seat:', sampleSeat);

        // Calculate expected price
        const basePrice = schedule.price || 0;
        const multiplier = sampleSeat.seat_class?.price_multiplier || 1;
        const adjustment = sampleSeat.price_adjustment || 0;
        const expectedPrice = (basePrice * multiplier) + adjustment;

        console.log('Price Calculation:');
        console.log(`  Base Price: ${basePrice}`);
        console.log(`  Multiplier: ${multiplier}`);
        console.log(`  Adjustment: ${adjustment}`);
        console.log(`  Expected: ${expectedPrice}`);
        console.log(`  Actual (final_price): ${sampleSeat.final_price}`);

        // Check if final_price exists
        console.log(`Has final_price property: ${'final_price' in sampleSeat}`);
      }

      return {
        success: true,
        schedule: schedule,
        seats_count: Array.isArray(seatsResponse.data) ? seatsResponse.data.length : 0
      };
    } catch (error) {
      console.error('Debug error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Get test seat data (for debugging)
   */
  async testSeatData(scheduleId) {
    try {
      const response = await api.get(`flightapp/api/test-seat-data/${scheduleId}/`);
      return response.data;
    } catch (error) {
      console.error('Error getting test data:', error);
      return { error: error.message };
    }
  }
};