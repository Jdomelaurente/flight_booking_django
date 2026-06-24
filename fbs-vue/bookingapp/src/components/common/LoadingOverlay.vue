<template>
  <Transition
    enter-active-class="transition-opacity duration-300 ease-out"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-500 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div v-if="show" class="fixed inset-0 bg-white/90 backdrop-blur-md z-[100] flex flex-col items-center justify-center p-6 text-center">
      <div class="relative w-24 h-24 mb-8">
        <!-- Main Spinner -->
        <svg class="animate-spin absolute inset-0 w-full h-full text-pink-100" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        
        <!-- Plane Icon Animation -->
        <div class="absolute inset-0 flex items-center justify-center">
          <svg class="w-10 h-10 text-pink-500 transform animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </div>
      </div>

      <h2 class="text-2xl font-black text-gray-900 tracking-tight mb-2 animate-pulse">
        {{ title }}
      </h2>
      <p class="text-gray-500 font-medium max-w-xs mx-auto">
        {{ subtitle }}
      </p>

      <!-- Progress bar decoration -->
      <div class="mt-8 w-48 h-1 bg-gray-100 rounded-full overflow-hidden">
        <div class="h-full bg-pink-500 animate-[loading_2s_ease-in-out_infinite]"></div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  show: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Processing...'
  },
  subtitle: {
    type: String,
    default: 'Please wait while we handle your request.'
  }
});
</script>

<style scoped>
@keyframes loading {
  0% { transform: translateX(-100%); }
  50% { transform: translateX(0); }
  100% { transform: translateX(100%); }
}
</style>
