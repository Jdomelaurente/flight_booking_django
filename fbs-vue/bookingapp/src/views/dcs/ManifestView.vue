<template>
  <div class="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-700">
    <!-- Back + Stats Row -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
      <button
        @click="router.push('/dcs/dashboard')"
        class="group flex items-center gap-3 text-sm font-black text-slate-400 hover:text-pink-600 transition-all uppercase tracking-widest"
      >
        <div class="w-8 h-8 rounded-full bg-white border border-slate-200 flex items-center justify-center group-hover:bg-pink-50 group-hover:border-pink-200 transition-all">
          <svg class="w-4 h-4 transition-transform group-hover:-translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M15 19l-7-7 7-7"/>
          </svg>
        </div>
        Terminal Dashboard
      </button>

      <div class="flex flex-wrap items-center gap-3">
        <!-- Scan QR Button -->
        <button
          @click="showScanner = true"
          class="bg-slate-900 border-2 border-slate-800 hover:bg-black text-white text-[11px] font-black uppercase tracking-[0.2em] px-6 py-3 rounded-lg shadow-sm cursor-pointer transition-all shadow-xl shadow-slate-200 flex items-center gap-3 group active:scale-95"
        >
          <svg class="w-4 h-4 text-pink-400 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M3 9V6a3 3 0 013-3h3M15 3h3a3 3 0 013 3v3M3 15v3a3 3 0 003 3h3M15 21h3a3 3 0 003-3v-3M7 7h10v10H7z"/>
          </svg>
          Optical Scan
        </button>

        <div class="h-10 w-px bg-slate-200 mx-2 hidden lg:block"></div>

        <div class="flex items-center gap-2">
          <div class="bg-white border border-slate-200 rounded-[5px] p-1.5 flex shadow-sm">
            <div class="px-4 py-2 text-center min-w-[80px] bg-slate-50 rounded-[2px]">
              <div class="text-[9px] text-slate-400 font-black uppercase tracking-tighter">Total</div>
              <div class="text-lg font-black text-slate-900 leading-none">{{ dcsStore.totalPassengers }}</div>
            </div>
            <div class="px-4 py-2 text-center min-w-[80px]">
              <div class="text-[9px] text-pink-500 font-black uppercase tracking-tighter">Onboard</div>
              <div class="text-lg font-black text-pink-600 leading-none">{{ dcsStore.checkedInPassengers }}</div>
            </div>
            <div class="px-4 py-2 text-center min-w-[80px]">
              <div class="text-[9px] text-amber-500 font-black uppercase tracking-tighter">Pending</div>
              <div class="text-lg font-black text-amber-600 leading-none">{{ dcsStore.pendingPassengers }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MODERN SEARCH / FILTER -->
    <div class="bg-white border border-slate-200 rounded-[5px] p-2.5 shadow-sm flex items-center gap-4 group focus-within:ring-2 focus-within:ring-pink-500/10 transition-all">
      <div class="w-10 h-10 bg-slate-50 rounded-[2px] flex items-center justify-center text-slate-400 shrink-0 group-focus-within:text-pink-600 transition-colors">
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </div>
      <input
        type="text"
        v-model="searchQuery"
        placeholder="Input PNR or Passenger Name for terminal look-up..."
        class="flex-1 text-sm font-bold text-slate-700 placeholder-slate-400 outline-none bg-transparent"
      >
      <div class="pr-4">
         <span class="text-[10px] font-black text-slate-300 uppercase tracking-widest hidden md:block">Active Manifest Terminal</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="dcsStore.error" class="bg-rose-50 border border-rose-200 rounded-[5px] p-5 text-rose-700 text-sm font-bold flex items-center gap-4 shadow-sm">
      <div class="w-10 h-10 bg-rose-100 rounded-[2px] flex items-center justify-center shrink-0">⚠️</div>
      {{ dcsStore.error }}
    </div>

    <!-- Loading Skeleton -->
    <div v-if="dcsStore.isLoading && !dcsStore.manifest.length" class="space-y-3 animate-pulse">
      <div class="h-14 bg-slate-100 rounded-[2px] border border-slate-200"></div>
      <div v-for="i in 8" :key="i" class="h-20 bg-white rounded-[2px] border border-slate-100 opacity-60"></div>
    </div>

    <!-- MANIFEST GRID/TABLE -->
    <div v-else class="bg-white rounded-[5px] border border-slate-200 shadow-xl shadow-slate-200/50 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50/50">
              <th class="px-8 py-5 group cursor-pointer" @click="sortBy('pnr')">
                <div class="flex items-center gap-2">
                  <span class="text-[10px] text-slate-400 font-black uppercase tracking-widest">PNR / Ref</span>
                  <span v-if="sortKey === 'pnr'" class="text-pink-500 font-black">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </div>
              </th>
              <th class="px-8 py-5 group cursor-pointer" @click="sortBy('passenger_name')">
                <div class="flex items-center gap-2">
                  <span class="text-[10px] text-slate-400 font-black uppercase tracking-widest">Traveller Identity</span>
                  <span v-if="sortKey === 'passenger_name'" class="text-pink-500 font-black">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </div>
              </th>
              <th class="px-8 py-5 hidden md:table-cell">
                <span class="text-[10px] text-slate-400 font-black uppercase tracking-widest">Class / Type</span>
              </th>
              <th class="px-8 py-5 cursor-pointer" @click="sortBy('seat')">
                <div class="flex items-center gap-2">
                  <span class="text-[10px] text-slate-400 font-black uppercase tracking-widest">Slot</span>
                  <span v-if="sortKey === 'seat'" class="text-pink-500 font-black">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
                </div>
              </th>
              <th class="px-8 py-5">
                <span class="text-[10px] text-slate-400 font-black uppercase tracking-widest">Handling Status</span>
              </th>
              <th class="px-8 py-5 text-right">
                <span class="text-[10px] text-slate-400 font-black uppercase tracking-widest">Protocol</span>
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50">
            <template v-if="filteredAndSortedManifest.length > 0">
              <tr
                v-for="passenger in filteredAndSortedManifest"
                :key="passenger.booking_detail_id"
                class="hover:bg-pink-50/30 transition-all duration-300 group"
                :class="{ 'bg-pink-50/40': highlightedPnr && passenger.pnr === highlightedPnr }"
              >
                <!-- PNR -->
                <td class="px-8 py-6">
                  <div class="flex flex-col">
                    <span class="font-mono font-black text-slate-900 tracking-widest group-hover:text-pink-600 transition-colors uppercase">{{ passenger.pnr }}</span>
                    <span class="text-[9px] text-slate-400 font-bold uppercase tracking-tighter mt-1 italic">DOMESTIC ISSUANCE</span>
                  </div>
                </td>

                <!-- Passenger Identity -->
                <td class="px-8 py-6">
                  <div class="flex items-center gap-4">
                    <div class="w-10 h-10 bg-slate-100 rounded-[2px] flex items-center justify-center text-slate-400 group-hover:bg-pink-100 group-hover:text-pink-600 transition-colors">
                      <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <div>
                      <div class="flex items-center gap-2">
                        <span class="font-black text-slate-900 tracking-tight leading-none group-hover:text-pink-700 transition-colors">{{ passenger.passenger_name }}</span>
                        <!-- SSR Icons Strip -->
                        <div v-if="passenger.ssrs" class="flex gap-1">
                           <span v-if="passenger.ssrs.is_premium" class="text-[10px] bg-amber-100 text-amber-700 px-1 rounded font-black">PREM</span>
                           <span v-if="passenger.ssrs.meal" class="text-[11px]" title="Catering Reserved">🍽️</span>
                           <span v-if="passenger.ssrs.assistance" class="text-[11px]" title="Special Assistance">♿</span>
                        </div>
                      </div>
                      <div class="flex items-center gap-2 mt-1.5">
                        <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest">{{ passenger.passenger_type }}</span>
                        <div v-if="passenger.allowed_baggage_weight > 0" class="flex items-center gap-1">
                          <span class="w-1 h-1 bg-slate-200 rounded-full"></span>
                          <span class="text-[9px] font-black text-pink-500 uppercase tracking-tighter">{{ passenger.allowed_baggage_weight }} KG ALLOWANCE</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </td>

                <!-- Class -->
                <td class="px-8 py-6 hidden md:table-cell">
                   <div class="flex flex-col">
                     <span class="text-[11px] font-black text-slate-600 uppercase tracking-widest">{{ passenger.passenger_type === 'Adult' ? 'CABIN-Y' : 'CABIN-J' }}</span>
                     <span class="text-[9px] text-slate-300 font-bold mt-0.5 uppercase">PH-Domestic</span>
                   </div>
                </td>

                <!-- Seat Slot -->
                <td class="px-8 py-6">
                   <div class="flex flex-col">
                     <span class="font-mono font-black text-lg text-slate-900 leading-none group-hover:text-pink-600 transition-colors">{{ passenger.seat || 'TBA' }}</span>
                     <span class="text-[9px] text-slate-400 font-bold uppercase tracking-widest mt-1">Confirmed</span>
                   </div>
                </td>

                <!-- Status Badge -->
                <td class="px-8 py-6">
                   <div :class="[
                     'inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border-2 transition-all',
                     passenger.status === 'checkin' || passenger.status === 'boarding'
                       ? 'bg-emerald-50 text-emerald-700 border-emerald-100 shadow-sm'
                       : 'bg-amber-50 text-amber-700 border-amber-100'
                   ]">
                      <span class="w-1.5 h-1.5 rounded-full" :class="passenger.status === 'checkin' || passenger.status === 'boarding' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)] animate-pulse' : 'bg-amber-400'"></span>
                      {{ passenger.status === 'checkin' ? 'Onboard' : passenger.status === 'boarding' ? 'Gate Boarding' : 'Manifest Pending' }}
                   </div>
                </td>

                <!-- Action Protocol -->
                <td class="px-8 py-6 text-right whitespace-nowrap">
                  <button
                    v-if="passenger.status !== 'checkin' && passenger.status !== 'boarding'"
                    @click="openCheckin(passenger)"
                    class="bg-pink-600 hover:bg-slate-900 text-white text-[10px] font-black uppercase tracking-[0.1em] px-4 py-2.5 rounded-[2px] transition-all shadow-lg shadow-pink-100 hover:shadow-slate-300 active:scale-95"
                  >
                    Initiate Check-in
                  </button>
                  <button
                    v-else
                    @click="reprintBoardingPass(passenger)"
                    class="bg-white border-2 border-slate-100 text-slate-600 hover:border-pink-500/30 hover:text-pink-600 text-[10px] font-black uppercase tracking-[0.1em] px-4 py-2.5 rounded-[2px] transition-all shadow-sm flex items-center gap-2 ml-auto"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                    </svg>
                    Reprint Pass
                  </button>
                </td>
              </tr>
            </template>
            <tr v-else>
              <td colspan="7" class="px-8 py-20 text-center">
                <div class="flex flex-col items-center">
                   <div class="text-6xl opacity-10 mb-6 grayscale text-pink-600">🔍</div>
                   <h4 class="text-xl font-black text-slate-400 tracking-tight italic text-pink-900/40">No Matching Terminal Records</h4>
                   <p class="text-[10px] font-black text-slate-300 uppercase tracking-widest mt-2">Verify search parameters or PNR integrity</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- TERMINAL FOOTER: System Status -->
      <div class="px-8 py-4 bg-slate-50 border-t border-slate-100 flex flex-col md:flex-row justify-between items-center gap-4">
        <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">
           Syncing {{ filteredAndSortedManifest.length }} of {{ dcsStore.totalPassengers }} System Nodes
        </span>
        <button 
          @click="refreshManifest" 
          class="flex items-center gap-3 bg-white border border-slate-200 px-4 py-2.5 rounded-[5px] hover:bg-pink-50 hover:border-pink-100 transition-all text-[10px] font-black text-slate-500 hover:text-pink-600 shadow-sm"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" :class="{ 'animate-spin': dcsStore.isLoading }">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
          FORCE DATA RE-SYNC
        </button>
      </div>
    </div>

    <!-- SCANNER MODULE -->
    <QrScannerModal
      v-if="showScanner"
      :schedule-id="schedule_id"
      @close="showScanner = false"
      @passenger-selected="handleScanResult"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDcsStore } from '@/stores/dcs'
import QrScannerModal from '@/components/dcs/QrScannerModal.vue'

const props = defineProps({
  schedule_id: { type: [String, Number], required: true }
})

const router = useRouter()
const route = useRoute()
const dcsStore = useDcsStore()

const searchQuery = ref('')
const sortKey = ref('passenger_name')
const sortOrder = ref('asc')
const showScanner = ref(false)
const highlightedPnr = ref(null)

onMounted(() => {
  dcsStore.fetchManifest(props.schedule_id)
  
  // If we just came back from a successful check-in, highlight that passenger
  if (route.query.checkedin) {
    const pId = route.query.checkedin
    highlightedPnr.value = pId // highlight the returned PNR in the table
    setTimeout(() => { highlightedPnr.value = null }, 4000) // clear after 4s
  }
})

const refreshManifest = () => dcsStore.fetchManifest(props.schedule_id)

const sortBy = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

const filteredAndSortedManifest = computed(() => {
  let result = dcsStore.manifest || []
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(p =>
      (p.passenger_name?.toLowerCase().includes(q)) ||
      (p.pnr?.toLowerCase().includes(q))
    )
  }
  return [...result].sort((a, b) => {
    let va = (a[sortKey.value] || '').toString().toLowerCase()
    let vb = (b[sortKey.value] || '').toString().toLowerCase()
    if (va < vb) return sortOrder.value === 'asc' ? -1 : 1
    if (va > vb) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
})

const openCheckin = (p) => { 
  router.push(`/dcs/checkin/${p.booking_detail_id}`)
}

const handleScanResult = (passenger) => {
  showScanner.value = false
  openCheckin(passenger)
}

const reprintBoardingPass = (p) => {
  // Bug fix: Use relative URL instead of hardcoded localhost
  window.open(`/flightapp/download-boarding-pass/${p.booking_detail_id}/`, '_blank')
}
</script>

<style scoped>
/* Scoped styles replaced by Tailwind v4 */
</style>
