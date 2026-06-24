<template>
  <div class="instructor-reports p-8">
    <div class="mb-8">
      <h1 class="text-3xl font-black text-gray-900 uppercase tracking-tight">Reports</h1>
      <p class="text-xs text-gray-400 font-bold uppercase tracking-widest mt-1">Aggregated statistics across your sections</p>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <!-- Total Sections -->
      <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex items-center gap-6">
        <div class="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center text-blue-500 border border-blue-100">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <div>
          <p class="text-[10px] font-black uppercase tracking-widest text-gray-400">Total Sections</p>
          <p class="text-3xl font-black text-gray-900">{{ sectionsCount }}</p>
        </div>
      </div>

      <!-- Total Students -->
      <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex items-center gap-6">
        <div class="w-14 h-14 bg-[#FF579A]/10 rounded-2xl flex items-center justify-center text-[#FF579A] border border-[#FF579A]/20">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
        <div>
          <p class="text-[10px] font-black uppercase tracking-widest text-gray-400">Total Students</p>
          <p class="text-3xl font-black text-gray-900">{{ totalStudentsCount }}</p>
        </div>
      </div>

      <!-- Total Activities -->
      <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex items-center gap-6">
        <div class="w-14 h-14 bg-green-50 rounded-2xl flex items-center justify-center text-green-500 border border-green-100">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
        </div>
        <div>
          <p class="text-[10px] font-black uppercase tracking-widest text-gray-400">Activities</p>
          <p class="text-3xl font-black text-gray-900">{{ activitiesCount }}</p>
        </div>
      </div>
      
      <!-- Avg class performance -->
      <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex items-center gap-6">
        <div class="w-14 h-14 bg-amber-50 rounded-2xl flex items-center justify-center text-amber-500 border border-amber-100">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        </div>
        <div>
          <p class="text-[10px] font-black uppercase tracking-widest text-gray-400">Submissions</p>
          <p class="text-3xl font-black text-gray-900">{{ totalSubmissions }}</p>
        </div>
      </div>
    </div>

    <!-- Detailed Section Breakdown -->
    <div class="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden mb-8">
      <div class="px-6 py-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
        <h3 class="text-sm font-black uppercase tracking-widest text-gray-900">Section Performance Breakdown</h3>
        <button @click="fetchReportData" class="text-[10px] font-bold text-[#FF579A] uppercase tracking-widest hover:bg-pink-50 px-3 py-1.5 rounded transition-colors flex items-center gap-2">
          <svg v-if="loading" class="animate-spin h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Refresh Data
        </button>
      </div>
      
      <div v-if="loading" class="p-20 text-center">
        <div class="inline-block w-8 h-8 border-4 border-[#FF579A] border-t-transparent rounded-full animate-spin mb-4"></div>
        <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Compiling reports...</p>
      </div>
      
      <div v-else-if="sectionReports.length === 0" class="p-20 text-center">
        <p class="text-gray-400 text-sm italic">No section data available to report.</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead class="bg-white border-b border-gray-100">
            <tr>
              <th class="px-6 py-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">Section</th>
              <th class="px-6 py-4 text-[10px] font-black text-gray-400 uppercase tracking-widest text-center">Total Enrolled</th>
              <th class="px-6 py-4 text-[10px] font-black text-gray-400 uppercase tracking-widest text-center">Activities</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="section in sectionReports" :key="section.id" class="hover:bg-gray-50/50 transition-colors">
              <td class="px-6 py-4">
                <div class="font-bold text-sm text-gray-900 border-l-2 border-[#FF579A] pl-3">{{ section.name }}</div>
                <div class="text-[10px] font-semibold text-gray-400 uppercase tracking-widest pl-3">{{ section.code }}</div>
              </td>
              <td class="px-6 py-4 text-center">
                <span class="bg-blue-50 text-blue-600 px-3 py-1 rounded-md text-xs font-bold">{{ section.enrolled }}</span>
              </td>
              <td class="px-6 py-4 text-center">
                <span class="bg-green-50 text-green-600 px-3 py-1 rounded-md text-xs font-bold">{{ section.activities }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { sectionPeopleListService } from '@/services/instructor/sectionPeopleListService'
import { useNotificationStore } from '@/stores/notification'
import { activityDetailsService } from '@/services/instructor/activityDetailsService'

const notificationStore = useNotificationStore()
const loading = ref(true)

// Stats
const sectionsCount = ref(0)
const activitiesCount = ref(0)
const totalStudentsCount = ref(0)
const totalSubmissions = ref(0)

const sectionReports = ref([])

onMounted(async () => {
  await fetchReportData()
})

const fetchReportData = async () => {
  loading.value = true
  try {
    const data = await instructorDashboardService.getDashboard()
    const sections = data.sections || []
    
    sectionsCount.value = sections.length
    
    // Calculate aggregate data
    let acts = 0;
    let enrolledSum = 0;
    let submissionsSum = 0;
    
    const reports = []
    
    const detailsPromises = sections.map(async (section) => {
      // Activity count is already provided from getDashboard
      const actCount = section.activity_count || 0;
      acts += actCount;
      
      let enrolled = 0;
      try {
        const studentData = await sectionPeopleListService.getEnrolledStudents(section.id)
        enrolled = Array.isArray(studentData) ? studentData.length : 0
        enrolledSum += enrolled
        
        // Note: For a true dashboard, fetching submissions for every activity across all sections
        // is expensive. Leaving it 0 unless a specific endpoint is constructed.
      } catch(e) {}
      
      reports.push({
        id: section.id,
        name: section.section_name,
        code: section.section_code,
        enrolled: enrolled,
        activities: actCount
      })
    })

    await Promise.all(detailsPromises)
    
    activitiesCount.value = acts
    totalStudentsCount.value = enrolledSum
    totalSubmissions.value = submissionsSum
    sectionReports.value = reports

  } catch (error) {
    console.error('Error fetching report data:', error)
    notificationStore.error('Failed to load reports')
  } finally {
    loading.value = false
  }
}
</script>
