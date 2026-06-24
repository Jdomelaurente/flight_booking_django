<template>
  <div class="activity-code-modal" v-if="isOpen">
    <div class="modal-overlay" @click="closeModal"></div>
    <div class="modal-content">
      <div class="modal-header">
        <h2>Start Your Booking</h2>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>

      <div class="modal-body">
        <p class="description">
          Choose how you'd like to proceed with your flight booking:
        </p>

        <!-- Activity Code Option -->
        <div class="option-card" :class="{ active: mode === 'graded' }">
          <div class="option-header" @click="mode = 'graded'">
            <input type="radio" name="booking-mode" value="graded" v-model="mode" />
            <div class="option-info">
              <h3>📚 Graded Activity</h3>
              <p>Enter an activity code from your instructor</p>
            </div>
          </div>

          <div class="activity-code-input" v-if="mode === 'graded'">
            <label for="activity-code">Activity Code</label>
            <input
              type="text"
              id="activity-code"
              v-model="activityCode"
              placeholder="Enter code (e.g., ABC12345)"
              @input="activityCode = activityCode.toUpperCase()"
              maxlength="8"
            />
            <p class="error-message" v-if="error">{{ error }}</p>
            <p class="success-message" v-if="validatedActivity">
              ✅ Valid code for: {{ validatedActivity.title }}
            </p>
          </div>
        </div>

        <!-- Practice Mode Option -->
        <div class="option-card" :class="{ active: mode === 'practice' }">
          <div class="option-header" @click="mode = 'practice'">
            <input type="radio" name="booking-mode" value="practice" v-model="mode" />
            <div class="option-info">
              <h3>🎯 Practice Mode</h3>
              <p>Book a flight for practice (not graded)</p>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" @click="closeModal">Cancel</button>
        <button 
          class="btn-primary" 
          @click="handleContinue"
          :disabled="loading || (mode === 'graded' && !activityCode)"
        >
          {{ loading ? 'Validating...' : 'Continue' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useBookingStore } from '@/stores/booking';
import api from '@/services/api/axios';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close', 'continue']);

const bookingStore = useBookingStore();

const mode = ref('graded');
const activityCode = ref('');
const error = ref('');
const loading = ref(false);
const validatedActivity = ref(null);

// Clear error when activity code changes
watch(activityCode, () => {
  error.value = '';
  validatedActivity.value = null;
});

const closeModal = () => {
  emit('close');
};

const validateActivityCode = async () => {
  if (!activityCode.value || activityCode.value.length < 6) {
    error.value = 'Please enter a valid activity code';
    return false;
  }

  loading.value = true;
  error.value = '';

  try {
    const response = await api.post(
      'validate-activity-code/',
      { activity_code: activityCode.value }
    );

    if (response.data.success) {
      validatedActivity.value = response.data.activity;
      return true;
    } else {
      error.value = response.data.error || 'Invalid activity code';
      return false;
    }
  } catch (err) {
    console.error('Activity code validation error:', err);
    if (err.response?.status === 401) {
      error.value = 'Please log in to validate activity code';
    } else if (err.response?.status === 403) {
      error.value = err.response.data.error || 'You are not enrolled in this activity';
    } else {
      error.value = err.response?.data?.error || 'Failed to validate activity code';
    }
    return false;
  } finally {
    loading.value = false;
  }
};

const handleContinue = async () => {
  if (mode.value === 'graded') {
    // Validate activity code
    const isValid = await validateActivityCode();
    if (!isValid) return;

    // Set activity code in store
    bookingStore.setActivityCode(activityCode.value, validatedActivity.value);
  } else {
    // Set practice mode
    bookingStore.setPracticeMode();
  }

  emit('continue');
  closeModal();
};
</script>

<style scoped>
.activity-code-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.modal-content {
  position: relative;
  background: white;
  border-radius: 16px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 32px;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #111827;
}

.modal-body {
  padding: 24px;
}

.description {
  margin: 0 0 24px 0;
  color: #6b7280;
  font-size: 15px;
}

.option-card {
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.option-card:hover {
  border-color: #3b82f6;
  background: #f9fafb;
}

.option-card.active {
  border-color: #3b82f6;
  background: #eff6ff;
}

.option-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.option-header input[type="radio"] {
  margin-top: 4px;
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.option-info {
  flex: 1;
}

.option-info h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.option-info p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.activity-code-input {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.activity-code-input label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.activity-code-input input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  font-family: monospace;
  text-transform: uppercase;
  transition: border-color 0.2s;
}

.activity-code-input input:focus {
  outline: none;
  border-color: #3b82f6;
}

.error-message {
  margin: 8px 0 0 0;
  color: #ef4444;
  font-size: 14px;
}

.success-message {
  margin: 8px 0 0 0;
  color: #10b981;
  font-size: 14px;
  font-weight: 500;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid #e5e7eb;
}

.btn-secondary,
.btn-primary {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}
</style>
