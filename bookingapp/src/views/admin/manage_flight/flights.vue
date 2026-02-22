<template>
  <div class="p-6 poppins">
    <!-- Header Section -->
    <div class="flex justify-between items-center mb-6">
      <button 
        @click="openModal()" 
        class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all"
      >
        <i class="ph ph-plus"></i>
        Create Flight
      </button>
    </div>

    <!-- Stats Section -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
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

    <!-- Table Section -->
    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Flight #</th>
            <th class="px-6 py-4 poppins">Airline</th>
            <th class="px-6 py-4 poppins">Aircraft</th>
            <th class="px-6 py-4 poppins">Route</th>
            <th class="px-6 py-4 poppins text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="f in flights" :key="f.id" class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium">
            <td class="px-6 py-4">
              <span class="font-bold text-[#fe3787] poppins text-sm">{{ f.flight_number }}</span>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center">
                  <i class="ph ph-buildings text-blue-600"></i>
                </div>
                <span class="font-bold text-[#002D1E] poppins">{{ f.airline_display || 'N/A' }}</span>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-2">
                <i class="ph ph-airplane-tilt text-gray-400"></i>
                <span class="text-gray-700 poppins">{{ f.aircraft_display || 'N/A' }}</span>
              </div>
            </td>
            <td class="px-6 py-4">
               <span class="bg-purple-100 text-purple-700 px-3 py-1 rounded-[1px] text-[10px] font-bold uppercase poppins tracking-tight">
                 {{ f.route_display || 'No Route' }}
               </span>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="openModal(f)" class="text-green-600 hover:text-green-400 p-2 transition-colors">
                  <i class="ph ph-pencil-simple text-lg"></i>
                </button>
                <button @click="deleteFlight(f.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors">
                  <i class="ph ph-trash text-lg"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="flights.length === 0">
            <td colspan="5" class="px-6 py-10 text-center text-gray-400 italic poppins">No flights found. Please add one.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Section -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">
            {{ isEditing ? 'Edit Flight' : 'New Flight' }}
          </h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveFlight" class="space-y-4">
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Flight Number</label>
            <input v-model="form.flight_number" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="e.g. PR101" required>
          </div>

          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Airline Owner</label>
            <select v-model="form.airline" class="w-full border p-2 text-sm bg-white outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
              <option value="" disabled>Select Airline</option>
              <option v-for="a in airlines" :key="a.id" :value="a.id">{{ a.name }}</option>
            </select>
          </div>

          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Aircraft Model</label>
            <select v-model="form.aircraft" class="w-full border p-2 text-sm bg-white outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required :disabled="!form.airline">
              <option value="" disabled>{{ form.airline ? 'Select Aircraft' : 'Select Airline First' }}</option>
              <option v-for="ac in filteredAircrafts" :key="ac.id" :value="ac.id">
                {{ ac.model }} ({{ ac.capacity }} seats)
              </option>
            </select>
          </div>

          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Flight Route</label>
            <select v-model="form.route" class="w-full border p-2 text-sm bg-white outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
              <option value="" disabled>Select Route</option>
              <option v-for="r in routes" :key="r.id" :value="r.id">
                {{ r.origin_info }} → {{ r.destination_info }}
              </option>
            </select>
          </div>

          <div class="flex justify-end gap-3 pt-6 border-t mt-4">
            <button type="button" @click="isModalOpen = false" class="text-sm text-gray-500 font-medium hover:text-gray-700 poppins">Cancel</button>
            <button type="submit" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins">
              {{ isEditing ? 'Update Flight' : 'Confirm Flight' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api from '@/services/admin/api';
import { useModalStore } from '@/stores/modal';

const modalStore = useModalStore();

const flights = ref([]);
const airlines = ref([]);
const allAircrafts = ref([]);
const filteredAircrafts = ref([]);
const routes = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);

const form = ref({
  flight_number: '',
  airline: '',
  aircraft: '',
  route: ''
});

// --- Computed Stats ---
const statsItems = computed(() => {
  return {
    'Total Flights': flights.value.length,
    'Active Airlines': new Set(flights.value.map(f => f.airline)).size,
    'Operational Aircraft': new Set(flights.value.map(f => f.aircraft)).size,
  };
});

const statIcon = (label) => {
  if (label === 'Total Flights') return 'ph ph-airplane';
  if (label === 'Active Airlines') return 'ph ph-buildings';
  return 'ph ph-airplane-tilt';
};

const statIconClass = (label) => {
  if (label === 'Total Flights') return 'bg-blue-100 text-blue-600';
  if (label === 'Active Airlines') return 'bg-green-100 text-green-600';
  return 'bg-purple-100 text-purple-600';
};

const fetchData = async () => {
  try {
    const [resF, resA, resAc, resR] = await Promise.all([
      api.get('/flights/'),
      api.get('/airlines/'),
      api.get('/aircraft/'),
      api.get('/routes/')
    ]);

    flights.value = resF.data.results || resF.data;
    airlines.value = resA.data.results || resA.data;
    allAircrafts.value = resAc.data.results || resAc.data;
    routes.value = resR.data.results || resR.data;
  } catch (err) {
    console.error("Data fetch failed:", err.response?.data || err.message);
  }
};

watch(() => form.value.airline, (newAirlineId) => {
  if (newAirlineId) {
    filteredAircrafts.value = allAircrafts.value.filter(
      ac => ac.airline === newAirlineId
    );
    if (!filteredAircrafts.value.find(ac => ac.id === form.value.aircraft)) {
      form.value.aircraft = '';
    }
  } else {
    filteredAircrafts.value = [];
  }
});

const saveFlight = async () => {
  try {
    const payload = { ...form.value };
    payload.flight_number = payload.flight_number.toUpperCase().trim();

    if (isEditing.value) {
      await api.put(`/flights/${currentId.value}/`, payload);
    } else {
      await api.post('/flights/', payload);
    }
    
    await fetchData();
    isModalOpen.value = false;
  } catch (err) {
    console.error("Save error:", err.response?.data);
    alert("Error saving flight.");
  }
};

const deleteFlight = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Delete Flight?',
    message: 'Are you sure you want to delete this flight record?',
    variant: 'danger',
    confirmText: 'Delete',
    loadingText: 'Deleting...'
  });

  if (confirmed) {
    modalStore.setLoader(true);
    try {
      await api.delete(`/flights/${id}/`);
      await fetchData();
      modalStore.close(true);
    } catch (err) {
      console.error("Delete Error:", err);
      modalStore.setLoader(false);
    }
  }
};

const openModal = (flight = null) => {
  isEditing.value = !!flight;
  currentId.value = flight?.id || null;
  
  if (flight) {
    form.value = { 
      flight_number: flight.flight_number,
      airline: flight.airline, 
      aircraft: flight.aircraft, 
      route: flight.route 
    };
  } else {
    form.value = { flight_number: '', airline: '', aircraft: '', route: '' };
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
