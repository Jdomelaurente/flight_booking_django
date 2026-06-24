<template>
  <div class="p-0.5 space-y-4 bg-gray-100 min-h-screen">
    
    <!-- Module Switcher Hub (Visible for Superadmins or users with multiple roles) -->
    <div v-if="canSwitchModules" class="sticky top-0 z-40 bg-white/80 backdrop-blur-md border border-gray-200 p-1.5 flex gap-1.5 rounded-[1px] shadow-lg mb-2 no-print">
      <button 
        @click="activeModule = 'flight'"
        :class="activeModule === 'flight' ? 'bg-[#002D1E] text-white shadow-lg scale-[1.02]' : 'bg-gray-50 text-gray-500 hover:bg-gray-100'"
        class="flex-1 py-3 text-[10px] font-black uppercase tracking-[0.3em] poppins transition-all duration-300 rounded-[1px] flex items-center justify-center gap-2 group"
      >
        <i class="ph ph-airplane text-lg px-2 py-1 rounded-[1px]" :class="activeModule === 'flight' ? 'bg-white/10' : 'bg-gray-200'"></i>
        Flight Management
      </button>
      
      <button 
        @click="activeModule = 'lms'"
        :class="activeModule === 'lms' ? 'bg-[#fe3787] text-white shadow-lg scale-[1.02]' : 'bg-gray-50 text-gray-500 hover:bg-gray-100'"
        class="flex-1 py-3 text-[10px] font-black uppercase tracking-[0.3em] poppins transition-all duration-300 rounded-[1px] flex items-center justify-center gap-2 group"
      >
        <i class="ph ph-graduation-cap text-lg px-2 py-1 rounded-[1px]" :class="activeModule === 'lms' ? 'bg-white/10' : 'bg-gray-200'"></i>
        School Management
      </button>
    </div>

    <!-- Active Module View -->
    <transition name="fade" mode="out-in">
      <div :key="activeModule">
        <FlightModule v-if="activeModule === 'flight'" />
        <LmsModule v-else-if="activeModule === 'lms'" />
      </div>
    </transition>

    <!-- Role-based Access Restriction Notice -->
    <div v-if="!activeModule" class="flex flex-col items-center justify-center h-[60vh] text-gray-400">
       <i class="ph ph-lock-keyhole text-6xl mb-4 opacity-20"></i>
       <p class="text-[10px] uppercase font-black tracking-widest poppins">Access Restricted: Module Not Assigned</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import AuthStorage from '@/utils/authStorage'
import FlightModule from './dashboard/modules/FlightModule.vue'
import LmsModule from './dashboard/modules/LmsModule.vue'

const activeModule = ref(null)

const userRole = computed(() => {
  return AuthStorage.getRole() || 'admin'
})

const isSuperAdmin = computed(() => userRole.value === 'superadmin')

const canSwitchModules = computed(() => {
  return isSuperAdmin.value
})

onMounted(() => {
  // Initial module selection based on role
  if (isSuperAdmin.value) {
    activeModule.value = 'flight' // Default to flight for superadmin
  } else if (userRole.value === 'lms_admin') {
    activeModule.value = 'lms'
  } else {
    activeModule.value = 'flight'
  }
})
</script>

<style scoped>
.poppins { font-family: 'Poppins', sans-serif; }

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>