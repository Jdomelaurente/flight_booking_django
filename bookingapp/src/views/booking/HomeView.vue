<template>
  <div class=" bg-gray-50">
    <section class="hero relative flex items-center justify-center text-white py-35 ">
      <div class="container mx-auto px-4 space-y-4 relative z-10">
        <h1 class="text-5xl   font-black  tracking-tight drop-shadow-lg">
          Welcome Home, Mabuhay!
        </h1>
        <p class="text-base mb-8  opacity-90 max-w-2xl font-medium">
          Book your next adventure across the Philippines and beyond.
        </p>
        
        <div class="text-slate-900">
          <FlightSearch />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useUserStore } from '@/stores/user';
import { useModalStore } from '@/stores/modal';
import { useNotificationStore } from '@/stores/notification';
import FlightSearch from '@/components/booking/FlightSearch.vue';

const bookingStore = useBookingStore();
const userStore = useUserStore();
const sessionCleared = ref(false);

// Clear any existing booking session when visiting home
onMounted(async () => {
  console.log('🏠 HomeView mounted - checking for active booking sessions...');
  
  // Ensure user data is loaded in store
  await userStore.ensureUserLoaded();
  
  // Check if there's an active session
  const session = bookingStore.checkSession();
  
  if (session.valid) {
    console.log('⚠️ Active booking session found. Checking if reset is needed...');
    
    // Skip auto-reset for instructors (they might be testing/demonstrating)
    if (userStore.isInstructor) {
       console.log('👨‍🏫 Instructor session - skipping automatic reset');
       return;
    }

    // Show confirmation if user has unsaved data
    if (bookingStore.passengers.length > 0 || bookingStore.selectedOutbound) {
      const modalStore = useModalStore();
      const notificationStore = useNotificationStore();
      
      const userConfirmed = await modalStore.confirm({
        title: 'Clear Active Session?',
        message: 'We found an active booking session. Would you like to start a new search? Your current booking data will be cleared.',
        confirmText: 'Start New Search',
        cancelText: 'Continue Previous'
      });
      
      if (userConfirmed) {
        bookingStore.resetBooking();
        localStorage.removeItem('payment_session');
        localStorage.removeItem('current_booking');
        sessionCleared.value = true;
        notificationStore.info('Previous session cleared.');
        
        // Hide message after 5 seconds
        setTimeout(() => {
          sessionCleared.value = false;
        }, 5000);
      } else {
        // Redirect to review if user wants to continue
        if (bookingStore.booking_id) {
          window.location.href = '/review/booking';
          return;
        }
      }
    } else {
      // Valid session but no real data - just ensure search state is clean
      bookingStore.resetBooking();
    }
  } else {
    // Session is invalid - clear everything if needed
    if (!userStore.isInstructor) {
      if (bookingStore.hasActivityCodeValidation) {
        console.log('🧹 Session invalid but validation remains - clearing everything');
        bookingStore.clearActivityCodeValidation();
      }
      bookingStore.resetBooking();
    }
  }
  
  // Log status for debugging
  console.log('📊 Current booking state after cleanup:', {
    hasBookingId: !!bookingStore.booking_id,
    hasPassengers: bookingStore.passengers.length,
    hasOutbound: !!bookingStore.selectedOutbound,
    hasReturn: !!bookingStore.selectedReturn,
    sessionExpired: !session.valid
  });
});
</script>

<style scoped>
.hero {
  /* Using #FF579A at 0.8 (80%) opacity per your request */
  background: 
              url('@/assets/image/bg-cthm.svg');
  background-size: cover;
  background-position: center;
}
</style>