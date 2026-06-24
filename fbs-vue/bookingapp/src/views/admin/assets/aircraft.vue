<template>
  <div class="p-6 poppins">
    <!-- Header & Tools Section -->
    <AdminTableTool 
      v-model="searchQuery" 
      placeholder="Search aircraft model or fleet ID..."
    >
      <template #filters>
        <div class="flex items-center gap-2">
          <select 
            v-model="filterAirline"
            class="text-[11px] font-bold border border-gray-200 px-3 py-2 bg-white rounded-[1px] outline-none focus:border-[#fe3787] poppins cursor-pointer"
          >
            <option value="all">Any Airline</option>
            <option v-for="airline in airlines" :key="airline.id" :value="airline.id">
              {{ airline.name }}
            </option>
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

    <!-- Import Modal -->
    <ImportModal 
      :show="showImportModal" 
      title="Aircraft" 
      model-type="aircrafts" 
      @close="showImportModal = false"
      @refresh="fetchData"
    />

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
          <tr 
            v-for="plane in paginatedAircraft" 
            :key="plane.id" 
            :id="`aircraft-row-${plane.id}`"
            :class="{'highlight-active': highlightedId === plane.id}"
            class="hover:bg-gray-50/50 transition-all text-[12px] font-medium"
          >
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <i class="ph ph-airplane text-blue-600"></i>
                </div>
                <div>
                  <span class="font-bold text-[#002D1E] poppins block">{{ plane.model }}</span>
                  <div class="flex items-center gap-1 mt-1">
                    <span class="text-[9px] text-gray-400 font-bold uppercase poppins">Fleet ID: {{ plane.id }}</span>
                    <div class="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></div>
                  </div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
               <router-link 
                 :to="{ name: 'AdminAirlines', query: { highlight: plane.airline } }"
                 class="bg-gray-100 text-gray-600 px-3 py-1 rounded-[1px] text-[10px] font-bold uppercase poppins hover:bg-[#fe3787] hover:text-white transition-all inline-block"
                 title="View Airline Connection"
               >
                 {{ plane.airline_name || 'Unassigned' }}
               </router-link>
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

      <!-- Pagination Section -->
      <div v-if="aircraftList.length > itemsPerPage" class="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
        <div class="flex items-center justify-between">
          <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
            Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ aircraftList.length }}
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
          <h2 class="text-lg font-bold text-[#002D1E] poppins">{{ isEditing ? 'Edit Aircraft' : 'Register New Aircraft' }}</h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveAircraft" class="space-y-4">
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Airline Owner</label>
            <SearchableSelect
              v-model="form.airline"
              :options="airlineOptions"
              placeholder="Search and select airline..."
              label="Airline"
            />
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
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/services/admin/api';
import { useModalStore } from '@/stores/modal';
import SearchableSelect from '@/components/admin/SearchableSelect.vue';
import AdminTableTool from '@/components/admin/AdminTableTool.vue';
import ImportModal from '@/components/admin/ImportModal.vue';

const modalStore = useModalStore();

const aircraftList = ref([]);
const showImportModal = ref(false);
const airlines = ref([]);

const airlineOptions = computed(() =>
  airlines.value.map(a => ({ value: a.id, label: a.name, sublabel: `IATA: ${a.code}` }))
);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const highlightedId = ref(null);
const route = useRoute();
const searchQuery = ref('');
const filterAirline = ref('all');

// Pagination State
const currentPage = ref(1);
const itemsPerPage = 10;

const form = ref({ model: '', capacity: 0, airline: '' });

// Search & Filter Logic
const filteredAircraft = computed(() => {
  let result = aircraftList.value;
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(a => 
      a.model.toLowerCase().includes(q) || 
      String(a.id).includes(q) ||
      (a.airline_name && a.airline_name.toLowerCase().includes(q))
    );
  }

  if (filterAirline.value !== 'all') {
    result = result.filter(a => a.airline === filterAirline.value);
  }
  
  return result;
});

// Pagination Logic
const totalPages = computed(() => Math.ceil(filteredAircraft.value.length / itemsPerPage));
const paginatedAircraft = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return filteredAircraft.value.slice(start, start + itemsPerPage);
});
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage);
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredAircraft.value.length));

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
    const [planeRes, airlineRes] = await Promise.all([
      api.get('/aircraft/'),
      api.get('/airlines/')
    ]);
    aircraftList.value = planeRes.data.results || planeRes.data;
    airlines.value = airlineRes.data.results || airlineRes.data;

    if (route.query.page) {
        currentPage.value = parseInt(route.query.page);
    }

    if (route.query.highlight) {
        const hId = parseInt(route.query.highlight);
        highlightedId.value = hId;

        // Auto-navigate to the correct page for this ID
        const index = aircraftList.value.findIndex(a => a.id === hId);
        if (index !== -1) {
            currentPage.value = Math.floor(index / itemsPerPage) + 1;
        }

        setTimeout(() => {
            const el = document.getElementById(`aircraft-row-${hId}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => { highlightedId.value = null; }, 3000);
        }, 500);
    }
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
  const confirmed = await modalStore.confirm({
    title: 'Decommission Aircraft?',
    message: 'Are you sure you want to remove this aircraft from the fleet?',
    variant: 'danger',
    confirmText: 'Remove',
    loadingText: 'Removing...'
  });

  if (confirmed) {
    modalStore.setLoader(true);
    try {
      await api.delete(`/aircraft/${id}/`);
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
