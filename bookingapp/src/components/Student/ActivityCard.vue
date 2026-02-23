<template>
  <div 
    class="bg-white rounded-lg p-5 shadow-sm border border-gray-200 hover:shadow-md transition-all cursor-pointer"
    @click="$emit('view', activity.id)"
  >
    <div class="flex gap-3 mb-3">
      <div class="w-10 h-10 bg-green-800 text-white rounded-full flex items-center justify-center text-lg font-bold flex-shrink-0">
        {{ activity.title.charAt(0).toUpperCase() }}
      </div>
      <div class="flex-1">
        <div class="flex items-start justify-between">
          <div>
            <h4 class="text-base font-bold text-gray-800 mb-1">{{ activity.title }}</h4>
            <p class="text-xs text-gray-500 mb-2">{{ activity.section_code || activity.section_name }}</p>
          </div>
          <span 
            v-if="activity.completed"
            class="px-2.5 py-0.5 bg-emerald-100 text-emerald-700 text-[10px] font-bold rounded-full uppercase"
          >
            ✓ Completed
          </span>
          <span 
            :class="[
              'px-2.5 py-0.5 text-[10px] font-bold rounded-full uppercase',
              activity.is_active 
                ? 'bg-green-50 text-green-700' 
                : 'bg-gray-100 text-gray-600'
            ]"
          >
            {{ activity.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>
        <div class="flex flex-wrap gap-1.5">
          <span class="px-2.5 py-0.5 bg-blue-50 text-blue-700 text-[10px] font-bold rounded-full uppercase">
            {{ activity.activity_type }}
          </span>
          <span 
            :class="[
              'px-2.5 py-0.5 text-[10px] font-bold rounded-full uppercase',
              getStatusColor(activity.status)
            ]"
          >
            {{ activity.status }}
          </span>
          <span 
            v-if="activity.grade !== null"
            class="px-2.5 py-0.5 bg-pink-50 text-pink-700 text-[10px] font-black rounded-full uppercase border border-pink-100"
          >
            Score: {{ activity.grade }} / {{ activity.total_points }} pts
          </span>
        </div>
      </div>
    </div>
    
    <p class="text-xs leading-relaxed text-gray-600 mb-4">
      {{ activity.description || 'No description provided.' }}
    </p>

    <div class="grid grid-cols-2 gap-4 pt-3 border-t border-gray-100">
      <div class="flex flex-col gap-1">
        <span class="text-[11px] text-gray-600"><strong>Points:</strong> {{ activity.total_points }}</span>
        <span class="text-[11px] text-gray-600"><strong>Trip:</strong> {{ activity.required_trip_type }}</span>
        <span class="text-[11px] text-gray-600"><strong>Class:</strong> {{ activity.required_travel_class }}</span>
      </div>
      <div class="flex flex-col gap-1">
        <span class="text-[11px] text-gray-600">
          <strong>Passengers:</strong> {{ activity.required_passengers }} Adult(s)
        </span>
        <span class="text-[11px] text-gray-600">
          <strong>Children:</strong> {{ activity.required_children }}
        </span>
        <span class="text-[11px] text-gray-600">
          <strong>Infants:</strong> {{ activity.required_infants }}
        </span>
      </div>
    </div>

    <div class="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
      <span class="text-[11px] text-gray-500">
        Assigned: {{ formatDate(activity.assigned_at) }}
      </span>
      <div class="flex gap-2">
        <button 
          v-if="activity.completed"
          @click.stop="$emit('compare', activity)"
          class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg transition-colors"
        >
          View Work
        </button>
        <button 
          @click.stop="$emit('view', activity.id)"
          :disabled="activity.completed"
          :class="[
            'px-4 py-2 text-white text-xs font-semibold rounded-lg transition-colors',
            activity.completed 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-pink-500 hover:bg-pink-600'
          ]"
        >
          {{ activity.completed ? 'Finished' : 'View Details' }}
        </button>
      </div>
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
  methods: {
    getStatusColor(status) {
      const colors = {
        'assigned': 'bg-orange-50 text-orange-700',
        'in_progress': 'bg-blue-50 text-blue-700',
        'submitted': 'bg-purple-50 text-purple-700',
        'graded': 'bg-green-50 text-green-700'
      };
      return colors[status] || 'bg-gray-50 text-gray-700';
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
    }
  }
}
</script>
