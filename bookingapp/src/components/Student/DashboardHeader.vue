<template>
  <div class="bg-pink-500 text-white px-4 py-2.5 flex items-center justify-between shadow-md z-20">
    <div class="flex items-center gap-3">
      <button 
        @click="$emit('toggle-sidebar')" 
        class="p-1.5 hover:bg-pink-600/50 rounded transition-colors focus:outline-none"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </button>
      
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 bg-white rounded-full flex items-center justify-center text-base">🎓</div>
        <div>
          <h1 class="text-xs font-bold leading-tight">CARAGA STATE UNIVERSITY</h1>
          <p class="text-[9px] opacity-90 leading-tight">Cabadbaran City</p>
        </div>
      </div>
    </div>

    <div class="relative">
      <button 
        @click="toggleDropdown" 
        class="flex items-center gap-2 hover:bg-pink-600/50 px-2 py-1 rounded transition-colors focus:outline-none"
      >
        <div class="w-7 h-7 bg-white rounded-full flex items-center justify-center overflow-hidden border-2 border-white shadow-sm">
          <div class="w-full h-full bg-pink-200 flex items-center justify-center text-pink-700 font-bold text-xs">
            {{ initials }}
          </div>
        </div>
      </button>

      <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl py-1 z-50 border border-gray-100">
        <div class="px-4 py-3 border-b border-gray-100">
          <p class="text-sm font-semibold text-gray-800">{{ fullName }}</p>
          <p class="text-xs text-gray-500">{{ student?.email }}</p>
        </div>
        <button 
          @click="$router.push('/profile')" 
          class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
        >
          My Profile
        </button>
        <button 
          @click="$emit('logout')" 
          class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
        >
          Logout
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardHeader',
  props: {
    student: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      dropdownOpen: false
    }
  },
  computed: {
    fullName() {
      if (!this.student) return 'Student';
      return `${this.student.first_name || ''} ${this.student.last_name || ''}`.trim() || 'Student';
    },
    initials() {
      if (!this.student) return 'ST';
      const first = this.student.first_name?.charAt(0) || '';
      const last = this.student.last_name?.charAt(0) || '';
      return (first + last).toUpperCase() || 'ST';
    }
  },
  methods: {
    toggleDropdown() {
      this.dropdownOpen = !this.dropdownOpen;
    }
  },
  mounted() {
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.relative')) {
        this.dropdownOpen = false;
      }
    });
  }
}
</script>
