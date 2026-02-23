<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50 p-4 md:p-8 relative overflow-hidden">
    <!-- Background Elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-0 right-0 w-1/3 h-1/3 bg-gradient-to-br from-[#FF579A]/5 to-transparent rounded-[2px] blur-3xl"></div>
      <div class="absolute bottom-0 left-0 w-1/3 h-1/3 bg-gradient-to-tr from-gray-400/5 to-transparent rounded-[2px] blur-3xl"></div>
    </div>

    <!-- Main Container -->
    <div class="relative max-w-6xl mx-auto">
      
      <!-- Loading State -->
      <div v-if="loading" class="bg-white rounded-[5px] border border-gray-100 shadow-xl p-12 text-center max-w-lg mx-auto mt-20">
        <div class="relative inline-flex mb-8">
          <div class="w-20 h-20 border-4 border-pink-50 rounded-[2px] animate-pulse"></div>
          <div class="absolute inset-0 w-20 h-20 border-4 border-[#FF579A] border-t-transparent rounded-[2px] animate-spin"></div>
        </div>
        <h3 class="text-2xl font-black text-gray-900 mb-2 uppercase tracking-tight">{{ loadingMessage }}</h3>
        <p class="text-gray-400 text-sm font-medium">Please do not refresh or close this window.</p>
      </div>

      <!-- Session Expired -->
      <div v-else-if="!isSessionValid" class="bg-white rounded-[5px] border border-gray-100 shadow-xl p-12 text-center max-w-lg mx-auto mt-20">
        <div class="w-20 h-20 bg-amber-50 rounded-[5px] flex items-center justify-center mx-auto mb-8 float-animation">
          <span class="text-3xl">⏰</span>
        </div>
        <h3 class="text-2xl font-black text-gray-900 mb-3">SESSION EXPIRED</h3>
        <p class="text-gray-400 text-sm mb-10 leading-relaxed font-medium">
          Your secure booking session has timed out. Please restart the booking process to ensure your seat remains available.
        </p>
        <button @click="restartBooking" 
                class="w-full bg-gray-900 hover:bg-black text-white py-4 rounded-[5px] font-bold transition-all active:scale-[0.98] shadow-lg shadow-gray-200">
          Start New Booking
        </button>
      </div>

      <!-- Main Content -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <!-- Left Column - Booking details & Summary -->
        <div class="lg:col-span-8 space-y-6">
          
          <!-- Premium Amount Display -->
          <div class="relative overflow-hidden bg-white rounded-[5px] border border-gray-100 shadow-sm p-1">
            <div class="absolute top-0 right-0 p-4">
              <div class="flex items-center space-x-2 px-3 py-1 bg-green-50 text-green-700 rounded-[2px] text-xs font-bold border border-green-100 uppercase tracking-tighter">
                <span class="w-1.5 h-1.5 bg-green-500 rounded-[2px] animate-pulse mr-1"></span>
                Secure Session
              </div>
            </div>
            
            <div class="bg-gradient-to-br from-gray-50/50 to-white p-8 rounded-[2px]">
              <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                  <h2 class="text-sm font-bold text-gray-400 uppercase tracking-[0.2em] mb-3">Total Amount to Pay</h2>
                  <div class="flex items-baseline">
                    <span class="text-2xl font-light text-gray-400 mr-2">₱</span>
                    <span class="text-6xl font-black text-gray-900 tracking-tight">{{ totalAmount.toLocaleString() }}</span>
                  </div>
                  <p class="text-gray-400 text-xs mt-3 flex items-center">
                    <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                    Final price inclusive of taxes and surcharge
                  </p>
                </div>
                
                <div class="flex flex-col items-end">
                  <div class="text-right mb-4">
                    <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Booking Ref</p>
                    <p class="text-xl font-mono font-black text-[#FF579A]">{{ bookingReference || 'N/A' }}</p>
                  </div>
                  <div class="px-4 py-2 bg-amber-50 rounded-[5px] border border-amber-100 flex items-center">
                    <span class="text-amber-700 text-xs font-bold uppercase tracking-wider">{{ bookingStatus }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Trip Overview -->
          <div class="bg-white rounded-[5px] border border-gray-100 shadow-sm overflow-hidden">
            <div class="border-b border-gray-50 px-8 py-5 flex items-center justify-between bg-gray-50/30">
              <h3 class="text-lg font-bold text-gray-800">Trip Overview</h3>
              <div class="flex items-center space-x-2">
                <span class="text-xs font-bold px-3 py-1 bg-[#FF579A]/10 text-[#FF579A] rounded-[2px] uppercase tracking-wider">
                  {{ tripTypeLabel }}
                </span>
              </div>
            </div>
            
            <div class="p-8">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-10">
                <!-- Flight Info -->
                <div class="space-y-6">
                  <!-- Depart -->
                  <div v-if="bookingStore.selectedOutbound" class="relative pl-8">
                    <div class="absolute left-0 top-1 w-6 h-6 bg-pink-50 rounded-[2px] flex items-center justify-center">
                      <svg class="w-3 h-3 text-[#FF579A] rotate-45" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                    </div>
                    <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Outbound Flight</p>
                    <p class="text-lg font-bold text-gray-900 leading-tight">
                      {{ bookingStore.selectedOutbound.origin }} 
                      <span class="text-gray-300 mx-2">→</span>
                      {{ bookingStore.selectedOutbound.destination }}
                    </p>
                    <p class="text-xs text-gray-500 font-medium">Flight {{ bookingStore.selectedOutbound.flight_number }}</p>
                  </div>

                  <!-- Return -->
                  <div v-if="bookingStore.selectedReturn" class="relative pl-8">
                    <div class="absolute left-0 top-1 w-6 h-6 bg-blue-50 rounded-[2px] flex items-center justify-center">
                      <svg class="w-3 h-3 text-blue-500 -rotate-135" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                    </div>
                    <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Return Flight</p>
                    <p class="text-lg font-bold text-gray-900 leading-tight">
                      {{ bookingStore.selectedReturn.origin }} 
                      <span class="text-gray-300 mx-2">→</span>
                      {{ bookingStore.selectedReturn.destination }}
                    </p>
                    <p class="text-xs text-gray-500 font-medium">Flight {{ bookingStore.selectedReturn.flight_number }}</p>
                  </div>
                </div>

                <!-- Traveler Info -->
                <div class="bg-gray-50/50 rounded-[5px] p-6 border border-gray-100/50">
                  <div class="flex items-center space-x-3 mb-6">
                    <div class="w-10 h-10 bg-white shadow-sm rounded-[2px] flex items-center justify-center">
                      <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Main Contact</p>
                      <p class="text-sm font-bold text-gray-900">{{ contactName }}</p>
                    </div>
                  </div>
                  
                  <div class="space-y-3">
                    <div class="flex items-center text-xs text-gray-500">
                      <svg class="w-3.5 h-3.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      {{ bookingStore.contactInfo.email }}
                    </div>
                    <div class="flex items-center text-xs text-gray-500">
                      <svg class="w-3.5 h-3.5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      +63 {{ bookingStore.contactInfo.phone }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column - Payment Panel -->
        <div class="lg:col-span-4 space-y-6">
          <div class="bg-white rounded-[5px] border border-gray-100 shadow-lg shadow-pink-100/20 overflow-hidden">
            <div class="p-8">
              <h3 class="text-xl font-bold text-gray-900 mb-2">Secure Checkout</h3>
              <p class="text-xs text-gray-400 mb-8 leading-relaxed">You will be redirected to our secure payment gateway to complete your transaction. All major credit cards and e-wallets are supported.</p>

              <!-- Main Action -->
              <div class="mt-8 pt-8 border-t border-gray-50">
                <button @click="handlePayMongoCheckout" 
                        :disabled="loading || !bookingId"
                        class="w-full py-4 bg-[#FF579A] hover:bg-[#FF4081] text-white rounded-[5px] font-bold shadow-lg shadow-pink-200 transition-all active:scale-[0.98] disabled:opacity-50 disabled:translate-y-0">
                  {{ loading ? 'Processing...' : 'Proceed to Payment' }}
                </button>
                
                <button @click="goBack" 
                        class="w-full mt-4 py-3 text-sm font-bold text-gray-400 hover:text-gray-600 transition-colors uppercase tracking-widest">
                  Back to Review
                </button>
              </div>
            </div>
          </div>

          <!-- Trust Badges -->
          <div class="flex items-center justify-center space-x-6 px-4">
            <div class="flex flex-col items-center opacity-30 grayscale hover:opacity-100 hover:grayscale-0 transition-all">
               <span class="text-[10px] font-black uppercase tracking-tighter">PCI DSS</span>
               <span class="text-[8px] text-gray-500 font-bold">COMPLIANT</span>
            </div>
            <div class="flex flex-col items-center opacity-30 grayscale hover:opacity-100 hover:grayscale-0 transition-all">
               <span class="text-[10px] font-black uppercase tracking-tighter">SECURE</span>
               <span class="text-[8px] text-gray-500 font-bold">256-BIT SSL</span>
            </div>
          </div>

          <!-- Help Section -->
          <div class="bg-gradient-to-br from-gray-900 to-black rounded-[5px] p-8 text-white relative overflow-hidden group border border-white/5">
            <div class="absolute -right-4 -bottom-4 w-24 h-24 bg-white/5 rounded-[2px] blur-2xl group-hover:scale-150 transition-transform duration-700"></div>
            <h4 class="font-bold text-lg mb-4 flex items-center text-white">
              <span class="w-8 h-8 bg-white/10 rounded-[5px] flex items-center justify-center mr-3 text-sm">?</span>
              Need Help?
            </h4>
            <div class="space-y-4">
              <a href="tel:+63288558888" 
                 class="flex items-center space-x-4 text-gray-400 hover:text-white transition-all group/link">
                <div class="w-10 h-10 rounded-[5px] bg-white/5 flex items-center justify-center group-hover/link:bg-white/10 transition-colors">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                </div>
                <div>
                  <p class="text-[10px] uppercase font-black tracking-widest text-[#FF579A]">Call Us</p>
                  <p class="text-sm font-bold text-white">(02) 8855-8888</p>
                </div>
              </a>
              <a href="mailto:support@philippineairlines.com" 
                 class="flex items-center space-x-4 text-gray-400 hover:text-white transition-all group/link">
                <div class="w-10 h-10 rounded-[5px] bg-white/5 flex items-center justify-center group-hover/link:bg-white/10 transition-colors">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <p class="text-[10px] uppercase font-black tracking-widest text-[#FF579A]">Email Us</p>
                  <p class="text-sm font-bold text-white">Payment Support</p>
                </div>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      leave-active-class="transition-all duration-200 ease-in"
      enter-from-class="opacity-0 translate-y-2"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div v-if="showToast" 
           class="fixed bottom-6 right-6 bg-gradient-to-r from-[#FF579A] to-pink-500 text-white px-6 py-4 rounded-[5px] shadow-2xl flex items-center space-x-3 max-w-sm z-50">
        <div class="w-6 h-6 bg-white/20 rounded-[2px] flex items-center justify-center">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <span class="font-bold text-sm tracking-tight">{{ toastMessage }}</span>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useRouter } from 'vue-router';
import api from '@/services/booking/api';

const bookingStore = useBookingStore();
const router = useRouter();

const loading = ref(false);
const loadingMessage = ref("");
const showToast = ref(false);
const toastMessage = ref("");

// Computed properties
const bookingId = computed(() => bookingStore.booking_id);
const bookingReference = computed(() => bookingStore.booking_reference);
const bookingStatus = computed(() => bookingStore.booking_status || 'pending');
const tripTypeLabel = computed(() => bookingStore.isRoundTrip ? 'Round Trip' : 'One Way');

const contactName = computed(() => {
  const info = bookingStore.contactInfo;
  return `${info.title || ''} ${info.firstName || ''} ${info.lastName || ''}`.trim() || 'Not specified';
});

const totalAmount = computed(() => {
  if (bookingStore.booking_total > 0) {
    console.log('💰 PaymentView: Using Store booking_total (from backend sync):', bookingStore.booking_total);
    return bookingStore.booking_total;
  }
  console.log('⚠️ PaymentView: No backend synced total, using Store grandTotal:', bookingStore.grandTotal);
  return bookingStore.grandTotal || 0;
});

const hasFlightInfo = computed(() => {
  return bookingStore.selectedOutbound || bookingStore.selectedReturn;
});

const isSessionValid = computed(() => {
  if (!bookingStore.sessionExpiry) return false;
  return Date.now() < bookingStore.sessionExpiry;
});

const syncBookingTotalFromBackend = async () => {
  try {
    if (!bookingStore.booking_id) return;
    const res = await api.get(`flightapp/booking/${bookingStore.booking_id}/`);
    if (res.data?.success && res.data?.booking) {
      const backendTotal = parseFloat(res.data.booking.total_amount);
      if (Number.isFinite(backendTotal) && backendTotal > 0) {
        bookingStore.booking_total = backendTotal;
        localStorage.setItem('current_booking_total', backendTotal);
      }
    }
  } catch (error) {
    console.error('Failed to sync booking total from backend:', error.response?.data || error.message);
  }
};

/**
 * Show toast message
 */
const showToastMessage = (message, duration = 3000) => {
  toastMessage.value = message;
  showToast.value = true;
  setTimeout(() => {
    showToast.value = false;
  }, duration);
};

/**
 * Restores booking data from localStorage if store is empty
 */
const restoreBookingData = () => {
  if (bookingStore.booking_id) return;
  
  try {
    const savedBooking = localStorage.getItem('current_booking');
    if (savedBooking) {
      const bookingData = JSON.parse(savedBooking);
      
      const bookingAge = Date.now() - new Date(bookingData.created_at).getTime();
      const thirtyMinutes = 30 * 60 * 1000;
      
      if (bookingAge < thirtyMinutes) {
        bookingStore.saveBookingConfirmation({
          booking_id: bookingData.id,
          booking_reference: bookingData.reference,
          status: bookingData.status,
          total_amount: bookingData.total
        });
        
        bookingStore.sessionExpiry = Date.now() + (15 * 60 * 1000);
      } else {
        localStorage.removeItem('current_booking');
      }
    }
  } catch (error) {
    console.error('Error restoring booking data:', error);
  }
};

/**
 * Go back to review page
 */
const goBack = () => {
  router.back();
};

/**
 * Restarts the booking process
 */
const restartBooking = () => {
  bookingStore.resetBooking();
  localStorage.removeItem('current_booking');
  router.push({ name: 'SearchFlights' });
};

/**
 * Handle PayMongo Checkout
 */
const handlePayMongoCheckout = async () => {
  if (!isSessionValid.value) {
    showToastMessage("Booking session expired. Please restart your booking.");
    restartBooking();
    return;
  }

  if (!bookingStore.booking_id) {
    showToastMessage("No booking ID found. Please complete your booking details first.");
    goBack();
    return;
  }

  loading.value = true;
  loadingMessage.value = "Creating secure payment session...";

  try {
    const paymentData = {
      amount: totalAmount.value,
      booking_id: bookingStore.booking_id,
      customer_email: bookingStore.contactInfo.email || 'test@example.com',
      customer_name: `${bookingStore.contactInfo.firstName || 'Customer'} ${bookingStore.contactInfo.lastName || ''}`.trim(),
      customer_phone: bookingStore.contactInfo.phone || '09171234567'
    };

    const response = await api.post('flightapp/create-checkout-session/', paymentData);

    if (response.data && response.data.success === true && response.data.checkout_url) {
      localStorage.setItem('payment_session', JSON.stringify({
        checkout_url: response.data.checkout_url,
        booking_id: bookingStore.booking_id,
        booking_reference: bookingStore.booking_reference,
        amount: totalAmount.value,
        timestamp: Date.now()
      }));

      loading.value = false;
      loadingMessage.value = "";
      
      setTimeout(() => {
        window.location.href = response.data.checkout_url;
      }, 500);
      
    } else {
      let errorMsg = 'Failed to create checkout session';
      if (response.data && response.data.error) {
        errorMsg = typeof response.data.error === 'string' ? response.data.error : JSON.stringify(response.data.error);
      }
      showToastMessage(`Payment setup failed: ${errorMsg}`);
      loading.value = false;
    }
  } catch (error) {
    console.error("PayMongo Checkout Error:", error);
    showToastMessage("Payment Error: Failed to initialize payment gateway.");
    loading.value = false;
  }
};


// Lifecycle hooks
onMounted(() => {
  restoreBookingData();
  syncBookingTotalFromBackend();
  checkPaymentCallback();
});

/**
 * Check for payment callback parameters
 */
const checkPaymentCallback = () => {
  const urlParams = new URLSearchParams(window.location.search);
  const success = urlParams.get('success');
  const error = urlParams.get('error');
  const bookingId = urlParams.get('booking_id');
  
  if (success === 'true' && bookingId) {
    showToastMessage('Payment successful! Your booking has been confirmed.');
    window.history.replaceState({}, document.title, window.location.pathname);
  } else if (error) {
    showToastMessage(`Payment failed: ${decodeURIComponent(error)}`);
    window.history.replaceState({}, document.title, window.location.pathname);
  }
};

onUnmounted(() => {
  // Clean up
});
</script>

<style scoped>
/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f8fafc;
}

::-webkit-scrollbar-thumb {
  background: #FF579A;
  border-radius: 10px;
}

/* Transitions */
.fade-up-enter-active, .fade-up-leave-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.fade-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}

.float-animation {
  animation: float 6s ease-in-out infinite;
}

/* Smooth transitions */
* {
  scroll-behavior: smooth;
}

/* Pulse animation for status */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Button active state */
button:active {
  transform: scale(0.98);
}
</style>