<template>
  <div class="p-8 text-center">
    <!-- Icon -->
    <div class="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl">
      <span v-if="modalStore.type === 'confirm'">❓</span>
      <span v-else-if="modalStore.type === 'alert'">⚠️</span>
    </div>

    <!-- Content -->
    <h3 class="text-xl font-bold text-gray-900 mb-2">{{ modalStore.title }}</h3>
    <p class="text-gray-500 mb-8 leading-relaxed">{{ modalStore.message }}</p>

    <!-- Actions -->
    <div class="flex gap-4">
      <button 
        v-if="modalStore.type === 'confirm'"
        @click="modalStore.close(false)"
        class="flex-1 py-3 px-4 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl font-semibold transition-colors"
      >
        {{ modalStore.cancelText }}
      </button>
      <button 
        @click="modalStore.close(true)"
        class="flex-1 py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold shadow-lg shadow-blue-200 transition-colors"
      >
        {{ modalStore.confirmText }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { useModalStore } from '@/stores/modal';

const modalStore = useModalStore();
</script>
