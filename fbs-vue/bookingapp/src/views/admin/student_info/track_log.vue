<template>
  <div class="p-6 poppins">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-2">
        <button 
          @click="exportLogs" 
          class="bg-white border border-gray-200 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all"
        >
          <i class="ph ph-export"></i> Export CSV
        </button>
        <button 
          @click="refreshLogs" 
          class="bg-white border border-gray-200 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all"
        >
          <i class="ph ph-arrows-clockwise"></i> Refresh
        </button>
        <button 
          @click="clearAllLogs" 
          class="bg-red-50 text-red-600 px-4 py-2 flex items-center gap-2 hover:bg-red-100 font-bold poppins text-[14px] rounded-[1px] shadow-sm transition-all"
        >
          <i class="ph ph-trash"></i> Clear All Logs
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div 
        v-for="(stat, key) in statsItems" 
        :key="key" 
        class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins leading-none mb-2">{{ key }}</p>
            <p class="text-2xl font-bold text-[#002D1E] poppins">{{ stat.value }}</p>
          </div>
          <div :class="stat.iconBg" class="w-12 h-12 rounded-full flex items-center justify-center">
            <i :class="[stat.icon, stat.iconColor, 'text-xl']"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-4 mb-6">
      <div class="flex flex-col md:flex-row md:items-center gap-4">
        <div class="relative flex-1">
          <i class="ph ph-magnifying-glass absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search by user, action, or keyword..." 
            class="pl-10 pr-4 py-2 border border-gray-200 rounded-[1px] w-full outline-none focus:border-[#fe3787] transition-all poppins text-sm"
            @input="debounceSearch"
          />
        </div>
        
        <select 
          v-model="selectedUser" 
          class="border border-gray-200 px-3 py-2 rounded-[1px] outline-none focus:border-[#fe3787] transition-all poppins text-sm bg-white min-w-[150px]"
          @change="fetchLogs"
        >
          <option value="">All Users</option>
          <option v-for="user in uniqueUsersList" :key="user.id" :value="user.id">
            {{ user.username }}
          </option>
        </select>

        <div class="flex items-center gap-2">
          <input 
            v-model="dateFrom" 
            type="date" 
            class="border border-gray-200 px-3 py-2 rounded-[1px] outline-none focus:border-[#fe3787] transition-all poppins text-sm bg-white"
            @change="fetchLogs"
          />
          <span class="text-gray-400">to</span>
          <input 
            v-model="dateTo" 
            type="date" 
            class="border border-gray-200 px-3 py-2 rounded-[1px] outline-none focus:border-[#fe3787] transition-all poppins text-sm bg-white"
            @change="fetchLogs"
          />
        </div>

        <button 
          @click="clearFilters" 
          class="bg-gray-100 text-gray-600 px-6 py-2 rounded-[1px] hover:bg-gray-200 font-bold poppins text-sm transition-all"
        >
          Reset
        </button>
      </div>
    </div>

    <!-- Activity Timeline -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gray-50/50">
        <div class="flex items-center gap-2">
          <i class="ph ph-clock-counter-clockwise text-[#fe3787] text-xl"></i>
          <h3 class="text-[14px] font-bold text-[#002D1E] uppercase tracking-wider poppins">Live Audit Activity</h3>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest poppins">Auto-refresh</span>
          <button 
            @click="toggleAutoRefresh" 
            :class="[
              'w-10 h-5 rounded-full relative transition-all duration-300',
              autoRefresh ? 'bg-green-500' : 'bg-gray-200'
            ]"
          >
            <div 
              :class="[
                'absolute top-1 w-3 h-3 bg-white rounded-full transition-all duration-300',
                autoRefresh ? 'left-6' : 'left-1'
              ]"
            ></div>
          </button>
        </div>
      </div>

      <div class="divide-y divide-gray-100 max-h-[600px] overflow-y-auto custom-scrollbar">
        <div 
          v-for="(log, index) in paginatedLogs" 
          :key="log.id" 
          :id="`log-row-${log.id}`"
          :class="[{'highlight-active': highlightedId === log.id}, 'p-4 hover:bg-gray-50/50 transition-colors group text-[12px] font-medium']"
        >
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0 relative">
              <div :class="[
                'w-10 h-10 rounded-full flex items-center justify-center shadow-sm',
                getActionColor(log.action)
              ]">
                <i :class="getActionIcon(log.action)" class="text-white text-lg"></i>
              </div>
              <div class="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-white border border-gray-100 flex items-center justify-center shadow-sm">
                <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between mb-1">
                <p class="text-[13px] font-bold text-[#002D1E] poppins">
                  {{ log.user?.username || 'System Agent' }}
                </p>
                <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest poppins">
                  {{ formatDateTime(log.timestamp) }}
                </span>
              </div>
              <p class="text-sm text-gray-600 poppins leading-relaxed">
                {{ log.action }}
              </p>
              <div class="flex items-center gap-4 mt-2">
                <span class="text-[10px] font-bold text-[#fe3787] uppercase tracking-widest poppins bg-[#fe3787]/5 px-2 py-0.5 rounded-[1px]">
                  {{ timeAgo(log.timestamp) }}
                </span>
                <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest poppins">
                  #{{ log.id }}
                </span>
              </div>
            </div>
            <div class="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
              <button 
                @click="deleteLog(log.id)" 
                class="text-gray-300 hover:text-red-600 transition-colors p-2"
                title="Purge Log"
              >
                <i class="ph ph-trash text-lg"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="logs.length === 0 && !loading" class="p-16 text-center poppins">
          <div class="w-20 h-20 mx-auto mb-4 bg-gray-50 border border-gray-100 rounded-full flex items-center justify-center">
            <i class="ph ph-clipboard-text text-3xl text-gray-200"></i>
          </div>
          <h3 class="text-lg font-bold text-[#002D1E] mb-2 poppins">No Activity Recorded</h3>
          <p class="text-sm text-gray-400 poppins max-w-xs mx-auto">System events and user movements will appear here once they occur.</p>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="p-16 text-center">
          <i class="ph ph-circle-notch animate-spin text-4xl text-[#fe3787]"></i>
          <p class="mt-4 text-sm font-bold text-gray-400 uppercase tracking-widest poppins">Reading Audit Logs...</p>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="filteredLogs.length > itemsPerPage" class="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
        <div class="flex items-center justify-between">
          <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
            Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ filteredLogs.length }} Entries
          </div>
          <div class="flex gap-1">
            <button 
              @click="prevPage" 
              :disabled="currentPage === 1"
              class="px-4 py-2 bg-white border border-gray-200 rounded-[1px] text-xs font-bold uppercase hover:bg-gray-50 disabled:opacity-50 poppins transition-all shadow-sm"
            >
              Prev
            </button>
            <button 
              v-for="page in visiblePages" 
              :key="page"
              @click="goToPage(page)"
              :disabled="page === '...'"
              :class="[
                'px-4 py-2 border rounded-[1px] text-xs font-bold uppercase poppins transition-all shadow-sm',
                page === '...' ? 'bg-white border-gray-200 text-gray-400' : 
                currentPage === page ? 'bg-[#fe3787] text-white border-[#fe3787]' : 'bg-white border-gray-200 text-[#002D1E] hover:bg-gray-50'
              ]"
            >
              {{ page }}
            </button>
            <button 
              @click="nextPage" 
              :disabled="currentPage === totalPages"
              class="px-4 py-2 bg-white border border-gray-200 rounded-[1px] text-xs font-bold uppercase hover:bg-gray-50 disabled:opacity-50 poppins transition-all shadow-sm"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Analytics Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
      <!-- Top Users -->
      <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
        <div class="flex items-center gap-2 mb-6">
          <i class="ph ph-users-four text-blue-600 text-xl"></i>
          <h3 class="text-[14px] font-bold text-[#002D1E] uppercase tracking-wider poppins">Active Personnel</h3>
        </div>
        <div class="space-y-4">
          <div 
            v-for="(user, index) in topUsers" 
            :key="user.user__id"
            class="flex items-center justify-between p-4 bg-gray-50 border border-gray-100 rounded-[1px] hover:border-[#fe3787]/30 transition-colors"
          >
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-full bg-[#fe3787]/10 text-[#fe3787] flex items-center justify-center font-bold text-sm">
                0{{ index + 1 }}
              </div>
              <div>
                <span class="font-bold text-[#002D1E] poppins block">{{ user.user__username }}</span>
                <span class="text-[10px] text-gray-400 font-bold uppercase tracking-widest poppins">Security Clearance L1</span>
              </div>
            </div>
            <div class="text-right">
              <span class="text-[14px] font-black text-[#fe3787] poppins">{{ user.count }}</span>
              <span class="text-[10px] text-gray-400 ml-1 font-bold uppercase poppins">Actions</span>
            </div>
          </div>
          <div v-if="topUsers.length === 0" class="text-center text-gray-300 py-8 poppins text-sm uppercase font-bold tracking-widest">
            Insufficient Analytical Data
          </div>
        </div>
      </div>

      <!-- Action Breakdown -->
      <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
        <div class="flex items-center gap-2 mb-6">
          <i class="ph ph-graph text-purple-600 text-xl"></i>
          <h3 class="text-[14px] font-bold text-[#002D1E] uppercase tracking-wider poppins">Operations Metrics</h3>
        </div>
        <div class="space-y-6">
          <div 
            v-for="(action, index) in actionBreakdown" 
            :key="index"
            class="relative"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <div :class="[
                  'w-2 h-2 rounded-full',
                  getActionColor(action.action)
                ]"></div>
                <span class="text-[11px] font-bold text-gray-600 uppercase tracking-widest poppins truncate">{{ truncateAction(action.action) }}</span>
              </div>
              <span class="text-[11px] font-black text-[#002D1E] poppins">{{ action.count }}</span>
            </div>
            <div class="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
              <div 
                class="bg-[#fe3787] h-full transition-all duration-1000 ease-out"
                :style="{ width: (action.count / stats.total * 100) + '%' }"
              ></div>
            </div>
          </div>
          <div v-if="actionBreakdown.length === 0" class="text-center text-gray-300 py-8 poppins text-sm uppercase font-bold tracking-widest">
            Audit Log Stream Empty
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/admin/api'

const route = useRoute()

// Reactive state
const logs = ref([])
const loading = ref(false)
const autoRefresh = ref(false)
const highlightedId = ref(null)
let refreshInterval = null

// Filters
const searchQuery = ref('')
const selectedUser = ref('')
const dateFrom = ref('')
const dateTo = ref('')

// Pagination
const currentPage = ref(1)
const itemsPerPage = 20

// Stats
const stats = ref({ total: 0, today: 0, uniqueUsers: 0, thisWeek: 0 })
const uniqueUsersList = ref([])
const topUsers = ref([])
const actionBreakdown = ref([])

const statsItems = computed(() => ({
  'Global Audit Logs': { value: stats.value.total, icon: 'ph ph-list-dashes', iconBg: 'bg-blue-100', iconColor: 'text-blue-600' },
  'Today\'s Ops': { value: stats.value.today, icon: 'ph ph-calendar-check', iconBg: 'bg-green-100', iconColor: 'text-green-600' },
  'Active Personnel': { value: stats.value.uniqueUsers, icon: 'ph ph-users-three', iconBg: 'bg-purple-100', iconColor: 'text-purple-600' },
  'Weekly Trend': { value: stats.value.thisWeek, icon: 'ph ph-chart-line-up', iconBg: 'bg-orange-100', iconColor: 'text-orange-600' }
}))

// Computed
const filteredLogs = computed(() => {
  let filtered = logs.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    filtered = filtered.filter(l => l.action?.toLowerCase().includes(q) || l.user?.username?.toLowerCase().includes(q))
  }
  if (selectedUser.value) filtered = filtered.filter(l => l.user?.id === parseInt(selectedUser.value))
  if (dateFrom.value) { const d = new Date(dateFrom.value); filtered = filtered.filter(l => new Date(l.timestamp) >= d) }
  if (dateTo.value) { const d = new Date(dateTo.value); d.setHours(23, 59, 59); filtered = filtered.filter(l => new Date(l.timestamp) <= d) }
  return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
})

const totalPages = computed(() => Math.ceil(filteredLogs.value.length / itemsPerPage))
const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredLogs.value.slice(start, start + itemsPerPage)
})
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredLogs.value.length))

const visiblePages = computed(() => {
  const pages = []
  const t = totalPages.value; const c = currentPage.value;
  if (t <= 5) for (let i = 1; i <= t; i++) pages.push(i)
  else {
    if (c <= 3) { for (let i = 1; i <= 4; i++) pages.push(i); pages.push('...', t) }
    else if (c >= t - 2) { pages.push(1, '...'); for (let i = t - 3; i <= t; i++) pages.push(i) }
    else pages.push(1, '...', c - 1, c, c + 1, '...', t)
  }
  return pages
})

// Methods
const fetchLogs = async () => {
  loading.value = true
  try {
    const response = await api.get('/tracklogs/')
    logs.value = response.data
    calculateStats(); extractUniqueUsers(); calculateTopUsers(); calculateActionBreakdown()

    if (route.query.page) {
        currentPage.value = parseInt(route.query.page);
    }

    if (route.query.highlight) {
        const hId = parseInt(route.query.highlight);
        highlightedId.value = hId;

        // Auto-navigate to the correct page for this ID
        const index = logs.value.findIndex(l => l.id === hId);
        if (index !== -1) {
            currentPage.value = Math.floor(index / itemsPerPage) + 1;
        }

        setTimeout(() => {
            const el = document.getElementById(`log-row-${hId}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => { highlightedId.value = null; }, 3000);
        }, 500);
    }
  } catch (err) { console.error(err); logs.value = [] } finally { loading.value = false }
}

const calculateStats = () => {
  const now = new Date(); const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
  stats.value.total = logs.value.length
  stats.value.today = logs.value.filter(l => new Date(l.timestamp) >= today).length
  stats.value.thisWeek = logs.value.filter(l => new Date(l.timestamp) >= weekAgo).length
  stats.value.uniqueUsers = new Set(logs.value.map(l => l.user?.id).filter(Boolean)).size
}

const extractUniqueUsers = () => {
  const usersMap = new Map()
  logs.value.forEach(l => { if (l.user && !usersMap.has(l.user.id)) usersMap.set(l.user.id, l.user) })
  uniqueUsersList.value = Array.from(usersMap.values())
}

const calculateTopUsers = () => {
  const userCounts = {}
  logs.value.forEach(l => {
    const userId = l.user?.id; const username = l.user?.username
    if (userId) {
      if (!userCounts[userId]) userCounts[userId] = { user__id: userId, user__username: username, count: 0 }
      userCounts[userId].count++
    }
  })
  topUsers.value = Object.values(userCounts).sort((a, b) => b.count - a.count).slice(0, 5)
}

const calculateActionBreakdown = () => {
  const actionCounts = {}
  logs.value.forEach(l => {
    const action = l.action
    if (!actionCounts[action]) actionCounts[action] = { action, count: 0 }
    actionCounts[action].count++
  })
  actionBreakdown.value = Object.values(actionCounts).sort((a, b) => b.count - a.count).slice(0, 10)
}

const getActionIcon = (action) => {
  const a = action?.toLowerCase() || ''
  if (a.includes('login')) return 'ph ph-sign-in'
  if (a.includes('logout')) return 'ph ph-sign-out'
  if (a.includes('create') || a.includes('add')) return 'ph ph-plus-circle'
  if (a.includes('update') || a.includes('edit')) return 'ph ph-pencil-simple'
  if (a.includes('delete')) return 'ph ph-trash'
  if (a.includes('book')) return 'ph ph-ticket'
  if (a.includes('pay')) return 'ph ph-credit-card'
  if (a.includes('check')) return 'ph ph-check-circle'
  return 'ph ph-activity'
}

const getActionColor = (action) => {
  const a = action?.toLowerCase() || ''
  if (a.includes('login')) return 'bg-green-500'
  if (a.includes('logout')) return 'bg-gray-400'
  if (a.includes('create') || a.includes('add')) return 'bg-blue-500'
  if (a.includes('update') || a.includes('edit')) return 'bg-amber-500'
  if (a.includes('delete')) return 'bg-red-500'
  return 'bg-[#fe3787]'
}

const formatDateTime = (t) => t ? new Date(t).toLocaleString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''

const timeAgo = (t) => {
  if (!t) return ''
  const s = Math.floor((new Date() - new Date(t)) / 1000)
  if (s < 60) return 'Just now'
  if (s < 3600) return Math.floor(s / 60) + 'm ago'
  if (s < 86400) return Math.floor(s / 3600) + 'h ago'
  return Math.floor(s / 86400) + 'd ago'
}

const truncateAction = (a) => a ? (a.length > 40 ? a.substring(0, 40) + '...' : a) : ''

const deleteLog = async (id) => {
  if (confirm('Permanently purge this activity record?')) {
    try {
      await api.delete(`/tracklogs/${id}/`)
      logs.value = logs.value.filter(l => l.id !== id); calculateStats()
    } catch (err) { console.error(err) }
  }
}

const clearAllLogs = async () => {
  if (confirm('DANGER: This action will PERMANENTLY ERASE all activity history. Continue?')) {
    try {
      await api.delete('/tracklogs/clear-all/')
      logs.value = []; calculateStats(); topUsers.value = []; actionBreakdown.value = []
    } catch (err) { console.error(err) }
  }
}

const exportLogs = async () => {
  try {
    const response = await api.get('/tracklogs/export/', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `audit_logs_${new Date().toISOString().split('T')[0]}.csv`)
    document.body.appendChild(link)
    link.click(); link.remove()
  } catch (err) { console.error(err) }
}

const refreshLogs = () => fetchLogs()

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) refreshInterval = setInterval(fetchLogs, 30000)
  else clearInterval(refreshInterval)
}

const clearFilters = () => { searchQuery.value = ''; selectedUser.value = ''; dateFrom.value = ''; dateTo.value = ''; currentPage.value = 1; fetchLogs() }

let searchTimeout = null
const debounceSearch = () => { clearTimeout(searchTimeout); searchTimeout = setTimeout(() => { currentPage.value = 1 }, 500) }

const prevPage = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const goToPage = (p) => { if (p !== '...') currentPage.value = p }

watch(searchQuery, () => currentPage.value = 1)
onMounted(fetchLogs)
onUnmounted(() => { if (refreshInterval) clearInterval(refreshInterval) })
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
.poppins { font-family: 'Poppins', sans-serif; }

.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #eee; border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #ddd; }
</style>
