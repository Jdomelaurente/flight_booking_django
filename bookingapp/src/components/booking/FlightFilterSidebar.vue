<template>
  <aside :class="['lg:w-70 flex-shrink-0', showFilters ? 'block' : 'hidden lg:block']">
    <div class="bg-white rounded-[5px] shadow-sm border border-gray-200 p-6">
      <div class="flex justify-between items-center mb-3 pb-2 border-b border-gray-100">
        <h2 class="text-base font-bold text-gray-900">Filters & Sort</h2>
        <button @click="$emit('reset-filters')" 
          class="text-xs bg-pink-500 p-1 cursor-pointer text-white hover:bg-pink-300 font-medium rounded-[2px]">
          Reset
        </button>
      </div>
      
      <!-- Flight Stats -->
      <div class="mb-3 p-2 bg-gray-50 rounded-[2px]">
        <div class="space-y-2">
          <div class="flex justify-between text-xs">
            <span class="text-gray-600">Showing:</span>
            <span class="font-medium text-gray-900">{{ filteredCount }} of {{ totalCount }} flights</span>
          </div>
          <div class="flex justify-between text-xs">
            <span class="text-gray-600">Price Range:</span>
            <span class="font-medium text-pink-500">₱{{ flightStats.priceRange }}</span>
          </div>
          <div v-if="uniqueDates.length > 0" class="flex justify-between text-xs">
            <span class="text-gray-600">Available Dates:</span>
            <span class="font-medium text-gray-900">{{ uniqueDates.length }} days</span>
          </div>
        </div>
      </div>
      
      <!-- Sort -->
      <div class="mb-3">
        <h3 class="text-xs font-semibold text-gray-300 mb-1">Sort By</h3>
        <select :value="filters.sortBy" @input="$emit('update:filters', { ...filters, sortBy: $event.target.value })"
          class="w-full px-2 py-1 border border-gray-300 rounded-sm focus:ring-2 focus:ring-pink-500 focus:border-transparent text-sm">
          <option v-for="option in filterOptions.sortOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>
      
      <!-- Price Range -->
      <div class="mb-3">
        <h3 class="text-sm font-semibold text-gray-300 mb-1">Price Range</h3>
        <div class="flex items-center space-x-1 mb-1">
          <input :value="filters.minPrice" @input="$emit('update:filters', { ...filters, minPrice: $event.target.value })" 
            type="number" placeholder="Min" 
            class="w-full px-1.5 py-1 border border-gray-300 rounded-sm text-xs focus:ring-2 focus:ring-pink-500 focus:border-transparent">
          <span class="text-gray-400">–</span>
          <input :value="filters.maxPrice" @input="$emit('update:filters', { ...filters, maxPrice: $event.target.value })" 
            type="number" placeholder="Max" 
            class="w-full px-1.5 py-1 border border-gray-300 rounded-sm text-xs focus:ring-2 focus:ring-pink-500 focus:border-transparent">
        </div>
        <p class="text-xs text-gray-400 bg-green-50 flex justify-between px-2 py-1 text-right">
          Price:
          <span class="text-sm text-black">
            ₱{{ priceRange.min.toLocaleString() }} - ₱{{ priceRange.max.toLocaleString() }}
          </span>
        </p>
      </div>
      
      <!-- Departure Time -->
      <div class="mb-3">
        <h3 class="text-xs font-semibold text-gray-800 mb-1">Departure Time</h3>
        <div class="space-y-1">
          <label v-for="time in filterOptions.departureTimes" :key="time.value" 
            class="flex items-center space-x-1 cursor-pointer">
            <input type="radio" :value="time.value" :checked="filters.departureTime === time.value"
              @change="$emit('update:filters', { ...filters, departureTime: time.value })"
              class="h-4 w-4 text-pink-500 focus:ring-pink-500 border-gray-300">
            <span class="text-sm text-gray-700">{{ time.label }}</span>
          </label>
        </div>
      </div>
      
      <!-- Flight Type -->
      <div class="mb-3">
        <h3 class="text-sm font-semibold text-gray-800 mb-3">Flight Type</h3>
        <div class="space-y-1">
          <label v-for="type in filterOptions.flightTypes" :key="type.value" 
            class="flex items-center space-x-3 cursor-pointer">
            <input type="radio" :value="type.value" :checked="filters.flightType === type.value"
              @change="$emit('update:filters', { ...filters, flightType: type.value })"
              class="h-4 w-4 text-pink-500 focus:ring-pink-500 border-gray-300">
            <span class="text-sm text-gray-700">{{ type.label }}</span>
          </label>
        </div>
      </div>
      
      <!-- Airline -->
      <div v-if="filterOptions.airlines.length > 1" class="mb-3">
        <h3 class="text-xs font-semibold text-gray-800 mb-1">Airline</h3>
        <select :value="filters.airline" @input="$emit('update:filters', { ...filters, airline: $event.target.value })"
          class="w-full px-2 py-1 border border-gray-300 rounded-sm focus:ring-2 focus:ring-pink-500 focus:border-transparent text-sm">
          <option v-for="airline in filterOptions.airlines" :key="airline.value" :value="airline.value">
            {{ airline.label }}
          </option>
        </select>
      </div>
      
      <!-- Seat Class -->
      <div class="mb-3">
        <h3 class="text-xs font-semibold text-gray-800 mb-3">Seat Class</h3>
        <select :value="filters.seatClass" @input="$emit('update:filters', { ...filters, seatClass: $event.target.value })"
          class="w-full px-4 py-2 border border-gray-300 rounded-sm focus:ring-2 focus:ring-pink-500 focus:border-transparent text-sm">
          <option v-for="seatClass in availableSeatClassOptions" :key="seatClass.value" :value="seatClass.value">
            {{ seatClass.label }}
          </option>
        </select>
      </div>
      
      <!-- Available Seats -->
      <div class="mb-3">
        <label class="flex items-center space-x-1.5 cursor-pointer">
          <input type="checkbox" :checked="filters.hasAvailableSeats" 
            @change="$emit('update:filters', { ...filters, hasAvailableSeats: $event.target.checked })"
            class="h-3 w-3 text-pink-500 rounded focus:ring-pink-500 border-gray-300">
          <span class="text-sm text-gray-700">Show only flights with available seats</span>
        </label>
      </div>
      
      <!-- Date Filter -->
      <div class="mb-3">
        <h3 class="text-xs font-semibold text-gray-800 mb-3">Date Filter</h3>
        <div class="space-y-2">
          <div>
            <label class="block text-xs text-gray-600 mb-2">Select Date</label>
            <select :value="dateFilter.selectedDate" @change="$emit('update:dateFilter', { ...dateFilter, selectedDate: $event.target.value })"
              class="w-full px-2 py-1 border border-gray-300 rounded-sm focus:ring-2 focus:ring-pink-500 focus:border-transparent text-sm">
              <option v-for="date in uniqueDates" :key="date.value" :value="date.value">
                {{ date.shortLabel }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-xs text-gray-600 mb-2">Date Range</label>
            <select :value="dateFilter.dateRange" @change="$emit('update:dateFilter', { ...dateFilter, dateRange: $event.target.value })"
              class="w-full px-4 py-2 border border-gray-300 rounded-sm focus:ring-2 focus:ring-pink-500 focus:border-transparent text-sm">
              <option v-for="range in filterOptions.dateRanges" :key="range.value" :value="range.value">
                {{ range.label }}
              </option>
            </select>
          </div>
          <button v-if="isDateFilterActive" @click="$emit('reset-date-filter')" 
            class="w-full text-sm text-pink-500 hover:text-pink-600 font-medium py-2 border border-pink-200 rounded-sm hover:bg-pink-50">
            Reset to Original Date
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
