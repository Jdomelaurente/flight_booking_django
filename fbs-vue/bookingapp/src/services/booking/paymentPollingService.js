// src/services/paymentPollingService.js
import api from './api.js';

export const paymentPollingService = {
  async runFullPaymentCheck(bookingId) {
    const fullResponse = await api.get(`flightapp/check-payment-status/${bookingId}/`);
    return {
      success: fullResponse.data.success !== false,
      paid: fullResponse.data.paid === true,
      data: fullResponse.data,
      immediate: false
    };
  },

  /**
   * Simple polling for booking status
   * Returns immediately if booking is confirmed
   */
  async pollBookingStatus(bookingId, options = {}) {
    const {
      maxAttempts = 30,
      interval = 2000,
      onProgress = () => { },
      immediateFirstCheck = true
    } = options;

    let attempts = 0;

    const checkStatus = async () => {
      attempts++;

      try {
        console.log(`🔄 Polling booking status (attempt ${attempts}/${maxAttempts})...`);

        // Use the simple endpoint that doesn't search PayMongo
        let response;
        try {
          response = await api.get(`flightapp/check-booking-status/${bookingId}/`);
        } catch (simpleError) {
          // If simple endpoint returns 404 or other error, fall back to full status check.
          // This avoids hard-failing polling on transient or route-level issues.
          const fallback = await this.runFullPaymentCheck(bookingId);
          onProgress({
            attempt: attempts,
            maxAttempts,
            data: fallback.data
          });

          if (fallback.paid) {
            return {
              success: true,
              paid: true,
              data: fallback.data,
              attempts
            };
          }

          response = { data: fallback.data };
        }

        onProgress({
          attempt: attempts,
          maxAttempts,
          data: response.data
        });

        if (response.data.paid || response.data.booking_status === 'Confirmed') {
          console.log('✅ Booking confirmed!', response.data);
          return {
            success: true,
            paid: true,
            data: response.data,
            attempts: attempts
          };
        }

        if (attempts >= maxAttempts) {
          console.log('⏰ Polling timeout reached');
          return {
            success: false,
            paid: false,
            timeout: true,
            attempts: attempts,
            message: 'Payment verification timeout'
          };
        }

        // Continue polling
        return new Promise((resolve) => {
          setTimeout(async () => {
            const result = await checkStatus();
            resolve(result);
          }, interval);
        });

      } catch (error) {
        console.error('Polling error:', error);
        return {
          success: false,
          paid: false,
          error: error.message,
          attempts: attempts
        };
      }
    };

    // Start polling
    return checkStatus();
  },

  /**
   * Check payment status once (no polling)
   */
  async checkPaymentStatusOnce(bookingId) {
    try {
      console.log(`🔍 Checking payment status for booking ${bookingId}...`);

      try {
        // Try the simple endpoint first
        const simpleResponse = await api.get(`flightapp/check-booking-status/${bookingId}/`);

        if (simpleResponse.data.paid || simpleResponse.data.booking_status === 'Confirmed') {
          return {
            success: true,
            paid: true,
            data: simpleResponse.data,
            immediate: true
          };
        }
      } catch (simpleError) {
        // Continue to full check below.
        console.warn('Simple booking-status check failed, using full payment status check.');
      }

      // Always try full check as fallback/verification path.
      return await this.runFullPaymentCheck(bookingId);

    } catch (error) {
      console.error('Payment check error:', error);
      return {
        success: false,
        paid: false,
        error: error.response?.data?.error || error.message
      };
    }
  }
};
