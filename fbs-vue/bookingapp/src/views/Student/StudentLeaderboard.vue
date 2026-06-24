<template>
  <div class="min-h-screen bg-slate-50">
    <!-- Header -->
    <div class="bg-white border-b border-slate-100 px-6 py-5 sticky top-0 z-10 shadow-sm">
      <div class="max-w-4xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-4">
          <button @click="$router.back()" class="w-9 h-9 rounded-sm bg-slate-50 border border-slate-200 flex items-center justify-center text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-all">
            <i class="ph ph-arrow-left text-lg"></i>
          </button>
          <div>
            <h1 class="text-sm font-black text-slate-900 uppercase tracking-tight">Section Leaderboard</h1>
            <p class="text-[9px] text-[#FF579A] font-bold uppercase tracking-widest">{{ sectionName }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <div v-if="myRank" class="px-3 py-1.5 bg-pink-50 border border-pink-100 rounded-sm text-[10px] font-black text-[#FF579A] uppercase tracking-widest">
            Your Rank: #{{ myRank }}
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-4xl mx-auto px-4 py-6 space-y-6">

      <!-- Loading Skeleton -->
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 5" :key="i" class="bg-white border border-slate-100 rounded-sm p-5 animate-pulse flex items-center gap-4">
          <div class="w-10 h-10 bg-slate-100 rounded-full"></div>
          <div class="flex-1 space-y-2">
            <div class="h-3 bg-slate-100 rounded w-1/3"></div>
            <div class="h-2 bg-slate-50 rounded w-1/4"></div>
          </div>
          <div class="h-6 w-12 bg-slate-100 rounded"></div>
        </div>
      </div>

      <template v-else-if="leaderboard.length > 0">
        <!-- Top 3 Podium -->
        <div class="grid grid-cols-3 gap-3 mb-2">
          <!-- 2nd Place -->
          <div v-if="leaderboard[1]" class="bg-white border border-slate-200 rounded-sm p-4 flex flex-col items-center text-center mt-6 shadow-sm">
            <div class="text-2xl mb-2">🥈</div>
            <div class="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center font-bold text-slate-500 text-sm mb-2">
              {{ leaderboard[1].initials }}
            </div>
            <p class="text-[10px] font-black text-slate-900 uppercase tracking-tight leading-tight">{{ leaderboard[1].name }}</p>
            <p class="text-lg font-black text-slate-700 mt-1">{{ leaderboard[1].avg }}%</p>
            <p class="text-[8px] text-slate-400 font-bold uppercase tracking-widest">{{ leaderboard[1].graded }} tasks graded</p>
          </div>

          <!-- 1st Place -->
          <div v-if="leaderboard[0]" class="bg-white border-2 rounded-sm p-4 flex flex-col items-center text-center shadow-md relative overflow-hidden"
            :class="leaderboard[0].isMe ? 'border-[#FF579A]' : 'border-amber-300'">
            <div class="absolute top-0 left-0 right-0 h-1" :class="leaderboard[0].isMe ? 'bg-[#FF579A]' : 'bg-amber-400'"></div>
            <div class="text-3xl mb-2">🥇</div>
            <div class="w-14 h-14 rounded-full flex items-center justify-center font-bold text-white text-sm mb-2 shadow-lg"
              :class="leaderboard[0].isMe ? 'bg-[#FF579A]' : 'bg-amber-400'">
              {{ leaderboard[0].initials }}
            </div>
            <p class="text-[10px] font-black uppercase tracking-tight leading-tight" :class="leaderboard[0].isMe ? 'text-[#FF579A]' : 'text-slate-900'">
              {{ leaderboard[0].isMe ? 'You 🎉' : leaderboard[0].name }}
            </p>
            <p class="text-xl font-black text-slate-900 mt-1">{{ leaderboard[0].avg }}%</p>
            <p class="text-[8px] text-slate-400 font-bold uppercase tracking-widest">{{ leaderboard[0].graded }} tasks graded</p>
          </div>

          <!-- 3rd Place -->
          <div v-if="leaderboard[2]" class="bg-white border border-slate-200 rounded-sm p-4 flex flex-col items-center text-center mt-8 shadow-sm">
            <div class="text-2xl mb-2">🥉</div>
            <div class="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center font-bold text-orange-600 text-sm mb-2">
              {{ leaderboard[2].initials }}
            </div>
            <p class="text-[10px] font-black text-slate-900 uppercase tracking-tight leading-tight">{{ leaderboard[2].name }}</p>
            <p class="text-lg font-black text-slate-700 mt-1">{{ leaderboard[2].avg }}%</p>
            <p class="text-[8px] text-slate-400 font-bold uppercase tracking-widest">{{ leaderboard[2].graded }} tasks graded</p>
          </div>
        </div>

        <!-- Full Rankings List -->
        <div class="bg-white rounded-sm border border-slate-100 shadow-sm overflow-hidden">
          <div class="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 class="text-[10px] font-black text-slate-900 uppercase tracking-widest">Full Rankings</h2>
            <span class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">{{ leaderboard.length }} Students</span>
          </div>

          <div class="divide-y divide-slate-50">
            <div
              v-for="(student, idx) in leaderboard"
              :key="student.id"
              class="flex items-center gap-4 px-5 py-4 transition-all"
              :class="student.isMe ? 'bg-pink-50/50 border-l-2 border-[#FF579A]' : 'hover:bg-slate-50'"
            >
              <!-- Rank Badge -->
              <div class="w-8 text-center shrink-0">
                <span v-if="idx === 0" class="text-xl">🥇</span>
                <span v-else-if="idx === 1" class="text-xl">🥈</span>
                <span v-else-if="idx === 2" class="text-xl">🥉</span>
                <span v-else class="text-[11px] font-black text-slate-400">#{{ idx + 1 }}</span>
              </div>

              <!-- Avatar -->
              <div class="w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs shrink-0"
                :class="student.isMe ? 'bg-[#FF579A] text-white' : 'bg-slate-100 text-slate-500'">
                {{ student.initials }}
              </div>

              <!-- Name -->
              <div class="flex-1 min-w-0">
                <p class="text-xs font-black truncate" :class="student.isMe ? 'text-[#FF579A]' : 'text-slate-900'">
                  {{ student.isMe ? 'You' : student.name }}
                  <span v-if="student.isMe" class="ml-1 text-[8px] bg-pink-100 text-[#FF579A] px-1.5 py-0.5 rounded-sm font-black uppercase tracking-widest">Me</span>
                </p>
                <p class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">{{ student.graded }} activities graded</p>
              </div>

              <!-- Score Bar -->
              <div class="w-28 hidden sm:block">
                <div class="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-700"
                    :class="student.isMe ? 'bg-[#FF579A]' : idx < 3 ? 'bg-amber-400' : 'bg-slate-300'"
                    :style="{ width: student.avg + '%' }">
                  </div>
                </div>
              </div>

              <!-- Score -->
              <div class="text-right shrink-0">
                <p class="text-sm font-black" :class="student.isMe ? 'text-[#FF579A]' : 'text-slate-900'">{{ student.avg }}%</p>
                <p class="text-[8px] text-slate-400 font-bold uppercase tracking-widest">avg</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Note -->
        <p class="text-center text-[9px] text-slate-400 font-bold uppercase tracking-widest pb-4">
          Rankings based on average grade across all graded activities
        </p>
      </template>

      <!-- Empty State -->
      <div v-else class="bg-white border-2 border-dashed border-slate-200 rounded-sm p-16 text-center">
        <div class="text-4xl mb-4">🏆</div>
        <p class="text-xs font-black text-slate-500 uppercase tracking-widest">No ranking data available yet</p>
        <p class="text-[9px] text-slate-400 font-bold mt-2">Complete graded activities to appear on the leaderboard</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { studentDashboardService } from '@/services/Student/studentDashboardService'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(true)
const rawActivities = ref([])
const sectionName = ref('')

// Build leaderboard from section activities that have graded submissions from all students.
// The dashboard endpoint returns the current student's activities; to get a class-wide
// leaderboard we fetch section details.
const leaderboard = ref([])

const myRank = computed(() => {
  const idx = leaderboard.value.findIndex(s => s.isMe)
  return idx >= 0 ? idx + 1 : null
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await studentDashboardService.getStudentDashboard()
    const data = res.data

    sectionName.value = data.section
      ? `${data.section.section_code} — ${data.section.section_name}`
      : 'Your Section'

    // Use section leaderboard if available from the API
    if (data.section_leaderboard && Array.isArray(data.section_leaderboard)) {
      leaderboard.value = buildLeaderboard(data.section_leaderboard, data.user)
    } else if (data.activities && Array.isArray(data.activities)) {
      // Fallback: build a single-student leaderboard if no multi-student data is provided
      rawActivities.value = data.activities
      leaderboard.value = buildSelfLeaderboard(data)
    }
  } catch (err) {
    console.error('Leaderboard fetch error:', err)
  } finally {
    loading.value = false
  }
}

const buildLeaderboard = (students, currentUser) => {
  return students
    .map(s => ({
      id: s.student_id || s.id,
      name: `${s.first_name} ${s.last_name}`,
      initials: `${(s.first_name || '?')[0]}${(s.last_name || '?')[0]}`.toUpperCase(),
      avg: s.avg_grade || s.average_grade || 0,
      graded: s.graded_count || 0,
      isMe: s.student_id === currentUser?.id || s.id === currentUser?.id
    }))
    .sort((a, b) => b.avg - a.avg)
}

const buildSelfLeaderboard = (data) => {
  // Only the current student's data is available
  const graded = (data.activities || []).filter(a => a.status === 'graded' && a.grade !== null)
  const avg = graded.length
    ? Math.round(graded.reduce((sum, a) => sum + parseFloat(a.grade), 0) / graded.length)
    : 0

  const user = data.user || {}
  return [{
    id: user.id,
    name: `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username,
    initials: `${(user.first_name || '?')[0]}${(user.last_name || '?')[0]}`.toUpperCase(),
    avg,
    graded: graded.length,
    isMe: true
  }]
}

onMounted(fetchData)
</script>
