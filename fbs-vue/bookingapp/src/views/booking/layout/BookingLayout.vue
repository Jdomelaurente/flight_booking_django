<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useBookingStore } from '@/stores/booking'
import { useModalStore } from '@/stores/modal'
import { useNotificationStore } from '@/stores/notification'

const router = useRouter()
const bookingStore = useBookingStore()
const modalStore = useModalStore()
const notificationStore = useNotificationStore()

const isSessionValid = computed(() => bookingStore.isSessionValid)
const isPracticeMode = computed(() => bookingStore.isPractice)
const hasValidation = computed(() => bookingStore.hasActivityCodeValidation)
const timeLeft = computed(() => bookingStore.timeLeftFormatted)
const secondsLeft = computed(() => bookingStore.secondsLeft)
const isUrgent = computed(() => secondsLeft.value < 120 && secondsLeft.value > 0)
const isManageDropdownOpen = ref(false)

let timerInterval = null

onMounted(() => {
  window.addEventListener('click', handleGlobalClick)
  timerInterval = setInterval(() => {
    // Session validation does not run during Online Check-in
    if (router.currentRoute.value.path === '/check-in') return

    const session = bookingStore.checkSession()
    if (!session.valid && hasValidation.value) {
      handleTimeUp()
    }
  }, 1000)
})

onUnmounted(() => {
  window.removeEventListener('click', handleGlobalClick)
  if (timerInterval) clearInterval(timerInterval)
})

const isTimeUpHandled = ref(false)

async function handleTimeUp() {
  if (isTimeUpHandled.value) return
  isTimeUpHandled.value = true
  
  if (timerInterval) clearInterval(timerInterval)
  
  // Call backend to fail the activity first
  if (!isPracticeMode.value) {
    await bookingStore.failActivity()
  }

  await modalStore.error({
    title: 'Time Reached!',
    message: 'The time allocated for this activity has expired. This attempt will be marked as failed with a 0 score.',
    confirmText: 'Close'
  })
  
  bookingStore.clearActivityCodeValidation()
  bookingStore.resetBooking(true)
  router.push('/student/dashboard')
}

async function handleReset() {
  const confirmed = await modalStore.confirm({
    title: 'Reset Search?',
    message: 'Are you sure you want to reset your search? Your selected flights and passenger details will be cleared.',
    confirmText: 'Reset Search',
    cancelText: 'Cancel'
  })
  
  if (confirmed) {
    bookingStore.resetBooking(false)
    router.push('/')
  }
}

async function handleEndSession() {
  const sessionType = isPracticeMode.value ? 'practice session' : 'activity'
  const confirmed = await modalStore.confirm({
    title: isPracticeMode.value ? 'End Practice?' : 'End Activity?',
    message: `Are you sure you want to end this ${sessionType}? All progress will be permanently cleared and you will return to the dashboard.`,
    confirmText: 'End Session',
    cancelText: 'Stay'
  })
  
  if (confirmed) {
    console.log(`🧹 Ending ${sessionType}...`)
    bookingStore.clearActivityCodeValidation()
    bookingStore.resetBooking(true)
    router.push('/student/dashboard')
  }
}

function handleGlobalClick(e) {
  const trigger = document.querySelector('.manage-flight-trigger')
  if (trigger && !trigger.contains(e.target)) {
    isManageDropdownOpen.value = false
  }
}
</script>

<template>
  <div>
    <header class="bg-gray-100 shadow-lg/20">
      <div class="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">

        <router-link to="/" class="text-[#FF579A] font-bold text-xl tracking-wide flex items-center gap-2">
           <span>TourSim</span>
        </router-link>

        <nav class="flex items-center gap-2 md:gap-8">
            <div class="flex items-center gap-6">
              <!-- Manage Flight Dropdown -->
              <div class="relative hidden lg:block manage-flight-trigger">
                <button 
                  @click="isManageDropdownOpen = !isManageDropdownOpen" 
                  class="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-slate-500 hover:text-[#FF579A] transition-colors"
                >
                  <i class="ph ph-airplane text-lg"></i>
                  Manage Flight
                  <i class="ph ph-caret-down text-[10px]" :class="{ 'rotate-180': isManageDropdownOpen }"></i>
                </button>

                <!-- Dropdown Menu -->
                <div v-show="isManageDropdownOpen" 
                  class="absolute top-full left-0 mt-2 w-56 bg-white border border-slate-200 rounded-sm shadow-xl z-50 overflow-hidden"
                  @click="isManageDropdownOpen = false"
                >
                  <router-link to="/check-in" class="flex items-center gap-3 px-4 py-3 hover:bg-slate-50 transition-colors group">
                    <div class="w-8 h-8 rounded-sm bg-slate-100 flex items-center justify-center text-slate-400 group-hover:bg-[#FF579A] group-hover:text-white transition-all">
                      <i class="ph ph-airplane-landing text-lg"></i>
                    </div>
                    <div class="text-left">
                      <p class="text-[10px] font-black uppercase text-slate-900 leading-none">Online Check-in</p>
                      <p class="text-[8px] font-bold text-slate-400 uppercase tracking-widest mt-1">Authorized Access</p>
                    </div>
                  </router-link>
                </div>
              </div>

              <div class="flex items-center gap-2 md:gap-3">
              <!-- Activity Timer (Hidden on Check-in) -->
              <div 
                v-if="hasValidation && $route.path !== '/check-in'" 
                :class="[
                  'flex items-center gap-2 px-3 py-1.5 rounded-lg border font-black transition-all',
                  isUrgent ? 'bg-red-50 border-red-200 text-red-600 animate-pulse' : 'bg-white border-slate-200 text-slate-700'
                ]"
              >
                <i :class="['ph ph-timer text-lg', isUrgent ? 'text-red-500' : 'text-slate-400']"></i>
                <div class="flex flex-col leading-none">
                  <span class="text-[8px] uppercase tracking-tighter opacity-70">Remaining Time</span>
                  <span class="text-xs font-mono">{{ timeLeft }}</span>
                </div>
              </div>

              <!-- Reset Search Button (Only if validated & not on check-in) -->
              <button
                  v-if="hasValidation && $route.path !== '/check-in'"
                  @click="handleReset"
                  class="flex items-center gap-1.5 bg-blue-800 cursor-pointer hover:bg-blue-700/80 text-white text-[10px] md:text-xs font-semibold px-2.5 py-1.5 md:px-3 md:py-1.5 rounded-md transition-colors"
                  title="Reset search and passenger data"
                >
                  ↺ <span class="hidden sm:inline">Reset</span>
              </button>

              <!-- End Activity/Practice Button (Only if validated & not on check-in) -->
              <button
                  v-if="hasValidation && $route.path !== '/check-in'"
                  @click="handleEndSession"
                  class="flex items-center gap-1.5 bg-red-600 hover:bg-red-600/80 cursor-pointer text-white text-[10px] md:text-xs font-bold px-3 py-1.5 md:px-4 md:py-1.5 rounded-lg transition-colors"
                >
                  ✕ <span class="hidden sm:inline">{{ isPracticeMode ? 'End Practice' : 'End Activity' }}</span>
                  <span class="sm:hidden">{{ isPracticeMode ? 'Practice' : 'Activity' }}</span>
              </button>
              </div>
            </div>
        </nav>



      </div>
    </header>

    <!-- ✅ slot instead of <router-view /> -->
    <slot />
  </div>
</template>