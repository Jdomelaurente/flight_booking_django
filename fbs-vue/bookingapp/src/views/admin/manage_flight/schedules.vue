<template>
  <div class="p-6 poppins">
    <!-- Header & Tools Section -->
    <AdminTableTool 
      v-model="searchQuery" 
      placeholder="Search flight number or schedule ID..."
    >
      <template #filters>
        <div class="flex items-center gap-2">
          <select 
            v-model="filterStatus"
            class="text-[11px] font-bold border border-gray-200 px-3 py-2 bg-white rounded-[1px] outline-none focus:border-[#fe3787] poppins cursor-pointer"
          >
            <option value="all">Any Status</option>
            <option value="Open">Open</option>
            <option value="Closed">Closed</option>
            <option value="On Flight">On Flight</option>
            <option value="Arrived">Arrived</option>
          </select>

          <select 
            v-model="filterStops"
            class="text-[11px] font-bold border border-gray-200 px-3 py-2 bg-white rounded-[1px] outline-none focus:border-[#fe3787] poppins cursor-pointer"
          >
            <option value="all">Any Stops</option>
            <option value="0">Non-stop</option>
            <option value="1">1 Stop</option>
            <option value="2">2 Stops</option>
            <option value="3">3+ Stops</option>
          </select>
        </div>
      </template>
      <template #actions>
        <button 
          @click="openModal()" 
          class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[12px] rounded-[1px] shadow-sm transition-all"
        >
          <i class="ph ph-plus text-[14px]"></i> Add
        </button>
      </template>
    </AdminTableTool>

    <!-- Stats Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div 
        v-for="(count, label) in statsItems" 
        :key="label" 
        class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins leading-none mb-2">{{ label }}</p>
            <p class="text-2xl font-bold text-[#002D1E] poppins">{{ count }}</p>
          </div>
          <div :class="statIconClass(label)" class="w-12 h-12 rounded-full flex items-center justify-center">
            <i :class="[statIcon(label), 'text-xl']"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Schedule List Section -->
    <div class="space-y-2">

      <!-- List Header -->
      <div class="hidden md:grid grid-cols-[2fr_2fr_1fr_auto_auto] gap-4 px-5 py-2 bg-gray-50 border border-gray-200 rounded-[1px]">
        <span class="text-[9px] font-black uppercase tracking-widest text-gray-400 poppins">Flight / Route</span>
        <span class="text-[9px] font-black uppercase tracking-widest text-gray-400 poppins">Schedule</span>
        <span class="text-[9px] font-black uppercase tracking-widest text-gray-400 poppins">Duration</span>
        <span class="text-[9px] font-black uppercase tracking-widest text-gray-400 poppins text-center w-28">Status</span>
        <span class="text-[9px] font-black uppercase tracking-widest text-gray-400 poppins w-16 text-right">Action</span>
      </div>

      <!-- Empty State -->
      <div v-if="schedules.length === 0" class="bg-white border border-gray-200 rounded-[1px] px-6 py-14 text-center">
        <i class="ph ph-airplane text-4xl text-gray-200 block mb-3"></i>
        <p class="text-gray-400 text-sm font-bold poppins">No flight schedules found.</p>
      </div>

      <!-- Schedule Cards -->
      <div
        v-for="s in schedules"
        :key="s.id"
        :id="`schedule-row-${s.id}`"
        :class="{'highlight-active': highlightedId === s.id}"
        class="bg-white border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md hover:border-gray-300 transition-all duration-200 overflow-hidden"
      >
        <div class="grid grid-cols-1 md:grid-cols-[2fr_2fr_1fr_auto_auto] gap-0 md:gap-4 md:items-center px-5 py-4">

          <!-- Col 1: Flight + Route -->
          <div class="flex items-start gap-3">
            <!-- Icon -->
            <div class="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
                 :class="s.status === 'On Flight' ? 'bg-blue-100' : s.status === 'Open' ? 'bg-green-100' : s.status === 'Arrived' ? 'bg-purple-100' : 'bg-gray-100'">
              <i class="ph ph-airplane-tilt text-base"
                 :class="s.status === 'On Flight' ? 'text-blue-600' : s.status === 'Open' ? 'text-green-600' : s.status === 'Arrived' ? 'text-purple-600' : 'text-gray-400'"></i>
            </div>
            <!-- Text -->
            <div class="min-w-0">
              <!-- Flight Number -->
              <router-link
                :to="{ name: 'ManageFlights', query: { highlight: s.flight } }"
                class="font-black text-[#002D1E] poppins text-[13px] hover:text-[#fe3787] transition-colors flex items-center gap-1 group leading-tight"
                title="View Flight"
              >
                {{ s.flight_number }}
                <i class="ph ph-arrow-square-out text-[9px] opacity-0 group-hover:opacity-70 transition-opacity"></i>
              </router-link>

              <!-- Route: compact dot-line path indicator -->
              <div v-if="s.flight_detail" class="mt-1.5 flex items-end gap-0">
                <!-- Origin dot + label -->
                <div class="flex flex-col items-center">
                  <div class="w-2 h-2 rounded-full bg-[#002D1E] ring-2 ring-[#002D1E]/20"></div>
                  <span class="text-[7px] font-black text-gray-500 uppercase tracking-tight mt-0.5 leading-none">
                    {{ s.flight_detail.route_display?.split(' → ')[0]?.trim() || '—' }}
                  </span>
                </div>

                <!-- Stops: line + dot + label for each layover -->
                <template v-for="(stop, idx) in getLayovers(s.flight_detail.layovers_data)" :key="idx">
                  <!-- connecting line before stop -->
                  <div class="h-[2px] w-5 bg-gradient-to-r from-gray-300 to-orange-300 mb-[5px]"></div>
                  <!-- stop dot + label -->
                  <div class="flex flex-col items-center">
                    <div class="w-1.5 h-1.5 rounded-full bg-orange-400 ring-2 ring-orange-200"></div>
                    <span class="text-[7px] font-black text-orange-400 uppercase tracking-tight mt-0.5 leading-none" :title="stop.city">
                      {{ stop.airport }}
                    </span>
                  </div>
                </template>

                <!-- connecting line to destination -->
                <div class="h-[2px] mb-[5px]"
                     :class="getLayovers(s.flight_detail.layovers_data).length > 0
                       ? 'w-5 bg-gradient-to-r from-orange-300 to-blue-400'
                       : 'w-8 bg-gradient-to-r from-[#002D1E]/30 to-blue-400'">
                </div>

                <!-- Destination dot + label -->
                <div class="flex flex-col items-center">
                  <div class="w-2 h-2 rounded-full bg-blue-500 ring-2 ring-blue-200"></div>
                  <span class="text-[7px] font-black text-gray-500 uppercase tracking-tight mt-0.5 leading-none">
                    {{ s.flight_detail.route_display?.split(' → ')[1]?.trim() || '—' }}
                  </span>
                </div>
              </div>

              <!-- Badges row -->
              <div class="flex items-center gap-1.5 mt-1.5">
                <span class="text-[8px] text-gray-300 font-bold uppercase tracking-tighter poppins">#{{ s.id }}</span>
                <span v-if="s.flight_detail"
                  :class="getLayovers(s.flight_detail.layovers_data).length === 0 ? 'bg-green-50 text-green-600 border-green-100' : 'bg-orange-50 text-orange-500 border-orange-100'"
                  class="border px-1.5 py-0.5 rounded-[2px] text-[8px] font-black uppercase poppins leading-none">
                  {{ getLayovers(s.flight_detail.layovers_data).length === 0 ? 'Non-stop' : `${getLayovers(s.flight_detail.layovers_data).length} Stop${getLayovers(s.flight_detail.layovers_data).length > 1 ? 's' : ''}` }}
                </span>
                <div class="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" title="Live"></div>
              </div>
            </div>
          </div>

          <!-- Col 2: Schedule Times -->
          <div class="flex items-center gap-6 mt-3 md:mt-0 pl-12 md:pl-0">
            <!-- Departure -->
            <div>
              <p class="text-[8px] font-black uppercase text-gray-400 tracking-widest poppins leading-none mb-1">Departure</p>
              <p class="text-[12px] font-black text-[#002D1E] poppins leading-none">{{ formatTime(s.departure_time) }}</p>
              <p class="text-[9px] text-gray-400 font-semibold poppins mt-0.5">{{ formatDate(s.departure_time) }}</p>
            </div>
            <!-- Arrow -->
            <div class="flex flex-col items-center gap-0.5">
              <div class="w-10 h-[2px] bg-gradient-to-r from-[#fe3787] to-blue-500 rounded-full"></div>
              <i class="ph ph-airplane-takeoff text-[10px] text-gray-300"></i>
            </div>
            <!-- Arrival -->
            <div>
              <p class="text-[8px] font-black uppercase text-gray-400 tracking-widest poppins leading-none mb-1">Arrival</p>
              <p class="text-[12px] font-black text-[#002D1E] poppins leading-none">{{ formatTime(s.arrival_time) }}</p>
              <p class="text-[9px] text-gray-400 font-semibold poppins mt-0.5">{{ formatDate(s.arrival_time) }}</p>
            </div>
          </div>

          <!-- Col 3: Duration -->
          <div class="mt-3 md:mt-0 pl-12 md:pl-0">
            <p class="text-[8px] font-black uppercase text-gray-400 tracking-widest poppins leading-none mb-1">Duration</p>
            <p class="text-[12px] font-bold text-gray-600 poppins italic">{{ s.duration_display || '—' }}</p>
          </div>

          <!-- Col 4: Status Badge -->
          <div class="mt-3 md:mt-0 pl-12 md:pl-0 w-28 flex justify-start md:justify-center">
            <span :class="statusClass(s.status)" class="px-3 py-1.5 rounded-full text-[9px] font-black uppercase poppins tracking-wide inline-flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full inline-block"
                    :class="s.status === 'On Flight' ? 'bg-blue-500 animate-pulse' : s.status === 'Open' ? 'bg-green-500' : s.status === 'Arrived' ? 'bg-purple-500' : 'bg-gray-400'">
              </span>
              {{ s.status }}
            </span>
          </div>

          <!-- Col 5: Action -->
          <div class="mt-3 md:mt-0 pl-12 md:pl-0 w-16 flex justify-end">
            <button
              @click="deleteSchedule(s.id)"
              class="w-8 h-8 flex items-center justify-center rounded-full text-gray-300 hover:text-red-500 hover:bg-red-50 transition-all"
              title="Delete Schedule"
            >
              <i class="ph ph-trash text-base"></i>
            </button>
          </div>

        </div>
      </div>
    </div>

      <!-- Pagination Section -->
      <div v-if="totalRecords > itemsPerPage" class="mt-4 px-2 py-3 flex items-center justify-between">
        <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
          Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ totalRecords }}
        </div>
        <div class="flex gap-1">
          <button 
            @click="prevPage" 
            :disabled="currentPage === 1"
            class="px-4 py-2 bg-white border border-gray-200 rounded-[1px] text-xs font-bold uppercase hover:bg-gray-50 disabled:opacity-50 poppins transition-all shadow-sm"
          >
            Prev
          </button>
          <button 
            v-for="page in visiblePages" 
            :key="page"
            @click="goToPage(page)"
            :disabled="page === '...'"
            :class="[
              'px-4 py-2 border rounded-[1px] text-xs font-bold uppercase poppins transition-all shadow-sm',
              page === '...' ? 'bg-white border-gray-200 text-gray-400' : 
              currentPage === page ? 'bg-[#fe3787] text-white border-[#fe3787]' : 'bg-white border-gray-200 text-[#002D1E] hover:bg-gray-50'
            ]"
          >
            {{ page }}
          </button>
          <button 
            @click="nextPage" 
            :disabled="currentPage === totalPages"
            class="px-4 py-2 bg-white border border-gray-200 rounded-[1px] text-xs font-bold uppercase hover:bg-gray-50 disabled:opacity-50 poppins transition-all shadow-sm"
          >
            Next
          </button>
        </div>
      </div>

    <!-- Modal Section -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">New Flight Schedule</h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>

        <div v-if="errorMessage" class="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 animate-pulse">
          <div class="flex items-center gap-3">
            <i class="ph ph-warning-circle-bold text-xl"></i>
            <span class="text-xs font-bold uppercase poppins leading-tight">{{ errorMessage }}</span>
          </div>
        </div>

        <form @submit.prevent="saveSchedule" class="space-y-6">
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Select Flight Number</label>
            <SearchableSelect
              v-model="form.flight"
              :options="flightOptions"
              placeholder="Type a flight number (e.g. PR101)..."
              label="Flight"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Departure Date & Time</label>
              <input v-model="form.departure_time" type="datetime-local" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Arrival Date & Time</label>
              <input v-model="form.arrival_time" type="datetime-local" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
            </div>
          </div>



          <div class="flex justify-end gap-3 pt-6 border-t mt-4">
            <button type="button" @click="isModalOpen = false" class="text-sm text-gray-500 font-medium hover:text-gray-700 poppins">Cancel</button>
            <button type="submit" :disabled="loading" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins">
              {{ loading ? 'Validating...' : 'Confirm Schedule' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/admin/api';
import { useModalStore } from '@/stores/modal';
import SearchableSelect from '@/components/admin/SearchableSelect.vue';
import AdminTableTool from '@/components/admin/AdminTableTool.vue';

const modalStore = useModalStore();
const route = useRoute();

const schedules = ref([]);
const flightList = ref([]);
const apiStats = ref({ total: 0, open: 0, active: 0, arrived: 0 });

const flightOptions = computed(() =>
  flightList.value.map(f => ({ value: f.id, label: f.flight_number }))
);
const isModalOpen = ref(false);
const loading = ref(false);
const errorMessage = ref(null);
const highlightedId = ref(null);
const searchQuery = ref('');
const filterStatus = ref('all');
const filterStops = ref('all');

const form = ref({
  flight: null,
  departure_time: '',
  arrival_time: ''
});

// Pagination State
const currentPage = ref(1);
const itemsPerPage = 10;
const totalRecords = ref(0);

// Computed Stats
const statsItems = computed(() => {
  return {
    'Total Flights': apiStats.value.total,
    'Open for Booking': apiStats.value.open,
    'Planes In-Air': apiStats.value.active,
    'Completed': apiStats.value.arrived,
  };
});

// Pagination Logic
const totalPages = computed(() => Math.ceil(totalRecords.value / itemsPerPage));
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage);
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, totalRecords.value));

const visiblePages = computed(() => {
  const pages = [];
  const t = totalPages.value;
  const c = currentPage.value;
  if (t <= 5) {
    for (let i = 1; i <= t; i++) pages.push(i);
  } else {
    if (c <= 3) {
      for (let i = 1; i <= 4; i++) pages.push(i);
      pages.push('...', t);
    } else if (c >= t - 2) {
      pages.push(1, '...');
      for (let i = t - 3; i <= t; i++) pages.push(i);
    } else {
      pages.push(1, '...', c - 1, c, c + 1, '...', t);
    }
  }
  return pages;
});

const statIcon = (label) => {
  if (label === 'Total Flights') return 'ph ph-airplane';
  if (label === 'Open for Booking') return 'ph ph-ticket';
  if (label === 'Planes In-Air') return 'ph ph-airplane-in-flight';
  return 'ph ph-checks';
};

const statIconClass = (label) => {
  if (label === 'Total Flights') return 'bg-blue-100 text-blue-600';
  if (label === 'Open for Booking') return 'bg-green-100 text-green-600';
  if (label === 'Planes In-Air') return 'bg-purple-100 text-purple-600';
  return 'bg-pink-100 text-pink-600';
};

const fetchData = async () => {
  try {
    const params = { page: currentPage.value, page_size: itemsPerPage };
    if (searchQuery.value) params.search = searchQuery.value;
    if (filterStatus.value !== 'all') params.status = filterStatus.value;
    if (filterStops.value !== 'all') params.stops = filterStops.value;

    const [resS, resF, resStats] = await Promise.all([
      api.get('/schedules/', { params }),
      api.get('/flights/', { params: { pagination: 'false' } }),
      api.get('/schedules/stats/')
    ]);
    schedules.value = resS.data.results || resS.data;
    totalRecords.value = resS.data.count || schedules.value.length;
    flightList.value = resF.data.results || resF.data;
    apiStats.value = resStats.data;

    if (route.query.page) {
        currentPage.value = parseInt(route.query.page);
    }

    if (route.query.highlight) {
        const hId = parseInt(route.query.highlight);
        highlightedId.value = hId;

        setTimeout(() => {
            const el = document.getElementById(`schedule-row-${hId}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => { highlightedId.value = null; }, 3000);
        }, 500);
    }
  } catch (err) {
    console.error("Fetch Error:", err);
  }
};

const saveSchedule = async () => {
  loading.value = true;
  errorMessage.value = null;
  
  if (!form.value.flight) {
    errorMessage.value = "Please select a flight.";
    loading.value = false;
    return;
  }
  
  const payload = {
    flight: parseInt(form.value.flight),
    departure_time: form.value.departure_time,
    arrival_time: form.value.arrival_time
  };
  
  try {
    await api.post('/schedules/', payload);
    await fetchData();
    isModalOpen.value = false;
  } catch (err) {
    if (err.response && err.response.data) {
      const data = err.response.data;
      if (data.flight) errorMessage.value = `Flight: ${data.flight.join(', ')}`;
      else if (data.non_field_errors) errorMessage.value = data.non_field_errors.join(', ');
      else if (data.detail) errorMessage.value = data.detail;
      else errorMessage.value = "An error occurred. Check inputs.";
    } else {
      errorMessage.value = "Connection error.";
    }
  } finally {
    loading.value = false;
  }
};

const openModal = () => {
  form.value = { flight: null, departure_time: '', arrival_time: '' };
  errorMessage.value = null;
  isModalOpen.value = true;
};

const deleteSchedule = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Purge Schedule?',
    message: 'Are you sure you want to permanently remove this schedule?',
    variant: 'danger',
    confirmText: 'Purge',
    loadingText: 'Purging...'
  });

  if (confirmed) {
    modalStore.setLoader(true);
    try {
      await api.delete(`/schedules/${id}/`);
      await fetchData();
      modalStore.close(true);
    } catch (err) {
      console.error("Delete Error:", err);
      modalStore.setLoader(false);
    }
  }
};

let searchTimeout = null;
const debounceSearch = () => { clearTimeout(searchTimeout); searchTimeout = setTimeout(() => fetchData(), 500); };
watch([searchQuery, filterStatus, filterStops], () => { currentPage.value = 1; debounceSearch(); });

const prevPage = () => { if (currentPage.value > 1) { currentPage.value--; fetchData(); } };
const nextPage = () => { if (currentPage.value < totalPages.value) { currentPage.value++; fetchData(); } };
const goToPage = (p) => { if (p !== '...') { currentPage.value = p; fetchData(); } };

// UI Helpers
const formatTime = (d) => new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
const formatDate = (d) => new Date(d).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
const statusClass = (s) => {
  if (s === 'Open') return 'bg-green-100 text-green-700';
  if (s === 'Closed') return 'bg-pink-100 text-pink-700';
  if (s === 'On Flight') return 'bg-blue-100 text-blue-700';
  if (s === 'Arrived') return 'bg-purple-100 text-purple-700';
  return 'bg-gray-100 text-gray-500';
};

// Parse layovers_data which may come as a JSON string or already-parsed array
const getLayovers = (layoversData) => {
  if (!layoversData) return [];
  try {
    return typeof layoversData === 'string' ? JSON.parse(layoversData) : layoversData;
  } catch {
    return [];
  }
};

onMounted(fetchData);
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

@keyframes pulse-highlight {
  0% { background-color: rgba(254, 55, 135, 0.05); }
  50% { background-color: rgba(254, 55, 135, 0.2); }
  100% { background-color: rgba(254, 55, 135, 0.05); }
}

.highlight-active {
  animation: pulse-highlight 1.5s ease-in-out infinite;
  border-left: 4px solid #fe3787 !important;
  box-shadow: inset 0 0 20px rgba(254, 55, 135, 0.1);
}

.poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
