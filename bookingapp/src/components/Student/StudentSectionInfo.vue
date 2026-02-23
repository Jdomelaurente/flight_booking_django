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
  }
}
</script>
