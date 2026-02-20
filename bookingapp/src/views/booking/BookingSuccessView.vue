<template>
  <div class="min-h-screen bg-slate-50 py-20 px-4 md:px-8">
    <!-- Main Content Container -->
    <div class="max-w-3xl mx-auto text-center">
      <!-- Success Header Section -->
      <div class="mb-12">
        <h1 class="text-6xl md:text-7xl font-black text-slate-900 mb-8 tracking-tighter uppercase">
          Thank You!
        </h1>
        
        <!-- Large Green Checkmark -->
        <div class="flex justify-center mb-10">
          <div class="w-32 h-32 bg-emerald-500 rounded-lg flex items-center justify-center shadow-xl shadow-emerald-200">
            <svg class="w-20 h-20 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="4" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>

        <p class="text-xl text-slate-600 font-medium mb-2">
          Your e-ticket is on its way to your email. But first...
        </p>
      </div>

      <!-- Booking Summary Card -->
      <div class="bg-white rounded-xl border border-slate-200 p-8 mb-10 shadow-sm">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 text-left">
          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-widest font-black mb-1">Booking Reference</p>
            <div class="flex items-center gap-3">
              <span class="text-2xl font-mono font-bold text-slate-900 tracking-tighter">{{ bookingReference }}</span>
              <button @click="copyReference" class="text-emerald-600 text-[10px] uppercase font-black hover:text-emerald-700 transition-colors">Copy</button>
            </div>
          </div>
          
          <div>
            <p class="text-[10px] text-slate-400 uppercase tracking-widest font-black mb-1">Total Amount Paid</p>
            <span class="text-2xl font-bold text-slate-900">₱{{ formattedAmount }}</span>
          </div>

          <div class="md:col-span-2 pt-4 border-t border-slate-100 flex items-center gap-4">
             <div class="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center text-xl">
               💳
             </div>
             <div>
               <p class="text-[10px] text-slate-400 uppercase tracking-widest font-black">Transaction ID</p>
               <p class="text-sm font-mono text-slate-600">{{ transactionId }}</p>
             </div>
          </div>
        </div>
      </div>

      <!-- Actions Section -->
      <div class="space-y-4 max-w-sm mx-auto">
        <button @click="goToDashboard" 
                class="w-full cursor-pointer py-5 bg-slate-900 text-white rounded-lg font-black text-lg hover:bg-slate-700 transition-all shadow-lg hover:shadow-slate-200 mb-2">
          Return to Dashboard
        </button>

        <div v-if="!isActivity">
          <button @click="goHome" 
                  class="w-full py-4 text-emerald-600 font-black flex items-center justify-center gap-2 hover:text-emerald-500 cursor-pointer">
            <span class="underline" >Click here to start a new booking instantly.</span>
          </button>
        </div>
        <div v-else class="p-4 bg-slate-100 rounded-lg">
          <p class="text-slate-500 text-sm font-medium italic">
            "We can't wait to see you complete your session and master the skies!"
          </p>
        </div>
      </div>

      <!-- Share Link -->
      <div class="mt-12 pt-8 border-t border-slate-100">
        <button @click="copyBookingLink" class="text-slate-400 hover:text-slate-600 text-xs font-bold uppercase tracking-widest transition-colors flex items-center gap-2 mx-auto">
          <span>🔗 Share your journey link</span>
        </button>
      </div>
    </div>

    <!-- Minimal Toast Message -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      leave-active-class="transition-all duration-200 ease-in"
      enter-from-class="opacity-0 -translate-y-4"
      leave-to-class="opacity-0 -translate-y-4"
    >
      <div v-if="showToast" 
           class="fixed top-8 left-1/2 -translate-x-1/2 z-[100]">
        <div class="bg-slate-900 text-white px-6 py-3 rounded-full shadow-2xl flex items-center gap-3">
          <span class="text-emerald-400">✓</span>
          <p class="text-sm font-bold tracking-tight">{{ toastMessage }}</p>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useBookingStore } from '@/stores/booking';

const route = useRoute();
const router = useRouter();
const bookingStore = useBookingStore();

const bookingReference = ref('PAL' + Math.random().toString(36).substr(2, 9).toUpperCase());
const transactionId = ref('TRX' + Math.random().toString(36).substr(2, 12).toUpperCase());
const amountPaid = ref(12500.50);
const showToast = ref(false);
const toastMessage = ref('');

const formattedAmount = computed(() => {
  return amountPaid.value.toLocaleString('en-PH', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
});

onMounted(() => {
  const query = route.query;
  
  if (query.ref) {
    bookingReference.value = query.ref;
    localStorage.setItem('last_booking_ref', query.ref);
  }
  
  if (query.payment_id) {
    transactionId.value = query.payment_id;
  }
  
  if (query.amount) {
    amountPaid.value = parseFloat(query.amount);
  }
  
  if (!bookingReference.value) {
    bookingReference.value = localStorage.getItem('last_booking_ref') || 'PAL' + Math.random().toString(36).substr(2, 9).toUpperCase();
  }
});

const copyReference = () => {
  navigator.clipboard.writeText(bookingReference.value);
  showToastMessage('Booking reference copied');
};

const copyBookingLink = () => {
  const link = `${window.location.origin}/booking/${bookingReference.value}`;
  navigator.clipboard.writeText(link);
  showToastMessage('Booking link copied');
};

const showToastMessage = (message) => {
  toastMessage.value = message;
  showToast.value = true;
  setTimeout(() => {
    showToast.value = false;
  }, 3000);
};

const isActivity = computed(() => !!bookingStore.activityCode);

const goToDashboard = () => {
  showToastMessage('Returning to dashboard...');
  bookingStore.clearActivityCodeValidation();
  bookingStore.resetBooking();
  localStorage.removeItem('payment_session');
  localStorage.removeItem('current_booking');
  router.push({ name: 'StudentDashboard' });
};

const goHome = () => {
  if (isActivity.value) {
    showToastMessage('Action unavailable during activity');
    return;
  }
  showToastMessage('Starting new booking...');
  bookingStore.resetBooking();
  router.push({ name: 'Home' });
};
</script>

<style scoped>
/* Smooth transitions */
* {
  scroll-behavior: smooth;
}
</style>