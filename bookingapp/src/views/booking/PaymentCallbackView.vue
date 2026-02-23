<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useBookingStore } from '@/stores/booking';
import { paymentPollingService } from '@/services/booking/paymentPollingService';
import api from '@/services/booking/api';
import { useNotificationStore } from '@/stores/notification';
import { useModalStore } from '@/stores/modal';

const route = useRoute();
const router = useRouter();
const bookingStore = useBookingStore();
const notificationStore = useNotificationStore();
const modalStore = useModalStore();

const loading = ref(true);
const errorMessage = ref('');
const pollingCount = ref(0);
const maxPollingAttempts = 15;
const pollingInterval = ref(null);
const processingStatus = ref('');
const showIncompleteState = ref(false);

// Get parameters from URL
const urlParams = new URLSearchParams(window.location.search);
const paymentSuccess = urlParams.get('payment_success');
const sessionIdFromUrl = urlParams.get('session_id');
const bookingId = urlParams.get('booking_id') || bookingStore.booking_id;
const paymentIntentId = urlParams.get('payment_intent_id');

console.log('Payment callback parameters:', { 
  paymentSuccess, 
  bookingId, 
  sessionId: sessionIdFromUrl,
  paymentIntentId 
});

const getLoadingMessage = () => {
  const messages = [
    "Verifying your payment...",
    "Confirming transaction details...",
    "Processing your booking...",
    "Almost there...",
    "Finalizing confirmation..."
  ];
  return messages[pollingCount.value % messages.length];
};

// Poll payment status - REDIRECTS TO SUCCESS PAGE WHEN PAID
const pollPaymentStatus = async (bookingId) => {
  if (pollingCount.value >= maxPollingAttempts) {
    clearInterval(pollingInterval.value);
    showIncompleteState.value = true;
    loading.value = false;
    return;
  }

  pollingCount.value++;
  processingStatus.value = `Checking payment status (Attempt ${pollingCount.value}/${maxPollingAttempts})...`;

  try {
    console.log(`Polling attempt ${pollingCount.value} for booking ${bookingId}`);
    
    // Use the new polling service
    const result = await paymentPollingService.checkPaymentStatusOnce(bookingId);
    
    console.log('Polling result:', result);

    if (result.paid === true) {
      // Payment confirmed! Navigate to success page
      clearInterval(pollingInterval.value);
      
      // Prepare data for success page
      const bookingReference = result.data.booking_reference || `CSUCC${bookingId.toString().padStart(8, '0')}`;
      const paymentId = result.data.payment_id;
      const amount = bookingStore.booking_total || bookingStore.grandTotal;
      
      console.log('Payment successful! Navigating to success page with:', {
        ref: bookingReference,
        payment_id: paymentId,
        amount: amount
      });
      
      // Defer clearing the booking store until the user leaves the success page
      // This prevents the router guard from redirecting to dashboard prematurely
      // bookingStore.clearActivityCodeValidation();
      // bookingStore.resetBooking();
      // localStorage.removeItem('current_booking');
      // localStorage.removeItem('payment_session');
      
      // Navigate to success page
      router.push({
        name: 'BookingSuccess',
        query: {
          ref: bookingReference,
          payment_id: paymentId,
          amount: amount,
          booking_id: bookingId
        }
      });
      
    } else if (result.success === false) {
      // Error from backend
      clearInterval(pollingInterval.value);
      errorMessage.value = result.error || 'Payment verification failed.';
      loading.value = false;
    }
    // If paid is false, continue polling
    
  } catch (error) {
    console.error('Polling error:', error);
    processingStatus.value = 'Connection error, retrying...';
  }
};

const startPolling = (bookingId) => {
  console.log(`Starting polling for booking ${bookingId}`);
  pollingCount.value = 0;
  processingStatus.value = 'Starting payment verification...';
  
  // Start immediate poll
  pollPaymentStatus(bookingId);
  
  // Set up interval for subsequent polls
  pollingInterval.value = setInterval(() => {
    pollPaymentStatus(bookingId);
  }, 2000);
};

const verifyPaymentWithSession = async () => {
  if (!sessionIdFromUrl || sessionIdFromUrl.includes('{')) {
    console.log('Invalid session ID, skipping verification');
    return false;
  }
  
  try {
    console.log(`Verifying payment with session: ${sessionIdFromUrl}`);
    
    const response = await api.post('verify-session-payment/', {
      booking_id: bookingId,
      session_id: sessionIdFromUrl
    });
    
    console.log('Session verification response:', response.data);
    
    if (response.data.success) {
      return {
        success: true,
        data: response.data
      };
    }
  } catch (error) {
    console.error('Session verification error:', error);
  }
  
  return { success: false };
};

onMounted(async () => {
  // Check for booking ID
  if (!bookingId) {
    errorMessage.value = 'No booking found. Please start a new booking.';
    loading.value = false;
    return;
  }

  // Check if payment was successful
  if (paymentSuccess === 'true') {
    console.log('Payment reported as successful, starting verification...');
    
    // Try to verify with session ID if available
    if (sessionIdFromUrl && !sessionIdFromUrl.includes('{')) {
      console.log(`Got valid session ID: ${sessionIdFromUrl}`);
      processingStatus.value = 'Verifying payment with session ID...';
      
      // Try direct verification first with the correct endpoint
      try {
        const verifyResponse = await api.post('verify-session-payment/', {
          booking_id: bookingId,
          session_id: sessionIdFromUrl,
          payment_success: 'true'
        });
        
        console.log('Direct verification response:', verifyResponse.data);
        
        if (verifyResponse.data.success) {
          // Payment processed successfully! Navigate to success page
          const bookingReference = verifyResponse.data.booking_reference || `CSUCC${bookingId.toString().padStart(8, '0')}`;
          const paymentId = verifyResponse.data.payment_id;
          const amount = bookingStore.booking_total || bookingStore.grandTotal;
          
          console.log('Direct verification successful! Navigating to success page');
          
          // Defer clearing the booking store until the user leaves the success page
          // bookingStore.clearActivityCodeValidation();
          // bookingStore.resetBooking();
          // localStorage.removeItem('current_booking');
          // localStorage.removeItem('payment_session');
          
          // Navigate to success page
          router.push({
            name: 'BookingSuccess',
            query: {
              ref: bookingReference,
              payment_id: paymentId,
              amount: amount,
              booking_id: bookingId
            }
          });
          
          return;
        } else {
          console.log('Direct verification failed, session status:', verifyResponse.data.session_status);
        }
      } catch (error) {
        console.log('Direct verification failed, falling back to polling:', error);
      }
    }
    
    // If direct verification fails, fall back to polling
    processingStatus.value = 'Payment verification needed, starting polling...';
    startPolling(bookingId);
    
  } else if (paymentSuccess === 'false') {
    errorMessage.value = 'Payment was cancelled or failed.';
    loading.value = false;
  } else {
    // No success parameter - maybe direct access
    console.log('No success parameter, checking payment status...');
    processingStatus.value = 'Checking payment status...';
    startPolling(bookingId);
  }
});

onUnmounted(() => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value);
  }
});

const goHome = () => {
  bookingStore.resetBooking();
  localStorage.removeItem('current_booking');
  localStorage.removeItem('payment_session');
  router.push({ name: 'Home' });
};

const retryPayment = () => {
  if (bookingStore.booking_id) {
    router.push({
      name: 'Payment',
      query: { 
        bookingId: bookingStore.booking_id,
        retry: true 
      }
    });
  } else {
    router.push({ name: 'SearchFlights' });
  }
};

const cancelBooking = async () => {
  const confirmed = await modalStore.confirm({
    title: 'Cancel Booking?',
    message: 'Are you sure you want to cancel this booking? This action cannot be undone.',
    confirmText: 'Yes, Cancel',
    cancelText: 'No, Keep'
  });

  if (confirmed) {
    try {
      await api.post(`cancel-booking/${bookingStore.booking_id}/`);
      bookingStore.resetBooking();
      localStorage.removeItem('current_booking');
      localStorage.removeItem('payment_session');
      router.push({ name: 'Home' });
    } catch (error) {
      notificationStore.error('Failed to cancel booking: ' + error.message);
    }
  }
};
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-pink-50 via-white to-rose-50 flex justify-center items-center p-5">
    
    <!-- Loading State - SHOWS WHILE POLLING -->
    <div v-if="loading" class="bg-white border border-gray-300 rounded-[5px] p-8 md:p-10 text-center max-w-lg w-full">
      <div class="w-12 h-12 border-4 border-gray-200 border-t-pink-500 rounded-[2px] animate-spin mx-auto mb-6"
           style="border-color: #e5e7eb; border-top-color: #FF5794;"></div>
      
      <p class="text-lg font-semibold text-gray-800 mb-2">{{ processingStatus }}</p>
      
      <p v-if="pollingCount < maxPollingAttempts" class="text-gray-600 mb-4">
        {{ getLoadingMessage() }}
      </p>
      <p v-else class="text-gray-600 mb-4">
        Taking longer than expected... Still verifying your payment.
      </p>
      
      <div v-if="pollingCount > 0" class="mt-4">
        <small class="text-gray-500 text-sm">Attempt {{ pollingCount }} of {{ maxPollingAttempts }}</small>
      </div>

      <div class="mt-6 pt-6 border-t border-gray-200">
        <p class="text-sm text-gray-500">
          Please do not close this window while we process your payment.
        </p>
      </div>
    </div>

    <!-- Incomplete Payment State -->
    <div v-else-if="showIncompleteState" class="bg-white border border-gray-300 rounded-[5px] p-8 md:p-10 text-center max-w-2xl w-full">
      <div class="text-6xl mb-4">🔄</div>
      
      <h1 class="text-3xl font-bold text-gray-800 mb-3">Payment Not Completed</h1>
      
      <p class="text-lg text-gray-600 mb-6">
        It looks like you didn't complete the payment on PayMongo's checkout page.
      </p>
      
      <div class="bg-gray-50 border border-gray-300 rounded-[5px] p-5 text-left mb-6">
        <p class="font-semibold text-gray-800 mb-3">What happened:</p>
        <ul class="space-y-2 text-gray-600 ml-5">
          <li class="list-disc">You were redirected to PayMongo's secure payment page</li>
          <li class="list-disc">The payment was not completed</li>
          <li class="list-disc">You returned to this page without finishing the transaction</li>
        </ul>
      </div>
      
      <div class="bg-amber-50 border border-amber-300 rounded-[5px] p-5 text-left mb-6">
        <div class="space-y-2">
          <p class="text-gray-700">
            <strong class="font-semibold">Booking Reference:</strong> 
            {{ bookingStore.booking_reference || `CSUCC${bookingId?.toString().padStart(8, '0')}` }}
          </p>
          <p class="text-gray-700">
            <strong class="font-semibold">Amount:</strong> 
            ₱{{ bookingStore.booking_total?.toLocaleString() || bookingStore.grandTotal?.toLocaleString() }}
          </p>
          <p class="text-gray-700">
            <strong class="font-semibold">Status:</strong> 
            <span class="inline-block bg-yellow-100 border border-yellow-400 text-yellow-800 px-3 py-1 rounded-[5px] text-sm font-semibold ml-2">
              Payment Pending
            </span>
          </p>
        </div>
      </div>
      
      <div class="flex flex-col md:flex-row gap-3 mb-6">
        <button @click="retryPayment" 
                class="flex-1 border border-gray-300 rounded-[5px] px-6 py-3 font-semibold text-white transition-colors"
                style="background-color: #FF5794;">
          Complete Payment Now
        </button>
        <button @click="cancelBooking" 
                class="flex-1 bg-white border border-gray-300 rounded-[5px] px-6 py-3 font-semibold text-red-600 hover:bg-red-50 transition-colors">
          Cancel Booking
        </button>
      </div>
      
      <p class="text-sm text-gray-500 border-t border-gray-200 pt-4">
        Your booking will be held for 24 hours. Complete payment to confirm your seats.
      </p>
    </div>

    <!-- Error State - NO SUCCESS STATE HERE -->
    <div v-else class="bg-white border border-gray-300 rounded-[5px] p-8 md:p-10 text-center max-w-lg w-full">
      <div class="text-6xl mb-4">❌</div>
      
      <h1 class="text-3xl font-bold text-gray-800 mb-3">Payment Unsuccessful</h1>
      
      <p class="text-lg text-red-600 mb-6">
        {{ errorMessage || 'We couldn\'t confirm your payment.' }}
      </p>
      
      <div class="flex flex-col md:flex-row gap-3 mb-6">
        <button @click="retryPayment" 
                class="flex-1 border border-gray-300 rounded-[5px] px-6 py-3 font-semibold text-white transition-colors"
                style="background-color: #FF5794;">
          Try Payment Again
        </button>
        <button @click="goHome" 
                class="flex-1 bg-white border border-gray-300 rounded-[5px] px-6 py-3 font-semibold text-gray-600 hover:bg-gray-50 transition-colors">
          Return to Home
        </button>
      </div>
      
      <div class="border-t border-gray-200 pt-6">
        <p class="text-sm text-gray-600">
          If this issue persists, please contact our support team at 
          <a href="mailto:support@airlines.com" class="font-medium underline" style="color: #FF5794;">
            support@airlines.com
          </a>
        </p>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* Custom animations */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>