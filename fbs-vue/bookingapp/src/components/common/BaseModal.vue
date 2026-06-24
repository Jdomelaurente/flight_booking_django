<template>
  <Transition name="modal">
    <div v-if="isOpen" class="fixed inset-0 z-[10000] flex items-center justify-center p-4">
      <!-- Backdrop -->
      <div 
        class="absolute inset-0 bg-black/40 backdrop-blur-sm"
        @click="$emit('close')"
      ></div>
      
      <!-- Content Container -->
      <div 
        class="relative bg-white rounded-[1px] shadow-2xl max-w-lg w-full overflow-hidden transform transition-all"
        :class="compact ? 'max-w-sm' : 'max-w-lg'"
      >
        <slot></slot>
      </div>
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  isOpen: Boolean,
  compact: {
    type: Boolean,
    default: false
  }
});

defineEmits(['close']);
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .relative,
.modal-leave-active .relative {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.9) translateY(20px);
}
</style>
