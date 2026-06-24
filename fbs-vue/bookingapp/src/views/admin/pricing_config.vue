<template>
  <div class="p-6 poppins">
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-8 max-w-3xl mx-auto">
      <div class="flex items-center gap-4 mb-8 pb-6 border-b">
        <div class="w-12 h-12 rounded-full bg-pink-100 flex items-center justify-center">
          <i class="ph ph-sliders text-[#fe3787] text-2xl"></i>
        </div>
        <div>
          <h2 class="text-xl font-bold text-[#002D1E] poppins">Dynamic Pricing Configuration</h2>
          <p class="text-sm text-gray-500">Adjust multipliers that affect live flight prices in real-time.</p>
        </div>
      </div>

      <div v-if="loading" class="text-center py-10 text-gray-400 italic">Loading configuration...</div>
      <form v-else @submit.prevent="saveConfig" class="space-y-6">
        <!-- Occupancy Factors -->
        <div>
          <p class="text-[10px] font-black uppercase text-gray-400 tracking-widest poppins mb-4">Occupancy-Based Pricing</p>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div v-for="f in occupancyFields" :key="f.key">
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">{{ f.label }}</label>
              <input v-model="form[f.key]" type="number" step="0.01" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]">
              <p class="text-[10px] text-gray-400 mt-1">{{ f.hint }}</p>
            </div>
          </div>
        </div>
        <!-- Thresholds -->
        <div>
          <p class="text-[10px] font-black uppercase text-gray-400 tracking-widest poppins mb-4">Threshold Settings</p>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div v-for="f in thresholdFields" :key="f.key">
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">{{ f.label }}</label>
              <input v-model="form[f.key]" type="number" step="0.01" min="0" max="1" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]">
              <p class="text-[10px] text-gray-400 mt-1">{{ f.hint }}</p>
            </div>
          </div>
        </div>
        <div class="flex justify-end pt-4 border-t">
          <button type="submit" :disabled="saving" class="bg-[#fe3787] text-white px-8 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins">
            {{ saving ? 'Saving...' : 'Save Configuration' }}
          </button>
        </div>
        <p v-if="saved" class="text-green-600 text-sm font-semibold text-right animate-pulse">✓ Configuration saved successfully!</p>
      </form>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/admin/api';

const form = ref({});
const loading = ref(true);
const saving = ref(false);
const saved = ref(false);
const configId = ref(null);

const occupancyFields = [
  { key: 'occupancy_factor_high', label: 'High Occupancy Factor', hint: 'Multiplier when > high threshold' },
  { key: 'occupancy_factor_medium', label: 'Medium Occupancy Factor', hint: 'Multiplier when > medium threshold' },
  { key: 'occupancy_factor_low', label: 'Low Occupancy Factor', hint: 'Multiplier when < low threshold' },
];
const thresholdFields = [
  { key: 'occupancy_high_threshold', label: 'High Threshold', hint: 'e.g. 0.8 = 80%' },
  { key: 'occupancy_medium_threshold', label: 'Medium Threshold', hint: 'e.g. 0.6 = 60%' },
  { key: 'occupancy_low_threshold', label: 'Low Threshold', hint: 'e.g. 0.2 = 20%' },
];

const fetchData = async () => {
  try {
    const res = await api.get('/pricing-config/');
    const data = res.data.results || res.data;
    if (data.length > 0) { form.value = { ...data[0] }; configId.value = data[0].id; }
  } catch(e) { console.error(e); }
  loading.value = false;
};
const saveConfig = async () => {
  saving.value = true;
  try {
    if (configId.value) await api.patch(`/pricing-config/${configId.value}/`, form.value);
    else { const res = await api.post('/pricing-config/', form.value); configId.value = res.data.id; }
    saved.value = true; setTimeout(() => saved.value = false, 3000);
  } catch(e) { alert('Error saving configuration.'); }
  saving.value = false;
};
onMounted(fetchData);
</script>
<style scoped>.poppins { font-family: 'Poppins', sans-serif; }</style>
