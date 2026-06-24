<template>
  <Transition name="fade">
    <div v-if="loading" class="fixed inset-0 z-[100] flex items-center justify-center bg-white/60 backdrop-blur-[2px]">
      <div class="flex flex-col items-center">
        <!-- Premium Spinner -->
        <div class="relative w-16 h-16">
          <div class="absolute inset-0 border-4 border-pink-100 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-pink-500 rounded-full border-t-transparent animate-spin"></div>
          <div class="absolute inset-2 border-4 border-green-100 rounded-full"></div>
          <div class="absolute inset-2 border-4 border-green-600 rounded-full border-b-transparent animate-spin-slow"></div>
        </div>
        
        <div class="mt-6 flex flex-col items-center">
          <p class="text-[10px] font-black uppercase tracking-[0.3em] text-gray-400 mb-1">Processing</p>
          <div class="flex gap-1.5">
            <div class="w-1.5 h-1.5 bg-pink-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
            <div class="w-1.5 h-1.5 bg-pink-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
            <div class="w-1.5 h-1.5 bg-pink-300 rounded-full animate-bounce"></div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.animate-spin-slow {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
