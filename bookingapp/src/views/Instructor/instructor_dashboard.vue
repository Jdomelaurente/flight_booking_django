<template>
  <div class="flex flex-col h-screen bg-gray-50 font-sans">
    <div class="bg-gradient-to-r from-pink-500 to-pink-400 text-white px-6 py-4 flex items-center justify-between shadow-md z-20">
      <div class="flex items-center gap-4">
        <button 
          @click="toggleSidebar" 
          class="p-2 hover:bg-pink-600 rounded-lg transition-colors focus:outline-none"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
        
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center text-2xl shadow-inner">🎓</div>
          <div>
            <h1 class="text-sm font-bold uppercase tracking-tight">CABAGAN STATE UNIVERSITY</h1>
            <p class="text-[10px] opacity-90">Cabagan City</p>
          </div>
        </div>
      </div>

      <div class="relative">
        <button 
          @click="toggleDropdown" 
          class="flex items-center gap-3 hover:bg-pink-600 p-2 rounded-lg transition-colors focus:outline-none"
        >
          <span class="text-sm font-medium">{{ fullName }}</span>
          <div class="w-10 h-10 bg-white rounded-full flex items-center justify-center overflow-hidden border-2 border-pink-300">
             <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-gray-600 font-bold uppercase">{{ initials }}</div>
          </div>
        </button>

        <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-100">
           <button @click="handleLogout" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">Logout</button>
        </div>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <div 
        :class="[
          'bg-gradient-to-b from-pink-500 to-pink-400 text-white transition-all duration-300 ease-in-out flex flex-col z-10 shadow-lg', 
          sidebarOpen ? 'w-64' : 'w-20'
        ]"
      >
        <div class="flex flex-col h-full overflow-y-auto">
           <button class="flex items-center py-4 hover:bg-pink-600 transition-colors border-b border-pink-400 justify-center">
             <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
             </svg>
             <span v-show="sidebarOpen" class="text-lg font-medium ml-3">Home</span>
           </button>

           <div v-for="section in sections" :key="section.id" @click="goToSection(section.id)" class="flex items-center py-3 px-6 hover:bg-pink-600 cursor-pointer transition-colors border-b border-pink-400/20">
              <div class="w-8 h-8 rounded-full bg-white text-pink-500 flex items-center justify-center font-black text-xs flex-shrink-0 shadow-sm uppercase">
                {{ section.section_name.charAt(0) }}
              </div>
              <span v-show="sidebarOpen" class="ml-3 truncate text-sm font-bold tracking-wide uppercase">{{ section.section_name }}</span>
           </div>
        </div>
      </div>

      <div class="flex-1 overflow-auto bg-gray-50 ">
        <div class="p-8">
          <div class="mb-6">
              <h2 class="text-3xl font-bold text-gray-800 tracking-tight">SECTIONS</h2>
              <p class="text-gray-500 mt-1">Welcome back, {{ fullName }}!</p>
          </div><br></br>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-300 ml-27">
            
            <div 
              @click="showModal = true"
              class="border-2 border-dashed border-gray-300 rounded-lg p-8 flex flex-col items-center justify-center cursor-pointer hover:border-pink-400 hover:bg-pink-50 transition-all min-h-[220px]"
            >
              <div class="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mb-3">
                <span class="text-3xl text-gray-400">+</span>
              </div>
              <p class="text-gray-600 font-bold uppercase text-xs tracking-widest">Add section</p>
            </div>

            <template v-if="sections && sections.length > 0">
              <div v-for="section in sections" :key="section.id" @click="goToSection(section.id)" class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow border border-gray-100 flex flex-col min-h-[220px] cursor-pointer group/card">
                  <div class="bg-[#e93d82] text-white px-4 py-3 flex justify-between items-center group-hover/card:bg-pink-600 transition-colors">
                    <h3 class="font-bold tracking-wide uppercase text-sm text-white">
                      {{ section.section_code }}
                    </h3>
                    
                    <div class="relative group">
                      <button @click.stop class="text-white/100 hover:text-white p-1">⋮</button>
                      <div class="hidden group-hover:block absolute right-0 top-full w-32 bg-white shadow-xl rounded border border-gray-100 z-30 overflow-hidden">
                        <button @click.stop="editSection(section)" class="block w-full text-left px-4 py-2 text-[10px] text-gray-700 hover:bg-gray-50 font-bold uppercase">Edit</button>
                        <button @click.stop="deleteSection(section.id)" class="block w-full text-left px-4 py-2 text-[10px] text-red-600 hover:bg-red-50 font-bold uppercase">Delete</button>
                      </div>
                    </div>
                  </div>

                  <div class="p-5 flex-1">
                    <div class="flex justify-between items-start mb-1">
                      <p class="text-[10px] font-black text-[#0E8028] uppercase tracking-widest">
                        {{ section.section_name }}
                      </p>
                      <p v-if="section.schedule" class="text-[9px] font-bold text-green-700 bg-green-50 px-2 py-0.5 rounded border border-green-100 uppercase">
                        {{ section.schedule }}
                      </p>
                    </div>

                    <p class="text-sm text-gray-400 italic line-clamp-3 leading-relaxed mt-2">
                      {{ section.description || 'No description provided.' }}
                    </p>
                  </div>

                  <div class="px-5 py-3 bg-gray-50 border-t border-gray-100 flex justify-between items-center text-[10px] text-[#0E8028] font-bold uppercase">
                    <div class="flex flex-col">
                        <span>{{ section.semester }}</span>
                        <span class="text-[8px] lowercase opacity-70">0 students - 0 activities</span>
                    </div>
                    <span>{{ section.academic_year }}</span>
                  </div>
              </div>
            </template>

            <div v-else class="col-span-full py-10 text-center bg-white rounded-lg border border-gray-100">
                <p class="text-gray-400 italic">No sections found in the database for your account.</p>
            </div>

          </div>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[1px] px-4">
      <div class="bg-white rounded-lg shadow-2xl w-full max-w-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="bg-pink-500 text-white px-6 py-4 flex justify-between items-center">
          <h3 class="text-lg font-bold uppercase tracking-tight">Create New Section</h3>
          <button @click="showModal = false" class="text-white hover:text-pink-200 text-2xl transition-colors">&times;</button>
        </div>

        <form @submit.prevent="submitSection" class="p-8">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Section Name <span class="text-red-500 font-bold">*</span></label>
              <input v-model="form.section_name" type="text" placeholder="e.g., BSIT 3A" class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50" required>
            </div>
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Section Code <span class="text-red-500 font-bold">*</span></label>
              <input v-model="form.section_code" type="text" placeholder="e.g., IT311" class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50" required>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Semester <span class="text-red-500 font-bold">*</span></label>
              <select v-model="form.semester" class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50" required>
                <option value="" disabled>Select Semester</option>
                <option value="1st Semester">1st Semester</option>
                <option value="2nd Semester">2nd Semester</option>
              </select>
            </div>
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Academic Year <span class="text-red-500 font-bold">*</span></label>
              <input v-model="form.academic_year" type="text" placeholder="2024-2025" class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50" required>
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Schedule</label>
            <input v-model="form.schedule" type="text" placeholder="e.g., M-W-F 8:00 AM - 10:00 AM" class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50">
          </div>

          <div class="mb-6">
            <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Description</label>
            <textarea v-model="form.description" rows="3" placeholder="Enter course details..." class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none resize-none bg-gray-50"></textarea>
          </div>

          <div class="flex justify-end gap-4 border-t pt-6">
            <button type="button" @click="showModal = false" class="text-gray-400 font-bold uppercase text-xs hover:text-gray-600 transition-colors">Cancel</button>
            <button type="submit" class="px-8 py-3 bg-pink-500 text-white rounded-lg font-black uppercase text-xs shadow-lg active:scale-95 transition-all">Create Section</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
// Import the new API service
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'
import { useModalStore } from '@/stores/modal'

const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()
const modalStore = useModalStore()

const sidebarOpen = ref(false) 
const dropdownOpen = ref(false)
const showModal = ref(false)
const sections = ref([])

// Form state for creating a new section
const form = ref({
  section_name: '',
  section_code: '',
  semester: '',
  academic_year: '',
  schedule: '',
  description: ''
})

// Computed: Full name display logic
const fullName = computed(() => {
  if (userStore.user.first_name && userStore.user.last_name) return `${userStore.user.first_name} ${userStore.user.last_name}`
  if (userStore.user.first_name) return userStore.user.first_name
  return userStore.user.username || 'Instructor'
})

// Computed: User initials for the avatar
const initials = computed(() => {
  const u = userStore.user?.username || 'I'
  return u[0].toUpperCase()
})

// UI Toggles
const toggleSidebar = () => { sidebarOpen.value = !sidebarOpen.value }
const toggleDropdown = () => { dropdownOpen.value = !dropdownOpen.value }

// Navigation logic for Section Details
const goToSection = (id) => {
  router.push(`/instructor/section/${id}`)
}

// Logout logic
const handleLogout = () => {
  localStorage.clear()
  router.push('/login')
}

/**
 * Action: Fetch data from Backend
 */
const fetchInstructorData = async () => {
  try {
    const data = await instructorDashboardService.getDashboard();
    
    // Update local refs with data from Django
    sections.value = data.sections;
    if (data.user) {
      userStore.user = data.user;
    }
  } catch (error) {
    if (error.response?.status === 401 || error.response?.status === 403) {
      // If unauthorized, boot to login
      handleLogout();
    }
  }
}

/**
 * Action: Submit new section
 */
const submitSection = async () => {
  try {
    await instructorDashboardService.createSection(form.value);
    
    // Reset UI state
    showModal.value = false;
    form.value = { 
      section_name: '', section_code: '', semester: '', 
      academic_year: '', schedule: '', description: '' 
    };
    
    // Refresh the list immediately
    await fetchInstructorData();
    notificationStore.success("Section created successfully!");
  } catch (error) {
    const serverMessage = error.response?.data?.error || "Check if Section Code is unique.";
    notificationStore.error("Backend Error: " + serverMessage);
  }
};

/**
 * Action: Delete a section
 */
const deleteSection = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Delete Section?',
    message: 'Are you sure you want to delete this section? This action cannot be undone and all associated students and activities will be lost.',
    confirmText: 'Delete',
    cancelText: 'Cancel'
  })

  if (confirmed) {
    try {
      await instructorDashboardService.deleteSection(id);
      notificationStore.success("Section deleted successfully.");
      await fetchInstructorData(); // Refresh list
    } catch (error) {
      notificationStore.error("Failed to delete section.");
    }
  }
}

// Lifecycle: Initialize data
onMounted(async () => {
  await userStore.ensureUserLoaded();
  await fetchInstructorData();
})
</script>