<template>
  <div class="comparison-modal" v-if="isOpen">
    <div class="modal-overlay" @click="closeModal"></div>
    <div class="modal-content">
      <div class="modal-header">
        <div class="header-info">
          <h2>Activity Comparison</h2>
          <p class="subtitle">{{ activity?.title }}</p>
        </div>
        <div class="header-actions">
          <div v-if="grade !== null" class="grade-badge" :class="getGradeClass(grade)">
            Score: {{ grade }}/{{ activity?.total_points }}
          </div>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
      </div>

      <div class="modal-body" v-if="isLoading">
        <!-- Skeleton Loading State -->
        <div class="skeleton-summary animate-pulse">
          <div class="h-16 bg-gray-200 rounded-xl mb-6"></div>
        </div>
        
        <div class="comparison-grid skeleton">
          <div class="grid-header">Requirement</div>
          <div class="grid-header">Expected</div>
          <div class="grid-header">Actual</div>
          <div class="grid-header">Status</div>
          
          <template v-for="i in 5" :key="i">
            <div class="row-label"><div class="h-4 bg-gray-100 rounded w-24 animate-pulse"></div></div>
            <div class="cell"><div class="h-4 bg-gray-50 rounded w-32 animate-pulse"></div></div>
            <div class="cell"><div class="h-4 bg-gray-50 rounded w-28 animate-pulse"></div></div>
            <div class="status-cell"><div class="h-6 w-6 bg-gray-100 rounded-full animate-pulse"></div></div>
          </template>
        </div>

        <div class="mt-8">
          <div class="h-6 bg-gray-200 rounded w-48 mb-4 animate-pulse"></div>
          <div v-for="i in 2" :key="i" class="h-24 bg-gray-100 rounded-xl mb-3 animate-pulse"></div>
        </div>
      </div>

      <div class="modal-body flex flex-col items-center justify-center py-16 text-center" v-else-if="errorMessage">
        <div class="error-icon text-red-500 text-5xl mb-4">⚠️</div>
        <h3 class="text-xl font-bold text-gray-900 mb-2">Failed to load comparison</h3>
        <p class="text-gray-600 mb-6 max-w-xs">{{ errorMessage }}</p>
        <button class="btn-secondary" @click="closeModal">Close</button>
      </div>

      <div class="modal-body" v-else-if="activity && booking">
        <!-- Summary Strip -->
        <div class="status-summary" :class="allCorrect ? 'bg-green-50' : 'bg-red-50'">
          <div class="icon">
            <span v-if="allCorrect">✅</span>
            <span v-else>⚠️</span>
          </div>
          <div class="text">
            <h4 :class="allCorrect ? 'text-green-800' : 'text-red-800'">
              {{ allCorrect ? 'All requirements met!' : 'Some requirements were not met.' }}
            </h4>
            <p :class="allCorrect ? 'text-green-600' : 'text-red-600'">
              {{ allCorrect ? 'The booking matches the activity instructions perfectly.' : 'Check the details below to see the discrepancies.' }}
            </p>
          </div>
        </div>

        <!-- Comparison Table -->
        <div class="comparison-grid">
          <div class="grid-header">Requirement</div>
          <div class="grid-header">Expected</div>
          <div class="grid-header">Actual</div>
          <div class="grid-header">Status</div>

          <!-- Trip Type -->
          <div class="row-label">Trip Type</div>
          <div class="cell">{{ formatTripType(activity.required_trip_type) }}</div>
          <div class="cell">{{ formatTripType(booking.trip_type) }}</div>
          <div class="status-cell">
            <span v-if="matches.trip_type" class="check">✓</span>
            <span v-else class="cross">✕</span>
          </div>

          <!-- Origin -->
          <div class="row-label">Origin</div>
          <div class="cell">{{ activity.required_origin }}</div>
          <div class="cell">{{ actualOrigin }}</div>
          <div class="status-cell">
            <span v-if="matches.origin" class="check">✓</span>
            <span v-else class="cross">✕</span>
          </div>

          <!-- Destination -->
          <div class="row-label">Destination</div>
          <div class="cell">{{ activity.required_destination }}</div>
          <div class="cell">{{ actualDestination }}</div>
          <div class="status-cell">
            <span v-if="matches.destination" class="check">✓</span>
            <span v-else class="cross">✕</span>
          </div>

          <!-- Travel Class -->
          <div class="row-label">Travel Class</div>
          <div class="cell">{{ formatClass(activity.required_travel_class) }}</div>
          <div class="cell">{{ actualClass }}</div>
          <div class="status-cell">
            <span v-if="matches.travel_class" class="check">✓</span>
            <span v-else class="cross">✕</span>
          </div>

          <!-- Passenger Count -->
          <div class="row-label">Total Passengers</div>
          <div class="cell">{{ expectedPaxCount }}</div>
          <div class="cell">{{ booking.details?.length || 0 }}</div>
          <div class="status-cell">
            <span v-if="matches.pax_count" class="check">✓</span>
            <span v-else class="cross">✕</span>
          </div>
        </div>

        <!-- Detailed Passenger Work -->
        <div class="passenger-details mt-8">
          <h3 class="text-lg font-bold mb-4">Passenger Details in Booking</h3>
          <div v-for="(detail, index) in booking.details" :key="index" class="p-4 border rounded-lg mb-3 bg-gray-50">
            <div class="flex justify-between items-center mb-2">
              <span class="font-bold">Passenger {{ index + 1 }}</span>
              <span class="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800 uppercase">{{ detail.passenger_type }}</span>
            </div>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div><span class="text-gray-500">Name:</span> {{ detail.passenger?.first_name }} {{ detail.passenger?.last_name }}</div>
              <div><span class="text-gray-500">Seat:</span> {{ detail.seat?.seat_number }} ({{ detail.seat_class_name }})</div>
              <div><span class="text-gray-500">Flight:</span> {{ detail.schedule?.flight_number }}</div>
              <div><span class="text-gray-500">Price:</span> ₱{{ formatAmount(detail.price) }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn-primary" @click="closeModal">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  isOpen: Boolean,
  isLoading: Boolean,
  errorMessage: String,
  activity: Object,
  booking: Object,
  grade: {
    type: [Number, String],
    default: null
  }
});

const emit = defineEmits(['close']);

const closeModal = () => emit('close');

// Formatting Helpers
const formatTripType = (type) => {
  const map = {
    'one_way': 'One Way',
    'round_trip': 'Round Trip',
    'multi_city': 'Multi City'
  };
  return map[type] || type || 'N/A';
};

const formatClass = (cls) => {
  const map = {
    'economy': 'Economy',
    'premium_economy': 'Premium Economy',
    'business': 'Business',
    'first': 'First Class'
  };
  return map[cls?.toLowerCase()] || cls || 'N/A';
};

const formatAmount = (amt) => {
  return parseFloat(amt).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

// Comparison Logic
const actualOrigin = computed(() => {
  return props.booking?.details?.[0]?.schedule?.origin || 'N/A';
});

const actualDestination = computed(() => {
  return props.booking?.details?.[0]?.schedule?.destination || 'N/A';
});

const actualClass = computed(() => {
  return props.booking?.details?.[0]?.seat_class_name || 'N/A';
});

const expectedPaxCount = computed(() => {
  if (!props.activity) return 0;
  return (props.activity.required_passengers || 0) + 
         (props.activity.required_children || 0) + 
         (props.activity.required_infants || 0);
});

const matches = computed(() => {
  if (!props.activity || !props.booking) return {};
  
  return {
    trip_type: props.activity.required_trip_type === props.booking.trip_type,
    origin: props.activity.required_origin === actualOrigin.value,
    destination: props.activity.required_destination === actualDestination.value,
    travel_class: props.activity.required_travel_class?.toLowerCase() === actualClass.value?.toLowerCase(),
    pax_count: expectedPaxCount.value === (props.booking.details?.length || 0)
  };
});

const allCorrect = computed(() => {
  return Object.values(matches.value).every(v => v === true);
});

const getGradeClass = (g) => {
  const num = parseFloat(g);
  const total = parseFloat(props.activity?.total_points || 100);
  const percentage = (num / total) * 100;
  
  if (percentage >= 90) return 'bg-green-100 text-green-800';
  if (percentage >= 75) return 'bg-blue-100 text-blue-800';
  if (percentage >= 50) return 'bg-yellow-100 text-yellow-800';
  return 'bg-red-100 text-red-800';
};
</script>

<style scoped>
.comparison-modal {
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
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
}

.modal-content {
  position: relative;
  background: #ffffff;
  border-radius: 20px;
  max-width: 800px;
  width: 95%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.modal-header {
  padding: 24px 32px;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
}

.header-info h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.subtitle {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 4px 0 0 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.grade-badge {
  padding: 6px 12px;
  border-radius: 99px;
  font-size: 0.875rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  line-height: 1;
  color: #9ca3af;
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #111827;
}

.modal-body {
  padding: 32px;
  overflow-y: auto;
  flex: 1;
}

.status-summary {
  display: flex;
  gap: 16px;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 24px;
}

.status-summary .icon {
  font-size: 24px;
}

.status-summary h4 {
  font-weight: 700;
  margin: 0 0 4px 0;
}

.status-summary p {
  margin: 0;
  font-size: 0.875rem;
}

.comparison-grid {
  display: grid;
  grid-template-columns: 2fr 2fr 2fr 1fr;
  gap: 1px;
  background: #e5e7eb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.grid-header {
  background: #f9fafb;
  padding: 12px 16px;
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #6b7280;
  letter-spacing: 0.05em;
}

.row-label {
  background: #ffffff;
  padding: 16px;
  font-weight: 600;
  color: #374151;
}

.cell {
  background: #ffffff;
  padding: 16px;
  color: #111827;
}

.status-cell {
  background: #ffffff;
  padding: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.check {
  color: #10b981;
  font-weight: bold;
  font-size: 1.25rem;
}

.cross {
  color: #ef4444;
  font-weight: bold;
  font-size: 1.25rem;
}

.modal-footer {
  padding: 20px 32px;
  border-top: 1px solid #f3f4f6;
  background: #f9fafb;
  display: flex;
  justify-content: flex-end;
}

.btn-primary {
  background: #2563eb;
  color: white;
  padding: 10px 24px;
  border-radius: 10px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  padding: 10px 24px;
  border-radius: 10px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

@media (max-width: 640px) {
  .comparison-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .grid-header:nth-child(3),
  .grid-header:nth-child(4),
  .status-cell,
  .cell:nth-child(4n) {
     /* Hide status and headers in mobile or adapt */
  }
}
</style>
