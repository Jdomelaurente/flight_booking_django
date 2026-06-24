<template>
  <div class="p-8 max-w-7xl mx-auto font-sans bg-[#F9FAFB] min-h-screen">
    <!-- Header/Breadcrumbs and Top Actions -->
    <div class="mb-6 flex flex-col md:flex-row md:justify-between items-start md:items-center gap-4">
      <div>
        <div class="flex items-center gap-2 text-xs font-medium text-gray-400 mb-2">
          <router-link to="/instructor/dashboard" class="hover:text-pink-600 transition-colors">My Courses</router-link>
          <span class="text-gray-300">›</span>
          <span class="hover:text-pink-600 cursor-pointer transition-colors">CTHM</span>
          <span class="text-gray-300">›</span>
          <span class="text-pink-600 font-bold">Section {{ section?.section_code || 'N/A' }}</span>
        </div>
        <div class="flex items-center flex-wrap gap-3 mt-1">
          <h2 class="text-[22px] font-bold text-gray-800 tracking-tight">
            Course Section: {{ section?.section_name || 'N/A' }} — CTHM · {{ section?.section_code || 'N/A' }}
          </h2>
        </div>
      </div>
      <div class="flex flex-wrap gap-3">
        <input type="file" ref="fileInput" @change="handleCSVUpload" accept=".csv" class="hidden">
        
        <button @click="handleClearAll" class="flex items-center gap-2 border border-red-200 text-red-600 bg-red-50 px-4 py-2 rounded-lg font-bold text-xs shadow-sm hover:bg-red-100 transition-all">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Clear Section
        </button>
        <button @click="triggerFileUpload" class="flex items-center gap-2 border border-gray-200 text-gray-600 bg-white px-4 py-2 rounded-lg font-bold text-xs shadow-sm hover:bg-gray-50 transition-all">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          Import CSV
        </button>
        <button @click="openEnrollModal" class="flex items-center gap-2 bg-[#E91E63] hover:bg-[#D81B60] text-white px-4 py-2 rounded-lg font-bold text-xs shadow-sm transition-all shadow-[#E91E63]/20">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 4v16m8-8H4" />
          </svg>
          Enroll Student
        </button>
      </div>
    </div>

    <!-- Course Information Card -->
    <div class="bg-white border border-gray-100 rounded-xl p-6 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] mb-6 flex flex-wrap justify-between items-center gap-4">
      <div class="flex flex-wrap gap-12 sm:gap-16">
        <div>
          <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-1.5">Academic Year</p>
          <p class="text-[15px] font-bold text-gray-800">{{ section?.academic_year || 'N/A' }}</p>
        </div>
        <div>
          <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-1.5">Semester</p>
          <p class="text-[15px] font-bold text-gray-800">{{ section?.semester || 'N/A' }}</p>
        </div>
        <div>
          <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-1.5">Section</p>
          <p class="text-[15px] font-bold text-gray-800">{{ section?.section_code || 'N/A' }}</p>
        </div>
        <div>
          <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-1.5">Instructor</p>
          <p class="text-[15px] font-bold text-gray-800">{{ userStore.userFullName || 'Instructor' }}</p>
        </div>
      </div>
      <div>
        <span v-if="section?.is_active !== false" class="bg-[#E91E63] text-white px-5 py-1.5 rounded-lg text-xs font-bold shadow-sm inline-block tracking-wide">Active</span>
        <span v-else class="bg-red-500 text-white px-5 py-1.5 rounded-lg text-xs font-bold shadow-sm inline-block tracking-wide">Disabled</span>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex flex-col sm:flex-row justify-between sm:items-end border-b border-gray-200 mb-8 pb-0 gap-4">
      <div class="flex gap-8 px-2 overflow-x-auto">
        <button 
          @click="$router.push(`/instructor/section/${route.params.id}`)"
          class="pb-3 px-1 text-[13px] font-medium text-gray-400 hover:text-gray-600 tracking-wide transition-colors whitespace-nowrap"
        >
          Assessments
        </button>
        <button class="pb-3 px-1 text-[13px] font-bold border-b-[3px] border-[#E91E63] text-gray-900 tracking-wide whitespace-nowrap">
          Students
        </button>
        <button 
          @click="$router.push(`/instructor/section/${route.params.id}/settings`)"
          class="pb-3 px-1 text-[13px] font-medium text-gray-400 hover:text-gray-600 tracking-wide transition-colors whitespace-nowrap"
        >
          Settings
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="w-full">
      <!-- Students List Section -->
      <section>
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-4">
          <p class="text-[13px] text-gray-400 font-medium">
            Currently showing <strong>{{ filteredStudents.length }}</strong> enrolled students
          </p>
          
          <div class="relative w-full sm:w-72 shadow-sm rounded-lg">
            <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <svg class="w-4 h-4 text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"/>
              </svg>
            </div>
            <input 
              v-model="searchQuery" 
              type="text" 
              class="block w-full p-2.5 pl-10 text-sm text-gray-900 border border-gray-200 rounded-lg bg-white focus:ring-[#E91E63] focus:border-[#E91E63] transition-colors outline-none" 
              placeholder="Search by name, ID, or email..."
            >
          </div>
        </div>
        
        <div class="bg-white rounded-xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-gray-100 overflow-hidden">
          <table class="w-full text-left">
             <thead class="bg-gray-50/80 border-b border-gray-100">
               <tr>
                 <th class="px-6 py-4 text-[11px] font-bold text-gray-500 uppercase tracking-widest">Student Info</th>
                 <th class="px-6 py-4 text-[11px] font-bold text-gray-500 uppercase tracking-widest hidden md:table-cell">Student Number</th>
                 <th class="px-6 py-4 text-[11px] font-bold text-gray-500 uppercase tracking-widest hidden lg:table-cell">Enrolled Date</th>
                 <th class="px-6 py-4 text-[11px] font-bold text-gray-500 uppercase tracking-widest text-right">Actions</th>
               </tr>
             </thead>
             <tbody class="divide-y divide-gray-100">
               <tr v-for="student in paginatedStudents" :key="student.id" class="group hover:bg-gray-50 transition-colors">
                  <td class="px-6 py-4">
                    <div class="flex items-center gap-4">
                      <div class="w-10 h-10 bg-pink-50 rounded-xl flex items-center justify-center text-pink-500 font-bold text-sm border border-pink-100 shadow-sm shadow-pink-100/50 flex-shrink-0">
                        {{ student.first_name.charAt(0) }}
                      </div>
                      <div>
                        <p class="text-[15px] font-bold text-gray-800 capitalize leading-tight">{{ student.first_name }} {{ student.last_name }}</p>
                        <p class="text-[11px] text-gray-400 font-medium mt-0.5">{{ student.email || 'No email provided' }}</p>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 hidden md:table-cell">
                    <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-gray-100 text-gray-600">{{ student.student_number }}</span>
                  </td>
                  <td class="px-6 py-4 hidden lg:table-cell">
                    <span class="text-[13px] text-gray-500 font-medium">{{ student.enrolled_at || 'Just now' }}</span>
                  </td>
                  <td class="px-6 py-4 text-right">
                    <div class="flex items-center justify-end gap-2">
                       <button @click="removeStudent(student)" class="p-2 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all" title="Unenroll Student">
                         <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                         </svg>
                       </button>
                    </div>
                  </td>
               </tr>
               <tr v-if="filteredStudents.length === 0">
                 <td colspan="4" class="px-6 py-16 text-center">
                    <div class="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-gray-100 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.05)]">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                      </svg>
                    </div>
                    <h3 class="text-[17px] font-bold text-gray-800 mb-1">No students enrolled</h3>
                    <p class="text-[13px] text-gray-500 mb-6">Get started by enrolling students manually or importing a CSV file.</p>
                    <button @click="openEnrollModal" class="bg-[#E91E63] text-white px-6 py-2 rounded-lg font-bold text-sm shadow-sm hover:bg-[#D81B60] transition-colors inline-block">Enroll Student</button>
                 </td>
               </tr>
             </tbody>
          </table>
        </div>

        <!-- Pagination Controls -->
        <div v-if="totalPages > 1" class="flex items-center justify-between border border-gray-100 bg-white rounded-xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] px-6 py-4 mt-4">
          <p class="text-xs text-gray-500 font-medium tracking-wide">
            Showing <span class="font-bold text-gray-800">{{ (currentPage - 1) * pageSize + 1 }}</span> to <span class="font-bold text-gray-800">{{ Math.min(currentPage * pageSize, filteredStudents.length) }}</span> of <span class="font-bold text-gray-800">{{ filteredStudents.length }}</span> entries
          </p>
          <div class="flex items-center gap-1">
            <button 
              @click="currentPage > 1 && currentPage--" 
              :disabled="currentPage === 1"
              class="px-3 py-1.5 rounded-lg border border-gray-200 text-xs font-bold text-gray-600 disabled:opacity-50 hover:bg-gray-50 hover:text-[#E91E63] transition-all uppercase tracking-widest shadow-sm mr-1"
            >
              Prev
            </button>
            
            <!-- Page Numbers -->
            <button 
              v-for="page in totalPages" 
              :key="page"
              @click="currentPage = page"
              :class="[
                'w-8 h-8 flex items-center justify-center rounded-lg text-[13px] font-bold transition-all shadow-sm border',
                currentPage === page 
                  ? 'bg-[#E91E63] border-[#E91E63] text-white shadow-[#E91E63]/30' 
                  : 'bg-white border-gray-200 text-gray-600 hover:bg-[#FDF2F5] hover:text-[#E91E63] hover:border-[#F8BBD0]'
              ]"
            >
              {{ page }}
            </button>

            <button 
              @click="currentPage < totalPages && currentPage++" 
              :disabled="currentPage === totalPages"
              class="px-3 py-1.5 rounded-lg border border-gray-200 text-xs font-bold text-gray-600 disabled:opacity-50 hover:bg-gray-50 hover:text-[#E91E63] transition-all uppercase tracking-widest shadow-sm ml-1"
            >
              Next
            </button>
          </div>
        </div>
      </section>
    </div>

    <!-- Modals -->
    <!-- Enroll Student Modal -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center backdrop-blur-sm bg-black/50">
      <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="bg-white p-6 text-black flex justify-between items-center border-b border-gray-100">
          <h3 class="text-xl font-bold">Enroll Student</h3>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-gray-600 hover:rotate-90 transition-all">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-8">
          <div class="mb-6">
            <label class="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Enter Student Number</label>
            <input 
              v-model="studentNumberInput"
              type="text" 
              placeholder="e.g. 21-0001"
              class="w-full p-4 border-2 border-gray-100 rounded-xl focus:border-[#E91E63] outline-none transition-all text-lg font-medium"
            />
          </div>
          <div class="flex gap-4">
            <button @click="isModalOpen = false" class="flex-1 py-3 text-gray-400 font-bold hover:bg-gray-100 rounded-xl transition-colors uppercase text-xs">Cancel</button>
            <button @click="submitEnrollment" :disabled="loading" class="flex-1 py-3 bg-[#E91E63] text-white font-bold rounded-xl shadow-lg shadow-[#E91E63]/20 hover:bg-[#D81B60] transition-colors uppercase text-xs disabled:opacity-50">
              {{ loading ? 'Enrolling...' : 'Enroll Student' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Import Results Modal -->
    <div v-if="showResultModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4">
      <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="bg-white border-b border-gray-100 p-6 flex justify-between items-center">
          <h3 class="text-xl font-bold text-gray-800">Import Summary</h3>
          <button @click="showResultModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-8 space-y-5">
          <div v-if="importResults.enrolled_count > 0" class="flex items-center gap-4 p-4 bg-emerald-50 text-emerald-700 rounded-xl border border-emerald-100">
            <div class="flex-shrink-0 w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <p class="text-sm font-bold text-emerald-800">Enrollment Successful</p>
              <p class="text-xs text-emerald-600 mt-0.5">Successfully enrolled {{ importResults.enrolled_count }} students from CSV.</p>
            </div>
          </div>

          <div v-if="importResults.not_found?.length > 0" class="space-y-2">
            <p class="text-[11px] font-bold text-red-600 uppercase tracking-widest">Master List Rejections (Not Found)</p>
            <div class="bg-red-50 border border-red-100 rounded-xl p-4 max-h-40 overflow-y-auto">
              <ul class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                <li v-for="id in importResults.not_found" :key="id" class="text-[11px] font-mono font-medium text-red-700 bg-white px-2 py-1.5 rounded-md border border-red-100 shadow-sm text-center">{{ id }}</li>
              </ul>
            </div>
          </div>

          <div v-if="importResults.already_enrolled?.length > 0" class="space-y-2">
            <p class="text-[11px] font-bold text-amber-600 uppercase tracking-widest">Already Enrolled (Skipped)</p>
            <div class="bg-amber-50 border border-amber-100 rounded-xl p-4 max-h-32 overflow-y-auto">
              <ul class="space-y-2">
                <li v-for="item in importResults.already_enrolled" :key="item.id" class="text-[11px] text-amber-800 font-medium">
                  <span class="font-bold border bg-white px-1.5 py-0.5 rounded mr-1">{{ item.id }}</span> already in <span class="font-bold ml-1">{{ item.section }}</span>
                </li>
              </ul>
            </div>
          </div>

          <button @click="showResultModal = false" class="w-full mt-4 py-3.5 bg-gray-100 text-gray-600 font-bold rounded-xl hover:bg-gray-200 transition-colors text-xs uppercase tracking-widest">Close Summary</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api/axios'
import { sectionDetailsService } from '@/services/instructor/sectionDetailsService'
import { sectionPeopleListService } from '@/services/instructor/sectionPeopleListService'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'
import { useModalStore } from '@/stores/modal'

const props = defineProps({
  sections: Array
})

const route = useRoute()
const userStore = useUserStore()
const notificationStore = useNotificationStore()
const modalStore = useModalStore()

const section = ref(null)
const enrolledStudents = ref([])
const isModalOpen = ref(false)
const studentNumberInput = ref('')
const loading = ref(false)
const fileInput = ref(null)
const showResultModal = ref(false)
const importResults = ref({ enrolled_count: 0, not_found: [], already_enrolled: [] })

// Pagination & Search State
const currentPage = ref(1)
const pageSize = ref(30)
const searchQuery = ref('')

const filteredStudents = computed(() => {
  if (!searchQuery.value) return enrolledStudents.value;
  const q = searchQuery.value.toLowerCase().trim();
  return enrolledStudents.value.filter(s => 
    s.first_name?.toLowerCase().includes(q) || 
    s.last_name?.toLowerCase().includes(q) || 
    s.student_number?.toLowerCase().includes(q) ||
    s.email?.toLowerCase().includes(q)
  );
})

watch(searchQuery, () => {
  currentPage.value = 1
})

const paginatedStudents = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredStudents.value.slice(start, end)
})

const totalPages = computed(() => {
  if (filteredStudents.value.length === 0) return 1
  return Math.ceil(filteredStudents.value.length / pageSize.value)
})

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
    const response = await api.post(`api/instructor/sections/${sectionId}/enroll/`, 
      { student_number: studentNumberInput.value }
    )
    notificationStore.success(response.data.message)
    isModalOpen.value = false
    await fetchStudentData()
  } catch (error) {
    notificationStore.error(error.response?.data?.error || "Failed to enroll student")
  } finally {
    loading.value = false
  }
}

const removeStudent = async (student) => {
  const confirmed = await modalStore.confirm({
    title: 'Unenroll Student',
    message: `Are you sure you want to unenroll ${student.first_name} ${student.last_name}?`,
    confirmText: 'Unenroll Student',
    cancelText: 'Cancel',
    danger: true
  })
  if (!confirmed) return
  
  loading.value = true
  try {
    const sectionId = route.params.id
    await sectionPeopleListService.unenrollStudent(sectionId, student.id)
    notificationStore.success("Student successfully unenrolled.")
    await fetchStudentData()
  } catch (error) {
    notificationStore.error(error.response?.data?.error || "Failed to unenroll student")
  } finally {
    loading.value = false
  }
}

const triggerFileUpload = () => { fileInput.value.click() }

const handleCSVUpload = async (event) => {
  const file = event.target.files[0]
  if (!file || !file.name.endsWith('.csv')) {
    notificationStore.error("Please upload a valid .csv file")
    return
  }
  loading.value = true
  try {
    const sectionId = route.params.id
    const response = await sectionPeopleListService.bulkEnrollStudents(sectionId, file)
    importResults.value = response
    showResultModal.value = true
    await fetchStudentData()
  } catch (error) {
    notificationStore.error("Failed to process bulk enrollment")
  } finally {
    loading.value = false
    event.target.value = ''
  }
}

const handleClearAll = async () => {
  if (enrolledStudents.value.length === 0) return
  const confirmed = await modalStore.confirm({
    title: 'Wipe Section Roster',
    message: 'Are you sure you want to unenroll EVERY student in this section?',
    confirmText: 'Wipe Everything',
    cancelText: 'Cancel',
    danger: true
  })
  if (!confirmed) return
  loading.value = true
  try {
    const sectionId = route.params.id
    await sectionPeopleListService.clearEnrolledStudents(sectionId)
    notificationStore.success("Section roster cleared.")
    await fetchStudentData()
  } catch (error) {
    notificationStore.error("Failed to clear section")
  } finally {
    loading.value = false
  }
}

const fetchStudentData = async () => {
  try {
    const id = route.params.id
    section.value = await sectionDetailsService.getSectionDetails(id)
    enrolledStudents.value = await sectionPeopleListService.getEnrolledStudents(id)
  } catch (error) {
    console.error("Failed to load students", error)
  }
}

watch(() => route.params.id, fetchStudentData)
onMounted(fetchStudentData)
</script>