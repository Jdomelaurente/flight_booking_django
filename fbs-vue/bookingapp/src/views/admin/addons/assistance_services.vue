<template>
  <div class="p-6 poppins">
    <div class="flex justify-between items-center mb-6">
      <div class="flex gap-3">
        <select v-model="filterAirline" class="border p-2 text-sm bg-white outline-none focus:border-[#fe3787] rounded-[1px]">
          <option value="">All Airlines</option>
          <option v-for="a in airlines" :key="a.id" :value="a.id">{{ a.name }}</option>
        </select>
        <button @click="openModal()" class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold text-[14px] rounded-[1px] shadow-sm transition-all">
          <i class="ph ph-plus"></i> Add Service
        </button>
      </div>
    </div>
    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4">Service Name</th>
            <th class="px-6 py-4">Type</th>
            <th class="px-6 py-4">Airline</th>
            <th class="px-6 py-4 text-right">Price</th>
            <th class="px-6 py-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="s in filtered" :key="s.id" class="hover:bg-gray-50/50 transition-all text-[12px] font-medium">
            <td class="px-6 py-4 font-bold text-[#002D1E]">{{ s.name }}</td>
            <td class="px-6 py-4"><span class="px-2 py-0.5 bg-purple-100 text-purple-700 rounded-[1px] text-[10px] font-bold uppercase">{{ s.service_type }}</span></td>
            <td class="px-6 py-4 text-gray-500">{{ s.airline_name }}</td>
            <td class="px-6 py-4 text-right font-bold">{{ parseFloat(s.price) === 0 ? 'Free' : '₱' + parseFloat(s.price).toLocaleString() }}</td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="openModal(s)" class="text-green-600 hover:text-green-400 p-2 transition-colors"><i class="ph ph-pencil-simple text-lg"></i></button>
                <button @click="deleteItem(s.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors"><i class="ph ph-trash text-lg"></i></button>
              </div>
            </td>
          </tr>
          <tr v-if="!filtered.length"><td colspan="5" class="px-6 py-10 text-center text-gray-400 italic">No assistance services found.</td></tr>
        </tbody>
      </table>
    </div>
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E]">{{ isEditing ? 'Edit Service' : 'New Assistance Service' }}</h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black transition-colors"><i class="ph ph-x text-xl"></i></button>
        </div>
        <form @submit.prevent="saveItem" class="space-y-4">
          <div><label class="block text-[10px] font-bold uppercase text-gray-400 mb-1">Service Name</label>
            <input v-model="form.name" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required></div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="block text-[10px] font-bold uppercase text-gray-400 mb-1">Service Type</label>
              <select v-model="form.service_type" class="w-full border p-2 text-sm bg-white outline-none focus:border-[#fe3787] rounded-[1px]" required>
                <option value="wheelchair">Wheelchair</option>
                <option value="boarding">Pre-boarding</option>
                <option value="medical">Medical</option>
                <option value="deaf">Deaf Assistance</option>
                <option value="blind">Blind Assistance</option>
                <option value="other">Other</option>
              </select></div>
            <div><label class="block text-[10px] font-bold uppercase text-gray-400 mb-1">Airline</label>
              <select v-model="form.airline" class="w-full border p-2 text-sm bg-white outline-none focus:border-[#fe3787] rounded-[1px]" required>
                <option value="" disabled>Select</option>
                <option v-for="a in airlines" :key="a.id" :value="a.id">{{ a.name }}</option>
              </select></div>
          </div>
          <div><label class="block text-[10px] font-bold uppercase text-gray-400 mb-1">Price (0 = Free)</label>
            <input v-model="form.price" type="number" step="0.01" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]"></div>
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
import { ref, computed, onMounted } from 'vue';
import api from '@/services/admin/api';
import { useModalStore } from '@/stores/modal';
const modalStore = useModalStore();
const services = ref([]);
const airlines = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const filterAirline = ref('');
const form = ref({ name: '', service_type: 'wheelchair', airline: '', price: 0, is_available: true, display_order: 0 });
const filtered = computed(() => filterAirline.value ? services.value.filter(s => s.airline === filterAirline.value) : services.value);
const fetchData = async () => {
  const [r1, r2] = await Promise.all([api.get('/assistance-services/'), api.get('/airlines/')]);
  services.value = r1.data.results || r1.data;
  airlines.value = r2.data.results || r2.data;
};
const saveItem = async () => {
  const payload = { ...form.value, airline: parseInt(form.value.airline) };
  if (isEditing.value) await api.put(`/assistance-services/${currentId.value}/`, payload);
  else await api.post('/assistance-services/', payload);
  await fetchData(); isModalOpen.value = false;
};
const deleteItem = async (id) => {
  const ok = await modalStore.confirm({ title: 'Delete Service?', message: 'Are you sure?', variant: 'danger', confirmText: 'Delete', loadingText: 'Deleting...' });
  if (ok) { modalStore.setLoader(true); await api.delete(`/assistance-services/${id}/`); await fetchData(); modalStore.close(true); }
};
const openModal = (item = null) => {
  isEditing.value = !!item; currentId.value = item?.id || null;
  form.value = item ? { name: item.name, service_type: item.service_type, airline: item.airline, price: item.price, is_available: item.is_available, display_order: item.display_order } : { name: '', service_type: 'wheelchair', airline: '', price: 0, is_available: true, display_order: 0 };
  isModalOpen.value = true;
};
onMounted(fetchData);
</script>
<style scoped>.poppins { font-family: 'Poppins', sans-serif; }</style>
