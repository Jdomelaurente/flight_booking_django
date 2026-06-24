<template>
  <div 
    class="bg-white rounded-lg p-6 shadow-sm border border-slate-200 hover:shadow-md transition-all cursor-pointer group relative overflow-hidden"
    @click="$emit('view', activity.id)"
  >
    <div class="flex gap-4 mb-4">
      <div class="w-12 h-12 bg-[#FF579A] text-white rounded-lg flex items-center justify-center text-xl font-bold flex-shrink-0  transition-transform">
        <i v-if="activity.activity_type === 'dcs'" class="ph ph-monitor"></i>
        <i v-else class="ph ph-airplane"></i>
      </div>
      <div class="flex-1">
        <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 ">
          <div>
            <h4 class="text-base font-black text-slate-800 mb-1 group-hover:text-slate-900 transition-colors">{{ activity.title }}</h4>
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{{ activity.section_code || activity.section_name }}</p>
          </div>
          <div>
          <span 
            v-if="activity.completed"
            class="px-2.5 py-0.5 bg-emerald-50 text-emerald-700 text-[9px] font-black rounded-lg border border-emerald-100 uppercase tracking-widest"
          >
            ✓ Done
          </span >
            <span 
              :class="[
                'px-2.5 py-0.5 text-[9px] font-black rounded-lg  uppercase tracking-widest w-fit border',
                activity.is_failed_due_to_time ? 'bg-rose-100 text-rose-800 border-rose-200' :
                activity.status === 'unassigned' ? 'bg-rose-50 text-rose-700 border-rose-100' :
                isOverdue && !activity.completed && activity.status !== 'submitted' && activity.status !== 'graded'
                  ? 'bg-rose-50 text-rose-700 border-rose-100'
                  : activity.is_active 
                    ? 'bg-emerald-50 text-emerald-700 border-emerald-100' 
                    : 'bg-slate-100 text-slate-600 border-slate-200'
              ]"
            >
              {{ activity.is_failed_due_to_time ? 'TIME REACHED' : (activity.status === 'unassigned' ? 'MISSING' : (isOverdue && !activity.completed && activity.status !== 'submitted' && activity.status !== 'graded' ? 'OVERDUE' : (activity.is_active ? 'ACTIVE' : 'INACTIVE'))) }}
            </span>
            </div>
          </div>
        <div class="flex flex-wrap gap-2 mt-3">
          <span class="px-3 py-1 bg-slate-50 text-slate-800 text-[9px] font-black rounded-lg uppercase tracking-widest border border-slate-200">
            {{ activity.activity_type }}
          </span>
          <span 
            :class="[
              'px-3 py-1 text-[9px] font-black rounded-lg uppercase tracking-widest border transition-colors',
              activity.is_failed_due_to_time ? 'bg-rose-50 text-rose-700 border-rose-200' : getStatusColor(activity.status)
            ]"
          >
            {{ activity.is_failed_due_to_time ? 'FAILED' : (activity.status || 'assigned').replace('_', ' ') }}
          </span>
          <span 
            v-if="activity.grade !== null && activity.grades_released"
            :class="[
              'px-3 py-1 text-[9px] font-black rounded-lg uppercase tracking-widest',
              activity.is_failed_due_to_time ? 'bg-rose-600 text-white' : 'bg-[#FF579A] text-white'
            ]"
          >
            Score: {{ Math.round((activity.grade / (activity.total_points || 100)) * 100) }}%
          </span>
          <span 
            v-else-if="activity.status === 'graded' || activity.status === 'submitted' || activity.completed"
            class="px-3 py-1 bg-amber-50 text-amber-600 text-[9px] font-black rounded-lg uppercase tracking-widest border border-amber-100"
          >
            Evaluation Pending
          </span>
        </div>
      </div>
    </div>
    
    <p class="text-[11px] leading-relaxed text-slate-500 mb-6 line-clamp-3 font-medium">
      {{ activity.description || activity.instructions || 'No detailed instructions provided for this curriculum activity.' }}
    </p>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 p-4 bg-slate-50 border border-slate-100 rounded-lg mb-6">
      <div class="flex flex-col gap-2">
        <div class="flex justify-between border-b border-white pb-1">
          <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest">Weight</span>
          <span 
            :class="[
              'text-[10px] font-black',
              activity.is_failed_due_to_time ? 'text-rose-600' : 'text-slate-800'
            ]"
          >
            {{ activity.is_failed_due_to_time ? 'FAIL' : '100%' }}
          </span>
        </div>
        <div class="flex justify-between border-b border-white pb-1">
          <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest">Trip</span>
          <span class="text-[10px] font-black text-slate-800 uppercase">{{ activity.required_trip_type }}</span>
        </div>
        <div class="flex justify-between border-b border-white pb-1">
          <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest">Class</span>
          <span class="text-[10px] font-black text-slate-800 uppercase">{{ activity.required_travel_class }}</span>
        </div>
      </div>
      <div class="flex flex-col gap-2">
        <div class="flex justify-between border-b border-white pb-1">
          <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest">Adults</span>
          <span class="text-[10px] font-black text-slate-800">{{ activity.required_passengers }}</span>
        </div>
        <div class="flex justify-between border-b border-white pb-1">
          <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest">Children</span>
          <span class="text-[10px] font-black text-slate-800">{{ activity.required_children }}</span>
        </div>
        <div class="flex justify-between border-b border-white pb-1">
          <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest">Infants</span>
          <span class="text-[10px] font-black text-slate-800">{{ activity.required_infants }}</span>
        </div>
      </div>
    </div>

    <div class="mt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div class="flex flex-col gap-1">
        <p class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">
          Assigned: {{ formatDate(activity.assigned_at) }}
        </p>
        <p v-if="activity.submitted_at" class="text-[9px] text-emerald-600 font-black uppercase tracking-widest flex items-center gap-1">
          <i class="ph ph-check-circle"></i>
          Submitted: {{ formatDateTime(activity.submitted_at) }}
        </p>
      </div>
      <button 
        @click.stop="$emit('view', activity.id)"
        :disabled="activity.completed || activity.is_failed_due_to_time || (isOverdue && !['submitted', 'graded'].includes(activity.status))"
        :class="[
          'px-6 py-3 text-[10px] font-black uppercase tracking-[0.2em] rounded-lg transition-all border active:scale-95',
          (activity.completed || activity.is_failed_due_to_time || (isOverdue && !['submitted', 'graded'].includes(activity.status)) || activity.status === 'unassigned')
            ? (activity.status === 'unassigned' ? 'bg-rose-50 text-rose-600 border-rose-200' : 'bg-slate-100 text-slate-400 cursor-not-allowed')
            : 'bg-[#FF579A] text-white hover:bg-pink-600'
        ]"
      >
        {{ activity.completed 
            ? 'Curriculum Finished' 
            : (activity.is_failed_due_to_time 
                ? 'TIME REACHED' 
                : (activity.status === 'unassigned'
                    ? 'MISSING'
                    : (isOverdue && !['submitted', 'graded'].includes(activity.status) 
                        ? 'LOCKED - OVERDUE' 
                        : 'Launch Module'
                      )
                  )
              )
        }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ActivityCard',
  props: {
    activity: {
      type: Object,
      required: true
    }
  },
  computed: {
    isOverdue() {
      if (!this.activity.due_date) return false;
      const now = new Date();
      const dueDate = new Date(this.activity.due_date);
      // If it's just a date string (YYYY-MM-DD), set to end of day
      if (typeof this.activity.due_date === 'string' && this.activity.due_date.length <= 10) {
        dueDate.setHours(23, 59, 59, 999);
      }
      return now > dueDate;
    }
  },
  methods: {
    getStatusColor(status) {
      const colors = {
        'assigned': 'bg-slate-50 text-slate-600 border-slate-200',
        'in_progress': 'bg-blue-50 text-blue-700 border-blue-200',
        'submitted': 'bg-indigo-50 text-indigo-700 border-indigo-200',
        'graded': 'bg-emerald-50 text-emerald-700 border-emerald-200'
      };
      return colors[status] || 'bg-gray-50 text-gray-700 border-gray-100';
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric', 
          year: 'numeric' 
        });
      } catch (e) {
        return 'Invalid date';
      }
    },
    formatDateTime(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric', 
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch (e) {
        return 'Invalid date';
      }
    }
  }
}
</script>
