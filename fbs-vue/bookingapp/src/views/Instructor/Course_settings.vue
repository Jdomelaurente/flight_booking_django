<template>
  <div class="max-w-4xl mx-auto p-8">
    <LoadingOverlay :loading="isFetching" />
    <div class="mb-8">
      <nav class="flex mb-4" aria-label="Breadcrumb">
        <ol class="inline-flex items-center space-x-1 md:space-x-3">
          <li class="inline-flex items-center">
            <router-link :to="`/instructor/section/${route.params.id}`" class="text-sm text-gray-500 hover:text-pink-600 font-medium transition-colors">Section Details</router-link>
                </li>
                <li>
                  <div class="flex items-center">
                    <svg class="w-3 h-3 text-gray-400 mx-1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 6 10">
                      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 9 4-4-4-4"/>
                    </svg>
                    <span class="ml-1 text-sm font-bold text-gray-800 md:ml-2">Course Settings</span>
                  </div>
                </li>
              </ol>
            </nav>
            <h2 class="text-3xl font-light text-gray-900 tracking-wide">Course Settings</h2>
            <p class="text-sm text-gray-500 mt-1">Manage configurations and administrative controls for this course section.</p>
          </div>

          <div class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="p-8">
              <form @submit.prevent="saveSettings">
                <div class="space-y-8">
                  <!-- Section Profile -->
                  <div>
                    <h3 class="text-xs font-black text-pink-500 uppercase tracking-widest mb-6 border-b border-pink-100 pb-2">Section Profile</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Section Name</label>
                        <input v-model="form.section_name" type="text" class="w-full border-2 border-gray-50 rounded-xl px-4 py-3 focus:border-pink-400 outline-none transition-all font-medium text-gray-700 bg-gray-50/50" required>
                      </div>
                      <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Section Code</label>
                        <input v-model="form.section_code" type="text" class="w-full border-2 border-gray-50 rounded-xl px-4 py-3 focus:border-pink-400 outline-none transition-all font-medium text-gray-700 bg-gray-50/50" required>
                      </div>
                      <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Semester</label>
                        <select v-model="form.semester" class="w-full border-2 border-gray-50 rounded-xl px-4 py-3 focus:border-pink-400 outline-none transition-all font-medium text-gray-700 bg-gray-50/50" required>
                          <option value="1st Semester">1st Semester</option>
                          <option value="2nd Semester">2nd Semester</option>
                        </select>
                      </div>
                      <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Academic Year</label>
                        <select v-model="form.academic_year" class="w-full border-2 border-gray-50 rounded-xl px-4 py-3 focus:border-pink-400 outline-none transition-all font-medium text-gray-700 bg-gray-50/50" required>
                          <option value="2024-2025">2024-2025</option>
                          <option value="2025-2026">2025-2026</option>
                          <option value="2026-2027">2026-2027</option>
                          <option value="2027-2028">2027-2028</option>
                          <option value="2029-2030">2029-2030</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  <!-- Schedule & Description -->
                  <div>
                    <h3 class="text-xs font-black text-pink-500 uppercase tracking-widest mb-6 border-b border-pink-100 pb-2">Schedule & Description</h3>
                    <div class="space-y-6">
                      <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-4">Class Schedule(s)</label>
                        <div v-for="(sched, index) in form.schedules" :key="index" class="flex gap-4 mb-4 items-center">
                          <div class="flex-1">
                            <select v-model="sched.day" class="w-full border-2 border-gray-50 rounded-xl px-4 py-3 focus:border-pink-400 outline-none transition-all font-medium text-gray-700 bg-gray-50/50" required>
                              <option value="" disabled>Select Day</option>
                              <option value="Monday">Monday</option>
                              <option value="Tuesday">Tuesday</option>
                              <option value="Wednesday">Wednesday</option>
                              <option value="Thursday">Thursday</option>
                              <option value="Friday">Friday</option>
                              <option value="Saturday">Saturday</option>
                              <option value="Sunday">Sunday</option>
                            </select>
                          </div>
                          <div class="flex-1">
                            <input v-model="sched.start_time" type="time" class="w-full border-2 border-gray-50 rounded-xl px-4 py-3 focus:border-pink-400 outline-none transition-all font-medium text-gray-700 bg-gray-50/50" required>
                          </div>
                          <span class="text-gray-300 font-bold">to</span>
                          <div class="flex-1">
                            <input v-model="sched.end_time" type="time" class="w-full border-2 border-gray-50 rounded-xl px-4 py-3 focus:border-pink-400 outline-none transition-all font-medium text-gray-700 bg-gray-50/50" required>
                          </div>
                          <button v-if="form.schedules.length > 1" type="button" @click="removeSchedule(index)" class="p-2 text-red-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                          </button>
                        </div>
                        <button type="button" @click="addSchedule" class="px-4 py-2 border-2 border-pink-100 text-pink-500 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-pink-50 transition-all flex items-center gap-2">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 4v16m8-8H4" />
                          </svg>
                          Add Another Schedule
                        </button>
                      </div>
                      <div>
                        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Course Description</label>
                        <textarea v-model="form.description" rows="4" class="w-full border-2 border-gray-50 rounded-xl px-4 py-3 focus:border-pink-400 outline-none transition-all font-medium text-gray-700 bg-gray-50/50 resize-none"></textarea>
                      </div>
                    </div>
                  </div>

                  <!-- Administrative Controls -->
                  <div class="space-y-4">
                    <div class="bg-gray-50 rounded-2xl p-6 border border-gray-100">
                      <h3 class="text-xs font-black text-gray-400 uppercase tracking-widest mb-6">Administrative Controls</h3>
                      <div class="space-y-6">
                        <!-- Lock Section -->
                        <div class="flex items-center justify-between">
                          <div class="pr-8">
                            <h4 class="text-sm font-bold text-gray-800">Lock Section</h4>
                            <p class="text-xs text-gray-500 mt-1">Preventing new students from enrolling in this section. Existing students are unaffected.</p>
                          </div>
                          <label class="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" v-model="form.is_locked" class="sr-only peer">
                            <div class="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-pink-500"></div>
                          </label>
                        </div>


                      </div>
                    </div>

                    <!-- Danger Zone -->
                    <div class="bg-red-50/50 rounded-2xl p-6 border border-red-100 mt-8">
                      <h3 class="text-xs font-black text-red-400 uppercase tracking-widest mb-6">Danger Zone</h3>
                      <div class="flex items-center justify-between">
                        <div class="pr-8">
                          <h4 class="text-sm font-bold text-red-800">Delete Course</h4>
                          <p class="text-xs text-red-500 mt-1">Permanently delete this section and all its associated data. Enrolled students will be unenrolled automatically.</p>
                        </div>
                        <button 
                          type="button" 
                          @click="confirmDelete"
                          class="px-6 py-2.5 bg-red-500 hover:bg-red-600 text-white rounded-xl text-xs font-black uppercase tracking-widest shadow-md transition-all active:scale-95"
                        >
                          Delete Section
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="mt-10 flex justify-end gap-4 border-t border-gray-100 pt-8">
                  <button 
                    type="button" 
                    @click="$router.push(`/instructor/section/${route.params.id}`)"
                    class="px-6 py-3 text-sm font-bold text-gray-400 hover:text-gray-600 uppercase tracking-widest transition-colors"
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    :disabled="loading"
                    class="bg-pink-500 text-white px-10 py-3 rounded-xl font-bold text-xs uppercase tracking-widest shadow-lg hover:shadow-pink-200 active:scale-95 transition-all disabled:opacity-50"
                  >
                    {{ loading ? 'Saving...' : 'Save Changes' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
  </div>
</template>

<script setup>
import CTHM from '@/assets/image/cthm-logos.png'
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { sectionDetailsService } from '@/services/instructor/sectionDetailsService'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { sectionSettingsService } from '@/services/instructor/sectionSettingsService'
import LoadingOverlay from '@/components/instructor/LoadingOverlay.vue'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'
import { useModalStore } from '@/stores/modal'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()
const modalStore = useModalStore()

const isFetching = ref(false)
const loading = ref(false)
const sidebarSections = ref([])
const section = ref(null)

const form = ref({
  section_name: '',
  section_code: '',
  semester: '',
  academic_year: '',
  schedules: [{ day: '', start_time: '', end_time: '' }],
  description: '',
  is_locked: false,
  is_active: true
})

const addSchedule = () => {
  form.value.schedules.push({ day: '', start_time: '', end_time: '' })
}

const removeSchedule = (index) => {
  form.value.schedules.splice(index, 1)
}

const parseSchedule = (scheduleData) => {
  if (!scheduleData) return [{ day: '', start_time: '', end_time: '' }]
  
  try {
    const schedules = typeof scheduleData === 'string' ? JSON.parse(scheduleData) : scheduleData
    if (Array.isArray(schedules) && schedules.length > 0) {
      return schedules
    }
  } catch (e) {
    // If it's not JSON, it might be the old string format like "M-W-F 8:00 AM - 10:00 AM"
    // We'll leave it as is or return a default empty schedule for editing
  }
  
  return [{ day: '', start_time: '', end_time: '' }]
}

const fetchData = async () => {
  isFetching.value = true
  try {
    const sectionId = route.params.id
    const data = await sectionDetailsService.getSectionDetails(sectionId)
    section.value = data
    
    // Populate form
    form.value = {
      section_name: data.section_name || '',
      section_code: data.section_code || '',
      semester: data.semester || '',
      academic_year: data.academic_year || '',
      schedules: parseSchedule(data.schedule),
      description: data.description || '',
      is_locked: data.is_locked || false,
      is_active: data.is_active !== false // Default to true if not present
    }

    const dashboardData = await instructorDashboardService.getDashboard()
    sidebarSections.value = dashboardData.sections
  } catch (error) {
    notificationStore.error("Failed to load section settings.")
  } finally {
    isFetching.value = false
  }
}

const saveSettings = async () => {
  loading.value = true
  try {
    const payload = {
      ...form.value,
      schedule: JSON.stringify(form.value.schedules)
    }
    await sectionSettingsService.updateSectionSettings(route.params.id, payload)
    notificationStore.success("Settings updated successfully!")
    router.push(`/instructor/section/${route.params.id}`)
  } catch (error) {
    const msg = error.response?.data?.error || "Failed to update settings."
    notificationStore.error(msg)
  } finally {
    loading.value = false
  }
}

const confirmDelete = async () => {
  const confirmed = await modalStore.confirm({
    title: 'Delete Section?',
    message: `Are you sure you want to delete "${section.value?.section_name}"? This action is permanent and will unenroll all students and delete all activities.`,
    confirmText: 'Delete Forever',
    cancelText: 'Cancel'
  })

  if (confirmed) {
    loading.value = true
    try {
      await instructorDashboardService.deleteSection(route.params.id)
      notificationStore.success("Section deleted successfully.")
      router.push('/instructor/dashboard')
    } catch (error) {
      notificationStore.error("Failed to delete section.")
    } finally {
      loading.value = false
    }
  }
}

onMounted(async () => {
  await userStore.ensureUserLoaded()
  await fetchData()
})
</script>

<style scoped>
.peer-checked\:bg-pink-500:checked ~ div {
  background-color: #ec4899;
}
</style>
