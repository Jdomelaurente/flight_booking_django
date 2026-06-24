<template>
  <div class="p-6 poppins">
    <div class="flex justify-between items-center mb-6">
      <div class="flex gap-3">
        <select v-model="filterAirline" class="border p-2 text-sm bg-white outline-none focus:border-[#fe3787] rounded-[1px]">
          <option value="">All Airlines</option>
          <option v-for="a in airlines" :key="a.id" :value="a.id">{{ a.name }}</option>
        </select>
        <button @click="openModal()" class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold text-[14px] rounded-[1px] shadow-sm transition-all">
          <i class="ph ph-plus"></i> Add Meal
        </button>
      </div>
    </div>
    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4">Meal Name</th>
            <th class="px-6 py-4">Type</th>
            <th class="px-6 py-4">Airline</th>
            <th class="px-6 py-4 text-right">Price</th>
            <th class="px-6 py-4 text-center">Available</th>
            <th class="px-6 py-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="m in filteredMeals" :key="m.id" class="hover:bg-gray-50/50 transition-all text-[12px] font-medium">
            <td class="px-6 py-4 font-bold text-[#002D1E]">{{ m.name }}</td>
            <td class="px-6 py-4"><span class="px-2 py-0.5 bg-orange-100 text-orange-700 rounded-[1px] text-[10px] font-bold uppercase">{{ m.meal_type }}</span></td>
            <td class="px-6 py-4 text-gray-500">{{ m.airline_name }}</td>
            <td class="px-6 py-4 text-right font-bold">{{ parseFloat(m.price) === 0 ? 'Free' : '₱' + parseFloat(m.price).toLocaleString() }}</td>
            <td class="px-6 py-4 text-center">
              <span :class="m.is_available ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'" class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase">{{ m.is_available ? 'Yes' : 'No' }}</span>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="openModal(m)" class="text-green-600 hover:text-green-400 p-2 transition-colors"><i class="ph ph-pencil-simple text-lg"></i></button>
                <button @click="deleteItem(m.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors"><i class="ph ph-trash text-lg"></i></button>
              </div>
            </td>
          </tr>
          <tr v-if="!filteredMeals.length"><td colspan="6" class="px-6 py-10 text-center text-gray-400 italic">No meals found.</td></tr>
        </tbody>
      </table>
    </div>
    <!-- Modal -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-md p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E]">{{ isEditing ? 'Edit Meal Option' : 'New Meal Option' }}</h2>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-black transition-colors"><i class="ph ph-x text-xl"></i></button>
        </div>
        <form @submit.prevent="saveItem" class="space-y-4">
          <div><label class="block text-[10px] font-bold uppercase text-gray-400 mb-1">Meal Name</label>
            <input v-model="form.name" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required></div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="block text-[10px] font-bold uppercase text-gray-400 mb-1">Meal Type</label>
              <select v-model="form.meal_type" class="w-full border p-2 text-sm bg-white outline-none focus:border-[#fe3787] rounded-[1px]" required>
                <option value="standard">Standard</option>
                <option value="vegetarian">Vegetarian</option>
                <option value="vegan">Vegan</option>
                <option value="halal">Halal</option>
                <option value="kosher">Kosher</option>
                <option value="diabetic">Diabetic</option>
              </select></div>
            <div><label class="block text-[10px] font-bold uppercase text-gray-400 mb-1">Airline</label>
              <select v-model="form.airline" class="w-full border p-2 text-sm bg-white outline-none focus:border-[#fe3787] rounded-[1px]" required>
                <option value="" disabled>Select</option>
                <option v-for="a in airlines" :key="a.id" :value="a.id">{{ a.name }}</option>
              </select></div>
          </div>
          <div><label class="block text-[10px] font-bold uppercase text-gray-400 mb-1">Price (0 = Free)</label>
            <input v-model="form.price" type="number" step="0.01" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]"></div>
          <div class="flex items-center gap-2">
            <input v-model="form.is_available" type="checkbox" class="h-4 w-4 text-pink-500">
            <label class="text-sm text-gray-600">Available</label>
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
import { ref, computed, onMounted } from 'vue';
import api from '@/services/admin/api';
import { useModalStore } from '@/stores/modal';
const modalStore = useModalStore();
const meals = ref([]);
const airlines = ref([]);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const filterAirline = ref('');
const form = ref({ name: '', meal_type: 'standard', airline: '', price: 0, is_available: true, display_order: 0 });

const filteredMeals = computed(() => filterAirline.value ? meals.value.filter(m => m.airline === filterAirline.value) : meals.value);

const fetchData = async () => {
  const [r1, r2] = await Promise.all([api.get('/meal-options/'), api.get('/airlines/')]);
  meals.value = r1.data.results || r1.data;
  airlines.value = r2.data.results || r2.data;
};
const saveItem = async () => {
  const payload = { ...form.value, airline: parseInt(form.value.airline) };
  if (isEditing.value) await api.put(`/meal-options/${currentId.value}/`, payload);
  else await api.post('/meal-options/', payload);
  await fetchData(); isModalOpen.value = false;
};
const deleteItem = async (id) => {
  const ok = await modalStore.confirm({ title: 'Delete Meal Option?', message: 'Are you sure?', variant: 'danger', confirmText: 'Delete', loadingText: 'Deleting...' });
  if (ok) { modalStore.setLoader(true); await api.delete(`/meal-options/${id}/`); await fetchData(); modalStore.close(true); }
};
const openModal = (item = null) => {
  isEditing.value = !!item; currentId.value = item?.id || null;
  form.value = item ? { name: item.name, meal_type: item.meal_type, airline: item.airline, price: item.price, is_available: item.is_available, display_order: item.display_order } : { name: '', meal_type: 'standard', airline: '', price: 0, is_available: true, display_order: 0 };
  isModalOpen.value = true;
};
onMounted(fetchData);
</script>
<style scoped>.poppins { font-family: 'Poppins', sans-serif; }</style>
