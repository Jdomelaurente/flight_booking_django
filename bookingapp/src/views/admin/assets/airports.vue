<template>
  <div class="p-6 poppins">
    <!-- Header Section -->
    <div class="flex justify-between items-center mb-6">
      <button 
        @click="openModal()" 
        class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all"
      >
        <i class="ph ph-plus"></i> Add Airport
      </button>
    </div>

    <!-- Table Section -->
    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Code</th>
            <th class="px-6 py-4 poppins">Airport</th>
            <th class="px-6 py-4 poppins">City/Country</th>
            <th class="px-6 py-4 poppins">Type</th>
            <th class="px-6 py-4 poppins text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="airport in airports" :key="airport.id" class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium">
            <td class="px-6 py-4">
              <span class="font-bold text-[#fe3787] poppins text-sm">{{ airport.code }}</span>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <i class="ph ph-buildings text-blue-600"></i>
                </div>
                <div>
                  <span class="font-bold text-[#002D1E] block poppins">{{ airport.name }}</span>
                  <span class="text-gray-400 poppins text-[10px]">{{ airport.location }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 poppins">
              {{ airport.city }}, {{ airport.country_name || 'N/A' }}
            </td>
            <td class="px-6 py-4">
              <span 
                :class="airport.airport_type === 'international' ? 'bg-purple-100 text-purple-700' : 'bg-green-100 text-green-700'" 
                class="px-3 py-1 rounded-full text-[10px] font-bold uppercase poppins"
              >
                {{ airport.airport_type }}
              </span>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="openModal(airport)" class="text-green-600 hover:text-green-400 p-2 transition-colors">
                  <i class="ph ph-pencil-simple text-lg"></i>
                </button>
                <button @click="deleteAirport(airport.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors">
                  <i class="ph ph-trash text-lg"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="airports.length === 0">
            <td colspan="5" class="px-6 py-10 text-center text-gray-400 italic poppins">No airports found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Section -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-lg p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">{{ isEditing ? 'Edit Airport' : 'Add New Airport' }}</h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveAirport" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2">
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Airport Name</label>
              <input v-model="form.name" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
            </div>
            
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">IATA Code</label>
              <input v-model="form.code" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="MNL" maxlength="3" required>
            </div>

            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Type</label>
              <select v-model="form.airport_type" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px] bg-white">
                <option value="domestic">Domestic</option>
                <option value="international">International</option>
                <option value="unknown">Unknown</option>
              </select>
            </div>

            <div class="col-span-2">
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">City</label>
              <input v-model="form.city" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]">
            </div>

            <div class="col-span-2">
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Detailed Location</label>
              <input v-model="form.location" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="NAIA Terminal 3, Pasay City">
            </div>
          </div>
          
          <div class="flex justify-end gap-3 pt-6 border-t mt-4">
            <button type="button" @click="isModalOpen = false" class="text-sm text-gray-500 font-medium hover:text-gray-700 poppins">Cancel</button>
            <button type="submit" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins">
              {{ isEditing ? 'Update Airport' : 'Confirm Airport' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/admin/api';

// State
const airports = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);

const form = ref({
  name: '',
  code: '',
  city: '',
  location: '',
  airport_type: 'domestic'
});

// Fetch Data
const fetchAirports = async () => {
  try {
    const res = await api.get('/airports/');
    airports.value = res.data.results || res.data;
  } catch (err) {
    console.error("Fetch Error:", err.response?.data || err.message);
  }
};

// Save (Create or Update)
const saveAirport = async () => {
  try {
    if (isEditing.value) {
      await api.put(`/airports/${currentId.value}/`, form.value);
    } else {
      await api.post('/airports/', form.value);
    }
    await fetchAirports(); 
    isModalOpen.value = false;
  } catch (err) {
    console.error("Save error:", err.response?.data);
    alert("Save failed. Please check the data format.");
  }
};

// Delete
const deleteAirport = async (id) => {
  if (confirm('Are you sure you want to delete this airport? This may affect existing routes.')) {
    try {
      await api.delete(`/airports/${id}/`);
      airports.value = airports.value.filter(a => a.id !== id);
    } catch (err) {
      console.error("Delete error:", err.response?.data);
      alert("Delete failed. This airport might be in use.");
    }
  }
};

// UI Logic
const openModal = (airport = null) => {
  if (airport) {
    isEditing.value = true;
    currentId.value = airport.id;
    form.value = { 
      name: airport.name, 
      code: airport.code, 
      city: airport.city, 
      location: airport.location, 
      airport_type: airport.airport_type 
    };
  } else {
    isEditing.value = false;
    currentId.value = null;
    form.value = { name: '', code: '', city: '', location: '', airport_type: 'domestic' };
  }
  isModalOpen.value = true;
};

onMounted(fetchAirports);
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

.poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
