<template>
  <div class="p-6 poppins">
    <!-- Header Section -->
    <div class="flex justify-between items-center mb-6">
      <button 
        @click="openModal()" 
        class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all"
      >
        <i class="ph ph-plus"></i> Add Class
      </button>
    </div>

    <!-- Table Section -->
    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Name</th>
            <th class="px-6 py-4 poppins">Airline</th>
            <th class="px-6 py-4 poppins">Multiplier</th>
            <th class="px-6 py-4 poppins text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="sc in seatClasses" :key="sc.id" class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium">
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                  <i class="ph ph-star text-purple-600"></i>
                </div>
                <span class="font-bold text-[#002D1E] poppins">{{ sc.name }}</span>
              </div>
            </td>
            <td class="px-6 py-4 poppins">
              <span class="bg-gray-100 text-gray-600 px-3 py-1 rounded-[1px] text-[10px] font-bold uppercase">
                {{ sc.airline_name || 'Global' }}
              </span>
            </td>
            <td class="px-6 py-4">
              <span class="text-blue-600 font-bold poppins">x{{ parseFloat(sc.price_multiplier).toFixed(2) }}</span>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="openModal(sc)" class="text-green-600 hover:text-green-400 p-2 transition-colors">
                  <i class="ph ph-pencil-simple text-lg"></i>
                </button>
                <button @click="deleteSeatClass(sc.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors">
                  <i class="ph ph-trash text-lg"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="seatClasses.length === 0">
            <td colspan="4" class="px-6 py-10 text-center text-gray-400 italic poppins">No seat classes found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Section -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">{{ isEditing ? 'Edit Seat Class' : 'New Seat Class' }}</h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveSeatClass" class="space-y-4">
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Airline</label>
            <select v-model="form.airline" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px] bg-white" required>
              <option value="" disabled>Select Airline</option>
              <option v-for="a in airlines" :key="a.id" :value="a.id">{{ a.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Class Name</label>
            <input v-model="form.name" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="e.g. Business Class" required>
          </div>
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Price Multiplier</label>
            <input v-model="form.price_multiplier" type="number" step="0.01" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
          </div>
          
          <div class="flex justify-end gap-3 pt-6 border-t mt-4">
            <button type="button" @click="isModalOpen = false" class="text-sm text-gray-500 font-medium hover:text-gray-700 poppins">Cancel</button>
            <button type="submit" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins">
              {{ isEditing ? 'Update Class' : 'Confirm Class' }}
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
import { useModalStore } from '@/stores/modal';

const modalStore = useModalStore();

const seatClasses = ref([]);
const airlines = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const form = ref({ airline: '', name: '', price_multiplier: 1.00 });

const fetchData = async () => {
  try {
    const [scRes, aRes] = await Promise.all([
      api.get('/seat-classes/'),
      api.get('/airlines/')
    ]);
    seatClasses.value = scRes.data.results || scRes.data;
    airlines.value = aRes.data.results || aRes.data;
  } catch (err) {
    console.error("Fetch Error:", err);
  }
};

const saveSeatClass = async () => {
  try {
    const payload = { ...form.value };
    if (isEditing.value) await api.put(`/seat-classes/${currentId.value}/`, payload);
    else await api.post('/seat-classes/', payload);
    await fetchData();
    isModalOpen.value = false;
  } catch (err) { 
    console.error("Save Error:", err);
    alert("Error saving seat class."); 
  }
};

const deleteSeatClass = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Delete Seat Class?',
    message: 'Are you sure you want to delete this seat class?',
    variant: 'danger',
    confirmText: 'Delete',
    loadingText: 'Deleting...'
  });

  if (confirmed) {
    modalStore.setLoader(true);
    try {
      await api.delete(`/seat-classes/${id}/`);
      await fetchData();
      modalStore.close(true);
    } catch (err) {
      console.error("Delete Error:", err);
      modalStore.setLoader(false);
    }
  }
};

const openModal = (sc = null) => {
  isEditing.value = !!sc;
  currentId.value = sc?.id || null;
  form.value = sc ? { airline: sc.airline, name: sc.name, price_multiplier: sc.price_multiplier } : { airline: '', name: '', price_multiplier: 1.00 };
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
