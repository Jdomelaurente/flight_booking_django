<template>
  <div class="p-8 text-center poppins">
    <!-- Icon -->
    <div 
      class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6"
      :class="variant === 'danger' ? 'bg-red-50 text-red-500' : 'bg-blue-50 text-blue-500'"
    >
      <i :class="[iconClass, 'text-4xl']"></i>
    </div>

    <!-- Content -->
    <h3 class="text-xl font-bold text-[#002D1E] mb-2 poppins uppercase tracking-tight">{{ title }}</h3>
    <p class="text-gray-500 mb-8 leading-relaxed poppins text-sm">{{ message }}</p>

    <!-- Actions -->
    <div class="flex border-t border-gray-100 pt-6 gap-3">
      <button 
        @click="$emit('cancel')"
        class="flex-1 px-6 py-2.5 text-xs font-bold uppercase text-gray-400 hover:text-gray-600 transition-colors poppins"
      >
        {{ cancelText }}
      </button>
      <button 
        @click="$emit('confirm')"
        :disabled="loading"
        class="flex-1 px-6 py-2.5 text-white rounded-[1px] text-xs font-bold uppercase tracking-widest transition-all shadow-lg poppins disabled:opacity-60"
        :class="variant === 'danger' ? 'bg-red-600 hover:bg-red-700 shadow-red-200' : 'bg-[#002D1E] hover:bg-black shadow-gray-200'"
      >
        {{ loading ? (loadingText || 'Processing...') : confirmText }}
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  message: String,
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  },
  iconClass: {
    type: String,
    default: 'ph ph-warning-circle'
  },
  variant: {
    type: String,
    default: 'standard' // 'standard', 'danger'
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: ''
  }
});

defineEmits(['confirm', 'cancel']);
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
.poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
