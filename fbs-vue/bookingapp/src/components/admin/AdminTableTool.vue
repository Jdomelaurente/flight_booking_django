<template>
  <div class="mb-6 flex flex-col md:flex-row gap-4 items-center justify-between poppins">
    <!-- Search Bar -->
    <div class="relative w-full md:w-96 group">
      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <i class="ph ph-magnifying-glass text-gray-400 group-focus-within:text-[#fe3787] transition-colors"></i>
      </div>
      <input 
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        type="text" 
        :placeholder="placeholder || 'Search documents, ID or name...'"
        class="block w-full pl-10 pr-10 py-2.5 bg-gray-50 border border-gray-200 rounded-[1px] text-sm focus:bg-white focus:border-[#fe3787] focus:ring-0 transition-all outline-none poppins"
      />
      <div v-if="modelValue" class="absolute inset-y-0 right-0 pr-3 flex items-center">
        <button @click="$emit('update:modelValue', '')" class="text-gray-400 hover:text-red-500 transition-colors">
          <i class="ph ph-x-circle"></i>
        </button>
      </div>
    </div>

    <!-- Actions & Filters -->
    <div class="flex items-center gap-3 w-full md:w-auto justify-end">
      <!-- Filter Button Slot (Optional) -->
      <slot name="filters"></slot>

      <!-- View Toggle (Optional) -->
      <slot name="view-toggle"></slot>

      <!-- Main Action Buttons Slot -->
      <div class="h-8 w-px bg-gray-200 mx-1 hidden md:block"></div>
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  }
});

defineEmits(['update:modelValue']);
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
.poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
