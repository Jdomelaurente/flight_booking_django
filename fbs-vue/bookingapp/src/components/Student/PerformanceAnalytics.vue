<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
    <!-- Welcome & Quick Stats -->
    <div class="lg:col-span-2 bg-white rounded-sm border border-slate-200 p-6 shadow-sm relative overflow-hidden flex flex-col justify-between ">
      <div class="absolute right-0 top-0 w-64 h-64 bg-slate-50 rounded-full -mr-32 -mt-32 blur-3xl opacity-50"></div>
      
      <div class="relative z-10">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-8 h-8 bg-[#FF579A] rounded-sm flex items-center justify-center text-white text-xl">
            <i class="ph ph-graduation-cap"></i>
          </div>
          <div>
            <h2 class="text-lg font-black text-slate-900 leading-none mb-1 uppercase tracking-tight">Academic Achievement</h2>
            <p class="text-[10px] text-[#FF579A] font-bold uppercase tracking-widest">Performance Insights & Analytics</p>
          </div>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="p-2 bg-pink-50/30 border border-pink-100 rounded-sm shadow-sm">
            <p class="text-[8px] font-black text-[#FF579A] uppercase tracking-[0.2em] mb-1">Average Grade</p>
            <h4 class="text-lg font-black text-slate-900 leading-none">{{ avgGrade }}%</h4>
            <div class="mt-2 h-1 w-full bg-slate-200 rounded-full overflow-hidden">
              <div class="h-full bg-[#FF579A]" :style="{ width: avgGrade + '%' }"></div>
            </div>
          </div>
          
          <div class="p-2 bg-pink-50/30 border border-pink-100 rounded-sm shadow-sm">
            <p class="text-[8px] font-black text-[#FF579A] uppercase tracking-[0.2em] mb-1">Activities Completed</p>
            <h4 class="text-lg font-black text-slate-900">{{ completedCount }}/{{ totalCount }}</h4>
            <p class="text-[9px] text-pink-600 font-bold mt-1 uppercase">{{ completionRate }}% Progress</p>
          </div>

          <div class="p-2 bg-emerald-50/50 border border-emerald-100 rounded-sm">
            <p class="text-[8px] font-black text-emerald-600/70 uppercase tracking-[0.2em] mb-1">Top Score</p>
            <h4 class="text-lg font-black text-emerald-700">{{ topScore }}%</h4>
            <p class="text-[9px] text-emerald-600/70 font-bold mt-1 uppercase">Peak Performance</p>
          </div>

          <div class="p-2 bg-blue-50/50 border border-blue-100 rounded-sm">
            <p class="text-[8px] font-black text-blue-600/70 uppercase tracking-[0.2em] mb-1">Total Points</p>
            <h4 class="text-lg font-black text-blue-700">{{ totalPoints }}</h4>
            <p class="text-[9px] text-blue-600/70 font-bold mt-1 uppercase">Accumulated</p>
          </div>
        </div>
      </div>

      <div class="relative z-10 pt-6 mt-4 border-t border-slate-100">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="flex -space-x-2">
              <div v-for="i in 3" :key="i" class="w-8 h-8 rounded-full border-2 border-white bg-slate-200 flex items-center justify-center text-[10px] font-bold text-slate-500">
                <i class="ph ph-user"></i>
              </div>
            </div>
            <p class="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Top performers in your section</p>
          </div>
          <button @click="goToLeaderboard" class="text-[10px] font-black text-[#FF579A] uppercase tracking-widest hover:underline active:scale-95 transition-all flex items-center gap-1">
            View Leaderboard
            <i class="ph ph-ranking text-sm"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Charts Container -->
    <div class="bg-white rounded-sm border border-slate-200 p-6 shadow-sm flex flex-col h-full ">
      <div class="flex items-center justify-between mb-6">
         <h3 class="text-xs font-black text-slate-900 uppercase tracking-widest">Score Evolution</h3>
         <span class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Last 10 Tasks</span>
      </div>
      
      <div class="flex-1 min-h-[180px]">
        <BaseChart 
          type="line" 
          :data="lineChartData" 
          :options="lineChartOptions"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import BaseChart from '@/components/common/BaseChart.vue'

const router = useRouter()

const goToLeaderboard = () => {
  router.push('/student/leaderboard')
}

const props = defineProps({
  activities: {
    type: Array,
    default: () => []
  }
})

const gradedActivities = computed(() => {
  return [...props.activities]
    .filter(a => a.status === 'graded' && a.grade !== null && a.grades_released)
    .sort((a, b) => new Date(a.submitted_at || a.updated_at) - new Date(b.submitted_at || b.updated_at))
})

const avgGrade = computed(() => {
  if (gradedActivities.value.length === 0) return 0
  const sum = gradedActivities.value.reduce((acc, a) => acc + parseFloat(a.grade), 0)
  return Math.round(sum / gradedActivities.value.length)
})

const completedCount = computed(() => {
  return props.activities.filter(a => ['submitted', 'graded'].includes(a.status)).length
})

const totalCount = computed(() => props.activities.length)

const completionRate = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((completedCount.value / totalCount.value) * 100)
})

const topScore = computed(() => {
  if (gradedActivities.value.length === 0) return 0
  return Math.max(...gradedActivities.value.map(a => parseFloat(a.grade)))
})

const totalPoints = computed(() => {
  return gradedActivities.value.reduce((acc, a) => acc + (a.points_awarded || (a.grade / 100 * a.total_points) || 0), 0).toFixed(0)
})

// Chart Data
const lineChartData = computed(() => {
  const last10 = gradedActivities.value.slice(-10)
  return {
    labels: last10.map((a, i) => `T${i + 1}`),
    datasets: [{
      label: 'Score',
      data: last10.map(a => parseFloat(a.grade)),
      borderColor: '#FF579A',
      borderWidth: 3,
      tension: 0.4,
      pointRadius: 0,
      pointHoverRadius: 6,
      pointHoverBackgroundColor: '#FF579A',
      pointHoverBorderColor: '#fff',
      pointHoverBorderWidth: 2,
      fill: true,
      backgroundColor: (context) => {
        const ctx = context.chart.ctx
        const gradient = ctx.createLinearGradient(0, 0, 0, 200)
        gradient.addColorStop(0, 'rgba(255, 87, 154, 0.1)')
        gradient.addColorStop(1, 'rgba(255, 87, 154, 0)')
        return gradient
      }
    }]
  }
})

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      min: 10,
      max: 100,
      grid: { 
        display: true,
        color: '#f1f5f9',
        drawTicks: false
      },
      ticks: { 
        display: true,
        font: { size: 9, family: 'Inter', weight: 'bold' },
        color: '#94a3b8',
        padding: 10,
        stepSize: 20,
        callback: (value) => value + '%'
      },
      border: { display: false }
    },
    x: {
      grid: { display: false },
      ticks: { 
        font: { size: 9, family: 'Inter', weight: 'bold' },
        color: '#94a3b8'
      }
    }
  },
  plugins: {
    tooltip: {
      callbacks: {
        title: (items) => {
          const index = items[0].dataIndex
          const act = gradedActivities.value.slice(-10)[index]
          return act.title
        },
        label: (item) => `Grade: ${item.formattedValue}%`
      }
    }
  }
}
</script>
