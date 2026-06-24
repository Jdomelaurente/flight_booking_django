<template>
  <div class="p-0.5 space-y-2 bg-gray-100 min-h-screen">
    <!-- Loading Overlay -->
    <div v-if="loading" class="fixed inset-0 bg-white/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <div class="flex flex-col items-center">
        <div class="w-12 h-12 border-4 border-[#002D1E] border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-4 text-gray-600 poppins">Decoding Network Analytics...</p>
      </div>
    </div>

    <!-- Formal Print Header (Only visible when printing) -->
    <div class="hidden print:flex items-center justify-between mb-8 border-b-2 border-black pb-4">
      <div class="flex items-center gap-4">
        <div class="w-16 h-16 bg-[#002D1E] flex items-center justify-center text-white font-black text-2xl">FBS</div>
        <div>
          <h1 class="text-2xl font-black uppercase poppins">Aviation Operations Report</h1>
          <p class="text-sm font-bold poppins text-gray-600 uppercase tracking-widest">Flight Management Division</p>
        </div>
      </div>
      <div class="text-right">
        <p class="text-xs font-black poppins uppercase">Network Snapshot:</p>
        <p class="text-xs font-medium poppins">{{ new Date().toLocaleString() }}</p>
      </div>
    </div>

    <!-- Basic Header -->
    <div class="relative overflow-hidden p-3 rounded-[1px] border border-white/20 shadow-2xl bg-gradient-to-br from-[#002D1E] to-[#013d29] mb-2 group no-print">
      <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
      <div class="absolute -right-20 -top-20 w-64 h-64 bg-[#fe3787] rounded-full blur-[100px] opacity-20 group-hover:opacity-30 transition-opacity"></div>
      
      <div class="relative flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/10 mb-4">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span class="text-[9px] font-bold text-white uppercase tracking-widest poppins">Flight Information Center</span>
          </div>
          <h1 class="text-xl font-black text-white poppins tracking-tight mb-2">
            Flight <span class="text-[#fe3787] drop-shadow-sm font-black italic">Dashboard</span>
          </h1>
          <p class="text-gray-300 poppins text-sm max-w-md">See your airlines, routes, and all airplanes in the air right now.</p>
        </div>
        
        <div class="flex items-center gap-4">
          <!-- Generate Report Button -->
          <button 
            @click="printReport"
            class="hidden md:flex items-center gap-2 px-5 py-2.5 bg-white text-[#002D1E] rounded-[1px] font-black uppercase text-[10px] tracking-widest poppins hover:bg-emerald-50 transition-all shadow-xl group/btn"
          >
            <i class="ph ph-printer text-lg group-hover/btn:scale-110 transition-transform"></i>
            Generate Report
          </button>

          <div class="flex items-center gap-3 bg-black/20 backdrop-blur-xl p-3 rounded-[1px] border border-white/10 shadow-inner">
            <div class="w-12 h-12 rounded-[1px] bg-[#fe3787] flex items-center justify-center shadow-lg">
              <i class="ph ph-ticket text-white text-2xl"></i>
            </div>
            <div>
              <p class="text-[10px] uppercase font-bold text-gray-400 tracking-widest poppins mb-1">Open for Booking</p>
              <p class="text-sm font-black text-white poppins leading-none">{{ totals.openForBooking }} Open Flights</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Daily Stats -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2 no-print">
      <div v-for="metric in metrics" :key="metric.label" 
           class="bg-white border border-gray-200 p-2.5 rounded-[1px] group hover:border-[#fe3787]/40 transition-all duration-300 shadow-sm relative overflow-hidden text-[#002D1E]">
        <div class="absolute top-0 right-0 w-8 h-8 bg-gray-50 rounded-bl-full flex items-center justify-center">
           <i :class="metric.icon" class="text-gray-300 text-[10px] group-hover:text-[#fe3787] transition-colors"></i>
        </div>
        <p class="text-[8px] font-black text-gray-400 uppercase tracking-widest mb-1">{{ metric.label }}</p>
        <p class="text-lg font-black poppins leading-none">{{ metric.value }}</p>
      </div>
    </div>


    <!-- Main Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-2">
      <!-- Popular Routes -->
      <div class="lg:col-span-8 bg-white border border-gray-200 p-4 rounded-[1px] relative group h-[380px] flex flex-col flight-routes-section">
        <h2 class="hidden print:block text-2xl font-black uppercase mb-4 text-[#002D1E] poppins border-b-2 border-[#002D1E] pb-2">PAGE 1: ROUTE PERFORMANCE</h2>
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center gap-4 text-[#002D1E]">
             <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-[#fe3787]"></div>
                <h3 class="text-[10px] font-black uppercase tracking-[0.2em] poppins">Busiest Routes</h3>
             </div>
             <div class="flex items-center bg-gray-50 border border-gray-100 p-0.5 rounded-[1px]">
                <button v-for="p in ['weekly', 'monthly', 'yearly']" :key="p" @click="popularPeriod = p"
                  :class="popularPeriod === p ? 'bg-[#fe3787] text-white shadow-lg' : 'text-gray-400 hover:text-gray-600 font-bold'"
                  class="px-2 py-0.5 text-[8px] font-black uppercase poppins rounded-[1px] transition-all">
                  {{ p }}
                </button>
             </div>
          </div>
        </div>
        <div class="flex-grow relative overflow-hidden">
          <canvas ref="mainChartRef"></canvas>
        </div>
      </div>

      <!-- Airline Summary -->
      <div class="lg:col-span-4 bg-white border border-gray-200 p-4 rounded-[1px] flex flex-col h-[380px] relative overflow-hidden text-[#002D1E] flight-market-section">
        <h2 class="hidden print:block text-2xl font-black uppercase mb-4 text-[#002D1E] poppins border-b-2 border-[#002D1E] pb-2">PAGE 2: AIRLINE ANALYTICS</h2>
        <h3 class="text-[10px] font-black uppercase tracking-[0.2em] poppins mb-8">Airlines</h3>
        <div class="flex-grow flex items-center justify-center relative min-h-[160px]">
          <canvas ref="distChartRef"></canvas>
          <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none translate-y-[-5px]">
            <span class="text-3xl font-black poppins">{{ totals.airlines }}</span>
            <span class="text-[8px] font-black text-gray-400 uppercase tracking-widest poppins">Airlines</span>
          </div>
        </div>
        <div class="mt-4 space-y-1 flex-grow overflow-y-auto">
           <div v-for="(count, label) in paginatedCarriers" :key="label" class="flex items-center justify-between text-[9px] font-bold uppercase poppins border-b border-gray-50 pb-1 last:border-0 px-1">
              <span class="text-gray-400 truncate max-w-[120px]">{{ label }}</span>
              <span class="font-black">{{ count }} Flights</span>
           </div>
        </div>
        <!-- Pagination -->
        <div v-if="Object.keys(carrierSummary).length > 0" class="mt-4 pt-3 border-t border-gray-50 flex items-center justify-between no-print">
           <span class="text-[8px] font-black text-gray-400 uppercase tracking-widest">Page {{ carrierPage }} / {{ carrierTotalPages }}</span>
           <div class="flex items-center gap-2">
              <button @click="carrierPage--" :disabled="carrierPage === 1" class="w-6 h-6 flex items-center justify-center border border-gray-100 text-gray-400 hover:text-[#fe3787] disabled:opacity-20 transition-all bg-white"><i class="ph ph-caret-left"></i></button>
              <button @click="carrierPage++" :disabled="carrierPage >= carrierTotalPages" class="w-6 h-6 flex items-center justify-center border border-gray-100 text-gray-400 hover:text-[#fe3787] disabled:opacity-20 transition-all bg-white"><i class="ph ph-caret-right"></i></button>
           </div>
        </div>
      </div>
    </div>

    <!-- Status Section -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-2">
       <!-- Flight Conditions -->
       <div class="lg:col-span-4 bg-white border border-gray-200 p-4 rounded-[1px] h-[340px] flex flex-col relative overflow-hidden text-[#002D1E] flight-status-section">
          <h2 class="hidden print:block text-2xl font-black uppercase mb-4 text-[#002D1E] poppins border-b-2 border-[#002D1E] pb-2">PAGE 3: NETWORK HEALTH</h2>
          <h3 class="text-[10px] font-black uppercase tracking-[0.2em] poppins mb-6">Flight Status</h3>
          <div class="flex-grow relative min-h-[180px]">
             <canvas ref="healthChartRef"></canvas>
          </div>
          <!-- Success Score Removed -->
       </div>

       <!-- Live Plane List -->
       <div class="lg:col-span-8 bg-[#002D1E] border border-[#002D1E] rounded-[1px] h-[340px] flex flex-col shadow-2xl relative fleet-status-section">
          <h2 class="hidden print:block text-2xl font-black uppercase mb-4 text-white poppins border-b-2 border-white pb-2 px-4 pt-4">PAGE 4: REAL-TIME HUB STATUS</h2>
          <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10 pointer-events-none"></div>
          <div class="p-4 border-b border-white/5 flex items-center justify-between bg-black/10 relative z-10">
            <h3 class="text-[10px] font-black uppercase tracking-[0.3em] text-white poppins flex items-center gap-2">
              <i class="ph ph-airplane text-[#fe3787]"></i>
              Live Plane List
            </h3>
            <div class="flex items-center gap-2">
               <span class="w-2 h-2 rounded-full bg-[#fe3787] animate-pulse"></span>
               <span class="text-[8px] font-black uppercase text-gray-400">Live</span>
            </div>
          </div>
          <div class="flex-grow overflow-auto relative z-10">
            <table class="w-full text-left">
              <thead class="bg-black/20 text-gray-500 text-[9px] uppercase font-bold tracking-widest border-b border-white/5 sticky top-0 bg-[#002D1E]">
                <tr>
                  <th class="px-6 py-3">Flight ID</th>
                  <th class="px-6 py-3">Airline</th>
                  <th class="px-6 py-3">Route</th>
                  <th class="px-6 py-3 text-right">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/5">
                <tr v-for="flight in paginatedRadar" :key="flight.id" class="hover:bg-white/[0.04] transition-colors group">
                  <td class="px-6 py-3">
                    <span class="text-[10px] font-black text-[#fe3787]">{{ flight.flight_number }}</span>
                  </td>
                  <td class="px-6 py-3">
                    <span class="text-[10px] font-bold text-gray-200 uppercase tracking-tight">{{ flight.airline }}</span>
                  </td>
                  <td class="px-6 py-3">
                    <div class="flex items-center gap-3 text-[10px] font-black text-emerald-400 uppercase">
                       <span>{{ flight.origin.code }}</span>
                       <i class="ph ph-arrow-right text-[#fe3787] text-[8px]"></i>
                       <span>{{ flight.destination.code }}</span>
                    </div>
                  </td>
                  <td class="px-6 py-3 text-right">
                    <span :class="statusBadgeClass(flight.status)" 
                          class="px-2 py-0.5 rounded-[1px] text-[8px] font-black uppercase poppins border shadow-sm">
                       {{ flight.status }}
                    </span>
                  </td>
                </tr>
                <tr v-if="activeRadar.length === 0">
                   <td colspan="4" class="px-6 py-16 text-center text-gray-500">
                      <p class="text-[9px] font-black uppercase tracking-[0.4em]">No flights in the air right now...</p>
                   </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Pagination Controls -->
          <div class="p-3 bg-black/40 border-t border-white/5 flex items-center justify-between relative z-10 no-print">
             <div class="text-[8px] font-black text-gray-500 uppercase tracking-widest">
                Showing {{ radarStartRange }}-{{ radarEndRange }} of {{ activeRadar.length }} Flights
             </div>
             <div class="flex items-center gap-2">
                <button 
                  @click="radarPage--" 
                  :disabled="radarPage === 1"
                  class="w-6 h-6 flex items-center justify-center bg-white/5 border border-white/10 text-gray-400 hover:text-[#fe3787] disabled:opacity-20 transition-all rounded-[1px]"
                >
                   <i class="ph ph-caret-left"></i>
                </button>
                <div class="text-[9px] font-black text-white bg-white/5 px-3 py-1 border border-white/10">
                   PAGE {{ radarPage }}
                </div>
                <button 
                  @click="radarPage++" 
                  :disabled="radarPage >= radarTotalPages"
                  class="w-6 h-6 flex items-center justify-center bg-white/5 border border-white/10 text-gray-400 hover:text-[#fe3787] disabled:opacity-20 transition-all rounded-[1px]"
                >
                   <i class="ph ph-caret-right"></i>
                </button>
             </div>
          </div>
       </div>
    </div>

    <!-- Busy Hours (Simple Analytics) -->
    <div class="bg-white border border-gray-200 p-4 rounded-[1px] relative overflow-hidden group no-print">
      <div class="absolute inset-0 bg-gradient-to-r from-gray-50/50 to-white pointer-events-none"></div>
      <div class="flex items-center justify-between mb-6 relative">
        <div class="flex items-center gap-3">
          <div class="w-2 h-8 bg-[#fe3787] rounded-[1px]"></div>
          <div>
            <h3 class="text-[10px] font-black uppercase tracking-[0.2em] text-[#002D1E] poppins">Busy Hours</h3>
            <p class="text-[9px] text-gray-400 font-bold poppins">Flights per Hour (24h Guide)</p>
          </div>
        </div>
        <div class="flex items-center gap-6">
           <div class="text-right">
              <p class="text-[8px] font-black text-gray-400 uppercase tracking-widest">Busiest Time</p>
              <p class="text-[10px] font-black text-[#002D1E] poppins">{{ peakHourString }}</p>
           </div>
           <div class="w-px h-8 bg-gray-100"></div>
           <div class="text-right">
              <p class="text-[8px] font-black text-gray-400 uppercase tracking-widest">Status</p>
              <div class="flex items-center gap-1.5">
                 <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                 <span class="text-[10px] font-black text-emerald-600 poppins uppercase">Operating</span>
              </div>
           </div>
        </div>
      </div>
      
      <div class="h-[180px] relative">
        <canvas ref="peakChartRef"></canvas>
        <div v-if="!peakStats.data?.length && !loading" class="absolute inset-0 flex items-center justify-center bg-gray-50/30">
           <p class="text-[9px] font-black text-gray-300 uppercase tracking-[0.3em]">Analyzing Traffic Patterns...</p>
        </div>
      </div>
      
      <div class="mt-4 grid grid-cols-24 gap-px bg-gray-100 border border-gray-100 rounded-[1px] overflow-hidden">
         <div v-for="h in 24" :key="h" 
              class="h-1 transition-colors duration-500"
              :class="getHeatColor(h-1)"
              :title="`Hour ${h-1}:00`"
         ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, nextTick, watch } from 'vue'
import { Chart, registerables } from 'chart.js'
import api from '@/services/admin/api'

Chart.register(...registerables)

const loading = ref(false)

// Data State
const totals = ref({ airlines: 0, routes: 0, flights: 0, scheduledToday: 0, openForBooking: 0 })
const popularRoutes = ref([])
const activeRadar = ref([])
const opStatus = ref({ labels: [], data: [] })
const popularPeriod = ref('weekly')
const peakStats = ref({ labels: [], data: [] })

watch(popularPeriod, () => {
  fetchPopularRoutes()
})

const fetchPopularRoutes = async () => {
  try {
    const res = await api.get(`/dashboard/popular_routes/?period=${popularPeriod.value}`)
    popularRoutes.value = res.data || { labels: [], data: [] }
    initMainChart()
  } catch (err) {
    console.error('Failed to fetch filtered routes:', err)
  }
}

// Pagination State
const radarPage = ref(1)
const radarPageSize = ref(8)
const radarTotalPages = computed(() => Math.ceil(activeRadar.value.length / radarPageSize.value))
const paginatedRadar = computed(() => {
  const start = (radarPage.value - 1) * radarPageSize.value
  const end = start + radarPageSize.value
  return activeRadar.value.slice(start, end)
})
const radarStartRange = computed(() => (radarPage.value - 1) * radarPageSize.value + 1)
const radarEndRange = computed(() => Math.min(radarPage.value * radarPageSize.value, activeRadar.value.length))

// Carrier Pagination State
const carrierPage = ref(1)
const carrierPageSize = ref(4)
const carrierTotalPages = computed(() => Math.ceil(Object.keys(carrierSummary.value).length / carrierPageSize.value))
const paginatedCarriers = computed(() => {
  const entries = Object.entries(carrierSummary.value)
  const start = (carrierPage.value - 1) * carrierPageSize.value
  return Object.fromEntries(entries.slice(start, start + carrierPageSize.value))
})

// Chart Instances
const mainChartRef = ref(null)
const distChartRef = ref(null)
const healthChartRef = ref(null)
const peakChartRef = ref(null)

let mainInstance = null
let distInstance = null
let healthInstance = null
let peakInstance = null

// Computed
const peakHourString = computed(() => {
  if (!peakStats.value.data?.length) return '--:--'
  const maxIdx = peakStats.value.data.indexOf(Math.max(...peakStats.value.data))
  return `${String(maxIdx).padStart(2, '0')}:00 - ${String((maxIdx + 1) % 24).padStart(2, '0')}:00`
})

const getHeatColor = (hour) => {
  const val = peakStats.value.data?.[hour] || 0
  const max = Math.max(...(peakStats.value.data || [1]))
  const intensity = val / (max || 1)
  if (intensity > 0.8) return 'bg-[#fe3787]'
  if (intensity > 0.5) return 'bg-[#fe3787]/60'
  if (intensity > 0.2) return 'bg-[#fe3787]/30'
  return 'bg-gray-100'
}

// Analytics Metrics
const metrics = computed(() => [
  { label: 'Airlines', value: totals.value.airlines, icon: 'ph ph-buildings', percent: 65 },
  { label: 'Total Routes', value: totals.value.routes, icon: 'ph ph-git-fork', percent: 85 },
  { label: 'Airplanes', value: totals.value.flights, icon: 'ph ph-airplane', percent: 45 },
  { label: 'Flights Today', value: totals.value.scheduledToday, icon: 'ph ph-calendar-check', percent: 92 },
  { label: 'Planes In-Air', value: activeRadar.value.length, icon: 'ph ph-airplane-in-flight', percent: 30 },
])

const activeRadarCount = computed(() => activeRadar.value.length)
const carrierSummary = computed(() => {
  const map = {}
  activeRadar.value.forEach(f => { map[f.airline] = (map[f.airline] || 0) + 1 })
  const entries = Object.entries(map).sort((a,b) => b[1] - a[1])
  return Object.fromEntries(entries)
})

const fetchData = async () => {
  loading.value = true
  try {
    const [airlines, routes, flights, stats, radar, pop, ops, peak] = await Promise.all([
      api.get('/airlines/'),
      api.get('/routes/'),
      api.get('/flights/'),
      api.get('/dashboard/stats/'),
      api.get('/dashboard/active_flights_map/'),
      api.get(`/dashboard/popular_routes/?period=${popularPeriod.value}`),
      api.get('/dashboard/flight_operations_stats/'),
      api.get('/dashboard/network_peak_hours/')
    ])

    totals.value = {
      airlines: airlines.data.count || airlines.data.length || 0,
      routes: routes.data.count || routes.data.length || 0,
      flights: flights.data.count || flights.data.length || 0,
      scheduledToday: stats.data.scheduledFlights || 0,
      openForBooking: stats.data.openForBooking || 0
    }

    activeRadar.value = radar.data || []
    popularRoutes.value = pop.data || { labels: [], data: [] }
    opStatus.value = ops.data || { labels: [], data: [] }
    peakStats.value = peak.data || { labels: [], data: [] }

    await nextTick()
    renderAnalytics()
  } catch (err) {
    console.error('Analytics Fetch Interrupted:', err)
  } finally {
    loading.value = false
  }
}

const renderAnalytics = () => {
  initMainChart()
  initDistChart()
  initHealthChart()
  initPeakChart()
}

const initPeakChart = () => {
  if (!peakChartRef.value) return
  if (peakInstance) peakInstance.destroy()
  const ctx = peakChartRef.value.getContext('2d')
  
  const gradient = ctx.createLinearGradient(0, 0, 0, 180)
  gradient.addColorStop(0, 'rgba(254, 55, 135, 0.2)')
  gradient.addColorStop(1, 'rgba(254, 55, 135, 0)')

  peakInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: peakStats.value.labels || [],
      datasets: [{
        label: 'Traffic',
        data: peakStats.value.data || [],
        borderColor: '#fe3787',
        borderWidth: 2,
        backgroundColor: gradient,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointBackgroundColor: '#fe3787'
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      interaction: {
        intersect: false,
        mode: 'index',
      },
      scales: {
        y: { 
          beginAtZero: true, 
          grid: { color: 'rgba(0,0,0,0.03)' }, 
          ticks: { display: false } 
        },
        x: { 
          grid: { display: false }, 
          ticks: { 
            font: { size: 7, family: 'Poppins' }, 
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 12
          } 
        }
      }
    }
  })
}

const initMainChart = () => {
  if (!mainChartRef.value) return
  if (mainInstance) mainInstance.destroy()
  const ctx = mainChartRef.value.getContext('2d')
  const gradient = ctx.createLinearGradient(0, 0, 0, 400)
  gradient.addColorStop(0, 'rgba(254, 55, 135, 0.15)')
  gradient.addColorStop(1, 'rgba(254, 55, 135, 0)')

  mainInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: popularRoutes.value.labels || [],
      datasets: [{
        label: 'Route Load',
        data: popularRoutes.value.data || [],
        borderColor: '#fe3787',
        borderWidth: 3,
        backgroundColor: gradient,
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#fe3787',
        pointBorderColor: '#fff',
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: '#f3f4f6' }, ticks: { font: { size: 9, family: 'Poppins' } } },
        x: { grid: { display: false }, ticks: { font: { size: 9, family: 'Poppins' } } }
      }
    }
  })
}

const initDistChart = () => {
  if (!distChartRef.value) return
  if (distInstance) distInstance.destroy()
  const labels = Object.keys(carrierSummary.value)
  const data = Object.values(carrierSummary.value)
  distInstance = new Chart(distChartRef.value, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data.length ? data : [1],
        backgroundColor: ['#002D1E', '#fe3787', '#2563eb', '#10b981', '#f59e0b'],
        borderWidth: 4,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: '82%',
      plugins: { legend: { display: false } }
    }
  })
}

const initHealthChart = () => {
  if (!healthChartRef.value) return
  if (healthInstance) healthInstance.destroy()
  healthInstance = new Chart(healthChartRef.value, {
    type: 'radar',
    data: {
      labels: opStatus.value.labels || ['Ground', 'Air', 'Delay', 'Cancel'],
      datasets: [{
        label: 'System Load',
        data: opStatus.value.data && opStatus.value.data.length ? opStatus.value.data : [10, 10, 10, 10],
        borderColor: '#fe3787',
        backgroundColor: 'rgba(254, 55, 135, 0.1)',
        borderWidth: 1.5,
        pointBackgroundColor: '#fe3787',
        pointRadius: 2
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        r: {
          angleLines: { color: '#f3f4f6' },
          grid: { color: '#f3f4f6' },
          pointLabels: { color: '#4B5563', font: { size: 8, family: 'Poppins', weight: 'black' } },
          ticks: { display: false }
        }
      }
    }
  })
}

const statusBadgeClass = (status) => {
  const map = {
    'On Flight': 'bg-emerald-50 text-emerald-700 border-emerald-100',
    'Boarding': 'bg-blue-50 text-blue-700 border-blue-100',
    'Delayed': 'bg-rose-50 text-[#fe3787] border-rose-100',
    'Cancelled': 'bg-gray-100 text-gray-500 border-gray-200',
    'Landed': 'bg-indigo-50 text-indigo-700 border-indigo-100'
  }
  return map[status] || 'bg-gray-50 text-gray-600 border-gray-100'
}

const printReport = () => {
  window.print()
}

onMounted(fetchData)
onUnmounted(() => {
  [mainInstance, distInstance, healthInstance, peakInstance].forEach(c => c?.destroy())
})
</script>

<style scoped>
.poppins { font-family: 'Poppins', sans-serif; }
@keyframes spin { to { transform: rotate(360deg); } }
.animate-spin { animation: spin 1s linear infinite; }

@media print {
  .no-print, button, .ph, header, nav, aside {
    display: none !important;
  }
  
  .grid { display: block !important; }
  .lg\:col-span-8, .lg\:col-span-4, .lg\:col-span-12 { width: 100% !important; margin-bottom: 0 !important; }

  .flight-routes-section,
  .flight-market-section,
  .flight-status-section,
  .fleet-status-section {
    page-break-before: always !important;
    break-before: page !important;
    height: auto !important;
    min-height: auto !important;
    margin-bottom: 0 !important;
    padding-top: 20px !important;
  }

  .flight-routes-section {
    page-break-before: avoid !important;
    break-before: avoid !important;
  }

  .flight-market-section,
  .flight-status-section {
    background: white !important;
    color: black !important;
    border: 1px solid #eee !important;
  }

  .flight-market-section h3, .flight-market-section p, .flight-market-section span,
  .flight-status-section h3, .flight-status-section p, .flight-status-section span {
    color: #002D1E !important;
  }

  canvas {
    max-width: 100% !important;
    height: 400px !important;
  }
}
</style>
