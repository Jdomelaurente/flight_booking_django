<template>
  <div class="p-6 poppins">
    <div class="flex justify-between items-center mb-6">
      <button @click="openModal()" class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold text-[14px] rounded-[1px] shadow-sm transition-all">
        <i class="ph ph-plus"></i> Add Plan
      </button>
    </div>
    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4">Plan Name</th>
            <th class="px-6 py-4">Provider</th>
            <th class="px-6 py-4 text-right">Retail Price</th>
            <th class="px-6 py-4 text-center">Status</th>
            <th class="px-6 py-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="p in plans" :key="p.id" class="hover:bg-gray-50/50 transition-all text-[12px] font-medium">
            <td class="px-6 py-4 font-bold text-[#002D1E]">{{ p.name }}</td>
            <td class="px-6 py-4 text-gray-500">{{ p.provider_name }}</td>
            <td class="px-6 py-4 text-right font-bold text-[#002D1E]">₱{{ parseFloat(p.retail_price).toLocaleString() }}</td>
            <td class="px-6 py-4 text-center">
              <span :class="p.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'" class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase">{{ p.is_active ? 'Active' : 'Inactive' }}</span>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="openModal(p)" class="text-green-600 hover:text-green-400 p-2 transition-colors"><i class="ph ph-pencil-simple text-lg"></i></button>
                <button @click="deleteItem(p.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors"><i class="ph ph-trash text-lg"></i></button>
              </div>
            </td>
          </tr>
          <tr v-if="!plans.length"><td colspan="5" class="px-6 py-10 text-center text-gray-400 italic">No insurance plans found.</td></tr>
        </tbody>
      </table>
    </div>
    <!-- Modal -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E]">{{ isEditing ? 'Edit Plan' : 'New Insurance Plan' }}</h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black transition-colors"><i class="ph ph-x text-xl"></i></button>
        </div>
        <form @submit.prevent="saveItem" class="space-y-4">
          <div><label class="block text-[10px] font-bold uppercase text-gray-400 mb-1">Plan Name</label>
            <input v-model="form.name" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required></div>
          <div><label class="block text-[10px] font-bold uppercase text-gray-400 mb-1">Provider</label>
            <select v-model="form.provider" class="w-full border p-2 text-sm bg-white outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
              <option value="" disabled>Select Provider</option>
              <option v-for="pv in providers" :key="pv.id" :value="pv.id">{{ pv.name }}</option>
            </select></div>
          <div><label class="block text-[10px] font-bold uppercase text-gray-400 mb-1">Retail Price (PHP)</label>
            <input v-model="form.retail_price" type="number" step="0.01" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required></div>
          <div class="flex items-center gap-2">
            <input v-model="form.is_active" type="checkbox" class="h-4 w-4 text-pink-500">
            <label class="text-sm text-gray-600">Active</label>
          </div>
          <div class="flex justify-end gap-3 pt-4 border-t">
            <button type="button" @click="isModalOpen = false" class="text-sm text-gray-500 hover:text-gray-700">Cancel</button>
            <button type="submit" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px]">Save</button>
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
const plans = ref([]);
const providers = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const form = ref({ name: '', provider: '', retail_price: 0, is_active: true, display_order: 0 });
const fetchData = async () => {
  const [r1, r2] = await Promise.all([api.get('/insurance-plans/'), api.get('/insurance-providers/')]);
  plans.value = r1.data.results || r1.data;
  providers.value = r2.data.results || r2.data;
};
const saveItem = async () => {
  const payload = { ...form.value, provider: parseInt(form.value.provider) };
  if (isEditing.value) await api.put(`/insurance-plans/${currentId.value}/`, payload);
  else await api.post('/insurance-plans/', payload);
  await fetchData(); isModalOpen.value = false;
};
const deleteItem = async (id) => {
  const ok = await modalStore.confirm({ title: 'Delete Plan?', message: 'Are you sure?', variant: 'danger', confirmText: 'Delete', loadingText: 'Deleting...' });
  if (ok) { modalStore.setLoader(true); await api.delete(`/insurance-plans/${id}/`); await fetchData(); modalStore.close(true); }
};
const openModal = (item = null) => {
  isEditing.value = !!item; currentId.value = item?.id || null;
  form.value = item ? { name: item.name, provider: item.provider, retail_price: item.retail_price, is_active: item.is_active, display_order: item.display_order } : { name: '', provider: '', retail_price: 0, is_active: true, display_order: 0 };
  isModalOpen.value = true;
};
onMounted(fetchData);
</script>
<style scoped>.poppins { font-family: 'Poppins', sans-serif; }</style>
