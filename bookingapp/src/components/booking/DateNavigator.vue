<template>
  <div class="bg-white rounded-[5px] shadow-sm border border-gray-200 py-2 px-5 mb-4">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-3">
      <h2 class="text-xl font-bold text-gray-900">Select Date</h2>
      <div class="flex items-center space-x-4">
        <div class="flex items-center space-x-2">
          <button @click="$emit('prev-week')" 
            class="p-1 border border-gray-300 rounded-[2px] hover:bg-gray-50 transition-colors">
            <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </button>
          <div class="text-sm font-medium text-gray-700">{{ weekRange }}</div>
          <button @click="$emit('next-week')" 
            class="p-1 border border-gray-300 rounded-[2px] hover:bg-gray-50 transition-colors">
            <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
        <button @click="$emit('go-to-current')" 
          :class="['px-2 py-1 rounded-[2px] text-sm font-medium transition-colors',
                   currentWeekContainsSelectedDate ? 'bg-pink-500 hover:bg-pink-300 cursor-pointer text-white' : 'border border-pink-300 text-pink-500 hover:bg-pink-50']">
          This Week
        </button>
      </div>
    </div>
    
    <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
      <div v-for="day in weekDays" :key="day.dateString" 
        @click="day.isAvailable && $emit('select-day', day)"
        :class="['p-4 rounded-[2px] border-2 cursor-pointer transition-all duration-150 transform active:scale-95',
                 day.isAvailable ? 'hover:border-pink-300 hover:shadow-md hover:-translate-y-0.5 active:bg-pink-50' : 'cursor-not-allowed opacity-50',
                 day.isSelected ? 'border-pink-500 bg-pink-500 shadow-lg scale-105 z-10 active:bg-pink-600' : 'border-gray-200 bg-white',
                 day.isToday && !day.isSelected ? 'border-pink-300' : '',
                 day.isSearchDate && !day.isToday && !day.isSelected ? 'border-pink-200' : '']">
        <div class="flex justify-between items-start mb-2">
          <div class="text-sm font-bold uppercase tracking-wider" :class="day.isSelected ? 'text-white' : 'text-gray-500'">
            {{ day.dayName }}
          </div>
          <div v-if="day.isSelected" class="text-white">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div v-else-if="day.isToday" class="px-2 py-0.5 bg-pink-500 text-white text-[10px] uppercase font-bold rounded-[2px]">
            Today
          </div>
          <div v-else-if="day.isSearchDate && !day.isToday" class="px-2 py-0.5 bg-pink-100 text-pink-700 text-[10px] uppercase font-bold rounded-full">
            Search
          </div>
        </div>
        <div class="text-center mb-2">
          <div class="text-3xl font-black leading-none mb-1" :class="day.isSelected ? 'text-white' : 'text-gray-900'">
            {{ day.dayNumber }}
          </div>
          <div class="text-xs font-medium uppercase tracking-widest" :class="day.isSelected ? 'text-white/80' : 'text-gray-400'">
            {{ day.monthName }}
          </div>
        </div>
        <div class="text-center mt-2 pt-2 border-t" :class="day.isSelected ? 'border-white/20' : 'border-gray-100'">
          <div v-if="day.isAvailable" class="text-[10px] font-bold uppercase" :class="day.isSelected ? 'text-white' : 'text-green-600'">
            {{ getFlightCount(day.dateString) }} flights
          </div>
          <div v-else class="text-[10px] text-gray-400 italic">
            No flights
          </div>
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
