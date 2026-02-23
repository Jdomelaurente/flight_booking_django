<template>
  <div class="p-6 poppins">
    <!-- Header Section -->
    <div class="flex justify-between items-center mb-6">
      <button 
        @click="openModal()" 
        class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all"
      >
        <i class="ph ph-plus"></i> Add Requirement
      </button>
    </div>

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
          <tr v-for="req in requirements" :key="req.id" class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium">
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
import { ref, onMounted } from 'vue';
import api from '@/services/admin/api';
import { useModalStore } from '@/stores/modal';

const modalStore = useModalStore();

// Requirements state
const requirements = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const form = ref({
  name: '',
  code: '',
  price: 0,
  icon: 'ph ph-star',
  description: ''
});

const fetchRequirements = async () => {
  try {
    const res = await api.get('/seat-requirements/');
    requirements.value = res.data.results || res.data || [];
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
