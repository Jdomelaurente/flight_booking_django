<template>
  <div class="fixed top-6 right-6 z-[9999] flex flex-col gap-4 max-w-sm w-full pointer-events-none">
    <TransitionGroup
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform translate-x-12 opacity-0"
      enter-to-class="transform translate-x-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-x-0 opacity-100"
      leave-to-class="transform translate-x-12 opacity-0"
    >
      <div
        v-for="notification in notificationStore.notifications"
        :key="notification.id"
        class="pointer-events-auto p-4 rounded-lg shadow-xl border flex items-start gap-3 bg-white"
        :class="{
          'border-emerald-200 bg-emerald-50': notification.type === 'success',
          'border-red-200 bg-red-50': notification.type === 'error',
          'border-amber-200 bg-amber-50': notification.type === 'warning',
          'border-blue-200 bg-blue-50': notification.type === 'info'
        }"
      >
        <!-- Icons -->
        <div class="flex-shrink-0 mt-0.5">
          <span v-if="notification.type === 'success'" class="text-emerald-500">✅</span>
          <span v-else-if="notification.type === 'error'" class="text-red-500">❌</span>
          <span v-else-if="notification.type === 'warning'" class="text-amber-500">⚠️</span>
          <span v-else class="text-blue-500">ℹ️</span>
        </div>

        <!-- Content -->
        <div class="flex-grow">
          <p class="text-sm font-medium" 
             :class="{
               'text-emerald-800': notification.type === 'success',
               'text-red-800': notification.type === 'error',
               'text-amber-800': notification.type === 'warning',
               'text-blue-800': notification.type === 'info'
             }">
            {{ notification.message }}
          </p>
        </div>

        <!-- Close Button -->
        <button 
          @click="notificationStore.removeNotification(notification.id)"
          class="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useNotificationStore } from '@/stores/notification';

const notificationStore = useNotificationStore();
</script>

<style scoped>
/* Optional: prevent stacking overlap during transitions */
.v-move {
  transition: transform 0.3s ease;
}
</style>
