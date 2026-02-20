<template>
  <BaseModal :isOpen="isOpen" @close="$emit('close')" :compact="true">
    <div class="p-6 text-center space-y-4">
      <SuccessAnimation />
      
      <div>
        <h3 class="text-xl font-bold text-gray-900 mb-2">{{ title }}</h3>
        <p class="text-gray-600">{{ message }}</p>
      </div>

      <button 
        @click="$emit('confirm')" 
        class="w-full bg-green-600 text-white font-bold py-3 px-4 rounded-xl hover:bg-green-700 transition-colors uppercase text-sm mt-4 shadow-lg active:scale-95 transform transition-transform"
      >
        {{ buttonText }}
      </button>
    </div>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue';
import SuccessAnimation from './SuccessAnimation.vue';

defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    default: 'Success!'
  },
  message: {
    type: String,
    default: 'Operation completed successfully.'
  },
  buttonText: {
    type: String,
    default: 'Continue'
  }
});

defineEmits(['close', 'confirm']);
</script>
