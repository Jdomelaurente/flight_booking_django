<template>
  <div class="flex flex-col h-screen bg-gray-200">
    <!-- TOP HEADER -->
    <DashboardHeader 
      :student="userStore.studentProfile || {}" 
      @toggle-sidebar="toggleSidebar" 
      @logout="handleLogout" 
    />

    <!-- MAIN CONTENT WITH SIDEBAR -->
    <div class="flex flex-1 overflow-hidden relative">
      <!-- LEFT SIDEBAR - Becomes a drawer on mobile -->
      <DashboardSidebar 
        :sidebar-open="sidebarOpen" 
        :section="section" 
        @close-sidebar="sidebarOpen = false"
      />

      <!-- RIGHT CONTENT AREA -->
      <main class="flex-1 flex flex-col bg-gray-200 overflow-y-auto">
        <router-view v-if="!loading" :section="section" :activities="activities" :classmates="classmates" :instructor="instructor" />
        
        <!-- Loading State -->
        <div v-else class="flex-1 flex items-center justify-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-500"></div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { studentDashboardService } from '@/services/Student/studentDashboardService.js'
import DashboardHeader from '@/components/Student/DashboardHeader.vue'
import DashboardSidebar from '@/components/Student/DashboardSidebar.vue'

export default {
  name: 'StudentLayout',
  components: {
    DashboardHeader,
    DashboardSidebar
  },
  setup() {
    const userStore = useUserStore()
    const router = useRouter()
    const sidebarOpen = ref(window.innerWidth >= 1024)
    const section = ref(null)
    const activities = ref([])
    const classmates = ref([])
    const instructor = ref(null)
    const loading = ref(true)

    const toggleSidebar = () => {
      sidebarOpen.value = !sidebarOpen.value
    }

    const handleLogout = () => {
      userStore.logout()
      router.push('/login')
    }

    const loadData = async () => {
      try {
        loading.value = true
        const response = await studentDashboardService.getStudentDashboard()
        
        if (response.data?.not_enrolled) {
          userStore.setEnrolled(false)
          return
        }
        
        userStore.setEnrolled(true)
        if (response.data?.user) {
          userStore.setStudentProfile(response.data.user)
        }
        
        section.value = response.data.section || null
        activities.value = response.data.activities || []
        classmates.value = response.data.classmates || []
        instructor.value = response.data.instructor || null
      } catch (error) {
        console.error("Error loading layout data:", error)
        if (error.response?.data?.not_enrolled) {
          userStore.setEnrolled(false)
          if (error.response.data.user) {
            userStore.setStudentProfile(error.response.data.user)
          }
        }
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadData()
    })

    return {
      userStore,
      sidebarOpen,
      section,
      activities,
      classmates,
      instructor,
      loading,
      toggleSidebar,
      handleLogout
    }
  }
}
</script>
