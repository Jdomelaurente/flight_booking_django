<template>
  <div class="p-6 poppins">
    <!-- Header & Tools Section -->
    <AdminTableTool 
      v-model="searchQuery" 
      placeholder="Search class name..."
    >
      <template #filters>
        <div class="flex items-center gap-2">
          <select 
            v-model="filterAirline"
            class="text-[11px] font-bold border border-gray-200 px-3 py-2 bg-white rounded-[1px] outline-none focus:border-[#fe3787] poppins cursor-pointer min-w-[150px]"
          >
            <option value="all">Any Airline</option>
            <option v-for="a in airlines" :key="a.id" :value="a.id">
              {{ a.name }}
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
          <tr 
            v-for="sc in paginatedSeatClasses" 
            :key="sc.id" 
            :id="`seatclass-row-${sc.id}`"
            :class="{'highlight-active': highlightedId === sc.id}"
            class="hover:bg-gray-50/50 transition-all text-[12px] font-medium"
          >
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                  <i class="ph ph-star text-purple-600"></i>
                </div>
                <div>
                  <span class="font-bold text-[#002D1E] poppins block">{{ sc.name }}</span>
                  <div class="flex items-center gap-1 mt-1">
                    <span class="text-[9px] text-gray-400 font-bold uppercase poppins">Class ID: {{ sc.id }}</span>
                    <div class="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse"></div>
                  </div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 poppins">
              <router-link 
                v-if="sc.airline"
                :to="{ name: 'AdminAirlines', query: { highlight: sc.airline } }"
                class="bg-gray-100 text-gray-600 px-3 py-1 rounded-[1px] text-[10px] font-bold uppercase hover:bg-[#fe3787] hover:text-white transition-all inline-block"
                title="View Airline Connection"
              >
                {{ sc.airline_name || 'Global' }}
              </router-link>
              <span v-else class="bg-gray-100 text-gray-600 px-3 py-1 rounded-[1px] text-[10px] font-bold uppercase italic">
                Global
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
          <tr v-if="filteredSeatClasses.length === 0">
            <td colspan="4" class="px-6 py-10 text-center text-gray-400 italic poppins">No seat classes found.</td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination Section -->
      <div v-if="filteredSeatClasses.length > itemsPerPage" class="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
        <div class="flex items-center justify-between">
          <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
            Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ filteredSeatClasses.length }}
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
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/admin/api';
import { useModalStore } from '@/stores/modal';
import AdminTableTool from '@/components/admin/AdminTableTool.vue';

const modalStore = useModalStore();

const seatClasses = ref([]);
const airlines = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const highlightedId = ref(null);
const route = useRoute();
const searchQuery = ref('');
const filterAirline = ref('all');

// Pagination State
const currentPage = ref(1);
const itemsPerPage = 10;

const form = ref({ airline: '', name: '', price_multiplier: 1.00 });

// Search & Filter Logic
const filteredSeatClasses = computed(() => {
  let result = seatClasses.value;
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(sc => sc.name.toLowerCase().includes(q));
  }

  if (filterAirline.value !== 'all') {
    result = result.filter(sc => sc.airline === filterAirline.value);
  }
  
  return result;
});

// Pagination Logic
const totalPages = computed(() => Math.ceil(filteredSeatClasses.value.length / itemsPerPage));
const paginatedSeatClasses = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return filteredSeatClasses.value.slice(start, start + itemsPerPage);
});
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage);
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredSeatClasses.value.length));

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

const fetchData = async () => {
  try {
    const [scRes, aRes] = await Promise.all([
      api.get('/seat-classes/'),
      api.get('/airlines/')
    ]);
    seatClasses.value = scRes.data.results || scRes.data;
    airlines.value = aRes.data.results || aRes.data;

    if (route.query.page) {
        currentPage.value = parseInt(route.query.page);
    }

    if (route.query.highlight) {
        const hId = parseInt(route.query.highlight);
        highlightedId.value = hId;

        // Auto-navigate to the correct page for this ID
        const index = seatClasses.value.findIndex(sc => sc.id === hId);
        if (index !== -1) {
            currentPage.value = Math.floor(index / itemsPerPage) + 1;
        }

        setTimeout(() => {
            const el = document.getElementById(`seatclass-row-${hId}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => { highlightedId.value = null; }, 3000);
        }, 500);
    }
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

const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const goToPage = (p) => { if (p !== '...') currentPage.value = p; };

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
</style>
