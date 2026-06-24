<template>
  <div class="bg-white py-2 sm:py-3 border-b border-slate-200 sticky top-0 z-50 me-auto shadow-sm mx-auto border-2">
    <!-- Global Practice Mode Indicator (Responsive Positioning) -->
    <div v-if="bookingStore.isPractice" class="flex justify-center sm:absolute sm:top-0 sm:right-4 sm:h-full items-center bg-transparent pointer-events-none mb-2 sm:mb-0">
      <div class="flex items-center gap-2 bg-blue-50/80 backdrop-blur-sm border border-blue-200 px-3 py-1 rounded-full shadow-sm animate-pulse pointer-events-auto mt-1 sm:mt-0">
        <span class="flex h-1.5 w-1.5 rounded-full bg-blue-500 text-blue-100 ring ring-blue-500/20"></span>
        <span class="text-[8px] sm:text-[9px] font-black text-blue-600 uppercase tracking-widest leading-none">Practice Mode Active</span>
      </div>
    </div>

    <div class="container mx-auto">
      <div class="flex justify-between items-center max-w-[900px] mx-auto px-5">
        <div v-for="(step, index) in steps" :key="index" class="flex items-center flex-1 last:flex-none">
          <div class="flex flex-col items-center gap-2 relative z-[2]">
            <div 
              class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm border-2 border-transparent transition-all duration-300"
              :class="[
                currentStepIndex === index ? 'bg-[#003870] text-white ring-4 ring-[#003870]/10' : 
                currentStepIndex > index ? 'bg-emerald-500 text-white' : 'bg-slate-100 text-slate-500'
              ]"
            >
              <span v-if="currentStepIndex > index">✓</span>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <span 
              class="text-xs font-semibold uppercase tracking-[0.5px] transition-all duration-300 hidden sm:block"
              :class="[
                currentStepIndex === index ? 'text-[#003870]' : 
                currentStepIndex > index ? 'text-emerald-500' : 'text-slate-500'
              ]"
            >{{ step.label }}</span>
          </div>
          <div 
            v-if="index < steps.length - 1" 
            class="flex-1 h-[2px] transition-all duration-300 mx-[10px] my-0 sm:-mt-6 sm:mx-[15px] sm:mb-0"
            :class="[
              currentStepIndex > index ? 'bg-emerald-500' : 'bg-slate-100'
            ]"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useBookingStore } from '@/stores/booking';

const route = useRoute();
const bookingStore = useBookingStore();

const steps = [
  { label: 'Selection', routes: ['SearchResults'] },
  { label: 'Details', routes: ['PassengerDetails'] },
  { label: 'Extras', routes: ['Addons', 'SeatSelection'] },
  { label: 'Review', routes: ['ReviewBooking'] },
  { label: 'Payment', routes: ['Payment'] }
];

const currentStepIndex = computed(() => {
  return steps.findIndex(step => step.routes.includes(route.name));
});
</script>
