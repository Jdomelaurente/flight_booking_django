// paymentService.js
import api from './api.js';
import axios from 'axios'; // Only used for direct PayMongo API calls (external)

const PAYMONGO_PUBLIC_KEY = import.meta.env.VITE_PAYMONGO_PUBLIC_KEY || '';

export const paymentService = {

  /**
   * Method 1: Create a PayMongo Checkout Session (Hosted Payment Page)
   * This allows users to choose from multiple payment methods
   */
  async createCheckoutSession(bookingData) {
    try {
      const response = await api.post('flightapp/create-checkout-session/', {
        amount: bookingData.amount,
        booking_id: bookingData.booking_id,
        booking_reference: bookingData.booking_reference,
        description: `Flight Booking ${bookingData.booking_id}`
      });

      if (response.data.success) {
        return {
          success: true,
          checkout_url: response.data.checkout_url,
          session_id: response.data.session_id,
          message: 'Checkout session created successfully'
        };
      } else {
        throw new Error(response.data.error || 'Failed to create checkout session');
      }

    } catch (error) {
      // Error is reported by global interceptor toast
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to create checkout session'
      };
    }
  },

  /**
   * Method 2: Process GCash payment directly
   * Alternative approach for direct GCash integration
   */
  async processGcashPayment(bookingData, billingInfo) {
    try {
      // 1. Create Payment Intent via Django Backend (uses global interceptor)
      const intentResponse = await api.post('flightapp/create-payment-intent/', {
        amount: bookingData.amount,
        booking_id: bookingData.booking_id,
        description: `Flight Booking ${bookingData.booking_id}`
      });

      if (!intentResponse.data.success) {
        throw new Error(intentResponse.data.error || 'Failed to create payment intent');
      }

      const { client_key, intent_id } = intentResponse.data;

      // 2. Create Payment Method (Directly to PayMongo - external API, uses raw axios)
      const pmResponse = await axios.post('https://api.paymongo.com/v1/payment_methods', {
        data: {
          attributes: {
            type: 'gcash',
            billing: billingInfo || {
              name: `${bookingData.contactInfo?.firstName || ''} ${bookingData.contactInfo?.lastName || ''}`.trim(),
              email: bookingData.contactInfo?.email || '',
              phone: bookingData.contactInfo?.phone || ''
            }
          }
        }
      }, {
        headers: {
          'Authorization': `Basic ${btoa(PAYMONGO_PUBLIC_KEY + ':')}`,
          'Content-Type': 'application/json'
        }
      });

      const paymentMethodId = pmResponse.data.data.id;

      // 3. Attach to Intent (Directly to PayMongo - external API, uses raw axios)
      const attachResponse = await axios.post(
        `https://api.paymongo.com/v1/payment_intents/${intent_id}/attach`,
        {
          data: {
            attributes: {
              payment_method: paymentMethodId,
              client_key: client_key,
              return_url: `${window.location.origin}/payment-callback`
            }
          }
        },
        {
          headers: {
            'Authorization': `Basic ${btoa(PAYMONGO_PUBLIC_KEY + ':')}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return {
        success: true,
        data: attachResponse.data.data,
        next_action: attachResponse.data.data.attributes.next_action,
        message: 'GCash payment initiated successfully'
      };

    } catch (error) {
      let errorMessage = 'GCash payment failed';
      if (error.response) {
        errorMessage = error.response.data?.errors?.[0]?.detail || error.response.data?.error || errorMessage;
      }

      return {
        success: false,
        error: errorMessage
      };
    }
  },

  /**
   * Method 3: Verify payment status
   */
  async verifyPayment(intentId) {
    try {
      const response = await api.post('flightapp/verify-payment/', {
        intent_id: intentId
      });

      return {
        success: response.data.success,
        status: response.data.status,
        data: response.data.data
      };

    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || error.message
      };
    }
  },

  /**
   * Method 4: Create payment source (alternative method)
   */
  async createPaymentSource(amount, paymentType = 'gcash', bookingId = null) {
    try {
      const response = await api.post('flightapp/create-payment-source/', {
        amount: amount,
        type: paymentType,
        booking_id: bookingId
      });

      if (response.data.success) {
        return {
          success: true,
          source_id: response.data.source_id,
          checkout_url: response.data.checkout_url,
          message: `${paymentType} payment source created`
        };
      } else {
        throw new Error(response.data.error);
      }

    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || error.message
      };
    }
  },

  /**
   * Helper: Check if PayMongo is configured
   */
  isPayMongoConfigured() {
    return PAYMONGO_PUBLIC_KEY && PAYMONGO_PUBLIC_KEY.startsWith('pk_');
  },

  /**
   * Helper: Get available payment methods
   */
  getAvailablePaymentMethods() {
    const methods = [
      {
        id: 'checkout',
        name: 'Multiple Options',
        description: 'Pay with GCash, Maya, Credit/Debit Card',
        icon: '💳',
        requiresCheckoutSession: true
      },
      {
        id: 'gcash',
        name: 'GCash',
        description: 'Pay using your GCash wallet',
        icon: '📱',
        requiresDirectIntegration: true
      },
      {
        id: 'card',
        name: 'Credit/Debit Card',
        description: 'Pay using Visa, Mastercard, or JCB',
        icon: '💳',
        requiresCheckoutSession: true
      }
    ];

    // Filter based on PayMongo configuration
    if (!this.isPayMongoConfigured()) {
      return methods.filter(method => method.id === 'checkout');
    }

    return methods;
  }
};

// Default export
export default paymentService;
