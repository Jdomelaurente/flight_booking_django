<template>
  <div class="instructor-section-list p-8">
    <div class="mb-8">
      <h1 class="text-3xl font-black text-gray-900 uppercase tracking-tight">Sections</h1>
      <p class="text-xs text-gray-400 font-bold uppercase tracking-widest mt-1">Manage your enrolled sections</p>
    </div>

    <div v-if="loading" class="animate-pulse space-y-4">
      <div v-for="i in 3" :key="i" class="h-24 bg-gray-100 rounded-xl"></div>
    </div>
    
    <div v-else-if="sections.length === 0" class="text-center py-20 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
      <p class="text-gray-400 text-sm italic">No sections available.</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="section in sections" 
        :key="section.id"
        class="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-[#FF579A]/30 transition-all cursor-pointer group"
        @click="goToSection(section.id)"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="w-12 h-12 bg-pink-100 rounded-xl text-pink-600 flex items-center justify-center font-black text-xl group-hover:bg-[#FF579A] group-hover:text-white transition-colors">
            {{ section.section_name.charAt(0).toUpperCase() }}
          </div>
          <span v-if="section.is_active" class="px-2 py-1 bg-green-50 text-green-600 text-[10px] font-black uppercase tracking-widest rounded">Active</span>
          <span v-else class="px-2 py-1 bg-gray-100 text-gray-500 text-[10px] font-black uppercase tracking-widest rounded">Inactive</span>
        </div>
        
        <h3 class="text-lg font-black text-gray-900 leading-tight mb-1 group-hover:text-[#FF579A] transition-colors">{{ section.section_name }}</h3>
        <p class="text-[11px] font-semibold text-gray-400 uppercase tracking-widest mb-4">{{ section.section_code }} • {{ section.academic_year }}</p>
        
        <div class="flex justify-between items-center text-xs text-gray-500 font-medium border-t border-gray-50 pt-4 mt-4">
          <span class="flex items-center gap-1.5 focus:outline-none">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            {{ section.enrolled_count || 0 }} Enrolled
          </span>
          <span class="bg-gray-100 font-bold px-2 py-1 rounded text-[10px] uppercase text-gray-600">{{ section.semester }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { useNotificationStore } from '@/stores/notification'

const router = useRouter()
const notificationStore = useNotificationStore()
const loading = ref(true)
const sections = ref([])

onMounted(async () => {
  try {
    const data = await instructorDashboardService.getDashboard()
    sections.value = data.sections || []
  } catch (error) {
    console.error('Error fetching sections:', error)
    notificationStore.error('Failed to load sections')
  } finally {
    loading.value = false
  }
})

const goToSection = (id) => {
  router.push(`/instructor/section/${id}`)
}
</script>
