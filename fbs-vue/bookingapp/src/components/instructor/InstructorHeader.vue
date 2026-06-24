<template>
  <header class="bg-white text-gray-800 px-4 py-2.5 flex items-center justify-between z-20  border-b border-gray-100">
    <div class="flex items-center gap-3">
      <button 
        @click="$emit('toggle-sidebar')" 
        class="p-1.5 hover:bg-gray-500/20 cursor-pointer rounded transition-colors focus:outline-none"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </button>
      
      <div class="flex items-center gap-2">
        <div class="w-10 h-10 rounded-full flex items-center justify-center overflow-hidden">
          <img :src="CTHM" alt="CTHM Logo" class="w-full h-full object-contain">
        </div>
        <div class="font-sans">
          <div class="text-[10px] sm:text-xs font-bold leading-tight text-gray-900">College of Tourism and Hospitality Management</div>
          <div class="text-[8px] sm:text-[9px] text-green-800 font-medium opacity-90 leading-tight">CARAGA STATE UNIVERSITY - CABADBARAN CITY</div>
        </div>
      </div>
    </div>

    <div class="flex items-center gap-4 relative">
      <!-- Notification Bell -->
      <div class="relative">
        <button 
          @click="$emit('toggle-notifications')" 
          class="p-2 hover:bg-pink-50 text-gray-400 hover:text-pink-600 rounded-full transition-colors relative focus:outline-none group"
          :class="{ 
            'bg-pink-50 text-pink-600': notificationsOpen,
            'animate-shake': unseenCount > 0 && !notificationsOpen
          }"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <div v-if="unseenCount > 0" class="absolute -top-0.5 -right-0.5 flex items-center justify-center">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-pink-400 opacity-75"></span>
            <span class="relative flex items-center justify-center min-w-[18px] h-[18px] bg-red-500 text-white text-[10px] font-black rounded-full border border-white shadow-sm px-1">
              {{ unseenCount }}
            </span>
          </div>
        </button>

        <!-- Notification Dropdown -->
        <div v-if="notificationsOpen" class="absolute right-0 mt-2 w-72 bg-white rounded-2xl shadow-2xl py-2 z-[60] border border-gray-100 overflow-hidden animate-in slide-in-from-top-2 duration-200">
          <div class="px-4 py-2 border-b border-gray-50 flex items-center justify-between bg-slate-50/50">
            <span class="text-[10px] font-black uppercase tracking-widest text-slate-500">Scheduled Notifications</span>
            <span v-if="notifications.length > 0" class="text-[9px] bg-pink-100 text-pink-600 px-1.5 py-0.5 rounded-full font-black uppercase tracking-widest">Today</span>
          </div>
          
          <div class="max-h-80 overflow-y-auto">
            <div v-if="notifications.length === 0" class="p-10 text-center">
              <div class="w-12 h-12 bg-slate-50 rounded-2xl flex items-center justify-center mx-auto mb-3 rotate-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
              </div>
              <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">No notifications yet</p>
            </div>
            
            <div 
              v-for="s in notifications" 
              :key="s.id"
              class="px-4 py-4 hover:bg-slate-50 transition-all border-b border-gray-50 last:border-0 group relative"
              :class="{ 'opacity-85 bg-slate-50/40': s.read }"
            >
              <div class="flex items-start gap-4">
                <div :class="[
                  'w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 font-bold text-xs shadow-sm transition-transform group-hover:scale-110',
                  s.type === 'missed' ? 'bg-red-50 text-red-500 border border-red-100' : 'bg-emerald-50 text-emerald-600 border border-emerald-100',
                  { 'grayscale opacity-70': s.read }
                ]">
                  {{ s.sectionName.charAt(0) }}
                </div>
                <div class="flex-1 text-left">
                  <div class="flex justify-between items-start mb-0.5">
                    <p class="text-[11px] font-black text-slate-800 uppercase tracking-tight" :class="{ 'text-slate-500': s.read }">{{ s.sectionName }}</p>
                    <div class="flex justify-end">
                      <span v-if="s.read" class="text-[8px] font-black text-slate-400 uppercase tracking-widest bg-slate-100 px-1.5 py-0.5 rounded flex items-center gap-1">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-2.5 w-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                        </svg>
                        Checked
                      </span>
                      <span v-else :class="[
                        'text-[8px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded',
                        s.type === 'missed' ? 'text-red-500 bg-red-50' : 'text-emerald-500 bg-emerald-50'
                      ]">
                        {{ s.type }}
                      </span>
                    </div>
                  </div>
                  <p class="text-[10px] text-slate-500 font-medium leading-normal italic" :class="{ 'text-slate-400': s.read }">
                    {{ s.displayMessage }}
                  </p>
                  <div class="flex items-center gap-2 mt-2">
                     <span class="text-[9px] font-bold text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">{{ formatTimeOnly(s.start_time) }}</span>
                     <span class="text-[9px] font-bold text-slate-300">→</span>
                     <span class="text-[9px] font-bold text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">{{ formatTimeOnly(s.end_time) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="relative">
        <button 
          @click="$emit('toggle-dropdown')" 
          class="flex items-center gap-2 hover:bg-pink-600/10 px-1 py-1 rounded-full transition-colors focus:outline-none"
        >
          <span class="text-xs font-medium text-gray-700 hidden sm:block">{{ fullName }}</span>
          <div class="w-8 h-8 bg-[#F9F9F9] rounded-full flex items-center justify-center overflow-hidden border-2 border-white shadow-sm ring-1 ring-gray-100">
             <img v-if="profilePicture" :src="profilePicture" class="w-full h-full object-cover" alt="Profile">
             <div v-else class="w-full h-full bg-pink-200 rounded-full flex items-center justify-center text-pink-700 text-xs font-bold uppercase">{{ initials }}</div>
          </div>
        </button>

        <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl py-1 z-50 border border-gray-100">
           <div class="px-4 py-3 border-b border-gray-100">
             <p class="text-sm font-semibold text-gray-800">{{ fullName }}</p>
           </div>
           <button @click="$emit('go-to-profile')" class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">My Profile</button>
           <button @click="$emit('logout')" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors">Logout</button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import CTHM from '@/assets/image/cthm-logos.png'

const props = defineProps({
  fullName: String,
  initials: String,
  profilePicture: String,
  dropdownOpen: Boolean,
  notificationsOpen: Boolean,
  unseenCount: Number,
  notifications: Array
})

const emit = defineEmits([
  'toggle-sidebar', 
  'toggle-dropdown', 
  'toggle-notifications', 
  'go-to-profile', 
  'logout'
])

const formatTimeOnly = (t) => {
  if (!t) return ''
  const [h, m] = t.split(':')
  const hour = parseInt(h)
  const ampm = hour >= 12 ? 'PM' : 'AM'
  const h12 = hour % 12 || 12
  return `${h12}:${m} ${ampm}`
}
</script>

<style scoped>
@keyframes shake {
  0%, 100% { transform: rotate(0deg); }
  20% { transform: rotate(8deg); }
  40% { transform: rotate(-8deg); }
  60% { transform: rotate(8deg); }
  80% { transform: rotate(-8deg); }
}

.animate-shake {
  animation: shake 0.6s cubic-bezier(.36,.07,.19,.97) both;
  animation-iteration-count: infinite;
  transform-origin: center top;
}
</style>
