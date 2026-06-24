<template>
  <div class="instructor-students-list p-8">
    <div class="mb-8">
      <h1 class="text-3xl font-black text-gray-900 uppercase tracking-tight">Students</h1>
      <p class="text-xs text-gray-400 font-bold uppercase tracking-widest mt-1">Directory of enrolled students</p>
    </div>

    <!-- Filter Bar -->
    <div class="bg-white border border-gray-100 rounded-2xl p-4 mb-6 shadow-sm flex flex-col md:flex-row gap-4 items-center">
      <div class="flex-1 w-full">
        <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1.5 ml-1">Filter by Section</label>
        <select 
          v-model="selectedSectionId" 
          class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-xs font-bold focus:ring-2 focus:ring-[#FF579A] focus:border-transparent outline-none transition-all"
        >
          <option value="">All Sections</option>
          <option v-for="section in sectionsList" :key="section.id" :value="section.id">
            {{ section.section_name }} ({{ section.section_code }})
          </option>
        </select>
      </div>
      
      <div class="flex-1 w-full">
        <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1.5 ml-1">Search Student</label>
        <div class="relative">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </span>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Name or ID..." 
            class="w-full bg-gray-50 border border-gray-200 rounded-xl py-2.5 pl-10 pr-4 text-xs font-medium focus:ring-2 focus:ring-[#FF579A] outline-none transition-all"
            @keyup.enter="applyFilters"
          >
        </div>
      </div>
      
      <div class="flex items-end h-full">
        <button 
          @click="applyFilters"
          class="w-full md:w-auto mt-5 px-6 py-2.5 bg-slate-900 text-white rounded-xl font-bold text-xs uppercase tracking-widest hover:bg-black transition-all shadow-md active:scale-95 flex items-center justify-center h-[42px]"
        >
          <span v-if="loading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></span>
          Filter Results
        </button>
      </div>
    </div>

    <!-- Students Table -->
    <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      <div v-if="loading && appliedStudents.length === 0" class="p-20 text-center">
        <div class="inline-block w-8 h-8 border-4 border-[#FF579A] border-t-transparent rounded-full animate-spin mb-4"></div>
        <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Loading directory...</p>
      </div>
      
      <div v-else-if="appliedStudents.length === 0" class="p-20 text-center bg-gray-50/50">
        <p class="text-gray-400 text-sm italic mb-2">No students match the current filters.</p>
        <button @click="resetFilters" class="text-[10px] font-bold text-[#FF579A] hover:underline uppercase tracking-widest">Clear filters</button>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="px-6 py-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">Student Info</th>
              <th class="px-6 py-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">Student Number</th>
              <th class="px-6 py-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">Section</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="student in paginatedStudents" :key="student.id + '-' + student.section_id" class="hover:bg-gray-50/50 transition-colors">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 bg-pink-50 text-pink-600 rounded-full flex items-center justify-center font-bold text-xs">
                    {{ student.first_name?.charAt(0) || '-' }}{{ student.last_name?.charAt(0) || '-' }}
                  </div>
                  <div>
                    <h3 class="font-bold text-sm text-gray-900">{{ student.first_name }} {{ student.last_name }}</h3>
                    <p class="text-[10px] text-gray-400">{{ student.email || 'No email provided' }}</p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="px-2.5 py-1 bg-gray-100 text-gray-600 text-[10px] font-bold uppercase tracking-widest rounded-md font-mono">
                  {{ student.student_number }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span class="text-xs font-semibold text-gray-700 bg-gray-50 px-2.5 py-1 rounded border border-gray-100 uppercase">
                  {{ student.section_name || 'N/A' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination Controls -->
    <div v-if="appliedStudents.length > pageSize" class="flex flex-col md:flex-row items-center justify-between mt-6 px-2 gap-4">
      <div class="flex items-center gap-4">
        <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Rows per page:</span>
        <select v-model="pageSize" @change="currentPage = 1" class="bg-white border border-gray-200 rounded-lg px-2 py-1.5 text-[10px] font-black outline-none focus:ring-2 focus:ring-[#FF579A] transition-all cursor-pointer">
          <option :value="15">15</option>
          <option :value="30">30</option>
          <option :value="50">50</option>
        </select>
        <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
          Showing {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, appliedStudents.length) }} of {{ appliedStudents.length }}
        </span>
      </div>
      
      <div class="flex items-center gap-2">
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="p-2.5 rounded-xl border border-gray-100 hover:bg-gray-50 disabled:opacity-20 disabled:hover:bg-transparent transition-all group"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-600 group-hover:text-[#FF579A]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        
        <div class="flex items-center gap-1.5">
          <button 
            v-for="page in totalPages" 
            :key="page"
            @click="currentPage = page"
            :class="[
              'w-9 h-9 rounded-xl text-[10px] font-black transition-all flex items-center justify-center border',
              currentPage === page ? 'bg-[#FF579A] text-white border-[#FF579A] shadow-lg shadow-pink-200' : 'text-gray-400 border-transparent hover:bg-gray-50 hover:border-gray-100'
            ]"
          >
            {{ page }}
          </button>
        </div>
        
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="p-2.5 rounded-xl border border-gray-100 hover:bg-gray-50 disabled:opacity-20 disabled:hover:bg-transparent transition-all group"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-600 group-hover:text-[#FF579A]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { sectionPeopleListService } from '@/services/instructor/sectionPeopleListService'
import { useNotificationStore } from '@/stores/notification'

const notificationStore = useNotificationStore()

const loading = ref(true)
const sectionsList = ref([])
const allStudentsUnfiltered = ref([])
const appliedStudents = ref([]) // Holds the filtered results after clicking "Filter Results"

// Filter states
const selectedSectionId = ref('')
const searchQuery = ref('')

// Pagination
const currentPage = ref(1)
const pageSize = ref(15)

onMounted(async () => {
  await fetchInitialData()
})

const fetchInitialData = async () => {
  loading.value = true
  try {
    const data = await instructorDashboardService.getDashboard()
    sectionsList.value = data.sections || []
    
    // To get all students, we fetch students for all active sections
    // This could be combined in a new backend endpoint, but for now we'll fetch them per section
    let combinedStudents = []
    
    // Fetch in parallel for better performance
    const fetchPromises = sectionsList.value.map(async (section) => {
      try {
        const studentData = await sectionPeopleListService.getEnrolledStudents(section.id)
        if (Array.isArray(studentData)) {
          return studentData.map(s => ({
            ...s,
            section_id: section.id,
            section_name: section.section_name
          }))
        }
      } catch (err) {
        console.error(`Failed to fetch students for section ${section.id}`, err)
      }
      return []
    })
    
    const results = await Promise.all(fetchPromises)
    results.forEach(studentBatch => {
      combinedStudents = [...combinedStudents, ...studentBatch]
    })
    
    // Deduplicate if a student is in multiple sections, though maybe we want to see them in both
    // We'll keep them to show the section they belong to
    
    allStudentsUnfiltered.value = combinedStudents
    appliedStudents.value = [...combinedStudents]
  } catch (error) {
    console.error('Error fetching data:', error)
    notificationStore.error('Failed to load students data')
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  loading.value = true
  setTimeout(() => { // Small timeout for UI feedback
    let filtered = [...allStudentsUnfiltered.value]
    
    if (selectedSectionId.value) {
      filtered = filtered.filter(s => s.section_id === selectedSectionId.value)
    }
    
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      filtered = filtered.filter(s => 
        (s.first_name && s.first_name.toLowerCase().includes(q)) ||
        (s.last_name && s.last_name.toLowerCase().includes(q)) ||
        (s.student_number && s.student_number.toLowerCase().includes(q))
      )
    }
    
    appliedStudents.value = filtered
    currentPage.value = 1
    loading.value = false
  }, 300)
}

const resetFilters = () => {
  selectedSectionId.value = ''
  searchQuery.value = ''
  applyFilters()
}

const paginatedStudents = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return appliedStudents.value.slice(start, start + pageSize.value)
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(appliedStudents.value.length / pageSize.value))
})
</script>
