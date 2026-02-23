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
        
        <div v-if="!selectedClassPendingAck" class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div v-for="(seatClass, index) in seatClasses" :key="index" 
            @click="selectClassForAck(seatClass)"
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

        <!-- NEW: Fare Rules Acknowledgment View -->
        <div v-else class="max-w-2xl mx-auto">
          <div class="flex items-center mb-6">
            <button @click="backToSelection" class="text-pink-600 hover:text-pink-700 font-medium flex items-center text-sm">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Classes
            </button>
          </div>
          
          <div class="bg-gray-50 border border-gray-200 rounded-sm p-6 mb-6">
            <div class="flex justify-between items-center mb-4 pb-4 border-b border-gray-200">
              <div>
                <h3 class="text-lg font-bold text-gray-900">{{ selectedClassPendingAck.name }} Fare Conditions</h3>
                <p class="text-sm text-gray-600">Please review standard airline rules for this ticket class.</p>
              </div>
              <div class="text-right">
                <div class="text-xl font-bold text-pink-500">₱{{ Number(selectedClassPendingAck.price).toLocaleString() }}</div>
                <div class="text-xs text-gray-500">per person</div>
              </div>
            </div>
            
            <ul class="space-y-4">
              <li v-for="(rule, index) in getFareRules(selectedClassPendingAck.name)" :key="index" class="flex items-start">
                <div class="flex-shrink-0 mt-0.5">
                  <svg v-if="rule.type === 'strict'" class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <svg v-else-if="rule.type === 'warning'" class="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <svg v-else class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div class="ml-3">
                  <p class="text-sm font-medium text-gray-900">{{ rule.title }}</p>
                  <p class="text-xs text-gray-600 mt-1">{{ rule.description }}</p>
                </div>
              </li>
            </ul>
          </div>
          
          <div class="bg-blue-50 border border-blue-200 rounded-sm p-4 mb-6 flex items-start cursor-pointer hover:bg-blue-100 transition-colors" @click="hasAcknowledgedRules = !hasAcknowledgedRules">
            <div class="flex items-center h-5 mt-0.5">
              <input 
                id="fare-acknowledgment" 
                type="checkbox" 
                v-model="hasAcknowledgedRules"
                class="w-4 h-4 text-pink-600 bg-white border-gray-300 rounded-sm focus:ring-pink-500 cursor-pointer"
              >
            </div>
            <div class="ml-3 text-sm">
              <label for="fare-acknowledgment" class="font-medium text-blue-900 cursor-pointer select-none">Travel Agency Acknowledgment</label>
              <p class="text-blue-700 mt-1 cursor-pointer select-none">I confirm that I have read and clearly explained these fare conditions, including any penalties or restrictions, to the passenger.</p>
            </div>
          </div>
          
          <button 
            @click="confirmSelectionWithAck"
            :disabled="!hasAcknowledgedRules"
            :class="[
              'w-full py-3 rounded-sm font-medium transition-colors text-white',
              hasAcknowledgedRules ? 'bg-pink-500 hover:bg-pink-600 cursor-pointer' : 'bg-gray-400 cursor-not-allowed'
            ]"
          >
            Confirm {{ selectedClassPendingAck.name }} Selection
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  show: Boolean,
  flight: Object,
  seatClasses: Array
});

const emit = defineEmits(['select-class', 'close']);

// NEW: Fare Rules State
const selectedClassPendingAck = ref(null);
const hasAcknowledgedRules = ref(false);

// Reset state when modal closes
watch(() => props.show, (newVal) => {
  if (!newVal) {
    selectedClassPendingAck.value = null;
    hasAcknowledgedRules.value = false;
  }
});

const selectClassForAck = (seatClass) => {
  selectedClassPendingAck.value = seatClass;
  hasAcknowledgedRules.value = false;
};

const backToSelection = () => {
  selectedClassPendingAck.value = null;
  hasAcknowledgedRules.value = false;
};

const confirmSelectionWithAck = () => {
  if (hasAcknowledgedRules.value && selectedClassPendingAck.value) {
    emit('select-class', selectedClassPendingAck.value);
  }
};

const getFareRules = (className) => {
  const isEconomy = className.toLowerCase().includes('economy');
  const isBusiness = className.toLowerCase().includes('business');
  const isFirst = className.toLowerCase().includes('first');
  
  if (isBusiness || isFirst) {
    return [
      { title: 'Refundable Ticket', description: 'Cancellations allowed up to 24 hours prior to departure without penalty.', type: 'flexible' },
      { title: 'Free Date Changes', description: 'Flight dates can be changed free of charge (fare difference may apply).', type: 'flexible' },
      { title: 'No-Show Policy', description: 'Standard no-show penalties apply if not cancelled prior to departure.', type: 'warning' }
    ];
  } else if (className.toLowerCase().includes('premium')) {
    return [
      { title: 'Partially Refundable', description: 'Cancellations allowed with a ₱2,500 penalty fee.', type: 'warning' },
      { title: 'Change Fee Applies', description: 'Flight dates can be changed for a ₱1,500 fee plus fare difference.', type: 'warning' },
      { title: 'No-Show Policy', description: 'Ticket is forfeited if not cancelled prior to departure.', type: 'strict' }
    ];
  } else {
    // Standard Economy
    return [
      { title: 'Non-Refundable Ticket', description: 'Strictly no refunds allowed for cancellations on this promotional fare.', type: 'strict' },
      { title: 'High Change Fee', description: 'Flight dates can be changed for a ₱3,500 penalty fee plus fare difference.', type: 'strict' },
      { title: 'No-Show Policy', description: 'Ticket is fully forfeited if passenger fails to board.', type: 'strict' }
    ];
  }
};

const formatDate = (dateTimeString) => {
  if (!dateTimeString) return '';
  const date = new Date(dateTimeString);
  return date.toLocaleDateString('en-PH', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' });
};
</script>
