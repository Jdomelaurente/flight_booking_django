<template>
  <div class="instructor-activities-list p-8">
    <div class="mb-8">
      <h1 class="text-3xl font-black text-gray-900 uppercase tracking-tight">Activities</h1>
      <p class="text-xs text-gray-400 font-bold uppercase tracking-widest mt-1">Manage all your activities</p>
    </div>

    <!-- Filters/Search -->
    <div class="mb-6 flex gap-4 print:hidden">
      <div class="relative w-full md:w-80">
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </span>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search activities..." 
          class="w-full bg-white border border-gray-200 rounded-xl py-2.5 pl-10 pr-4 text-xs font-medium focus:ring-2 focus:ring-[#FF579A] outline-none transition-all"
        >
      </div>
    </div>

    <div v-if="loading" class="animate-pulse space-y-4">
      <div v-for="i in 3" :key="i" class="h-24 bg-gray-100 rounded-xl"></div>
    </div>
    
    <div v-else-if="filteredActivities.length === 0" class="text-center py-20 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
      <p class="text-gray-400 text-sm italic">No activities found.</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="activity in paginatedActivities" 
        :key="activity.id"
        class="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-[#FF579A]/30 transition-all cursor-pointer group"
        @click="goToActivity(activity.id)"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-2">
            <span :class="[
              'px-2 py-1 text-[9px] font-black uppercase tracking-widest rounded',
              activity.is_code_active ? 'bg-green-50 text-green-600' : 'bg-yellow-50 text-yellow-600'
            ]">
              {{ activity.is_code_active ? 'Active' : 'Draft' }}
            </span>
          </div>
          <span v-if="activity.activity_code" class="text-xs font-mono font-bold text-gray-500 bg-gray-50 p-1 rounded">{{ activity.activity_code }}</span>
        </div>
        
        <h3 class="text-lg font-black text-gray-900 leading-tight mb-2 group-hover:text-[#FF579A] transition-colors truncate">{{ activity.title }}</h3>
        
        <div class="bg-gray-50 rounded-lg p-3 mb-4 border border-gray-100">
          <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Section</p>
          <p class="text-xs font-semibold text-gray-800">{{ getSectionName(activity.section_id) || 'Unknown Section' }}</p>
        </div>
        
        <div class="flex justify-between items-center text-[10px] font-black uppercase tracking-widest text-gray-400 border-t border-gray-50 pt-4 mt-4">
          <span>{{ activity.required_trip_type.replace('_', ' ') }}</span>
          <span>Due: {{ formatDate(activity.due_date) }}</span>
        </div>
      </div>
    </div>

    <!-- Pagination Controls -->
    <div v-if="filteredActivities.length > pageSize" class="flex items-center justify-between mt-8 print:hidden">
      <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
        Showing {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredActivities.length) }} of {{ filteredActivities.length }}
      </span>
      <div class="flex items-center gap-2">
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="p-2 rounded-lg border border-gray-100 hover:bg-gray-50 disabled:opacity-20 transition-all"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="p-2 rounded-lg border border-gray-100 hover:bg-gray-50 disabled:opacity-20 transition-all"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { sectionDetailsService } from '@/services/instructor/sectionDetailsService'
import { useNotificationStore } from '@/stores/notification'

const router = useRouter()
const notificationStore = useNotificationStore()
const loading = ref(true)
const allActivities = ref([])
const sectionsList = ref([])

const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(12)

onMounted(async () => {
  try {
    const data = await instructorDashboardService.getDashboard()
    sectionsList.value = data.sections || []
    
    // Fetch details for each section to get the activities
    const activitiesPromises = sectionsList.value.map(async (section) => {
      try {
        const details = await sectionDetailsService.getSectionDetails(section.id)
        if (details.activities && details.activities.length > 0) {
          return details.activities.map(act => ({
            ...act,
            section_id: section.id,
            section_name: section.section_name
          }))
        }
      } catch (err) {
        console.error(`Failed to fetch activities for section ${section.id}`, err)
      }
      return []
    })

    let activities = []
    const results = await Promise.all(activitiesPromises)
    results.forEach(actBatch => {
      activities = [...activities, ...actBatch]
    })

    // Sort by created date or due date
    allActivities.value = activities.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
  } catch (error) {
    console.error('Error fetching activities:', error)
    notificationStore.error('Failed to load activities')
  } finally {
    loading.value = false
  }
})

const filteredActivities = computed(() => {
  if (!searchQuery.value) return allActivities.value
  const q = searchQuery.value.toLowerCase()
  return allActivities.value.filter(a => 
    a.title.toLowerCase().includes(q) || 
    (a.activity_code && a.activity_code.toLowerCase().includes(q)) ||
    (a.section_name && a.section_name.toLowerCase().includes(q))
  )
})

const paginatedActivities = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredActivities.value.slice(start, start + pageSize.value)
})

const totalPages = computed(() => Math.ceil(filteredActivities.value.length / pageSize.value))

watch(searchQuery, () => {
  currentPage.value = 1
})

const getSectionName = (id) => {
  const section = sectionsList.value.find(s => s.id === id)
  return section ? section.section_name : ''
}

const formatDate = (dateString) => {
  if (!dateString) return 'No due date'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  } catch {
    return dateString
  }
}

const goToActivity = (id) => {
  router.push(`/instructor/activity/${id}`)
}
</script>
