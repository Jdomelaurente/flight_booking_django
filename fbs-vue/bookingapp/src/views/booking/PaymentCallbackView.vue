<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useBookingStore } from '@/stores/booking';
import { paymentPollingService } from '@/services/booking/paymentPollingService';
import api from '@/services/booking/api';
import { useNotificationStore } from '@/stores/notification';
import { useModalStore } from '@/stores/modal';
import LoadingOverlay from '@/components/common/LoadingOverlay.vue';

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
const hasRedirected = ref(false); // Guard against double-redirects
const isPolling = ref(false); // Mutex lock

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
  // Stop if we've already redirected or if a poll is currently running
  if (hasRedirected.value || isPolling.value) {
    if (hasRedirected.value) clearInterval(pollingInterval.value);
    return;
  }
  
  isPolling.value = true;

  if (pollingCount.value >= maxPollingAttempts) {
    clearInterval(pollingInterval.value);
    showIncompleteState.value = true;
    loading.value = false;
    isPolling.value = false;
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
      hasRedirected.value = true;
      
      // Prepare data for success page
      const bookingReference = result.data.booking_reference || `CSUCC${bookingId.toString().padStart(8, '0')}`;
      const paymentId = result.data.payment_id;
      const amount = bookingStore.booking_total || bookingStore.grandTotal;
      
      console.log('Payment successful! Navigating to success page with:', {
        ref: bookingReference,
        payment_id: paymentId,
        amount: amount
      });
      
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
      
    } else {
      console.log('Payment still pending, continuing poll...');
    }
    
  } catch (error) {
    console.error('Polling error:', error);
  } finally {
    isPolling.value = false;
  }
};

const startPolling = (bookingId) => {
  // Clear any existing interval
  if (pollingInterval.value) clearInterval(pollingInterval.value);
  
  // Initial check
  pollPaymentStatus(bookingId);
  
  // Set interval
  pollingInterval.value = setInterval(() => {
    pollPaymentStatus(bookingId);
  }, 3000); // Poll every 3 seconds
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
      processingStatus.value = 'Verifying payment...';
      
      try {
        const verifyResponse = await api.post('verify-session-payment/', {
          booking_id: bookingId,
          session_id: sessionIdFromUrl,
          payment_success: 'true'
        });
        
        console.log('Direct verification response:', verifyResponse.data);
        
        if (verifyResponse.data.success) {
          const bookingReference = verifyResponse.data.booking_reference || `CSUCC${bookingId.toString().padStart(8, '0')}`;
          const paymentId = verifyResponse.data.payment_id;
          const amount = bookingStore.booking_total || bookingStore.grandTotal;
          
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
        }
      } catch (error) {
        console.log('Direct verification failed, falling back to polling:', error);
      }
    }
    
    startPolling(bookingId);
    
  } else if (paymentSuccess === 'false') {
    errorMessage.value = 'Payment was cancelled or failed by the provider.';
    loading.value = false;
  } else {
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
  if (bookingId) {
    router.push({
      name: 'Payment',
      query: { 
        bookingId: bookingId,
        retry: true 
      }
    });
  } else {
    router.push({ name: 'Home' });
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
      await api.post(`cancel-booking/${bookingId}/`);
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
  <div class="min-h-screen bg-gradient-to-br from-pink-50 via-white to-rose-50 flex justify-center items-center p-5 selection:bg-pink-100">
    
    <!-- Loading State - Premium Branding -->
    <LoadingOverlay 
      v-if="loading"
      :show="true" 
      :title="processingStatus || 'Verifying Your Payment'"
      :subtitle="pollingCount < maxPollingAttempts ? getLoadingMessage() : 'Verification is taking a bit longer than usual... Please stay with us.'"
    />

    <!-- Status Cards Container -->
    <transition 
      enter-active-class="transition duration-500 ease-out"
      enter-from-class="transform translate-y-8 opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
    >
      <div v-if="!loading" class="w-full max-w-2xl">
        <!-- Incomplete/Verification Status -->
        <div v-if="showIncompleteState" class="bg-white rounded-[2rem] border border-gray-100 shadow-2xl overflow-hidden">
          <div class="h-2 bg-gradient-to-r from-amber-400 to-orange-500"></div>
          
          <div class="p-8 sm:p-12 text-center">
            <div class="w-20 h-20 bg-amber-50 rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-inner ring-4 ring-amber-50/50 float-animation">
              <span class="text-3xl">🔄</span>
            </div>
            
            <h1 class="text-3xl font-black text-slate-800 mb-3 tracking-tight">Payment Verification Needed</h1>
            
            <p class="text-[15px] text-slate-500 font-medium mb-10 max-w-md mx-auto leading-relaxed">
              We couldn't finalize your payment confirmation in time. This sometimes happens due to provider delays.
            </p>
            
            <!-- Summary Info -->
            <div class="grid grid-cols-2 gap-4 mb-10">
              <div class="bg-slate-50 rounded-2xl p-4 border border-slate-100/50 text-left">
                <p class="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-1">REFERENCE</p>
                <p class="text-sm font-black text-pink-500 font-mono">{{ bookingStore.booking_reference || bookingId }}</p>
              </div>
              <div class="bg-slate-50 rounded-2xl p-4 border border-slate-100/50 text-right">
                <p class="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-1">TOTAL AMOUNT</p>
                <p class="text-sm font-black text-slate-800">₱{{ (bookingStore.booking_total || bookingStore.grandTotal)?.toLocaleString() }}</p>
              </div>
            </div>
            
            <div class="flex flex-col sm:flex-row gap-4">
              <button @click="retryPayment" 
                      class="flex-1 bg-pink-500 hover:bg-pink-600 text-white px-8 py-4 rounded-xl font-bold text-sm uppercase tracking-widest transition-all shadow-xl shadow-pink-100 active:scale-[0.98]">
                Complete Payment
              </button>
              <button @click="cancelBooking" 
                      class="flex-1 bg-white border-2 border-slate-100 hover:border-slate-200 px-8 py-4 rounded-xl font-bold text-sm uppercase tracking-widest text-slate-400 hover:text-slate-600 transition-all">
                Cancel Booking
              </button>
            </div>
            
            <p class="mt-8 text-[11px] text-slate-400 font-medium flex items-center justify-center gap-2">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
              Secure Transaction Monitoring Active
            </p>
          </div>
        </div>

        <!-- Error State -->
        <div v-else class="bg-white rounded-[2rem] border border-gray-100 shadow-2xl overflow-hidden">
          <div class="h-2 bg-rose-500"></div>
          
          <div class="p-8 sm:p-12 text-center">
            <div class="w-20 h-20 bg-rose-50 rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-inner ring-4 ring-rose-50/50">
              <span class="text-3xl">❌</span>
            </div>
            
            <h1 class="text-3xl font-black text-slate-800 mb-3 tracking-tight">Payment Unsuccessful</h1>
            
            <p class="text-[16px] text-rose-500 font-bold mb-10 leading-relaxed max-w-md mx-auto">
              {{ errorMessage || 'We couldn\'t process your payment. Please try again or choose a different method.' }}
            </p>
            
            <div class="space-y-4">
              <button @click="retryPayment" 
                      class="w-full bg-slate-900 border-2 border-slate-900 hover:bg-black text-white py-4 rounded-xl font-bold text-sm uppercase tracking-widest transition-all shadow-xl shadow-slate-200 active:scale-[0.98]">
                Try Payment Again
              </button>
              <button @click="goHome" 
                      class="w-full bg-white border-2 border-slate-100 hover:border-slate-200 text-slate-400 hover:text-slate-600 py-4 rounded-xl font-bold text-sm uppercase tracking-widest transition-all">
                Return to Home
              </button>
            </div>
          </div>
          
          <div class="bg-slate-50 p-6 text-center border-t border-slate-100">
             <p class="text-[11px] text-slate-400 font-medium">
               Assistance needed? <a href="mailto:support@airline.com" class="text-pink-500 font-black hover:underline">support@airline.com</a>
             </p>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.float-animation {
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* Page transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>