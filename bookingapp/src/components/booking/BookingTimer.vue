<template>
  <div v-if="timeLeft > 0" class="timer-banner" :class="{ 'timer-warn': timeLeft < 300 }">
    <span class="clock-icon">⏳</span>
    <span class="timer-text">Session expires in: <strong>{{ formattedTime }}</strong></span>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useRouter } from 'vue-router';
import { useNotificationStore } from '@/stores/notification';

const bookingStore = useBookingStore();
const router = useRouter();
const notificationStore = useNotificationStore();
const timeLeft = ref(0);
let interval = null;

const formattedTime = computed(() => {
  const mins = Math.floor(timeLeft.value / 60);
  const secs = timeLeft.value % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
});

const updateTimer = () => {
  if (!bookingStore.sessionExpiry) return;
  
  const now = Date.now();
  const diff = Math.round((bookingStore.sessionExpiry - now) / 1000);
  
  if (diff <= 0) {
    timeLeft.value = 0;
    clearInterval(interval);
    handleTimeout();
  } else {
    timeLeft.value = diff;
  }
};

const handleTimeout = () => {
  notificationStore.error("Your booking session has expired. Please start over.");
  bookingStore.resetBooking();
  router.push({ name: 'Home' }); // Or your search page
};

onMounted(() => {
  // If no session exists, start one (usually triggered on flight selection)
  if (!bookingStore.sessionExpiry) {
    bookingStore.startSession();
  }
  updateTimer();
  interval = setInterval(updateTimer, 1000);
});

onUnmounted(() => clearInterval(interval));
</script>

<style scoped>
.timer-banner {
  background: #003870; /* PAL Blue */
  color: white;
  padding: 10px;
  text-align: center;
  position: sticky;
  top: 0;
  z-index: 1000;
  font-size: 0.9rem;
}
.timer-warn {
  background: #d11241; /* PAL Red - Alert when under 5 mins */
}
.timer-text strong { margin-left: 5px; font-family: monospace; font-size: 1.1rem; }
</style>