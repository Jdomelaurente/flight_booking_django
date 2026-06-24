<template>
  <div class="p-4 md:p-8 max-w-7xl mx-auto min-h-screen bg-gray-200 w-full ">
    <div class="flex flex-col md:flex-row md:items-end justify-between mb-10 gap-6">
      <div class="max-w-xl">
        <h1 class="text-xl md:text-2xl lg:text-3xl font-black text-slate-900 tracking-tight leading-none mb-4">Assessment Calendar</h1>
        <p class="text-slate-500 font-medium text-xs md:text-sm leading-relaxed">Track your release dates, deadlines, and performance metrics in one formal overview.</p>
      </div>
      
      <div class="flex items-center gap-1 md:gap-2 bg-white p-1 md:p-1.5 rounded-sm shadow-sm border border-slate-200 w-full md:w-auto justify-between md:justify-start">
        <button @click="changeMonth(-1)" class="p-2 md:p-2.5 hover:bg-slate-50 rounded-sm transition-all active:scale-90">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div class="px-4 md:px-6 py-1 md:py-2 flex flex-col items-center min-w-[120px] md:min-w-[180px]">
          <span class="text-[8px] md:text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] mb-0.5">{{ currentYear }}</span>
          <span class="text-base md:text-lg font-black text-slate-800 uppercase tracking-widest leading-none">{{ currentMonthName }}</span>
        </div>
        <button @click="changeMonth(1)" class="p-2 md:p-2.5 hover:bg-slate-50 rounded-sm transition-all active:scale-90">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-4 gap-8">
      <!-- Calendar Grid -->
      <div class="xl:col-span-3">
        <div class="bg-white rounded-sm shadow-2xl shadow-slate-200/50 border border-slate-200 overflow-hidden">
          <!-- Weekdays -->
          <div class="grid grid-cols-7 bg-slate-50 border-b border-slate-200">
            <div v-for="day in weekdays" :key="day" class="py-4 md:py-5 text-center text-[9px] md:text-[11px] font-black text-slate-400 uppercase tracking-widest border-r border-slate-200 last:border-0">
              <span class="hidden md:inline">{{ day }}</span>
              <span class="md:hidden">{{ day.substring(0, 3) }}</span>
            </div>
          </div>
          
          <!-- Days Grid -->
          <div class="grid grid-cols-7 grid-rows-6">
            <div 
              v-for="(day, index) in calendarDays" 
              :key="index"
              :class="[
                'min-h-[80px] md:h-32 p-1 md:p-3 border-r border-b border-slate-200 transition-all relative group overflow-hidden',
                day.isCurrentMonth ? 'bg-white' : 'bg-slate-50/50 opacity-40',
                day.isToday ? 'bg-indigo-50/30' : '',
                index % 7 === 6 ? 'border-r-0' : ''
              ]"
            >
              <!-- Day Number -->
              <div class="flex justify-between items-start mb-1">
                <span :class="[
                  'text-[10px] md:text-xs font-black p-1 md:p-1.5 rounded-sm inline-flex items-center justify-center min-w-[24px] md:min-w-[28px] transition-colors',
                  day.isToday ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' : 'text-slate-400 group-hover:text-slate-900 group-hover:bg-slate-100'
                ]">{{ day.date }}</span>
                
                <div v-if="day.isToday" class="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse"></div>
              </div>
              
              <!-- Activity Indicators -->
              <div class="space-y-1.5 mt-2">
                <div 
                  v-for="event in day.events" 
                  :key="event.id"
                  @click="selectEvent(event)"
                  :class="[
                    'event-group relative flex flex-col gap-0.5 px-1 py-1 md:px-2 md:py-1.5 rounded-sm border transition-all cursor-pointer select-none',
                    getEventClass(event)
                  ]"
                >
                  <div class="flex items-center justify-between gap-1 overflow-hidden">
                    <span class="text-[7px] md:text-[8px] font-black uppercase tracking-tight truncate leading-none flex-1">{{ event.title }}</span>
                    <span v-if="event.grade !== null" class="hidden sm:inline-block text-[7px] md:text-[8px] font-black bg-white/20 px-1 rounded-sm border border-white/10 uppercase">{{ event.grade }}%</span>
                  </div>
                  <div v-if="event.type === 'deadline'" class="hidden md:flex items-center gap-1 opacity-60">
                    <svg v-if="isCompleted(event)" xmlns="http://www.w3.org/2000/svg" class="h-2 w-2" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                    <span class="text-[7px] font-bold uppercase tracking-widest">{{ event.type === 'deadline' ? 'Due' : 'Release' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Legend -->
        <div class="mt-8 flex flex-wrap gap-4 md:gap-6 justify-center bg-white p-4 md:p-5 rounded-3xl border border-slate-200 shadow-sm">
          <div class="flex items-center gap-2">
            <div class="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm border border-emerald-600/20"></div>
            <span class="text-[9px] md:text-[10px] font-black text-slate-500 uppercase tracking-widest">Completed</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-2.5 h-2.5 rounded-full bg-rose-500 shadow-sm border border-rose-600/20"></div>
            <span class="text-[9px] md:text-[10px] font-black text-slate-500 uppercase tracking-widest">Overdue</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-2.5 h-2.5 rounded-full bg-indigo-500 shadow-sm border border-indigo-600/20"></div>
            <span class="text-[9px] md:text-[10px] font-black text-slate-500 uppercase tracking-widest">Upcoming</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-2.5 h-2.5 rounded-full bg-slate-400 shadow-sm border border-slate-500/20"></div>
            <span class="text-[9px] md:text-[10px] font-black text-slate-500 uppercase tracking-widest">Released Today</span>
          </div>
        </div>
      </div>

      <!-- Detail Sidebar -->
      <div class="flex flex-col gap-6">
        <h2 class="text-sm font-black text-slate-800 flex items-center gap-3 uppercase tracking-[0.2em] px-2">
          <span class="w-1 h-6 bg-slate-900 rounded-sm"></span>
          Selected Analysis
        </h2>
        
        <div v-if="selectedEvent" class="bg-white p-6 md:p-8 rounded-sm shadow-2xl shadow-slate-200/50 border border-slate-200 animate-in fade-in responsive-slide-in duration-300">
          <div :class="[
            'w-12 h-12 md:w-16 md:h-16 rounded-sm flex items-center justify-center text-2xl md:text-3xl mb-6 md:mb-8 shadow-inner border',
            getEventIconClass(selectedEvent)
          ]">
            {{ isCompleted(selectedEvent) ? '✅' : (isOverdue(selectedEvent) ? '⚠️' : '🎯') }}
          </div>

          <div class="mb-2">
            <span :class="[
              'text-[8px] font-black uppercase tracking-[0.3em] px-2 py-0.5 rounded-full border',
              selectedEvent.type === 'deadline' ? 'bg-amber-50 text-amber-600 border-amber-200' : 'bg-slate-50 text-slate-600 border-slate-200'
            ]">{{ selectedEvent.type === 'deadline' ? 'Assessment Submission' : 'System Availability' }}</span>
          </div>
          
          <h3 class="text-2xl font-black text-slate-900 leading-tight mb-4">{{ selectedEvent.title }}</h3>
          
          <div class="bg-slate-50 rounded-sm p-4 mb-8 border border-slate-200/50">
            <div class="flex items-center justify-between text-slate-400 mb-1">
              <span class="text-[8px] font-black uppercase tracking-widest">Timestamp</span>
              <span class="text-[8px] font-black uppercase tracking-widest">Details</span>
            </div>
            <div class="flex items-center justify-between">
              <p class="text-slate-800 font-bold text-sm">{{ formatFullDate(selectedEvent.time) }}</p>
              <p class="text-slate-500 font-bold text-xs">{{ formatTimeOnly(selectedEvent.time) }}</p>
            </div>
          </div>
          
          <div class="space-y-4 mb-10">
            <div class="flex justify-between items-center py-3 border-b border-slate-50">
              <span class="text-slate-400 font-bold text-[10px] uppercase tracking-wider">Evaluation Status</span>
              <span :class="[
                'px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border shadow-sm',
                getStatusStyle(selectedEvent)
              ]">{{ selectedEvent.statusLabel }}</span>
            </div>
          </div>
          
          <router-link 
            :to="`/student/activity/${selectedEvent.id}`"
            class="event-btn relative block w-full text-center py-3 md:py-4 bg-slate-900 text-white rounded-sm font-black text-[10px] md:text-xs tracking-[0.2em] border-2 border-slate-900 hover:bg-white hover:text-slate-900 transition-all shadow-xl shadow-slate-200 active:scale-95 overflow-hidden"
          >
            <span class="relative z-10 uppercase">Access Activity Portal</span>
            <div class="absolute inset-0 bg-slate-100 translate-y-full hover:translate-y-0 transition-transform duration-300"></div>
          </router-link>
        </div>
        
        <div v-else class="bg-slate-50 border-2 border-dashed border-slate-200 rounded-sm p-12 text-center flex flex-col items-center justify-center min-h-[400px]">
          <div class="w-20 h-20 bg-white rounded-sm shadow-sm border border-slate-200 flex items-center justify-center text-3xl mb-6 opacity-40 grayscale">
            🔍
          </div>
          <h4 class="text-lg font-black text-slate-800 uppercase tracking-widest mb-2">Awaiting Selection</h4>
          <p class="text-slate-400 font-medium text-xs max-w-[200px] leading-relaxed">Choose an activity mark on the grid to view detailed performance analytics and submission info.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  activities: {
    type: Array,
    default: () => []
  }
})

const today = new Date()
const currentMonth = ref(today.getMonth())
const currentYear = ref(today.getFullYear())
const selectedEvent = ref(null)

const weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
const months = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

const currentMonthName = computed(() => months[currentMonth.value])

const calendarDays = computed(() => {
  const firstDayOfMonth = new Date(currentYear.value, currentMonth.value, 1).getDay()
  const daysInMonth = new Date(currentYear.value, currentMonth.value + 1, 0).getDate()
  const daysInPrevMonth = new Date(currentYear.value, currentMonth.value, 0).getDate()
  
  const days = []
  const now = new Date()
  
  // Previous month padding
  for (let i = firstDayOfMonth - 1; i >= 0; i--) {
    days.push({ 
      date: daysInPrevMonth - i, 
      isCurrentMonth: false,
      isToday: false,
      events: []
    })
  }
  
    // Current month days
    for (let i = 1; i <= daysInMonth; i++) {
      // Comparison logic using local time to avoid timezone shifts
      const isToday = i === today.getDate() && 
                      currentMonth.value === today.getMonth() && 
                      currentYear.value === today.getFullYear();
      
      // Map events for this day
      const dayEvents = []
      props.activities.forEach(a => {
        // We still need a string for matching activity dates (assuming backend provides YYYY-MM-DD)
        const dateStr = `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`
        
        // Release Events
        if (a.assigned_at && a.assigned_at.startsWith(dateStr)) {
          dayEvents.push({
            ...a,
            type: 'release',
            time: a.assigned_at,
            statusLabel: 'System Released'
          })
        }
        // Deadline Events
        if (a.due_date && a.due_date.startsWith(dateStr)) {
          dayEvents.push({
            ...a,
            type: 'deadline',
            time: a.due_date,
            statusLabel: a.status === 'graded' ? 'Graded' : (a.status === 'submitted' ? 'Submitted' : 'Pending')
          })
        }
      })
      
      days.push({ 
        date: i, 
        isCurrentMonth: true,
        isToday: isToday,
        events: dayEvents.sort((a, b) => (a.type === 'release' ? -1 : 1))
      })
    }
  
  // Next month padding
  const remainingDays = 42 - days.length
  for (let i = 1; i <= remainingDays; i++) {
    days.push({ 
      date: i, 
      isCurrentMonth: false,
      isToday: false,
      events: []
    })
  }
  
  return days
})

const changeMonth = (delta) => {
  currentMonth.value += delta
  if (currentMonth.value > 11) {
    currentMonth.value = 0
    currentYear.value++
  } else if (currentMonth.value < 0) {
    currentMonth.value = 11
    currentYear.value--
  }
  selectedEvent.value = null
}

const selectEvent = (event) => {
  selectedEvent.value = event
}

// Logic Helpers
const isCompleted = (event) => {
  return event.grade !== null || event.status === 'submitted' || event.status === 'graded'
}

const isOverdue = (event) => {
  if (isCompleted(event)) return false
  if (event.type !== 'deadline') return false
  const deadline = new Date(event.due_date)
  return deadline < today
}

const getEventClass = (event) => {
  if (isCompleted(event)) {
    return 'bg-emerald-500 border-emerald-600 text-white shadow-lg shadow-emerald-200/50 hover:bg-emerald-600'
  }
  if (isOverdue(event)) {
    return 'bg-rose-500 border-rose-600 text-white shadow-lg shadow-rose-200/50 hover:bg-rose-600 animate-pulse'
  }
  if (event.type === 'release') {
    return 'bg-white border-slate-300 text-slate-800 hover:border-slate-800'
  }
  return 'bg-indigo-600 border-indigo-700 text-white shadow-lg shadow-indigo-200/50 hover:bg-indigo-700'
}

const getEventIconClass = (event) => {
  if (isCompleted(event)) return 'bg-emerald-50 text-emerald-600 border-emerald-100'
  if (isOverdue(event)) return 'bg-rose-50 text-rose-600 border-rose-100'
  return 'bg-indigo-50 text-indigo-600 border-indigo-100'
}

const getStatusStyle = (event) => {
  if (isCompleted(event)) return 'bg-emerald-50 text-emerald-700 border-emerald-200'
  if (isOverdue(event)) return 'bg-rose-50 text-rose-700 border-rose-200'
  return 'bg-blue-50 text-blue-700 border-blue-200'
}

const formatFullDate = (d) => {
  if (!d) return 'N/A'
  return new Date(d).toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  })
}

const formatTimeOnly = (d) => {
  if (!d) return ''
  return new Date(d).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.animate-in {
  animation-duration: 0.3s;
  animation-timing-function: ease-out;
  animation-fill-mode: forwards;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(1rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(1rem);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.responsive-slide-in {
  animation-name: slideInUp;
}

@media (min-width: 768px) {
  .responsive-slide-in {
    animation-name: slideInRight;
  }
}

/* Custom indicator for overlapping events */
.event-group:nth-child(n+3) {
  display: none;
}
</style>
