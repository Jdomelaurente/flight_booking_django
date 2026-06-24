<template>
  <div class="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-sm">
    <div class="p-5 bg-slate-100 border-b border-slate-200">
      <h3 class="text-base font-bold text-slate-900 m-0">Booking Summary</h3>
    </div>
    
    <!-- Flight Summary -->
    <div class="p-6 border-b border-slate-100">
      <template v-if="isMultiCity">
        <div v-for="(segment, index) in multiCitySegments" :key="index" class="pb-5 mb-5 border-b border-slate-50 last:pb-0 last:mb-0 last:border-b-0">
          <div class="flex justify-between items-center mb-2">
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Flight {{ index + 1 }}</span>
            <span class="text-sm font-bold text-slate-700">₱{{ Number(segment.selectedFlight?.price || 0).toLocaleString() }}</span>
          </div>
          <div class="flex items-center gap-2 mb-1" v-if="segment.selectedFlight">
            <span class="text-base font-bold text-slate-800">{{ segment.selectedFlight.origin }}</span>
            <span class="text-slate-400">→</span>
            <span class="text-base font-bold text-slate-800">{{ segment.selectedFlight.destination }}</span>
          </div>
          <div class="text-xs text-slate-500" v-if="segment.selectedFlight">
            {{ segment.selectedFlight.departure_date }}
          </div>
        </div>
      </template>
      <template v-else>
        <!-- Departure -->
        <div class="pb-5 mb-5 border-b border-slate-50 last:pb-0 last:mb-0 last:border-b-0">
          <div class="flex justify-between items-center mb-2">
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Departure</span>
            <span class="text-sm font-bold text-slate-700">₱{{ Number(selectedFlight?.price || 0).toLocaleString() }}</span>
          </div>
          <div class="flex items-center gap-2 mb-1" v-if="selectedFlight">
            <span class="text-base font-bold text-slate-800">{{ selectedFlight.origin }}</span>
            <span class="text-slate-400">→</span>
            <span class="text-base font-bold text-slate-800">{{ selectedFlight.destination }}</span>
          </div>
          <div class="text-xs text-slate-500" v-if="selectedFlight">{{ selectedFlight.departure_date }}</div>
        </div>

        <!-- Return -->
        <div v-if="isRoundTrip && selectedReturn" class="pt-5 mt-5 border-t border-slate-50 first:pt-0 first:mt-0 first:border-t-0">
          <div class="flex justify-between items-center mb-2">
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Return</span>
            <span class="text-sm font-bold text-slate-700">₱{{ Number(selectedReturn?.price || 0).toLocaleString() }}</span>
          </div>
          <div class="flex items-center gap-2 mb-1">
            <span class="text-base font-bold text-slate-800">{{ selectedReturn.origin }}</span>
            <span class="text-slate-400">→</span>
            <span class="text-base font-bold text-slate-800">{{ selectedReturn.destination }}</span>
          </div>
          <div class="text-xs text-slate-500">{{ selectedReturn.departure_date }}</div>
        </div>
      </template>
    </div>

    <!-- Travelers Summary -->
    <div class="p-6 border-b border-slate-100">
      <div class="flex flex-col gap-3">
        <div class="flex justify-between items-center text-sm">
          <span class="text-slate-600">Adults ({{ adultCount }})</span>
          <span class="text-slate-900 font-semibold">₱{{ (adultTotal || 0).toLocaleString() }}</span>
        </div>
        
        <div v-if="childCount > 0" class="flex justify-between items-center text-sm">
          <span class="text-slate-600">Children ({{ childCount }})</span>
          <span class="text-slate-900 font-semibold">₱{{ (childTotal || 0).toLocaleString() }}</span>
        </div>
        
        <div v-if="infantCount > 0" class="flex justify-between items-center text-sm">
          <span class="text-slate-600">Infants ({{ infantCount }})</span>
          <span class="text-slate-900 font-semibold">₱{{ (infantTotal || 0).toLocaleString() }}</span>
        </div>
      </div>
      
      <!-- Infant Assignment Note -->
      <div v-if="infantCount > 0" class="mt-4 pt-4 border-t border-slate-50">
        <span class="text-[11px] text-slate-500 italic">Infants will sit on an adult's lap</span>
      </div>
    </div>

    <!-- Total -->
    <div class="p-6 bg-slate-50 text-right">
      <div class="flex justify-between items-center mb-1">
        <span class="text-base font-bold text-slate-900">Total Amount</span>
        <span class="text-xl font-bold text-pink-500">₱{{ (totalAmount || 0).toLocaleString() }}</span>
      </div>
      <div class="text-[10px] text-slate-400">Taxes & fees calculated at review</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isMultiCity: Boolean,
  multiCitySegments: Array,
  selectedFlight: Object,
  selectedReturn: Object,
  isRoundTrip: Boolean,
  adultCount: Number,
  childCount: Number,
  infantCount: Number,
  adultTotal: Number,
  childTotal: Number,
  infantTotal: Number,
  totalAmount: Number
});
</script>
