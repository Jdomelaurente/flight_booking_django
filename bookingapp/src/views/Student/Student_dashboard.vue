<template>
  <div class="flex flex-col h-screen bg-gray-50">
    <!-- TOP HEADER -->
    <DashboardHeader 
      :student="student" 
      @toggle-sidebar="toggleSidebar" 
      @logout="handleLogout" 
    />

    <!-- MAIN CONTENT WITH SIDEBAR -->
    <div class="flex flex-1 overflow-hidden">
      <!-- LEFT SIDEBAR -->
      <DashboardSidebar 
        :sidebar-open="sidebarOpen" 
        :section="section" 
        @go-home="goToHome" 
      />

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
              <UpcomingDeadlines 
                :deadlines="upcomingDeadlines" 
                @view="viewActivityDetails" 
              />

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
                <button 
                  @click="openPracticeBookings"
                  class="w-full mt-2 bg-white text-blue-600 px-4 py-2.5 rounded-lg text-sm font-semibold hover:bg-blue-50 transition-colors shadow-sm"
                >
                  View Practice Bookings
                </button>
              </div>

              <StudentSectionInfo 
                :section="section" 
                :total-activities="activities.length" 
                :active-activities="activeActivitiesCount" 
              />
            </div>
            

            <!-- RIGHT PANEL - Activities -->
            <div class="flex flex-col gap-5">
              <!-- Activities List -->
              <ActivityCard 
                v-if="filteredActivities.length > 0"
                v-for="activity in filteredActivities" 
                :key="activity.id"
                :activity="activity"
                @view="viewActivityDetails"
                @compare="openComparisonModal"
              />

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
    <!-- Practice Bookings Modal -->
    <BaseModal 
      :is-open="showPracticeBookings" 
      @close="showPracticeBookings = false"
    >
      <div class="flex flex-col h-[500px] max-h-[80vh]">
        <!-- Modal Header -->
        <div class="px-6 py-4 border-b flex justify-between items-center bg-gray-50 flex-shrink-0">
          <div class="flex items-center gap-2">
            <span class="text-xl">📋</span>
            <h3 class="text-lg font-bold text-gray-900">Practice Bookings History</h3>
          </div>
          <button 
            @click="showPracticeBookings = false" 
            class="p-2 hover:bg-gray-200 rounded-full transition-colors text-gray-500 hover:text-gray-700"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Modal Body -->
        <div class="p-6 overflow-y-auto flex-1 bg-white">
          <div v-if="practiceBookings.length === 0" class="flex flex-col items-center justify-center py-20 text-center">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center text-3xl mb-4 grayscale opacity-50">
              ✈️
            </div>
            <p class="text-gray-500 font-medium">No practice bookings found.</p>
            <p class="text-sm text-gray-400 mt-1">Start a practice booking to see your results here!</p>
          </div>
          
          <ul v-else class="space-y-4">
            <li 
              v-for="booking in practiceBookings" 
              :key="booking.id" 
              class="border border-gray-100 rounded-xl p-4 hover:border-blue-200 hover:bg-blue-50/30 transition-all shadow-sm group"
            >
              <div class="flex justify-between items-start gap-4">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-xs font-mono font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded leading-none">
                      #{{ booking.id }}
                    </span>
                    <span class="text-xs text-gray-400">
                      {{ formatDate(booking.created_at) }}
                    </span>
                  </div>
                  <h4 class="font-bold text-gray-900 mb-1 group-hover:text-blue-700 transition-colors">
                    {{ booking.route_summary }}
                  </h4>
                  <div class="flex flex-wrap gap-x-4 gap-y-1 mt-2">
                    <div class="flex items-center gap-1.5 text-xs text-gray-500">
                      <span class="opacity-70">📅</span>
                      {{ formatDate(booking.departure_date) }}
                    </div>
                    <div class="flex items-center gap-1.5 text-xs text-gray-500">
                      <span class="opacity-70">👤</span>
                      {{ booking.passenger_count }} Passenger{{ booking.passenger_count !== 1 ? 's' : '' }}
                    </div>
                  </div>
                </div>
                
                <div class="flex flex-col items-end gap-2">
                  <span 
                    :class="[
                      'px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider shadow-sm',
                      booking.ui_status === 'success' 
                        ? 'bg-green-100 text-green-700 border border-green-200' 
                        : booking.ui_status === 'fail' 
                          ? 'bg-red-100 text-red-700 border border-red-200' 
                          : 'bg-yellow-100 text-yellow-700 border border-yellow-200'
                    ]"
                  >
                    {{ booking.ui_status }}
                  </span>
                  <div class="text-sm font-bold text-gray-900">
                    ₱{{ parseFloat(booking.total_amount).toLocaleString() }}
                  </div>
                </div>
              </div>
            </li>
          </ul>
        </div>
        
        <!-- Modal Footer -->
        <div class="px-6 py-4 bg-gray-50 border-t flex justify-end flex-shrink-0">
          <button 
            @click="showPracticeBookings = false"
            class="px-5 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-colors shadow-sm text-sm"
          >
            Close History
          </button>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script>
import { studentDashboardService } from '@/services/Student/studentDashboardService.js';
import { useBookingStore } from '@/stores/booking';
import ComparisonModal from '@/components/common/ComparisonModal.vue';
import DashboardHeader from '@/components/Student/DashboardHeader.vue';
import DashboardSidebar from '@/components/Student/DashboardSidebar.vue';
import BaseModal from '@/components/common/BaseModal.vue';
import UpcomingDeadlines from '@/components/Student/UpcomingDeadlines.vue';
import StudentSectionInfo from '@/components/Student/StudentSectionInfo.vue';
import ActivityCard from '@/components/Student/ActivityCard.vue';
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
    ComparisonModal,
    DashboardHeader,
    DashboardSidebar,
    BaseModal,
    UpcomingDeadlines,
    StudentSectionInfo,
    ActivityCard
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
      comparisonError: null,
      showPracticeBookings: false,
      practiceBookings: []
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
          // Ensure practice bookings are cleared on reload
          this.practiceBookings = [];
        
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
          // Load practice bookings after dashboard data
          this.loadPracticeBookings();
          
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
      
      // Ensure everything is clean before starting
      bookingStore.resetBooking();
      
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

    async loadPracticeBookings() {
      try {
        const resp = await studentDashboardService.getPracticeBookings();
        this.practiceBookings = resp.data.practice_bookings || [];
        console.log('✅ Loaded practice bookings', this.practiceBookings);
      } catch (e) {
        console.error('Failed to load practice bookings', e);
        this.notificationStore.error('Could not load practice bookings');
      }
    },

    openPracticeBookings() {
      this.showPracticeBookings = true;
      if (this.practiceBookings.length === 0) {
        this.loadPracticeBookings();
      }
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