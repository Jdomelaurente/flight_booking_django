<template>
  <div class="bg-white rounded-[5px] shadow-sm border border-gray-200 py-3 px-3 sm:px-4 mb-4 overflow-hidden">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
      <div class="flex items-center justify-between sm:justify-start gap-4">
        <h2 class="text-sm font-black text-gray-900 uppercase tracking-tighter">Select Date</h2>
        <button @click="$emit('go-to-current')" 
          :class="['px-3 py-1 rounded-[4px] text-[10px] font-black uppercase tracking-widest transition-all duration-200',
                   currentWeekContainsSelectedDate ? 'bg-pink-500 text-white shadow-sm' : 'border border-pink-200 text-pink-500 hover:bg-pink-50']">
          This Week
        </button>
      </div>
      
      <div class="flex items-center justify-between sm:justify-end gap-3 bg-gray-50/80 p-1 rounded-lg sm:bg-transparent sm:p-0">
        <button @click="$emit('prev-week')" 
          class="p-2 sm:p-1.5 border border-gray-200 rounded-md bg-white hover:bg-gray-50 transition-colors shadow-sm">
          <svg class="w-3.5 h-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div class="text-[10px] sm:text-xs font-black text-gray-400 uppercase tracking-[0.1em]">{{ weekRange }}</div>
        <button @click="$emit('next-week')" 
          class="p-2 sm:p-1.5 border border-gray-200 rounded-md bg-white hover:bg-gray-50 transition-colors shadow-sm">
          <svg class="w-3.5 h-3.5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
    
    <!-- Horizontal Scrollable Container on Mobile, Grid on Tablet/Desktop -->
    <div class="flex sm:grid sm:grid-cols-4 lg:grid-cols-7 gap-2 overflow-x-auto sm:overflow-x-visible pb-2 sm:pb-0 scrollbar-hide -mx-1 px-1">
      <div v-for="day in weekDays" :key="day.dateString" 
        @click="day.isAvailable && $emit('select-day', day)"
        :class="['flex-shrink-0 w-[100px] sm:w-auto py-2.5 px-3 rounded-[4px] border-2 cursor-pointer transition-all duration-200 relative',
                 day.isAvailable ? 'hover:border-pink-200 active:bg-pink-50' : 'cursor-not-allowed opacity-40',
                 day.isSelected 
                  ? 'border-pink-500 bg-white ring-1 ring-pink-500/10' 
                  : (day.isToday ? 'border-pink-200 bg-white' : 'border-gray-100 bg-white')]">
        
        <!-- Selection Marker -->
        <div v-if="day.isSelected" class="absolute top-0 right-0 p-1">
          <div class="w-2 h-2 rounded-full bg-pink-500 ring-2 ring-white"></div>
        </div>

        <div class="flex justify-between items-start mb-1 text-[8px] font-black uppercase tracking-widest">
          <span :class="day.isSelected ? 'text-pink-600' : (day.isToday ? 'text-pink-400' : 'text-gray-400')">
            {{ day.dayName }}
          </span>
          <span v-if="day.isToday" class="text-pink-500">Today</span>
        </div>

        <div class="text-center py-1">
          <div class="text-xl sm:text-2xl font-black leading-none" :class="day.isSelected ? 'text-pink-600' : 'text-slate-800'">
            {{ day.dayNumber }}
          </div>
          <div class="text-[8px] font-bold text-gray-400 uppercase tracking-widest mt-0.5">
            {{ day.monthName }}
          </div>
        </div>

        <div class="text-center mt-2 pt-1.5 border-t border-gray-50 flex flex-col items-center">
          <template v-if="day.isAvailable">
            <span class="text-[9px] font-black" :class="day.isSelected ? 'text-pink-600' : 'text-green-600'">
              {{ getFlightCount(day.dateString) }} FLIGHTS
            </span>
            <!-- Simple availability dot -->
            <div class="w-1 h-1 rounded-full bg-green-500 mt-0.5 animate-pulse"></div>
          </template>
          <span v-else class="text-[8px] font-medium text-gray-300 uppercase tracking-tight">Closed</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  weekDays: Array,
  weekRange: String,
  currentWeekContainsSelectedDate: Boolean,
  flights: Array
});

defineEmits(['prev-week', 'next-week', 'go-to-current', 'select-day']);

const getFlightCount = (dateString) => {
  return props.flights.filter(f => {
    const flightDate = new Date(f.departure_time);
    return flightDate.toISOString().split('T')[0] === dateString;
  }).length;
};
</script>
