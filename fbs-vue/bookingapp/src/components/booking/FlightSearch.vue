<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { VueDatePicker } from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import airportService from '@/services/booking/airportService';
import { useBookingStore } from '@/stores/booking';
import { useRouter } from 'vue-router';
import { useNotificationStore } from '@/stores/notification';
import ActivityCodeEntry from '@/components/booking/ActivityCodeEntry.vue';

const router = useRouter()
const bookingStore = useBookingStore();
const notificationStore = useNotificationStore();

// Activity Code Modal State
const showActivityCodeModal = ref(false);

// --- 1. TRIP TYPE STATE ---
const tripType = ref('round-trip');
const stopPreference = ref('all'); // 'all', 'nonstop', 'direct', 'connecting'

// Watch for trip type changes to clear return date when switching to one-way
watch(tripType, (newType) => {
  if (newType === 'one-way') {
    returnDate.value = null;
  }
});

// --- 2. AIRPORT SEARCH STATE ---
const fromSearch = ref('');
const toSearch = ref('');
const fromResults = ref([]);
const toResults = ref([]);
const selectedFrom = ref(null);
const selectedTo = ref(null);

// --- 2.1 MULTI-CITY STATE ---
const multiSegments = ref([
  { fromSearch: '', toSearch: '', selectedFrom: null, selectedTo: null, date: new Date().toISOString().split('T')[0], fromResults: [], toResults: [] },
  { fromSearch: '', toSearch: '', selectedFrom: null, selectedTo: null, date: new Date().toISOString().split('T')[0], fromResults: [], toResults: [] }
]);

const addSegment = () => {
  if (multiSegments.value.length < 6) {
    const lastSeg = multiSegments.value[multiSegments.value.length - 1];
    multiSegments.value.push({
      fromSearch: lastSeg.selectedTo ? `${lastSeg.selectedTo.code} - ${lastSeg.selectedTo.city}` : '',
      toSearch: '',
      selectedFrom: lastSeg.selectedTo || null,
      selectedTo: null,
      date: lastSeg.date,
      fromResults: [],
      toResults: []
    });
  } else {
    notificationStore.warn("Maximum 6 segments allowed.");
  }
};

const removeSegment = (index) => {
  if (multiSegments.value.length > 2) {
    multiSegments.value.splice(index, 1);
  }
};

const searchAirports = async (query, target, segmentIndex = null) => {
  if (query.includes(' - ')) return;

  const searchQuery = query.toUpperCase().trim();
  
  // Update UI state immediately if not enough chars
  if (searchQuery.length < 3) {
    if (segmentIndex !== null) {
      multiSegments.value[segmentIndex][target === 'from' ? 'fromResults' : 'toResults'] = [];
    } else {
      target === 'from' ? fromResults.value = [] : toResults.value = [];
    }
    return;
  }

  try {
    const response = await airportService.searchAirports(searchQuery);
    const airports = response.data.results || response.data;
    
    let excludedCode = null;
    if (segmentIndex !== null) {
      const seg = multiSegments.value[segmentIndex];
      excludedCode = target === 'from' ? seg.selectedTo?.code : seg.selectedFrom?.code;
    } else {
      excludedCode = target === 'from' ? selectedTo.value?.code : selectedFrom.value?.code;
    }

    const filteredResults = airports
      .filter(airport => airport.code !== excludedCode)
      .sort((a, b) => {
        if (a.code === searchQuery) return -1;
        if (b.code === searchQuery) return 1;
        return 0;
      });

    if (segmentIndex !== null) {
      multiSegments.value[segmentIndex][target === 'from' ? 'fromResults' : 'toResults'] = filteredResults;
    } else {
      if (target === 'from') fromResults.value = filteredResults;
      else toResults.value = filteredResults;
    }
  } catch (error) {
    console.error("Search error:", error);
  }
};

const selectAirport = (airport, target, segmentIndex = null) => {
  const displayString = `${airport.code} - ${airport.city}`;

  if (segmentIndex !== null) {
    const seg = multiSegments.value[segmentIndex];
    if (target === 'from') {
      seg.selectedFrom = airport;
      seg.fromSearch = displayString;
      seg.fromResults = [];
    } else {
      seg.selectedTo = airport;
      seg.toSearch = displayString;
      seg.toResults = [];
      
      // Auto-fill next segment's 'from' if it exists
      if (segmentIndex < multiSegments.value.length - 1) {
        const nextSeg = multiSegments.value[segmentIndex + 1];
        if (!nextSeg.selectedFrom) {
          nextSeg.selectedFrom = airport;
          nextSeg.fromSearch = displayString;
        }
      }
    }
  } else {
    if (target === 'from') {
      selectedFrom.value = airport;
      fromSearch.value = displayString; 
      fromResults.value = []; 
    } else {
      selectedTo.value = airport;
      toSearch.value = displayString;
      toResults.value = [];
    }
  }
};

const clearAirport = (target, segmentIndex = null) => {
  if (segmentIndex !== null) {
    const seg = multiSegments.value[segmentIndex];
    if (target === 'from') {
      seg.selectedFrom = null;
      seg.fromSearch = '';
      seg.fromResults = [];
    } else {
      seg.selectedTo = null;
      seg.toSearch = '';
      seg.toResults = [];
    }
  } else {
    if (target === 'from') {
      selectedFrom.value = null;
      fromSearch.value = '';
      fromResults.value = [];
    } else {
      selectedTo.value = null;
      toSearch.value = '';
      toResults.value = [];
    }
  }
};

const handleEnterKey = (query, target, segmentIndex = null) => {
  if (!query || query.includes(' - ')) return;
  
  const results = segmentIndex !== null 
    ? multiSegments.value[segmentIndex][target === 'from' ? 'fromResults' : 'toResults']
    : (target === 'from' ? fromResults.value : toResults.value);

  if (results.length > 0) {
    const searchQuery = query.toUpperCase().trim();
    // Prioritize exact code match, then exact city match, then first result
    const match = results.find(a => a.code === searchQuery) || 
                  results.find(a => a.city.toUpperCase() === searchQuery) || 
                  results[0];
    if (match) {
      selectAirport(match, target, segmentIndex);
    }
  }
};

const handleClickOutside = (e) => {
  if (!e.target.closest('.field-container') && !e.target.closest('.airport-input-container')) {
    fromResults.value = [];
    toResults.value = [];
    multiSegments.value.forEach(s => {
      s.fromResults = [];
      s.toResults = [];
    });
    showPassengerDropdown.value = false;
  }
};

onMounted(() => window.addEventListener('click', handleClickOutside));
onUnmounted(() => window.removeEventListener('click', handleClickOutside));

// --- 3. DATE STATE ---
const today = new Date().toISOString().split('T')[0];
const departureDate = ref(today); 
const returnDate = ref(null);
const minDate = new Date(); 

// NEW FORMAT: "9 Wed January"
const dateFormat = (date) => {
  if (!date) return '';
  const d = new Date(date);
  const dayNum = d.getDate();
  const weekDay = d.toLocaleString('default', { weekday: 'short' });
  const month = d.toLocaleString('default', { month: 'long' });
  return `${dayNum} ${weekDay} ${month}`;
};

const minReturnDate = computed(() => {
  return departureDate.value ? new Date(departureDate.value) : new Date();
});

const getMinDateForSegment = (index) => {
  if (index === 0) return minDate;
  const prevDate = multiSegments.value[index-1].date;
  return prevDate ? new Date(prevDate) : minDate;
};

// --- 4. PASSENGER STATE ---
const showPassengerDropdown = ref(false);
const passengers = ref({ adult: 1, children: 0, infant: 0 });
const totalPassengers = computed(() => passengers.value.adult + passengers.value.children + passengers.value.infant);

const updateCount = (type, delta) => {
  const current = passengers.value;
  const newVal = current[type] + delta;

  // Basic range check
  if (newVal < 0 || newVal > 9) return;

  // Adult minimum check
  if (type === 'adult' && newVal < 1) return;

  // Rule: Total (Adult + Children) usually capped at 9 in standard GDS
  if ((type === 'adult' || type === 'children')) {
    const totalBookable = (type === 'adult' ? newVal : current.adult) + (type === 'children' ? newVal : current.children);
    if (totalBookable > 9) {
      notificationStore.warn("Maximum 9 passengers (Adults + Children) allowed per booking.");
      return;
    }
  }

  // Rule: Infant count cannot exceed Adult count (1 infant per adult)
  if (type === 'infant' && newVal > current.adult) {
    notificationStore.warn("Each infant must be accompanied by an adult (1 Infant per Adult).");
    return;
  }

  // Rule: If reducing adults, ensure we don't have more infants than remaining adults
  if (type === 'adult' && delta < 0 && current.infant > newVal) {
    notificationStore.warn("Cannot reduce adults below infant count. Each infant needs an accompanying adult.");
    return;
  }

  passengers.value[type] = newVal;
};

// --- 5. SEARCH EXECUTION ---
const handleSearch = () => {
  if (!bookingStore.hasActivityCodeValidation) {
    showActivityCodeModal.value = true;
    return;
  }

  const isMulti = tripType.value === 'multi-city';

  if (isMulti) {
    // Validate multi-city segments
    for (let i = 0; i < multiSegments.value.length; i++) {
      const seg = multiSegments.value[i];
      if (!seg.selectedFrom || !seg.selectedTo) {
        notificationStore.warn(`Please select both Origin and Destination for Flight ${i + 1}.`);
        return;
      }
      if (seg.selectedFrom.code === seg.selectedTo.code) {
        notificationStore.warn(`Origin and Destination cannot be the same for Flight ${i + 1}.`);
        return;
      }
    }
  } else {
    // Validate standard fields
    if (!selectedFrom.value || !selectedTo.value) {
      notificationStore.warn("Please select both Origin and Destination.");
      return;
    }
    if (selectedFrom.value.code === selectedTo.value.code) {
      notificationStore.warn("Origin and Destination cannot be the same airport.");
      return;
    }
    if (tripType.value === 'round-trip' && !returnDate.value) {
      notificationStore.warn("Please select a return date for round-trip flights.");
      return;
    }
  }

  bookingStore.setPassengerCount(passengers.value);
  bookingStore.setTripType(tripType.value);
  bookingStore.setStopPreference(stopPreference.value);
  bookingStore.startSession();

  if (isMulti) {
    bookingStore.setMultiCitySegments(multiSegments.value.map(s => ({
      origin: s.selectedFrom,
      destination: s.selectedTo,
      date: s.date
    })));

    router.push({
      name: 'SearchResults',
      query: {
        tripType: 'multi-city',
        segments: JSON.stringify(multiSegments.value.map(s => ({
          origin: s.selectedFrom.code,
          destination: s.selectedTo.code,
          date: s.date
        }))),
        adults: passengers.value.adult,
        children: passengers.value.children,
        infants: passengers.value.infant,
        stops: stopPreference.value
      }
    });
  } else {
    router.push({
      name: 'SearchResults',
      query: {
        origin: selectedFrom.value.code,
        destination: selectedTo.value.code,
        departure: departureDate.value,
        returnDate: returnDate.value,
        tripType: tripType.value,
        adults: passengers.value.adult,
        children: passengers.value.children,
        infants: passengers.value.infant,
        stops: stopPreference.value
      }
    });
  }
};

// Handle activity code modal continue
const handleActivityCodeContinue = () => {
  handleSearch();
};
</script>

<template>
  <!-- Activity Code Entry Modal -->
  <ActivityCodeEntry 
    :isOpen="showActivityCodeModal"
    @close="showActivityCodeModal = false"
    @continue="handleActivityCodeContinue"
  />

  <div class="mx-auto my-5 rounded-[5px] bg-white p-6 text-gray-800 shadow-[0_10px_30px_rgba(0,0,0,0.15)]">

    <!-- Trip Type & Stop Preference Container -->
    <div class="mb-5 flex flex-wrap items-center justify-between gap-4 border-b border-gray-200">
      <!-- Trip Type Tabs -->
      <div class="flex gap-2">
        <button
          v-for="t in ['one-way', 'round-trip', 'multi-city']"
          :key="t"
          @click="tripType = t"
          class="group relative cursor-pointer border-b-4 px-4 py-2 text-xs font-black uppercase tracking-widest transition-all duration-300"
          :class="tripType === t
            ? 'border-pink-500 text-pink-600'
            : 'border-transparent text-gray-400 hover:text-pink-400'"
        >
          <span class="flex items-center gap-2">
            {{ t.replace('-', ' ') }}
            <!-- Multi-city Badge Indicator -->
            <span v-if="t === 'multi-city'" 
              class="flex h-2 w-2 rounded-full animate-pulse transition-colors"
              :class="tripType === 'multi-city' ? 'bg-pink-600' : 'bg-gray-300 group-hover:bg-pink-300'"></span>
          </span>
          
          <!-- Animated Underline for active state -->
          <div v-if="tripType === t" class="absolute -bottom-1 left-0 right-0 h-1 bg-gradient-to-r from-pink-500 to-orange-400 rounded-full"></div>
        </button>
      </div>

      <!-- Stop Preference Selector -->
      <div class="flex items-center gap-2 pb-2">
        <span class="text-[0.65rem] font-bold uppercase tracking-wider text-gray-400">Flight Category:</span>
        <select 
          v-model="stopPreference"
          class="cursor-pointer border-none bg-transparent py-1 text-xs font-bold text-[#FF579A] focus:ring-0"
        >
          <option value="all">Any Stops</option>
          <option value="nonstop">Non-stop</option>
          <option value="direct">Direct</option>
          <option value="connecting">Connecting</option>
        </select>
      </div>
    </div>

    <!-- Search Grid (One-Way & Round-Trip) -->
    <div v-if="tripType !== 'multi-city'" class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">

      <!-- FROM -->
      <div class="relative flex flex-col airport-input-container">
        <label class="mb-1 text-[0.7rem] font-bold tracking-wide text-[#FF579A]">
          FROM
        </label>
        <div class="field-container relative">
          <input
            v-model="fromSearch"
            @input="searchAirports(fromSearch, 'from')"
            @keydown.enter.prevent="handleEnterKey(fromSearch, 'from')"
            @focus="fromSearch = ''; fromResults = []"
            placeholder="e.g. MNL"
            class="w-full rounded-[2px] border border-gray-300 bg-white pl-2 pr-8 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#FF579A]"
          />
          <button 
            v-if="selectedFrom || fromSearch"
            @click="clearAirport('from')"
            class="absolute right-2 top-1/2 flex h-6 w-6 -translate-y-1/2 items-center justify-center rounded-full text-gray-400 hover:bg-gray-100 hover:text-red-500 transition-colors text-xl font-medium"
            type="button"
          >
            &times;
          </button>
        </div>
      </div>

      <!-- TO -->
      <div class="relative flex flex-col airport-input-container">
        <label class="mb-1 text-[0.7rem] font-bold tracking-wide text-[#FF579A]">
          TO
        </label>
        <div class="field-container relative">
          <input
            v-model="toSearch"
            @input="searchAirports(toSearch, 'to')"
            @keydown.enter.prevent="handleEnterKey(toSearch, 'to')"
            @focus="toSearch = ''; toResults = []"
            placeholder="Destination City/Code"
            class="w-full rounded-[2px] border border-gray-300 bg-white pl-2 pr-8 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#FF579A]"
          />
          <button 
            v-if="selectedTo || toSearch"
            @click="clearAirport('to')"
            class="absolute right-2 top-1/2 flex h-6 w-6 -translate-y-1/2 items-center justify-center rounded-full text-gray-400 hover:bg-gray-100 hover:text-red-500 transition-colors text-xl font-medium"
            type="button"
          >
            &times;
          </button>
        </div>
      </div>

      <!-- DEPARTURE -->
      <div class="flex flex-col">
        <label class="mb-1 text-[0.7rem] font-bold tracking-wide text-[#FF579A]">
          DEPARTURE
        </label>
        <VueDatePicker
          v-model="departureDate"
          :min-date="minDate"
          :format="dateFormat"
          model-type="yyyy-MM-dd"
          :enable-time-picker="false"
          auto-apply
        />
      </div>

      <!-- RETURN -->
      <div
        class="flex flex-col"
        :class="tripType === 'one-way' ? 'pointer-events-none opacity-40' : ''"
      >
        <label class="mb-1 text-[0.7rem] font-bold tracking-wide text-[#FF579A]">
          RETURN
        </label>
        <VueDatePicker
          v-model="returnDate"
          :min-date="minReturnDate"
          :disabled="tripType === 'one-way'"
          :format="dateFormat"
          model-type="yyyy-MM-dd"
          :enable-time-picker="false"
          auto-apply
          placeholder="Select Date"
        />
      </div>

      <!-- PASSENGERS -->
      <div class="relative flex flex-col">
        <label class="mb-1 text-[0.7rem] font-bold tracking-wide text-[#FF579A]">
          PASSENGERS
        </label>

        <div
          @click.stop="showPassengerDropdown = !showPassengerDropdown"
          class="cursor-pointer rounded-[2px] border border-gray-300 bg-white px-2 py-3 text-sm"
        >
          {{ totalPassengers }} Passenger(s)
        </div>

        <div
          v-if="showPassengerDropdown"
          @click.stop
          class="absolute right-0 top-full z-[70] w-60 border border-gray-300 bg-white p-5 shadow-xl"
        >
          <div
            v-for="(val, type) in passengers"
            :key="type"
            class="mb-4 flex items-center justify-between"
          >
            <span class="font-medium capitalize">{{ type }}</span>
            <div class="flex items-center gap-4">
              <button
                @click="updateCount(type, -1)"
                class="flex h-8 w-8 items-center justify-center rounded-full border border-[#FF579A] text-lg text-[#FF579A] hover:bg-gray-100"
              >
                −
              </button>
              <span>{{ val }}</span>
              <button
                @click="updateCount(type, 1)"
                class="flex h-8 w-8 items-center justify-center rounded-full border border-[#FF579A] text-lg text-[#FF579A] hover:bg-gray-100"
              >
                +
              </button>
            </div>
          </div>

          <button
            @click="showPassengerDropdown = false"
            class="w-full rounded-[2px] bg-[#FF579A] py-2 text-xs font-bold text-white"
          >
            DONE
          </button>
        </div>
      </div>

      <!-- SEARCH BUTTON (Standard) -->
      <div class="flex flex-col justify-end">
        <button
          @click="handleSearch"
          class="h-12 w-full rounded-[2px] bg-[#FF579A] cursor-pointer text-lg font-bold text-white transition hover:bg-[#ff7bb0] shadow-md active:scale-[0.98]"
        >
          SEARCH FLIGHTS
        </button>
      </div>

    </div>

    <!-- Multi-City Segment Repeater -->
    <div v-else class="space-y-6">
      <!-- Multi-City Mode Status Indicator -->
      <div class="mb-8 flex items-center gap-3">
        <div class="h-[1px] flex-1 bg-gradient-to-r from-transparent via-pink-100 to-pink-500"></div>
        <div class="flex items-center gap-2 px-5 py-2 bg-pink-50/50 rounded-full border border-pink-100/50 backdrop-blur-sm">
          <div class="w-2 h-2 rounded-full bg-[#FF579A] animate-pulse"></div>
          <span class="text-[10px] font-black text-[#FF579A] uppercase tracking-[0.2em] leading-none">Multi-City Planner</span>
        </div>
        <div class="h-[1px] flex-1 bg-gradient-to-l from-transparent via-pink-100 to-pink-500"></div>
      </div>
      <div 
        v-for="(segment, index) in multiSegments" 
        :key="index"
        class="relative flex flex-col gap-4 border-b border-gray-100 pb-6 last:border-0 lg:flex-row lg:items-end lg:gap-3"
      >
        <button 
          v-if="multiSegments.length > 2"
          @click="removeSegment(index)"
          class="absolute -right-1 -top-1 flex h-6 w-6 items-center justify-center rounded-full bg-gray-100 text-gray-400 hover:bg-red-50 hover:text-red-500 transition lg:static lg:h-10 lg:w-10 lg:translate-y-[-1px]"
          title="Remove flight"
        >
          &times;
        </button>

        <div class="flex-1 space-y-1 airport-input-container">
          <label class="text-[0.65rem] font-bold text-[#FF579A] uppercase">Flight {{ index + 1 }} From</label>
          <div class="field-container relative">
            <input
              v-model="segment.fromSearch"
              @input="searchAirports(segment.fromSearch, 'from', index)"
              @keydown.enter.prevent="handleEnterKey(segment.fromSearch, 'from', index)"
              @focus="segment.fromSearch = ''; segment.fromResults = []"
              placeholder="Origin"
              class="w-full rounded-[2px] border border-gray-300 bg-white pl-2 pr-8 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#FF579A]"
            />
            <button 
              v-if="segment.selectedFrom || segment.fromSearch"
              @click="clearAirport('from', index)"
              class="absolute right-2 top-1/2 flex h-6 w-6 -translate-y-1/2 items-center justify-center rounded-full text-gray-400 hover:bg-gray-100 hover:text-red-500 transition-colors text-xl font-medium"
              type="button"
            >
              &times;
            </button>
          </div>
        </div>

        <div class="flex-1 space-y-1 airport-input-container">
          <label class="text-[0.65rem] font-bold text-[#FF579A] uppercase">To</label>
          <div class="field-container relative">
            <input
              v-model="segment.toSearch"
              @input="searchAirports(segment.toSearch, 'to', index)"
              @keydown.enter.prevent="handleEnterKey(segment.toSearch, 'to', index)"
              @focus="segment.toSearch = ''; segment.toResults = []"
              placeholder="Destination"
              class="w-full rounded-[2px] border border-gray-300 bg-white pl-2 pr-8 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#FF579A]"
            />
            <button 
              v-if="segment.selectedTo || segment.toSearch"
              @click="clearAirport('to', index)"
              class="absolute right-2 top-1/2 flex h-6 w-6 -translate-y-1/2 items-center justify-center rounded-full text-gray-400 hover:bg-gray-100 hover:text-red-500 transition-colors text-xl font-medium"
              type="button"
            >
              &times;
            </button>
          </div>
        </div>

        <div class="flex-1 space-y-1">
          <label class="text-[0.65rem] font-bold text-[#FF579A] uppercase">Departure Date</label>
          <VueDatePicker
            v-model="segment.date"
            :min-date="getMinDateForSegment(index)"
            :format="dateFormat"
            model-type="yyyy-MM-dd"
            :enable-time-picker="false"
            auto-apply
            class="h-[46px]"
          />
        </div>
      </div>

      <!-- Multi-City Footer (Add Flight, Passengers, Search) -->
      <div class="flex flex-col flex-wrap items-center justify-between gap-6 border-t border-gray-100 pt-6 lg:flex-row lg:gap-4">
        <button 
          @click="addSegment"
          v-if="multiSegments.length < 6"
          class="flex items-center gap-2 rounded-full border-2 border-[#FF579A] px-6 py-2 text-sm font-bold text-[#FF579A] transition hover:bg-[#FF579A] hover:text-white"
        >
          <span>+</span> ADD FLIGHT
        </button>

        <div class="flex flex-1 flex-col items-center gap-6 lg:flex-row lg:justify-end">
          <!-- PASSENGERS (Multi-city version) -->
          <div class="relative flex flex-col min-w-[180px]">
            <label class="mb-1 text-[0.7rem] font-bold tracking-wide text-[#FF579A]">PASSENGERS</label>
            <div @click.stop="showPassengerDropdown = !showPassengerDropdown" class="cursor-pointer rounded-[2px] border border-gray-300 bg-white px-4 py-3 text-sm shadow-sm hover:border-[#FF579A]">
              {{ totalPassengers }} Passenger(s)
            </div>
            
            <div v-if="showPassengerDropdown" @click.stop class="absolute bottom-full right-0 mb-2 z-[70] w-60 border border-gray-300 bg-white p-5 shadow-2xl">
              <div v-for="(val, type) in passengers" :key="type" class="mb-4 flex items-center justify-between">
                <span class="font-medium capitalize">{{ type }}</span>
                <div class="flex items-center gap-4">
                  <button @click="updateCount(type, -1)" class="flex h-8 w-8 items-center justify-center rounded-full border border-[#FF579A] text-[#FF579A] hover:bg-gray-100">−</button>
                  <span>{{ val }}</span>
                  <button @click="updateCount(type, 1)" class="flex h-8 w-8 items-center justify-center rounded-full border border-[#FF579A] text-[#FF579A] hover:bg-gray-100">+</button>
                </div>
              </div>
              <button @click="showPassengerDropdown = false" class="w-full rounded-[2px] bg-[#FF579A] py-2 text-xs font-bold text-white">DONE</button>
            </div>
          </div>

          <button
            @click="handleSearch"
            class="h-14 min-w-[220px] rounded-[2px] bg-[#FF579A] px-10 text-lg font-bold text-white shadow-lg transition hover:bg-[#ff7bb0] active:scale-[0.98]"
          >
            SEARCH FLIGHTS
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
