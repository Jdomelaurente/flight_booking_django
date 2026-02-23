<template>
  <div 
    :class="[
      'bg-pink-500 text-white transition-all duration-300 ease-in-out flex flex-col shadow-lg overflow-hidden', 
      sidebarOpen ? 'w-56' : 'w-0'
    ]"
  >
    <div v-show="sidebarOpen" class="flex flex-col h-full overflow-y-auto">
      <!-- Home Button -->
      <button 
        @click="$emit('go-home')"
        class="flex items-center px-4 py-3 hover:bg-pink-600 transition-colors border-b border-pink-400/30"
      >
        <div class="w-7 h-7 flex items-center justify-center flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
        </div>
        <span class="text-sm font-medium ml-3 whitespace-nowrap">Home</span>
      </button>

      <!-- Calendar Button -->
      <button 
        class="flex items-center px-4 py-3 hover:bg-pink-600 transition-colors border-b border-pink-400/30"
      >
        <div class="w-7 h-7 flex items-center justify-center flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
          </svg>
        </div>
        <span class="text-sm font-medium ml-3 whitespace-nowrap">Calendar</span>
      </button>

      <!-- Tasks Button -->
      <button 
        class="flex items-center px-4 py-3 hover:bg-pink-600 transition-colors border-b border-pink-400/30"
      >
        <div class="w-7 h-7 flex items-center justify-center flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
          </svg>
        </div>
        <span class="text-sm font-medium ml-3 whitespace-nowrap">Tasks</span>
      </button>

      <!-- My Section (Only if enrolled) -->
      <div 
        v-if="section"
        class="flex items-center px-4 py-3 bg-pink-600 border-b border-pink-400/20"
      >
        <div class="w-7 h-7 rounded-full bg-white text-pink-500 flex items-center justify-center font-bold text-xs flex-shrink-0 shadow-sm">
          {{ section.section_name.charAt(0).toUpperCase() }}
        </div>
        <div class="ml-3 flex-1">
          <span class="block truncate text-sm font-medium">
            {{ section.section_name }}
          </span>
          <span class="text-[10px] opacity-80">
            {{ section.activities_count }} activities
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardSidebar',
  props: {
    sidebarOpen: {
      type: Boolean,
      required: true
    },
    section: {
      type: Object,
      default: null
    }
  }
}
</script>
