<template>
  <aside class="w-full md:sticky md:top-24 h-fit space-y-4">
    <!-- Desktop Sidebar (md and up) -->
    <div class="hidden md:block bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm transition-all duration-300">
      <!-- Header -->
      <div class="p-6 border-b border-slate-200 bg-slate-50/50">
        <h2 class="text-sm font-black text-slate-800 uppercase tracking-widest mb-1">Travelers</h2>
        <div class="flex items-center justify-between">
          <div class="text-[10px] text-slate-500 font-bold uppercase">{{ totalTravelers }} Total</div>
          <div class="text-[10px] text-emerald-600 font-black uppercase">{{ completedCount }} Done</div>
        </div>
        
        <!-- Progress Bar -->
        <div class="mt-4 h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div 
            class="h-full bg-emerald-500 rounded-full transition-all duration-500 ease-out shadow-[0_0_8px_rgba(16,185,129,0.4)]" 
            :style="{ width: completionPercentage + '%' }"
          ></div>
        </div>
      </div>
      
      <!-- Passenger List -->
      <div class="divide-y divide-slate-100">
        <div 
          v-for="n in totalTravelers" 
          :key="n"
          class="flex items-center px-6 py-4 cursor-pointer transition-all relative group"
          :class="[
            activeIndex === n ? 'bg-pink-50/40' : 'hover:bg-slate-50/50',
          ]"
          @click="$emit('select', n)"
        >
          <!-- Active Indicator Bar -->
          <div 
            v-if="activeIndex === n"
            class="absolute left-0 top-0 bottom-0 w-1 bg-pink-500 rounded-r-full"
          ></div>

          <!-- Status Icon / Number -->
          <div 
            class="w-8 h-8 flex items-center justify-center rounded-lg text-xs font-black mr-4 shrink-0 transition-all duration-300"
            :class="[
              isPassengerComplete(n) 
                ? 'bg-emerald-100 text-emerald-600' 
                : activeIndex === n 
                  ? 'bg-pink-500 text-white shadow-lg shadow-pink-200' 
                  : 'bg-slate-100 text-slate-400 group-hover:bg-slate-200'
            ]"
          >
            <svg v-if="isPassengerComplete(n)" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
            </svg>
            <span v-else>{{ n }}</span>
          </div>
          
          <div class="flex-1 min-w-0">
            <div 
              class="text-sm font-bold transition-colors truncate"
              :class="[
                activeIndex === n ? 'text-pink-600' : 'text-slate-700',
                getPassengerType(n) === 'Infant' ? 'text-amber-600' : ''
              ]"
            >
              {{ getPassengerType(n) }} {{ n }}
            </div>
            
            <div class="flex items-center gap-1.5 mt-0.5">
              <template v-if="isPassengerComplete(n)">
                <span class="text-[9px] font-black text-emerald-500 uppercase tracking-tighter">Verified</span>
              </template>
              <template v-else-if="hasPassengerError(n)">
                <span class="text-[9px] font-black text-pink-500 uppercase tracking-tighter flex items-center gap-1">
                  <span class="w-1 h-1 rounded-full bg-pink-500 animate-pulse"></span> Requires Attention
                </span>
              </template>
              <template v-else>
                <span class="text-[9px] font-black text-slate-400 uppercase tracking-tighter">Pending</span>
              </template>
            </div>
          </div>
          
          <!-- Type Specific Badge -->
          <div v-if="getPassengerType(n) === 'Infant'" class="ml-2">
            <div class="w-5 h-5 rounded-full bg-amber-100 flex items-center justify-center text-amber-600" title="Infant">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2a2 2 0 00-2 2v1h4V4a2 2 0 00-2-2zM8 7h4v2a2 2 0 01-2 2 2 2 0 01-2-2V7z"/><path fill-rule="evenodd" d="M5 8.85s0 1.02.01 1.02a6.99 6.99 0 001.37 3.57c.64.93 1.49 1.7 2.47 2.22.14.07.3.11.45.14v1.2a1 1 0 102 0v-1.2c.15-.03.31-.07.45-.14a7.04 7.04 0 002.47-2.22 6.99 6.99 0 001.37-3.57c.01 0 .01-1.02.01-1.02H5z" clip-rule="evenodd"/></svg>
            </div>
          </div>
          
          <div 
            class="ml-3 text-slate-300 group-hover:text-slate-400 transition-transform duration-300"
            :class="{ 'translate-x-1 text-pink-400': activeIndex === n }"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </div>
        </div>
      </div>
      
      <!-- Infant Assignment Status -->
      <div v-if="infantCount > 0" class="p-4 bg-amber-50/50 border-t border-slate-100">
        <div class="flex items-start gap-2.5">
          <div class="w-5 h-5 rounded-full bg-amber-100 flex items-center justify-center text-amber-600 shrink-0 mt-0.5">
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
          <div class="min-w-0">
            <h4 class="text-[10px] font-black text-amber-800 uppercase tracking-widest leading-none mb-1">Infant Setup</h4>
            <p v-if="allInfantsAssigned" class="text-[10px] text-amber-600 font-medium">All assigned to adults</p>
            <p v-else class="text-[10px] text-pink-600 font-bold">{{ unassignedInfantsCount }} need lap assignment</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Horizontal Nav (visible on small screens) -->
    <div class="md:hidden bg-white border-b border-slate-200 sticky top-[72px] z-20 -mx-5 px-5 py-3 overflow-x-auto no-scrollbar flex gap-3 shadow-sm shadow-slate-100/50">
      <div 
        v-for="n in totalTravelers" 
        :key="'mob-'+n"
        class="flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-xl transition-all border"
        :class="[
          activeIndex === n ? 'bg-pink-500 border-pink-500 text-white shadow-md shadow-pink-200' : 'bg-slate-50 border-slate-200 text-slate-600'
        ]"
        @click="$emit('select', n)"
      >
        <div 
          class="w-5 h-5 flex items-center justify-center rounded-md text-[9px] font-black transition-colors"
          :class="[
            isPassengerComplete(n) 
              ? 'bg-emerald-400 text-white' 
              : activeIndex === n ? 'bg-white/20 text-white' : 'bg-slate-200 text-slate-500'
          ]"
        >
          <svg v-if="isPassengerComplete(n)" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="4" d="M5 13l4 4L19 7" />
          </svg>
          <span v-else>{{ n }}</span>
        </div>
        <span class="text-[10px] font-black uppercase tracking-widest whitespace-nowrap">{{ getPassengerType(n) }}</span>
      </div>
    </div>
    
    <!-- Help Card (Desktop only) -->
    <div class="hidden md:block p-5 rounded-xl bg-gradient-to-br from-slate-800 to-slate-900 text-white shadow-lg overflow-hidden relative">
      <div class="absolute -right-4 -bottom-4 w-24 h-24 bg-white/5 rounded-full blur-2xl"></div>
      <h3 class="text-xs font-black uppercase tracking-[0.2em] mb-3 text-slate-400">Need Help?</h3>
      <p class="text-[11px] text-slate-300 leading-relaxed mb-4">Make sure names match your official documents or passport exactly.</p>
      <button class="w-full py-2 bg-white/10 hover:bg-white/20 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-colors border border-white/10">View Policies</button>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  totalTravelers: {
    type: Number,
    required: true
  },
  activeIndex: {
    type: Number,
    required: true
  },
  infantCount: {
    type: Number,
    default: 0
  },
  completedCount: {
    type: Number,
    required: true
  },
  completionPercentage: {
    type: Number,
    required: true
  },
  allInfantsAssigned: {
    type: Boolean,
    default: true
  },
  unassignedInfantsCount: {
    type: Number,
    default: 0
  },
  isPassengerComplete: {
    type: Function,
    required: true
  },
  hasPassengerError: {
    type: Function,
    required: true
  },
  getPassengerType: {
    type: Function,
    required: true
  },
  getInfantAdultName: {
    type: Function,
    required: true
  }
});

defineEmits(['select']);
</script>
