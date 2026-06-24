<template>
  <div class="p-6 poppins">
    <!-- Header & Tools Section -->
    <AdminTableTool 
      v-model="searchQuery" 
      placeholder="Search by origin or destination..."
    >
      <template #filters>
        <div class="flex items-center gap-2 text-[14px]">
          <select 
            v-model="selectedAirportFilter" 
            class="text-[11px] font-bold border border-gray-200 px-3 py-2 bg-white rounded-[1px] outline-none focus:border-[#fe3787] poppins cursor-pointer min-w-[150px]"
          >
            <option value="">All Airports</option>
            <option v-for="airport in airports" :key="airport.id" :value="airport.id">
              {{ airport.code }} - {{ airport.name }}
            </option>
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
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">Total Routes</p>
            <p class="text-2xl font-bold text-[#002D1E] poppins">{{ stats.totalRoutes }}</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
            <i class="ph ph-map-trifold text-xl text-green-600"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">Active Origins</p>
            <p class="text-2xl font-bold text-[#002D1E] poppins">{{ stats.activeOrigins }}</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
            <i class="ph ph-map-pin text-xl text-blue-600"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins">Connected Hubs</p>
            <p class="text-2xl font-bold text-[#002D1E] poppins">{{ stats.connectedHubs }}</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
            <i class="ph ph-corners-out text-xl text-purple-600"></i>
          </div>
        </div>
      </div>
    </div>



    <!-- Table Section -->
    <div class="bg-white border border-gray-200 shadow-sm overflow-hidden rounded-[1px]">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Route ID</th>
            <th class="px-6 py-4 poppins">Origin Airport</th>
            <th class="px-6 py-4 poppins">Destination Airport</th>
            <th class="px-6 py-4 poppins">Base Price</th>
            <th class="px-6 py-4 text-right poppins">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr 
            v-for="route in paginatedRoutes" 
            :key="route.id" 
            :id="`route-row-${route.id}`"
            :class="{'highlight-active': highlightedId === route.id}"
            class="hover:bg-gray-50/50 transition-all text-[12px] font-medium"
          >
            <td class="px-6 py-4">
              <div class="flex items-center gap-2">
                <span class="font-bold text-gray-400 block poppins">#{{ route.id }}</span>
                <div class="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" title="Connected Data"></div>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-3 group">
                <div class="w-8 h-8 rounded-full bg-[#fe3787] flex items-center justify-center group-hover:scale-110 transition-transform">
                  <i class="ph ph-airplane-takeoff text-white text-md"></i>
                </div>
                <div>
                  <router-link 
                    :to="{ name: 'AdminAirports', query: { highlight: route.origin_airport } }"
                    class="font-bold text-[#002D1E] block poppins hover:text-[#fe3787] transition-all"
                    title="View Airport Connection"
                  >
                    {{ route.origin_info || route.origin_airport_name || route.origin_airport }}
                  </router-link>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-3 group">
                <div class="w-8 h-8 rounded-full bg-[#002D1E] flex items-center justify-center group-hover:scale-110 transition-transform">
                  <i class="ph ph-airplane-landing text-white text-md"></i>
                </div>
                <div>
                  <router-link 
                    :to="{ name: 'AdminAirports', query: { highlight: route.destination_airport } }"
                    class="font-bold text-[#002D1E] block poppins hover:text-[#fe3787] transition-all"
                    title="View Airport Connection"
                  >
                    {{ route.destination_info || route.destination_airport_name || route.destination_airport }}
                  </router-link>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <span class="text-sm font-bold poppins text-[#fe3787]">
                ₱{{ parseFloat(route.base_price || 0).toLocaleString(undefined, { minimumFractionDigits: 2 }) }}
              </span>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="openModal(route)" class="text-green-600 hover:text-green-400 p-2 transition-colors">
                  <i class="ph ph-pencil-simple text-lg"></i>
                </button>
                <button @click="deleteRoute(route.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors">
                  <i class="ph ph-trash text-lg"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredRoutes.length === 0">
            <td colspan="5" class="px-6 py-10 text-center text-gray-400 italic poppins">No routes found matching your criteria.</td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination Section -->
      <div v-if="filteredRoutes.length > itemsPerPage" class="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
        <div class="flex items-center justify-between">
          <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
            Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ filteredRoutes.length }}
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
      </div>
    </div>

    <!-- Modal Section -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins transition-all duration-300">
      <div class="bg-white w-full max-w-5xl h-[85vh] flex flex-col md:flex-row shadow-2xl rounded-[1px] overflow-hidden border border-gray-100 animate-modal-in">
        <!-- Left Side: Form -->
        <div class="w-full md:w-5/12 p-8 flex flex-col justify-between overflow-y-auto bg-white border-r border-gray-100">
          <div>
            <div class="flex justify-between items-center mb-6">
              <h2 class="font-black text-xl text-[#002D1E] tracking-tight uppercase">
                {{ isEditing ? 'Edit Flight Route' : 'Create Flight Route' }}
              </h2>
            </div>
            
            <form @submit.prevent="saveRoute" class="space-y-6">
              <div>
                <label class="block text-[10px] font-black uppercase text-gray-400 mb-2 tracking-widest">Origin Airport</label>
                <SearchableSelect
                  v-model="form.origin_airport"
                  :options="airportOptions"
                  placeholder="Select or search origin..."
                  label="Origin Airport"
                />
              </div>

              <div>
                <label class="block text-[10px] font-black uppercase text-gray-400 mb-2 tracking-widest">Destination Airport</label>
                <SearchableSelect
                  v-model="form.destination_airport"
                  :options="airportOptions"
                  placeholder="Select or search destination..."
                  label="Destination Airport"
                />
              </div>

              <div>
                <label class="block text-[10px] font-black uppercase text-gray-400 mb-2 tracking-widest">Base Price (PHP)</label>
                <div class="relative">
                  <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[#002D1E] font-black text-sm">₱</span>
                  <input 
                    v-model="form.base_price" 
                    type="number" 
                    step="0.01" 
                    class="w-full border border-gray-200 p-3 pl-8 text-sm outline-none focus:border-[#fe3787] font-bold text-[#002D1E] transition-all bg-gray-50 focus:bg-white rounded-[1px]" 
                    placeholder="0.00" 
                    required
                  >
                </div>
              </div>
            </form>
          </div>
          
          <div class="flex justify-between items-center pt-6 border-t border-gray-100 mt-6 bg-white z-10">
            <button 
              type="button" 
              @click="isModalOpen = false" 
              class="text-xs font-black uppercase tracking-widest text-gray-400 hover:text-gray-600 transition-colors"
            >
              Cancel
            </button>
            <div class="flex gap-3">
              <button 
                type="button" 
                @click="clearRouteSelection" 
                class="border border-gray-200 text-gray-500 px-4 py-2.5 text-xs font-black uppercase tracking-widest hover:bg-gray-50 transition-all rounded-[1px]"
              >
                Reset
              </button>
              <button 
                type="submit" 
                @click="saveRoute"
                class="bg-[#fe3787] text-white px-6 py-2.5 text-xs font-black uppercase tracking-widest shadow-md hover:bg-[#e6327a] transition-all rounded-[1px]"
              >
                {{ isEditing ? 'Update Route' : 'Confirm Route' }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- Right Side: Leaflet Map -->
        <div class="hidden md:block w-7/12 relative bg-gray-50">
          <div id="modal-map" class="w-full h-full z-0"></div>
          
          <!-- Floating Map Guide Helper -->
          <div class="absolute top-4 right-4 z-[400] bg-white/90 backdrop-blur-md border border-gray-200/80 px-4 py-3 rounded-[1px] shadow-lg max-w-[240px]">
            <p class="text-[10px] font-black text-[#002D1E] uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
              <i class="ph ph-info text-[#fe3787] text-xs"></i> Interactive Map
            </p>
            <p class="text-[9px] text-gray-500 font-bold leading-normal">
              Click any airport pin on the map to set it as the Origin or Destination for your new route.
            </p>
            <div class="mt-3 pt-2 border-t border-gray-100 flex gap-4">
              <div class="flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                <span class="text-[8px] font-bold text-gray-400 uppercase">International</span>
              </div>
              <div class="flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-[#10b981]"></span>
                <span class="text-[8px] font-bold text-gray-400 uppercase">Domestic</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import api from '@/services/admin/api';
import { useModalStore } from '@/stores/modal';
import SearchableSelect from '@/components/admin/SearchableSelect.vue';
import AdminTableTool from '@/components/admin/AdminTableTool.vue';

// Leaflet fix for icons
if (L && L.Icon && L.Icon.Default) {
  delete L.Icon.Default.prototype._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
    iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
    shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
  })
}

const modalStore = useModalStore();

// --- State ---
const routes = ref([]);
const airports = ref([]);

const airportOptions = computed(() =>
  airports.value.map(a => ({ value: a.id, label: a.name, sublabel: `${a.code} · ${a.city || ''}`.replace(/·\s*$/, '').trim() }))
);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);

const highlightedId = ref(null);
const route = useRoute();

const searchQuery = ref('');
const selectedAirportFilter = ref('');

const form = ref({
  origin_airport: '',
  destination_airport: '',
  base_price: 0
});

// Map variables
let mapInstance = null;
let airportMarkers = [];
let routePolyline = null;

// Pagination State
const currentPage = ref(1);
const itemsPerPage = 10;

// --- Computed Stats ---
const stats = computed(() => {
  const uniqueOrigins = new Set(routes.value.map(r => r.origin_airport)).size;
  const uniqueHubs = new Set([
    ...routes.value.map(r => r.origin_airport),
    ...routes.value.map(r => r.destination_airport)
  ]).size;

  return {
    totalRoutes: routes.value.length,
    activeOrigins: uniqueOrigins,
    connectedHubs: uniqueHubs,
  };
});

const filteredRoutes = computed(() => {
  let filtered = routes.value;
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(route => 
      (route.origin_info || route.origin_airport_name || route.origin_airport || '').toString().toLowerCase().includes(query) ||
      (route.destination_info || route.destination_airport_name || route.destination_airport || '').toString().toLowerCase().includes(query)
    );
  }
  
  if (selectedAirportFilter.value) {
    const airportId = parseInt(selectedAirportFilter.value);
    filtered = filtered.filter(route => 
      route.origin_airport === airportId || route.destination_airport === airportId
    );
  }
  
  return filtered;
});

// Pagination Logic
const totalPages = computed(() => Math.ceil(filteredRoutes.value.length / itemsPerPage));
const paginatedRoutes = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return filteredRoutes.value.slice(start, start + itemsPerPage);
});
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage);
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredRoutes.value.length));

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

// --- Methods ---

const fetchData = async () => {
  try {
    const [routeRes, airportRes] = await Promise.all([
      api.get('/routes/'),
      api.get('/airports/')
    ]);

    routes.value = routeRes.data.results || routeRes.data;
    airports.value = airportRes.data.results || airportRes.data;

    if (route.query.page) {
        currentPage.value = parseInt(route.query.page);
    }

    // Handle highlighted record from query params
    if (route.query.highlight) {
        const hId = parseInt(route.query.highlight);
        highlightedId.value = hId;

        // Auto-navigate to the correct page for this ID
        const index = routes.value.findIndex(r => r.id === hId);
        if (index !== -1) {
            currentPage.value = Math.floor(index / itemsPerPage) + 1;
        }

        setTimeout(() => {
            const el = document.getElementById(`route-row-${hId}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Clear highlight after 3 seconds
            setTimeout(() => { highlightedId.value = null; }, 3000);
        }, 500);
    }
  } catch (error) {
    console.error("Fetch Error:", error.response?.data || error.message);
  }
};

const clearFilters = () => {
  searchQuery.value = '';
  selectedAirportFilter.value = '';
  currentPage.value = 1;
};

const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const goToPage = (p) => { if (p !== '...') currentPage.value = p; };

watch([searchQuery, selectedAirportFilter], () => { currentPage.value = 1; });

// --- Map Operations ---
const initMap = () => {
  const container = document.getElementById('modal-map');
  if (!container || mapInstance) return;

  mapInstance = L.map(container, {
    center: [12.8797, 121.7740],
    zoom: 6,
    zoomControl: true,
    attributionControl: false
  });

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19
  }).addTo(mapInstance);

  renderMapAirports();
  updateMapRoute();
};

const destroyMap = () => {
  if (mapInstance) {
    mapInstance.remove();
    mapInstance = null;
  }
  airportMarkers = [];
  routePolyline = null;
};

const clearRouteSelection = () => {
  form.value.origin_airport = '';
  form.value.destination_airport = '';
  form.value.base_price = 0;
  updateMapRoute();
};

const renderMapAirports = () => {
  if (!mapInstance) return;

  airportMarkers.forEach(m => m.remove());
  airportMarkers = [];

  const originId = form.value.origin_airport;
  const destId = form.value.destination_airport;

  airports.value.forEach(ap => {
    const lat = ap.latitude !== undefined && ap.latitude !== null ? parseFloat(ap.latitude) : parseFloat(ap.lat);
    const lng = ap.longitude !== undefined && ap.longitude !== null ? parseFloat(ap.longitude) : parseFloat(ap.lng);

    if (isNaN(lat) || isNaN(lng)) return;

    const isOrigin = originId && Number(ap.id) === Number(originId);
    const isDest = destId && Number(ap.id) === Number(destId);

    const isIntl = ap.airport_type === 'international' || ap.type === 'international';
    let color = isIntl ? '#3b82f6' : '#10b981';
    let border = '2px solid white';
    let scale = 'scale(1)';
    let zIndex = 100;
    let shadow = isIntl ? 'rgba(59,130,246,0.35)' : 'rgba(16,185,129,0.35)';

    if (isOrigin) {
      color = '#fe3787'; // Pink highlight for Origin
      border = '2px solid #002D1E';
      scale = 'scale(1.5)';
      zIndex = 1000;
      shadow = 'rgba(254, 55, 135, 0.6)';
    } else if (isDest) {
      color = '#002D1E'; // Dark green/black for Destination
      border = '2px solid #fe3787';
      scale = 'scale(1.5)';
      zIndex = 1000;
      shadow = 'rgba(0, 45, 30, 0.6)';
    }

    const apIcon = L.divIcon({
      html: `<div style="
        width: 12px; height: 12px;
        background: ${color};
        border: ${border};
        border-radius: 50%;
        box-shadow: 0 0 10px ${shadow};
        cursor: pointer;
        transform: ${scale};
        transition: transform 0.2s ease, background-color 0.2s ease;
      "></div>`,
      className: 'airport-dot-icon',
      iconSize: [12, 12],
      iconAnchor: [6, 6]
    });

    const marker = L.marker([lat, lng], { icon: apIcon, zIndexOffset: zIndex })
      .addTo(mapInstance)
      .bindTooltip(
        `<div class="poppins" style="min-width:130px; font-family: 'Poppins', sans-serif;">
          <span style="font-size:11px; font-weight:900; color:#002D1E; display:block">${ap.code} – ${ap.name}</span>
          <span style="font-size:9px; color:#888; font-weight:700; text-transform:uppercase">${ap.city || ''}</span><br>
          <span style="font-size:8px; font-weight:900; text-transform:uppercase; color:${color}">${ap.airport_type || ap.type}</span>
          ${isOrigin ? '<span style="font-size:8px; font-weight:900; color:#fe3787; display:block; margin-top:2px;">[ORIGIN]</span>' : ''}
          ${isDest ? '<span style="font-size:8px; font-weight:900; color:#002D1E; display:block; margin-top:2px;">[DESTINATION]</span>' : ''}
        </div>`,
        { direction: 'top', className: 'airport-tooltip', offset: [0, -6] }
      );

    const popupContent = document.createElement('div');
    popupContent.className = 'poppins p-2 text-center flex flex-col gap-2';
    popupContent.style.fontFamily = "'Poppins', sans-serif";
    
    const title = document.createElement('div');
    title.className = 'font-bold text-xs text-[#002D1E] mb-1';
    title.innerText = `${ap.code} - ${ap.name}`;
    popupContent.appendChild(title);

    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'flex gap-2 justify-center';

    const setOriginBtn = document.createElement('button');
    setOriginBtn.className = 'bg-[#fe3787] text-white text-[10px] font-bold px-2 py-1 rounded hover:bg-[#e6327a] transition-all cursor-pointer';
    setOriginBtn.innerText = 'Set Origin';
    setOriginBtn.onclick = () => {
      form.value.origin_airport = ap.id;
      marker.closePopup();
      updateMapRoute();
    };
    buttonContainer.appendChild(setOriginBtn);

    const setDestBtn = document.createElement('button');
    setDestBtn.className = 'bg-[#002D1E] text-white text-[10px] font-bold px-2 py-1 rounded hover:bg-black transition-all cursor-pointer';
    setDestBtn.innerText = 'Set Destination';
    setDestBtn.onclick = () => {
      form.value.destination_airport = ap.id;
      marker.closePopup();
      updateMapRoute();
    };
    buttonContainer.appendChild(setDestBtn);

    popupContent.appendChild(buttonContainer);

    marker.bindPopup(popupContent, {
      closeButton: false,
      minWidth: 180
    });

    airportMarkers.push(marker);
  });
};

const updateMapRoute = () => {
  if (!mapInstance) return;

  if (routePolyline) {
    routePolyline.remove();
    routePolyline = null;
  }

  // Reactive redraw of airport markers to show dynamic colors
  renderMapAirports();

  const originId = form.value.origin_airport;
  const destId = form.value.destination_airport;

  const originAp = airports.value.find(a => Number(a.id) === Number(originId));
  const destAp = airports.value.find(a => Number(a.id) === Number(destId));

  const points = [];

  if (originAp) {
    const lat = originAp.latitude !== undefined && originAp.latitude !== null ? parseFloat(originAp.latitude) : parseFloat(originAp.lat);
    const lng = originAp.longitude !== undefined && originAp.longitude !== null ? parseFloat(originAp.longitude) : parseFloat(originAp.lng);
    if (!isNaN(lat) && !isNaN(lng)) {
      points.push([lat, lng]);
    }
  }

  if (destAp) {
    const lat = destAp.latitude !== undefined && destAp.latitude !== null ? parseFloat(destAp.latitude) : parseFloat(destAp.lat);
    const lng = destAp.longitude !== undefined && destAp.longitude !== null ? parseFloat(destAp.longitude) : parseFloat(destAp.lng);
    if (!isNaN(lat) && !isNaN(lng)) {
      points.push([lat, lng]);
    }
  }

  if (points.length === 2) {
    routePolyline = L.polyline(points, {
      color: '#fe3787',
      weight: 4,
      opacity: 0.9,
      dashArray: '8, 8'
    }).addTo(mapInstance);

    mapInstance.fitBounds(routePolyline.getBounds(), { padding: [60, 60] });
  } else if (points.length === 1) {
    mapInstance.flyTo(points[0], 8, { duration: 1.0 });
  } else {
    mapInstance.setView([12.8797, 121.7740], 6);
  }
};

// --- Modal and Form Watches ---
watch(isModalOpen, async (newVal) => {
  if (newVal) {
    await nextTick();
    setTimeout(initMap, 200);
  } else {
    destroyMap();
  }
});

watch(() => form.value.origin_airport, () => {
  updateMapRoute();
});

watch(() => form.value.destination_airport, () => {
  updateMapRoute();
});

const saveRoute = async () => {
  if (form.value.origin_airport === form.value.destination_airport) {
    alert("Error: Origin and Destination cannot be the same airport.");
    return;
  }

  try {
    const payload = {
      origin_airport: form.value.origin_airport,
      destination_airport: form.value.destination_airport,
      base_price: parseFloat(form.value.base_price)
    };

    if (isEditing.value) {
      await api.put(`/routes/${currentId.value}/`, payload);
    } else {
      await api.post('/routes/', payload);
    }
    
    await fetchData(); 
    isModalOpen.value = false;
  } catch (error) {
    console.error("Save failed:", error.response?.data);
    const errorMsg = error.response?.data?.non_field_errors?.[0] || "Check if this route already exists.";
    alert("Error: " + errorMsg);
  }
};

const deleteRoute = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Purge Flight Route?',
    message: 'Are you sure you want to permanently remove this route? This will affect schedules linked to it.',
    variant: 'danger',
    confirmText: 'Purge',
    loadingText: 'Purging...'
  });

  if (confirmed) {
    modalStore.setLoader(true);
    try {
      await api.delete(`/routes/${id}/`);
      routes.value = routes.value.filter(r => r.id !== id);
      modalStore.close(true);
    } catch (error) {
      console.error("Delete failed:", error);
      modalStore.setLoader(false);
      alert("Could not delete. Route may be in use by active flights.");
    }
  }
};

const openModal = (route = null) => {
  if (route) {
    isEditing.value = true;
    currentId.value = route.id;
    form.value = { 
      origin_airport: route.origin_airport, 
      destination_airport: route.destination_airport, 
      base_price: route.base_price 
    };
  } else {
    isEditing.value = false;
    currentId.value = null;
    form.value = { origin_airport: '', destination_airport: '', base_price: 0 };
  }
  isModalOpen.value = true;
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

/* Modal In Animation */
@keyframes modal-in {
  from {
    opacity: 0;
    transform: scale(0.98) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.animate-modal-in {
  animation: modal-in 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* Custom tooltip styling to match premium feel */
:deep(.airport-tooltip) {
  background: white !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  border-radius: 2px !important;
  padding: 6px 10px !important;
  opacity: 1 !important;
}

/* Leaflet popup overrides */
:deep(.leaflet-popup-content-wrapper) {
  border-radius: 2px !important;
  box-shadow: 0 10px 35px rgba(0,0,0,0.12) !important;
  border: 1px solid #e2e8f0 !important;
  padding: 0 !important;
}

:deep(.leaflet-popup-content) {
  margin: 0 !important;
}

:deep(.leaflet-popup-tip-container) {
  display: none !important;
}
</style>
