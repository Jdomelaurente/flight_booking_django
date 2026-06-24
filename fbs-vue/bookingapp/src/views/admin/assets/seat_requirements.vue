<template>
  <div class="p-6 poppins">
    <!-- Header & Tools Section -->
    <AdminTableTool 
      v-model="searchQuery" 
      placeholder="Search requirement name or code..."
    >
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
            <th class="px-6 py-4 poppins">Icon</th>
            <th class="px-6 py-4 poppins">Name</th>
            <th class="px-6 py-4 poppins">Code</th>
            <th class="px-6 py-4 poppins text-right">Price</th>
            <th class="px-6 py-4 poppins text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr 
            v-for="req in paginatedRequirements" 
            :key="req.id" 
            :id="`requirement-row-${req.id}`"
            :class="{'highlight-active': highlightedId === req.id}"
            class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium"
          >
            <td class="px-6 py-4">
              <div class="w-10 h-10 bg-gray-50 border border-gray-100 rounded-[1px] flex items-center justify-center">
                <i :class="[formatIcon(req.icon), 'text-[#fe3787] text-xl']"></i>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="font-bold text-[#002D1E] poppins text-sm">{{ req.name }}</div>
              <div class="text-[10px] text-gray-400 poppins truncate max-w-[200px]">{{ req.description }}</div>
            </td>
            <td class="px-6 py-4">
               <span class="font-mono text-[10px] bg-gray-100 text-gray-500 px-2 py-1 rounded-[1px] uppercase tracking-wider">
                 {{ req.code }}
               </span>
            </td>
            <td class="px-6 py-4 text-right">
              <span class="font-bold text-[#fe3787] poppins text-sm">₱{{ formatPrice(req.price) }}</span>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="openModal(req)" class="text-green-600 hover:text-green-400 p-2 transition-colors">
                  <i class="ph ph-pencil-simple text-lg"></i>
                </button>
                <button @click="deleteRequirement(req.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors">
                  <i class="ph ph-trash text-lg"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="requirements.length === 0">
            <td colspan="5" class="px-6 py-10 text-center text-gray-400 italic poppins">
              No seat requirements found. Add one to get started!
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination Section -->
      <div v-if="requirements.length > itemsPerPage" class="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
        <div class="flex items-center justify-between">
          <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
            Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ requirements.length }}
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
          <h2 class="text-lg font-bold text-[#002D1E] poppins">{{ isEditing ? 'Edit Requirement' : 'Add Requirement' }}</h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>

        <form @submit.prevent="saveRequirement" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Name</label>
              <input v-model="form.name" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="e.g. Extra Legroom" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Code</label>
              <input v-model="form.code" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="e.g. has_extra_legroom" required>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Price (₱)</label>
              <input v-model.number="form.price" type="number" step="0.01" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Icon (Phospor Class)</label>
              <div class="flex gap-2">
                <input v-model="form.icon" type="text" class="flex-1 border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="ph ph-star">
                <div class="w-10 h-10 bg-gray-50 border border-gray-200 flex items-center justify-center rounded-[1px]">
                  <i :class="[formatIcon(form.icon), 'text-[#fe3787]']"></i>
                </div>
              </div>
            </div>
          </div>

          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Description</label>
            <textarea v-model="form.description" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px] h-24" placeholder="Describe this requirement..."></textarea>
          </div>

          <div class="flex justify-end gap-3 pt-6 border-t mt-4">
            <button type="button" @click="isModalOpen = false" class="text-sm text-gray-500 font-medium hover:text-gray-700 poppins">Cancel</button>
            <button type="submit" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins">
              {{ isEditing ? 'Update Requirement' : 'Save Requirement' }}
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

// State
const requirements = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const highlightedId = ref(null);
const route = useRoute();
const searchQuery = ref('');

// Pagination State
const currentPage = ref(1);
const itemsPerPage = 10;
const form = ref({
  name: '',
  code: '',
  price: 0,
  icon: 'ph ph-star',
  description: ''
});

// Search Logic
const filteredRequirements = computed(() => {
  if (!searchQuery.value) return requirements.value;
  const q = searchQuery.value.toLowerCase();
  return requirements.value.filter(r => 
    r.name.toLowerCase().includes(q) || 
    r.code.toLowerCase().includes(q)
  );
});

// Pagination Logic
const totalPages = computed(() => Math.ceil(filteredRequirements.value.length / itemsPerPage));
const paginatedRequirements = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return filteredRequirements.value.slice(start, start + itemsPerPage);
});
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage);
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredRequirements.value.length));

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

const fetchRequirements = async () => {
  try {
    const res = await api.get('/seat-requirements/');
    requirements.value = res.data.results || res.data || [];

    if (route.query.page) {
        currentPage.value = parseInt(route.query.page);
    }

    if (route.query.highlight) {
        const hId = parseInt(route.query.highlight);
        highlightedId.value = hId;

        // Auto-navigate to the correct page for this ID
        const index = requirements.value.findIndex(r => r.id === hId);
        if (index !== -1) {
            currentPage.value = Math.floor(index / itemsPerPage) + 1;
        }

        setTimeout(() => {
            const el = document.getElementById(`requirement-row-${hId}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => { highlightedId.value = null; }, 3000);
        }, 500);
    }
  } catch (err) {
    console.error('Failed to fetch requirements:', err);
  }
};

const saveRequirement = async () => {
  try {
    if (isEditing.value) {
      await api.put(`/seat-requirements/${currentId.value}/`, form.value);
    } else {
      await api.post('/seat-requirements/', form.value);
    }
    await fetchRequirements();
    isModalOpen.value = false;
  } catch (err) {
    console.error("Save Error:", err);
    alert("Error saving: " + JSON.stringify(err.response?.data || err.message));
  }
};

const deleteRequirement = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Delete Requirement?',
    message: 'Are you sure you want to delete this seat requirement? This might affect existing seat configurations.',
    variant: 'danger',
    confirmText: 'Delete',
    loadingText: 'Deleting...'
  });

  if (confirmed) {
    modalStore.setLoader(true);
    try {
      await api.delete(`/seat-requirements/${id}/`);
      await fetchRequirements();
      modalStore.close(true);
    } catch (err) {
      console.error("Delete Error:", err);
      alert("Error deleting: " + JSON.stringify(err.response?.data || err.message));
      modalStore.setLoader(false);
    }
  }
};

const openModal = (req = null) => {
  isEditing.value = !!req;
  currentId.value = req?.id || null;
  form.value = req ? { ...req } : {
    name: '',
    code: '',
    price: 0,
    icon: 'ph ph-star',
    description: ''
  };
  isModalOpen.value = true;
};

const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const goToPage = (p) => { if (p !== '...') currentPage.value = p; };

const formatPrice = (price) => {
  return parseFloat(price).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

const formatIcon = (iconClass) => {
  if (!iconClass) return 'ph ph-star';
  if (iconClass.startsWith('ph-') && !iconClass.includes(' ')) {
    return `ph ${iconClass}`;
  }
  return iconClass;
};

onMounted(fetchRequirements);
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

.poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
