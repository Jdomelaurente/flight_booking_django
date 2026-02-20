<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBookingStore } from '@/stores/booking'
import { useModalStore } from '@/stores/modal'

const router = useRouter()
const bookingStore = useBookingStore()
const modalStore = useModalStore()

const isSessionValid = computed(() => bookingStore.isSessionValid)

const isPracticeMode = computed(() => bookingStore.isPractice)
const hasValidation = computed(() => bookingStore.hasActivityCodeValidation)

async function handleReset() {
  const confirmed = await modalStore.confirm({
    title: 'Reset Search?',
    message: 'Are you sure you want to reset your search? Your selected flights and passenger details will be cleared.',
    confirmText: 'Reset Search',
    cancelText: 'Cancel'
  })
  
  if (confirmed) {
    bookingStore.resetBooking()
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
    bookingStore.resetBooking()
    router.push('/student/dashboard')
  }
}
</script>

<template>
  <div>
    <header class="bg-blue-900 shadow-md">
      <div class="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">

        <router-link to="/" class="text-white font-bold text-xl tracking-wide flex items-center gap-2">
          ✈ <span>Philippine Airlines</span>
        </router-link>

        <nav class="hidden md:flex items-center gap-6">
            <router-link to="/check-in"  class="text-blue-200 hover:text-white text-sm font-medium transition-colors" active-class="text-white border-b-2 border-yellow-400 pb-0.5">Check-in</router-link>
            <router-link to="/status"    class="text-blue-200 hover:text-white text-sm font-medium transition-colors" active-class="text-white border-b-2 border-yellow-400 pb-0.5">Flight Status</router-link>
   
            <div class="flex items-center gap-3">
              <!-- Reset Search Button (Only if validated) -->
              <button
                  v-if="hasValidation"
                  @click="handleReset"
                  class="flex items-center gap-2 border border-blue-400/30 bg-blue-800/50 hover:bg-blue-800 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition-colors"
                  title="Reset search and passenger data"
                >
                  ↺ Reset
              </button>

              <!-- End Activity/Practice Button -->
              <button
                  v-if="hasValidation"
                  @click="handleEndSession"
                  class="flex items-center gap-2 border bg-red-600 hover:bg-red-700 text-white text-xs font-bold px-4 py-1.5 rounded-lg transition-colors shadow-lg"
                >
                  ✕ {{ isPracticeMode ? 'End Practice' : 'End Activity' }}
              </button>
            </div>
            
            <div v-if="!hasValidation" class="w-36" />
        </nav>



      </div>
    </header>

    <!-- ✅ slot instead of <router-view /> -->
    <slot />
  </div>
</template>