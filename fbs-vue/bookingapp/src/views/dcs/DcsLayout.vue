<template>
  <div class="flex flex-col h-screen bg-[#FDF2F8]/30 font-sans text-slate-900 overflow-hidden">
    <!-- MODERN AVIATION HEADER -->
    <header :class="['text-white px-6 py-3.5 flex items-center justify-between shadow-lg z-30 shrink-0 border-b transition-colors duration-500', theme.headerBg, theme.headerBorder]">
      <div class="flex items-center gap-4">
        <!-- Logo/Icon -->
        <div :class="['w-9 h-9 rounded-[5px] flex items-center justify-center shadow-lg text-lg transition-colors duration-500', theme.logoBg, theme.logoShadow]">
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
          </svg>
        </div>
        <div class="flex flex-col">
          <h1 :class="['text-xs font-black tracking-[0.2em] leading-tight uppercase transition-colors duration-500', theme.titleText]">{{ dcsStore.activeAirline ? dcsStore.activeAirline + ' DCS' : 'Aviation Terminal' }}</h1>
          <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest leading-tight mt-0.5">DCS Agent Simulation Portal</p>
        </div>
      </div>

      <div class="flex items-center gap-6">
        <!-- Clock -->
        <div class="flex flex-col items-end">
          <span class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-0.5">Local Server Time</span>
          <div :class="['text-sm font-black font-mono tracking-tighter transition-colors duration-500', theme.clockText]">{{ currentTime }}</div>
        </div>

        <div class="h-8 w-px bg-white/10 hidden sm:block"></div>

        <!-- System State -->
        <div class="hidden md:flex items-center gap-3">
          <div class="flex flex-col items-end">
            <span class="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-0.5">Network Status</span>
            <div class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)] animate-pulse"></span>
              <span class="text-[10px] font-bold text-slate-300 uppercase tracking-wider">Secure Connection</span>
            </div>
          </div>
        </div>

        <div class="h-8 w-px bg-white/10"></div>

        <!-- Exit Button -->
        <button
          @click="exitDcs"
          :class="['flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-[2px] transition-all duration-300 border border-slate-700 group', theme.hoverBorder]"
        >
          <span class="text-[10px] font-black text-slate-300 group-hover:text-white uppercase tracking-widest">Logout</span>
          <svg :class="['w-4 h-4 text-slate-400 transition-colors', theme.hoverText]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </div>
    </header>


    <!-- CONTENT AREA -->
    <main class="flex-1 overflow-y-auto px-8 py-8 relative">
      <!-- Grid/Pattern Background Overlay -->
      <div class="absolute inset-0 opacity-[0.03] pointer-events-none transition-colors duration-500" :style="theme.gridStyle"></div>
      
      <div class="max-w-7xl mx-auto relative z-10 transition-all duration-500">
        <!-- AIRLINE SELECTION MODAL -->
        <div v-if="!dcsStore.activeAirline" class="absolute inset-0 z-50 flex items-center justify-center pt-20">
           <div class="bg-white p-10 shadow-2xl rounded-[5px] border border-slate-200 w-full max-w-2xl animate-in slide-in-from-bottom-8 duration-500">
              <h2 class="text-3xl font-black text-slate-900 tracking-tighter italic mb-2">Select Operator Station</h2>
              <p class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-8">Choose the airline system you will operate for this session.</p>
              
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                 <!-- PAL -->
                 <button @click="selectAirline('Philippine Airlines')" class="group flex flex-col items-center justify-center p-6 border-2 border-slate-100 hover:border-blue-600 rounded-[5px] transition-all hover:bg-blue-50/50 hover:-translate-y-2 hover:shadow-xl hover:shadow-blue-600/10">
                    <div class="w-16 h-16 bg-blue-900 text-white flex items-center justify-center font-black text-xl rounded shadow-md group-hover:scale-110 transition-transform mb-4">PR</div>
                    <span class="text-xs font-black text-slate-700 uppercase tracking-tight group-hover:text-blue-900 text-center">Philippine Airlines</span>
                 </button>
                 <!-- CEB -->
                 <button @click="selectAirline('Cebu Pacific')" class="group flex flex-col items-center justify-center p-6 border-2 border-slate-100 hover:border-orange-500 rounded-[5px] transition-all hover:bg-orange-50/50 hover:-translate-y-2 hover:shadow-xl hover:shadow-orange-500/10">
                    <div class="w-16 h-16 bg-orange-500 text-white flex items-center justify-center font-black text-xl rounded shadow-md group-hover:scale-110 transition-transform mb-4">5J</div>
                    <span class="text-xs font-black text-slate-700 uppercase tracking-tight group-hover:text-orange-900 text-center">Cebu Pacific</span>
                 </button>
                 <!-- AirAsia -->
                 <button @click="selectAirline('AirAsia Philippines')" class="group flex flex-col items-center justify-center p-6 border-2 border-slate-100 hover:border-red-600 rounded-[5px] transition-all hover:bg-red-50/50 hover:-translate-y-2 hover:shadow-xl hover:shadow-red-600/10">
                    <div class="w-16 h-16 bg-red-600 text-white flex items-center justify-center font-black text-xl rounded shadow-md group-hover:scale-110 transition-transform mb-4">Z2</div>
                    <span class="text-xs font-black text-slate-700 uppercase tracking-tight group-hover:text-red-900 text-center">AirAsia Philippines</span>
                 </button>
              </div>
           </div>
        </div>

        <div v-else class="h-full w-full relative -z-0">
          <router-view v-slot="{ Component }">
            <transition 
              name="fade-slide" 
              mode="out-in"
            >
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </div>
    </main>

    <!-- MINI FOOTER STATUS -->
    <footer class="bg-white border-t border-slate-200 px-6 py-2 flex items-center justify-between shrink-0 z-20">
       <div class="flex items-center gap-4">
         <div class="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
           <span class="w-1.5 h-1.5 rounded-full bg-pink-500"></span>
           Active Session
         </div>
       </div>
       <div class="text-[10px] font-medium text-slate-400">
         v3.0.0-DCS · Departure Control Management System
       </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDcsStore } from '@/stores/dcs'

const router = useRouter()
const route = useRoute()
const dcsStore = useDcsStore()

const currentTime = ref('')
let timer

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  // Ensure flights are loaded for the sidebar or selection
  if (dcsStore.flights.length === 0) {
    dcsStore.fetchFlights()
  }
})

onUnmounted(() => {
  clearInterval(timer)
})

const selectAirline = (airlineName) => {
  dcsStore.setActiveAirline(airlineName)
}

const theme = computed(() => {
  if (dcsStore.activeAirline === 'Philippine Airlines') {
    return {
      headerBg: 'bg-[#002244]', headerBorder: 'border-blue-500/30',
      logoBg: 'bg-gradient-to-br from-blue-600 to-blue-900', logoShadow: 'shadow-blue-500/20',
      titleText: 'text-blue-300', clockText: 'text-blue-100',
      hoverBorder: 'hover:border-blue-500/50', hoverText: 'group-hover:text-blue-400',
      gridStyle: 'background-image: linear-gradient(#2563eb 1px, transparent 1px), linear-gradient(90deg, #2563eb 1px, transparent 1px); background-size: 40px 40px;'
    }
  } else if (dcsStore.activeAirline === 'Cebu Pacific') {
    return {
      headerBg: 'bg-[#1E1B18]', headerBorder: 'border-orange-500/30',
      logoBg: 'bg-gradient-to-br from-orange-400 to-orange-600', logoShadow: 'shadow-orange-500/20',
      titleText: 'text-orange-400', clockText: 'text-orange-100',
      hoverBorder: 'hover:border-orange-500/50', hoverText: 'group-hover:text-orange-400',
      gridStyle: 'background-image: linear-gradient(#f97316 1px, transparent 1px), linear-gradient(90deg, #f97316 1px, transparent 1px); background-size: 40px 40px;'
    }
  } else if (dcsStore.activeAirline === 'AirAsia Philippines') {
    return {
      headerBg: 'bg-[#1A1A1A]', headerBorder: 'border-red-600/30',
      logoBg: 'bg-gradient-to-br from-red-600 to-red-800', logoShadow: 'shadow-red-600/20',
      titleText: 'text-red-500', clockText: 'text-red-100',
      hoverBorder: 'hover:border-red-600/50', hoverText: 'group-hover:text-red-500',
      gridStyle: 'background-image: linear-gradient(#dc2626 1px, transparent 1px), linear-gradient(90deg, #dc2626 1px, transparent 1px); background-size: 40px 40px;'
    }
  }
  
  // Default (No airline selected yet / Generic)
  return {
    headerBg: 'bg-[#0F172A]', headerBorder: 'border-pink-500/20',
    logoBg: 'bg-gradient-to-br from-pink-500 to-rose-700', logoShadow: 'shadow-pink-500/20',
    titleText: 'text-pink-400', clockText: 'text-pink-100',
    hoverBorder: 'hover:border-pink-500/50', hoverText: 'group-hover:text-pink-400',
    gridStyle: 'background-image: linear-gradient(#db2777 1px, transparent 1px), linear-gradient(90deg, #db2777 1px, transparent 1px); background-size: 40px 40px;'
  }
})

const exitDcs = () => {
  if (dcsStore.activeAirline && route.name !== 'DcsDashboard') {
      router.push('/dcs/dashboard')
      dcsStore.clearSelection()
  } else if (dcsStore.activeAirline && route.name === 'DcsDashboard') {
      dcsStore.setActiveAirline(null) // Logout of airline
  } else {
      router.push('/student/dashboard')
  }
}
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
