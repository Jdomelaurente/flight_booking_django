<template>
  <div class="p-8 max-w-7xl mx-auto">
    <div class="max-w-6xl mx-auto">
            
            <div class="flex justify-between items-center mb-6">
              <button @click="router.back()" class="flex items-center text-gray-500 hover:text-black font-bold text-sm uppercase">
                <span class="mr-2">←</span> BACK
              </button>
              <div class="flex gap-6 text-[11px] font-bold uppercase tracking-widest font-sans">
                <span 
                  @click="router.push(`/instructor/activity/${activityId}`)"
                  class="text-gray-400 cursor-pointer hover:text-gray-600"
                >
                  Instruction/s
                </span>
                <span 
                  @click="router.push(`/instructor/activity/${activityId}?tab=submissions`)"
                  class="text-gray-400 cursor-pointer hover:text-gray-600"
                >
                  Student work
                </span>
                <span 
                  class="text-green-700 border-b-2 border-green-700 pb-1"
                >
                  Overview (Top List)
                </span>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-10">
              <div v-if="loading" class="animate-pulse flex flex-col gap-6">
                <div class="h-8 bg-gray-200 w-1/4 rounded"></div>
                <div class="h-64 bg-gray-100 w-full rounded-xl"></div>
              </div>

              <div v-else>
                <div class="flex justify-between items-end mb-8 border-b border-gray-50 pb-6">
                  <div>
                    <h2 class="text-3xl font-black text-gray-900 uppercase tracking-tight">{{ activity?.title }}</h2>
                    <p class="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1">Class Performance Rankings</p>
                  </div>
                  <div class="text-right">
                    <p class="text-[10px] font-black text-pink-500 uppercase tracking-widest">Total Points</p>
                    <p class="text-2xl font-black text-slate-800">{{ activity?.total_points || 100 }}</p>
                  </div>
                </div>

                <!-- Top 5 Leaderboard Highlights (Left Aligned) -->
                <div v-if="topStudents.length > 0" class="gap-4 mb-8 mt-6" style="display:grid; grid-template-columns: repeat(5, 1fr);">
                  <div v-for="(student, idx) in topStudents.slice(0, 5)" :key="student.student_id" 
                    class="flex items-center gap-3 px-4 py-2.5 rounded-2xl border bg-white transition-all shadow-sm hover:shadow-md w-full"
                    :class="[
                      idx === 0 ? 'border-amber-200 bg-amber-50/20 shadow-amber-100/20' : 
                      idx === 1 ? 'border-slate-200 bg-gray-50/10' : 
                      'border-gray-100 hover:border-gray-200'
                    ]"
                  >
                    <div class="relative shrink-0">
                      <div :class="[
                        'w-10 h-10 rounded-full flex items-center justify-center text-lg shadow-inner border border-black/5',
                        idx === 0 ? 'bg-amber-400 text-white' : idx === 1 ? 'bg-slate-300 text-white' : idx === 2 ? 'bg-orange-300 text-white' : 'bg-gray-100 text-gray-500'
                      ]">
                        {{ idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : (idx + 1) }}
                      </div>
                      <div v-if="idx === 0" class="absolute -top-1.5 -right-1.5 text-[10px] drop-shadow-sm">👑</div>
                    </div>
                    <div class="truncate">
                      <p class="text-[8px] font-black uppercase tracking-widest leading-none mb-1" :class="idx === 0 ? 'text-amber-600' : 'text-gray-400'">{{ getRankWithSuffix(idx + 1) }} Place</p>
                      <h4 class="text-xs font-bold text-gray-900 leading-tight truncate">{{ student.first_name }} {{ student.last_name }}</h4>
                      <p class="text-[11px] font-black mt-0.5" :class="idx === 0 ? 'text-amber-700' : 'text-gray-600'">{{ getPercentage(student) }}%</p>
                    </div>
                  </div>
                </div>

                <!-- Quick Insights Bar -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10">
                  <div class="bg-slate-900 rounded-2xl p-4 text-white shadow-xl flex items-center gap-4">
                    <div class="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center text-xl">📊</div>
                    <div>
                      <p class="text-[9px] font-black uppercase tracking-widest text-white/50">Class Average</p>
                      <p class="text-xl font-black">{{ classAverage }}%</p>
                    </div>
                  </div>
                  <div class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm flex items-center gap-4">
                    <div class="w-10 h-10 bg-green-50 rounded-xl flex items-center justify-center text-xl border border-green-100">✅</div>
                    <div>
                      <p class="text-[9px] font-black uppercase tracking-widest text-gray-400">Pass Rate</p>
                      <p class="text-xl font-black text-green-600">{{ passRate }}%</p>
                      <p class="text-[8px] text-gray-400 font-bold mt-0.5 uppercase tracking-tighter">{{ passedCount }} of {{ totalStudents }} Passed</p>
                    </div>
                  </div>
                  <div class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm flex items-center gap-4">
                    <div class="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center text-xl border border-blue-100">📝</div>
                    <div>
                      <p class="text-[9px] font-black uppercase tracking-widest text-gray-400">Participation</p>
                      <p class="text-xl font-black text-blue-600">{{ participationRate }}%</p>
                      <p class="text-[8px] text-gray-400 font-bold mt-0.5 uppercase tracking-tighter">{{ participationCount }} of {{ totalStudents }} Active</p>
                    </div>
                  </div>
                  <div class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm flex items-center gap-4">
                    <div class="w-10 h-10 bg-pink-50 rounded-xl flex items-center justify-center text-xl border border-pink-100">⏳</div>
                    <div>
                      <p class="text-[9px] font-black uppercase tracking-widest text-gray-400">Pending Release</p>
                      <p class="text-xl font-black text-pink-500">{{ pendingReleaseCount }}</p>
                    </div>
                  </div>
                </div>

                <!-- Filters and Search -->
                <div class="flex flex-col md:flex-row gap-4 mb-6 items-center justify-between">
                  <div class="relative w-full md:w-80">
                    <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </span>
                    <input 
                      v-model="searchQuery" 
                      type="text" 
                      placeholder="Search student or ID..." 
                      class="w-full bg-white border border-gray-200 rounded-xl py-2.5 pl-10 pr-4 text-xs font-medium focus:ring-2 focus:ring-pink-500 outline-none transition-all"
                    >
                  </div>
                  <div class="flex gap-2">
                    <button 
                      v-for="f in ['all', 'passed', 'failed', 'not taken']" 
                      :key="f"
                      @click="filterStatus = f"
                      :class="[
                        'px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border',
                        filterStatus === f ? 'bg-pink-500 text-white border-pink-500 shadow-md' : 'bg-white text-gray-400 border-gray-100 hover:bg-gray-50'
                      ]"
                    >
                      {{ f }}
                    </button>
                  </div>
                </div>

                <!-- Main Leaderboard Table: Classic Print Style -->
                <div class="overflow-hidden border border-gray-100 rounded-xl bg-white shadow-sm print:border-none print:shadow-none print:mt-10">
                  <!-- Print Header: Classic Form Layout -->
                  <div class="hidden print:block mb-10 w-full">
                    <div class="text-center mb-10">
                      <h1 class="text-3xl font-black uppercase tracking-widest border-b-2 border-black pb-4">Grade Report</h1>
                    </div>

                    <div class="grid grid-cols-2 gap-x-12 gap-y-6">
                      <div class="flex items-end gap-2 text-left">
                        <span class="text-[11px] font-black uppercase whitespace-nowrap">Course Number:</span>
                        <div class="border-b border-black flex-1 text-xs font-bold uppercase pb-0.5 px-2">{{ activity?.section_code }}</div>
                      </div>
                      <div class="flex items-end gap-2 text-left">
                        <span class="text-[11px] font-black uppercase whitespace-nowrap">Section:</span>
                        <div class="border-b border-black flex-1 text-xs font-bold uppercase pb-0.5 px-2">{{ activity?.section_name }}</div>
                      </div>
                      <div class="flex items-end gap-2 text-left">
                        <span class="text-[11px] font-black uppercase whitespace-nowrap">Activity Title:</span>
                        <div class="border-b border-black flex-1 text-xs font-bold uppercase pb-0.5 px-2">{{ activity?.title }}</div>
                      </div>
                      <div class="flex items-end gap-2 text-left">
                        <span class="text-[11px] font-black uppercase whitespace-nowrap">Schedule:</span>
                        <div class="border-b border-black flex-1 text-xs font-bold uppercase pb-0.5 px-2">{{ activity ? formatSchedule(activity.schedule) : '' }}</div>
                      </div>
                      <div class="flex items-end gap-2 text-left">
                        <span class="text-[11px] font-black uppercase whitespace-nowrap">A.Y. Semester:</span>
                        <div class="border-b border-black flex-1 text-xs font-bold uppercase pb-0.5 px-2">{{ activity?.academic_year }} - {{ activity?.semester }}</div>
                      </div>
                      <div class="flex items-end gap-2 text-left">
                        <span class="text-[11px] font-black uppercase whitespace-nowrap">Date Printed:</span>
                        <div class="border-b border-black flex-1 text-xs font-bold uppercase pb-0.5 px-2">{{ new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) }}</div>
                      </div>
                    </div>
                  </div>

                  <table class="w-full text-left border-collapse print:border-2 print:border-black">
                    <thead class="bg-gray-50 border-b border-gray-100 print:bg-gray-100">
                      <tr>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest w-16 text-center print:text-black print:border print:border-black">Rank</th>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest print:text-black print:border print:border-black">Student Information</th>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest text-center print:text-black print:border print:border-black">Raw Score</th>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest text-center print:text-black print:border print:border-black">Percentage</th>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest text-center print:hidden">Status</th>
                        <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest text-right print:text-black print:border print:border-black">Result</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-50 text-print-black">
                      <tr v-for="(sub, index) in filteredSubmissions" :key="sub.student_id" 
                        class="hover:bg-gray-50/50 transition-colors"
                        :class="[sub.grade === null ? 'bg-gray-50/20' : '', index === 0 && sub.grade !== null && filterStatus === 'all' ? 'bg-amber-50/10' : '']"
                      >
                        <td class="px-3 py-3 print:border print:border-gray-200">
                          <div class="flex items-center justify-center">
                            <span v-if="sub.grade !== null" :class="[
                              'px-2 py-0.5 rounded-full text-[9px] font-black shadow-sm border border-black/5 whitespace-nowrap',
                              index === 0 ? 'bg-amber-400 text-white' : index === 1 ? 'bg-slate-300 text-slate-700' : index === 2 ? 'bg-orange-200 text-orange-800' : 'bg-slate-100 text-slate-500'
                            ]">
                              {{ getRankWithSuffix(index + 1) }}
                            </span>
                            <span v-else class="text-gray-300 font-bold text-[9px]">-</span>
                          </div>
                        </td>
                        <td class="px-3 py-3 print:border print:border-gray-200">
                          <div class="flex items-center gap-2">
                            <div class="w-7 h-7 rounded-lg bg-gray-100 flex items-center justify-center font-bold text-gray-400 text-[9px] uppercase print:hidden">
                              {{ sub.first_name[0] }}{{ sub.last_name[0] }}
                            </div>
                            <div>
                              <div class="font-bold text-xs text-gray-900 flex items-center gap-1.5 leading-tight print:text-gray-800">
                                {{ sub.first_name }} {{ sub.last_name }}
                              </div>
                              <div class="text-[9px] text-gray-400 font-medium tracking-tight uppercase print:text-gray-500 print:font-bold print:mt-0.5">{{ sub.student_number }}</div>
                            </div>
                          </div>
                        </td>
                        <td class="px-3 py-3 text-center font-mono font-bold text-xs print:border print:border-gray-200 print:text-gray-700">
                          <span v-if="sub.grade !== null" class="text-slate-700">
                            {{ sub.grade }} <span class="text-gray-300 font-normal print:hidden">/ {{ activity?.total_points }}</span>
                          </span>
                          <span v-else class="text-gray-300 italic text-[9px]">No Grade</span>
                        </td>
                        <td class="px-3 py-3 text-center print:border print:border-gray-200">
                          <div v-if="sub.grade !== null" class="inline-block px-1.5 py-0.5 rounded-full text-[10px] font-black print:text-gray-800 print:border-none" 
                            :class="getPercentage(sub) >= 60 ? 'bg-green-50 text-green-700 border border-green-100' : 'bg-red-50 text-red-700 border border-red-100'">
                            {{ getPercentage(sub) }}%
                          </div>
                          <span v-else class="text-gray-300 italic text-[9px]">No Data</span>
                        </td>
                        <td class="px-3 py-3 text-center print:hidden">
                          <span v-if="sub.grade !== null" :class="['px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-widest', sub.is_released ? 'bg-blue-50 text-blue-600' : 'bg-amber-50 text-amber-600']">
                            {{ sub.is_released ? 'Released' : 'Pending' }}
                          </span>
                          <span v-else class="px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-widest bg-gray-100 text-gray-400">
                            Not Taken
                          </span>
                        </td>
                        <td class="px-3 py-3 text-right print:text-center print:border print:border-gray-200">
                          <div v-if="sub.grade !== null">
                            <span :class="['text-[9px] font-black uppercase tracking-widest print:text-[10px] print:font-bold', getPercentage(sub) >= 60 ? 'text-green-600' : 'text-red-600']">
                              {{ getPercentage(sub) >= 60 ? 'Passed' : 'Failed' }}
                            </span>
                          </div>
                          <span v-else class="text-gray-300 font-bold text-[8px] uppercase tracking-tighter">Incomplete</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <div v-if="sortedSubmissions.length === 0" class="py-20 text-center">
                    <p class="text-gray-400 text-sm italic font-medium">No students enrolled in this section.</p>
                  </div>
                </div>
              </div>
            </div>
    </div>
  </div>
</template>

<script setup>
import CTHM from '@/assets/image/cthm-logos.png'
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { activityDetailsService } from '@/services/instructor/activityDetailsService'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const activityId = route.params.activityId

// --- UI State ---
const loading = ref(true)
const searchQuery = ref('')
const filterStatus = ref('all')

// --- Data State ---
const sections = ref([])
const user = ref({ first_name: '', last_name: '', username: '' })
const activity = ref(null)
const submissions = ref([])

// --- Data State ---

const fetchData = async () => {
  loading.value = true
  try {
    const dashData = await instructorDashboardService.getDashboard()
    sections.value = dashData.sections || []
    user.value = dashData.user || { first_name: '', last_name: '', username: '' }

    const actData = await activityDetailsService.getActivity(activityId)
    activity.value = actData

    const subData = await activityDetailsService.getSubmissions(activityId)
    submissions.value = subData.submissions || []
  } catch (error) {
    console.error("Error fetching data:", error)
  } finally {
    loading.value = false
  }
}

const sortedSubmissions = computed(() => {
  return [...submissions.value].sort((a, b) => {
    // If one has no grade, put it at the bottom
    if (a.grade === null && b.grade !== null) return 1
    if (a.grade !== null && b.grade === null) return -1
    if (a.grade === null && b.grade === null) return 0
    
    // Sort by grade descending
    return b.grade - a.grade
  })
})

const topStudents = computed(() => {
  return sortedSubmissions.value.filter(s => s.grade !== null)
})

const filteredSubmissions = computed(() => {
  let list = sortedSubmissions.value
  
  // Apply Search
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(s => 
      s.first_name.toLowerCase().includes(q) || 
      s.last_name.toLowerCase().includes(q) || 
      s.student_number.toLowerCase().includes(q)
    )
  }
  
  // Apply Status Filter
  if (filterStatus.value !== 'all') {
    if (filterStatus.value === 'passed') {
      list = list.filter(s => s.grade !== null && getPercentage(s) >= 60)
    } else if (filterStatus.value === 'failed') {
      list = list.filter(s => s.grade !== null && getPercentage(s) < 60)
    } else if (filterStatus.value === 'not taken') {
      list = list.filter(s => s.grade === null)
    }
  }
  
  return list
})

const totalStudents = computed(() => submissions.value.length)
const participationCount = computed(() => submissions.value.filter(s => s.booking !== null).length)
const passedCount = computed(() => submissions.value.filter(s => s.grade !== null && getPercentage(s) >= 60).length)

const classAverage = computed(() => {
  const graded = submissions.value.filter(s => s.grade !== null)
  if (graded.length === 0) return 0
  const totalPercentage = graded.reduce((sum, s) => sum + getPercentage(s), 0)
  return Math.round(totalPercentage / graded.length)
})

const passRate = computed(() => {
  if (totalStudents.value === 0) return 0
  return Math.round((passedCount.value / totalStudents.value) * 100)
})

const participationRate = computed(() => {
  if (totalStudents.value === 0) return 0
  return Math.round((participationCount.value / totalStudents.value) * 100)
})

const pendingReleaseCount = computed(() => {
  return submissions.value.filter(s => s.grade !== null && !s.is_released).length
})

const getPercentage = (sub) => {
  // Ensure we are working with numbers
  const grade = sub.grade === null ? 0 : parseFloat(sub.grade)
  const total = parseFloat(activity.value?.total_points || 100)
  
  if (total === 0) return 0
  
  // Calculate percentage against activity total points
  const percentage = (grade / total) * 100
  return Math.round(percentage)
}

const getRankWithSuffix = (rank) => {
  const j = rank % 10,
        k = rank % 100;
  if (j == 1 && k != 11) {
    return rank + "st";
  }
  if (j == 2 && k != 12) {
    return rank + "nd";
  }
  if (j == 3 && k != 13) {
    return rank + "rd";
  }
  return rank + "th";
}

const formatTimeOnly = (t) => {
  if (!t) return ''
  const [h, m] = t.split(':')
  const hour = parseInt(h)
  const ampm = hour >= 12 ? 'PM' : 'AM'
  const h12 = hour % 12 || 12
  return `${h12}:${m} ${ampm}`
}

const formatSchedule = (scheduleData) => {
  if (!scheduleData) return 'No schedule set'
  try {
    const schedules = typeof scheduleData === 'string' ? JSON.parse(scheduleData) : scheduleData
    if (Array.isArray(schedules)) {
      if (schedules.length === 0) return 'No schedule set'
      return schedules.map(s => {
        const dayShort = s.day.substring(0, 3)
        return `${dayShort} ${formatTimeOnly(s.start_time)}-${formatTimeOnly(s.end_time)}`
      }).join(', ')
    }
  } catch (e) {}
  return scheduleData
}

onMounted(fetchData)
</script>

<style scoped>
.font-sans {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
</style>
