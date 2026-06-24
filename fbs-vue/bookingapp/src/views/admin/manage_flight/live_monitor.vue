<template>
  <div class="h-[calc(100vh-100px)] flex flex-col bg-gray-100 poppins">
    <!-- Header / Toolbar -->
    <div class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm z-10">
      <div>
        <h1 class="text-xl font-black text-[#002D1E] tracking-tight flex items-center gap-3">
          <i class="ph ph-broadcast text-[#fe3787] text-2xl animate-pulse"></i>
          Live Simulation Command Center
        </h1>
        <p class="text-[10px] text-gray-400 uppercase font-black tracking-widest mt-1">Real-time aircraft tracking & airport network visualization</p>
      </div>

      <div class="flex items-center gap-6">
        <!-- Live Status Indicators -->
        <div class="hidden md:flex items-center gap-4 border-r border-gray-100 pr-6 mr-2">
          <div class="text-right">
            <p class="text-[9px] text-gray-400 uppercase font-bold leading-none">Status</p>
            <p class="text-xs font-black text-emerald-500">SYSTEM ONLINE</p>
          </div>
          <div class="w-10 h-10 rounded-full bg-emerald-50 border border-emerald-100 flex items-center justify-center">
            <div class="w-3 h-3 bg-emerald-500 rounded-full animate-ping"></div>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <div class="bg-gray-50 border border-gray-200 rounded-[1px] px-4 py-2 flex items-center gap-3">
            <span class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Planes In-Air:</span>
            <span class="text-sm font-black text-[#fe3787]">{{ activeFlights.length }}</span>
          </div>
          <div class="bg-gray-50 border border-gray-200 rounded-[1px] px-4 py-2 flex items-center gap-3">
            <span class="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Airports:</span>
            <span class="text-sm font-black text-[#002D1E]">{{ airports.length }}</span>
          </div>

          <button 
            @click="refreshData" 
            :disabled="refreshing"
            class="h-full px-4 py-2 bg-slate-900 text-white rounded-[1px] text-[10px] font-bold uppercase tracking-widest hover:bg-slate-800 disabled:opacity-50 transition-all flex items-center gap-2"
          >
            <i class="ph ph-arrows-counter-clockwise" :class="{ 'animate-spin': refreshing }"></i>
            {{ refreshing ? 'Refreshing...' : 'Refresh' }}
          </button>

          <button 
            @click="toggleFullScreen" 
            class="p-2.5 bg-[#002D1E] text-white rounded-[1px] hover:bg-black transition-all shadow-lg flex items-center gap-2"
          >
            <i class="ph ph-corners-out text-lg"></i>
            <span class="text-[10px] font-black uppercase tracking-widest hidden sm:inline">Fullscreen Radar</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content: Map + Sidebar -->
    <div class="flex-1 flex overflow-hidden relative">
      <!-- Sidebar -->
      <div v-if="showSidebar" class="w-80 bg-white border-r border-gray-200 overflow-y-auto hidden xl:block shadow-xl z-20">
        <div class="p-4 space-y-5">
          
          <!-- Sidebar Tabs -->
          <div class="flex border-b border-gray-100">
            <button @click="sidebarTab = 'flights'"
              :class="sidebarTab === 'flights' ? 'border-b-2 border-[#fe3787] text-[#fe3787]' : 'text-gray-400'"
              class="flex-1 py-2.5 text-[10px] font-black uppercase tracking-widest transition-colors">
              <i class="ph ph-airplane-tilt mr-1"></i> Flights
            </button>
            <button @click="sidebarTab = 'airports'"
              :class="sidebarTab === 'airports' ? 'border-b-2 border-[#002D1E] text-[#002D1E]' : 'text-gray-400'"
              class="flex-1 py-2.5 text-[10px] font-black uppercase tracking-widest transition-colors">
              <i class="ph ph-buildings mr-1"></i> Airports
            </button>
          </div>

          <!-- ===== FLIGHTS TAB ===== -->
          <div v-if="sidebarTab === 'flights'">
            <div v-if="activeFlights.length === 0" class="py-12 text-center">
               <i class="ph ph-airplane-slash text-4xl text-gray-100 mb-4"></i>
               <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">No Active Simulations</p>
            </div>
            
            <div v-for="flight in activeFlights" :key="flight.id" 
                 @click="centerOnFlight(flight)"
                 class="p-4 border border-gray-100 rounded-[1px] hover:border-[#fe3787] hover:shadow-md transition-all cursor-pointer group bg-gray-50/50 mb-3">
              <div class="flex justify-between items-start mb-3">
                <div>
                  <p class="text-xs font-black text-[#002D1E] group-hover:text-[#fe3787] transition-colors">{{ flight.flight_number }}</p>
                  <p class="text-[9px] text-gray-400 font-bold uppercase">{{ flight.airline }}</p>
                </div>
                <span class="px-2 py-0.5 rounded-[1px] text-[8px] font-black uppercase bg-emerald-100 text-emerald-700">IN-FLIGHT</span>
              </div>
              <div class="flex items-center justify-between text-[10px] font-bold poppins">
                <span class="text-gray-700 font-black">{{ flight.origin.code }}</span>
                <div class="flex-1 mx-2 h-[1px] bg-gray-200 relative">
                  <i class="ph ph-airplane-tilt absolute -top-1.5 left-1/2 -translate-x-1/2 text-[10px] text-[#fe3787]"></i>
                </div>
                <span class="text-gray-700 font-black">{{ flight.destination.code }}</span>
              </div>
              <div class="mt-3 w-full h-1 bg-gray-100 rounded-full overflow-hidden">
                 <div class="h-full bg-[#fe3787] transition-all duration-1000" :style="{ width: Math.round(getFlightProgress(flight) * 100) + '%' }"></div>
              </div>
              <p class="text-[8px] text-gray-400 font-bold uppercase mt-1 text-right">{{ Math.round(getFlightProgress(flight) * 100) }}% complete</p>

              <!-- Stopover Timeline -->
              <div v-if="flight.layovers && flight.layovers.length > 0" class="mt-5 pt-4 border-t border-gray-100">
                <p class="text-[8px] font-black text-gray-400 uppercase tracking-widest mb-3">Operational Timeline</p>
                <div class="ml-1 border-l border-dashed border-gray-200 pl-3 space-y-4">
                  <div class="relative">
                    <div class="absolute -left-[16.5px] top-1 w-2 h-2 rounded-full bg-slate-200 border border-white"></div>
                    <p class="text-[9px] font-black text-gray-500 uppercase leading-none">{{ flight.origin.code }}</p>
                    <p class="text-[7px] text-gray-400 font-bold uppercase mt-1">{{ flight.origin.city }} – Origin</p>
                  </div>
                  <div v-for="(stop, idx) in flight.layovers" :key="idx" class="relative">
                    <div class="absolute -left-[16.5px] top-1 w-2 h-2 rounded-full bg-[#fe3787] shadow-[0_0_8px_rgba(254,55,135,0.4)] border border-white"></div>
                    <p class="text-[9px] font-black text-[#fe3787] uppercase leading-none">{{ stop.airport }}</p>
                    <p class="text-[7px] text-gray-400 font-bold uppercase mt-1">Stopover · {{ stop.duration }}</p>
                  </div>
                  <div class="relative">
                    <div class="absolute -left-[16.5px] top-1 w-2 h-2 rounded-full bg-slate-200 border border-white"></div>
                    <p class="text-[9px] font-black text-gray-500 uppercase leading-none">{{ flight.destination.code }}</p>
                    <p class="text-[7px] text-gray-400 font-bold uppercase mt-1">{{ flight.destination.city }} – Final</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ===== AIRPORTS TAB ===== -->
          <div v-if="sidebarTab === 'airports'">
            <!-- Search -->
            <div class="mb-3">
              <input v-model="airportSearch" type="text" placeholder="Search airport..." 
                class="w-full text-[11px] border border-gray-200 px-3 py-2 rounded-[1px] focus:outline-none focus:border-[#002D1E] font-bold text-[#002D1E] bg-gray-50" />
            </div>
            <!-- Filter tabs -->
            <div class="flex gap-2 mb-3">
              <button v-for="t in ['all', 'international', 'domestic']" :key="t"
                @click="airportTypeFilter = t"
                :class="airportTypeFilter === t ? 'bg-[#002D1E] text-white' : 'bg-gray-100 text-gray-500'"
                class="flex-1 py-1 text-[8px] font-black uppercase tracking-widest rounded-[1px] transition-colors">
                {{ t }}
              </button>
            </div>

            <p class="text-[8px] text-gray-400 font-bold uppercase tracking-widest mb-2">{{ filteredAirports.length }} airports shown</p>

            <div v-if="filteredAirports.length === 0" class="py-8 text-center">
              <i class="ph ph-buildings text-3xl text-gray-100 mb-3"></i>
              <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">No airports found</p>
            </div>

            <div v-for="ap in filteredAirports" :key="ap.code"
                 @click="flyToAirport(ap)"
                 class="flex items-center gap-3 p-3 border border-gray-100 rounded-[1px] hover:border-[#002D1E] hover:shadow-sm cursor-pointer transition-all group mb-2 bg-gray-50/50">
              <!-- Badge -->
              <div class="w-9 h-9 shrink-0 rounded-[1px] flex items-center justify-center font-black text-[9px] tracking-widest"
                   :class="ap.type === 'international' ? 'bg-blue-50 text-blue-700 border border-blue-100' : 'bg-emerald-50 text-emerald-700 border border-emerald-100'">
                {{ ap.code }}
              </div>
              <div class="min-w-0">
                <p class="text-[10px] font-black text-[#002D1E] group-hover:text-[#fe3787] transition-colors truncate">{{ ap.name }}</p>
                <p class="text-[8px] text-gray-400 font-bold uppercase truncate">{{ ap.city }}<span v-if="ap.country"> · {{ ap.country }}</span></p>
                <span class="inline-block mt-1 px-1.5 py-0.5 rounded-[1px] text-[7px] font-black uppercase"
                      :class="ap.type === 'international' ? 'bg-blue-50 text-blue-600' : 'bg-emerald-50 text-emerald-600'">
                  {{ ap.type }}
                </span>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- Map Container -->
      <div class="flex-1 relative group" ref="mapCardRef">
        <div ref="mapContainer" class="absolute inset-0 z-0"></div>
        
        <!-- Toggle Manifest Button -->
        <button @click="showSidebar = !showSidebar" 
                class="absolute left-4 top-4 z-[400] bg-white border border-gray-200 p-2 rounded-[1px] shadow-lg hover:bg-gray-50 transition-all text-[#002D1E]">
          <i class="ph" :class="showSidebar ? 'ph-caret-double-left' : 'ph-caret-double-right'"></i>
        </button>

        <!-- Map Legend -->
        <div class="absolute bottom-6 left-6 z-[400] bg-white/90 backdrop-blur-md border border-gray-200 p-4 rounded-[1px] shadow-2xl space-y-3 min-w-[210px]">
          <h4 class="text-[10px] font-black text-[#002D1E] uppercase tracking-widest border-b border-gray-100 pb-2">Radar Legend</h4>
          <div class="flex items-center gap-3">
            <span class="w-3 h-3 rounded-full bg-[#fe3787]"></span>
            <span class="text-[10px] font-bold text-gray-600 uppercase">Active Aircraft</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="w-3 h-[2px] bg-[#fe3787] border-dashed border-t border-b"></span>
            <span class="text-[10px] font-bold text-gray-600 uppercase">Flight Path</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="w-3 h-3 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.4)]"></span>
            <span class="text-[10px] font-bold text-gray-600 uppercase">International Airport</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]"></span>
            <span class="text-[10px] font-bold text-gray-600 uppercase">Domestic Airport</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import api from '@/services/admin/api'

// Leaflet fix for icons
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
})

// State
const mapContainer = ref(null)
const mapCardRef = ref(null)
const mapLoading = ref(false)
const showSidebar = ref(true)
const activeFlights = ref([])
const airports = ref([])
const syncing = ref(false)
const sidebarTab = ref('flights')
const airportSearch = ref('')
const airportTypeFilter = ref('all')
const isMapFullScreen = ref(false)

// Map instances
let mapInstance = null
let flightMarkers = []
let flightPolylines = []
let airportMarkers = []
let animationInterval = null
let mapRefreshInterval = null

const filteredAirports = computed(() => {
  let list = airports.value
  if (airportTypeFilter.value !== 'all') {
    list = list.filter(ap => ap.type === airportTypeFilter.value)
  }
  if (airportSearch.value.trim()) {
    const q = airportSearch.value.toLowerCase()
    list = list.filter(ap =>
      ap.code.toLowerCase().includes(q) ||
      ap.name.toLowerCase().includes(q) ||
      (ap.city || '').toLowerCase().includes(q)
    )
  }
  return list
})

const syncRadar = async () => {
  if (syncing.value) return
  syncing.value = true
  try {
    await api.post('/dashboard/sync_active_flights/')
    await fetchActiveFlights()
  } catch (err) {
    console.error('Failed to sync radar:', err)
  } finally {
    syncing.value = false
  }
}

const refreshAll = async () => {
  mapLoading.value = true
  await Promise.all([fetchActiveFlights(), fetchAirports()])
  mapLoading.value = false
}

// Fetch all airports for map
const fetchAirports = async () => {
  try {
    const res = await api.get('/dashboard/airports_map/')
    airports.value = res.data || []
    if (mapInstance) renderAirportMarkers()
  } catch (err) {
    console.error('Airport fetch error:', err)
  }
}

// Fetch active flights
const fetchActiveFlights = async () => {
  try {
    const res = await api.get('/dashboard/active_flights_map/')
    activeFlights.value = res.data || []
    if (mapInstance) {
      updateMapMarkers()
    } else {
      await nextTick()
      initMap()
    }
    startFlightAnimation()
  } catch (err) {
    console.error('Map data fetch error:', err)
  }
}

const initMap = () => {
  if (!mapContainer.value || mapInstance) return

  mapInstance = L.map(mapContainer.value, {
    center: [12.8797, 121.7740],
    zoom: 6,
    zoomControl: false,
    attributionControl: false
  })

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19
  }).addTo(mapInstance)

  L.control.zoom({ position: 'topright' }).addTo(mapInstance)

  renderAirportMarkers()
  updateMapMarkers()
}

const renderAirportMarkers = () => {
  if (!mapInstance) return

  // Clear old airport markers
  airportMarkers.forEach(m => m.remove())
  airportMarkers = []

  airports.value.forEach(ap => {
    const isIntl = ap.type === 'international'
    const color = isIntl ? '#3b82f6' : '#10b981'
    const shadow = isIntl ? 'rgba(59,130,246,0.35)' : 'rgba(16,185,129,0.35)'

    const apIcon = L.divIcon({
      html: `<div style="
        width: 10px; height: 10px;
        background: ${color};
        border: 2px solid white;
        border-radius: 50%;
        box-shadow: 0 0 8px ${shadow};
      "></div>`,
      className: 'airport-dot-icon',
      iconSize: [10, 10],
      iconAnchor: [5, 5]
    })

    const marker = L.marker([ap.lat, ap.lng], { icon: apIcon })
      .addTo(mapInstance)
      .bindTooltip(
        `<div class="poppins" style="min-width:130px">
          <span style="font-size:11px; font-weight:900; color:#002D1E; display:block">${ap.code} – ${ap.name}</span>
          <span style="font-size:9px; color:#888; font-weight:700; text-transform:uppercase">${ap.city}${ap.country ? ' · ' + ap.country : ''}</span><br>
          <span style="font-size:8px; font-weight:900; text-transform:uppercase; color:${color}">${ap.type}</span>
        </div>`,
        { direction: 'top', className: 'airport-tooltip', offset: [0, -4] }
      )
      .on('click', () => flyToAirport(ap))

    airportMarkers.push(marker)
  })
}

const flyToAirport = (ap) => {
  if (!mapInstance) return
  mapInstance.flyTo([ap.lat, ap.lng], 10, { duration: 1.2 })
  // open the tooltip of the airport marker
  const marker = airportMarkers.find(m => {
    const ll = m.getLatLng()
    return Math.abs(ll.lat - ap.lat) < 0.0001 && Math.abs(ll.lng - ap.lng) < 0.0001
  })
  if (marker) marker.openTooltip()
}

const updateMapMarkers = () => {
  if (!mapInstance) return

  // Clear existing flight markers/polylines
  flightMarkers.forEach(m => m.remove())
  flightPolylines.forEach(p => p.remove())
  flightMarkers = []
  flightPolylines = []

  activeFlights.value.forEach(flight => {
    const points = [[flight.origin.lat, flight.origin.lng]]
    if (flight.layovers && flight.layovers.length > 0) {
      flight.layovers.forEach(l => {
        if (l.lat && l.lng) points.push([l.lat, l.lng])
      })
    }
    points.push([flight.destination.lat, flight.destination.lng])

    // Flight path polyline
    const polyline = L.polyline(points, {
      color: '#fe3787',
      weight: 2,
      dashArray: '5, 8',
      opacity: 0.4
    }).addTo(mapInstance)
    flightPolylines.push(polyline)

    // Layover hub markers
    if (flight.layovers && flight.layovers.length > 0) {
      flight.layovers.forEach(stop => {
        if (stop.lat && stop.lng) {
          const hubMarker = L.circleMarker([stop.lat, stop.lng], {
            radius: 4,
            fillColor: '#fe3787',
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 1
          }).addTo(mapInstance)
            .bindTooltip(`<span class="poppins" style="font-size:9px;font-weight:900;text-transform:uppercase;color:#002D1E">${stop.airport} HUB</span>`, {
              permanent: false,
              direction: 'top',
              className: 'hub-tooltip'
            })
          flightMarkers.push(hubMarker)
        }
      })
    }

    // Aircraft position
    const t = getFlightProgress(flight)
    const numSegments = points.length - 1
    let segmentIndex = Math.min(Math.floor(t * numSegments), numSegments - 1)
    if (segmentIndex < 0) segmentIndex = 0

    const p1 = points[segmentIndex]
    const p2 = points[segmentIndex + 1]
    const segmentT = (t * numSegments) - segmentIndex

    const aircraftPos = [
      p1[0] + (p2[0] - p1[0]) * segmentT,
      p1[1] + (p2[1] - p1[1]) * segmentT
    ]

    const bearing = calculateBearing(p1[0], p1[1], p2[0], p2[1])
    const progressPct = Math.round(t * 100)
    
    const planeIcon = L.divIcon({
      html: `<div class="relative aircraft-icon-wrapper" style="transform: rotate(${bearing - 45}deg)">
               <i class="ph ph-airplane-tilt text-[#fe3787] text-3xl drop-shadow-2xl"></i>
               <div class="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full border-2 border-white bg-emerald-500 animate-pulse"></div>
             </div>`,
      className: 'custom-plane-icon',
      iconSize: [32, 32],
      iconAnchor: [16, 16]
    })

    const depStr = new Date(flight.departure_time).toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' })
    const arrStr = new Date(flight.arrival_time).toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' })

    const marker = L.marker(aircraftPos, { icon: planeIcon })
      .addTo(mapInstance)
      .bindPopup(`
        <div class="poppins p-2 min-w-[200px]">
          <div class="flex justify-between items-center mb-2">
            <span style="font-weight:900;color:#002D1E;font-size:13px">${flight.flight_number}</span>
            <span style="font-size:8px;font-weight:900;color:#fe3787;text-transform:uppercase">${progressPct}% COMPLETE</span>
          </div>
          <p style="font-size:9px;color:#aaa;text-transform:uppercase;font-weight:700;margin-bottom:8px">
            ${flight.airline}
            ${flight.layovers && flight.layovers.length > 0 ? `<span style="color:#fe3787"> VIA ${flight.layovers.map(l => l.airport).join(', ')}</span>` : ''}
          </p>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;border-top:1px solid #f3f4f6;padding-top:10px">
             <div>
                <p style="font-size:7px;color:#aaa;text-transform:uppercase;font-weight:700">Departure</p>
                <p style="font-size:11px;font-weight:900;color:#002D1E">${flight.origin.code}</p>
                <p style="font-size:8px;color:#666;font-weight:700">${flight.origin.city || ''}</p>
                <p style="font-size:8px;color:#999;font-weight:700">${depStr}</p>
             </div>
             <div style="text-align:right">
                <p style="font-size:7px;color:#aaa;text-transform:uppercase;font-weight:700">Arrival</p>
                <p style="font-size:11px;font-weight:900;color:#002D1E">${flight.destination.code}</p>
                <p style="font-size:8px;color:#666;font-weight:700">${flight.destination.city || ''}</p>
                <p style="font-size:8px;color:#999;font-weight:700">${arrStr}</p>
             </div>
          </div>
          <div style="margin-top:10px">
             <div style="width:100%;height:4px;background:#f3f4f6;border-radius:99px;overflow:hidden">
                <div style="width:${progressPct}%;height:100%;background:#fe3787"></div>
             </div>
          </div>
        </div>
      `, {
        className: 'custom-radar-popup',
        closeButton: false
      })
    
    marker.customFlightInfo = flight
    flightMarkers.push(marker)
  })

  // Fit bounds if we have flights on first load
  if (flightMarkers.length > 0 && !animationInterval) {
    try {
      const group = new L.featureGroup(flightPolylines)
      mapInstance.fitBounds(group.getBounds().pad(0.2))
    } catch {}
  }
}

const getFlightProgress = (flight) => {
  const now = Date.now()
  const dep = new Date(flight.departure_time).getTime()
  const arr = new Date(flight.arrival_time).getTime()
  if (now <= dep) return 0
  if (now >= arr) return 1
  return (now - dep) / (arr - dep)
}

const calculateBearing = (startLat, startLng, endLat, endLng) => {
  const startLatRad = startLat * Math.PI / 180
  const startLngRad = startLng * Math.PI / 180
  const endLatRad = endLat * Math.PI / 180
  const endLngRad = endLng * Math.PI / 180
  const y = Math.sin(endLngRad - startLngRad) * Math.cos(endLatRad)
  const x = Math.cos(startLatRad) * Math.sin(endLatRad) -
    Math.sin(startLatRad) * Math.cos(endLatRad) * Math.cos(endLngRad - startLngRad)
  return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360
}

const centerOnFlight = (flight) => {
  const t = getFlightProgress(flight)
  const origin = [flight.origin.lat, flight.origin.lng]
  const dest = [flight.destination.lat, flight.destination.lng]
  const pos = [
    origin[0] + (dest[0] - origin[0]) * t,
    origin[1] + (dest[1] - origin[1]) * t
  ]
  mapInstance.flyTo(pos, 8, { duration: 1.5 })
  const marker = flightMarkers.find(m => m.customFlightInfo?.id === flight.id)
  if (marker) marker.openPopup()
}

const startFlightAnimation = () => {
  if (animationInterval) clearInterval(animationInterval)
  if (mapRefreshInterval) clearInterval(mapRefreshInterval)
  animationInterval = setInterval(updateMapMarkers, 30000)
  mapRefreshInterval = setInterval(fetchActiveFlights, 20000)
}

const toggleFullScreen = () => {
  if (mapCardRef.value.requestFullscreen) {
    mapCardRef.value.requestFullscreen()
  }
}

const handleFullScreenChange = () => {
  isMapFullScreen.value = !!document.fullscreenElement
  if (mapInstance) {
    setTimeout(() => mapInstance.invalidateSize(), 100)
  }
}

onMounted(async () => {
  await nextTick()
  await Promise.all([fetchActiveFlights(), fetchAirports()])
  document.addEventListener('fullscreenchange', handleFullScreenChange)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullScreenChange)
  if (animationInterval) clearInterval(animationInterval)
  if (mapRefreshInterval) clearInterval(mapRefreshInterval)
  if (mapInstance) mapInstance.remove()
})
</script>

<style>
.poppins {
  font-family: 'Poppins', sans-serif;
}

.custom-radar-popup .leaflet-popup-content-wrapper {
  background: white !important;
  color: #002D1E !important;
  border-radius: 1px !important;
  padding: 0 !important;
  border: 1px solid #eee;
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1);
}

.custom-radar-popup .leaflet-popup-content {
  margin: 0 !important;
}

.custom-radar-popup .leaflet-popup-tip {
  background: white !important;
}

.hub-tooltip {
  background: white !important;
  border: 1px solid #fe3787 !important;
  border-radius: 1px !important;
  padding: 2px 6px !important;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1) !important;
}

.hub-tooltip:before {
  border-top-color: #fe3787 !important;
}

.airport-tooltip .leaflet-tooltip-content {
  padding: 6px 8px !important;
}

.airport-tooltip {
  background: white !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 1px !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
  padding: 4px 8px !important;
}

.airport-dot-icon {
  background: none !important;
  border: none !important;
}

.leaflet-control-attribution {
  display: none !important;
}

.aircraft-icon-wrapper {
  transition: all 0.3s ease;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #eee; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #fe3787; }
</style>
