<template>
  <div class="sidebar-wrapper h-full">
    <Transition name="fade">
      <div 
        v-if="sidebarOpen" 
        class="fixed inset-0 bg-gray-900/40 backdrop-blur-sm z-[90] lg:hidden"
        @click="$emit('close-sidebar')"
      ></div>
    </Transition>

    <div 
      :class="[
        'bg-[#F9F9F9] text-gray-800 transition-all duration-300 ease-in-out flex flex-col font-normal overflow-hidden z-[100]',
        'fixed inset-y-0 left-0 lg:relative lg:inset-auto lg:h-full border-r border-gray-200/50',
        sidebarOpen ? 'w-64 translate-x-0' : 'w-20 -translate-x-full lg:translate-x-0'
      ]"
    >
      <div class="flex-shrink-0 w-full flex flex-col h-full overflow-y-auto space-y-2 mt-6 no-scrollbar">
        <!-- Navigation Links -->
        <router-link 
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center mx-3 px-3 py-2 rounded-full transition-all duration-300 group relative"
          :class="[
            $route.path === item.to ? 'bg-[#FF579A] text-white ' : 'hover:bg-pink-50 text-gray-600 hover:text-[#FF579A]'
          ]"
        >
          <div class="flex items-center justify-center w-8 flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
            <i :class="[item.icon, 'text-xl']"></i>
          </div>
          <div 
            class="ml-4 flex-1 overflow-hidden transition-all duration-300 ease-in-out"
            :class="[sidebarOpen ? 'max-w-[200px] opacity-100' : 'max-w-0 opacity-0']"
          >
            <span class="text-sm font-semibold tracking-wide whitespace-nowrap">{{ item.label }}</span>
          </div>

          <!-- Tooltip for collapsed state -->
          <div v-if="!sidebarOpen" class="absolute left-full ml-4 px-2 py-1 bg-gray-900 text-white text-[10px] rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-[110]">
            {{ item.label }}
          </div>
        </router-link>

        <!-- My Section (Only if enrolled) -->
        <router-link 
          v-if="section"
          to="/student/dashboard"
          class="flex items-center mt-auto border-t border-gray-200/50 transition-all duration-300 group hover:bg-black/5"
          :class="sidebarOpen ? 'px-6 py-5' : 'px-0 justify-center py-6'"
        >
          <div 
            :class="[
              'rounded-xl bg-white text-[#FF579A] flex items-center justify-center font-bold shadow-sm transition-all duration-300 border border-pink-100 flex-shrink-0',
              sidebarOpen ? 'w-12 h-12 text-xl group-hover:rotate-6' : 'w-10 h-10 text-lg'
            ]"
          >
            {{ section.section_code?.charAt(0).toUpperCase() || section.section_name?.charAt(0).toUpperCase() }}
          </div>
          
          <div 
            class="overflow-hidden transition-all duration-300 ease-in-out"
            :class="[sidebarOpen ? 'ml-4 max-w-[150px] opacity-100' : 'max-w-0 opacity-0']"
          >
            <span class="block truncate text-sm font-black tracking-tight uppercase text-gray-800">
              {{ section.section_code || section.section_name }}
            </span>
            <span class="text-[10px] text-gray-500 font-bold flex items-center gap-1.5 mt-0.5">
              <span class="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></span>
              {{ section.activities_count || 0 }} Activities
            </span>
          </div>
        </router-link>
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
  },
  data() {
    return {
      navItems: [
        { to: '/student/dashboard', label: 'Dashboard', icon: 'ph ph-house' },
        { to: '/student/calendar', label: 'Calendar', icon: 'ph ph-calendar' }
      ]
    }
  }
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>

