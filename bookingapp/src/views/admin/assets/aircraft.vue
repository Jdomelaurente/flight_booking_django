<template>
  <div class="p-6 poppins">
    <!-- Header Section -->
    <div class="flex justify-between items-center mb-6">
      <button 
        @click="openModal()" 
        class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all"
      >
        <i class="ph ph-plus"></i> Add Aircraft
      </button>
    </div>

    <!-- Table Section -->
    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Model</th>
            <th class="px-6 py-4 poppins">Airline</th>
            <th class="px-6 py-4 poppins text-center">Capacity</th>
            <th class="px-6 py-4 poppins text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="plane in aircraftList" :key="plane.id" class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium">
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <i class="ph ph-airplane text-blue-600"></i>
                </div>
                <span class="font-bold text-[#002D1E] poppins">{{ plane.model }}</span>
              </div>
            </td>
            <td class="px-6 py-4">
               <span class="bg-gray-100 text-gray-600 px-3 py-1 rounded-[1px] text-[10px] font-bold uppercase poppins">
                 {{ plane.airline_name || 'Unassigned' }}
               </span>
            </td>
            <td class="px-6 py-4 text-center">
              <span class="font-bold text-[#fe3787] poppins">{{ plane.capacity }} seats</span>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="openModal(plane)" class="text-green-600 hover:text-green-400 p-2 transition-colors">
                  <i class="ph ph-pencil-simple text-lg"></i>
                </button>
                <button @click="deleteAircraft(plane.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors">
                  <i class="ph ph-trash text-lg"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="aircraftList.length === 0">
            <td colspan="4" class="px-6 py-10 text-center text-gray-400 italic poppins">No aircraft found in the fleet.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Section -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">{{ isEditing ? 'Edit Aircraft' : 'Register New Aircraft' }}</h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveAircraft" class="space-y-4">
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Airline Owner</label>
            <select v-model="form.airline" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px] bg-white" required>
              <option value="" disabled>Select Airline</option>
              <option v-for="a in airlines" :key="a.id" :value="a.id">{{ a.name }} ({{ a.code }})</option>
            </select>
          </div>
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Aircraft Model</label>
            <input v-model="form.model" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="e.g. Airbus A321neo" required>
          </div>
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Total Seat Capacity</label>
            <input v-model="form.capacity" type="number" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
          </div>
          
          <div class="flex justify-end gap-3 pt-6 border-t mt-4">
            <button type="button" @click="isModalOpen = false" class="text-sm text-gray-500 font-medium hover:text-gray-700 poppins">Cancel</button>
            <button type="submit" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins">
              {{ isEditing ? 'Update Aircraft' : 'Confirm Aircraft' }}
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

const aircraftList = ref([]);
const airlines = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const form = ref({ model: '', capacity: 0, airline: '' });

const fetchData = async () => {
  try {
    const [planeRes, airlineRes] = await Promise.all([
      api.get('/aircraft/'),
      api.get('/airlines/')
    ]);
    aircraftList.value = planeRes.data.results || planeRes.data;
    airlines.value = airlineRes.data.results || airlineRes.data;
  } catch (err) { 
    console.error("Fetch Error:", err); 
  }
};

const saveAircraft = async () => {
  try {
    if (isEditing.value) await api.put(`/aircraft/${currentId.value}/`, form.value);
    else await api.post('/aircraft/', form.value);
    await fetchData();
    isModalOpen.value = false;
  } catch (err) { 
    console.error("Save Error:", err);
    alert("Error saving aircraft."); 
  }
};

const deleteAircraft = async (id) => {
  if (confirm('Remove this aircraft from fleet?')) {
    try {
      await api.delete(`/aircraft/${id}/`);
      await fetchData();
    } catch (err) {
      console.error("Delete Error:", err);
      alert("Delete failed.");
    }
  }
};

const openModal = (plane = null) => {
  isEditing.value = !!plane;
  currentId.value = plane?.id || null;
  form.value = plane ? { model: plane.model, capacity: plane.capacity, airline: plane.airline } : { model: '', capacity: 0, airline: '' };
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
