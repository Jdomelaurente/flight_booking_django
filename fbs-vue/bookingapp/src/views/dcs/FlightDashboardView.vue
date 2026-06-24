<template>
  <div class="space-y-8 animate-in fade-in duration-700">
    <!-- Header with Stats -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight italic">Flight Operations</h1>
        <p class="text-sm text-slate-500 font-bold uppercase tracking-widest mt-1">Real-time Departure Monitoring Terminal</p>
      </div>
      
      <div class="flex items-center gap-4">
        <div class="bg-white border border-slate-200 p-1.5 rounded-[5px] shadow-sm flex items-center gap-1">
          <div class="bg-slate-50 px-5 py-3 rounded-[2px] flex flex-col min-w-[120px]">
            <span class="text-[10px] text-slate-400 font-black uppercase tracking-tighter mb-0.5">Network Flights</span>
            <span class="text-2xl font-black text-slate-900 leading-none tracking-tighter">{{ activeAirlineFlights.length }}</span>
          </div>
          <div class="bg-pink-600 px-5 py-3 rounded-[2px] flex flex-col min-w-[120px] shadow-lg shadow-pink-100">
            <span class="text-[10px] text-pink-200 font-black uppercase tracking-tighter mb-0.5">Today's Dispatch</span>
            <span class="text-2xl font-black text-white leading-none tracking-tighter">{{ todayFlightsCount }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- MODERN COMPACT FILTER BAR -->
    <div class="bg-white border border-slate-200 rounded-[5px] shadow-sm p-2 flex flex-col lg:flex-row items-center gap-2">
      <!-- Search Input -->
      <div class="relative flex-1 w-full group">
        <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-pink-500 transition-colors">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </span>
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Filter by flight, route, or carrier..." 
          class="w-full pl-12 pr-4 py-3.5 bg-slate-50 border-none rounded-[2px] text-sm focus:ring-2 focus:ring-pink-500/10 transition-all font-bold placeholder:text-slate-400"
        />
      </div>

      <div class="h-8 w-px bg-slate-100 hidden lg:block mx-2"></div>

      <!-- Quick Action Filters -->
      <div class="flex items-center gap-2 w-full lg:w-auto p-1">
        <button 
          @click="showTodayOnly = !showTodayOnly"
          :class="[
            'px-6 py-3.5 rounded-[2px] text-[10px] font-black uppercase tracking-widest transition-all border-2 shrink-0',
            showTodayOnly 
              ? 'bg-slate-900 border-slate-900 text-white shadow-xl shadow-slate-200' 
              : 'bg-white border-slate-100 text-slate-500 hover:border-pink-200 hover:text-pink-600'
          ]"
        >
          Current Cycle
        </button>



        <button 
          @click="$router.push({ name: 'DcsAirlineCheckin' })"
          class="px-6 py-3.5 rounded-[2px] text-[10px] font-black uppercase tracking-widest transition-all border-2 bg-slate-900 border-slate-900 text-white hover:bg-pink-600 hover:border-pink-600 shadow-lg shadow-slate-200 shrink-0 flex items-center gap-2"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          Online Check-in
        </button>

        <button 
          v-if="hasFilters"
          @click="resetFilters"
          class="bg-slate-50 text-slate-400 hover:text-red-500 p-3 rounded-[2px] transition-all hover:bg-red-50"
          title="Clear Terminal Filters"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-if="dcsStore.error" class="bg-red-50 border border-red-200 rounded-[5px] p-4 flex items-center gap-4 text-red-700 text-sm font-bold shadow-sm animate-in slide-in-from-top duration-300">
      <div class="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center text-red-600 shrink-0">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
      </div>
      {{ dcsStore.error }}
    </div>

    <!-- FLIGHT TERMINAL GRID -->
    <div v-if="dcsStore.isLoading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
      <div v-for="i in 6" :key="i" class="bg-white rounded-[5px] border border-slate-100 h-64 shadow-sm animate-pulse"></div>
    </div>

    <div v-else-if="filteredFlights.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 pb-10">
      <div
        v-for="flight in filteredFlights"
        :key="flight.id"
        class="bg-white rounded-[5px] border border-slate-200/60 shadow-sm hover:shadow-2xl hover:shadow-pink-500/10 hover:-translate-y-1.5 transition-all duration-500 group flex flex-col overflow-hidden"
      >
        <!-- UPPER SECTION: Flight Identity -->
        <div class="p-8 pb-6">
          <div class="flex justify-between items-start mb-6">
            <div class="flex items-center gap-4">
               <div class="w-12 h-12 bg-slate-900 rounded-[5px] flex flex-col items-center justify-center text-white border-2 border-slate-700 shadow-xl shadow-slate-200">
                  <span class="text-[9px] font-black uppercase tracking-tighter leading-none mb-0.5 opacity-60">Flt</span>
                  <span class="text-xs font-black leading-none">{{ flight.airline_code }}</span>
               </div>
               <div>
                  <h3 class="text-2x font-black text-slate-900 tracking-tighter leading-none">{{ flight.flight_number }}</h3>
                  <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1.5">{{ flight.airline_name }}</p>
               </div>
            </div>
            <div :class="[
              'px-3.5 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest shadow-sm border-2',
              getStatusClass(flight.status)
            ]">
              {{ flight.status || 'Scheduled' }}
            </div>
          </div>

          <div class="flex items-center justify-between relative px-2">
            <!-- Origin -->
            <div class="text-left z-10 bg-white pr-4">
              <div class="text-4xl font-black text-slate-900 tracking-tighter italic leading-none">{{ flight.origin }}</div>
              <div class="text-[11px] font-black text-slate-400 mt-2.5 uppercase tracking-tighter flex items-center gap-1.5">
                <svg class="w-3.5 h-3.5 text-pink-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ formatTime(flight.departure_time) }}
              </div>
            </div>

            <!-- Trajectory Line -->
            <div class="absolute inset-x-0 top-[18px] h-0.5 bg-slate-100 flex items-center justify-center -z-10">
               <div class="bg-white px-3 text-pink-600 transition-all duration-700 group-hover:scale-125">
                 <svg class="w-5 h-5 rotate-90" fill="currentColor" viewBox="0 0 24 24">
                   <path d="M21 16.5C21 16.88 20.79 17.21 20.47 17.38L12.57 21.82C12.41 21.94 12.21 22 12 22C11.79 22 11.59 21.94 11.43 21.82L3.53 17.38C3.21 17.21 3 16.88 3 16.5V7.5C3 7.12 3.21 6.79 3.53 6.62L11.43 2.18C11.59 2.06 11.79 2 12,2C12.21 2 12.41 2.06 12.57 2.18L20.47 6.62C20.79 6.79 21 7.12 21 7.5V16.5Z" />
                 </svg>
               </div>
            </div>

            <!-- Destination -->
            <div class="text-right z-10 bg-white pl-4">
              <div class="text-4xl font-black text-slate-900 tracking-tighter italic leading-none">{{ flight.destination }}</div>
              <div class="text-[11px] font-black text-slate-400 mt-2.5 uppercase tracking-tighter flex items-center gap-1.5 justify-end">
                {{ formatTime(flight.arrival_time) }}
                <svg class="w-3.5 h-3.5 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- LOWER SECTION: Operational Data -->
        <div class="flex-1 px-8 py-6 bg-slate-50 border-t border-slate-100/60">
           <div class="grid grid-cols-2 gap-4 mb-6">
              <div class="flex flex-col">
                <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Gate Status</span>
                <div class="flex items-center gap-2">
                   <div class="bg-white border border-slate-200 px-2 py-1 rounded-[2px] text-xs font-black text-slate-900 shadow-sm font-mono">
                     {{ flight.gate || '--' }}
                   </div>
                   <span class="text-[10px] font-bold text-slate-500 uppercase">MNL-T3</span>
                </div>
              </div>

              <div class="flex flex-col items-end">
                <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Load Analysis</span>
                <div class="flex items-center gap-1.5">
                   <div 
                     class="h-1.5 w-16 bg-slate-200 rounded-full overflow-hidden"
                     title="Load Factor"
                   >
                     <div 
                       class="h-full bg-pink-600 rounded-full transition-all duration-1000"
                       :style="{ width: `${getFlightLoad(flight)}%` }"
                     ></div>
                   </div>
                   <span class="text-[11px] font-black text-slate-900 italic underline decoration-pink-200 underline-offset-4">{{ getFlightLoad(flight) }}%</span>
                </div>
              </div>
           </div>

           <!-- Multi-metric Balance Bar -->
           <div class="bg-white border border-slate-200 rounded-[5px] p-4 flex items-center justify-between shadow-sm">
             <div class="flex items-center gap-3">
                <div :class="[
                  'w-8 h-8 rounded-[2px] flex items-center justify-center text-sm shadow-inner',
                  getTrimStatus(flight) === 'Safe' ? 'bg-emerald-50 text-emerald-600' : getTrimStatus(flight) === 'Caution' ? 'bg-amber-50 text-amber-600' : 'bg-rose-50 text-rose-600'
                ]">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 21L3 7h18l-9 14z" />
                  </svg>
                </div>
                <div>
                   <div class="flex items-center gap-1.5">
                     <span class="text-[10px] font-black uppercase tracking-tighter" :class="[
                        getTrimStatus(flight) === 'Safe' ? 'text-emerald-700' : getTrimStatus(flight) === 'Caution' ? 'text-amber-700' : 'text-red-700'
                     ]">{{ getTrimStatus(flight) }} Trim</span>
                   </div>
                   <p class="text-[9px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">Stability OK</p>
                </div>
             </div>

             <div class="flex flex-col items-end">
                <span class="text-[13px] font-black text-slate-900 font-mono tracking-tighter">{{ formatWeight(calculateTotalWeight(flight)) }} KG</span>
                <span class="text-[9px] text-slate-400 font-bold uppercase tracking-widest leading-none mt-1">Gross T.O Weight</span>
             </div>
           </div>
        </div>

        <!-- FOOTER: Terminal Action -->
        <div class="px-8 py-5 bg-white flex justify-between items-center group/footer">
           <div class="flex items-center gap-2">
              <svg class="w-3.5 h-3.5 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">{{ formatDate(flight.departure_time) }}</span>
           </div>
           
           <button
            @click="manageManifest(flight.id)"
            class="bg-pink-600 hover:bg-slate-900 text-white rounded-[2px] px-5 py-2.5 transition-all duration-300 flex items-center gap-2 shadow-lg shadow-pink-100 hover:shadow-slate-300 active:scale-95 group/btn"
          >
            <span class="text-[10px] font-black uppercase tracking-widest">Entry Manifest</span>
            <svg class="w-3.5 h-3.5 transition-transform duration-300 group-hover/btn:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- TERMINAL EMPTY STATE -->
    <div v-else class="bg-white border-4 border-dashed border-slate-100 rounded-[5px] p-24 text-center">
      <div class="relative inline-block mb-10">
         <div class="text-[120px] filter grayscale opacity-10 blur-sm">🛰️</div>
         <div class="absolute inset-0 flex items-center justify-center text-7xl animate-bounce">🛰️</div>
      </div>
      <h3 class="text-3xl font-black text-slate-900 tracking-tighter italic">Terminal Log Null</h3>
      <p class="text-slate-500 mt-3 font-bold uppercase tracking-widest max-w-sm mx-auto leading-relaxed">
        {{ hasFilters 
          ? 'Clear active filters to restore data throughput.' 
          : 'No upcoming flight cycles detected in the current node.' 
        }}
      </p>
      
      <button 
        v-if="hasFilters"
        @click="resetFilters"
        class="mt-10 bg-pink-50 hover:bg-pink-600 text-pink-600 hover:text-white px-10 py-4 rounded-[2px] text-[11px] font-black uppercase tracking-[0.2em] transition-all duration-300 italic"
      >
        Flush Filters
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDcsStore } from '@/stores/dcs'

const router = useRouter()
const dcsStore = useDcsStore()

// Filter State
const searchQuery = ref('')
const showTodayOnly = ref(false)

onMounted(() => {
  dcsStore.fetchFlights()
})

// Recommendations & Derived Data
const activeAirlineFlights = computed(() => {
  if (!dcsStore.activeAirline) return []
  return (dcsStore.flights || []).filter(f => f.airline_name === dcsStore.activeAirline)
})

const todayFlightsCount = computed(() => {
  return activeAirlineFlights.value.filter(f => isToday(f.departure_time)).length
})

const hasFilters = computed(() => {
  return searchQuery.value || showTodayOnly.value
})

const filteredFlights = computed(() => {
  return activeAirlineFlights.value.filter(flight => {
    // 1. Search Query (Number, Origin, Dest)
    const q = searchQuery.value.toLowerCase().trim()
    const matchesSearch = !q || 
      (flight.flight_number || '').toLowerCase().includes(q) ||
      (flight.origin || '').toLowerCase().includes(q) ||
      (flight.destination || '').toLowerCase().includes(q) ||
      (flight.airline_name || '').toLowerCase().includes(q)

    // 2. Today Only
    const matchesToday = !showTodayOnly.value || isToday(flight.departure_time)

    return matchesSearch && matchesToday
  })
})

const resetFilters = () => {
  searchQuery.value = ''
  showTodayOnly.value = false
}

// Helpers
const getStatusClass = (status) => {
  switch (status) {
    case 'Open': return 'bg-emerald-50 text-emerald-700 border-emerald-200'
    case 'On Flight': return 'bg-pink-50 text-pink-700 border-pink-200'
    case 'Closed': return 'bg-rose-50 text-rose-700 border-rose-200'
    case 'Arrived': return 'bg-slate-50 text-slate-700 border-slate-200'
    default: return 'bg-slate-50 text-pink-700 border-pink-100'
  }
}

const getFlightLoad = (flight) => {
  if (!flight.total_seats) return 0
  return Math.round((flight.booked_count / flight.total_seats) * 100)
}

const formatTime = (d) => {
  if (!d) return '--:--'
  return new Date(d).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' })
}
const formatDate = (d) => {
  if (!d) return '---'
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
const isToday = (d) => {
  if (!d) return false
  const date = new Date(d)
  const today = new Date()
  return date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
}

// Weight & Balance Helpers
const calculateTotalWeight = (flight) => {
  const paxWeight = (flight.checked_in_count || 0) * 75
  const bagWeight = flight.total_baggage_weight || 0
  const fuelAndStaff = 3500 // Simulated base weight for fuel/crew/aircraft
  return paxWeight + bagWeight + fuelAndStaff
}

const getTrimStatus = (flight) => {
  const total = calculateTotalWeight(flight)
  const capacity = 20000 // Simulated max lift for this aircraft type
  const ratio = total / capacity
  
  if (ratio < 0.75) return 'Safe'
  if (ratio < 0.90) return 'Caution'
  return 'Limited'
}

const formatWeight = (w) => {
  return new Intl.NumberFormat().format(Math.round(w))
}

const manageManifest = (id) => router.push(`/dcs/manifest/${id}`)
</script>

<style scoped>
/* No extra scoped CSS needed thanks to Tailwind v4 brilliance */
</style>
