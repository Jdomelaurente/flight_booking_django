<template>
  <div v-if="show" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-sm shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
      <div class="p-6 border-b border-gray-200">
        <div class="flex justify-between items-center">
          <h2 class="text-2xl font-bold text-gray-900">Select Seat Class</h2>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div v-if="flight" class="mt-2 text-gray-600">
          {{ flight.origin }} → {{ flight.destination }} • 
          {{ formatDate(flight.departure_time) }}
        </div>
      </div>
      
      <div class="p-6">
        <div class="mb-6 bg-pink-50 border border-pink-200 rounded-sm p-4">
          <div class="flex items-center">
            <svg class="w-5 h-5 text-pink-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
            <div>
              <p class="text-sm text-pink-700 font-medium">Pricing varies by class selection</p>
              <p class="text-xs text-pink-600 mt-1">Choose from the available options below. The price varies depending on the class you select.</p>
            </div>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="(seatClass, index) in seatClasses" :key="index" 
            @click="$emit('select-class', seatClass)"
            class="border-2 border-gray-200 hover:border-pink-500 rounded-sm p-6 cursor-pointer transition-all duration-200 hover:shadow-lg group flex flex-col h-full">
            
            <div class="flex justify-between items-start mb-4">
              <div class="p-2 bg-pink-50 rounded-sm group-hover:bg-pink-100 transition-colors">
                <svg class="w-6 h-6 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="seatClass.icon" />
                </svg>
              </div>
            </div>
            
            <h3 class="text-xl font-bold text-gray-900 mb-2">{{ seatClass.name }}</h3>
            <p class="text-sm text-gray-600 mb-6 flex-grow">{{ seatClass.description }}</p>
            
            <div class="space-y-3 mb-6">
              <div v-for="(feature, fIndex) in seatClass.features" :key="fIndex" class="flex items-start text-xs text-gray-700">
                <svg class="w-4 h-4 text-green-500 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span>{{ feature }}</span>
              </div>
            </div>
            
            <div class="mt-auto pt-6 border-t border-gray-100">
              <div class="text-2xl font-bold text-gray-900">₱{{ Number(seatClass.price).toLocaleString() }}</div>
              <div class="text-xs text-gray-500">per person</div>
              
              <button class="w-full mt-4 py-2 bg-pink-500 text-white rounded-sm font-medium group-hover:bg-pink-600 transition-colors">
                Select {{ seatClass.name }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  show: Boolean,
  flight: Object,
  seatClasses: Array
});

defineEmits(['select-class', 'close']);

const formatDate = (dateTimeString) => {
  if (!dateTimeString) return '';
  const date = new Date(dateTimeString);
  return date.toLocaleDateString('en-PH', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' });
};
</script>
