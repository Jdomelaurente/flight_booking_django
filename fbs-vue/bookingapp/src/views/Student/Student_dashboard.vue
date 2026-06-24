<template>
  <div class="flex-1 flex flex-col bg-gray-200">
    <!-- <div class="bg-white mx-3 sm:mx-6 mt-4 sm:mt-5 px-5 sm:px-8 py-8 sm:py-12 rounded-lg shadow-sm relative overflow-hidden">
 
      <div class="absolute -right-10 -top-10 w-40 h-40 bg-white/10 rounded-full blur-2xl"></div>
      <div class="absolute -left-10 -bottom-10 w-32 h-32 bg-pink-400/20 rounded-full blur-xl"></div>
      
      <div class="relative z-10">
        <h1 class="text-[#FF579A] text-xl sm:text-3xl font-light tracking-wide drop-shadow-sm">
          {{ sectionDisplayName }}
        </h1>
        <div class="flex flex-wrap items-center gap-4 mt-3">
          <p class="text-[#FF579A] text-sm font-medium flex items-center gap-1.5 bg-white/10 px-3 py-1 rounded-full border border-white/10 backdrop-blur-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            {{ filteredActivities.length }} {{ filteredActivities.length === 1 ? 'activity' : 'activities' }}
          </p>
          
       
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
    </div> -->

    <!-- TABS - Only show if section exists -->
    <div v-if="section" class="mx-3 sm:mx-6 mt-4 sm:mt-5 flex items-center justify-between border-b border-slate-200 pb-4">
      <div class="flex items-center gap-4">
        <!-- Main Filter Toggle -->
        <div class="relative">
          <button 
            @click="showTabDropdown = !showTabDropdown"
            class="flex items-center gap-3 bg-white px-5 sm:px-8 py-3 rounded-lg border border-slate-200 shadow-sm hover:border-[#FF579A] transition-all min-w-[200px] sm:min-w-[280px] group active:scale-[0.98]"
          >
            <div class="flex flex-col items-start text-left">
              <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest leading-none mb-1">Filter View</span>
              <span class="text-xs font-black text-slate-900 uppercase tracking-tight flex items-center gap-2">
                {{ activeTabLabel }}
                <span class="px-1.5 py-0.5 bg-[#FF579A] text-white rounded-lg text-[8px]">
                  {{ getTabCount(activeTab) }}
                </span>
              </span>
            </div>
            <div class="ml-auto flex items-center gap-3">
              <div class="w-[1px] h-6 bg-slate-100"></div>
              <i class="ph ph-caret-down text-slate-400 group-hover:text-[#FF579A] transition-transform duration-300" :class="{ 'rotate-180': showTabDropdown }"></i>
            </div>
          </button>

          <!-- Premium Dropdown Menu -->
          <div 
            v-if="showTabDropdown"
            class="absolute top-full left-0 mt-2 w-full bg-white rounded-lg shadow-2xl border border-slate-100 z-[100] overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200"
          >
            <div class="py-1">
              <button 
                v-for="tab in tabs" 
                :key="tab.name"
                @click="selectTab(tab.name)"
                :class="[
                  'w-full flex items-center justify-between px-6 py-4 text-left transition-all group/opt',
                  activeTab === tab.name ? 'bg-pink-50/50' : 'bg-transparent hover:bg-slate-50'
                ]"
              >
                <div class="flex items-center gap-3">
                  <div 
                    :class="[
                      'w-1.5 h-1.5 rounded-full transition-all duration-300',
                      activeTab === tab.name ? 'bg-[#FF579A] scale-125' : 'bg-slate-200 group-hover/opt:bg-slate-300'
                    ]"
                  ></div>
                  <span :class="[
                    'text-[10px] font-black uppercase tracking-widest transition-colors',
                    activeTab === tab.name ? 'text-[#FF579A]' : 'text-slate-600 group-hover/opt:text-slate-900'
                  ]">
                    {{ tab.label }}
                  </span>
                </div>
                <span :class="[
                  'px-1.5 py-0.5 rounded-lg text-[8px] font-bold transition-colors',
                  activeTab === tab.name ? 'bg-[#FF579A] text-white' : 'bg-slate-100 text-slate-400 group-hover/opt:bg-slate-200 group-hover/opt:text-slate-600'
                ]">
                  {{ getTabCount(tab.name) }}
                </span>
              </button>
            </div>
            
            <div class="p-3 bg-slate-50 border-t border-slate-100">
              <p class="text-[8px] text-center font-bold text-slate-400 uppercase tracking-widest">Select Category to Filter Results</p>
            </div>
          </div>
        </div>

        <!-- Class Registry Button (Stand-alone) -->
        <button 
          @click="activeTab = 'classmates'"
          :class="[
            'hidden sm:flex items-center gap-3 px-6 py-3 rounded-lg border transition-all min-w-[200px] group active:scale-[0.98]',
            activeTab === 'classmates' 
              ? 'bg-gray-900 border-gray-900 text-white shadow-lg' 
              : 'bg-white border-slate-200 text-slate-900 hover:border-[#FF579A] shadow-sm'
          ]"
        >
          <div class="flex flex-col items-start text-left">
            <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest leading-none mb-1">Explore Members</span>
            <span class="text-xs font-black uppercase tracking-tight flex items-center gap-2">
              Class Registry
              <span :class="[
                'px-1.5 py-0.5 rounded-lg text-[8px]',
                activeTab === 'classmates' ? 'bg-[#FF579A] text-white' : 'bg-slate-100 text-slate-400'
              ]">
                {{ getTabCount('classmates') }}
              </span>
            </span>
          </div>
          <i class="ph ph-users-three ml-auto text-xl" :class="activeTab === 'classmates' ? 'text-white' : 'text-slate-400 group-hover:text-[#FF579A]'"></i>
        </button>
      </div>
      
      <!-- Desktop Section Display -->
      <div class="hidden md:flex items-center gap-2 px-4 py-2 border border-b-0 border-slate-100 bg-white rounded-t-sm ml-4 shadow-sm">
        <div class="w-1.5 h-1.5 rounded-full bg-[#FF579A] animate-pulse"></div>
        <span class="text-[10px] font-black text-[#FF579A] uppercase tracking-widest">{{ sectionDisplayName }}</span>
      </div>
    </div>

    <!-- CONTENT AREA -->
    <div :class="[
      'px-4 sm:px-6 py-4 sm:py-6 mx-3 sm:mx-6 mb-4 sm:mb-6',
      section ? 'bg-transparent' : 'bg-transparent'
    ]">
      <!-- Performance Hub (Desktop) -->
      <PerformanceAnalytics v-if="section && activeTab === 'all'" class="hidden lg:grid" :activities="activities" />

      <!-- Content when section exists -->
      <div v-if="section" class="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-8">
        <!-- Dashboard Toolbar for Mobile -->
        <div class="lg:hidden grid grid-cols-2 gap-3 mb-6">
          <button 
            @click="showSimulationModal = true"
            class="w-full bg-gray-900 text-white py-5 px-6 rounded-lg shadow-xl font-bold flex flex-col items-center justify-center group active:scale-[0.98] transition-all relative overflow-hidden border border-white/10"
          >
            <div class="absolute right-0 top-0 w-16 h-16 bg-white/5 rounded-full -mr-8 -mt-8 blur-xl"></div>
            <div class="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center mb-3">
              <i class="ph ph-terminal-window text-xl"></i>
            </div>
            <span class="text-[10px] font-black uppercase tracking-widest text-center">Training Hub</span>
          </button>

          <button 
            @click="showPerformanceModal = true"
            class="w-full bg-white text-slate-900 py-5 px-6 rounded-lg shadow-xl font-bold flex flex-col items-center justify-center group active:scale-[0.98] transition-all relative overflow-hidden border border-slate-100"
          >
             <div class="w-10 h-10 bg-pink-50 text-[#FF579A] rounded-lg flex items-center justify-center mb-3 border border-pink-100">
              <i class="ph ph-chart-line-up text-xl"></i>
            </div>
            <span class="text-[10px] font-black uppercase tracking-widest text-center">Performance</span>
          </button>
        </div>

        <!-- LEFT PANEL -->
        <div class="flex flex-col gap-4">
          <UpcomingDeadlines 
            :deadlines="upcomingDeadlines" 
            @view="viewActivityDetails" 
          />

          <!-- Consolidated Simulation Console Button -->
          <div class="hidden lg:block bg-gray-900 rounded-lg p-6 text-white shadow-lg transition-all relative overflow-hidden group cursor-pointer border border-white/10" @click="showSimulationModal = true">
            <div class="absolute -right-6 -top-6 w-32 h-32 bg-white/10 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700"></div>
            
            <div class="relative z-10">
              <div class="flex items-center gap-3 mb-6">
                <div class="w-12 h-12 bg-white/10 rounded-lg flex items-center justify-center backdrop-blur-md shadow-inner border border-white/10">
                  <i class="ph ph-terminal-window text-2xl"></i>
                </div>
                <div>
                  <h3 class="text-xs font-black uppercase tracking-widest poppins leading-none mb-1 text-white">Training Hub</h3>
                  <p class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Flight Simulation Console</p>
                </div>
              </div>
              


              <button 
                class="w-full bg-white text-gray-900 py-4 rounded-lg text-[10px] font-black cursor-pointer uppercase tracking-[0.2em] hover:bg-slate-50 transition-all active:scale-[0.97] shadow-xl flex items-center justify-center gap-3 group/btn border border-transparent"
              >
                Access Portal
                <i class="ph ph-arrow-square-out text-lg transition-transform group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5"></i>
              </button>
            </div>
          </div>

        </div>

        <!-- RIGHT PANEL - Activities or Classmates -->
        <div class="flex flex-col gap-3">
          <p class="text-slate-500  font-bold text-[10px] uppercase tracking-widest">Activities</p>
          <!-- Activities View -->
          <template v-if="activeTab !== 'classmates'">
            <TransitionGroup name="list" tag="div" class="space-y-4">
              <ActivityCard 
                v-if="filteredActivities.length > 0"
                v-for="activity in filteredActivities" 
                :key="activity.id"
                :activity="activity"
                @view="viewActivityDetails"
                @compare="openComparisonModal"
              />
            </TransitionGroup>
            <div v-if="filteredActivities.length === 0" class="bg-white border-2 border-dashed border-slate-200 rounded-lg p-12 text-center shadow-sm">
              <div class="w-16 h-16 bg-slate-50 rounded-lg flex items-center justify-center mx-auto mb-4 border border-slate-100 text-slate-300 text-2xl">
                <i class="ph ph-clipboard-text"></i>
              </div>
              <p class="text-slate-500 font-black text-[10px] uppercase tracking-widest">No activities found in this category</p>
            </div>
          </template>

          <!-- Classmates View -->
          <template v-if="activeTab === 'classmates'">
            <div class="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
              <div class="p-4 sm:p-6 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
                <div>
                  <h3 class="text-sm font-black text-slate-900 uppercase tracking-tight">Class Registry</h3>
                  <p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Instructor + {{ classmates.length }} Students Enrolled</p>
                </div>
                <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center text-[#FF579A] border border-pink-100 shadow-sm">
                  <i class="ph ph-users-three text-xl"></i>
                </div>
              </div>
              
              <div class="divide-y divide-slate-100 p-0">
                <!-- Instructor Card -->
                <div v-if="instructor" class="p-4 sm:p-5 flex items-center gap-4 bg-pink-50/30">
                  <div class="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold shrink-0 shadow-sm bg-gray-900 relative">
                    <div class="absolute -bottom-1 -right-1 w-4 h-4 bg-[#FF579A] rounded-full border-2 border-white flex items-center justify-center text-[8px]">
                      <i class="ph-fill ph-star"></i>
                    </div>
                    {{ instructor.first_name ? instructor.first_name.charAt(0) : '?' }}{{ instructor.last_name ? instructor.last_name.charAt(0) : '' }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <h4 class="text-sm font-black text-gray-900 truncate">{{ instructor.last_name }}, {{ instructor.first_name }} <span class="ml-2 px-1.5 py-0.5 rounded-lg bg-[#FF579A] text-white text-[8px] uppercase tracking-widest align-middle">Instructor</span></h4>
                    <div class="flex items-center gap-3 mt-1">
                      <span class="text-[10px] text-slate-500 font-bold uppercase tracking-widest flex items-center gap-1">
                        <i class="ph ph-chalkboard-teacher"></i> Course Instructor
                      </span>
                    </div>
                  </div>
                  <div class="hidden sm:block">
                    <a :href="`mailto:${instructor.email}`" class="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-500 hover:bg-[#FF579A] hover:text-white transition-colors">
                       <i class="ph ph-envelope-simple text-lg"></i>
                    </a>
                  </div>
                </div>

                <!-- Students List -->
                <div v-for="student in classmates" :key="student.student_number" class="p-4 sm:p-5 flex items-center gap-4 hover:bg-slate-50 transition-colors">
                  <div class="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold shrink-0 shadow-sm" :class="student.gender === 'female' ? 'bg-[#FF579A]' : 'bg-[#0E8028]'">
                    {{ student.first_name ? student.first_name.charAt(0) : '?' }}{{ student.last_name ? student.last_name.charAt(0) : '' }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <h4 class="text-sm font-black text-slate-900 truncate">
                      {{ student.last_name }}, {{ student.first_name }}
                      <span v-if="student.student_number === userStore.studentProfile?.student_number" class="ml-2 px-1.5 py-0.5 rounded-lg bg-slate-200 text-slate-600 text-[8px] uppercase tracking-widest align-middle">You</span>
                    </h4>
                    <div class="flex items-center gap-3 mt-1">
                      <span class="text-[10px] text-slate-500 font-bold uppercase tracking-widest flex items-center gap-1">
                        <i class="ph ph-identification-card"></i> {{ student.student_number }}
                      </span>
                    </div>
                  </div>
                  <div class="hidden sm:block">
                    <a :href="`mailto:${student.email}`" class="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-500 hover:bg-[#FF579A] hover:text-white transition-colors">
                       <i class="ph ph-envelope-simple text-lg"></i>
                    </a>
                  </div>
                </div>
                
                <div v-if="classmates.length === 0" class="p-12 text-center">
                  <div class="w-16 h-16 bg-slate-50 rounded-lg flex items-center justify-center mx-auto mb-4 border border-slate-100 text-slate-300 text-2xl">
                    <i class="ph ph-users-slash"></i>
                  </div>
                  <p class="text-slate-500 font-black text-[10px] uppercase tracking-widest">No students enrolled in this section yet</p>
                </div>
              </div>
            </div>
          </template>
        </div>
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

    <!-- Simulation Console Modal (Mobile Only) -->
    <Transition name="fade">
      <div v-if="showSimulationModal" class="fixed inset-0 z-[100] flex items-end sm:items-center justify-center p-0 sm:p-4">
        <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="showSimulationModal = false"></div>
        
        <Transition name="slide-up">
          <div v-if="showSimulationModal" class="relative w-full max-w-md bg-white rounded-t-xl sm:rounded-lg shadow-2xl overflow-hidden">
            <!-- Modal Header -->
            <div class="px-6 py-6 border-b border-white/10 flex items-center justify-between bg-gray-900 relative overflow-hidden">
              <div class="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -mr-16 -mt-16 blur-3xl"></div>
              <div class="relative z-10">
                <h3 class="text-lg font-black text-white poppins uppercase tracking-tight">Simulation Console</h3>
                <p class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Unified Training Environment</p>
              </div>
              <button @click="showSimulationModal = false" class="relative z-10 w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center text-slate-300 hover:text-white transition-all border border-white/10">
                <i class="ph ph-x text-xl"></i>
              </button>
            </div>

            <!-- Modal Content -->
            <div class="p-6 space-y-5 max-h-[70vh] overflow-y-auto no-scrollbar">
              <!-- Primary Actions Section -->
              <div>
                <p class="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-4 px-1">Simulation Modules</p>
                  <div class="grid grid-cols-1 gap-3">
                     <button 
                        @click="startPracticeBooking(); showSimulationModal = false"
                        class="flex items-center cursor-pointer gap-4 p-5 bg-gray-50 rounded-lg border border-slate-200 text-left hover:bg-slate-100 transition-all group relative overflow-hidden"
                     >
                        <div class="w-12 h-12 bg-gray-900 rounded-lg flex items-center justify-center text-white shadow-lg group-hover:scale-105 transition-transform">
                          <i class="ph ph-airplane text-2xl"></i>
                        </div>
                        <div class="relative z-10">
                          <span class="block text-xs font-black text-slate-900 uppercase tracking-tight">Practice Booking</span>
                          <span class="block text-[9px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">Global Reservation Training</span>
                        </div>
                     </button>
  

                  </div>
              </div>

              <!-- Logs & Registry Section -->
              <div class="mt-8 border-t border-slate-50 pt-8">
                <p class="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-4 px-1">Registry Access</p>
                  <div class="grid grid-cols-2 gap-3">
                     <button 
                        @click="$router.push('/student/booking-registry'); showSimulationModal = false"
                        class="flex flex-col gap-3 p-5 bg-gray-50 rounded-lg border border-slate-200 text-left hover:bg-slate-100 transition-all group relative overflow-hidden"
                     >
                        <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center text-slate-900 border border-slate-100 shadow-sm group-hover:scale-105 transition-transform">
                          <i class="ph ph-address-book text-xl"></i>
                        </div>
                        <div>
                          <span class="block text-[10px] font-black text-slate-900 uppercase tracking-tight poppins">Booking Registry</span>
                          <span class="block text-[8px] text-slate-400 font-bold uppercase tracking-widest mt-0.5 poppins">PNR Manifests</span>
                        </div>
                     </button>

                     <button 
                        @click="$router.push('/student/checkin-registry'); showSimulationModal = false"
                        class="flex flex-col gap-3 p-5 bg-gray-50 rounded-lg border border-slate-200 text-left hover:bg-slate-100 transition-all group relative overflow-hidden"
                     >
                        <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center text-slate-900 border border-slate-100 shadow-sm group-hover:scale-105 transition-transform">
                          <i class="ph ph-monitor text-xl"></i>
                        </div>
                        <div>
                          <span class="block text-[10px] font-black text-slate-900 uppercase tracking-tight poppins">DCS Registry</span>
                          <span class="block text-[8px] text-slate-400 font-bold uppercase tracking-widest mt-0.5 poppins">Ops Dashboard</span>
                        </div>
                     </button>
                  </div>
              </div>
            </div>

              <!-- Modal Footer -->
              <div class="p-4 bg-gray-50 flex justify-center border-t border-slate-100 shrink-0">
                <p class="text-[9px] text-gray-400 font-medium uppercase tracking-widest">Aviation Training System v2.0</p>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>

    <!-- Performance Modal (Mobile Only) -->
    <Transition name="fade">
      <div v-if="showPerformanceModal" class="fixed inset-0 z-[100] flex items-end sm:items-center justify-center p-0 lg:hidden">
        <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="showPerformanceModal = false"></div>
        
        <Transition name="slide-up">
          <div v-if="showPerformanceModal" class="relative w-full max-w-2xl bg-white rounded-t-xl sm:rounded-lg shadow-2xl overflow-hidden h-[90vh] flex flex-col">
            <!-- Modal Header -->
            <div class="px-6 py-6 border-b border-slate-100 flex items-center justify-between bg-white shrink-0">
              <div>
                <h3 class="text-lg font-black text-slate-900 uppercase tracking-tight">Academic Analytics</h3>
                <p class="text-[9px] text-[#FF579A] font-bold uppercase tracking-widest">Performance Insights</p>
              </div>
              <button @click="showPerformanceModal = false" class="w-10 h-10 rounded-lg bg-slate-50 flex items-center justify-center text-slate-400 hover:text-slate-900 transition-all border border-slate-100">
                <i class="ph ph-x text-xl"></i>
              </button>
            </div>

            <!-- Modal Content -->
            <div class="p-4 overflow-y-auto no-scrollbar flex-1">
               <PerformanceAnalytics :activities="activities" />
            </div>
            
            <div class="p-4 bg-slate-50 border-t border-slate-100 shrink-0 text-center">
               <p class="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Global Academic Tracker</p>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>

  </div>
</template>

<script>
import ComparisonModal from '@/components/common/ComparisonModal.vue';
import UpcomingDeadlines from '@/components/Student/UpcomingDeadlines.vue';
import ActivityCard from '@/components/Student/ActivityCard.vue';
import PerformanceAnalytics from '@/components/Student/PerformanceAnalytics.vue';
import { comparisonService } from '@/services/Student/comparisonService';
import { useUserStore } from '@/stores/user'
import { useModalStore } from '@/stores/modal'
import { useNotificationStore } from '@/stores/notification'
import { useBookingStore } from '@/stores/booking'

export default {
  name: 'StudentDashboard',
  props: {
    section: Object,
    activities: {
      type: Array,
      default: () => []
    },
    classmates: {
      type: Array,
      default: () => []
    },
    instructor: {
      type: Object,
      default: () => null
    }
  },
  setup() {
    const userStore = useUserStore()
    const modalStore = useModalStore()
    const notificationStore = useNotificationStore()
    const bookingStore = useBookingStore()
    return { userStore, modalStore, notificationStore, bookingStore }
  },
  components: {
    ComparisonModal,
    UpcomingDeadlines,
    ActivityCard,
    PerformanceAnalytics
  },
  data() {
    return {
      activeTab: 'all',
      tabs: [
        { name: 'all', label: 'All Activities' },
        { name: 'active', label: 'Active' },
        { name: 'missing', label: 'Missing' },
        { name: 'submitted', label: 'Submitted' },
        { name: 'graded', label: 'Graded' }
      ],
      showComparison: false,
      showSimulationModal: false,
      showPerformanceModal: false,
      comparisonActivity: null,
      comparisonBooking: null,
      isLoadingBooking: false,
      comparisonError: null,
      showTabDropdown: false
    }
  },
  computed: {
    activeTabLabel() {
      return this.tabs.find(t => t.name === this.activeTab)?.label || 'All Activities';
    },
    sectionDisplayName() {
      if (!this.section) return 'No section enrolled';
      return `${this.section.section_code} - ${this.section.section_name}`;
    },
    filteredActivities() {
      let filtered = this.activities;
      if (this.activeTab === 'active') {
        filtered = filtered.filter(a => a.is_active && !['submitted', 'graded', 'unassigned'].includes(a.status) && !this.checkIsOverdue(a));
      } else if (this.activeTab === 'missing') {
        filtered = filtered.filter(a => this.checkIsOverdue(a) || a.status === 'unassigned');
      } else if (this.activeTab === 'submitted') {
        filtered = filtered.filter(a => a.status === 'submitted');
      } else if (this.activeTab === 'graded') {
        filtered = filtered.filter(a => a.status === 'graded');
      }
      return filtered;
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
    selectTab(tabName) {
      this.activeTab = tabName;
      this.showTabDropdown = false;
    },
    viewActivityDetails(activityId) {
      this.$router.push(`/student/activity/${activityId}`);
    },
    startPracticeBooking() {
      this.bookingStore.resetBooking();
      this.bookingStore.setPracticeMode();
      this.notificationStore.success('Practice mode enabled. Happy booking!');
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
          this.comparisonError = data.error || "Could not find booking data.";
        }
      } catch (error) {
        this.comparisonError = "Failed to connect to the server.";
      } finally {
        this.isLoadingBooking = false;
      }
    },
    getTabCount(tabName) {
      if (tabName === 'active') return this.activities.filter(a => a.is_active && !['submitted', 'graded', 'unassigned'].includes(a.status) && !this.checkIsOverdue(a)).length;
      if (tabName === 'missing') return this.activities.filter(a => this.checkIsOverdue(a) || a.status === 'unassigned').length;
      if (tabName === 'submitted') return this.activities.filter(a => a.status === 'submitted').length;
      if (tabName === 'graded') return this.activities.filter(a => a.status === 'graded').length;
      if (tabName === 'classmates') return this.classmates.length + (this.instructor ? 1 : 0);
      return this.activities.length;
    },
    checkIsOverdue(activity) {
      if (!activity.due_date) return false;
      const now = new Date();
      const dueDate = new Date(activity.due_date);
      if (typeof activity.due_date === 'string' && activity.due_date.length <= 10) {
        dueDate.setHours(23, 59, 59, 999);
      }
      return now > dueDate && !activity.completed && activity.status !== 'submitted' && activity.status !== 'graded';
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

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

@keyframes slide-up {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.animate-slide-up {
  animation: slide-up 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

/* Vue Transitions */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active, .slide-up-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-enter-from, .slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
@media (min-width: 640px) {
  .slide-up-enter-from, .slide-up-leave-to {
    transform: scale(0.95);
    opacity: 0;
  }
}

/* List Transitions */
.list-enter-active, .list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from, .list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
.list-move {
  transition: transform 0.4s ease;
}
</style>
