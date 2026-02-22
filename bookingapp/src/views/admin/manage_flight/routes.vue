<template>
  <div class="p-6 poppins">
    <!-- Header Section -->
    <div class="flex justify-between items-center mb-6">
      <button 
        @click="openModal()" 
        class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#e02d74] transition-all shadow-sm rounded-[1px] font-semibold text-[14px]"
      >
        <i class="ph ph-plus"></i>
        Add New Route
      </button>
    </div>

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

    <!-- Filters Section -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-4 mb-6 text-[14px]">
      <div class="flex flex-col md:flex-row md:items-center gap-4">
        <div class="relative flex-1">
          <i class="ph ph-magnifying-glass absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search by origin or destination..." 
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-[1px] w-full focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
          />
        </div>
        
        <select 
          v-model="selectedAirportFilter" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px] min-w-[150px]"
        >
          <option value="">All Airports</option>
          <option v-for="airport in airports" :key="airport.id" :value="airport.id">
            {{ airport.code }} - {{ airport.name }}
          </option>
        </select>

        <button 
          @click="clearFilters" 
          class="text-white px-4 py-2 border bg-[#fe3787] rounded-[1px] hover:bg-[#fb1873] font-medium poppins text-[14px]"
        >
          Clear
        </button>
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
          <tr v-for="route in filteredRoutes" :key="route.id" class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium">
            <td class="px-6 py-4">
              <span class="font-bold text-gray-400 block poppins">#{{ route.id }}</span>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-[#fe3787] flex items-center justify-center">
                  <i class="ph ph-airplane-takeoff text-white text-md"></i>
                </div>
                <div>
                  <span class="font-bold text-[#002D1E] block poppins">
                    {{ route.origin_info || route.origin_airport_name || route.origin_airport }}
                  </span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-[#002D1E] flex items-center justify-center">
                  <i class="ph ph-airplane-landing text-white text-md"></i>
                </div>
                <div>
                  <span class="font-bold text-[#002D1E] block poppins">
                    {{ route.destination_info || route.destination_airport_name || route.destination_airport }}
                  </span>
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
    </div>

    <!-- Modal Section -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-md p-6 shadow-2xl rounded-[1px]">
        <div class="flex justify-between items-center mb-6">
          <h2 class="font-bold text-lg text-[#002D1E]">
            {{ isEditing ? 'Edit Route' : 'New Flight Route' }}
          </h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveRoute" class="space-y-4">
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Origin Airport</label>
            <select v-model="form.origin_airport" class="w-full border p-2 text-sm bg-white focus:border-[#fe3787] outline-none transition-all rounded-[1px]" required>
              <option value="" disabled>Choose origin...</option>
              <option v-for="airport in airports" :key="airport.id" :value="airport.id">
                {{ airport.name }} ({{ airport.code }})
              </option>
            </select>
          </div>

          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Destination Airport</label>
            <select v-model="form.destination_airport" class="w-full border p-2 text-sm bg-white focus:border-[#fe3787] outline-none transition-all rounded-[1px]" required>
              <option value="" disabled>Choose destination...</option>
              <option v-for="airport in airports" :key="airport.id" :value="airport.id">
                {{ airport.name }} ({{ airport.code }})
              </option>
            </select>
          </div>

          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Base Price (PHP)</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 font-bold text-sm">₱</span>
              <input v-model="form.base_price" type="number" step="0.01" class="w-full border p-2 pl-7 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="0.00" required>
            </div>
          </div>
          
          <div class="flex justify-end gap-3 pt-4 border-t">
            <button type="button" @click="isModalOpen = false" class="text-sm text-gray-500 font-medium hover:text-gray-700 poppins">Cancel</button>
            <button type="submit" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins">
              {{ isEditing ? 'Update Route' : 'Confirm Route' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import api from '@/services/admin/api';
import { useModalStore } from '@/stores/modal';

const modalStore = useModalStore();

// --- State ---
const routes = ref([]);
const airports = ref([]); 
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);

const searchQuery = ref('');
const selectedAirportFilter = ref('');

const form = ref({
  origin_airport: '',
  destination_airport: '',
  base_price: 0
});

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
      (route.origin_info || route.origin_airport_name || route.origin_airport).toLowerCase().includes(query) ||
      (route.destination_info || route.destination_airport_name || route.destination_airport).toLowerCase().includes(query)
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

// --- Methods ---

const fetchData = async () => {
  try {
    const [routeRes, airportRes] = await Promise.all([
      api.get('/routes/'),
      api.get('/airports/')
    ]);

    routes.value = routeRes.data.results || routeRes.data;
    airports.value = airportRes.data.results || airportRes.data;
  } catch (error) {
    console.error("Fetch Error:", error.response?.data || error.message);
  }
};

const clearFilters = () => {
  searchQuery.value = '';
  selectedAirportFilter.value = '';
};

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

.poppins {
  font-family: 'Poppins', sans-serif;
}
</style>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

.poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
