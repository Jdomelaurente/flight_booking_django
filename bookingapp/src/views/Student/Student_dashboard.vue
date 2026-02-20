<template>
  <div class="flex flex-col h-screen bg-gray-50">
    <!-- TOP HEADER -->
    <div class="bg-pink-500 text-white px-4 py-2.5 flex items-center justify-between shadow-md z-20">
      <div class="flex items-center gap-3">
        <button 
          @click="toggleSidebar" 
          class="p-1.5 hover:bg-pink-600/50 rounded transition-colors focus:outline-none"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
        
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 bg-white rounded-full flex items-center justify-center text-base">🎓</div>
          <div>
            <h1 class="text-xs font-bold leading-tight">CARAGA STATE UNIVERSITY</h1>
            <p class="text-[9px] opacity-90 leading-tight">Cabadbaran City</p>
          </div>
        </div>
      </div>

      <div class="relative">
        <button 
          @click="toggleDropdown" 
          class="flex items-center gap-2 hover:bg-pink-600/50 px-2 py-1 rounded transition-colors focus:outline-none"
        >
          <div class="w-7 h-7 bg-white rounded-full flex items-center justify-center overflow-hidden border-2 border-white shadow-sm">
            <div class="w-full h-full bg-pink-200 flex items-center justify-center text-pink-700 font-bold text-xs">
              {{ initials }}
            </div>
          </div>
        </button>

        <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl py-1 z-50 border border-gray-100">
          <div class="px-4 py-3 border-b border-gray-100">
            <p class="text-sm font-semibold text-gray-800">{{ fullName }}</p>
            <p class="text-xs text-gray-500">{{ student.email }}</p>
          </div>
          <button 
            @click="handleLogout" 
            class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </div>

    <!-- MAIN CONTENT WITH SIDEBAR -->
    <div class="flex flex-1 overflow-hidden">
      <!-- LEFT SIDEBAR -->
      <div 
        :class="[
          'bg-pink-500 text-white transition-all duration-300 ease-in-out flex flex-col shadow-lg overflow-hidden', 
          sidebarOpen ? 'w-56' : 'w-0'
        ]"
      >
        <div v-show="sidebarOpen" class="flex flex-col h-full overflow-y-auto">
          <!-- Home Button -->
          <button 
            @click="goToHome"
            class="flex items-center px-4 py-3 hover:bg-pink-600 transition-colors border-b border-pink-400/30"
          >
            <div class="w-7 h-7 flex items-center justify-center flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
            </div>
            <span class="text-sm font-medium ml-3 whitespace-nowrap">Home</span>
          </button>

          <!-- Calendar Button -->
          <button 
            class="flex items-center px-4 py-3 hover:bg-pink-600 transition-colors border-b border-pink-400/30"
          >
            <div class="w-7 h-7 flex items-center justify-center flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
            </div>
            <span class="text-sm font-medium ml-3 whitespace-nowrap">Calendar</span>
          </button>

          <!-- Tasks Button -->
          <button 
            class="flex items-center px-4 py-3 hover:bg-pink-600 transition-colors border-b border-pink-400/30"
          >
            <div class="w-7 h-7 flex items-center justify-center flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
              </svg>
            </div>
            <span class="text-sm font-medium ml-3 whitespace-nowrap">Tasks</span>
          </button>

          <!-- My Section (Only if enrolled) -->
          <div 
            v-if="section"
            class="flex items-center px-4 py-3 bg-pink-600 border-b border-pink-400/20"
          >
            <div class="w-7 h-7 rounded-full bg-white text-pink-500 flex items-center justify-center font-bold text-xs flex-shrink-0 shadow-sm">
              {{ section.section_name.charAt(0).toUpperCase() }}
            </div>
            <div class="ml-3 flex-1">
              <span class="block truncate text-sm font-medium">
                {{ section.section_name }}
              </span>
              <span class="text-[10px] opacity-80">
                {{ section.activities_count }} activities
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT CONTENT AREA -->
      <main class="flex-1 flex flex-col bg-gray-50 overflow-y-auto">
        <!-- PINK BANNER -->
        <div class="bg-pink-500 mx-6 mt-5 px-8 py-12 rounded-lg shadow-lg">
          <h1 class="text-white text-2xl font-light tracking-wide">
            {{ sectionDisplayName }}
          </h1>
          <p class="text-white/80 text-sm mt-2">
            {{ filteredActivities.length }} {{ filteredActivities.length === 1 ? 'activity' : 'activities' }}
          </p>
        </div>

        <!-- TABS - Only show if section exists -->
        <div v-if="section" class="bg-white mx-6 mt-5 flex gap-0 border-b border-gray-200 rounded-t-lg">
          <button 
            v-for="tab in tabs" 
            :key="tab.name"
            :class="[
              'px-5 py-3 text-xs font-semibold transition-all uppercase tracking-wide border-b-[3px]',
              activeTab === tab.name 
                ? 'text-pink-600 border-pink-600 bg-pink-50/50' 
                : 'text-gray-600 border-transparent hover:text-pink-600 hover:bg-pink-50/30'
            ]"
            @click="activeTab = tab.name"
          >
            {{ tab.label }}
            <span class="ml-1.5 px-1.5 py-0.5 bg-gray-200 text-gray-700 rounded-full text-[9px]">
              {{ getTabCount(tab.name) }}
            </span>
          </button>
        </div>

        <!-- CONTENT AREA -->
        <div :class="[
          'px-6 py-6 mx-6 mb-6',
          section ? 'bg-white rounded-b-lg shadow-sm' : 'bg-transparent'
        ]">
          <!-- Loading State (Skeleton UI) -->
          <div v-if="loading" class="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-6 animate-pulse">
            <!-- Left Side Skeleton -->
            <div class="space-y-4">
              <!-- Deadlines Card Skeleton -->
              <div class="bg-gray-200/50 border border-gray-200 rounded-lg p-4 h-48">
                <div class="h-4 bg-gray-300 rounded w-1/2 mb-4"></div>
                <div class="space-y-3">
                  <div v-for="i in 3" :key="i" class="h-12 bg-white rounded border border-gray-200"></div>
                </div>
              </div>
              <!-- Practice Booking Skeleton -->
              <div class="bg-gray-200 rounded-lg p-5 h-32"></div>
              <!-- Section Card Skeleton -->
              <div class="bg-gray-100/50 border border-gray-200 rounded-lg p-4 h-64">
                <div class="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
                <div class="space-y-2">
                  <div v-for="i in 4" :key="i" class="h-10 bg-gray-200 rounded opacity-50"></div>
                </div>
              </div>
            </div>

            <!-- Right Side Skeleton (Activities) -->
            <div class="space-y-5">
              <div v-for="i in 3" :key="i" class="bg-white rounded-lg p-5 border border-gray-200 h-32 flex gap-4">
                <div class="w-10 h-10 bg-gray-200 rounded-full flex-shrink-0"></div>
                <div class="flex-1 space-y-3">
                  <div class="flex justify-between items-start">
                    <div class="space-y-2 w-full">
                      <div class="h-4 bg-gray-200 rounded w-1/3"></div>
                      <div class="h-3 bg-gray-100 rounded w-1/4"></div>
                    </div>
                    <div class="h-5 bg-gray-100 rounded-full w-20"></div>
                  </div>
                  <div class="flex gap-2">
                    <div v-for="j in 2" :key="j" class="h-5 bg-gray-50 rounded-full w-16 border border-gray-100"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-5">
            <div class="flex items-start gap-3">
              <svg class="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <div class="flex-1">
                <h3 class="text-sm font-semibold text-red-800 mb-1">Error Loading Dashboard</h3>
                <p class="text-sm text-red-600">{{ error }}</p>
                <button 
                  @click="loadDashboard" 
                  class="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 transition-colors"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>

          <!-- No Section Enrolled State -->
          <div v-else-if="!section" class="flex items-center justify-center h-full">
            <div class="bg-white border-2 border-dashed border-gray-300 rounded-lg p-16 text-center max-w-md">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-20 w-20 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <p class="text-gray-800 font-semibold text-lg mb-2">No Section Enrolled</p>
              <p class="text-sm text-gray-500">You haven't been enrolled in any section yet. Please contact your instructor or administrator.</p>
            </div>
          </div>

          <!-- Content when section exists -->
          <div v-else class="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-6">
            <!-- LEFT PANEL -->
            <div class="flex flex-col gap-4">
      
              <!-- Deadlines Card -->
              <div class="bg-white border border-gray-300 rounded-lg p-4 text-gray-800 shadow-sm">
                <h3 class="text-sm font-bold text-gray-800 mb-3">Upcoming Deadlines</h3>
                <div class="flex flex-col gap-3 ">
                  <div
                      v-for="activity in upcomingDeadlines"
                      :key="activity.id"
                      class="flex justify-between items-center p-2.5 bg-white rounded-md 
                            border border-gray-300 border-l-4 border-l-orange-500 shadow-sm cursor-pointer hover:bg-gray-50 transition-colors"
                      @click="viewActivityDetails(activity.id)"
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
                    v-if="upcomingDeadlines.length === 0"
                    class="bg-white rounded-md p-4 text-center border border-dashed border-gray-300"
                  >
                    <p class="text-xs text-gray-500">No upcoming deadlines</p>
                  </div>
                </div>
                
                
              </div>

              <!-- Practice Booking Button -->
              <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-5 text-white shadow-lg hover:shadow-xl transition-all">
                <div class="flex items-center gap-3 mb-3">
                  <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center text-2xl">
                    🎯
                  </div>
                  <div>
                    <h3 class="text-sm font-bold">Practice Booking</h3>
                    <p class="text-xs opacity-90">Try the booking system</p>
                  </div>
                </div>
                <button 
                  @click="startPracticeBooking"
                  class="w-full bg-white text-blue-600 px-4 py-2.5 rounded-lg text-sm font-semibold hover:bg-blue-50 transition-colors shadow-sm"
                >
                  Start Practice Booking
                </button>
              </div>

              <div class="bg-white border border-gray-300 rounded-lg p-4 text-gray-800 shadow-lg">
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
                      {{ activities.length }}
                    </span>
                  </div>

                  <!-- Active Activities -->
                  <div class="rounded-md border border-gray-300 p-3 flex justify-between items-center">
                    <span class="text-xs text-gray-500">Active Activities</span>
                    <span class="text-lg font-bold text-gray-900">
                      {{ activeActivitiesCount }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            

            <!-- RIGHT PANEL - Activities -->
            <div class="flex flex-col gap-5">
              <!-- Activities List -->
              <div 
                v-if="filteredActivities.length > 0"
                v-for="activity in filteredActivities" 
                :key="activity.id"
                class="bg-white rounded-lg p-5 shadow-sm border border-gray-200 hover:shadow-md transition-all cursor-pointer"
                @click="viewActivityDetails(activity.id)"
              >
                <div class="flex gap-3 mb-3">
                  <div class="w-10 h-10 bg-green-800 text-white rounded-full flex items-center justify-center text-lg font-bold flex-shrink-0">
                    {{ activity.title.charAt(0).toUpperCase() }}
                  </div>
                  <div class="flex-1">
                    <div class="flex items-start justify-between">
                      <div>
                        <h4 class="text-base font-bold text-gray-800 mb-1">{{ activity.title }}</h4>
                        <p class="text-xs text-gray-500 mb-2">{{ activity.section_code }} - {{ activity.section_name }}</p>
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
                      @click.stop="openComparisonModal(activity)"
                      class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg transition-colors"
                    >
                      View Work
                    </button>
                    <button 
                      @click.stop="viewActivityDetails(activity.id)"
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

              <!-- No Activities State -->
              <div 
                v-else
                class="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-10 text-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="text-gray-600 font-semibold text-sm">No activities found</p>
                <p class="text-xs text-gray-500 mt-1">
                  Check back later for new assignments
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Comparison Modal -->
    <ComparisonModal
      :is-open="showComparison"
      :is-loading="isLoadingBooking"
      :error-message="comparisonError"
      :activity="comparisonActivity"
      :booking="comparisonBooking"
      @close="showComparison = false"
    />
  </div>
</template>

<script>
import { studentDashboardService } from '@/services/Student/studentDashboardService.js';
import { useBookingStore } from '@/stores/booking';
import ComparisonModal from '@/components/common/ComparisonModal.vue';
import { comparisonService } from '@/services/Student/comparisonService';
import api from '@/services/api/axios';
import { useUserStore } from '@/stores/user'
import { useModalStore } from '@/stores/modal'
import { useNotificationStore } from '@/stores/notification'

export default {
  name: 'StudentDashboard',
  setup() {
    const userStore = useUserStore()
    const modalStore = useModalStore()
    const notificationStore = useNotificationStore()
    return { userStore, modalStore, notificationStore }
  },
  components: {
    ComparisonModal
  },
  data() {
    return {
      student: {
        first_name: '',
        last_name: '',
        username: '',
        email: '',
        student_number: '',
        mi: '',
        phone_number: ''
      },
      activities: [],
      section: null,
      activeTab: 'all',
      tabs: [
        { name: 'all', label: 'All Activities' },
        { name: 'active', label: 'Active' },
        { name: 'assigned', label: 'Assigned' },
        { name: 'submitted', label: 'Submitted' }
      ],
      loading: true,
      error: null,
      sidebarOpen: false,
      dropdownOpen: false,
      
      // Comparison Modal State
      showComparison: false,
      comparisonActivity: null,
      comparisonBooking: null,
      isLoadingBooking: false,
      comparisonError: null
    }
  },
  computed: {
    fullName() {
      return `${this.student.first_name} ${this.student.last_name}`.trim() || 'Student';
    },
    initials() {
      const first = this.student.first_name?.charAt(0) || '';
      const last = this.student.last_name?.charAt(0) || '';
      return (first + last).toUpperCase() || 'ST';
    },
    sectionDisplayName() {
      if (!this.section) return 'No section enrolled';
      return `${this.section.section_code} - ${this.section.section_name}`;
    },
    filteredActivities() {
      let filtered = this.activities;

      if (this.activeTab === 'active') {
        filtered = filtered.filter(a => a.is_active === true);
      } else if (this.activeTab === 'assigned') {
        filtered = filtered.filter(a => a.status === 'assigned');
      } else if (this.activeTab === 'submitted') {
        filtered = filtered.filter(a => ['submitted', 'graded'].includes(a.status));
      }

      return filtered;
    },
    activeActivitiesCount() {
      return this.activities.filter(a => a.is_active === true).length;
    },
    upcomingDeadlines() {
      return this.activities
        .filter(a => a.due_date && a.is_active)
        .slice(0, 5)
        .sort((a, b) => new Date(a.due_date) - new Date(b.due_date));
    }
  },
  async created() {
    console.log('🔐 Component Created - Auth Check');
    
    if (!this.userStore.isAuthenticated) {
      console.error('❌ No token found!');
      this.error = "Authentication required. Please login.";
      this.loading = false;
      
      setTimeout(() => {
        this.$router.push('/login');
      }, 2000);
      return;
    }
    
    await this.loadDashboard();
  },
  methods: {
    async loadDashboard() {
      try {
        this.loading = true;
        this.error = null;
        
        console.log('📡 Fetching student dashboard...');
        
        const token = localStorage.getItem('token');
        console.log('🔑 Token in localStorage:', token ? 'EXISTS' : 'MISSING');
        
        if (!token) {
          throw new Error('No authentication token found');
        }
        
        const response = await studentDashboardService.getStudentDashboard();
        
        console.log('✅ Response received:', response.data);
        
        if (response.data && response.data.user) {
          this.student = {
            first_name: response.data.user.first_name || '',
            last_name: response.data.user.last_name || '',
            username: response.data.user.username || '',
            email: response.data.user.email || '',
            student_number: response.data.user.student_number || '',
            mi: response.data.user.mi || '',
            phone_number: response.data.user.phone_number || ''
          };
          
          // Store student data in central store
          this.userStore.setStudentProfile(this.student);
          
          this.section = response.data.section || null;
          this.activities = response.data.activities || [];
          
          console.log('✅ Student loaded:', this.student);
          console.log('✅ Section loaded:', this.section);
          console.log('✅ Total activities loaded:', this.activities.length);
          
          if (this.activities.length > 0) {
            console.log('📦 First activity structure:', this.activities[0]);
          } else {
            console.warn('⚠️ No activities found for this student');
          }
        } else {
          console.error("❌ Student data not found in response");
          this.error = "Failed to load student data";
        }
      } catch (error) {
        console.error("❌ Error loading dashboard:", error);
        
        if (error.response) {
          console.error("❌ Server responded with error:", error.response.status);
          console.error("📋 Error data:", error.response.data);
          
          if (error.response.status === 404) {
            this.error = "Dashboard endpoint not found. Please check your server configuration.";
          } else if (error.response.status === 403) {
            this.error = error.response.data.error || "Access denied. You must be a student to access this page.";
          } else if (error.response.status === 401) {
            this.error = "Your session has expired. Please login again.";
            localStorage.removeItem('token');
            localStorage.removeItem('auth_token');
            localStorage.removeItem('student_data');
            setTimeout(() => {
              this.$router.push('/login');
            }, 2000);
          } else if (error.response.status === 500) {
            this.error = "Server error. Please contact your administrator.";
          } else {
            this.error = error.response.data.error || `Error: ${error.response.status}`;
          }
        } else if (error.request) {
          this.error = "Cannot connect to server. Please check your connection.";
          console.error("🔌 Server connection failed");
        } else {
          this.error = error.message || "An unexpected error occurred. Please try again.";
        }
      } finally {
        this.loading = false;
      }
    },
    
    viewActivityDetails(activityId) {
      console.log('🔗 Navigating to activity details:', activityId);
      this.$router.push(`/student/activity/${activityId}`);
    },
    async startPracticeBooking() {
      console.log('🎯 Starting practice booking session');
      
      const confirmed = await this.modalStore.confirm({
        title: 'Start Practice Booking?',
        message: 'This will start a simulation where you can practice the booking flow without affecting real data. Any activity code you enter will be verified against your assignments.',
        confirmText: 'Start Simulation',
        cancelText: 'Maybe Later'
      });

      if (!confirmed) return;

      // Use the booking store
      const bookingStore = useBookingStore();
      
      // Enable practice mode
      bookingStore.setPracticeMode();
      
      console.log('✅ Practice mode enabled:', {
        isPractice: bookingStore.isPractice,
        hasActivityCodeValidation: bookingStore.hasActivityCodeValidation
      });
      
      this.notificationStore.success('Practice mode enabled. Happy booking!');
      
      // Redirect to home page to start booking
      this.$router.push('/');
    },

    async openComparisonModal(activity) {
      this.showComparison = true;
      this.comparisonActivity = activity;
      this.comparisonBooking = null;
      this.isLoadingBooking = true;
      this.comparisonError = null;

      try {
        console.log('🔍 Loading comparison data for activity:', activity.id);
        const data = await comparisonService.getComparisonData(activity.id, activity.confirmed_booking_id);
        
        if (data.success) {
          if (data.activity) this.comparisonActivity = data.activity;
          this.comparisonBooking = data.booking;
        } else {
          this.comparisonError = data.error || "Could not find booking data for this activity.";
        }
      } catch (error) {
        console.error("Error loading comparison data:", error);
        this.comparisonError = "Failed to connect to the server. Please try again later.";
      } finally {
        this.isLoadingBooking = false;
      }
    },
    
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen;
    },
    toggleDropdown() {
      this.dropdownOpen = !this.dropdownOpen;
    },
    handleLogout() {
      console.log('👋 User manually logging out');
      localStorage.clear();
      this.$router.push('/login');
    },
    goToHome() {
      this.activeTab = 'all';
    },
    getTabCount(tabName) {
      if (tabName === 'active') {
        return this.activities.filter(a => a.is_active === true).length;
      } else if (tabName === 'assigned') {
        return this.activities.filter(a => a.status === 'assigned').length;
      } else if (tabName === 'submitted') {
        return this.activities.filter(a => ['submitted', 'graded'].includes(a.status)).length;
      }
      
      return this.activities.length;
    },
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
  },
  mounted() {
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.relative')) {
        this.dropdownOpen = false;
      }
    });
  }
}
</script>