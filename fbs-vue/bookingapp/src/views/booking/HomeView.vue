<template>
  <div class="min-h-screen bg-gray-50">
    <section class="hero relative flex items-center justify-center text-white py-16 md:py-32 lg:py-40">
      <div class="container mx-auto px-4 space-y-6 relative z-10">
        <div class="flex flex-col md:flex-row md:items-center gap-4 md:gap-6">
          <h1 class="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-black tracking-tight drop-shadow-lg leading-tight">
            Welcome Home, Mabuhay!
          </h1>
          
          <!-- Badges -->
          <div class="flex flex-wrap gap-2">
            <!-- Practice Mode Badge -->
            <div v-if="bookingStore.isPractice" class="flex items-center gap-2 bg-blue-100/90 backdrop-blur-sm border border-blue-200 px-4 py-1.5 rounded-full shadow-sm">
              <span class="flex h-2 w-2 rounded-full bg-blue-500"></span>
              <span class="text-[10px] font-black text-blue-700 uppercase tracking-widest leading-none">Practice Mode Active</span>
            </div>
            <!-- Activity Mode Badge -->
            <div v-else-if="bookingStore.activityCode" class="flex items-center gap-2 bg-pink-100/90 backdrop-blur-sm border border-pink-200 px-4 py-1.5 rounded-full shadow-sm">
              <span class="flex h-2 w-2 rounded-full bg-pink-500 animate-pulse"></span>
              <span class="text-[10px] font-black text-pink-700 uppercase tracking-widest leading-none">Activity: {{ bookingStore.activityCode }}</span>
            </div>
          </div>
        </div>
        
        <p class="text-sm md:text-base lg:text-lg mb-8 opacity-90 max-w-2xl font-medium leading-relaxed">
          Book your next adventure across the Philippines and beyond. Experience the warmth of Filipino hospitality from takeoff to landing.
        </p>
        
        <div class="text-slate-900 mt-8">
          <FlightSearch />
        </div>
      </div>
      
      <!-- Overlay to ensure text readability -->
      <div class="absolute inset-0 bg-black/20 z-0"></div>
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
    
    // Skip auto-reset if in practice mode, activity mode, or if user is an instructor
    if (bookingStore.hasActivityCodeValidation) {
      console.log('🎯 Booking session active (Activity or Practice) - preserving session state');
      return;
    }
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