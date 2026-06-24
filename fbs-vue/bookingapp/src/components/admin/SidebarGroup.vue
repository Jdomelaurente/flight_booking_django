<template>
  <div class="w-full">
      <div 
        @click="toggle"
        class="flex items-center justify-between px-4 py-1.5 cursor-pointer hover:bg-white/10 transition-colors group"
        :class="{ 'bg-white/5': isOpen }"
      >
        <div class="flex items-center">
          <i :class="['ph', icon, 'text-lg']"></i>
          
          <span v-if="!isCollapsed" class="ml-3 text-[12px] font-medium whitespace-nowrap">
            {{ title }}
          </span>
        </div>

      <i 
        v-if="!isCollapsed"
        class="ph ph-caret-down text-[10px] transition-transform duration-300"
        :class="{ 'rotate-180': isOpen }"
      ></i>
    </div>

    <div 
      v-show="isOpen && !isCollapsed" 
      class="bg-black/20 overflow-hidden"
    >
      <slot />
    </div>
  </div>
</template>

<script setup>
import { ref, inject, watch } from 'vue';

const props = defineProps({
  title: String,
  icon: String
});

// Listen to the sidebar state from AdminLayout.vue
const isCollapsed = inject('isSidebarCollapsed');
const isOpen = ref(false);

const toggle = () => {
  if (!isCollapsed.value) {
    isOpen.value = !isOpen.value;
  }
};

// Close the dropdown automatically if the sidebar is collapsed
watch(isCollapsed, (newVal) => {
  if (newVal) isOpen.value = false;
});
</script>   