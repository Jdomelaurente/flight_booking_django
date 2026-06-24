<template>
  <span>{{ prefix }}{{ displayValue }}{{ suffix }}</span>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';

const props = defineProps({
  value: {
    type: Number,
    required: true
  },
  duration: {
    type: Number,
    default: 500
  },
  prefix: {
    type: String,
    default: ''
  },
  suffix: {
    type: String,
    default: ''
  },
  format: {
    type: Boolean,
    default: true
  }
});

const displayValue = ref('');
const internalValue = ref(0);

const animateValue = (start, end, duration) => {
  const startTime = performance.now();
  
  const update = (currentTime) => {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // Ease out cubic
    const ease = 1 - Math.pow(1 - progress, 3);
    const current = start + (end - start) * ease;
    
    internalValue.value = current;
    updateDisplay();
    
    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      internalValue.value = end;
      updateDisplay();
    }
  };
  
  requestAnimationFrame(update);
};

const updateDisplay = () => {
  if (props.format) {
    displayValue.value = Math.round(internalValue.value).toLocaleString();
  } else {
    displayValue.value = Math.round(internalValue.value);
  }
};

watch(() => props.value, (newVal, oldVal) => {
  animateValue(oldVal || 0, newVal, props.duration);
});

onMounted(() => {
  internalValue.value = props.value;
  updateDisplay();
});
</script>
