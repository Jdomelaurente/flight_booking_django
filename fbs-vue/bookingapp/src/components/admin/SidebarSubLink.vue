<template>
  <router-link 
    :to="to" 
    class="flex items-center py-1.5 pl-10 pr-4 text-[11px] text-gray-400 hover:text-white hover:bg-white/5 transition-all border-l-2 border-transparent hover:border-[#fe3787]
"
    active-class="text-white bg-white/5 !border-[#fe3787]"
  >
    {{ label }}
  </router-link>
</template>

<script setup>
defineProps({
  label: String,
  to: {
    type: String,
    default: '#'
  }
});
</script>