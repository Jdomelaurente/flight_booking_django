<template>
  <div class="p-4 lg:p-8 max-w-7xl mx-auto">
    <LoadingOverlay :loading="isLoading" />
    <div class="flex-1 overflow-auto">
        <div class="p-4 lg:p-8 max-w-7xl mx-auto">
          <!-- Title Section -->
          <div class="mb-8">
            <h2 class="text-2xl font-bold text-slate-800 tracking-tight">Instructor Activity Logs</h2>
            <div class="flex items-center gap-2 text-sm text-slate-500 mt-1">
              <span>Main Console</span>
              <span class="text-slate-300">•</span>
              <span class="text-pink-500 font-medium">Audit Trail</span>
            </div>
          </div>

          <!-- Logs Table -->
          <div class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
            <div class="overflow-x-auto">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="bg-slate-50/50 border-b border-slate-100">
                    <th class="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Timestamp</th>
                    <th class="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Action</th>
                    <th class="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">User Involved</th>
                    <th class="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Details</th>
                    <th class="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Location/Device</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-50">
                  <tr v-for="log in logs" :key="log.id" class="hover:bg-slate-50/50 transition-colors">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-[11px] font-bold text-slate-700">{{ formatDate(log.timestamp) }}</div>
                      <div class="text-[10px] text-slate-400">{{ formatTime(log.timestamp) }}</div>
                    </td>
                    <td class="px-6 py-4">
                      <span :class="getActionClass(log.action_type)" class="px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-widest border">
                        {{ log.action_type.replace('_', ' ') }}
                      </span>
                    </td>
                    <td class="px-6 py-4">
                      <div class="flex items-center gap-3">
                        <div class="w-7 h-7 bg-slate-100 rounded-full flex items-center justify-center text-[10px] font-bold text-slate-500 border border-slate-200">
                          {{ log.actor_role === 'student' ? '🎓' : '👨‍🏫' }}
                        </div>
                        <div>
                          <div class="text-[11px] font-bold text-slate-800">{{ log.actor_name }}</div>
                          <div class="text-[9px] text-slate-400 uppercase tracking-tighter">{{ log.actor_role }}</div>
                          <div v-if="log.student_number" class="text-[9px] font-bold text-pink-500">ID: {{ log.student_number }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4">
                      <div class="text-[11px] text-slate-600 max-w-md">
                        {{ log.details }}
                        <div v-if="log.section_name" class="mt-1">
                          <span class="text-[9px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded border border-slate-200 font-bold uppercase">{{ log.section_name }}</span>
                          <span v-if="log.activity_name" class="ml-1 text-[9px] bg-indigo-50 text-indigo-500 px-1.5 py-0.5 rounded border border-indigo-100 font-bold uppercase">{{ log.activity_name }}</span>
                        </div>
                        <div v-if="log.login_time || log.logout_time" class="mt-1 flex gap-2">
                           <span v-if="log.login_time" class="text-[9px] text-emerald-600 font-bold">In: {{ formatTime(log.login_time) }}</span>
                           <span v-if="log.logout_time" class="text-[9px] text-red-500 font-bold">Out: {{ formatTime(log.logout_time) }}</span>
                        </div>
                        <div v-if="log.is_csv" class="mt-1">
                          <span class="text-[9px] bg-amber-50 text-amber-600 px-1.5 py-0.5 rounded border border-amber-100 font-black uppercase tracking-tighter italic">Imported via CSV/Excel</span>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-[10px] font-medium text-slate-500 flex items-center gap-1.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        <span class="truncate max-w-[150px]" :title="log.device">{{ log.device }}</span>
                      </div>
                      <div class="text-[9px] font-bold text-slate-400 tracking-widest mt-0.5">{{ log.ip_address }}</div>
                    </td>
                  </tr>
                  <tr v-if="logs.length === 0 && !isLoading">
                    <td colspan="5" class="px-6 py-20 text-center">
                      <div class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-100">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <p class="text-sm font-bold text-slate-400 uppercase tracking-widest">No activity logs recorded yet</p>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import CTHM from '@/assets/image/cthm-logos.png'
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import LoadingOverlay from '@/components/instructor/LoadingOverlay.vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const isLoading = ref(false)
const logs = ref([])
const sections = ref([])

const fetchLogs = async () => {
  isLoading.value = true
  try {
    const [logsData, dashData] = await Promise.all([
      instructorDashboardService.getLogs(),
      instructorDashboardService.getDashboard()
    ])
    logs.value = logsData
    sections.value = dashData.sections
  } catch (error) {
    console.error('Failed to fetch logs:', error)
  } finally {
    isLoading.value = false
  }
}

const goToSection = (id) => {
  router.push(`/instructor/section/${id}`)
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const formatTime = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
}

const getActionClass = (type) => {
  switch (type) {
    case 'LOGIN': return 'bg-emerald-50 text-emerald-600 border-emerald-100'
    case 'LOGOUT': return 'bg-slate-100 text-slate-500 border-slate-200'
    case 'SECTION_CREATED': return 'bg-blue-50 text-blue-600 border-blue-100'
    case 'SECTION_DELETED': return 'bg-red-50 text-red-600 border-red-100'
    case 'ACTIVITY_CREATED': return 'bg-indigo-50 text-indigo-600 border-indigo-100'
    case 'ACTIVITY_DELETED': return 'bg-rose-50 text-rose-600 border-rose-100'
    case 'STUDENT_ENROLLED': return 'bg-pink-50 text-pink-600 border-pink-100'
    case 'STUDENT_UNENROLLED': return 'bg-orange-50 text-orange-600 border-orange-100'
    case 'ACTIVITY_TAKEN': return 'bg-amber-50 text-amber-600 border-amber-100'
    case 'GRADES_RELEASED': return 'bg-violet-50 text-violet-600 border-violet-100'
    case 'REPORT_PRINTED': return 'bg-cyan-50 text-cyan-600 border-cyan-100'
    default: return 'bg-gray-50 text-gray-500 border-gray-100'
  }
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
/* Optional styling */
</style>
