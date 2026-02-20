<template>
  <div class="bg-white rounded-[5px] shadow-sm border border-gray-200 hover:border-pink-300 hover:shadow-md transition-all duration-200">
    <div class="px-6 py-3">
      <!-- Flight Header -->
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6 pb-6 border-b border-gray-100">
        <div class="flex items-center space-x-4">
          <div>
            <div class="font-bold text-pink-500">{{ flight.airline_name }}</div>
            <div class="text-sm text-green-500">{{ flight.flight_number }}</div>
          </div>
          <div v-if="flight.is_domestic !== undefined" 
            :class="['px-3 py-1 rounded-full text-xs font-medium',
                     flight.is_domestic ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700']">
            {{ flight.is_domestic ? 'Domestic' : 'International' }}
          </div>
        </div>
        
        <div class="text-center">
          <div class="text-sm text-gray-700">{{ formatDate(flight.departure_time) }}</div>
          <div class="text-bold font-bold text-gray-500">{{ formatDay(flight.departure_time) }}</div>
        </div>
        
        <div class="text-right">
          <div class="text-2xl font-bold" :class="flight.ml_predicted ? 'text-pink-600' : 'text-pink-500'">
            ₱{{ Number(flight.price).toLocaleString() }}
          </div>
        </div>
      </div>
      
      <!-- Schedule Info -->
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-8 mb-6">
        <!-- Departure -->
        <div class="flex-1">
          <div class="text-3xl font-bold text-gray-900 mb-1">{{ formatTime(flight.departure_time) }}</div>
          <div class="text-gray-700">{{ flight.origin }}</div>
          <div class="text-sm text-green-500">{{ flight.origin_airport_code }}</div>
        </div>
        
        <!-- Duration -->
        <div class="flex flex-col items-center">
          <div class="w-full h-px bg-gray-300 mb-2"></div>
          <div class="text-sm text-gray-600">{{ flight.flight_duration || formatDuration(flight.duration_minutes) }}</div>
          <div class="w-full h-px bg-gray-300 mt-2"></div>
        </div>
        
        <!-- Arrival -->
        <div class="flex-1 text-right">
          <div class="text-3xl font-bold text-gray-900 mb-1">{{ formatTime(flight.arrival_time) }}</div>
          <div class="text-gray-700">{{ flight.destination }}</div>
          <div class="text-sm text-green-500">{{ flight.destination_airport_code }}</div>
        </div>
      </div>
      
      <!-- Flight Details -->
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-2">
        <div class="space-y-2">
          <div v-if="flight.available_seats !== undefined" class="flex items-center text-sm">
            <svg class="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span class="text-gray-700" :class="{ 'text-orange-500 font-semibold': flight.available_seats < 10 }">
              {{ flight.available_seats }} seats available
            </span>
          </div>
          
          <!-- Display seat classes -->
          <div v-if="flight.seat_classes && flight.seat_classes.length" class="text-sm text-gray-600">
            Classes: {{ formatSeatClasses(flight.seat_classes) }}
          </div>
          
          <!-- Selected Indicator -->
          <div v-if="isSelected" class="text-sm text-pink-600 font-medium mt-1 animate-pulse">
            ✓ Selected: {{ selectedClassName }}
          </div>
        </div>
        
        <div class="flex space-x-2">
          <template v-if="isSelected">
            <button class="px-6 py-3 bg-green-500 text-white rounded-sm font-medium whitespace-nowrap">
              ✓ {{ selectionLabel }}
            </button>
            <button @click="$emit('select-flight', flight)" 
              class="px-6 py-3 border border-gray-300 text-gray-700 rounded-sm hover:bg-gray-50 transition-colors font-medium whitespace-nowrap">
              Change Selection
            </button>
          </template>
          <template v-else>
            <button @click="$emit('select-flight', flight)" 
              class="px-6 py-3 bg-pink-500 text-white rounded-[2px] hover:bg-pink-600 transition-colors font-medium whitespace-nowrap">
              {{ selectButtonText }}
            </button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { format } from 'date-fns';

const props = defineProps({
  flight: Object,
  isRoundTrip: Boolean,
  selectionPhase: String,
  selectedOutbound: Object,
  selectedReturn: Object,
  selectButtonText: String
});

defineEmits(['select-flight']);

const isSelected = computed(() => {
  if (props.isRoundTrip) {
    if (props.selectionPhase === 'outbound') {
      return props.selectedOutbound?.flight_number === props.flight.flight_number;
    } else {
      return props.selectedReturn?.flight_number === props.flight.flight_number;
    }
  }
  return props.selectedOutbound?.flight_number === props.flight.flight_number;
});

const selectedClassName = computed(() => {
  const selected = props.selectionPhase === 'return' ? props.selectedReturn : props.selectedOutbound;
  return selected?.selected_seat_class || selected?.seat_class || 'Not selected';
});

const selectionLabel = computed(() => {
  if (!props.isRoundTrip) return 'Flight Selected';
  return props.selectionPhase === 'outbound' ? 'Outbound Selected' : 'Return Selected';
});

// Helpers
const formatTime = (dateTimeString) => {
  if (!dateTimeString) return '';
  const date = new Date(dateTimeString);
  return date.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit', hour12: true });
};

const formatDate = (dateTimeString) => {
  if (!dateTimeString) return '';
  const date = new Date(dateTimeString);
  return date.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' });
};

const formatDay = (dateTimeString) => {
  if (!dateTimeString) return '';
  return format(new Date(dateTimeString), 'EEEE');
};

const formatDuration = (minutes) => {
  if (!minutes) return '';
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};

const formatSeatClasses = (seatClasses) => {
  if (!seatClasses || !Array.isArray(seatClasses)) return '';
  return seatClasses.map(sc => {
    if (typeof sc === 'string') return sc;
    if (sc && typeof sc === 'object') return sc.name || sc.class_name || sc.value || 'Unknown';
    return 'Unknown';
  }).join(', ');
};
</script>
