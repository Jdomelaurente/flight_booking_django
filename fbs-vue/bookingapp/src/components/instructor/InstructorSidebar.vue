<template>
  <div
    :class="[
      'relative bg-white text-gray-600 transition-all duration-300 ease-in-out flex flex-col z-10 border-r border-gray-100 shadow-sm h-full',
      sidebarOpen ? 'w-60' : 'w-16'
    ]"
  >
    <!-- Navigation Links -->
    <nav class="flex-1 flex flex-col overflow-y-auto py-3 gap-0.5 px-2">

      <!-- Main Nav Items -->
      <template v-for="item in navItems" :key="item.to">
        <router-link
          :to="item.to"
          :class="[
            'flex items-center gap-3 rounded-xl transition-all duration-200 group relative',
            sidebarOpen ? 'px-3 py-2.5' : 'justify-center p-3 mx-auto w-10 h-10',
            'hover:bg-[#FF579A]/10 hover:text-[#FF579A]'
          ]"
          active-class="!bg-[#FF579A]/10 !text-[#FF579A] font-semibold"
        >
          <!-- Active Indicator Bar -->
          <span
            class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 rounded-r-full bg-[#FF579A] opacity-0 group-[.router-link-active]:opacity-100 transition-opacity"
          ></span>

          <component :is="'svg'" xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5 flex-shrink-0 transition-transform group-hover:scale-110" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="item.icon"></component>

          <span v-show="sidebarOpen" class="text-[13px] font-medium truncate flex-1">{{ item.label }}</span>

          <!-- Badge for Activities -->
          <span
            v-if="sidebarOpen && item.badge && item.badge > 0"
            class="ml-auto bg-[#FF579A]/10 text-[#FF579A] text-[10px] font-black px-2 py-0.5 rounded-full group-[.router-link-active]:bg-[#FF579A] group-[.router-link-active]:text-white"
          >
            {{ item.badge }}
          </span>
          <span
            v-if="!sidebarOpen && item.badge && item.badge > 0"
            class="absolute top-0.5 right-0.5 bg-[#FF579A] text-white text-[8px] font-black rounded-full w-4 h-4 flex items-center justify-center"
          >
            {{ item.badge > 9 ? '9+' : item.badge }}
          </span>

          <!-- Tooltip when collapsed -->
          <div
            v-if="!sidebarOpen"
            class="absolute left-full ml-3 px-2.5 py-1.5 bg-slate-800 text-white text-xs font-semibold rounded-lg opacity-0 group-hover:opacity-100 transition-all pointer-events-none whitespace-nowrap z-50 shadow-xl"
          >
            {{ item.label }}
            <div class="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-slate-800"></div>
          </div>
        </router-link>
      </template>

      <!-- Divider -->
      <div v-if="sidebarOpen" class="my-2 border-t border-gray-100 mx-1"></div>
      <div v-else class="my-2 border-t border-gray-100"></div>

      <!-- Sections Sub-nav (collapsed shortcut) -->
      <div v-if="sidebarOpen && sections && sections.length > 0">
        <p class="text-[9px] uppercase tracking-[0.15em] font-black text-slate-400 px-3 mb-1.5">My Sections</p>
        <div class="space-y-0.5 max-h-40 overflow-y-auto pr-1">
          <button
            v-for="section in sections.slice(0, 5)"
            :key="section.id"
            @click="$emit('go-to-section', section.id)"
            :class="[
              'w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-left transition-all hover:bg-[#FF579A]/10 hover:text-[#FF579A] group',
              isSectionActive(section.id) ? 'bg-[#FF579A]/10 text-[#FF579A]' : 'text-slate-500'
            ]"
          >
            <span
              :class="[
                'w-6 h-6 rounded-lg flex items-center justify-center text-[10px] font-black flex-shrink-0 transition-colors',
                isSectionActive(section.id) ? 'bg-[#FF579A] text-white' : 'bg-slate-100 text-slate-500 group-hover:bg-[#FF579A] group-hover:text-white'
              ]"
            >
              {{ section.section_name?.charAt(0)?.toUpperCase() }}
            </span>
            <div class="flex-1 min-w-0">
              <p class="text-[11px] font-bold truncate leading-tight">{{ section.section_name }}</p>
              <p class="text-[9px] font-medium text-slate-400 truncate">{{ section.section_code }}</p>
            </div>
          </button>
          <button
            v-if="sections.length > 5"
            @click="$emit('nav', '/instructor/sections')"
            class="w-full text-[10px] text-[#FF579A] font-bold px-3 py-1.5 text-left hover:underline"
          >
            +{{ sections.length - 5 }} more sections →
          </button>
        </div>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()

const props = defineProps({
  sidebarOpen: Boolean,
  sections: Array
})

defineEmits(['nav', 'go-to-section'])

const isSectionActive = (sectionId) => {
  return route.path.includes(`/instructor/section/${sectionId}`)
}

const totalActivities = computed(() => {
  if (!props.sections) return 0
  return props.sections.reduce((total, section) => total + (section.activity_count || 0), 0)
})

const navItems = computed(() => [
  {
    to: '/instructor/dashboard',
    label: 'Dashboard',
    icon: '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>'
  },
  {
    to: '/instructor/sections',
    label: 'Sections',
    icon: '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>'
  },
  {
    to: '/instructor/activities',
    label: 'Activities',
    icon: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>',
    badge: totalActivities.value
  },
  {
    to: '/instructor/students',
    label: 'Students',
    icon: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
  },
  {
    to: '/instructor/reports',
    label: 'Reports',
    icon: '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>'
  },
  {
    to: '/instructor/logs',
    label: 'Activity Logs',
    icon: '<path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>'
  },
])
</script>
