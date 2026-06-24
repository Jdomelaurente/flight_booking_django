<template>
  <div v-if="section" class="bg-white border border-gray-300 rounded-lg p-4 text-gray-800 shadow-lg">
    <h3 class="text-sm font-bold mb-3">My Section</h3>

    <div class="space-y-2">
      <!-- Section Code -->
      <div class="rounded-md border border-gray-300 p-1">
        <p class="text-xs text-gray-500 mb-1">Section Code</p>
        <p class="text-lg font-bold text-gray-900">
          {{ section.section_code }}
        </p>
      </div>

      <!-- Section Name -->
      <div class="rounded-md border border-gray-300 p-3">
        <p class="text-xs text-gray-500 mb-1">Section Name</p>
        <p class="text-base font-semibold text-gray-900">
          {{ section.section_name }}
        </p>
      </div>

      <!-- Description -->
      <div class="rounded-md border border-gray-300 p-3">
        <p class="text-xs text-gray-500 mb-1">Description</p>
        <p class="text-sm text-gray-800">
          {{ section.description || 'No description' }}
        </p>
      </div>

      <!-- Schedule -->
      <div class="rounded-md border border-gray-300 p-3">
        <p class="text-xs text-gray-500 mb-2">Class Schedule</p>
        <div v-if="!section.schedule" class="text-xs text-gray-400 italic">No schedule set</div>
        <div v-else class="space-y-2">
          <div v-for="(s, i) in parsedSchedules" :key="i" class="flex items-center justify-between bg-gray-50 p-2 rounded border border-gray-100">
            <span class="text-[10px] font-bold text-pink-500 uppercase">{{ s.day.substring(0, 3) }}</span>
            <span class="text-[10px] font-medium text-gray-600">{{ formatTime(s.start_time) }} - {{ formatTime(s.end_time) }}</span>
          </div>
        </div>
      </div>

      <!-- Total Activities -->
      <div class="rounded-md border border-gray-300 p-3 flex justify-between items-center">
        <span class="text-xs text-gray-500">Total Activities</span>
        <span class="text-lg font-bold text-gray-900">
          {{ totalActivities }}
        </span>
      </div>

      <!-- Active Activities -->
      <div class="rounded-md border border-gray-300 p-3 flex justify-between items-center">
        <span class="text-xs text-gray-500">Active Activities</span>
        <span class="text-lg font-bold text-gray-900">
          {{ activeActivities }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentSectionInfo',
  props: {
    section: {
      type: Object,
      required: true
    },
    totalActivities: {
      type: Number,
      default: 0
    },
    activeActivities: {
      type: Number,
      default: 0
    }
  },
  computed: {
    parsedSchedules() {
      const scheduleData = this.section.schedule
      if (!scheduleData) return []
      try {
        const schedules = typeof scheduleData === 'string' ? JSON.parse(scheduleData) : scheduleData
        if (Array.isArray(schedules)) return schedules
      } catch (e) {}
      return []
    }
  },
  methods: {
    formatTime(t) {
      if (!t) return ''
      const [h, m] = t.split(':')
      const hour = parseInt(h)
      const ampm = hour >= 12 ? 'PM' : 'AM'
      const h12 = hour % 12 || 12
      return `${h12}:${m} ${ampm}`
    }
  }
}
</script>
