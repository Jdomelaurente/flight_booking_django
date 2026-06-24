<template>
  <div class="p-6 poppins">
    <!-- Action Buttons -->
    <div class="flex items-center mb-6">
      <div class="flex items-center gap-2">
        <button @click="showTodayCheckIns" class="bg-white border border-gray-200 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all">
          <i class="ph ph-calendar-check"></i> Training Registry
        </button>
        <button @click="refreshData" class="bg-white border border-gray-200 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all">
          <i class="ph ph-arrows-clockwise"></i> Refresh
        </button>
        <button @click="printAllBoarding" class="bg-white border border-gray-200 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all">
          <i class="ph ph-printer"></i> Bulk Print
        </button>
      </div>
    </div>

    <!-- Check-in Stats -->
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

    <!-- Search and Filter -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-4 mb-6">
      <div class="flex flex-col md:flex-row md:items-center gap-4">
        <div class="relative flex-1">
          <i class="ph ph-magnifying-glass absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search by trainee or simulation ID..." 
            class="pl-10 pr-4 py-2 border border-gray-200 rounded-[1px] w-full outline-none focus:border-[#fe3787] transition-all poppins text-sm"
            @input="debounceSearch"
          />
        </div>
        
        <select 
          v-model="selectedFlight" 
          class="border border-gray-200 px-3 py-2 rounded-[1px] outline-none focus:border-[#fe3787] transition-all poppins text-sm bg-white min-w-[150px]"
          @change="fetchCheckIns"
        >
          <option value="">All Flights</option>
          <option v-for="flight in uniqueFlights" :key="flight" :value="flight">{{ flight }}</option>
        </select>

        <select 
          v-model="selectedStatus" 
          class="border border-gray-200 px-3 py-2 rounded-[1px] outline-none focus:border-[#fe3787] transition-all poppins text-sm bg-white min-w-[150px]"
          @change="fetchCheckIns"
        >
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="checked-in">Checked-in</option>
          <option value="boarding">Boarding</option>
          <option value="completed">Completed</option>
        </select>

        <button 
          @click="clearFilters" 
          class="bg-gray-100 text-gray-600 px-6 py-2 rounded-[1px] hover:bg-gray-200 font-bold poppins text-sm transition-all"
        >
          Reset
        </button>
      </div>
    </div>

    <!-- Main Table -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Trainee</th>
            <th class="px-6 py-4 poppins">Simulation Route</th>
            <th class="px-6 py-4 poppins text-center">Identity / Baggage</th>
            <th class="px-6 py-4 poppins">Boarding Token</th>
            <th class="px-6 py-4 poppins text-center">Status</th>
            <th class="px-6 py-4 text-right poppins">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr 
            v-for="checkIn in paginatedCheckIns" 
            :key="checkIn.id" 
            :id="`checkin-row-${checkIn.id}`"
            :class="{'highlight-active': highlightedId === checkIn.id}"
            class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium"
          >
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center font-bold text-blue-600 poppins">
                  {{ checkIn.seat_number?.substring(0, 1) || '?' }}
                </div>
                <div>
                  <span class="font-bold text-[#002D1E] block poppins">{{ checkIn.passenger_name }}</span>
                  <span class="text-[10px] text-[#fe3787] font-bold poppins uppercase">Seat {{ checkIn.seat_number || 'TBD' }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <router-link 
                :to="{ name: 'ManageFlights', query: { highlight: checkIn.booking_detail?.schedule?.flight?.id } }"
                class="font-bold text-[#002D1E] poppins uppercase hover:text-[#fe3787] transition-all flex items-center gap-1 group"
                title="View Flight Details"
              >
                {{ checkIn.flight_number }}
                <i class="ph ph-link-simple text-[10px] opacity-0 group-hover:opacity-100 transition-opacity"></i>
              </router-link>
              <div class="text-[10px] text-gray-400 poppins">{{ formatRoute(checkIn.route) }}</div>
              <div class="text-[10px] text-gray-400 poppins uppercase">{{ formatTime(checkIn.departure_time) }}</div>
            </td>
            <td class="px-6 py-4 text-center">
              <div class="flex flex-col items-center gap-1">
                <div class="flex items-center gap-1 text-[10px] font-bold text-gray-500 poppins uppercase bg-gray-50 px-2 py-1 rounded-[1px] border border-gray-100">
                  <i class="ph ph-suitcase-simple"></i> {{ checkIn.baggage_count || 0 }} Bags • {{ checkIn.baggage_weight || 0 }}kg
                </div>
                <div v-if="checkIn.check_in_counter" class="text-[10px] text-gray-400 poppins">Counter {{ checkIn.check_in_counter }}</div>
              </div>
            </td>
            <td class="px-6 py-4">
              <div v-if="checkIn.boarding_pass" class="flex items-center gap-2">
                <i class="ph ph-ticket text-green-500 text-lg"></i>
                <span class="font-bold text-[#002D1E] poppins tracking-tighter">{{ checkIn.boarding_pass }}</span>
              </div>
              <div v-else class="text-pink-500 font-bold poppins text-[10px] uppercase">Awaiting Issue</div>
            </td>
            <td class="px-6 py-4 text-center">
              <span :class="statusClass(checkIn.status)" class="px-3 py-1 rounded-full text-[10px] font-bold uppercase poppins">
                {{ checkIn.status }}
              </span>
              <div class="text-[9px] text-gray-400 mt-1 poppins font-bold">{{ checkIn.status === 'pending' ? 'NOT CHECKED' : formatDateTime(checkIn.check_in_time) }}</div>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-1">
                <button @click="checkInPassenger(checkIn)" class="text-green-600 hover:text-green-400 p-2 transition-colors" title="Check-in" v-if="checkIn.status === 'pending'">
                  <i class="ph ph-check-circle text-lg"></i>
                </button>
                <button @click="printBoardingPass(checkIn)" class="text-purple-600 hover:text-purple-400 p-2 transition-colors" title="Print Token" v-if="checkIn.boarding_pass">
                  <i class="ph ph-printer text-lg"></i>
                </button>
                <button @click="editCheckIn(checkIn)" class="text-blue-600 hover:text-blue-400 p-2 transition-colors" title="Edit">
                  <i class="ph ph-pencil-simple text-lg"></i>
                </button>
                <button @click="deleteCheckIn(checkIn.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors" title="Delete">
                  <i class="ph ph-trash text-lg"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty/Pagination States (Simplified for brevity as per list.vue pattern) -->
      <div v-if="checkIns.length === 0 && !loading" class="p-12 text-center poppins">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-50 border border-gray-100 rounded-full flex items-center justify-center">
          <i class="ph ph-airplane-takeoff text-2xl text-gray-300"></i>
        </div>
        <h3 class="text-lg font-bold text-[#002D1E] mb-2 poppins">No Records</h3>
        <p class="text-sm text-gray-400 poppins">Check-in data will appear here during active flights.</p>
      </div>

      <!-- Pagination -->
      <div v-if="filteredCheckIns.length > itemsPerPage" class="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
        <div class="flex items-center justify-between">
          <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
            Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ filteredCheckIns.length }}
          </div>
          <div class="flex gap-1">
            <button @click="prevPage" :disabled="currentPage === 1" class="px-4 py-2 bg-white border border-gray-200 rounded-[1px] text-xs font-bold uppercase hover:bg-gray-50 disabled:opacity-50 poppins transition-all shadow-sm">Prev</button>
            <button v-for="page in visiblePages" :key="page" @click="goToPage(page)" :disabled="page === '...'" :class="['px-4 py-2 border rounded-[1px] text-xs font-bold uppercase poppins transition-all shadow-sm', page === '...' ? 'bg-white border-gray-200 text-gray-400' : currentPage === page ? 'bg-[#fe3787] text-white border-[#fe3787]' : 'bg-white border-gray-200 text-[#002D1E] hover:bg-gray-50']">{{ page }}</button>
            <button @click="nextPage" :disabled="currentPage === totalPages" class="px-4 py-2 bg-white border border-gray-200 rounded-[1px] text-xs font-bold uppercase hover:bg-gray-50 disabled:opacity-50 poppins transition-all shadow-sm">Next</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals (Standardized look) -->
    <div v-if="showCheckInModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-lg p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">Registry Process</h2>
          <button @click="closeModal" class="text-gray-400 hover:text-black"><i class="ph ph-x text-xl"></i></button>
        </div>
        
        <form @submit.prevent="processCheckIn" class="space-y-6">
          <div class="bg-gray-50 p-4 border border-gray-100 rounded-[1px] flex items-center gap-4">
            <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600"><i class="ph ph-user text-xl"></i></div>
            <div>
              <div class="font-bold text-[#002D1E] poppins">{{ selectedCheckIn?.passenger_name }}</div>
              <div class="text-[10px] uppercase font-bold text-gray-400 poppins">Flight {{ selectedCheckIn?.flight_number }}</div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Seat Number</label>
              <input v-model="checkInForm.seat_number" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Counter</label>
              <input v-model="checkInForm.check_in_counter" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]">
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Bags</label>
              <input v-model="checkInForm.baggage_count" type="number" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]">
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Weight (kg)</label>
              <input v-model="checkInForm.baggage_weight" type="number" step="0.1" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]">
            </div>
          </div>
          
          <div class="flex justify-end gap-3 pt-6 border-t">
            <button type="button" @click="closeModal" class="text-sm text-gray-500 font-medium poppins">Cancel</button>
            <button type="submit" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins">Complete Registration</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Boarding Pass Token -->
    <div v-if="showBoardingModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-sm rounded-[1px] shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-300">
        <div class="bg-[#002D1E] p-6 text-white flex justify-between items-start">
          <div>
            <div class="text-[10px] uppercase font-bold opacity-60 poppins">Boarding Pass</div>
            <div class="text-2xl font-black poppins tracking-tighter uppercase">{{ selectedCheckIn?.flight_number }}</div>
          </div>
          <div class="text-right">
            <div class="text-[10px] uppercase font-bold opacity-60 poppins">Seat</div>
            <div class="text-2xl font-black poppins">{{ selectedCheckIn?.seat_number }}</div>
          </div>
        </div>
        
        <div class="p-6 space-y-4">
          <div class="border-b border-dashed border-gray-200 pb-4">
            <div class="text-[10px] uppercase font-bold text-gray-400 poppins">Passenger</div>
            <div class="text-lg font-bold text-[#002D1E] poppins">{{ selectedCheckIn?.passenger_name }}</div>
          </div>
          
          <div class="grid grid-cols-2 gap-4 pb-4 border-b border-dashed border-gray-200">
            <div>
              <div class="text-[10px] uppercase font-bold text-gray-400 poppins">Departure</div>
              <div class="font-bold text-[#002D1E] poppins">{{ formatTime(selectedCheckIn?.departure_time) }}</div>
            </div>
            <div>
              <div class="text-[10px] uppercase font-bold text-gray-400 poppins">Boarding</div>
              <div class="font-bold text-[#fe3787] poppins">{{ calculateBoardingTime(selectedCheckIn?.departure_time) }}</div>
            </div>
          </div>

          <div class="text-center py-4 bg-gray-50 border border-gray-100 rounded-[1px]">
             <div class="text-[14px] font-black font-mono text-gray-800 mb-2 leading-none uppercase tracking-widest">{{ selectedCheckIn?.boarding_pass }}</div>
             <div class="text-xs text-gray-400 poppins font-bold tracking-[0.4em]">||||||||||||||||||||||||||||||||||</div>
          </div>
        </div>

        <div class="p-4 bg-gray-50 flex justify-end gap-3">
          <button @click="closeBoardingModal" class="text-xs font-bold text-gray-400 uppercase poppins">Close</button>
          <button @click="printCurrentBoardingPass" class="bg-white border border-gray-200 px-4 py-2 text-xs font-bold uppercase shadow-sm rounded-[1px] poppins"><i class="ph ph-printer mr-2"></i> Print</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/admin/api'

const route = useRoute()

// Reactive state
const checkIns = ref([])
const loading = ref(false)
const showCheckInModal = ref(false)
const showBoardingModal = ref(false)
const selectedCheckIn = ref(null)
const highlightedId = ref(null);

// Filters and pagination
const searchQuery = ref('')
const selectedFlight = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Form data
const checkInForm = ref({
  seat_number: '',
  check_in_counter: '',
  baggage_count: 0,
  baggage_weight: 0,
  special_instructions: '',
  status: 'checked-in'
})

// Computed properties
const statsItems = computed(() => {
  const total = checkIns.value.length
  const todayStr = new Date().toISOString().split('T')[0]
  const todays = checkIns.value.filter(c => c.check_in_time && c.check_in_time.startsWith(todayStr)).length
  const pending = checkIns.value.filter(c => c.status === 'pending').length
  const baggage = checkIns.value.reduce((sum, c) => sum + (c.baggage_count || 0), 0)
  
  return {
    'Total Registered': total,
    "Today's Activity": todays,
    'Awaiting Registry': pending,
    'Baggage Units': baggage
  }
})

const statIcon = (label) => {
  if (label === 'Total Registered') return 'ph ph-users-four';
  if (label === "Today's Activity") return 'ph ph-calendar-check';
  if (label === 'Awaiting Registry') return 'ph ph-hourglass-high';
  return 'ph ph-suitcase';
};

const statIconClass = (label) => {
  if (label === 'Total Registered') return 'bg-blue-100 text-blue-600';
  if (label === "Today's Activity") return 'bg-green-100 text-green-600';
  if (label === 'Awaiting Registry') return 'bg-purple-100 text-purple-600';
  return 'bg-pink-100 text-pink-600';
};

const uniqueFlights = computed(() => {
  const flights = new Set()
  checkIns.value.forEach(c => { if (c.flight_number) flights.add(c.flight_number) })
  return Array.from(flights).sort()
})

const filteredCheckIns = computed(() => {
  let filtered = checkIns.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    filtered = filtered.filter(c => c.passenger_name?.toLowerCase().includes(q) || c.flight_number?.toLowerCase().includes(q))
  }
  if (selectedFlight.value) filtered = filtered.filter(c => c.flight_number === selectedFlight.value)
  if (selectedStatus.value) filtered = filtered.filter(c => c.status === selectedStatus.value)
  return [...filtered].sort((a, b) => new Date(b.check_in_time || 0) - new Date(a.check_in_time || 0))
})

const totalPages = computed(() => Math.ceil(filteredCheckIns.value.length / itemsPerPage))
const paginatedCheckIns = computed(() => {
  const s = (currentPage.value - 1) * itemsPerPage
  return filteredCheckIns.value.slice(s, s + itemsPerPage)
})
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredCheckIns.value.length))

const visiblePages = computed(() => {
  const pages = []; const t = totalPages.value; const c = currentPage.value;
  if (t <= 5) for (let i = 1; i <= t; i++) pages.push(i)
  else {
    if (c <= 3) { for (let i = 1; i <= 4; i++) pages.push(i); pages.push('...', t) }
    else if (c >= t - 2) { pages.push(1, '...'); for (let i = t - 3; i <= t; i++) pages.push(i) }
    else pages.push(1, '...', c - 1, c, c + 1, '...', t)
  }
  return pages
})

// Methods
const fetchCheckIns = async () => {
  loading.value = true
  try {
    const response = await api.get('/checkins/')
    checkIns.value = (response.data.results || response.data).map(c => ({
      ...c,
      passenger_name: c.passenger_name || '',
      flight_number: c.flight_number || '',
      route: c.route || '',
      departure_time: c.departure_time || '',
      seat_number: c.seat_number || '',
      status: c.status || 'pending'
    }))

    if (route.query.page) {
        currentPage.value = parseInt(route.query.page);
    }

    if (route.query.highlight) {
        const hId = parseInt(route.query.highlight);
        highlightedId.value = hId;

        // Auto-navigate to the correct page for this ID
        const index = checkIns.value.findIndex(c => c.id === hId);
        if (index !== -1) {
            currentPage.value = Math.floor(index / itemsPerPage) + 1;
        }

        setTimeout(() => {
            const el = document.getElementById(`checkin-row-${hId}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => { highlightedId.value = null; }, 3000);
        }, 500);
    }
  } catch (err) { console.error(err) } finally { loading.value = false }
}

const refreshData = () => fetchCheckIns()
const showTodayCheckIns = () => {
  const today = new Date().toISOString().split('T')[0]
  const count = checkIns.value.filter(c => c.check_in_time?.startsWith(today)).length
  alert(`Daily Summary: ${count} passengers processed today.`)
}

const checkInPassenger = (c) => {
  selectedCheckIn.value = c
  checkInForm.value = {
    seat_number: c.seat_number || '',
    check_in_counter: c.check_in_counter || '',
    baggage_count: c.baggage_count || 0,
    baggage_weight: c.baggage_weight || 0,
    special_instructions: '',
    status: 'checked-in'
  }
  showCheckInModal.value = true
}

const processCheckIn = async () => {
  try {
    const bp = `BP-${Math.random().toString(36).substring(2, 10).toUpperCase()}`
    const data = { ...checkInForm.value, boarding_pass: bp, check_in_time: new Date().toISOString(), status: 'checked-in' }
    await api.put(`/checkins/${selectedCheckIn.value.id}/`, data)
    await fetchCheckIns()
    closeModal()
    selectedCheckIn.value = checkIns.value.find(c => c.id === selectedCheckIn.value.id)
    showBoardingModal.value = true
  } catch (err) { alert('Process failed.') }
}

const printBoardingPass = (c) => { selectedCheckIn.value = c; showBoardingModal.value = true }
const printCurrentBoardingPass = () => window.print()
const printAllBoarding = () => alert('Bulk printing initiated for all checked-in passengers.')
const editCheckIn = (c) => { selectedCheckIn.value = c; checkInForm.value = { ...c }; showCheckInModal.value = true }

const deleteCheckIn = async (id) => {
  if (confirm('Delete this record?')) {
    await api.delete(`/checkins/${id}/`)
    checkIns.value = checkIns.value.filter(c => c.id !== id)
  }
}

const closeModal = () => { showCheckInModal.value = false; selectedCheckIn.value = null }
const closeBoardingModal = () => { showBoardingModal.value = false; selectedCheckIn.value = null }

const statusClass = (s) => {
  switch(s?.toLowerCase()) {
    case 'pending': return 'bg-purple-100 text-purple-700'
    case 'checked-in': return 'bg-green-100 text-green-700'
    case 'boarding': return 'bg-blue-100 text-blue-700'
    case 'completed': return 'bg-gray-100 text-gray-700'
    default: return 'bg-gray-100 text-gray-500'
  }
}

const formatRoute = (r) => r?.replace('→', ' to ') || 'N/A'
const formatTime = (d) => d ? new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'N/A'
const formatDateTime = (d) => d ? new Date(d).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'N/A'
const calculateBoardingTime = (d) => d ? new Date(new Date(d).getTime() - 30 * 60000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'TBD'
const clearFilters = () => { searchQuery.value = ''; selectedFlight.value = ''; selectedStatus.value = ''; currentPage.value = 1; fetchCheckIns() }

let searchTimeout = null
const debounceSearch = () => { clearTimeout(searchTimeout); searchTimeout = setTimeout(() => fetchCheckIns(), 500) }

const prevPage = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const goToPage = (p) => { if (p !== '...') currentPage.value = p }

watch([searchQuery, selectedFlight, selectedStatus], () => currentPage.value = 1)
onMounted(fetchCheckIns)
</script>

<style scoped>
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

.poppins { font-family: 'Poppins', sans-serif; }
@media print { .no-print { display: none; } }
</style>
