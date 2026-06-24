<template>
  <Teleport to="body">
    <div 
      v-if="isVisible" 
      class="flying-icon" 
      :style="iconStyle"
    >
      {{ icon }}
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue';

const isVisible = ref(false);
const currentPos = ref({ x: 0, y: 0 });
const icon = ref('🧳');
const opacity = ref(1);
const scale = ref(1);

const iconStyle = computed(() => ({
  left: `${currentPos.value.x}px`,
  top: `${currentPos.value.y}px`,
  opacity: opacity.value,
  transform: `translate(-50%, -50%) scale(${scale.value})`,
  position: 'fixed',
  pointerEvents: 'none',
  zIndex: 9999,
  fontSize: '24px',
  transition: 'all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
}));

const fly = (startElement, targetSelector, iconSymbol = '🧳') => {
  if (!startElement) return;
  
  const targetElement = document.querySelector(targetSelector);
  if (!targetElement) return;

  const startRect = startElement.getBoundingClientRect();
  const targetRect = targetElement.getBoundingClientRect();

  icon.value = iconSymbol;
  currentPos.value = { 
    x: startRect.left + startRect.width / 2, 
    y: startRect.top + startRect.height / 2 
  };
  
  isVisible.value = true;
  opacity.value = 1;
  scale.value = 1;

  // Small delay to ensure the initial position is set before transition starts
  setTimeout(() => {
    currentPos.value = { 
      x: targetRect.left + targetRect.width / 2, 
      y: targetRect.top + targetRect.height / 2 
    };
    scale.value = 0.5;
    
    // Fade out towards the end
    setTimeout(() => {
      opacity.value = 0;
    }, 600);

    // Reset after animation
    setTimeout(() => {
      isVisible.value = false;
    }, 850);
  }, 50);
};

defineExpose({ fly });
</script>

<style scoped>
.flying-icon {
  will-change: transform, left, top, opacity;
  filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
}
</style>
