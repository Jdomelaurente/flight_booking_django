<template>
  <div class="bg-white border border-gray-300 rounded-lg p-4 text-gray-800 shadow-sm">
    <h3 class="text-sm font-bold text-gray-800 mb-3">Upcoming Deadlines</h3>
    <div class="flex flex-col gap-3 ">
      <div
          v-for="activity in deadlines"
          :key="activity.id"
          class="flex justify-between items-center p-2.5 bg-white rounded-md 
                border border-gray-300 border-l-4 border-l-orange-500 shadow-sm cursor-pointer hover:bg-gray-50 transition-colors"
          @click="$emit('view', activity.id)"
        >
        <div class="flex-1">
          <p class="text-xs font-semibold text-gray-800">{{ activity.title }}</p>
          <small class="block text-[10px] text-orange-600 font-medium mt-0.5">
            Due: {{ activity.due_date || 'No due date' }}
          </small>
        </div>
      </div>
      
      <!-- Placeholder if no activities -->
      <div 
        v-if="deadlines.length === 0"
        class="bg-white rounded-md p-4 text-center border border-dashed border-gray-300"
      >
        <p class="text-xs text-gray-500">No upcoming deadlines</p>
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
