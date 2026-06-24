<template>
  <div v-if="show" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-[#002D1E]/40 backdrop-blur-sm poppins">
    <div class="bg-white rounded-[1px] shadow-2xl w-full max-w-md overflow-hidden border border-gray-100 animate-in fade-in zoom-in duration-300">
      
      <!-- Header -->
      <div class="bg-gradient-to-r from-[#002D1E] to-[#014d33] p-6 text-white relative">
        <div class="absolute -right-6 -top-6 w-24 h-24 bg-[#fe3787] rounded-full blur-3xl opacity-20"></div>
        <h3 class="text-xl font-black flex items-center gap-2 relative">
          <i class="ph ph-file-csv text-2xl text-[#fe3787]"></i>
          Import {{ title }}
        </h3>
        <p class="text-xs text-white/60 mt-1 uppercase tracking-widest font-bold">Bulk Upload via CSV</p>
      </div>

      <div class="p-8">
        <!-- Success State -->
        <div v-if="importResult" class="text-center space-y-4 py-4 animate-in slide-in-from-bottom-4 duration-500">
          <div class="w-20 h-20 bg-emerald-50 text-emerald-500 rounded-full flex items-center justify-center mx-auto border border-emerald-100">
            <i class="ph ph-check-circle text-5xl"></i>
          </div>
          <div>
            <h4 class="text-lg font-black text-[#002D1E]">Import Successful</h4>
            <p class="text-sm text-gray-500 mt-1">
              Successfully processed <span class="font-bold text-emerald-600">{{ importResult.success_count }}</span> records.
            </p>
            <p v-if="importResult.error_count > 0" class="text-xs text-rose-500 mt-2 font-medium">
              Note: {{ importResult.error_count }} rows had errors.
            </p>
          </div>
          
          <div v-if="importResult.errors.length > 0" class="bg-rose-50 p-4 text-left rounded-[1px] border border-rose-100 max-h-32 overflow-y-auto">
            <p class="text-[10px] uppercase font-black text-rose-400 mb-2">Error Log (Preview)</p>
            <ul class="text-[11px] text-rose-700 space-y-1">
              <li v-for="(err, i) in importResult.errors" :key="i" class="flex gap-2">
                <span class="font-bold shrink-0">•</span>
                <span>{{ err }}</span>
              </li>
            </ul>
          </div>

          <button 
            v-if="importResult.error_count > 0"
            @click="downloadDetailedErrorReport" 
            class="w-full py-3 bg-rose-50 text-rose-600 font-black text-[10px] uppercase tracking-widest hover:bg-rose-100 transition-colors mt-2 flex items-center justify-center gap-2 border border-rose-200"
          >
            <i class="ph ph-warning-circle text-sm"></i>
            Download Detailed Failure Report (.CSV)
          </button>

          <button @click="close" class="w-full py-3 bg-[#002D1E] text-white font-black text-sm uppercase tracking-widest hover:bg-[#014d33] transition-colors mt-4">
            Close & Refresh
          </button>
        </div>

        <!-- Initial Upload State -->
        <div v-else class="space-y-6">
          <div 
            class="group border-2 border-dashed border-gray-200 rounded-[1px] p-10 text-center transition-all hover:border-[#fe3787]/50 hover:bg-pink-50/20 cursor-pointer relative overflow-hidden"
            @dragover.prevent="dragOver = true"
            @dragleave.prevent="dragOver = false"
            @drop.prevent="onDrop"
            @click="triggerFileInput"
            :class="dragOver ? 'border-[#fe3787] bg-pink-50/50' : ''"
          >
            <input type="file" ref="fileInput" class="hidden" accept=".csv" @change="onFileChange">
            
            <i class="ph ph-cloud-arrow-up text-5xl transition-transform group-hover:-translate-y-2 duration-300" 
               :class="selectedFile ? 'text-emerald-500' : 'text-gray-300'"></i>
            
            <p class="text-sm font-bold text-[#002D1E] mt-4">
              {{ selectedFile ? selectedFile.name : 'Click or drag CSV file here' }}
            </p>
            <p class="text-[10px] text-gray-400 mt-1 uppercase tracking-widest font-black">Max size: 5MB</p>
          </div>

          <div class="bg-blue-50/50 p-4 border border-blue-100 flex gap-3 relative overflow-hidden group">
             <div class="absolute -right-2 -bottom-2 opacity-10 group-hover:rotate-12 transition-transform duration-500">
               <i class="ph ph-file-csv text-4xl text-blue-900"></i>
             </div>
             <i class="ph ph-info text-blue-500 text-xl"></i>
             <div class="flex-1">
               <div class="flex justify-between items-start">
                 <p class="text-[11px] font-bold text-blue-900 uppercase tracking-tighter">Requirements</p>
                 <button @click.stop="downloadTemplate" class="text-[10px] font-black text-[#fe3787] underline hover:text-[#002D1E] transition-colors uppercase tracking-widest">
                   Download Template
                 </button>
               </div>
               <p class="text-[10px] text-blue-700/70 leading-relaxed mt-0.5">
                 Headers must match model fields. Use lowercase with underscores (e.g., student_number, first_name).
               </p>
             </div>
          </div>

          <div class="flex gap-3 pt-2">
            <button @click="close" class="flex-1 py-3 bg-gray-100 text-gray-500 font-bold text-xs uppercase tracking-widest hover:bg-gray-200 transition-colors">
              Cancel
            </button>
            <button 
              @click="uploadFile" 
              :disabled="!selectedFile || loading"
              class="flex-1 py-3 bg-[#fe3787] text-white font-black text-xs uppercase tracking-widest hover:bg-[#e62e7a] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg shadow-pink-500/20"
            >
              <i v-if="loading" class="ph ph-circle-notch animate-spin"></i>
              {{ loading ? 'Processing...' : 'Upload & Import' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue';
import api from '@/services/admin/api';

const props = defineProps({
  show: Boolean,
  title: String,
  modelType: String,
});

const emit = defineEmits(['close', 'refresh']);

const fileInput = ref(null);
const selectedFile = ref(null);
const loading = ref(false);
const dragOver = ref(false);
const importResult = ref(null);

const templateHeaders = {
  students: 'username,student_number,first_name,mi,last_name,email,phone,course,year_level,gender',
  instructors: 'username,instructor_id,first_name,mi,last_name,email,phone',
  airlines: 'code,name,country,is_active',
  aircrafts: 'model,capacity,airline',
  airports: 'code,name,city,country,airport_type,latitude,longitude',
  flights: 'Flight number,Airline,Aircraft,Route,Total stops,Layovers data',
  routes: 'origin_code,destination_code,base_price',
  schedules: 'flight_number,departure_time,arrival_time,price,status',
  seat_classes: 'name,price_multiplier,color,airline'
};

const triggerFileInput = () => fileInput.value.click();

const onFileChange = (e) => {
  const file = e.target.files[0];
  if (file && (file.type === 'text/csv' || file.name.endsWith('.csv'))) {
    selectedFile.value = file;
  } else {
    alert('Please select a valid CSV file.');
  }
};

const onDrop = (e) => {
  dragOver.value = false;
  const file = e.dataTransfer.files[0];
  if (file && file.name.endsWith('.csv')) {
    selectedFile.value = file;
  }
};

const downloadTemplate = () => {
  const headers = templateHeaders[props.modelType] || 'id,name';
  const blob = new Blob([headers], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.setAttribute('href', url);
  a.setAttribute('download', `template_${props.modelType}.csv`);
  a.click();
};

const uploadFile = async () => {
  if (!selectedFile.value) return;

  loading.value = true;
  const formData = new FormData();
  formData.append('file', selectedFile.value);
  formData.append('model_type', props.modelType);

  try {
    const res = await api.post('/universal-import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    importResult.value = res.data;
  } catch (err) {
    console.error('Import error:', err);
    alert(err.response?.data?.error || 'Failed to import CSV.');
  } finally {
    loading.value = false;
  }
};

const downloadDetailedErrorReport = () => {
  if (!importResult.value || !importResult.value.failed_rows || importResult.value.failed_rows.length === 0) return;
  
  const rows = importResult.value.failed_rows;
  // Get all unique headers from all rows (to handle varying keys in CSV if any)
  const allHeaders = [...new Set(rows.flatMap(r => Object.keys(r)))];
  
  // Create CSV content
  const csvContent = [
    allHeaders.join(','),
    ...rows.map(row => allHeaders.map(header => {
      const cell = row[header] === null || row[header] === undefined ? '' : row[header];
      // Escape quotes and wrap in quotes
      return `"${String(cell).replace(/"/g, '""')}"`;
    }).join(','))
  ].join('\n');
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", `import_errors_${props.modelType}_${new Date().getTime()}.csv`);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const close = () => {
  if (importResult.value) {
    emit('refresh');
  }
  selectedFile.value = null;
  importResult.value = null;
  emit('close');
};
</script>
