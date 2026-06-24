<template>
  <div class="p-6 space-y-6 bg-gray-50 min-h-screen poppins">
    <!-- Header -->
    <div class="bg-[#002D1E] p-8 rounded-[1px] text-white relative overflow-hidden group mb-8">
      <div class="absolute -right-10 -bottom-10 opacity-10 group-hover:rotate-12 transition-transform duration-700">
        <i class="ph ph-file-csv text-[200px]"></i>
      </div>
      <div class="relative">
        <h1 class="text-3xl font-black uppercase tracking-tight mb-2">Bulk Import Terminal</h1>
        <p class="text-gray-300 text-sm max-w-lg">Central command for bulk data ingestion. Migrate trainees, flight catalogs, and airport networks using CSV automation.</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- Import Control Panel -->
      <div class="lg:col-span-8 space-y-6">
        <div class="bg-white border border-gray-200 rounded-[1px] p-8 shadow-sm">
          <h3 class="text-lg font-black text-[#002D1E] uppercase tracking-widest mb-6 flex items-center gap-3">
             <i class="ph ph-terminal text-[#fe3787]"></i>
             Configuration
          </h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="space-y-2">
              <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest">Target Module</label>
              <select v-model="selectedModule" class="w-full border-2 border-gray-100 p-4 text-sm font-bold text-[#002D1E] bg-gray-50 rounded-[1px] outline-none focus:border-[#fe3787] transition-all">
                <option value="" disabled>Select a module to import...</option>
                <optgroup label="LMS Operations" v-if="canShowLMS">
                  <option value="students">Students / Trainees</option>
                  <option value="instructors">Instructors / Admins</option>
                </optgroup>
                <optgroup label="Flight Operations" v-if="canShowFlight">
                   <option value="airlines">Airlines</option>
                   <option value="airports">Airports</option>
                   <option value="aircrafts">Aircraft Fleet</option>
                   <option value="seat_classes">Seat Classes</option>
                   <option value="flights">Flight Catalog</option>
                   <option value="routes">Routes</option>
                   <option value="schedules">Schedules</option>
                   <option value="baggage">Baggage Options</option>
                   <option value="meals">Meal Catalogs</option>
                   <option value="taxes">Taxes & Fees</option>
                </optgroup>
              </select>
            </div>

            <div class="space-y-2">
              <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest">Quick Download</label>
              <button 
                @click="downloadTemplate" 
                :disabled="!selectedModule"
                class="w-full border-2 border-dashed border-gray-200 p-4 text-xs font-bold text-[#fe3787] bg-pink-50/20 rounded-[1px] hover:border-[#fe3787] hover:bg-pink-50 transition-all flex items-center justify-center gap-2 disabled:opacity-30 disabled:grayscale"
              >
                <i class="ph ph-download-simple"></i>
                Get Template CSV
              </button>
            </div>
          </div>

          <div 
            v-if="selectedModule"
            class="border-4 border-dashed border-gray-100 rounded-[1px] p-16 text-center hover:border-[#fe3787]/30 transition-all cursor-pointer bg-gray-50/50 group"
            @click="triggerImport"
          >
             <div class="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto shadow-sm mb-6 group-hover:scale-110 transition-transform">
                <i class="ph ph-upload-simple text-4xl text-[#fe3787]"></i>
             </div>
             <p class="text-sm font-black text-[#002D1E] uppercase tracking-widest">Execute Import for {{ selectedModuleTitle }}</p>
             <p class="text-[10px] text-gray-400 mt-2">Click to open the file selection terminal</p>
          </div>
          
          <div v-else class="py-20 text-center bg-gray-50/30 border border-dashed border-gray-100 italic text-gray-400 text-sm">
             Select a module above to begin the import process.
          </div>
        </div>
      </div>

      <!-- Instructions & Samples -->
      <div class="lg:col-span-4 space-y-6">
        <div class="bg-white border border-gray-200 rounded-[1px] p-6 shadow-sm">
           <h3 class="text-sm font-black text-[#002D1E] uppercase tracking-widest mb-4">Storage Map</h3>
           <p class="text-[11px] text-gray-500 mb-6 leading-relaxed">I've placed the sample CSV templates in the following system directory for your reference:</p>
           
           <div class="bg-gray-900 p-4 rounded-[1px] mb-6 overflow-hidden">
              <code class="text-[10px] text-emerald-400 break-all poppins font-bold">/samples/csv_templates/</code>
           </div>

           <div class="space-y-3">
              <div v-for="file in filteredSampleFiles" :key="file" class="flex items-center gap-3 p-3 bg-gray-50 border border-gray-100 rounded-[1px] group hover:bg-white hover:border-[#fe3787]/20 transition-all">
                 <i class="ph ph-file-csv text-2xl text-gray-300 group-hover:text-[#fe3787]"></i>
                 <div>
                    <p class="text-[10px] font-black text-[#002D1E] uppercase">{{ file }}</p>
                    <p class="text-[8px] text-gray-400 font-bold tracking-widest uppercase">Template Ready</p>
                 </div>
              </div>
           </div>
        </div>

        <div class="bg-blue-50 border border-blue-100 p-6 rounded-[1px]">
           <div class="flex gap-4">
              <i class="ph ph-lightbulb-filament text-3xl text-blue-500"></i>
              <div>
                 <p class="text-xs font-black text-blue-900 uppercase mb-2">Quick Tip</p>
                 <p class="text-[11px] text-blue-700 leading-relaxed">Ensure all foreign keys (like airline_code or route_id) exist in the system before importing flights or schedules. Use the templates to guarantee correct header names.</p>
              </div>
           </div>
        </div>
      </div>
    </div>

    <!-- The Actual Shared Import Component -->
    <ImportModal 
      :show="showModal" 
      :title="selectedModuleTitle" 
      :model-type="selectedModule" 
      @close="showModal = false"
      @refresh="handleRefresh"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import ImportModal from '@/components/admin/ImportModal.vue';
import AuthStorage from '@/utils/authStorage';

const selectedModule = ref('');
const showModal = ref(false);

const userRole = computed(() => AuthStorage.getRole() || 'admin');

const canShowLMS = computed(() => ['superadmin', 'lms_admin'].includes(userRole.value));
const canShowFlight = computed(() => ['superadmin', 'flight_admin'].includes(userRole.value));

const filteredSampleFiles = computed(() => {
  let files = [];
  if (canShowLMS.value) {
    files.push('students.csv', 'instructors.csv');
  }
  if (canShowFlight.value) {
    files.push('flights.csv', 'routes.csv', 'schedules.csv', 'airlines.csv', 'airports.csv', 'aircrafts.csv', 'seat_classes.csv', 'baggage.csv', 'meals.csv', 'taxes.csv');
  }
  return files;
});

const selectedModuleTitle = computed(() => {
  const titles = {
    students: 'Students',
    instructors: 'Instructors',
    airlines: 'Airlines',
    airports: 'Airports',
    aircrafts: 'Aircraft Fleet',
    seat_classes: 'Seat Classes',
    flights: 'Flights',
    routes: 'Routes',
    schedules: 'Schedules',
    baggage: 'Baggage Options',
    meals: 'Meal Catalogs',
    taxes: 'Taxes & Fees'
  };
  return titles[selectedModule.value] || 'Data';
});

const sampleFiles = [
  'students.csv',
  'instructors.csv',
  'aircrafts.csv',
  'seat_classes.csv',
  'flights.csv',
  'routes.csv',
  'schedules.csv',
  'baggage.csv',
  'meals.csv',
  'airlines.csv',
  'airports.csv',
  'taxes.csv'
];

const triggerImport = () => {
  if (selectedModule.value) {
    showModal.value = true;
  }
};

const downloadTemplate = () => {
  const headers = {
    students: 'Username,Student Number,First Name,Middle Initial,Last Name,Email Address,Phone Number,Course,Year Level,Gender',
    instructors: 'Username,Password,First Name,Last Name,Middle Initial,Instructor ID,Phone Number,Email Address',
    airlines: 'Airline Name,IATA Code',
    airports: 'Airport Name,IATA Code,Type,City,Detailed Location',
    aircrafts: 'model,capacity,airline',
    seat_classes: 'Class Name,Price Multiplier,Color,Airline',
    flights: 'Flight number,Airline,Aircraft,Route,Total stops,Layovers data',
    routes: 'Origin Airport,Destination Airport,Base Price',
    schedules: 'Flight Number,Departure Date & Time,Arrival Date & Time,Price,Status',
    baggage: 'Airline,Baggage Name,Weight KG,Price,Is Included',
    meals: 'Airline,Meal Name,Meal Type,Category,Price,Is Included',
    taxes: 'Tax Name,Tax Code,Category,Base Amount,Per Passenger,Applies Domestic,Applies International'
  };
  
  const content = headers[selectedModule.value] || 'id,name';
  const blob = new Blob([content], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.setAttribute('href', url);
  a.setAttribute('download', `template_${selectedModule.value}.csv`);
  a.click();
};

const handleRefresh = () => {
  // Global refresh or success notification
  console.log('Import successful');
};
</script>

<style scoped>
.poppins { font-family: 'Poppins', sans-serif; }
</style>
