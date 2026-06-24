<template>
  <div v-if="isVisible" class="mobile-booking-footer">
    <div class="footer-content">
      <div class="total-info">
        <span class="label">Total Amount</span>
        <span class="amount">₱{{ totalAmount.toLocaleString() }}</span>
      </div>
      <button 
        class="next-btn" 
        :disabled="disabled || loading"
        @click="$emit('next')"
      >
        <span v-if="loading">Processing...</span>
        <span v-else>{{ buttonText }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useBookingStore } from '@/stores/booking';

const props = defineProps({
  buttonText: {
    type: String,
    default: 'Continue'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
});

defineEmits(['next']);

const bookingStore = useBookingStore();

const totalAmount = computed(() => bookingStore.grandTotal);

const isVisible = computed(() => {
  // Only show on mobile (visibility handled by CSS)
  return true;
});
</script>

<style scoped>
.mobile-booking-footer {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 12px 20px 24px; /* Extra padding for iOS home bar */
  box-shadow: 0 -10px 25px rgba(0, 0, 0, 0.08);
  z-index: 100;
  border-top: 1px solid rgba(226, 232, 240, 0.8);
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 600px;
  margin: 0 auto;
  gap: 15px;
}

.total-info {
  display: flex;
  flex-direction: column;
}

.total-info .label {
  font-size: 11px;
  color: #64748b;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.total-info .amount {
  font-size: 18px;
  font-weight: 800;
  color: #FF579A;
}

.next-btn {
  flex: 1;
  background: linear-gradient(135deg, #FF579A 0%, #0056b3 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 14px 20px;
  font-weight: 700;
  font-size: 15px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 56, 112, 0.2);
}

.next-btn:active {
  transform: scale(0.97);
  box-shadow: 0 2px 6px rgba(0, 56, 112, 0.15);
}

.next-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(0, 56, 112, 0.25);
}

.next-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

@media (max-width: 1024px) {
  .mobile-booking-footer {
    display: block;
  }
}

/* Ensure content above isn't hidden by the footer */
:global(body) {
  padding-bottom: 80px;
}

@media (min-width: 1025px) {
  :global(body) {
    padding-bottom: 0;
  }
}
</style>
