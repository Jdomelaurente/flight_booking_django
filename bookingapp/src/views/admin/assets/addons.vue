<template>
  <div class="p-6 poppins">
    <!-- Header Section -->
    <div class="flex justify-between items-center mb-6">
      <button 
        @click="openModal()" 
        class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all"
      >
        <i class="ph ph-plus"></i> New Add-On
      </button>
    </div>

    <!-- Grid Section -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="item in addOns" :key="item.id" class="bg-white border border-gray-200 p-5 rounded-[1px] shadow-sm flex flex-col justify-between hover:shadow-md transition-all">
        <div>
          <div class="flex justify-between items-start mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-pink-100 flex items-center justify-center">
                <i class="ph ph-package text-[#fe3787] text-lg"></i>
              </div>
              <h3 class="font-bold text-[#002D1E] text-md poppins">{{ item.name }}</h3>
            </div>
            <div class="flex gap-2">
              <button @click="openModal(item)" class="text-green-600 hover:text-green-400 p-1 transition-colors">
                <i class="ph ph-pencil-simple text-lg"></i>
              </button>
              <button @click="deleteAddOn(item.id)" class="text-red-600 hover:text-red-400 p-1 transition-colors">
                <i class="ph ph-trash text-lg"></i>
              </button>
            </div>
          </div>
          <p class="text-gray-500 text-[12px] font-medium leading-relaxed poppins line-clamp-3">
            {{ item.description || 'No description provided.' }}
          </p>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-if="addOns.length === 0" class="col-span-full py-20 text-center bg-white border border-gray-200 border-dashed rounded-[1px]">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-50 rounded-full flex items-center justify-center">
          <i class="ph ph-package text-3xl text-gray-300"></i>
        </div>
        <p class="text-gray-400 poppins text-sm italic">No add-ons created yet. Click "New Add-On" to get started.</p>
      </div>
    </div>

    <!-- Modal Section -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">{{ isEditing ? 'Edit Service' : 'Create New Service' }}</h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveAddOn" class="space-y-4">
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Service Name</label>
            <input v-model="form.name" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="e.g. 20kg Extra Baggage" required>
          </div>
          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Description</label>
            <textarea v-model="form.description" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px] h-24" placeholder="Briefly describe what is included..."></textarea>
          </div>
          
          <div class="flex justify-end gap-3 pt-6 border-t mt-4">
            <button type="button" @click="isModalOpen = false" class="text-sm text-gray-500 font-medium hover:text-gray-700 poppins">Cancel</button>
            <button type="submit" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins">
              Save Service
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

const addOns = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const form = ref({ name: '', description: '' });

const fetchAddOns = async () => {
  try {
    const res = await api.get('/add-ons/');
    addOns.value = res.data.results || res.data;
  } catch (err) {
    console.error("Fetch Error:", err);
  }
};

const saveAddOn = async () => {
  try {
    if (isEditing.value) await api.put(`/add-ons/${currentId.value}/`, form.value);
    else await api.post('/add-ons/', form.value);
    await fetchAddOns();
    isModalOpen.value = false;
  } catch (err) { 
    console.error("Save Error:", err);
    alert("Error saving Add-On."); 
  }
};

const deleteAddOn = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Delete Service Type?',
    message: 'Are you sure you want to delete this service type?',
    variant: 'danger',
    confirmText: 'Delete',
    loadingText: 'Deleting...'
  });

  if (confirmed) {
    modalStore.setLoader(true);
    try {
      await api.delete(`/add-ons/${id}/`);
      await fetchAddOns();
      modalStore.close(true);
    } catch (err) {
      console.error("Delete Error:", err);
      modalStore.setLoader(false);
    }
  }
};

const openModal = (item = null) => {
  isEditing.value = !!item;
  currentId.value = item?.id || null;
  form.value = item ? { ...item } : { name: '', description: '' };
  isModalOpen.value = true;
};

onMounted(fetchAddOns);
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

.poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
