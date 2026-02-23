<template>
  <div class="flex flex-col h-screen bg-[#FDFCF7] font-sans">
    <div class="bg-gradient-to-r from-pink-500 to-pink-400 text-white px-6 py-4 flex items-center justify-between shadow-md z-20">
      <div class="flex items-center gap-4">
        <button @click="toggleSidebar" class="p-2 hover:bg-pink-600 rounded-lg transition-colors focus:outline-none">
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
        <button @click="toggleDropdown" class="flex items-center gap-3 hover:bg-pink-600 p-2 rounded-lg transition-colors focus:outline-none">
          <span class="text-sm font-medium">{{ userFullName }}</span>
          <div class="w-10 h-10 bg-white rounded-full flex items-center justify-center overflow-hidden border-2 border-pink-300">
             <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-gray-600 font-bold uppercase">{{ initials }}</div>
          </div>
        </button>
        <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-100">
           <button @click="handleLogout" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 font-medium">Logout</button>
        </div>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <div :class="['bg-gradient-to-b from-pink-500 to-pink-400 text-white transition-all duration-300 ease-in-out flex flex-col z-10 shadow-lg', sidebarOpen ? 'w-64' : 'w-20']">
        <div class="flex flex-col h-full overflow-y-auto">
           <button @click="$router.push('/instructor/dashboard')" class="flex items-center py-4 hover:bg-pink-600 transition-colors border-b border-pink-400 justify-center">
             <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
             </svg>
             <span v-show="sidebarOpen" class="text-lg font-medium ml-3">Home</span>
           </button>
           <div v-for="sidebarSection in sidebarSections" :key="sidebarSection.id" @click="goToSection(sidebarSection.id)" :class="['flex items-center py-3 px-6 hover:bg-pink-600 cursor-pointer transition-colors border-b border-pink-400/20', route.params.id == sidebarSection.id ? 'bg-pink-700' : '']">
              <div class="w-8 h-8 rounded-full bg-white text-pink-500 flex items-center justify-center font-black text-xs flex-shrink-0 shadow-sm uppercase">
                {{ sidebarSection.section_name.charAt(0) }}
              </div>
              <span v-show="sidebarOpen" class="ml-3 truncate text-sm font-bold tracking-wide uppercase">{{ sidebarSection.section_name }}</span>
           </div>
        </div>
      </div>

      <div class="flex-1 overflow-auto bg-[#FDFCF7]">
        <div class="p-8">
          <div>
            <h2 class="text-4xl font-serif text-lack font-bold">
              {{ section?.section_code }} - {{ section?.section_name }}
            </h2>
          </div><br>

          <div class="flex items-center gap-8 border-b border-gray-300 mb-8 px-2 relative">
            <button @click="$router.push(`/instructor/section/${route.params.id}`)" class="pb-3 text-sm font-black uppercase text-gray-400 hover:text-gray-600">Activity</button>
            <button class="pb-3 text-sm font-black uppercase border-b-4 border-[#0E8028] text-gray-800">People</button>
            <button class="pb-3 text-sm font-black uppercase text-gray-400 hover:text-gray-600">Settings</button>
            
            <div class="ml-auto flex gap-3 mb-2">
              <button @click="openEnrollModal" class="bg-[#F4D03F] text-[#0A3D16] px-5 py-2 rounded font-black text-[10px] uppercase shadow-md hover:scale-105 transition-transform">Add Student</button>
            </div>
          </div>

          <div class="max-w-6xl mx-auto space-y-12">
  
            <section>
              <div class="flex items-center justify-between border-b-2 border-green-700 pb-2 mb-4">
                <h3 class="text-xl font-bold text-green-800 uppercase tracking-wide">Instructor</h3>
              </div>
              
              <div class="flex items-center gap-4 px-4 py-3 bg-white rounded-lg border border-gray-100 shadow-sm">
                <div class="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center border border-gray-200">
                  <span class="text-gray-500 font-bold text-sm">{{ initials }}</span>
                </div>
                <div>
                  <p class="font-semibold text-gray-900 leading-tight">{{ userFullName }}</p>
                  <p class="text-[11px] text-gray-500 uppercase tracking-wider">Instructor in Charge</p>
                </div>
              </div>
            </section>

            <section>
              <div class="flex items-center justify-between border-b-2 border-green-700 pb-2 mb-0">
                <h3 class="text-xl font-bold text-green-800 uppercase tracking-wide">Students</h3>
                <span class="text-sm font-medium text-gray-500">{{ enrolledStudents.length }} enrolled</span>
              </div>
              
              <div class="bg-white rounded-b-lg shadow-sm border border-gray-100 divide-y divide-gray-100">
                <div v-for="student in enrolledStudents" :key="student.id" 
                    class="group flex items-center justify-between p-4 px-6 hover:bg-gray-50 transition-colors">
                  
                  <div class="flex items-center gap-4">
                    <div class="w-9 h-9 bg-pink-50 rounded-full flex items-center justify-center text-pink-600 font-bold text-xs border border-pink-100">
                      {{ student.first_name.charAt(0) }}
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 items-center">
                      <p class="font-medium text-gray-900">{{ student.first_name }} {{ student.last_name }}</p>
                      <p class="text-xs text-gray-400 font-mono hidden md:block">#{{ student.student_number }}</p>
                    </div>
                  </div>

                  <div class="flex items-center gap-6">
                    <span class="text-[11px] text-gray-400 font-medium uppercase tracking-tight hidden sm:block">
                      Joined {{ student.enrolled_at }}
                    </span>
                    <button class="text-gray-300 hover:text-red-500 transition-colors">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>

                <div v-if="enrolledStudents.length === 0" class="p-12 text-center">
                  <p class="text-gray-400 text-sm italic">No students currently enrolled in this section.</p>
                </div>
              </div>
            </section>

          </div>

          </div>
        </div>
      </div>
    </div>

    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/20 backdrop-blur-sm">
      <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="bg-[#FF579A] p-6 text-white flex justify-between items-center">
          <h3 class="text-xl font-bold">Enroll Student</h3>
          <button @click="isModalOpen = false" class="hover:rotate-90 transition-transform">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-8">
          <div class="mb-6">
            <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Enter Student Number</label>
            <input 
              v-model="studentNumberInput"
              type="text" 
              placeholder="e.g. 21-0001"
              class="w-full p-4 border-2 border-gray-100 rounded-xl focus:border-[#FF579A] outline-none transition-all text-lg font-medium"
            />
          </div>
          <div class="flex gap-4">
            <button @click="isModalOpen = false" class="flex-1 py-3 text-gray-400 font-bold hover:bg-gray-50 rounded-xl transition-colors uppercase text-xs">Cancel</button>
            <button @click="submitEnrollment" :disabled="loading" class="flex-1 py-3 bg-[#0E8028] text-white font-bold rounded-xl shadow-lg hover:bg-green-700 transition-colors uppercase text-xs">
              {{ loading ? 'Enrolling...' : 'Enroll Student' }}
            </button>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api/axios'
import { sectionDetailsService } from '@/services/instructor/sectionDetailsService'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { sectionPeopleListService } from '@/services/instructor/sectionPeopleListService'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()

// Data State
const section = ref(null)
const sidebarSections = ref([])
const enrolledStudents = ref([])
const sidebarOpen = ref(false)
const dropdownOpen = ref(false)

// Modal State
const isModalOpen = ref(false)
const studentNumberInput = ref('')
const loading = ref(false)

// Logic: Modals
const openEnrollModal = () => {
  studentNumberInput.value = ''
  isModalOpen.value = true
}

const submitEnrollment = async () => {
  if (!studentNumberInput.value) {
    notificationStore.warn("Please enter a student number")
    return
  }
  
  loading.value = true
  try {
    const sectionId = route.params.id
    const token = localStorage.getItem('auth_token')
    
    const response = await api.post(`api/instructor/sections/${sectionId}/enroll/`, 
      { student_number: studentNumberInput.value }
    )
    
    notificationStore.success(response.data.message)
    isModalOpen.value = false
    await fetchAllData() // Refresh student list
  } catch (error) {
    notificationStore.error(error.response?.data?.error || "Failed to enroll student")
  } finally {
    loading.value = false
  }
}

// Logic: UI Toggles
const toggleSidebar = () => { sidebarOpen.value = !sidebarOpen.value }
const toggleDropdown = () => { dropdownOpen.value = !dropdownOpen.value }

// Logic: Computed Props
const userFullName = computed(() => userStore.userFullName || "Instructor")
const initials = computed(() => userStore.userInitials)

// Logic: Auth/Nav
const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
const goToSection = (id) => { router.push(`/instructor/section/${id}`) }

// Logic: Data Fetching
const fetchAllData = async () => {
  try {
    const id = route.params.id;
    // 1. Fetch Section Details
    section.value = await sectionDetailsService.getSectionDetails(id);
    // 2. Fetch Enrolled Students from Django API
    enrolledStudents.value = await sectionPeopleListService.getEnrolledStudents(id);
    // 3. Fetch Sidebar Navigation
    const dashData = await instructorDashboardService.getDashboard();
    sidebarSections.value = dashData.sections;
    
    // 4. Ensure user data is loaded in store
    await userStore.ensureUserLoaded();
  } catch (error) { 
    console.error("Failed to load people data", error) 
  }
}

watch(() => route.params.id, () => { fetchAllData() })
onMounted(fetchAllData)
</script>