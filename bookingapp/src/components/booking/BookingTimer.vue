<template>
  <div v-if="timeLeftSeconds > 0" 
       :class="[variant === 'sidebar' ? 'timer-sidebar' : 'timer-banner', 
                { 'timer-warn': timeLeftSeconds < 120 }]">
    <span class="clock-icon">{{ variant === 'sidebar' ? '⌚' : '⏳' }}</span>
    <span class="timer-text">
      {{ variant === 'sidebar' ? 'Session Expires In' : 'Session expires in' }}: 
      <strong>{{ formattedTime }}</strong>
    </span>
  </div>
</template>

<script setup>
import { defineProps, onMounted, onUnmounted, ref, computed } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useRouter } from 'vue-router';
import { useNotificationStore } from '@/stores/notification';

const props = defineProps({
  variant: {
    type: String,
    default: 'banner' // 'banner' or 'sidebar'
  }
});

const bookingStore = useBookingStore();
const router = useRouter();
const notificationStore = useNotificationStore();

const currentTime = ref(Date.now());
let interval = null;
let hasNotified = false;

const timeLeftSeconds = computed(() => {
  if (!bookingStore.sessionExpiry) return 0;
  return Math.max(0, Math.round((bookingStore.sessionExpiry - currentTime.value) / 1000));
});

const formattedTime = computed(() => {
  const diff = timeLeftSeconds.value;
  const mins = Math.floor(diff / 60);
  const secs = diff % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
});

const tick = () => {
  currentTime.value = Date.now();
  
  const secondsLeft = timeLeftSeconds.value;

  if (secondsLeft <= 0 && bookingStore.sessionExpiry) {
    handleTimeout();
  }
  
  // Proximity notification at 2 minutes
  if (secondsLeft <= 120 && secondsLeft > 115 && !hasNotified) {
    notificationStore.info("Your flight price is locked for 2 more minutes. Need more time?");
    hasNotified = true;
  }
  
  // Reset notification flag if session is extended or restarted
  if (secondsLeft > 120) {
    hasNotified = false;
  }
};

const handleTimeout = () => {
  if (interval) clearInterval(interval);
  notificationStore.error("Your booking session has expired. Please start over.");
  bookingStore.resetBooking();
  router.push({ name: 'Home' });
};

onMounted(() => {
  // If no session exists, start one (usually happens at flight selection)
  if (!bookingStore.sessionExpiry) {
    bookingStore.startSession();
  }
  
  currentTime.value = Date.now();
  interval = setInterval(tick, 1000);
});

onUnmounted(() => {
  if (interval) clearInterval(interval);
});
</script>

<style scoped>
.timer-banner {
  background: #003870; 
  color: white;
  padding: 10px;
  text-align: center;
  position: sticky;
  top: 0;
  z-index: 1000;
  font-size: 0.9rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.timer-sidebar {
  background: #F8F9FA;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #666;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}

.timer-warn.timer-banner {
  background: #d11241;
}

.timer-warn.timer-sidebar {
  background: #FFF5F5;
  border-color: #FED7D7;
  color: #C53030;
  animation: pulse-border 2s infinite;
}

@keyframes pulse-border {
  0% { border-color: #FED7D7; }
  50% { border-color: #FC8181; }
  100% { border-color: #FED7D7; }
}

.timer-text strong { 
  margin-left: 5px; 
  font-family: monospace; 
  font-size: 1.1rem; 
}

.timer-warn.timer-sidebar .timer-text strong {
  color: #D32F2F;
}

.timer-banner .timer-text strong {
  color: white;
}
</style>