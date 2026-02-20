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

const searchAirports = async (query, target) => {
  if (query.includes(' - ')) return;

  const searchQuery = query.toUpperCase().trim();
  if (searchQuery.length < 3) {
    target === 'from' ? fromResults.value = [] : toResults.value = [];
    return;
  }

  try {
    const response = await airportService.searchAirports(searchQuery);
    
    // 1. Get the opposite selected airport's code
    const excludedCode = target === 'from' 
      ? selectedTo.value?.code 
      : selectedFrom.value?.code;

    // 2. Handle paginated response (response.data.results) or flat array
    const airports = response.data.results || response.data;

    // 3. Filter and Sort
    const filteredResults = airports
      .filter(airport => airport.code !== excludedCode) // Remove duplicates
      .sort((a, b) => {
        if (a.code === searchQuery) return -1;
        if (b.code === searchQuery) return 1;
        return 0;
      });

    if (target === 'from') fromResults.value = filteredResults;
    else toResults.value = filteredResults;
  } catch (error) {
    console.error("Search error:", error);
  }
};

const selectAirport = (airport, target) => {
  // Construct the exact string: "BXU - Butuan City"
  const displayString = `${airport.code} - ${airport.city}`;

  if (target === 'from') {
    selectedFrom.value = airport;
    fromSearch.value = displayString; 
    fromResults.value = []; 
  } else {
    selectedTo.value = airport;
    toSearch.value = displayString;
    toResults.value = [];
  }
};

const handleClickOutside = (e) => {
  if (!e.target.closest('.field-container')) {
    fromResults.value = [];
    toResults.value = [];
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

// --- 4. PASSENGER STATE ---
const showPassengerDropdown = ref(false);
const passengers = ref({ adult: 1, children: 0, infant: 0 });
const totalPassengers = computed(() => passengers.value.adult + passengers.value.children + passengers.value.infant);

const updateCount = (type, delta) => {
  const newVal = passengers.value[type] + delta;
  if (type === 'adult' && newVal < 1) return;
  if (newVal >= 0 && newVal <= 9) passengers.value[type] = newVal;
};

// --- 5. SEARCH EXECUTION ---
const handleSearch = () => {
  // Check if activity code validation is complete
  if (!bookingStore.hasActivityCodeValidation) {
    showActivityCodeModal.value = true;
    return;
  }

  // Check if fields are empty
  if (!selectedFrom.value || !selectedTo.value) {
    notificationStore.warn("Please select both Origin and Destination.");
    return;
  }

  // Check if they are the same
  if (selectedFrom.value.code === selectedTo.value.code) {
    notificationStore.warn("Origin and Destination cannot be the same airport.");
    return;
  }

  // Check if return date is required for round-trip
  if (tripType.value === 'round-trip' && !returnDate.value) {
    notificationStore.warn("Please select a return date for round-trip flights.");
    return;
  }

  bookingStore.setPassengerCount(passengers.value);
  bookingStore.setTripType(tripType.value);
  bookingStore.startSession();
  console.log('Passenger Count:', bookingStore.passengerCount)

  router.push({
    name: 'SearchResults',
    query:{
        origin: selectedFrom.value.code,
        destination: selectedTo.value.code,
        departure: departureDate.value,
        returnDate: returnDate.value,
        tripType: tripType.value,
        adults: passengers.value.adult,
        children: passengers.value.children,
        infants: passengers.value.infant
    }
  })
};

// Handle activity code modal continue
const handleActivityCodeContinue = () => {
  console.log('✅ Activity code validation complete, proceeding with search');
  // After modal closes, automatically trigger search
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

    <!-- Trip Type Tabs -->
    <div class="mb-5 flex gap-2 border-b border-gray-200">
      <button
        v-for="t in ['one-way', 'round-trip', 'multi-city']"
        :key="t"
        @click="tripType = t"
        class="cursor-pointer border-b-4 px-4 py-2 text-xs font-bold uppercase tracking-wide text-gray-500 transition"
        :class="tripType === t
          ? 'border-[#d11241] text-[#003870]'
          : 'border-transparent hover:text-[#003870]'"
      >
        {{ t.replace('-', ' ') }}
      </button>
    </div>

    <!-- Search Grid -->
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">

      <!-- FROM -->
      <div class="relative flex flex-col">
        <label class="mb-1 text-[0.7rem] font-bold tracking-wide text-[#003870]">
          FROM
        </label>
        <input
          v-model="fromSearch"
          @input="searchAirports(fromSearch, 'from')"
          @focus="fromSearch = ''; fromResults = []"
          placeholder="e.g. MNL"
          class="w-full rounded-[2px] border border-gray-300 bg-white px-2 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#003870]"
        />

        <ul
          v-if="fromResults.length"
          class="absolute left-0 top-full z-50 max-h-64 w-full overflow-y-auto border border-gray-300 bg-white shadow-lg"
        >
          <li
            v-for="a in fromResults"
            :key="a.id"
            @click="selectAirport(a, 'from')"
            class="cursor-pointer border-b border-gray-100 p-3 hover:bg-gray-50"
          >
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-lg font-extrabold text-[#003870]">{{ a.code }}</span>
              <span class="font-medium text-gray-700">- {{ a.city }}</span>
              <small class="w-full text-xs text-gray-400">{{ a.name }}</small>
            </div>
          </li>
        </ul>
      </div>

      <!-- TO -->
      <div class="relative flex flex-col">
        <label class="mb-1 text-[0.7rem] font-bold tracking-wide text-[#003870]">
          TO
        </label>
        <input
          v-model="toSearch"
          @input="searchAirports(toSearch, 'to')"
          @focus="toSearch = ''; toResults = []"
          placeholder="Destination City/Code"
          class="w-full rounded-[2px] border border-gray-300 bg-white px-2 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#003870]"
        />

        <ul
          v-if="toResults.length"
          class="absolute left-0 top-full z-50 max-h-64 w-full overflow-y-auto border border-gray-300 bg-white shadow-lg"
        >
          <li
            v-for="a in toResults"
            :key="a.id"
            @click="selectAirport(a, 'to')"
            class="cursor-pointer border-b border-gray-100 p-3 hover:bg-gray-50"
          >
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-lg font-extrabold text-[#003870]">{{ a.code }}</span>
              <span class="font-medium text-gray-700">- {{ a.city }}</span>
              <small class="w-full text-xs text-gray-400">{{ a.name }}</small>
            </div>
          </li>
        </ul>
      </div>

      <!-- DEPARTURE -->
      <div class="flex flex-col">
        <label class="mb-1 text-[0.7rem] font-bold tracking-wide text-[#003870]">
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
        <label class="mb-1 text-[0.7rem] font-bold tracking-wide text-[#003870]">
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
        <label class="mb-1 text-[0.7rem] font-bold tracking-wide text-[#003870]">
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
          class="absolute right-0 top-full z-50 w-60 border border-gray-300 bg-white p-5 shadow-xl"
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
                class="flex h-8 w-8 items-center justify-center rounded-full border border-[#003870] text-lg text-[#003870]"
              >
                −
              </button>
              <span>{{ val }}</span>
              <button
                @click="updateCount(type, 1)"
                class="flex h-8 w-8 items-center justify-center rounded-full border border-[#003870] text-lg text-[#003870]"
              >
                +
              </button>
            </div>
          </div>

          <button
            @click="showPassengerDropdown = false"
            class="w-full rounded-[2px] bg-[#003870] py-2 text-xs font-bold text-white"
          >
            DONE
          </button>
        </div>
      </div>

      <!-- SEARCH BUTTON -->
      <div class="flex flex-col justify-end">
        <button
          @click="handleSearch"
          class="h-12 w-full rounded-[2px] bg-[#FF579A] text-lg font-bold text-white transition hover:bg-[#ff7bb0]"
        >
          SEARCH FLIGHTS
        </button>
      </div>

    </div>
  </div>
</template>
