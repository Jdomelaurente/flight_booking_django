<template>
  <div class="bg-white border border-slate-200 rounded-lg p-6 shadow-sm flex flex-col h-fit">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-xs font-black text-slate-900 uppercase tracking-widest leading-none">Upcoming Schedule</h3>
      <div class="w-1.5 h-1.5 rounded-full bg-[#FF579A] animate-pulse"></div>
    </div>
    
    <div class="flex flex-col gap-2">
      <div
        v-for="activity in deadlines"
        :key="activity.id"
        class="flex justify-between items-center p-4 bg-pink-50/20 border border-pink-100/50 rounded-lg cursor-pointer hover:bg-pink-50 transition-all group"
        @click="$emit('view', activity.id)"
      >
        <div class="flex-1">
          <p class="text-[11px] font-black text-slate-800 uppercase tracking-tight group-hover:text-[#FF579A] transition-colors">{{ activity.title }}</p>
          <div class="flex items-center gap-1.5 mt-1">
            <i class="ph ph-calendar-blank text-[10px] text-[#FF579A]"></i>
            <span class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">
              {{ activity.due_date || 'No due date' }}
            </span>
          </div>
        </div>
        <i class="ph ph-caret-right text-slate-300 group-hover:text-[#FF579A] transition-colors"></i>
      </div>
      
      <!-- Placeholder if no activities -->
      <div 
        v-if="deadlines.length === 0"
        class="bg-slate-50 rounded-lg p-2 text-center border border-dashed border-slate-200"
      >
        <div class="w-6 h-6 bg-white rounded-lg flex items-center justify-center mx-auto mb-3 border border-slate-100 text-slate-300">
           <i class="ph ph-calendar-x"></i>
        </div>
        <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Clear Schedule</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UpcomingDeadlines',
  props: {
    deadlines: {
      type: Array,
      default: () => []
    }
  }
}
</script>
