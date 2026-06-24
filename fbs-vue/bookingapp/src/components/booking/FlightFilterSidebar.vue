<template>
  <aside :class="['lg:w-70 flex-shrink-0', showFilters ? 'block' : 'hidden lg:block']">
    <div class="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden sticky top-8">
      <div class="p-6 bg-gradient-to-r from-gray-50 to-white border-b border-gray-100 flex justify-between items-center">
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5 text-gray-800 font-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
          </svg>
          <h2 class="text-lg font-black text-gray-900 uppercase tracking-tighter">Filters</h2>
        </div>
        <button @click="$emit('reset-filters')" 
          class="text-[10px] font-black uppercase tracking-widest text-[#FF579A] hover:bg-pink-50 px-3 py-1 rounded-full border border-pink-100 transition-all cursor-pointer">
          Reset All
        </button>
      </div>
      
      <div class="p-6 space-y-8">
        <!-- Flight Stats Summary -->
        <div class="grid grid-cols-2 gap-3">
          <div class="bg-gray-50 rounded-xl p-3 border border-gray-100">
            <span class="block text-[8px] font-black text-gray-400 uppercase tracking-widest mb-1">Showing</span>
            <span class="text-xs font-black text-gray-900">{{ filteredCount }}/{{ totalCount }}</span>
          </div>
          <div class="bg-pink-50 rounded-xl p-3 border border-pink-100/50">
            <span class="block text-[8px] font-black text-pink-400 uppercase tracking-widest mb-1">Range</span>
            <span class="text-xs font-black text-pink-600">₱{{ flightStats.priceRange }}</span>
          </div>
        </div>
      
        <!-- Sort Section -->
        <div class="space-y-3">
          <h3 class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Global Sorting</h3>
          <div class="relative group">
            <select :value="filters.sortBy" @input="$emit('update:filters', { ...filters, sortBy: $event.target.value })"
              class="w-full appearance-none cursor-pointer border border-gray-200 rounded-xl bg-white px-4 py-3 text-sm font-bold text-gray-700 transition focus:border-pink-500 focus:ring-2 focus:ring-pink-500/10">
              <option v-for="option in filterOptions.sortOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
            <div class="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 border-l border-gray-100 pl-3">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>
      
        <!-- Price Range Section -->
        <div class="space-y-3">
          <h3 class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Price Limit</h3>
          <div class="flex items-center gap-2">
            <div class="relative flex-1">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[10px] font-bold text-gray-400">₱</span>
              <input :value="filters.minPrice" @input="$emit('update:filters', { ...filters, minPrice: $event.target.value })" 
                type="number" placeholder="Min" 
                class="w-full pl-6 pr-2 py-2.5 border border-gray-200 rounded-xl text-xs font-bold focus:ring-2 focus:ring-pink-500/10 focus:border-pink-500 outline-none transition">
            </div>
            <div class="text-gray-300">—</div>
            <div class="relative flex-1">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[10px] font-bold text-gray-400">₱</span>
              <input :value="filters.maxPrice" @input="$emit('update:filters', { ...filters, maxPrice: $event.target.value })" 
                type="number" placeholder="Max" 
                class="w-full pl-6 pr-2 py-2.5 border border-gray-200 rounded-xl text-xs font-bold focus:ring-2 focus:ring-pink-500/10 focus:border-pink-500 outline-none transition">
            </div>
          </div>
          <div class="flex justify-between items-center px-4 py-2 bg-gray-50 rounded-xl border border-gray-100">
            <span class="text-[9px] font-bold text-gray-400 uppercase">Actual Range:</span>
            <span class="text-[10px] font-black text-gray-800">₱{{ priceRange.min.toLocaleString() }} - ₱{{ priceRange.max.toLocaleString() }}</span>
          </div>
        </div>
      
        <!-- Flight Type & Time Visual Selection -->
        <div class="space-y-6">
          <div class="space-y-3">
            <h3 class="text-[10px] font-black text-gray-400 uppercase tracking-widest leading-none">Schedule Preference</h3>
            <div class="grid grid-cols-2 gap-2">
              <button v-for="time in filterOptions.departureTimes" :key="time.value" 
                @click="$emit('update:filters', { ...filters, departureTime: time.value })"
                :class="[
                  'px-3 py-2 rounded-xl text-center text-[10px] font-black transition-all border uppercase tracking-wider',
                  filters.departureTime === time.value 
                    ? 'bg-pink-500 border-pink-500 text-white shadow-md shadow-pink-200' 
                    : 'bg-white border-gray-100 text-gray-600 hover:border-gray-200 hover:bg-gray-50'
                ]"
              >
                {{ time.label }}
              </button>
            </div>
          </div>

          <div class="space-y-3">
            <h3 class="text-[10px] font-black text-gray-400 uppercase tracking-widest leading-none">Stops</h3>
            <div class="grid grid-cols-2 gap-2">
              <button 
                v-for="stop in [
                  { label: 'All', value: 'all' },
                  { label: 'Non-stop', value: 'nonstop' },
                  { label: '1 Stop', value: '1-stop' },
                  { label: '2+ Stops', value: '2-stop' }
                ]"
                :key="stop.value"
                @click="$emit('update:filters', { ...filters, stops: stop.value })"
                :class="[
                  'px-3 py-2 rounded-xl text-center text-[10px] font-black transition-all border uppercase tracking-wider',
                  filters.stops === stop.value 
                    ? 'bg-pink-500 border-pink-500 text-white shadow-md shadow-pink-200' 
                    : 'bg-white border-gray-100 text-gray-600 hover:border-gray-200 hover:bg-gray-50'
                ]"
              >
                {{ stop.label }}
              </button>
            </div>
          </div>
        </div>
      
        <!-- Airline & Advanced Visual Selection -->
        <div class="space-y-6">
          <div v-if="filterOptions.airlines.length > 1" class="space-y-3">
            <h3 class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Airline</h3>
            <div class="relative group">
              <select :value="filters.airline" @input="$emit('update:filters', { ...filters, airline: $event.target.value })"
                class="w-full appearance-none cursor-pointer border border-gray-200 rounded-xl bg-white px-4 py-3 text-sm font-bold text-gray-700 transition focus:border-pink-500 focus:ring-2 focus:ring-pink-500/10">
                <option v-for="airline in filterOptions.airlines" :key="airline.value" :value="airline.value">
                  {{ airline.label }}
                </option>
              </select>
              <div class="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-gray-400">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
              </div>
            </div>
          </div>

          <div class="space-y-3">
            <h3 class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Experience</h3>
            <div class="relative group">
              <select :value="filters.seatClass" @input="$emit('update:filters', { ...filters, seatClass: $event.target.value })"
                class="w-full appearance-none cursor-pointer border border-gray-200 rounded-xl bg-white px-4 py-3 text-sm font-bold text-gray-700 transition focus:border-pink-500 focus:ring-2 focus:ring-pink-500/10">
                <option v-for="seatClass in availableSeatClassOptions" :key="seatClass.value" :value="seatClass.value">
                  {{ seatClass.label }}
                </option>
              </select>
              <div class="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-gray-400">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
              </div>
            </div>
          </div>

          <label class="flex items-center gap-3 p-4 bg-gray-50 rounded-2xl border border-gray-100 cursor-pointer group hover:bg-pink-50 hover:border-pink-100 transition-all">
            <div class="relative flex items-center">
              <input type="checkbox" :checked="filters.hasAvailableSeats" 
                @change="$emit('update:filters', { ...filters, hasAvailableSeats: $event.target.checked })"
                class="peer sr-only">
              <div class="w-10 h-6 bg-gray-200 rounded-full peer peer-checked:bg-pink-500 after:content-[''] after:absolute after:top-1 after:left-1 after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-4 peer-checked:after:border-white"></div>
            </div>
            <span class="text-xs font-black text-gray-700 uppercase tracking-tight">Real-time availability only</span>
          </label>
        </div>
      

      
        <!-- Date Selection Visual -->
        <div class="space-y-4 pt-6 border-t border-gray-100">
          <h3 class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Date Flexibility</h3>
          <div class="space-y-4">
            <div class="relative group">
              <select :value="dateFilter.selectedDate" @change="$emit('update:dateFilter', { ...dateFilter, selectedDate: $event.target.value })"
                class="w-full appearance-none cursor-pointer border border-gray-200 rounded-xl bg-white px-4 py-3 text-sm font-bold text-gray-700 transition focus:border-pink-500">
                <option v-for="date in uniqueDates" :key="date.value" :value="date.value">
                  {{ date.shortLabel }}
                </option>
              </select>
              <div class="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-gray-400">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-2">
              <button v-for="range in filterOptions.dateRanges" :key="range.value"
                @click="$emit('update:dateFilter', { ...dateFilter, dateRange: range.value })"
                :class="[
                  'px-2 py-2 rounded-xl text-[9px] font-black uppercase tracking-tighter border transition-all',
                  dateFilter.dateRange === range.value 
                    ? 'bg-gray-900 border-gray-900 text-white' 
                    : 'bg-white border-gray-100 text-gray-500 hover:border-gray-200'
                ]"
              >
                {{ range.label }}
              </button>
            </div>
            
            <button v-if="isDateFilterActive" @click="$emit('reset-date-filter')" 
              class="w-full text-[10px] font-black uppercase tracking-widest text-[#FF579A] border border-[#FF579A]/20 py-3 rounded-xl hover:bg-pink-50 transition-all">
              Restore Original Date
            </button>
          </div>
        </div>
      
      <!-- Active Filters Summary -->
      <div v-if="hasActiveFilters" class="pt-6 border-t border-gray-100">
        <h3 class="text-xs font-semibold text-gray-800 mb-3">Active Filters</h3>
        <div class="flex flex-wrap gap-2">
          <span v-if="isDateFilterActive" 
            class="inline-flex items-center px-3 py-1 rounded-full text-[9px] font-medium bg-pink-100 text-pink-700">
            Date: {{ dateFilterDisplay }}
          </span>
          <span v-if="filters.minPrice || filters.maxPrice" 
            class="inline-flex items-center px-3 py-1 rounded-full text-[9px] font-medium bg-pink-100 text-pink-700">
            Price: ₱{{ filters.minPrice || priceRange.min }} - ₱{{ filters.maxPrice || priceRange.max }}
          </span>
          <span v-if="filters.departureTime !== 'all'" 
            class="inline-flex items-center px-3 py-1 rounded-full text-[9px] font-medium bg-pink-100 text-pink-700">
            {{ getOptionLabel(filterOptions.departureTimes, filters.departureTime) }}
          </span>
          <span v-if="filters.flightType !== 'all'" 
            class="inline-flex items-center px-3 py-1 rounded-full text-[9px] font-medium bg-pink-100 text-pink-700">
            {{ getOptionLabel(filterOptions.flightTypes, filters.flightType) }}
          </span>
          <span v-if="filters.stops !== 'all'" 
            class="inline-flex items-center px-3 py-1 rounded-full text-[9px] font-medium bg-pink-100 text-pink-700">
            Stops: {{ filters.stops === 'nonstop' ? 'Non-stop' : (filters.stops === '1-stop' ? '1 Stop' : (filters.stops === '2-stop' ? '2 Stops' : filters.stops)) }}
          </span>
          <span v-if="filters.airline !== 'all'" 
            class="inline-flex items-center px-3 py-1 rounded-full text-[9px] font-medium bg-pink-100 text-pink-700">
            {{ getOptionLabel(filterOptions.airlines, filters.airline) }}
          </span>
          <span v-if="filters.seatClass !== 'all'" 
            class="inline-flex items-center px-3 py-1 rounded-full text-[9px] font-medium bg-pink-100 text-pink-700">
            {{ getOptionLabel(availableSeatClassOptions, filters.seatClass) }}
          </span>
          <span v-if="filters.hasAvailableSeats" 
            class="inline-flex items-center px-3 py-1 rounded-full text-[9px] font-medium bg-pink-100 text-pink-700">
            Available Seats Only
          </span>
        </div>
      </div>
    </div>
  </div>
</aside>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  showFilters: Boolean,
  filters: Object,
  dateFilter: Object,
  filterOptions: Object,
  totalCount: Number,
  filteredCount: Number,
  flightStats: Object,
  uniqueDates: Array,
  priceRange: Object,
  availableSeatClassOptions: Array,
  isDateFilterActive: Boolean,
  dateFilterDisplay: String
});

defineEmits(['update:filters', 'update:dateFilter', 'reset-filters', 'reset-date-filter']);

const hasActiveFilters = computed(() => {
  return Object.values(props.filters).some(f => f !== 'all' && f !== false && f !== null) || props.isDateFilterActive;
});

const getOptionLabel = (options, value) => {
  return options.find(o => o.value === value)?.label || value;
};
</script>
