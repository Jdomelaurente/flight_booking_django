<template>
  <div class="p-6 poppins">
    <!-- Header & Tools Section -->
    <AdminTableTool 
      v-model="searchQuery" 
      placeholder="Search airports, codes or city..."
    >
      <template #filters>
        <div class="flex items-center gap-2">
          <select 
            v-model="filterType"
            class="text-[11px] font-bold border border-gray-200 px-3 py-2 bg-white rounded-[1px] outline-none focus:border-[#fe3787] poppins cursor-pointer"
          >
            <option value="all">Any Type</option>
            <option value="domestic">Domestic</option>
            <option value="international">International</option>
          </select>
        </div>
      </template>
      <template #actions>
        <div class="flex items-center gap-2">
          <button 
            @click="showImportModal = true" 
            class="bg-[#002D1E] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#014d33] font-semibold poppins text-[12px] rounded-[1px] shadow-sm transition-all"
          >
            <i class="ph ph-file-csv text-[14px]"></i> Import
          </button>
          <button 
            @click="openModal()" 
            class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[12px] rounded-[1px] shadow-sm transition-all"
          >
            <i class="ph ph-plus text-[14px]"></i> Add
          </button>
        </div>
      </template>
    </AdminTableTool>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      <div class="bg-white border border-gray-200 p-6 rounded-[1px] shadow-sm flex items-center justify-between">
        <div>
          <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest block mb-1">Total Airports</span>
          <span class="text-3xl font-black text-[#002D1E]">{{ airports.length }}</span>
        </div>
        <div class="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center text-blue-600">
          <i class="ph ph-buildings text-2xl"></i>
        </div>
      </div>
      
      <div class="bg-white border border-gray-200 p-6 rounded-[1px] shadow-sm flex items-center justify-between">
        <div>
          <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest block mb-1">International Airports</span>
          <span class="text-3xl font-black text-purple-600">{{ airports.filter(a => a.airport_type === 'international').length }}</span>
        </div>
        <div class="w-12 h-12 rounded-full bg-purple-50 flex items-center justify-center text-purple-600">
          <i class="ph ph-globe text-2xl"></i>
        </div>
      </div>

      <div class="bg-white border border-gray-200 p-6 rounded-[1px] shadow-sm flex items-center justify-between">
        <div>
          <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest block mb-1">Domestic Airports</span>
          <span class="text-3xl font-black text-green-600">{{ airports.filter(a => a.airport_type === 'domestic').length }}</span>
        </div>
        <div class="w-12 h-12 rounded-full bg-green-50 flex items-center justify-center text-green-600">
          <i class="ph ph-map-pin text-2xl"></i>
        </div>
      </div>
    </div>

    <!-- Import Modal -->
    <ImportModal 
      :show="showImportModal" 
      title="Airports" 
      model-type="airports" 
      @close="showImportModal = false"
      @refresh="fetchAirports"
    />

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
          <tr 
            v-for="airport in paginatedAirports" 
            :key="airport.id" 
            :id="`airport-row-${airport.id}`"
            :class="{'highlight-active': highlightedId === airport.id}"
            class="hover:bg-gray-50/50 transition-all text-[12px] font-medium"
          >
            <td class="px-6 py-4">
              <div class="flex items-center gap-2">
                <span class="font-bold text-[#fe3787] poppins text-sm block">{{ airport.code }}</span>
                <div class="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" title="System Connected"></div>
              </div>
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

      <!-- Pagination Section -->
      <div v-if="airports.length > itemsPerPage" class="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
        <div class="flex items-center justify-between">
          <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
            Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ airports.length }}
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
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/admin/api';
import { useModalStore } from '@/stores/modal';
import ImportModal from '@/components/admin/ImportModal.vue';
import AdminTableTool from '@/components/admin/AdminTableTool.vue';

const modalStore = useModalStore();

// State
const airports = ref([]);
const isModalOpen = ref(false);
const showImportModal = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const highlightedId = ref(null);
const route = useRoute();
const searchQuery = ref('');
const filterType = ref('all');

// Pagination State
const currentPage = ref(1);
const itemsPerPage = 10;

const form = ref({
  name: '',
  code: '',
  city: '',
  location: '',
  airport_type: 'domestic'
});

// Search & Filter Logic
const filteredAirports = computed(() => {
  let result = airports.value;
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(a => 
      a.name.toLowerCase().includes(q) || 
      a.code.toLowerCase().includes(q) || 
      a.city.toLowerCase().includes(q) ||
      (a.country_name && a.country_name.toLowerCase().includes(q))
    );
  }

  if (filterType.value !== 'all') {
    result = result.filter(a => a.airport_type === filterType.value);
  }
  
  return result;
});

// Pagination Logic
const totalPages = computed(() => Math.ceil(filteredAirports.value.length / itemsPerPage));
const paginatedAirports = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return filteredAirports.value.slice(start, start + itemsPerPage);
});
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage);
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredAirports.value.length));

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

// Fetch Data
const fetchAirports = async () => {
  try {
    const res = await api.get('/airports/');
    airports.value = res.data.results || res.data;

    if (route.query.page) {
        currentPage.value = parseInt(route.query.page);
    }

    if (route.query.highlight) {
        const hId = parseInt(route.query.highlight);
        highlightedId.value = hId;

        // Auto-navigate to the correct page for this ID
        const index = airports.value.findIndex(a => a.id === hId);
        if (index !== -1) {
            currentPage.value = Math.floor(index / itemsPerPage) + 1;
        }

        setTimeout(() => {
            const el = document.getElementById(`airport-row-${hId}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => { highlightedId.value = null; }, 3000);
        }, 500);
    }
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
  const confirmed = await modalStore.confirm({
    title: 'Delete Airport?',
    message: 'Are you sure you want to delete this airport? This may affect existing routes.',
    variant: 'danger',
    confirmText: 'Delete',
    loadingText: 'Deleting...'
  });

  if (confirmed) {
    modalStore.setLoader(true);
    try {
      await api.delete(`/airports/${id}/`);
      airports.value = airports.value.filter(a => a.id !== id);
      modalStore.close(true);
    } catch (err) {
      console.error("Delete error:", err.response?.data);
      modalStore.setLoader(false);
      alert("Delete failed. This airport might be in use.");
    }
  }
};

const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const goToPage = (p) => { if (p !== '...') currentPage.value = p; };

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
