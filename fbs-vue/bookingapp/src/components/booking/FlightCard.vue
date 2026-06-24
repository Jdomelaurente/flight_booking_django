<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 hover:border-pink-300 hover:shadow-md transition-all duration-200">
    <div class="px-3 sm:px-6 py-4">
      <!-- Flight Header -->
      <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-5 pb-5 border-b border-slate-100">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center shrink-0">
             <!-- Placeholder for Airline Logo -->
             <span class="text-[10px] font-black text-slate-400">LOGO</span>
          </div>
          <div class="min-w-0">
            <h4 class="font-black text-slate-800 text-sm sm:text-base leading-tight truncate">{{ flight.airline_name }}</h4>
            <div class="flex items-center gap-2 mt-1">
              <span class="text-[10px] font-bold text-pink-500 uppercase tracking-wider">{{ flight.flight_number }}</span>
              <span v-if="flight.aircraft_name" class="text-[10px] text-slate-400 font-medium px-2 border-l border-slate-200 truncate max-w-[120px] sm:max-w-none">
                {{ flight.aircraft_name }}
              </span>
            </div>
          </div>
        </div>
        
        <div class="flex items-end sm:items-center justify-between sm:justify-end gap-6 sm:gap-8">
          <div class="hidden md:block text-center px-4 border-r border-slate-100">
            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">{{ formatDay(flight.departure_time) }}</div>
            <div class="text-xs font-black text-slate-700 whitespace-nowrap">{{ formatDate(flight.departure_time) }}</div>
          </div>
          
          <div class="text-right">
            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-0.5">Starting from</div>
            <div class="text-xl sm:text-2xl font-black text-pink-500 leading-none">
              ₱{{ Number(flight.price).toLocaleString() }}
            </div>
            <button 
              v-if="flight.ml_predicted" 
              @click="$emit('view-pricing', flight)"
              class="text-[9px] text-pink-400 hover:text-pink-600 font-black flex items-center gap-1 mt-1.5 uppercase tracking-widest transition-colors ml-auto"
            >
              Insights
              <svg class="w-3 h-3" :class="{'rotate-180': showPricingDetails && selectedPriceId === flight.price_id}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Price Insights Breakdown Overlay (Always remains responsive) -->
      <div v-if="showPricingDetails && selectedPriceId === flight.price_id" 
           class="mb-5 p-4 bg-pink-50/50 rounded-lg border border-pink-100/50 animate-in fade-in slide-in-from-top-2 duration-300">
        <div class="flex justify-between items-center mb-3">
          <h4 class="text-[10px] font-black text-pink-600 uppercase tracking-widest">Pricing Analysis</h4>
          <span class="text-[9px] font-bold text-slate-400 uppercase">ML-Engine: {{ flight.price_id.slice(0, 8) }}</span>
        </div>
        
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="space-y-1">
            <div class="text-[9px] font-bold text-slate-500 uppercase tracking-tighter">Market Base</div>
            <div class="text-sm font-black text-slate-800">₱{{ Number(flight.ml_base_price).toLocaleString() }}</div>
          </div>
          
          <div v-for="(factor, key) in flight.ml_factors" :key="key" class="space-y-1">
            <div class="text-[9px] font-bold text-slate-500 uppercase tracking-tighter">{{ getFactorLabel(key) }}</div>
            <div class="text-sm font-black flex items-baseline gap-1" :class="factor > 1 ? 'text-orange-500' : (factor < 1 ? 'text-green-600' : 'text-slate-600')">
              {{ factor > 1 ? '↑' : (factor < 1 ? '↓' : '') }} {{ Math.abs(((factor - 1) * 100)).toFixed(0) }}%
              <span class="text-[9px] font-bold opacity-40 ml-0.5 whitespace-nowrap">(x{{ factor.toFixed(2) }})</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Schedule Info - REFINED TIMELINE -->
      <div class="flex items-center justify-between gap-3 sm:gap-6 mb-6 px-1">
        <!-- Departure -->
        <div class="text-left sm:text-right w-16 sm:w-24 shrink-0">
          <div class="text-xl sm:text-2xl font-black text-slate-900 leading-none">{{ formatTime(flight.departure_time) }}</div>
          <div class="text-xs sm:text-sm font-black text-slate-500 mt-1.5 uppercase tracking-tighter">{{ flight.origin_airport_code }}</div>
        </div>
        
        <!-- Refined Visual Timeline (Kept horizontal but cleaner) -->
        <div class="flex-1 flex flex-col items-center justify-center relative min-w-0">
          <div class="text-[9px] font-black text-slate-400 mb-2.5 uppercase tracking-[0.2em] whitespace-nowrap">
            {{ flight.flight_duration || formatDuration(flight.duration_minutes) }}
          </div>
          
          <div class="w-full relative flex items-center h-4">
            <div class="absolute left-0 right-0 h-[3px] bg-slate-100 rounded-full"></div>
            
            <div class="absolute left-0 w-2.5 h-2.5 rounded-full border-[3px] border-pink-500 bg-white z-10"></div>
            
            <!-- Layover indicator labels -->
            <div v-if="(flight.total_stops || 0) > 0" class="flex justify-around absolute left-0 right-0 px-4">
              <div v-for="n in (flight.total_stops || 0)" :key="n" 
                class="w-2 h-2 rounded-full bg-orange-400 ring-4 ring-orange-50 z-10 transition-all hover:ring-orange-200">
              </div>
            </div>
            
            <div class="absolute right-0 w-2.5 h-2.5 rounded-full border-[3px] border-pink-500 bg-pink-500 z-10 shadow-[0_0_8px_rgba(236,72,153,0.3)]"></div>
          </div>
          
          <div class="mt-2.5 text-[9px] font-black uppercase tracking-widest" :class="flight.total_stops > 0 ? 'text-orange-500' : 'text-green-600'">
             {{ flight.total_stops === 0 ? 'Non-stop' : `${flight.total_stops} Stop${flight.total_stops > 1 ? 's' : ''}` }}
          </div>
        </div>
        
        <!-- Arrival -->
        <div class="text-right w-16 sm:w-24 shrink-0">
          <div class="text-xl sm:text-2xl font-black text-slate-900 leading-none">{{ formatTime(flight.arrival_time) }}</div>
          <div class="text-xs sm:text-sm font-black text-slate-500 mt-1.5 uppercase tracking-tighter">{{ flight.destination_airport_code }}</div>
        </div>
      </div>
      
      <!-- Footer: Amenities & Actions -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-5 pt-5 border-t border-slate-100 bg-slate-50/50 -mx-6 px-6 -mb-4 pb-4">
        
        <!-- Amenity Icons Preview (Compact and Scaled) -->
        <div class="flex items-center flex-wrap gap-4 text-slate-400">
          <div class="flex items-center gap-1.5" title="Personal Item Included">
             <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
             <span class="text-[9px] font-black uppercase tracking-tighter hidden xs:inline">Small Bag</span>
          </div>
          <div class="flex items-center gap-1.5" title="USB Power">
             <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
             <span class="text-[9px] font-black uppercase tracking-tighter hidden xs:inline">Power</span>
          </div>
          
          <div class="flex items-center gap-2 sm:ml-2">
             <div class="w-2 h-2 rounded-full" :class="(flight.available_seats || 0) < 10 ? 'bg-orange-500 animate-pulse' : 'bg-slate-300'"></div>
             <span :class="['text-[9px] font-black uppercase tracking-[0.1em]', (flight.available_seats || 0) < 10 ? 'text-orange-500' : 'text-slate-500']">
                {{ flight.available_seats ?? 0 }} Seats Left
             </span>
          </div>
        </div>
        
        <div class="flex items-center justify-end gap-3">
          <div v-if="isSelected" class="text-[10px] text-pink-600 font-black uppercase tracking-[0.2em] animate-in slide-in-from-right-1">
            {{ selectedClassName }}
          </div>
          
          <div class="flex gap-2">
            <template v-if="isSelected">
              <button @click="$emit('select-flight', flight)" 
                class="px-4 py-2 border-2 border-slate-200 text-slate-600 rounded-md hover:bg-slate-100 transition-colors font-black text-[10px] uppercase tracking-widest active:scale-95">
                {{ isExpanded ? 'Close' : 'Modify' }}
              </button>
            </template>
            <template v-else>
              <button @click="$emit('select-flight', flight)" 
                class="px-6 py-2.5 bg-pink-500 cursor-pointer text-white text-xs sm:text-sm rounded-md shadow-lg shadow-pink-100 hover:bg-pink-600 active:scale-[0.98] transition-all font-black uppercase tracking-widest whitespace-nowrap flex items-center gap-2">
                {{ isExpanded ? 'Close' : 'Select Flight' }}
                <svg class="w-4 h-4 transition-transform duration-300" :class="isExpanded ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"></path></svg>
              </button>
            </template>
          </div>
        </div>
      </div>
      
      <!-- INLINE EXPANDED FARE FAMILIES -->
      <div v-show="isExpanded" class="mt-4 pt-4 border-t border-gray-100 animate-in slide-in-from-top-4 fade-in duration-300">
        
        <!-- Tabbed Headers -->
        <div class="flex flex-row overflow-x-auto mb-6 bg-gray-50/50 -mx-6 px-6" v-if="availableTravelClasses.length > 0">
          <button 
            v-for="tClass in availableTravelClasses" 
            :key="tClass"
            @click="selectedTravelClass = tClass"
            class="flex-1 py-3 px-4 text-left border-t-4 transition-colors min-w-[140px] border-r border-r-white"
            :class="[
              selectedTravelClass === tClass 
                ? (getTabColor(tClass) === 'blue' ? 'border-blue-500 bg-blue-100/50' : 
                   getTabColor(tClass) === 'rose' ? 'border-pink-400 bg-pink-100/50' : 
                   'border-yellow-500 bg-yellow-100/50')
                : (getTabColor(tClass) === 'blue' ? 'border-blue-200 bg-blue-50/40 text-gray-500 hover:bg-blue-100/40' : 
                   getTabColor(tClass) === 'rose' ? 'border-pink-200 bg-pink-50/40 text-gray-500 hover:bg-pink-100/40' : 
                   'border-yellow-200 bg-yellow-50/40 text-gray-500 hover:bg-yellow-100/40')
            ]"
          >
            <div class="flex justify-between items-end">
              <div>
                <div class="font-medium" :class="selectedTravelClass === tClass ? 'text-blue-900 text-sm' : 'text-gray-600 text-sm'">{{ tClass }}</div>
                <div class="text-xs mt-1" :class="selectedTravelClass === tClass ? 'text-blue-800' : 'text-gray-500'">From PHP</div>
                <div class="font-black mt-0.5" :class="selectedTravelClass === tClass ? 'text-blue-900 text-base' : 'text-gray-700 text-base'">
                  {{ Number(getLowestPrice(tClass)).toLocaleString() }}
                </div>
              </div>
              <svg class="w-4 h-4 mb-1" :class="selectedTravelClass === tClass ? 'text-blue-900' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </button>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 px-2">
          <!-- Render Seat Classes passed from parent -->
          <div v-for="seatClass in groupedClasses[selectedTravelClass]" :key="seatClass.name" 
               class="border-2 rounded-lg p-5 flex flex-col transition-all cursor-pointer relative overflow-hidden"
               :class="[
                 seatClass.fare_family === 'flex' ? 'border-yellow-500 hover:border-yellow-400 hover:-translate-y-1 shadow-sm' : 
                   (hoveredClass === seatClass.name ? 'border-pink-500 shadow-md transform -translate-y-1' : 'border-gray-200 hover:border-pink-300')
               ]"
               @mouseenter="hoveredClass = seatClass.name"
               @mouseleave="hoveredClass = null"
               @click="$emit('select-seat-class', { flight, seatClass })">
               
            <!-- Recommended Banner for Flex -->
            <div v-if="seatClass.fare_family === 'flex'" class="absolute -top-1 -right-1 bg-yellow-500 text-white text-[10px] font-bold px-3 py-1 rounded-bl-lg">
              RECOMMENDED
            </div>
            <!-- Decorative Banner for Premium (Fallback) -->
            <div v-else-if="seatClass.fare_family === 'premium'" class="absolute -top-1 -right-1 bg-pink-500 text-white text-[10px] font-bold px-3 py-1 rounded-bl-lg">
              BEST VALUE
            </div>
               
            <div class="flex justify-between items-start mb-2">
              <div>
                <h3 class="font-black text-gray-900 text-lg">{{ seatClass.name }}</h3>
                <p class="text-xs text-gray-500 mt-1 line-clamp-2 h-8">{{ seatClass.description }}</p>
              </div>
              <div class="w-10 h-10 rounded-full bg-pink-50 flex items-center justify-center shrink-0 text-pink-500">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="seatClass.icon"></path>
                </svg>
              </div>
            </div>
            
            <div class="text-2xl font-black text-pink-600 my-4">
              ₱{{ Number(seatClass.price).toLocaleString() }}
            </div>
            
            <ul class="space-y-3 mb-6 flex-1">
              <li v-for="(feature, idx) in seatClass.features" :key="idx" class="flex items-start text-sm text-gray-700">
                <svg class="w-4 h-4 text-green-500 mr-2 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <span class="leading-tight">{{ typeof feature === 'object' && feature !== null ? (feature.feature_text || feature.text || JSON.stringify(feature)) : feature }}</span>
              </li>
            </ul>
            
            <button class="w-full py-3 rounded-md font-bold text-sm transition-colors"
                    :class="hoveredClass === seatClass.name ? 'bg-pink-500 text-white shadow-md shadow-pink-200' : 'bg-pink-50 text-pink-600'">
              Select {{ seatClass.name }}
            </button>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { format } from 'date-fns';

const props = defineProps({
  flight: Object,
  isRoundTrip: Boolean,
  isMultiCity: Boolean,
  selectionPhase: String,
  selectedOutbound: Object,
  selectedReturn: Object,
  selectedSegmentFlight: Object,
  selectButtonText: String,
  mlPricingEnabled: Boolean,
  showPricingDetails: Boolean,
  selectedPriceId: String,
  parsedSeatClasses: Array // New Array passed down from parent view
});

const emit = defineEmits(['select-flight', 'view-pricing', 'select-seat-class', 'expand']);

const isExpanded = computed(() => {
  return props.parsedSeatClasses && props.parsedSeatClasses.length > 0;
});
const hoveredClass = ref(null);

// NEW: Group seat classes by travel class and logic for tabs
const groupedClasses = computed(() => {
  if (!props.parsedSeatClasses) return {};
  return props.parsedSeatClasses.reduce((acc, sc) => {
    let tClass = sc.travel_class;
    // Fallback if travel_class is missing, parse from name
    if (!tClass) {
      if (sc.name.toLowerCase().includes('economy')) tClass = 'Economy';
      else if (sc.name.toLowerCase().includes('business')) tClass = 'Business';
      else if (sc.name.toLowerCase().includes('first')) tClass = 'First Class';
      else tClass = 'Economy';
    }
    
    // Capitalize properly
    // Ensure Title Case (e.g., "Comfort Class" or "Premium Economy")
    tClass = tClass.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');
    
    if (!acc[tClass]) acc[tClass] = [];
    acc[tClass].push(sc);
    return acc;
  }, {});
});

const availableTravelClasses = computed(() => Object.keys(groupedClasses.value));
const selectedTravelClass = ref('');

// Switch to first tab safely
watch(() => isExpanded.value, (newVal) => {
  if (newVal && availableTravelClasses.value.length > 0 && !selectedTravelClass.value) {
    selectedTravelClass.value = availableTravelClasses.value[0];
  }
});

const getTabColor = (tClass) => {
  const c = tClass.toLowerCase();
  if (c.includes('premium')) return 'rose';
  if (c.includes('business') || c.includes('first')) return 'yellow';
  return 'blue';
};

const getLowestPrice = (tClass) => {
  const classes = groupedClasses.value[tClass] || [];
  if (classes.length === 0) return 0;
  return Math.min(...classes.map(c => Number(c.price)));
};

const isFlightMatch = (flightA, flightB) => {
  if (!flightA || !flightB) return false;
  // Use ID if available, otherwise fallback to flight_number + departure_time combination
  if (flightA.id && flightB.id) {
    return flightA.id === flightB.id;
  }
  return flightA.flight_number === flightB.flight_number && 
         flightA.departure_time === flightB.departure_time;
};

const isSelected = computed(() => {
  if (props.isMultiCity) {
    return isFlightMatch(props.selectedSegmentFlight, props.flight);
  }
  if (props.isRoundTrip) {
    if (props.selectionPhase === 'outbound') {
      return isFlightMatch(props.selectedOutbound, props.flight);
    } else {
      return isFlightMatch(props.selectedReturn, props.flight);
    }
  }
  return isFlightMatch(props.selectedOutbound, props.flight);
});

const selectedClassName = computed(() => {
  let selected = props.selectedOutbound;
  if (props.isMultiCity) selected = props.selectedSegmentFlight;
  else if (props.isRoundTrip && props.selectionPhase === 'return') selected = props.selectedReturn;
  
  return selected?.selected_seat_class || selected?.seat_class || 'Not selected';
});

const selectionLabel = computed(() => {
  if (props.isMultiCity) return 'Flight Selected';
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
const getFactorLabel = (key) => {
  const labels = {
    'user_factor': 'Loyalty',
    'session_factor': 'Session',
    'demand_factor': 'Urgency',
    'time_factor': 'Peak Time',
    'inventory_factor': 'Occupancy',
    'randomization': 'Disturbance',
    'festival_factor': 'Fiesta'
  };
  return labels[key] || key.replace('_', ' ');
};
</script>
