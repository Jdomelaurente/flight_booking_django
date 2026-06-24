<template>
  <div class="searchable-select" ref="containerRef">
    <!-- Trigger Button -->
    <div
      class="select-trigger"
      :class="{ 'is-open': isOpen, 'is-disabled': disabled, 'has-value': modelValue !== '' && modelValue !== null }"
      @click="!disabled && toggleDropdown()"
    >
      <span v-if="selectedLabel" class="select-value poppins">{{ selectedLabel }}</span>
      <span v-else class="select-placeholder poppins">{{ placeholder }}</span>
      <div class="select-icons">
        <button
          v-if="(modelValue !== '' && modelValue !== null) && clearable"
          type="button"
          class="clear-btn"
          @click.stop="clearSelection"
          title="Clear selection"
        >
          <i class="ph ph-x"></i>
        </button>
        <i class="ph ph-caret-down chevron-icon" :class="{ 'rotated': isOpen }"></i>
      </div>
    </div>

    <!-- Dropdown Panel -->
    <Teleport to="body">
      <div
        v-if="isOpen"
        class="select-dropdown poppins"
        :style="dropdownStyle"
        ref="dropdownRef"
      >
        <!-- Search Input -->
        <div class="search-wrapper">
          <i class="ph ph-magnifying-glass search-icon"></i>
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            class="search-input poppins"
            :placeholder="`Search ${label || 'options'}...`"
            @keydown.escape="closeDropdown"
            @keydown.down.prevent="navigateDown"
            @keydown.up.prevent="navigateUp"
            @keydown.enter.prevent="selectHighlighted"
          />
          <span v-if="searchQuery" class="search-count">{{ filteredOptions.length }}</span>
        </div>

        <!-- Options List -->
        <div class="options-list" ref="listRef">
          <div
            v-if="filteredOptions.length === 0"
            class="no-results poppins"
          >
            <i class="ph ph-magnifying-glass"></i>
            <span>No results for "{{ searchQuery }}"</span>
          </div>

          <div
            v-for="(opt, index) in filteredOptions"
            :key="opt.value"
            class="option-item poppins"
            :class="{
              'is-selected': opt.value === modelValue,
              'is-highlighted': index === highlightedIndex
            }"
            @click="selectOption(opt)"
            @mouseenter="highlightedIndex = index"
          >
            <div class="option-content">
              <span class="option-label">{{ opt.label }}</span>
              <span v-if="opt.sublabel" class="option-sublabel">{{ opt.sublabel }}</span>
            </div>
            <i v-if="opt.value === modelValue" class="ph ph-check option-check"></i>
          </div>
        </div>

        <!-- Footer count -->
        <div v-if="filteredOptions.length > 0" class="dropdown-footer poppins">
          {{ filteredOptions.length }} of {{ options.length }} options
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  modelValue: {
    type: [String, Number, null],
    default: ''
  },
  options: {
    // Array of { value, label, sublabel? }
    type: Array,
    default: () => []
  },
  placeholder: {
    type: String,
    default: 'Select an option...'
  },
  label: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  clearable: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['update:modelValue', 'change']);

const isOpen = ref(false);
const searchQuery = ref('');
const highlightedIndex = ref(-1);
const containerRef = ref(null);
const dropdownRef = ref(null);
const searchInputRef = ref(null);
const listRef = ref(null);
const dropdownStyle = ref({});

const selectedLabel = computed(() => {
  if (props.modelValue === '' || props.modelValue === null) return null;
  const found = props.options.find(o => o.value == props.modelValue);
  return found ? found.label : null;
});

const filteredOptions = computed(() => {
  if (!searchQuery.value.trim()) return props.options;
  const q = searchQuery.value.toLowerCase();
  return props.options.filter(opt =>
    opt.label.toLowerCase().includes(q) ||
    (opt.sublabel && opt.sublabel.toLowerCase().includes(q))
  );
});

const positionDropdown = () => {
  if (!containerRef.value) return;
  const rect = containerRef.value.getBoundingClientRect();
  const viewportHeight = window.innerHeight;
  const dropdownHeight = 320;
  const spaceBelow = viewportHeight - rect.bottom;
  const openUpward = spaceBelow < dropdownHeight && rect.top > dropdownHeight;

  dropdownStyle.value = {
    position: 'fixed',
    left: `${rect.left}px`,
    width: `${rect.width}px`,
    zIndex: '9999',
    ...(openUpward
      ? { bottom: `${viewportHeight - rect.top}px`, top: 'auto' }
      : { top: `${rect.bottom + 4}px`, bottom: 'auto' })
  };
};

const toggleDropdown = async () => {
  if (isOpen.value) {
    closeDropdown();
  } else {
    positionDropdown();
    isOpen.value = true;
    highlightedIndex.value = -1;
    searchQuery.value = '';
    await nextTick();
    searchInputRef.value?.focus();

    // Scroll to selected item
    if (props.modelValue !== '' && props.modelValue !== null) {
      const idx = props.options.findIndex(o => o.value == props.modelValue);
      if (idx !== -1) {
        highlightedIndex.value = idx;
        await nextTick();
        scrollToHighlighted();
      }
    }
  }
};

const closeDropdown = () => {
  isOpen.value = false;
  searchQuery.value = '';
  highlightedIndex.value = -1;
};

const selectOption = (opt) => {
  emit('update:modelValue', opt.value);
  emit('change', opt.value);
  closeDropdown();
};

const clearSelection = () => {
  emit('update:modelValue', '');
  emit('change', '');
};

const navigateDown = () => {
  if (!isOpen.value) return;
  highlightedIndex.value = Math.min(highlightedIndex.value + 1, filteredOptions.value.length - 1);
  scrollToHighlighted();
};

const navigateUp = () => {
  if (!isOpen.value) return;
  highlightedIndex.value = Math.max(highlightedIndex.value - 1, 0);
  scrollToHighlighted();
};

const selectHighlighted = () => {
  if (highlightedIndex.value >= 0 && filteredOptions.value[highlightedIndex.value]) {
    selectOption(filteredOptions.value[highlightedIndex.value]);
  }
};

const scrollToHighlighted = async () => {
  await nextTick();
  if (listRef.value) {
    const items = listRef.value.querySelectorAll('.option-item');
    if (items[highlightedIndex.value]) {
      items[highlightedIndex.value].scrollIntoView({ block: 'nearest' });
    }
  }
};

// Reset highlighted index when search changes
watch(searchQuery, () => {
  highlightedIndex.value = -1;
});

// Close on outside click
const handleOutsideClick = (e) => {
  if (
    containerRef.value && !containerRef.value.contains(e.target) &&
    dropdownRef.value && !dropdownRef.value.contains(e.target)
  ) {
    closeDropdown();
  }
};

// Reposition on scroll/resize
const handleReposition = () => {
  if (isOpen.value) positionDropdown();
};

onMounted(() => {
  document.addEventListener('mousedown', handleOutsideClick);
  window.addEventListener('scroll', handleReposition, true);
  window.addEventListener('resize', handleReposition);
});

onUnmounted(() => {
  document.removeEventListener('mousedown', handleOutsideClick);
  window.removeEventListener('scroll', handleReposition, true);
  window.removeEventListener('resize', handleReposition);
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

.poppins { font-family: 'Poppins', sans-serif; }

.searchable-select {
  position: relative;
  width: 100%;
}

/* Trigger */
.select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  width: 100%;
  border: 1px solid #e5e7eb;
  padding: 8px 10px;
  font-size: 14px;
  background: #fff;
  border-radius: 1px;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
  min-height: 38px;
  user-select: none;
}

.select-trigger:hover:not(.is-disabled) {
  border-color: #fe3787;
}

.select-trigger.is-open {
  border-color: #fe3787;
  box-shadow: 0 0 0 3px rgba(254, 55, 135, 0.1);
}

.select-trigger.is-disabled {
  background: #f9fafb;
  cursor: not-allowed;
  opacity: 0.6;
}

.select-value {
  font-size: 13px;
  font-weight: 500;
  color: #111827;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.select-placeholder {
  font-size: 13px;
  color: #9ca3af;
  flex: 1;
}

.select-icons {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #e5e7eb;
  border: none;
  cursor: pointer;
  color: #6b7280;
  font-size: 10px;
  transition: background 0.15s, color 0.15s;
  padding: 0;
}
.clear-btn:hover {
  background: #fe3787;
  color: white;
}

.chevron-icon {
  font-size: 14px;
  color: #9ca3af;
  transition: transform 0.2s ease;
}
.chevron-icon.rotated {
  transform: rotate(180deg);
}

/* Dropdown (rendered via Teleport to body) */
.select-dropdown {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12), 0 4px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  animation: dropdownIn 0.12s ease-out;
}

@keyframes dropdownIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Search */
.search-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid #f3f4f6;
  background: #fafafa;
}
.search-icon {
  color: #9ca3af;
  font-size: 14px;
  flex-shrink: 0;
}
.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 13px;
  font-weight: 400;
  color: #111827;
  background: transparent;
}
.search-input::placeholder {
  color: #9ca3af;
}
.search-count {
  font-size: 10px;
  font-weight: 700;
  color: #9ca3af;
  background: #e5e7eb;
  padding: 2px 6px;
  border-radius: 10px;
}

/* Options */
.options-list {
  max-height: 240px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #e5e7eb transparent;
}
.options-list::-webkit-scrollbar { width: 4px; }
.options-list::-webkit-scrollbar-track { background: transparent; }
.options-list::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 4px; }
.options-list::-webkit-scrollbar-thumb:hover { background: #d1d5db; }

.option-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 14px;
  cursor: pointer;
  transition: background 0.1s;
  gap: 8px;
}
.option-item:hover,
.option-item.is-highlighted {
  background: #fff5f9;
}
.option-item.is-selected {
  background: #fef1f6;
}
.option-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}
.option-label {
  font-size: 13px;
  font-weight: 500;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.option-item.is-selected .option-label {
  color: #fe3787;
  font-weight: 600;
}
.option-sublabel {
  font-size: 10px;
  color: #9ca3af;
  font-weight: 400;
  margin-top: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.option-check {
  color: #fe3787;
  font-size: 14px;
  flex-shrink: 0;
}

/* No results */
.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 24px 16px;
  color: #9ca3af;
  font-size: 12px;
  font-style: italic;
}
.no-results i {
  font-size: 20px;
  opacity: 0.5;
}

/* Footer */
.dropdown-footer {
  padding: 6px 12px;
  border-top: 1px solid #f3f4f6;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #d1d5db;
  background: #fafafa;
}
</style>
