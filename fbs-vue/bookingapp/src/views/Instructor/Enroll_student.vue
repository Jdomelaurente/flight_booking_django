<template>
  <div class="flex flex-col h-screen bg-[#FDFCF7] font-sans">
    <div class="bg-[#F9F9F9] text-gray-800 px-6 py-2.5 flex items-center justify-between shadow-sm z-20 border-b border-gray-100">
      <div class="flex items-center gap-4">
        <button @click="toggleSidebar" class="p-1.5 hover:bg-pink-600 rounded-md transition-colors focus:outline-none">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-xl shadow-inner">🎓</div>
          <div>
            <h1 class="text-[10px] font-bold uppercase tracking-widest text-white/90">Cabagan State University</h1>
            <p class="text-[9px] uppercase tracking-tighter opacity-60">Faculty Portal</p>
          </div>
        </div>
      </div>

      <div class="relative">
        <button @click="toggleDropdown" class="flex items-center gap-2 hover:bg-gray-100 p-1.5 rounded-md transition-colors focus:outline-none">
          <span class="text-xs font-medium">{{ userFullName }}</span>
          <div class="w-8 h-8 bg-white rounded-full flex items-center justify-center overflow-hidden border border-gray-200">
             <div class="w-full h-full bg-pink-100 flex items-center justify-center text-pink-700 font-bold text-xs font-bold uppercase">{{ initials }}</div>
          </div>
        </button>
        <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-100">
           <button @click="handleLogout" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 font-medium">Logout</button>
        </div>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <div :class="['bg-[#F9F9F9] text-gray-600 transition-all duration-300 ease-in-out flex flex-col z-10 shadow-sm border-r border-gray-200', sidebarOpen ? 'w-56' : 'w-16']">
        <div class="flex flex-col h-full overflow-y-auto">
           <button @click="$router.push('/instructor/dashboard')" class="flex items-center py-3 hover:bg-[#FF579A]/10 hover:text-[#FF579A] transition-colors border-b border-gray-100 justify-center group">
             <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0 group-hover:scale-110 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
             </svg>
             <span v-show="sidebarOpen" class="text-sm font-medium ml-3">Home</span>
           </button>

           <button @click="$router.push('/instructor/logs')" class="flex items-center py-3 hover:bg-[#FF579A]/10 hover:text-[#FF579A] transition-colors border-b border-gray-100 justify-center group">
             <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0 group-hover:scale-110 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
             </svg>
             <span v-show="sidebarOpen" class="text-sm font-medium ml-3">Activity Logs</span>
           </button>
           <div 
             v-for="sidebarSection in sidebarSections" 
             :key="sidebarSection.id" 
             @click="goToSection(sidebarSection.id)" 
             :class="[
               'flex items-center py-3 hover:bg-[#FF579A]/10 hover:text-[#FF579A] cursor-pointer transition-colors border-b border-gray-100 group',
               sidebarOpen ? 'px-5' : 'justify-center',
               route.params.id == sidebarSection.id ? 'bg-pink-700' : ''
             ]"
           >
              <div class="w-8 h-8 rounded-lg bg-pink-100 text-pink-600 group-hover:bg-[#FF579A] group-hover:text-white flex items-center justify-center font-bold text-xs flex-shrink-0 transition-colors uppercase">{{ sidebarSection.section_name.charAt(0) }}</div>
              <span v-show="sidebarOpen" class="ml-3 truncate text-xs font-semibold uppercase text-gray-700 group-hover:text-[#FF579A] transition-colors">{{ sidebarSection.section_name }}</span>
           </div>
        </div>
      </div>

      <div class="flex-1 overflow-auto bg-[#FDFCF7]">
        <div class="p-8 max-w-5xl mx-auto">
          <div class="bg-[#0A3D16] rounded-xl p-8 mb-6 shadow-xl border-l-8 border-yellow-500">
            <h2 class="text-3xl font-light text-[#F4D03F] uppercase tracking-wide">
              {{ section?.section_code }} {{ section?.section_name }}
            </h2>
            <p class="text-white/80 text-sm mt-1 font-medium tracking-tight">Instructor: {{ userFullName }}</p>
          </div>

          <div class="flex items-center gap-8 border-b border-gray-300 mb-8 px-2 relative">
            <button @click="$router.push(`/instructor/section/${route.params.id}`)" class="pb-3 text-sm font-bold uppercase text-gray-400 hover:text-gray-600 tracking-wider">Assessments</button>
            <button class="pb-3 text-sm font-bold uppercase border-b-4 border-[#0A3D16] text-gray-800 tracking-wider">Student</button>
            <button class="pb-3 text-sm font-bold uppercase text-gray-400 hover:text-gray-600 tracking-wider">Section Settings</button>
            <div class="ml-auto flex gap-3 mb-2">
              <button @click="showStudentModal = true" class="bg-[#F4D03F] text-[#0A3D16] px-5 py-2 rounded font-bold text-xs uppercase tracking-widest shadow-md hover:translate-y-[-1px] transition-all">Enroll Student</button>
            </div>
          </div>

          <div class="space-y-8">
            <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div class="bg-[#0A3D16] py-3 px-6 text-center">
                <h3 class="text-white font-bold uppercase tracking-widest text-sm">Instructor</h3>
              </div>
              <div class="p-6 flex items-center gap-4">
                <div class="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center text-xl overflow-hidden border">
                   <span v-if="!userData?.profile_img">👤</span>
                </div>
                <span class="text-lg font-medium text-gray-800">{{ userFullName }}</span>
              </div>
            </div>

            <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div class="bg-[#0A3D16] py-3 px-6 flex justify-between items-center">
                <h3 class="text-white font-bold uppercase tracking-widest text-sm">Student</h3>
                <span class="text-white/70 text-xs font-medium">{{ students.length }} total</span>
              </div>
              <div class="divide-y divide-gray-100">
                <div v-for="student in students" :key="student.id" class="p-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
                  <div class="flex items-center gap-4">
                    <div class="w-10 h-10 bg-pink-100 text-pink-500 rounded-full flex items-center justify-center font-bold">
                      {{ student.first_name[0] }}{{ student.last_name[0] }}
                    </div>
                    <div>
                      <p class="font-bold text-gray-800 text-sm">{{ student.first_name }} {{ student.mi }}. {{ student.last_name }}</p>
                      <p class="text-[10px] text-gray-400 uppercase tracking-tighter">{{ student.student_number }}</p>
                    </div>
                  </div>
                  <button class="text-gray-400 hover:text-red-500">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  </button>
                </div>
                <div v-if="students.length === 0" class="p-12 text-center text-gray-400 italic">No students enrolled yet.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showStudentModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[2px] px-4">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-lg overflow-hidden animate-in zoom-in duration-200">
        <div class="bg-pink-500 text-white px-6 py-4 flex justify-between items-center">
          <h3 class="text-lg font-light uppercase tracking-wide">Enroll New Student</h3>
          <button @click="showStudentModal = false" class="text-2xl leading-none">&times;</button>
        </div>
        <form @submit.prevent="handleEnroll" class="p-6 space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5">Student Number</label>
            <input v-model="studentForm.student_number" type="text" placeholder="e.g. 2021-1234" class="w-full border rounded-lg px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-pink-400 bg-gray-50 font-medium" required>
          </div>
          <div class="grid grid-cols-3 gap-3">
            <div class="col-span-1">
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">First Name</label>
              <input v-model="studentForm.first_name" type="text" class="w-full border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-pink-400 bg-gray-50" required>
            </div>
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">MI</label>
              <input v-model="studentForm.mi" type="text" maxlength="1" class="w-full border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-pink-400 bg-gray-50">
            </div>
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Lastname</label>
              <input v-model="studentForm.last_name" type="text" class="w-full border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-pink-400 bg-gray-50" required>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Email</label>
              <input v-model="studentForm.email" type="email" class="w-full border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-pink-400 bg-gray-50" required>
            </div>
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Phone Number</label>
              <input v-model="studentForm.phone" type="text" class="w-full border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-pink-400 bg-gray-50">
            </div>
          </div>
          <div>
            <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Password</label>
            <input v-model="studentForm.password" type="password" class="w-full border rounded-lg px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-pink-400 bg-gray-50" required>
          </div>
          <div class="flex justify-end gap-3 pt-6 border-t border-gray-100">
            <button type="button" @click="showStudentModal = false" class="text-xs font-bold text-gray-400 uppercase tracking-widest px-4 py-2 hover:text-gray-600 transition-colors">Cancel</button>
            <button type="submit" class="bg-pink-500 text-white px-6 py-3 rounded-lg font-bold text-xs uppercase tracking-widest shadow-md hover:translate-y-[-1px] active:scale-95 transition-all">Enroll Student</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import CTHM from '@/assets/image/cthm-logos.png'
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { sectionDetailsService } from '@/services/instructor/sectionDetailsService'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const section = ref(null)
const sidebarSections = ref([])
const students = ref([]) // Local list for UI
const sidebarOpen = ref(false)
const dropdownOpen = ref(false)
const showStudentModal = ref(false)

const studentForm = ref({
  student_number: '',
  first_name: '',
  mi: '',
  last_name: '',
  email: '',
  phone: '',
  password: ''
})

const toggleSidebar = () => { sidebarOpen.value = !sidebarOpen.value }
const toggleDropdown = () => { dropdownOpen.value = !dropdownOpen.value }

const userFullName = computed(() => userStore.userFullName || "Instructor")
const initials = computed(() => userStore.userInitials)

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const goToSection = (id) => { router.push(`/instructor/section/${id}`) }

const handleEnroll = async () => {
  // Logic to call your API for adding student
  console.log("Enrolling Student:", studentForm.value);
  // Add to local list for visual feedback (Replace with real API call later)
  students.value.push({ ...studentForm.value, id: Date.now() });
  showStudentModal.value = false;
  // Reset form
  studentForm.value = { student_number: '', first_name: '', mi: '', last_name: '', email: '', phone: '', password: '' };
}

const fetchAllData = async () => {
  try {
    const id = route.params.id;
    const detailData = await sectionDetailsService.getSectionDetails(id);
    section.value = detailData;
    const dashData = await instructorDashboardService.getDashboard();
    sidebarSections.value = dashData.sections;
    
    // Ensure user data is loaded in store
    await userStore.ensureUserLoaded();
  } catch (error) {
    console.error("Failed to load data", error);
  }
}

watch(() => route.params.id, () => fetchAllData())
onMounted(fetchAllData)
</script>