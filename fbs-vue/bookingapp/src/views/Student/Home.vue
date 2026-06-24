<template>
  <div class="flex-1 flex flex-col overflow-y-auto bg-gray-200">
    <!-- Header Hero -->
    <div class="bg-pink-500 mx-6 mt-5 px-8 py-12 rounded-lg shadow-lg relative overflow-hidden">
      <!-- Background decoration -->
      <div class="absolute -right-10 -top-10 w-40 h-40 bg-white/10 rounded-full blur-2xl"></div>
      <div class="absolute -left-10 -bottom-10 w-32 h-32 bg-pink-400/20 rounded-full blur-xl"></div>
      
      <div class="relative z-10">
        <h1 class="text-white text-3xl font-light tracking-wide drop-shadow-sm">
          {{ sectionDisplayName }}
        </h1>
        <div class="flex flex-wrap items-center gap-4 mt-3">
          <p class="text-white/90 text-sm font-medium flex items-center gap-1.5 bg-white/10 px-3 py-1 rounded-full border border-white/10 backdrop-blur-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            {{ filteredActivities.length }} {{ filteredActivities.length === 1 ? 'activity' : 'activities' }}
          </p>
          
          <!-- Schedule Display -->
          <div v-if="section" class="flex flex-wrap gap-2">
            <template v-if="parsedSchedules.length > 0">
              <div v-for="(s, i) in parsedSchedules" :key="i" class="text-white/90 text-[11px] font-bold flex items-center gap-1.5 bg-pink-600/30 px-3 py-1 rounded-full border border-white/10 backdrop-blur-sm">
                <span class="opacity-70 uppercase">{{ s.day.substring(0, 3) }}</span>
                <span>{{ formatTimeOnly(s.start_time) }} - {{ formatTimeOnly(s.end_time) }}</span>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- TABS -->
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
      <div v-if="section" class="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-6">
        <!-- LEFT PANEL -->
        <div class="flex flex-col gap-4">
          <UpcomingDeadlines 
            :deadlines="upcomingDeadlines" 
            @view="viewActivityDetails" 
          />

          <!-- Practice Booking -->
          <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg hover:shadow-xl transition-all border border-white/10">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center text-xl">🚀</div>
              <h3 class="text-sm font-black uppercase tracking-widest">Practice Lab</h3>
            </div>
            <p class="text-[10px] font-medium leading-relaxed opacity-80 mb-6">Experience the complete booking lifecycle in a risk-free simulator. No grades affected.</p>
            <button 
              @click="startPracticeBooking"
              class="w-full bg-white text-blue-600 py-3 rounded-xl text-[10px] font-black uppercase tracking-[0.1em] hover:bg-blue-50 transition-colors shadow-sm"
            >
              Initialize Simulation
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
          <ActivityCard 
            v-if="filteredActivities.length > 0"
            v-for="activity in filteredActivities" 
            :key="activity.id"
            :activity="activity"
            @view="viewActivityDetails"
            @compare="openComparisonModal"
          />
          <div v-else class="bg-gray-50 border-2 border-dashed border-gray-200 rounded-[32px] p-20 text-center flex flex-col items-center">
            <div class="text-4xl mb-4 grayscale opacity-20">📂</div>
            <h4 class="text-sm font-black text-gray-800 uppercase tracking-widest mb-1">No Entries Found</h4>
            <p class="text-xs text-gray-400 font-medium">There are no records matching the selected filter.</p>
          </div>
        </div>
      </div>
      
      <div v-else class="flex flex-col items-center justify-center min-h-[400px]">
        <div class="w-20 h-20 bg-white rounded-3xl shadow-sm border border-gray-100 flex items-center justify-center text-3xl mb-6 opacity-30 grayscale">
          🎓
        </div>
        <h2 class="text-2xl font-black text-gray-800 uppercase tracking-widest mb-2">No Active Enrollment</h2>
        <p class="text-gray-400 font-medium text-sm">You haven't been assigned to a section yet. Contact your instructor.</p>
      </div>
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
import { useUserStore } from '@/stores/user'
import { useModalStore } from '@/stores/modal'
import { useNotificationStore } from '@/stores/notification'
import { useBookingStore } from '@/stores/booking'
import ComparisonModal from '@/components/common/ComparisonModal.vue'
import UpcomingDeadlines from '@/components/Student/UpcomingDeadlines.vue'
import StudentSectionInfo from '@/components/Student/StudentSectionInfo.vue'
import ActivityCard from '@/components/Student/ActivityCard.vue'
import { comparisonService } from '@/services/Student/comparisonService'

export default {
  name: 'StudentHome',
  components: {
    ComparisonModal,
    UpcomingDeadlines,
    StudentSectionInfo,
    ActivityCard
  },
  props: {
    section: Object,
    activities: {
      type: Array,
      default: () => []
    }
  },
  setup() {
    const userStore = useUserStore()
    const modalStore = useModalStore()
    const notificationStore = useNotificationStore()
    const bookingStore = useBookingStore()
    return { userStore, modalStore, notificationStore, bookingStore }
  },
  data() {
    return {
      activeTab: 'all',
      tabs: [
        { name: 'all', label: 'All Activities' },
        { name: 'active', label: 'Active' },
        { name: 'assigned', label: 'Assigned' },
        { name: 'submitted', label: 'Submitted' }
      ],
      showComparison: false,
      comparisonActivity: null,
      comparisonBooking: null,
      isLoadingBooking: false,
      comparisonError: null
    }
  },
  computed: {
    sectionDisplayName() {
      if (!this.section) return 'Academic Overview';
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
        .filter(a => a.due_date && a.is_active && !a.completed && !['submitted', 'graded'].includes(a.status))
        .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
        .slice(0, 5);
    },
    parsedSchedules() {
      if (!this.section?.schedule) return []
      try {
        const schedules = typeof this.section.schedule === 'string' ? JSON.parse(this.section.schedule) : this.section.schedule
        if (Array.isArray(schedules)) return schedules
      } catch (e) {}
      return []
    }
  },
  methods: {
    viewActivityDetails(activityId) {
      this.$router.push(`/student/activity/${activityId}`);
    },
    async startPracticeBooking() {
      const confirmed = await this.modalStore.confirm({
        title: 'Initialize Practice Lab?',
        message: 'This will launch a risk-free booking environment for performance training.',
        confirmText: 'Start Training',
        cancelText: 'Cancel'
      });
      if (!confirmed) return;
      this.bookingStore.resetBooking();
      this.bookingStore.setPracticeMode();
      this.notificationStore.success('Practice mode initialized.');
      this.$router.push('/');
    },
    async openComparisonModal(activity) {
      this.showComparison = true;
      this.comparisonActivity = activity;
      this.comparisonBooking = null;
      this.isLoadingBooking = true;
      this.comparisonError = null;

      try {
        const data = await comparisonService.getComparisonData(activity.id, activity.confirmed_booking_id);
        if (data.success) {
          if (data.activity) this.comparisonActivity = data.activity;
          this.comparisonBooking = data.booking;
        } else {
          this.comparisonError = data.error || "Booking results unavailable.";
        }
      } catch (error) {
        this.comparisonError = "Network error during data retrieval.";
      } finally {
        this.isLoadingBooking = false;
      }
    },
    getTabCount(tabName) {
      if (tabName === 'active') return this.activeActivitiesCount;
      if (tabName === 'assigned') return this.activities.filter(a => a.status === 'assigned').length;
      if (tabName === 'submitted') return this.activities.filter(a => ['submitted', 'graded'].includes(a.status)).length;
      return this.activities.length;
    },
    formatTimeOnly(t) {
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
