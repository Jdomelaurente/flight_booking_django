<template>
  <div class="fixed inset-0 bg-slate-900/60 backdrop-blur-md flex items-center justify-center p-4 z-[100] animate-in fade-in duration-300">
    <div class="bg-white rounded-[5px] shadow-2xl w-full max-w-lg overflow-hidden flex flex-col max-h-[88vh] border border-slate-200">

      <!-- Header -->
      <div class="bg-pink-600 px-8 py-5 flex justify-between items-center shrink-0 relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-r from-pink-500 to-pink-700 opacity-50"></div>
        <div class="relative z-10">
          <h3 class="text-white font-black text-xs uppercase tracking-[0.2em]">
             Optical Scanner
          </h3>
          <p class="text-pink-100 text-[10px] font-black uppercase tracking-widest mt-1 opacity-80 flex items-center gap-2">
            <span class="w-1 h-1 bg-white/30 rounded-full"></span>
            {{ dcsStore.selectedSchedule?.origin || 'MNL-T3' }} Terminal
          </p>
        </div>
        <button @click="handleClose" class="relative z-10 text-white/60 hover:text-white transition-all p-2 rounded-[2px] hover:bg-white/10 active:scale-90">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <div class="p-6 overflow-y-auto flex-1 space-y-6 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-slate-200">

        <!-- Tab Switcher: Camera / Manual -->
        <div class="flex bg-slate-100 rounded-[5px] p-1.5 gap-1 shadow-inner">
          <button
            @click="switchToCamera"
            :class="[
              'flex-1 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-2',
              activeTab === 'camera'
                ? 'bg-white text-pink-600 shadow-lg shadow-pink-100'
                : 'text-slate-400 hover:text-slate-600 hover:bg-white/50'
            ]"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
            </svg>
            Capture Mode
          </button>
          <button
            @click="switchToManual"
            :class="[
              'flex-1 py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-2',
              activeTab === 'manual'
                ? 'bg-white text-pink-600 shadow-lg shadow-pink-100'
                : 'text-slate-400 hover:text-slate-600 hover:bg-white/50'
            ]"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
            Command Input
          </button>
        </div>

        <!-- ===================== CAMERA TAB ===================== -->
        <div v-show="activeTab === 'camera'" class="animate-in fade-in zoom-in-95 duration-500">
          <!-- Camera Viewfinder -->
          <div class="relative rounded-[5px] overflow-hidden bg-slate-900 aspect-video shadow-2xl shadow-slate-200 border-4 border-slate-50">
            <div id="qr-reader" class="w-full h-full"></div>

            <!-- Scanning Overlay -->
            <div v-if="cameraActive && !scanResult" class="absolute inset-0 pointer-events-none">
              <div class="absolute top-8 left-8 w-12 h-12 border-t-4 border-l-4 border-pink-500 rounded-tl-[5px] opacity-60"></div>
              <div class="absolute top-8 right-8 w-12 h-12 border-t-4 border-r-4 border-pink-500 rounded-tr-[5px] opacity-60"></div>
              <div class="absolute bottom-8 left-8 w-12 h-12 border-b-4 border-l-4 border-pink-500 rounded-bl-[5px] opacity-60"></div>
              <div class="absolute bottom-8 right-8 w-12 h-12 border-b-4 border-r-4 border-pink-500 rounded-br-[5px] opacity-60"></div>
              
              <div class="absolute inset-x-12 h-0.5 bg-gradient-to-r from-transparent via-pink-400 to-transparent animate-scan-line rounded-full shadow-[0_0_15px_rgba(236,72,153,0.8)]"></div>
              
              <div class="absolute bottom-4 inset-x-0 text-center">
                <span class="bg-black/80 backdrop-blur-md text-white text-[8px] font-black uppercase tracking-[0.2em] px-3 py-1.5 rounded-[2px] border border-white/10">
                  Align Grid with Central Hub
                </span>
              </div>
            </div>

            <!-- Camera not started placeholder -->
            <div v-if="!cameraActive && !cameraError && !scanResult" class="absolute inset-0 flex flex-col items-center justify-center bg-slate-950 text-white/60">
              <div class="w-10 h-10 border-4 border-white/10 border-t-pink-500 rounded-full animate-spin mb-4"></div>
              <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">Initializing Optical Core...</span>
            </div>

            <!-- Camera error -->
            <div v-if="cameraError" class="absolute inset-0 flex flex-col items-center justify-center bg-slate-950 text-white/70 px-10">
              <div class="w-16 h-16 bg-rose-500/10 rounded-[5px] flex items-center justify-center text-rose-500 mb-6">
                <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/>
                </svg>
              </div>
              <span class="text-sm font-black uppercase tracking-tight text-white mb-2">Sensor Blocked</span>
              <span class="text-[10px] text-center text-slate-500 font-bold uppercase tracking-widest leading-relaxed mb-8">{{ cameraError }}</span>
              <button @click="switchToManual" class="bg-pink-600 hover:bg-slate-900 text-white text-[10px] font-black uppercase tracking-widest px-6 py-4 rounded-[5px] transition-all active:scale-95 shadow-lg shadow-pink-900/20">
                Switch to Manual Protocol
              </button>
            </div>
          </div>

          <!-- Scan success feedback -->
          <Transition
            enter-active-class="transition duration-300 ease-out"
            enter-from-class="opacity-0 translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
          >
            <div v-if="scanResult" class="mt-6 bg-emerald-50 border-2 border-emerald-100 rounded-[5px] p-5 flex items-center gap-4 shadow-sm shadow-emerald-100/50">
              <div class="w-12 h-12 bg-emerald-600 rounded-[2px] flex items-center justify-center text-white shrink-0 shadow-lg shadow-emerald-200">
                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                </svg>
              </div>
              <div class="min-w-0">
                <div class="text-[10px] font-black text-emerald-800 uppercase tracking-[0.1em]">Signal Verified</div>
                <div class="text-sm font-mono font-black text-emerald-900 truncate tracking-widest mt-0.5">{{ scanResult }}</div>
              </div>
              <button @click="resetAndRescan" class="ml-auto p-2 text-emerald-400 hover:text-emerald-700 transition-colors">
                 <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                   <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                 </svg>
              </button>
            </div>
          </Transition>
        </div>

        <!-- ===================== MANUAL TAB ===================== -->
        <div v-show="activeTab === 'manual'" class="animate-in fade-in slide-in-from-right-4 duration-500">
          <div class="border-2 border-dashed border-slate-200 bg-slate-50/50 rounded-[5px] p-8 text-center">
            <div class="w-20 h-20 bg-white shadow-xl rounded-[5px] flex items-center justify-center text-pink-600 mx-auto mb-6 scale-110">
               <svg class="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                 <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
               </svg>
            </div>
            <p class="text-[10px] text-slate-400 font-black uppercase tracking-[0.15em] mb-8 leading-relaxed">
              Verify Identity via 6-Character Terminal Reference
            </p>
            <div class="max-w-[280px] mx-auto">
              <input
                type="text"
                v-model="manualInput"
                @keyup.enter="performManualScan"
                placeholder="PNR REF"
                maxlength="20"
                class="w-full bg-white border-2 border-slate-200 rounded-[2px] px-6 py-4 text-2xl font-mono font-black text-center text-slate-900 tracking-[0.4em] uppercase focus:border-pink-600 focus:ring-8 focus:ring-pink-100 outline-none transition-all shadow-sm"
                :disabled="isLooking"
                ref="manualInputRef"
              >
            </div>
            <button
              @click="performManualScan"
              :disabled="!manualInput.trim() || isLooking"
              class="mt-8 bg-slate-900 hover:bg-black disabled:bg-slate-200 text-white text-[10px] font-black uppercase tracking-[0.2em] px-10 py-4 rounded-[2px] transition-all active:scale-95 shadow-xl shadow-slate-200"
            >
              Authorize Node
            </button>
          </div>
        </div>

        <!-- ===================== LOADING ===================== -->
        <div v-if="isLooking" class="flex flex-col items-center justify-center gap-4 py-6 animate-pulse">
          <div class="flex gap-2">
             <div class="w-3 h-3 bg-pink-600 rounded-full animate-bounce" style="animation-delay: 0s"></div>
             <div class="w-3 h-3 bg-pink-600 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
             <div class="w-3 h-3 bg-pink-600 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
          </div>
          <span class="text-[10px] font-black text-pink-700 uppercase tracking-widest">Querying Central Manifest...</span>
        </div>

        <!-- ===================== ERROR ===================== -->
        <Transition
          enter-active-class="transition duration-300 ease-out"
          enter-from-class="-translate-y-2 opacity-0"
          enter-to-class="translate-y-0 opacity-100"
        >
          <div v-if="lookupError" class="bg-rose-50 border-2 border-rose-100 rounded-[5px] p-6 flex items-start gap-5 shadow-sm">
            <div class="w-12 h-12 bg-rose-600 rounded-[2px] flex items-center justify-center text-white shrink-0 shadow-lg shadow-rose-200">
               <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                 <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
               </svg>
            </div>
            <div class="flex-1">
              <div class="text-[11px] font-black text-rose-800 uppercase tracking-widest">Protocol Rejection</div>
              <div class="text-xs text-rose-600 font-bold mt-1 leading-relaxed">{{ lookupError }}</div>
              <button @click="resetAndRescan" class="text-[10px] font-black text-rose-900 uppercase tracking-widest mt-4 flex items-center gap-2 hover:underline">
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="4">
                   <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
                Retry Logic
              </button>
            </div>
          </div>
        </Transition>

        <!-- ===================== RESULTS ===================== -->
        <Transition
          enter-active-class="transition duration-400 ease-out"
          enter-from-class="opacity-0 translate-y-4"
          enter-to-class="opacity-100 translate-y-0"
        >
          <div v-if="passengers.length > 0" class="space-y-4">
            <div class="flex items-center justify-between px-2">
              <div class="flex items-center gap-3">
                 <span class="w-2 h-2 bg-pink-500 rounded-full animate-pulse-fast"></span>
                 <span class="text-[10px] font-black text-slate-800 uppercase tracking-widest">
                   Identified Nodes: {{ passengers.length }}
                 </span>
              </div>
              <span class="text-[9px] font-black text-pink-600 uppercase tracking-tighter">PH-DOMESTIC TERMINAL</span>
            </div>

            <div class="space-y-3">
               <div
                 v-for="p in passengers"
                 :key="p.booking_detail_id"
                 class="bg-white border-2 border-slate-100 rounded-[5px] overflow-hidden hover:border-pink-600/30 transition-all cursor-pointer group shadow-sm hover:shadow-xl hover:shadow-slate-200/50 active:scale-[0.98]"
                 :class="{ 'opacity-50 grayscale cursor-not-allowed': isCheckedIn(p) }"
                 @click="selectPassenger(p)"
               >
                 <div class="px-6 py-5 flex items-center justify-between">
                   <div class="flex items-center gap-5 min-w-0">
                     <div class="w-12 h-12 bg-slate-50 border border-slate-100 rounded-[2px] flex items-center justify-center text-slate-400 group-hover:bg-pink-100 group-hover:text-pink-600 transition-colors font-black text-lg shrink-0">
                       {{ p.passenger_name?.charAt(0) || '?' }}
                     </div>
                     <div class="min-w-0">
                       <div class="text-sm font-black text-slate-900 group-hover:text-pink-700 transition-colors truncate tracking-tight uppercase">
                         {{ p.passenger_name }}
                       </div>
                       <div class="flex items-center gap-3 mt-1.5">
                         <span class="text-[10px] font-mono font-black text-pink-600 tracking-widest">{{ p.pnr }}</span>
                         <div class="w-1 h-1 bg-slate-200 rounded-full"></div>
                         <span class="text-[9px] font-black text-slate-400 uppercase tracking-tighter">Slot {{ p.seat || 'TBA' }}</span>
                       </div>
                     </div>
                   </div>
                   <div class="shrink-0 ml-4">
                     <div v-if="isCheckedIn(p)" class="px-3 py-1 bg-emerald-50 text-emerald-700 text-[10px] font-black rounded-[2px] border border-emerald-100 uppercase tracking-widest">
                       Clearance OK
                     </div>
                     <div v-else class="w-10 h-10 rounded-[5px] bg-slate-50 flex items-center justify-center text-slate-400 group-hover:bg-pink-600 group-hover:text-white transition-all shadow-inner">
                        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                     </div>
                   </div>
                 </div>
               </div>
            </div>
          </div>
        </Transition>
      </div>

      <!-- Footer -->
      <div class="px-8 py-5 bg-slate-50 border-t border-slate-100 shrink-0 flex justify-between items-center">
        <span class="text-[9px] font-black text-slate-300 uppercase tracking-[0.2em] hidden sm:block">F-DCS Core Infrastructure</span>
        <button @click="handleClose" class="px-8 py-3 rounded-[2px] text-[10px] font-black text-slate-500 uppercase tracking-widest hover:bg-slate-200 hover:text-slate-900 transition-all active:scale-95">
          Abort Portal
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { Html5Qrcode } from 'html5-qrcode'
import { dcsService } from '@/services/api/dcsService'
import { useDcsStore } from '@/stores/dcs'

const props = defineProps({
  scheduleId: { type: [String, Number], required: true }
})

const emit = defineEmits(['close', 'passenger-selected'])

const dcsStore = useDcsStore()

// State
const activeTab = ref('camera')
const manualInput = ref('')
const manualInputRef = ref(null)

// Camera
const cameraActive = ref(false)
const cameraError = ref(null)
let html5QrCode = null
let scanLocked = false  

// Lookup
const scanResult = ref(null)
const isLooking = ref(false)
const lookupError = ref(null)
const passengers = ref([])

let capturedScheduleId = null

onMounted(() => {
  capturedScheduleId = props.scheduleId
  if (activeTab.value === 'camera') {
    startCamera()
  }
})

onBeforeUnmount(() => {
  stopCamera()
})

const startCamera = async () => {
  try {
    cameraError.value = null
    scanLocked = false
    await nextTick()
    await new Promise(r => setTimeout(r, 400))

    html5QrCode = new Html5Qrcode('qr-reader')

    await html5QrCode.start(
      { facingMode: 'environment' },
      {
        fps: 15, // Higher FPS for premium feel
        qrbox: { width: 250, height: 250 },
        aspectRatio: 4 / 3,
        disableFlip: false
      },
      onQrCodeSuccess,
      () => {} 
    )

    cameraActive.value = true
  } catch (err) {
    cameraError.value = typeof err === 'string'
      ? err
      : err?.message || 'Access protocol denied core sensor connection.'
  }
}

const stopCamera = async () => {
  if (html5QrCode) {
    try {
      const state = html5QrCode.getState()
      if (state === 2) { 
        await html5QrCode.stop()
      }
    } catch (e) { /* ignore */ }
    html5QrCode = null
  }
  cameraActive.value = false
}

const onQrCodeSuccess = (decodedText) => {
  if (scanLocked) return
  
  const rawValue = decodedText || ''
  const trimmedValue = rawValue.trim()
  
  if (!trimmedValue) return 

  scanLocked = true

  // Play "authorized" beep
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)()
    const osc = audioCtx.createOscillator()
    const gain = audioCtx.createGain()
    osc.connect(gain)
    gain.connect(audioCtx.destination)
    osc.frequency.value = 1500
    gain.gain.value = 0.1
    osc.start()
    osc.stop(audioCtx.currentTime + 0.1)
  } catch (e) { /* silent */ }

  setTimeout(async () => {
    try {
      scanResult.value = trimmedValue
      await stopCamera()
      await lookupQr(trimmedValue)
    } catch (err) {
      lookupError.value = 'Node lookup failed immediately after signal capture.'
      scanLocked = false 
    }
  }, 0)
}

const performManualScan = () => {
  const val = manualInput.value.trim()
  if (!val) return
  scanResult.value = val
  lookupQr(val)
}

const lookupQr = async (qrValue) => {
  const schedId = capturedScheduleId || props.scheduleId
  isLooking.value = true
  lookupError.value = null
  passengers.value = []

  try {
    const response = await dcsService.scanQr(qrValue, schedId)
    passengers.value = response.data.passengers || []
  } catch (err) {
    lookupError.value = err.response?.data?.error || 'Node synchronization failure: Reference ID unknown.'
  } finally {
    isLooking.value = false
  }
}

const resetAndRescan = async () => {
  scanResult.value = null
  lookupError.value = null
  passengers.value = []
  manualInput.value = ''
  scanLocked = false

  if (activeTab.value === 'camera') {
    await startCamera()
  } else {
    nextTick(() => manualInputRef.value?.focus())
  }
}

const isCheckedIn = (p) => p.status === 'checkin' || p.status === 'boarding'

const selectPassenger = (passenger) => {
  if (isCheckedIn(passenger)) return
  emit('passenger-selected', passenger)
}

const switchToCamera = async () => {
  if (activeTab.value === 'camera') return
  activeTab.value = 'camera'
  if (!scanResult.value) {
    await startCamera()
  }
}

const switchToManual = async () => {
  activeTab.value = 'manual'
  await stopCamera()
  nextTick(() => manualInputRef.value?.focus())
}

const handleClose = async () => {
  await stopCamera()
  emit('close')
}
</script>

<style scoped>
@keyframes scan-line {
  0%, 100% { top: 12%; }
  50% { top: 85%; }
}
.animate-scan-line {
  animation: scan-line 2.5s ease-in-out infinite;
}

@keyframes pulse-fast {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.9); }
}
.animate-pulse-fast {
  animation: pulse-fast 1s ease-in-out infinite;
}

/* Override html5-qrcode default styles */
:deep(#qr-reader) {
  border: none !important;
  width: 100% !important;
}
:deep(#qr-reader video) {
  border-radius: 0 !important;
  object-fit: cover !important;
}
:deep(#qr-reader__scan_region) {
  min-height: auto !important;
}
:deep(#qr-reader__dashboard),
:deep(#qr-reader__dashboard_section_csr),
:deep(#qr-reader__dashboard_section_swaplink),
:deep(#qr-reader__header_message),
:deep(#qr-reader img[alt="Info icon"]),
:deep(#qr-reader__scan_region br) {
  display: none !important;
}
</style>
