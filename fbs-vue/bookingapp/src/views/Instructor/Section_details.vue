<template>
  <div class="p-8 max-w-7xl mx-auto font-sans bg-[#F9FAFB] min-h-screen">
    <!-- Header/Breadcrumbs and Top Actions -->
    <div class="mb-6 flex justify-between items-start">
      <div>
        <div class="flex items-center gap-2 text-xs font-medium text-gray-400 mb-2">
          <router-link to="/instructor/dashboard" class="hover:text-pink-600 transition-colors">My Courses</router-link>
          <span class="text-gray-300">›</span>
          <span class="hover:text-pink-600 cursor-pointer transition-colors">CTHM</span>
          <span class="text-gray-300">›</span>
          <span class="text-pink-600 font-bold">Section {{ section?.section_code || 'QU1' }}</span>
        </div>
        <div class="flex items-center flex-wrap gap-3 mt-1">
          <h2 class="text-[22px] font-bold text-gray-800 tracking-tight">
            Course Section: {{ section?.section_name || 'EUQIO' }} - {{ section?.section_code || 'QU1' }}
          </h2>
        </div>
      </div>
      <div class="flex gap-3 bg-white">
        <button @click="openEnrollModal" class="flex items-center gap-2 border border-gray-200 text-gray-600 bg-white px-4 py-2 rounded-lg font-bold text-xs shadow-sm hover:bg-gray-50 transition-all">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
          </svg>
          Enroll Student
        </button>
        <button @click="openActivityModal" class="flex items-center gap-2 bg-[#E91E63] hover:bg-[#D81B60] text-white px-4 py-2 rounded-lg font-bold text-xs shadow-sm transition-all shadow-[#E91E63]/20">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 4v16m8-8H4" />
          </svg>
          Create Activity
        </button>
      </div>
    </div>

    <!-- Course Information Card -->
    <div class="bg-white border border-gray-100 rounded-xl p-6 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] mb-6 flex flex-wrap justify-between items-center gap-4">
      <div class="flex flex-wrap gap-12 sm:gap-16">
        <div>
          <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-1.5">Academic Year</p>
          <p class="text-[15px] font-bold text-gray-800">{{ section?.academic_year || 'N/A' }}</p>
        </div>
        <div>
          <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-1.5">Semester</p>
          <p class="text-[15px] font-bold text-gray-800">{{ section?.semester || 'N/A' }}</p>
        </div>
        <div>
          <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-1.5">Section</p>
          <p class="text-[15px] font-bold text-gray-800">{{ section?.section_code || 'N/A' }}</p>
        </div>
        <div>
          <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-1.5">Instructor</p>
          <p class="text-[15px] font-bold text-gray-800">{{ userFullName || 'Instructor' }}</p>
        </div>
      </div>
      <div>
        <span v-if="section?.is_active !== false" class="bg-[#E91E63] text-white px-5 py-1.5 rounded-lg text-xs font-bold shadow-sm inline-block tracking-wide">Active</span>
        <span v-else class="bg-red-500 text-white px-5 py-1.5 rounded-lg text-xs font-bold shadow-sm inline-block tracking-wide">Disabled</span>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white p-5 rounded-xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-gray-100 flex items-center gap-4">
        <div class="w-11 h-11 rounded-xl bg-pink-50 text-pink-400 flex items-center justify-center flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
        <div>
          <p class="text-xl font-bold text-gray-800 leading-none mb-1">{{ section?.student_count || 0 }}</p>
          <p class="text-[11px] text-gray-400 font-medium">Students Enrolled</p>
        </div>
      </div>
      <div class="bg-white p-5 rounded-xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-gray-100 flex items-center gap-4">
        <div class="w-11 h-11 rounded-xl bg-pink-50 text-pink-400 flex items-center justify-center flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div>
          <p class="text-xl font-bold text-gray-800 leading-none mb-1">{{ activities.length }}</p>
          <p class="text-[11px] text-gray-400 font-medium">Total Activities</p>
        </div>
      </div>
      <div class="bg-white p-5 rounded-xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-gray-100 flex items-center gap-4">
        <div class="w-11 h-11 rounded-xl bg-pink-50 text-pink-400 flex items-center justify-center flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div>
          <p class="text-xl font-bold text-gray-800 leading-none mb-1">{{ avgCompletionRate }}%</p>
          <p class="text-[11px] text-gray-400 font-medium">Avg. Completion</p>
        </div>
      </div>
      <div class="bg-white p-5 rounded-xl shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-gray-100 flex items-center gap-4">
        <div class="w-11 h-11 rounded-xl bg-pink-50 text-pink-400 flex items-center justify-center flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
          </svg>
        </div>
        <div>
          <p class="text-xl font-bold text-gray-800 leading-none mb-1">{{ submissionRate }}%</p>
          <p class="text-[11px] text-gray-400 font-medium">Submission Rate</p>
        </div>
      </div>
    </div>

    <!-- Tabs and Filters -->
    <div class="flex flex-col sm:flex-row justify-between sm:items-end border-b border-gray-200 mb-6 pb-0 gap-4">
      <div class="flex gap-8 px-2 overflow-x-auto">
        <button class="pb-3 px-1 text-[13px] font-bold border-b-[3px] border-[#E91E63] text-gray-900 tracking-wide whitespace-nowrap">Assessments</button>
        <button 
          @click="$router.push(`/instructor/section/${route.params.id}/student`)"
          class="pb-3 px-1 text-[13px] font-medium text-gray-400 hover:text-gray-600 tracking-wide transition-colors whitespace-nowrap"
        >
          Students
        </button>
        <button 
          @click="$router.push(`/instructor/section/${route.params.id}/settings`)"
          class="pb-3 px-1 text-[13px] font-medium text-gray-400 hover:text-gray-600 tracking-wide transition-colors whitespace-nowrap"
        >
          Settings
        </button>
      </div>
      <div class="flex gap-1 mb-2 bg-gray-50/80 p-1.5 rounded-xl border border-gray-100 flex-shrink-0">
        <button @click="activeFilter = 'All'" :class="activeFilter === 'All' ? 'bg-[#E91E63] text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200/50 transition-colors'" class="px-5 py-1.5 text-xs font-bold rounded-lg">All</button>
        <button @click="activeFilter = 'Active'" :class="activeFilter === 'Active' ? 'bg-[#E91E63] text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200/50 transition-colors'" class="px-5 py-1.5 text-xs font-semibold rounded-lg">Active</button>
        <button @click="activeFilter = 'Draft'" :class="activeFilter === 'Draft' ? 'bg-[#E91E63] text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-200/50 transition-colors'" class="px-5 py-1.5 text-xs font-semibold rounded-lg">Draft</button>
      </div>
    </div>

    <p class="text-xs text-gray-400 font-medium mb-6 px-1">Showing <strong>{{ filteredActivities.length }}</strong> activities</p>

    <!-- Activities Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-12">
      <!-- Activity Card -->
      <div 
        v-for="(activity, index) in filteredActivities" 
        :key="activity.id"
        @click="goToActivity(activity.id)"
        class="bg-white rounded-2xl border border-gray-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.05)] hover:shadow-lg transition-all flex flex-col pt-5 px-6 pb-6 cursor-pointer hover:border-pink-200 group"
      >
        <!-- Header -->
        <div class="flex justify-between items-center mb-5">
          <div class="flex items-center gap-2 text-[10px] font-bold text-gray-400 uppercase tracking-widest">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {{ activity.activity_type || 'ACTIVITY' }}
          </div>
          <div class="flex items-center gap-3">
            <span class="flex items-center gap-1.5 text-[11px] font-bold tracking-wide" :class="activity.is_code_active ? 'text-emerald-500' : 'text-amber-500'">
              <span class="w-1.5 h-1.5 rounded-full" :class="activity.is_code_active ? 'bg-emerald-500' : 'bg-amber-500'"></span> 
              {{ activity.is_code_active ? 'Active' : 'Draft' }} 
            </span>
            <div class="relative">
              <button @click.stop="toggleActivityDropdown(activity.id)" class="text-gray-400 hover:text-gray-800 transition-colors mt-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 8a1.5 1.5 0 110-3 1.5 1.5 0 010 3zm0 5.5a1.5 1.5 0 110-3 1.5 1.5 0 010 3zm0 5.5a1.5 1.5 0 110-3 1.5 1.5 0 010 3z" />
                </svg>
              </button>
              <!-- Dropdown Menu -->
              <div 
                v-if="activityDropdowns[activity.id]"
                class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-100"
              >
                <button 
                  v-if="!activity.is_code_active"
                  @click.stop="openEditActivity(activity)"
                  class="block w-full text-left px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 font-medium"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline-block mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                  Edit Activity
                </button>
                <button 
                  @click.stop="openDeleteModal(activity)"
                  class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 font-medium"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline-block mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                  Delete Activity
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Title & Due Date -->
        <h3 
          @click="goToActivity(activity.id)"
          class="text-[17px] font-bold text-gray-800 mb-2 leading-snug cursor-pointer hover:text-[#E91E63] transition-colors"
        >
          {{ activity.title }}
        </h3>
        <p class="text-xs text-gray-400/80 mb-4 flex items-center gap-1.5 font-medium">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          Due: {{ formatDate(activity.due_date) }}
        </p>

        <!-- Description -->
        <p class="text-gray-500 text-[13px] leading-relaxed line-clamp-2 mb-6 flex-grow">
          {{ activity.description || 'No description provided for this activity.' }}
        </p>

        <!-- Progress Bar -->
        <div class="mb-5">
          <div class="flex justify-between items-end text-[11px] font-bold mb-2">
            <span class="text-gray-400 tracking-wide">Submissions: <span class="text-gray-700 ml-1">{{ activity.total_submissions || 0 }} / {{ section?.student_count || 0 }}</span></span>
            <span class="text-[#E91E63] text-xs">{{ getActivityCompletionRate(activity) }}%</span>
          </div>
          <div class="h-1 bg-gray-100 rounded-full w-full overflow-hidden">
            <div class="h-full bg-[#E91E63] rounded-full transition-all duration-500" :style="{ width: getActivityCompletionRate(activity) + '%' }"></div>
          </div>
        </div>

        <!-- Bottom Actions -->
        <div class="flex justify-between items-center pt-4 border-t border-gray-100/60 mt-auto">
          <div class="flex items-center gap-2 text-[11px] text-gray-400 font-semibold tracking-wide">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            {{ section?.student_count || 0 }} students
          </div>
          <button 
            @click.stop="goToActivity(activity.id)"
            class="bg-[#E91E63] text-white px-6 py-1.5 rounded-lg text-xs font-bold shadow-sm shadow-[#E91E63]/20 hover:bg-[#D81B60] transition-colors"
          >
            Open
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="activities.length === 0" class="col-span-1 lg:col-span-2 bg-white rounded-2xl border border-gray-100 p-12 text-center shadow-[0_2px_12px_-4px_rgba(0,0,0,0.05)]">
        <div class="text-pink-100 mb-4 flex justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="text-lg font-bold text-gray-800 mb-2">No Activities Yet</h3>
        <p class="text-sm text-gray-500 mb-6">Get started by creating your first activity for this section.</p>
        <button 
          @click="openActivityModal"
          class="bg-[#E91E63] text-white px-6 py-2.5 rounded-lg font-bold text-sm shadow-sm hover:bg-[#D81B60] transition-colors inline-flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 4v16m8-8H4" /></svg>
          Create Activity
        </button>
      </div>
    </div>
  </div>

    <!-- Delete Confirmation Modal -->
    <Transition name="modal-fade">
      <div v-if="showDeleteModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-[60] backdrop-blur-sm">
        <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-md mx-4">
          <!-- Warning Icon -->
          <div class="flex justify-center mb-6">
            <div class="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
          
          <!-- Delete Confirmation -->
          <div class="text-center">
            <h3 class="text-2xl font-bold text-gray-800 mb-2">Delete Activity?</h3>
            <p class="text-gray-600 mb-4">
              Are you sure you want to delete <strong>"{{ activityToDelete?.title }}"</strong>?
            </p>
            <p class="text-sm text-red-600 mb-6">
              This action cannot be undone. All student submissions will also be deleted.
            </p>
          </div>
          
          <!-- Buttons -->
          <div class="flex gap-3">
            <button 
              @click="closeDeleteModal" 
              class="flex-1 px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors font-medium"
            >
              Cancel
            </button>
            <button 
              @click="confirmDeleteActivity" 
              :disabled="loading"
              class="flex-1 px-6 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors font-medium disabled:opacity-50"
            >
              <span v-if="loading">Deleting...</span>
              <span v-else>Delete</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Success Modal -->
    <Transition name="success-fade">
      <div v-if="showSuccessModal" class="fixed inset-0 flex items-center justify-center z-[100] bg-black/60 backdrop-blur-[2px]">
        <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-sm w-full mx-4 transform transition-all border border-green-100">
          <div class="flex justify-center mb-6">
            <div class="success-checkmark">
              <div class="check-icon">
                <span class="icon-line line-tip"></span>
                <span class="icon-line line-long"></span>
                <div class="icon-circle"></div>
                <div class="icon-fix"></div>
              </div>
            </div>
          </div>
          
          <div class="text-center">
            <h3 class="text-2xl font-bold text-gray-800 mb-2">Success!</h3>
            <p class="text-gray-600">{{ successMessage }}</p>
          </div>
          
          <div class="mt-6 flex justify-center">
            <button @click="showSuccessModal = false" 
              class="px-6 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors font-medium">
              Close
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Enroll Student Modal -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center backdrop-blur-sm bg-black/50">
      <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="bg-white p-6 text-black flex justify-between items-center">
          <h3 class="text-xl font-bold">Enroll Student</h3>
          <button @click="isModalOpen = false" class="hover:rotate-90 transition-transform">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-8">
          <div class="mb-6">
            <label class="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Enter Student Number</label>
            <input 
              v-model="studentNumberInput"
              type="text" 
              placeholder="e.g. 21-0001"
              class="w-full p-4 border-2 border-gray-100 rounded-xl focus:border-[#FF579A] outline-none transition-all text-lg font-medium"
            />
          </div>
          <div class="flex gap-4">
            <button @click="isModalOpen = false" class="flex-1 py-3 text-gray-400 font-bold hover:bg-gray-200 rounded-xl transition-colors uppercase text-xs">Cancel</button>
            <button @click="submitEnrollment" :disabled="loading" class="flex-1 py-3 bg-[#FF579A] text-white font-bold rounded-xl shadow-lg hover:bg-green-700 transition-colors uppercase text-xs">
              {{ loading ? 'Enrolling...' : 'Enroll Student' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  
   <!-- Add Activity Modal -->
    <!-- Add Activity Modal -->
    <div v-if="activityModalOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-[1px]">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
        <div class="bg-[#FF579A] px-6 py-4 flex justify-between items-center sticky top-0 z-10">
          <h2 class="text-xl font-semibold text-white">{{ isEditing ? 'Edit Activity' : 'Create New Activity' }}</h2>
          <button @click="closeActivityModal" class="text-black hover:text-yellow-300 text-2xl">
            &times;
          </button>
        </div>
        
        <div class="p-6">
          <form @submit.prevent="submitActivity">
            <div class="space-y-6">
              <!-- Basic Activity Information -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Activity Title *</label>
                  <input type="text" v-model="activityForm.title" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Activity Type *</label>
                  <input type="text" v-model="activityForm.activity_type" required 
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]"
                    placeholder="e.g., Flight Booking, Seat Selection, Payment Processing">
                </div>
                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Instructions *</label>
                  <textarea v-model="activityForm.instructions" required rows="4" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]"></textarea>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Due Date *</label>
                  <input type="datetime-local" v-model="activityForm.due_date" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Total Points</label>
                  <input type="number" v-model="activityForm.total_points" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]">
                </div>
              </div>

              <!-- Flight Requirements Section -->
              <div class="border-t border-gray-200 pt-4">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Flight Requirements</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Trip Type *</label>
                    <select v-model="activityForm.required_trip_type" @change="handleTripTypeChange" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]">
                      <option value="one_way">One Way</option>
                      <option value="round_trip">Round Trip</option>
                      <option value="multi_city">Multi City</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      Travel Class *
                      <span v-if="isFetchingTravelClasses" class="ml-2 text-xs text-blue-400 font-normal italic">Loading...</span>
                      <span v-else-if="(activityForm.required_origin && activityForm.required_destination && activityForm.required_departure_date || (activityForm.required_trip_type === 'multi_city' && activityForm.segments.length > 0)) && filteredTravelClasses.length === 0"
                        class="ml-2 text-xs text-orange-500 font-normal italic">
                        No available travel classes for this selection
                      </span>
                    </label>
                    <select v-model="activityForm.required_travel_class" required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]"
                      :disabled="isFetchingTravelClasses">
                      <!-- Filtered by route+date (preferred) -->
                      <template v-if="filteredTravelClasses.length > 0">
                        <option v-for="tClass in filteredTravelClasses" :key="tClass" :value="tClass">{{ tClass }}</option>
                      </template>
                      <!-- Fallback: all travel classes when no route/date is selected yet -->
                      <template v-else-if="travel_classes.length > 0">
                        <option v-for="tClass in travel_classes" :key="tClass" :value="tClass">{{ tClass }}</option>
                      </template>
                      <!-- Hard fallback -->
                      <template v-else>
                        <option value="economy">Economy</option>
                        <option value="premium_economy">Premium Economy</option>
                        <option value="business">Business</option>
                        <option value="first">First Class</option>
                      </template>
                    </select>
                  </div>

                  <div v-if="activityForm.required_travel_class">
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                      Ticket Bundle / Fare Type *
                    </label>
                    <select v-model="activityForm.required_seat_class" required 
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]"
                      :disabled="availableBundles.length === 0">
                      <option value="">{{ availableBundles.length === 0 ? 'Select Travel Class first' : 'Select Fare Type' }}</option>
                      <option v-for="bundle in availableBundles" :key="bundle" :value="bundle">{{ bundle }}</option>
                    </select>
                  </div>

                  <!-- Origin Airport Dropdown -->
                  <div v-if="activityForm.required_trip_type !== 'multi_city'">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Origin Airport *</label>
                    <select v-model="activityForm.required_origin" :required="activityForm.required_trip_type !== 'multi_city'" 
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]"
                      :disabled="airports.length === 0"
                      @change="fetchFilteredTravelClasses()">
                      <option value="">{{ airports.length === 0 ? 'Loading airports...' : 'Select Origin Airport' }}</option>
                      <option v-for="airport in airports" :key="airport.code" :value="airport.code">
                        {{ airport.code }} - {{ airport.name }}<template v-if="airport.location"> ({{ airport.location }})</template>
                      </option>
                    </select>
                    <p v-if="airports.length === 0" class="text-xs text-blue-500 mt-1">Loading airports...</p>
                  </div>

                  <!-- Destination Airport Dropdown -->
                  <div v-if="activityForm.required_trip_type !== 'multi_city'">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Destination Airport *</label>
                    <select v-model="activityForm.required_destination" :required="activityForm.required_trip_type !== 'multi_city'" 
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]"
                      :disabled="airports.length === 0"
                      @change="fetchFilteredTravelClasses()">
                      <option value="">{{ airports.length === 0 ? 'Loading airports...' : 'Select Destination Airport' }}</option>
                      <option v-for="airport in airports" :key="airport.code" :value="airport.code">
                        {{ airport.code }} - {{ airport.name }}<template v-if="airport.location"> ({{ airport.location }})</template>
                      </option>
                    </select>
                    <p v-if="airports.length === 0" class="text-xs text-blue-500 mt-1">Loading airports...</p>
                  </div>
                  <div v-if="activityForm.required_trip_type !== 'multi_city'">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Departure Date</label>
                    <input type="date" v-model="activityForm.required_departure_date"
                      @change="fetchFilteredTravelClasses()"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]">
                  </div>
                  <div v-show="showReturnDate && activityForm.required_trip_type !== 'multi_city'">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Return Date</label>
                    <input type="date" v-model="activityForm.required_return_date" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]">
                  </div>

                  <!-- Multi-City Segments Section -->
                  <div v-if="activityForm.required_trip_type === 'multi_city'" class="md:col-span-2 space-y-4">
                    <div class="flex items-center justify-between">
                      <label class="block text-sm font-bold text-gray-700">Flight Segments *</label>
                      <button type="button" @click="addSegment" class="text-xs bg-[#0E8028] text-white px-3 py-1 rounded hover:bg-green-700 transition-colors">
                        + Add Segment
                      </button>
                    </div>
                    
                    <div v-for="(segment, index) in activityForm.segments" :key="index" class="p-4 bg-gray-50 rounded-lg border border-gray-200 relative group">
                      <button @click="removeSegment(index)" type="button" class="absolute top-2 right-2 text-red-500 opacity-0 group-hover:opacity-100 transition-opacity">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <polyline points="3 6 5 6 21 6"></polyline>
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                      </button>
                      
                      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <label class="block text-xs font-medium text-gray-600 mb-1">Origin *</label>
                          <select v-model="segment.origin" required
                            class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-pink-500"
                            @change="fetchFilteredTravelClasses()">
                            <option value="">Select Origin</option>
                            <option v-for="airport in airports" :key="airport.code" :value="airport.code">{{ airport.code }} - {{ airport.name }}</option>
                          </select>
                        </div>
                        <div>
                          <label class="block text-xs font-medium text-gray-600 mb-1">Destination *</label>
                          <select v-model="segment.destination" required
                            class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-pink-500"
                            @change="fetchFilteredTravelClasses()">
                            <option value="">Select Destination</option>
                            <option v-for="airport in airports" :key="airport.code" :value="airport.code">{{ airport.code }} - {{ airport.name }}</option>
                          </select>
                        </div>
                        <div>
                          <label class="block text-xs font-medium text-gray-600 mb-1">Date *</label>
                          <input type="date" v-model="segment.departure_date" required
                            class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-pink-500"
                            @change="fetchFilteredTravelClasses()">
                        </div>
                      </div>
                    </div>
                    <p v-if="activityForm.segments.length === 0" class="text-sm text-red-500">At least one segment is required for multi-city trips.</p>
                  </div>
                </div>
              </div>

              <!-- Passenger Requirements Section -->
              <div class="border-t border-gray-200 pt-4">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Passenger Requirements</h3>
                
                <!-- Passenger Counts -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Adults (12+ years) *</label>
                    <input type="number" v-model.number="activityForm.required_passengers" @change="updatePassengerForms" min="1" max="9" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]">
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Children (2-11 years)</label>
                    <input type="number" v-model.number="activityForm.required_children" @change="updatePassengerForms" min="0" max="8" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]">
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Infants (Under 2 years)</label>
                    <input type="number" v-model.number="activityForm.required_infants" @change="updatePassengerForms" min="0" max="4" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]">
                    <p class="text-xs text-gray-500 mt-1">Note: Infants must be accompanied by adults</p>
                  </div>
                </div>

                <!-- Add-on & Insurance Requirements -->
                <div class="mb-6 p-4 bg-pink-50 rounded-lg border border-pink-100">
                  <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center">
                      <input type="checkbox" v-model="activityForm.require_addons" @change="toggleAddons"
                            class="mr-2 h-5 w-5 rounded border-gray-300 text-pink-600 focus:ring-pink-500">
                      <label class="text-md font-bold text-gray-800">Require Add-ons & Insurance</label>
                    </div>
                    <span v-if="activityForm.require_addons" class="text-xs font-bold text-pink-600 bg-white px-2 py-1 rounded-full border border-pink-200">
                      {{ activityForm.selected_addons.length }} Selected
                    </span>
                  </div>
                  
                  <div v-if="activityForm.require_addons" class="space-y-4">
                    <p class="text-sm text-gray-600">Select which add-ons or insurance plans should be available for this activity:</p>
                    
                    <div v-if="addons.length === 0" class="text-sm text-gray-500 italic py-2">
                       No add-ons available for this route/date yet.
                    </div>
                    
                    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-60 overflow-y-auto p-1">
                      <div v-for="addon in addons" :key="addon.id" 
                           class="flex items-start p-3 rounded-md border transition-all"
                           :class="activityForm.selected_addons.includes(addon.id) ? 'bg-white border-pink-400 shadow-sm' : 'bg-gray-50 border-gray-200 hover:border-pink-200'">
                        <div class="flex items-center h-5 mt-0.5">
                          <input type="checkbox" 
                                 :value="addon.id" 
                                 v-model="activityForm.selected_addons"
                                 @change="syncPassengerAddons"
                                 class="h-4 w-4 rounded border-gray-300 text-pink-600 focus:ring-pink-500">
                        </div>
                        <div class="ml-3 text-sm flex-1">
                          <div class="flex items-center justify-between">
                            <label class="font-bold text-gray-700">{{ addon.name }}</label>
                            <span class="text-[10px] px-1.5 py-0.5 rounded bg-gray-200 text-gray-700 font-bold uppercase">
                              {{ addon.type?.name || 'Add-on' }}
                            </span>
                          </div>
                          <div class="flex items-center justify-between mt-1">
                            <span class="text-xs text-pink-600 font-bold">₱{{ addon.price }}</span>
                            <div class="flex items-center gap-2">
                              <label class="text-[10px] text-gray-500 flex items-center cursor-pointer">
                                <input type="checkbox" 
                                       v-model="addonRequirements[addon.id]" 
                                       @change="syncPassengerAddons"
                                       class="mr-1 h-3 w-3 rounded text-pink-500">
                                Required?
                              </label>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Passport Requirement Checkbox -->
                <div class="mb-4">
                  <div class="flex items-center">
                    <input type="checkbox" v-model="activityForm.require_passport" 
                          class="mr-2 rounded border-gray-300 text-[#093704] focus:ring-[#093704]">
                    <label class="text-md font-semibold text-gray-700">Require Passport Information for ALL Passengers</label>
                  </div>
                  <p class="text-sm text-gray-600 ml-6 mt-1">
                    Students must provide passport numbers for every passenger in the booking
                  </p>
                </div>

                <!-- Passenger Details Requirements -->
                <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
                  <div class="flex items-center mb-3">
                    <input type="checkbox" v-model="activityForm.require_passenger_details" @change="togglePassengerForms" class="mr-2 rounded border-gray-300 text-[#093704] focus:ring-[#093704]">
                    <label class="text-md font-semibold text-gray-700">Require Passenger Details</label>
                  </div>
                  <p class="text-sm text-gray-600 mb-4">Students must provide the following details for each passenger:</p>
                  
                  <!-- Passenger Information Input Fields -->
                  <div v-if="activityForm.require_passenger_details" class="space-y-6">
                    <!-- Adults Section -->
                    <div v-for="(passenger, index) in getPassengersByType('Adult')" :key="'adult-' + index" class="bg-white rounded-lg border border-gray-300 overflow-hidden">
                      <div class="bg-gradient-to-r from-yellow-400 to-yellow-300 px-4 py-2 flex items-center justify-between">
                        <div class="flex items-center gap-2">
                          <span class="text-sm font-bold text-gray-800">Passenger {{ passenger.globalIndex }} - Adult</span>
                        </div>
                        <span class="bg-yellow-500 text-white text-xs font-bold px-3 py-1 rounded-full">Primary</span>
                      </div>
                      <div class="p-4">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">First Name *</label>
                            <input type="text" v-model="passenger.firstName" placeholder="Enter first name" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Middle Name</label>
                            <input type="text" v-model="passenger.middleName" placeholder="Enter middle name" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Last Name *</label>
                            <input type="text" v-model="passenger.lastName" placeholder="Enter last name" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Title / Gender *</label>
                            <select v-model="passenger.gender" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400 text-sm">
                              <option value="">Select Title</option>
                              <option value="MR">Mr.</option>
                              <option value="MRS">Mrs.</option>
                              <option value="MS">Ms.</option>
                            </select>
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Date of Birth *</label>
                            <input type="date" v-model="passenger.dob" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Nationality *</label>
                            <select v-model="passenger.nationality" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400 text-sm">
                              <option value="">Select Nationality</option>
                              <option v-for="nat in nationalities" :key="nat" :value="nat">{{ nat }}</option>
                            </select>
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Passport Number</label>
                            <input type="text" v-model="passenger.passportNumber" placeholder="Enter passport number" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Passenger Category *</label>
                            <select v-model="passenger.passenger_category" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400 text-sm">
                              <option value="none">Regular</option>
                              <option value="senior">Senior Citizen</option>
                              <option value="pwd">PWD</option>
                            </select>
                          </div>
                          <!-- PWD ID Number - shown only when PWD -->
                          <div v-if="passenger.passenger_category === 'pwd'">
                            <label class="block text-xs font-medium text-blue-600 mb-1">PWD ID Number *</label>
                            <input type="text" v-model="passenger.pwd_id_number" placeholder="e.g. PWD-1234567" class="w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 text-sm">
                          </div>
                          <!-- Senior Citizen ID - shown only when Senior -->
                          <div v-if="passenger.passenger_category === 'senior'">
                            <label class="block text-xs font-medium text-amber-600 mb-1">Senior Citizen ID *</label>
                            <input type="text" v-model="passenger.senior_id_number" placeholder="e.g. SC-1234567" class="w-full px-3 py-2 border border-amber-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-400 text-sm">
                          </div>
                          <!-- Passport Expiry - shown only for non-Philippines nationality -->
                          <div v-if="passenger.nationality && passenger.nationality !== 'Philippines'">
                            <label class="block text-xs font-medium text-red-600 mb-1">Passport Expiry Date *</label>
                            <input type="date" v-model="passenger.passport_expiry_date" class="w-full px-3 py-2 border border-red-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-400 text-sm">
                          </div>
                        </div>

                        <!-- Per-Passenger Add-ons Selection -->
                        <div v-if="activityForm.require_addons && activityForm.selected_addons.length > 0" class="md:col-span-2 mt-4">
                          <label class="block text-xs font-bold text-gray-600 mb-2 uppercase tracking-tight">Passenger Specific Add-ons</label>
                          <div class="flex flex-wrap gap-2">
                            <div v-for="addonId in activityForm.selected_addons" :key="addonId" 
                                 class="flex items-center px-3 py-1.5 rounded-lg border transition-all cursor-pointer"
                                 :class="passenger.selected_addons.includes(addonId) ? 'bg-pink-50 border-pink-400 text-pink-700' : 'bg-white border-gray-200 text-gray-500 hover:border-pink-200'"
                                 @click="togglePassengerAddon(passenger, addonId)">
                              <span class="text-[10px] font-bold">{{ addons.find(a => a.id === addonId)?.name }}</span>
                              <svg v-if="passenger.selected_addons.includes(addonId)" xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 ml-2" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                              </svg>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Children Section -->
                    <div v-for="(passenger, index) in getPassengersByType('Child')" :key="'child-' + index" class="bg-white rounded-lg border border-gray-300 overflow-hidden">
                      <div class="bg-gradient-to-r from-teal-400 to-teal-300 px-4 py-2 flex items-center justify-between">
                        <div class="flex items-center gap-2">
                          <span class="text-sm font-bold text-gray-800">Passenger {{ passenger.globalIndex }} - Child</span>
                        </div>
                        <span class="bg-teal-500 text-white text-xs font-bold px-3 py-1 rounded-full">Child</span>
                      </div>
                      <div class="p-4">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">First Name *</label>
                            <input type="text" v-model="passenger.firstName" placeholder="Enter first name" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Middle Name</label>
                            <input type="text" v-model="passenger.middleName" placeholder="Enter middle name" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Last Name *</label>
                            <input type="text" v-model="passenger.lastName" placeholder="Enter last name" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Gender *</label>
                            <select v-model="passenger.gender" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-400 text-sm">
                              <option value="">Select Gender</option>
                              <option value="mr">Mr.</option>
                              <option value="mrs">Mrs.</option>
                              <option value="other">Other</option>
                            </select>
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Date of Birth *</label>
                            <input type="date" v-model="passenger.dob" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Nationality *</label>
                            <select v-model="passenger.nationality" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-400 text-sm">
                              <option value="">Select Nationality</option>
                              <option v-for="nat in nationalities" :key="nat" :value="nat">{{ nat }}</option>
                            </select>
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Passport Number</label>
                            <input type="text" v-model="passenger.passportNumber" placeholder="Enter passport number" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Passenger Category *</label>
                            <select v-model="passenger.passenger_category" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-400 text-sm">
                              <option value="none">Regular</option>
                              <option value="senior">Senior Citizen</option>
                              <option value="pwd">PWD</option>
                            </select>
                          </div>
                          <!-- PWD ID Number - shown only when PWD -->
                          <div v-if="passenger.passenger_category === 'pwd'">
                            <label class="block text-xs font-medium text-blue-600 mb-1">PWD ID Number *</label>
                            <input type="text" v-model="passenger.pwd_id_number" placeholder="e.g. PWD-1234567" class="w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 text-sm">
                          </div>
                          <!-- Senior Citizen ID - shown only when Senior -->
                          <div v-if="passenger.passenger_category === 'senior'">
                            <label class="block text-xs font-medium text-amber-600 mb-1">Senior Citizen ID *</label>
                            <input type="text" v-model="passenger.senior_id_number" placeholder="e.g. SC-1234567" class="w-full px-3 py-2 border border-amber-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-400 text-sm">
                          </div>
                          <!-- Passport Expiry - shown only for non-Philippines nationality -->
                          <div v-if="passenger.nationality && passenger.nationality !== 'Philippines'">
                            <label class="block text-xs font-medium text-red-600 mb-1">Passport Expiry Date *</label>
                            <input type="date" v-model="passenger.passport_expiry_date" class="w-full px-3 py-2 border border-red-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-400 text-sm">
                          </div>
                        </div>

                        <!-- Per-Passenger Add-ons Selection -->
                        <div v-if="activityForm.require_addons && activityForm.selected_addons.length > 0" class="md:col-span-2 mt-4">
                          <label class="block text-xs font-bold text-gray-600 mb-2 uppercase tracking-tight">Passenger Specific Add-ons</label>
                          <div class="flex flex-wrap gap-2">
                            <div v-for="addonId in activityForm.selected_addons" :key="addonId" 
                                 class="flex items-center px-3 py-1.5 rounded-lg border transition-all cursor-pointer"
                                 :class="passenger.selected_addons.includes(addonId) ? 'bg-pink-50 border-pink-400 text-pink-700' : 'bg-white border-gray-200 text-gray-500 hover:border-pink-200'"
                                 @click="togglePassengerAddon(passenger, addonId)">
                              <span class="text-[10px] font-bold">{{ addons.find(a => a.id === addonId)?.name }}</span>
                              <svg v-if="passenger.selected_addons.includes(addonId)" xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 ml-2" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                              </svg>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Infants Section -->
                    <div v-for="(passenger, index) in getPassengersByType('Infant')" :key="'infant-' + index" class="bg-white rounded-lg border border-gray-300 overflow-hidden">
                      <div class="bg-gradient-to-r from-violet-400 to-violet-300 px-4 py-2 flex items-center justify-between">
                        <div class="flex items-center gap-2">
                          <span class="text-sm font-bold text-gray-800">Passenger {{ passenger.globalIndex }} - Infant</span>
                        </div>
                        <span class="bg-violet-500 text-white text-xs font-bold px-3 py-1 rounded-full">Infant</span>
                      </div>
                      <div class="p-4">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">First Name *</label>
                            <input type="text" v-model="passenger.firstName" placeholder="Enter first name" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Middle Name</label>
                            <input type="text" v-model="passenger.middleName" placeholder="Enter middle name" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Last Name *</label>
                            <input type="text" v-model="passenger.lastName" placeholder="Enter last name" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Gender</label>
                            <select v-model="passenger.gender" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-400 text-sm">
                              <option value="">Select Gender</option>
                              <option value="mr">Mr.</option>
                              <option value="mrs">Mrs.</option>
                              <option value="other">Other</option>
                            </select>
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Date of Birth *</label>
                            <input type="date" v-model="passenger.dob" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Nationality</label>
                            <select v-model="passenger.nationality" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-400 text-sm">
                              <option value="">Select Nationality</option>
                              <option v-for="nat in nationalities" :key="nat" :value="nat">{{ nat }}</option>
                            </select>
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Passport Number</label>
                            <input type="text" v-model="passenger.passportNumber" placeholder="Enter passport number" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Sitting on (Adult) *</label>
                            <select v-model="passenger.associatedAdultIndex" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-400 text-sm">
                              <option :value="null">Select Adult</option>
                              <option v-for="adult in getPassengersByType('Adult')" :key="'adult-for-infant-' + adult.globalIndex" :value="adult.globalIndex">
                                Passenger {{ adult.globalIndex }} ({{ adult.firstName }} {{ adult.lastName }})
                              </option>
                            </select>
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Passenger Category *</label>
                            <select v-model="passenger.passenger_category" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-400 text-sm">
                              <option value="none">Regular</option>
                              <option value="senior">Senior Citizen</option>
                              <option value="pwd">PWD</option>
                            </select>
                          </div>
                          <!-- Passport Expiry - shown only for non-Philippines nationality (infants can be foreign too) -->
                          <div v-if="passenger.nationality && passenger.nationality !== 'Philippines'">
                            <label class="block text-xs font-medium text-red-600 mb-1">Passport Expiry Date *</label>
                            <input type="date" v-model="passenger.passport_expiry_date" class="w-full px-3 py-2 border border-red-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-400 text-sm">
                          </div>
                        </div>

                        <!-- Infants never have add-ons -->
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Additional Details -->
              <div class="border-t border-gray-200 pt-4">
                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Activity Description (Optional)</label>
                  <textarea v-model="activityForm.description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]" placeholder="Additional details about the activity..."></textarea>
                </div>
              </div>
            </div>

            <div class="flex justify-end space-x-3 pt-6 mt-6 border-t border-gray-200">
              <button type="button" @click="closeActivityModal" 
                class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors">
                Cancel
              </button>
              
              <button type="button" @click="randomizeData" 
                :disabled="loading || isLoadingData || airports.length === 0"
                class="bg-gray-800 hover:bg-black text-white px-6 py-2 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                <span v-if="isLoadingData">Loading airports...</span>
                <span v-else-if="airports.length === 0">No airports available</span>
                <span v-else>Randomize</span>
              </button>
              
              <button type="submit" :disabled="loading"
                class="bg-[#FF579A] hover:bg-[#FF577A]/80 text-white px-6 py-2 rounded-md transition-colors disabled:opacity-50">
                <span v-if="loading">Processing...</span>
                <span v-else>{{ isEditing ? 'Save Changes' : 'Create Activity' }}</span>
              </button>
            </div>

          </form>
        </div>
      </div>
  </div>
</template>


<script setup>
import CTHM from '@/assets/image/cthm-logos.png'
import { ref, computed, onMounted, watch, reactive, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api/axios'
import { sectionDetailsService } from '@/services/instructor/sectionDetailsService'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { activityService } from '@/services/instructor/activityService'
import flightService from '@/services/booking/flightService'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()

const section = ref(null)
const userData = ref(null)
const isFetching = ref(false)

// Activities list
const activities = ref([])
const activeFilter = ref('All')

const filteredActivities = computed(() => {
  if (activeFilter.value === 'All') return activities.value
  if (activeFilter.value === 'Active') return activities.value.filter(a => a.is_code_active && (!a.due_date || new Date(a.due_date) >= new Date()))
  if (activeFilter.value === 'Draft') return activities.value.filter(a => !a.is_code_active)
  return activities.value
})

const activityDropdowns = ref({}) // Track which dropdown is open

// Enroll Student Modal Logic
const isModalOpen = ref(false)
const studentNumberInput = ref('')
const loading = ref(false)

// Activity Modal Logic
const activityModalOpen = ref(false)
const showReturnDate = ref(false)
const passengerForms = ref([])
const isEditing = ref(false)
const editingActivityId = ref(null)
// ✅ Passenger pool: stores ALL passenger data ever created/randomized
// so that reducing count and then increasing it again restores previously entered data.
const passengerPool = ref({})

// Success Modal
const showSuccessModal = ref(false)
const successMessage = ref('')

// Delete Confirmation Modal
const showDeleteModal = ref(false)
const activityToDelete = ref(null)

// Airport, addons and students data
const airports = ref([])
const addons = ref([])
const students = ref([]) // ✅ NEW: Students data
const travel_classes = ref([]) // ✅ All travel classes from backend (fallback)
const filteredTravelClasses = ref([]) // ✅ Classes filtered by route+date
const isFetchingTravelClasses = ref(false)
const filteredAddons = ref([]) // ✅ Add-ons filtered by route+date
const isFetchingAddons = ref(false)
const isLoadingData = ref(false)
const validRoutes = ref([]) // ✅ NEW: Store valid routes for randomization

const activityForm = reactive({
  title: '',
  activity_type: 'Flight Booking',
  instructions: '',
  due_date: '',
  total_points: 100,
  required_trip_type: 'one_way',
  required_travel_class: 'economy',
  required_origin: '',
  required_destination: '',
  required_departure_date: '',
  required_return_date: '',
  required_passengers: 1,
  required_children: 0,
  required_infants: 0,
  require_passport: true,
  require_passenger_details: true,
  require_addons: false,
  selected_addons: [],
  segments: [],
  description: ''
})

const availableBundles = computed(() => {
  const tc = (activityForm.required_travel_class || '').toLowerCase();
  if (tc.includes('economy') && !tc.includes('premium')) {
    return ['Super Saver', 'Saver', 'Value', 'Flex'];
  } else if (tc.includes('premium')) {
    return ['Premium Saver', 'Premium Value', 'Premium Flex'];
  } else if (tc.includes('business')) {
    return ['Business Value', 'Business Flex'];
  }
  return [];
})

const addonRequirements = reactive({})

const resetActivityForm = () => {
  Object.assign(activityForm, {
    title: '',
    activity_type: 'Flight Booking',
    instructions: '',
    due_date: '',
    total_points: 100,
    required_trip_type: 'one_way',
    required_travel_class: 'economy',
    required_seat_class: '',
    required_origin: '',
    required_destination: '',
    required_departure_date: '',
    required_return_date: '',
    required_passengers: 1,
    required_children: 0,
    required_infants: 0,
    require_passport: true,
    require_passenger_details: true,
    require_addons: false,
    selected_addons: [],
    segments: [],
    description: ''
  })
  
  Object.keys(addonRequirements).forEach(key => delete addonRequirements[key])
  passengerForms.value = []
  passengerPool.value = {}
  showReturnDate.value = false
}

// --- Randomizer Data Pools ---
const sampleTitles = ['Flight Booking Assessment', 'Advanced Reservation Task', 'Round Trip Coordination', 'Emergency Rebooking', 'Group Booking', 'Multi-city Itinerary', 'Flight Activity', 'Travel Planning', 'Luxury Flight Arrangement', 'International Travel Simulation' , 'Budget Travel Challenge', 'Family Vacation Planning', 'Business Trip Coordination', 'Last-minute Booking', 'Holiday Travel Arrangement', 'Student Travel Task', 'Airport Transfer Booking', 'Frequent Flyer Challenge', 'Airline Comparison Activity', 'Travel Class Upgrade Simulation', 'Flight Change Scenario'];
const firstNames = ['James', 'Mary', 'Robert', 'Patricia', 'John', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth', 'David', 'Maria', 'Richard', 'Susan', 'Joseph', 'Rose' , 'Pathrick', 'Kyle', 'Samantha', 'Brian', 'Jessica', 'Kevin', 'Sarah', 'Thomas', 'Karen' , 'Charles', 'Nancy', 'Christopher', 'Lisa', 'Daniel', 'Betty' , 'Matthew', 'Margaret', 'Anthony', 'Sandra', 'Mark', 'Ashley', 'Donald', 'Kimberly', 'Steven', 'Emily', 'Paul', 'Donna', 'Andrew', 'Michelle' , 'Joshua', 'Dorothy', 'Kenneth', 'Carol', 'Kevin', 'Amanda'];
const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts' ];
const middleNames = ['Lee', 'Garcia', 'Quinto', 'Santos', 'Reyes', 'Cruz', 'Bautista', 'Ocampo', 'Mae', 'Ann', 'Marie', 'Louise' , 'James', 'John', 'Ray', 'Lynn', 'Grace', 'Rose', 'Mae', 'Jean', 'Paul', 'Mark', 'Jane', 'Louise', 'Michael', 'Elizabeth', 'Ann', 'Lee', 'Marie', 'Ray', 'Lynn', 'Grace', 'Rose', 'Jean', 'Paul', 'Mark', 'Jane', 'Louise'];
// Must match exactly the options available in PassengerForm.vue (booking side)
const nationalities = ['Philippines', 'United States', 'Japan', 'South Korea', 'Singapore', 'Australia'];

let successTimeout = null;
const showSuccess = (message) => {
  if (successTimeout) clearTimeout(successTimeout);
  
  // Force a re-trigger of the animation if already shown
  if (showSuccessModal.value) {
    showSuccessModal.value = false;
    nextTick(() => {
      successMessage.value = message;
      showSuccessModal.value = true;
      successTimeout = setTimeout(() => {
        showSuccessModal.value = false;
      }, 3000);
    });
    return;
  }

  successMessage.value = message;
  showSuccessModal.value = true;
  successTimeout = setTimeout(() => {
    showSuccessModal.value = false;
  }, 3000);
}

const avgCompletionRate = computed(() => {
  if (activities.value.length === 0) return 0;
  const totalStudents = section.value?.student_count || 1; // avoid division by zero
  let totalSubmissions = 0;
  let expectedSubmissions = activities.value.length * totalStudents;
  
  activities.value.forEach(act => {
    totalSubmissions += act.total_submissions || 0;
  });
  
  return Math.min(100, Math.floor((totalSubmissions / expectedSubmissions) * 100));
});

const submissionRate = computed(() => {
  // Can be the same as avgCompletionRate, or could be distinct depending on logic.
  // Assuming they are conceptually the same here for high-level visualization.
  return avgCompletionRate.value;
});

const getActivityCompletionRate = (activity) => {
  const totalStudents = section.value?.student_count || 0;
  if (!totalStudents) return 0; // If no students, 0%
  const submissions = activity.total_submissions || 0;
  return Math.min(100, Math.floor((submissions / totalStudents) * 100));
};

const openEnrollModal = () => {
  studentNumberInput.value = ''
  isModalOpen.value = true
}

const submitEnrollment = async () => {
  if (!studentNumberInput.value) {
    notificationStore.warn("Please enter a student number")
    return
  }
  
  loading.value = true
  try {
    const sectionId = route.params.id
    const token = localStorage.getItem('auth_token')
    
    const response = await api.post(`api/instructor/sections/${sectionId}/enroll/`, 
      { student_number: studentNumberInput.value }
    )
    
    notificationStore.success(response.data.message)
    isModalOpen.value = false
  } catch (error) {
    notificationStore.error(error.response?.data?.error || "Failed to enroll student")
  } finally {
    loading.value = false
  }
}

const openActivityModal = async () => {
  resetActivityForm()
  isEditing.value = false
  editingActivityId.value = null
  activityModalOpen.value = true
  isLoadingData.value = true
  
  airports.value = []
  addons.value = []
  students.value = []
  
  await fetchAirportsAndAddons()
  
  isLoadingData.value = false
  updatePassengerForms()
}

const openEditActivity = async (activity) => {
  resetActivityForm()
  isEditing.value = true
  editingActivityId.value = activity.id
  activityModalOpen.value = true
  isLoadingData.value = true
  activityDropdowns.value[activity.id] = false
  
  await fetchAirportsAndAddons()
  
  try {
    const res = await api.get(`api/instructor/activities/${activity.id}/`)
    const act = res.data
    
    activityForm.title = act.title
    activityForm.activity_type = "Flight Booking"
    let formattedDue = ""
    if (act.due_date) {
        const d = new Date(act.due_date)
        if (!isNaN(d)) formattedDue = new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16)
    }
    activityForm.due_date = formattedDue
    activityForm.total_points = act.total_points || 100
    activityForm.instructions = act.instructions || ''
    
    let tripType = act.required_trip_type || 'one_way'
    if(tripType.toLowerCase() === 'round-trip') tripType = 'round_trip'
    else if(tripType.toLowerCase() === 'multi-city') tripType = 'multi_city'
    else if(tripType.toLowerCase() === 'one-way') tripType = 'one_way'
    activityForm.required_trip_type = tripType

    activityForm.required_travel_class = (act.required_travel_class || 'economy').toLowerCase().replace(' ', '_')
    activityForm.required_seat_class = act.required_seat_class || ''
    activityForm.required_origin = act.required_origin || ''
    activityForm.required_destination = act.required_destination || ''
    activityForm.required_departure_date = act.required_departure_date || ''
    activityForm.required_return_date = act.required_return_date || ''
    activityForm.required_passengers = act.required_passengers || 0
    activityForm.required_children = act.required_children || 0
    activityForm.required_infants = act.required_infants || 0
    activityForm.description = act.description || ''
    activityForm.require_passport = act.require_passport || false
    activityForm.require_passenger_details = act.require_passenger_details || false
    activityForm.require_addons = act.require_addons || false
    activityForm.time_limit_minutes = act.time_limit_minutes || null
    
    if (act.segments) {
      activityForm.segments = act.segments.map(s => ({
        origin: s.origin,
        destination: s.destination,
        departure_date: s.departure_date
      }))
    }
    
    handleTripTypeChange()
    await fetchFilteredTravelClasses()

    passengerForms.value = []
    if (act.passengers && act.passengers.length > 0) {
       activityForm.require_passenger_details = true
       
       act.passengers.forEach((p, idx) => {
          let type = p.type || 'Adult'
          if(p.passenger_type) type = p.passenger_type.charAt(0).toUpperCase() + p.passenger_type.slice(1)
          
          let pGender = p.gender || 'MR'
          if(pGender.toLowerCase() === 'male' || pGender.toLowerCase().includes('mr')) pGender = 'MR'
          else if(pGender.toLowerCase() === 'female' || pGender.toLowerCase().includes('mrs')) pGender = 'MRS'
          else if(pGender.toLowerCase().includes('ms')) pGender = 'MS'
          else pGender = pGender.toUpperCase().replace('.', '')

          let pForm = {
            type: type,
            globalIndex: idx + 1,
            poolIndex: idx,
            firstName: p.first_name,
            middleName: p.middle_name,
            lastName: p.last_name,
            gender: pGender,
            dob: p.date_of_birth,
            nationality: p.nationality,
            passportNumber: p.passport_number,
            passport_expiry_date: p.passport_expiry_date,
            passenger_category: p.passenger_category || 'none',
            pwd_id_number: p.pwd_id_number,
            senior_id_number: p.senior_id_number,
            selected_addons: [],
            addon_requirements: {}
          }
          passengerForms.value.push(pForm)
       })
    } else {
       activityForm.require_passenger_details = false
    }
    
    if (act.activity_addons && act.activity_addons.length > 0) {
      activityForm.require_addons = true
      let addonIds = new Set()
      act.activity_addons.forEach(aa => {
         addonIds.add(aa.addon_id)
         let p = passengerForms.value.find(pf => (pf.firstName === aa.passenger.first_name && pf.lastName === aa.passenger.last_name))
         if (p) {
             if (!p.selected_addons.includes(aa.addon_id)) {
                 p.selected_addons.push(aa.addon_id)
                 p.addon_requirements[aa.addon_id] = { required: true, quantity: 1, notes: '' }
             }
         }
      })
      activityForm.selected_addons = Array.from(addonIds)
      
      activityForm.selected_addons.forEach(id => {
          addonRequirements[id] = { required: true, quantity: 1, notes: '' }
      })
    } else {
      activityForm.require_addons = false
      activityForm.selected_addons = []
    }
    
  } catch(e) {
    console.error(e)
    notificationStore.error("Failed to load activity details")
  }
  
  isLoadingData.value = false
}

const closeActivityModal = () => {
  activityModalOpen.value = false
  isEditing.value = false
  editingActivityId.value = null
}

const handleTripTypeChange = () => {
  showReturnDate.value = activityForm.required_trip_type === 'round_trip'
  
  if (activityForm.required_trip_type === 'one_way') {
    activityForm.required_return_date = ''
  }

  if (activityForm.required_trip_type === 'multi_city' && activityForm.segments.length === 0) {
    // Add two initial segments for multi-city
    addSegment()
    addSegment()
  } else if (activityForm.required_trip_type !== 'multi_city') {
    activityForm.segments = []
  }
}

const addSegment = () => {
  activityForm.segments.push({
    origin: '',
    destination: '',
    departure_date: ''
  })
}

const removeSegment = (index) => {
  activityForm.segments.splice(index, 1)
}

// Activity dropdown toggle
const toggleActivityDropdown = (activityId) => {
  // Close all other dropdowns
  Object.keys(activityDropdowns.value).forEach(key => {
    if (key !== activityId.toString()) {
      activityDropdowns.value[key] = false
    }
  })
  // Toggle current dropdown
  activityDropdowns.value[activityId] = !activityDropdowns.value[activityId]
}

// Delete activity functions
const openDeleteModal = (activity) => {
  activityToDelete.value = activity
  showDeleteModal.value = true
  activityDropdowns.value[activity.id] = false // Close dropdown
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  activityToDelete.value = null
}

const confirmDeleteActivity = async () => {
  if (!activityToDelete.value) return
  
  loading.value = true
  try {
    const sectionId = route.params.id
    const activityId = activityToDelete.value.id
    const token = localStorage.getItem('auth_token')
    
    const response = await api.delete(
      `api/instructor/sections/${sectionId}/activities/${activityId}/delete/`
    )
    
    notificationStore.success(response.data.message || 'Activity deleted successfully!')
    closeDeleteModal()
    fetchAllData() // Refresh activities list
    
  } catch (error) {
    notificationStore.error(error.response?.data?.error || "Failed to delete activity")
  } finally {
    loading.value = false
  }
}

const goToActivity = (activityId) => {
  if (!activityId) {
    console.error("The activity ID is missing!");
    return;
  }
  router.push(`/instructor/activity/${activityId}`)
}

// Format date
const formatDate = (dateString) => {
  if (!dateString) return 'No due date'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

// Get activity icon letter
const getActivityIcon = (title) => {
  return title ? title.charAt(0).toUpperCase() : 'A'
}

// ✅ UPDATED: Fetch airports, addons, AND students
const fetchAirportsAndAddons = async () => {
  try {
    const sectionId = route.params.id
    const token = localStorage.getItem('auth_token')
    
    const response = await api.get(
      `api/instructor/sections/${sectionId}/activities/create/`
    )
    
    airports.value = response.data.airports || []
    addons.value = response.data.available_addons || []
    students.value = response.data.students || [] // ✅ Store students data
    travel_classes.value = response.data.available_travel_classes || [] // ✅ Store all travel classes (fallback)
    validRoutes.value = response.data.valid_routes || [] // ✅ NEW: Store valid routes
    // Initialize filteredTravelClasses with all classes until route+date is chosen
    filteredTravelClasses.value = travel_classes.value
    
  } catch (error) {
    console.error('Failed to fetch airports and addons:', error)
    airports.value = []
    addons.value = []
    students.value = []
  }
}

// ✅ Fetch available travel classes for a given route+date from the backend.
// Supports one-way, round-trip (single leg), and multi-city (segment intersection).
const fetchFilteredTravelClasses = async (opts = {}) => {
  const tripType = opts.tripType ?? activityForm.required_trip_type
  const origin = opts.origin ?? activityForm.required_origin
  const destination = opts.destination ?? activityForm.required_destination
  const date = opts.date ?? activityForm.required_departure_date
  const returnDate = opts.returnDate ?? activityForm.required_return_date
  const segments = opts.segments ?? activityForm.segments

  // Don't fetch if we don't have at least a route or segments
  const hasRoute = origin && destination && date
  const hasSegments = tripType === 'multi_city' && segments && segments.length > 0
  if (!hasRoute && !hasSegments) {
    // Fall back to full list only if NO route is selected at all
    filteredTravelClasses.value = travel_classes.value.length > 0 ? travel_classes.value : []
    return filteredTravelClasses.value
  }

  isFetchingTravelClasses.value = true
  try {
    let params = {}
    if (hasSegments) {
      params.segments = JSON.stringify(segments)
    } else {
      params.origin = origin
      params.destination = destination
      params.date = date
      if (tripType === 'round_trip' && returnDate) {
        params.return_date = returnDate
      }
    }

    const response = await api.get('api/instructor/available-travel-classes/', { params })
    const classes = response.data?.available_travel_classes || []
    filteredTravelClasses.value = classes

    // If currently selected travel class isn't available, reset to first option
    if (classes.length > 0 && !classes.includes(activityForm.required_travel_class)) {
      activityForm.required_travel_class = classes[0]
    }

    return classes
  } catch (err) {
    console.warn('⚠️ Could not fetch filtered travel classes, using fallback:', err)
    filteredTravelClasses.value = travel_classes.value
    return travel_classes.value
  } finally {
    isFetchingTravelClasses.value = false
  }
}

const fetchFilteredAddons = async (opts = {}) => {
  const tripType = opts.tripType ?? activityForm.required_trip_type
  const origin = opts.origin ?? activityForm.required_origin
  const destination = opts.destination ?? activityForm.required_destination
  const date = opts.date ?? activityForm.required_departure_date
  const segments = opts.segments ?? activityForm.segments

  const hasRoute = origin && destination && date
  const hasSegments = tripType === 'multi_city' && segments && segments.length > 0
  
  if (!hasRoute && !hasSegments) {
    filteredAddons.value = addons.value
    return addons.value
  }

  isFetchingAddons.value = true
  try {
    let params = {}
    if (hasSegments) {
      params.segments = JSON.stringify(segments)
    } else {
      params.origin = origin
      params.destination = destination
      params.date = date
    }

    const response = await api.get('api/instructor/available-addons/', { params })
    const available = response.data?.available_addons || []
    filteredAddons.value = available
    return available
  } catch (err) {
    console.warn('⚠️ Could not fetch filtered addons, using fallback:', err)
    filteredAddons.value = addons.value
    return addons.value
  } finally {
    isFetchingAddons.value = false
  }
}


// ✅ Pool-based passenger management: data is NEVER lost when counts change
const updatePassengerForms = () => {
  if (!activityForm.require_passenger_details) {
    // Move all current forms into pool before clearing
    passengerForms.value.forEach(p => {
      const poolKey = `${p.type}-${p.poolIndex ?? p.globalIndex}`;
      passengerPool.value[poolKey] = { ...p };
    });
    passengerForms.value = []
    return
  }

  // Move current forms into pool first (sync pool with latest data)
  passengerForms.value.forEach(p => {
    const poolKey = `${p.type}-${p.poolIndex ?? p.globalIndex}`;
    passengerPool.value[poolKey] = { ...p };
  });
  
  const newAdultCount = activityForm.required_passengers
  const newChildCount = activityForm.required_children
  const newInfantCount = activityForm.required_infants
  
  const newForms = []
  let globalIndex = 1

  const getOrRestorePassenger = (type, indexInType) => {
    const poolKey = `${type}-${indexInType}`;
    if (passengerPool.value[poolKey]) {
      // ✅ Restore from pool — preserves all randomized/entered data
      return { ...passengerPool.value[poolKey], globalIndex, poolIndex: indexInType };
    }
    // 🆕 Create a new passenger, but auto-fill with basic valid data to prevent
    // validation errors when user manually increments passenger counts after randomizing
    const newPassenger = {
      type,
      globalIndex,
      poolIndex: indexInType,
      firstName: '',
      middleName: '',
      lastName: '',
      gender: '',
      dob: '',
      nationality: nationalities.length > 0 ? nationalities[Math.floor(Math.random() * nationalities.length)] : 'Philippines',
      passportNumber: 'P' + Math.floor(10000000 + Math.random() * 90000000),
      passport_expiry_date: (() => {
        const expiry = new Date();
        expiry.setFullYear(expiry.getFullYear() + Math.floor(Math.random() * 8) + 2);
        return expiry.toISOString().split('T')[0];
      })(),
      passenger_category: 'none',
      pwd_id_number: '',
      senior_id_number: '',
      associatedAdultIndex: null, // ✅ NEW: For infants to sit on an adult's lap
      selected_addons: [],
      addon_requirements: {}
    }

    if (students.value && students.value.length > 0) {
      const randomStudent = students.value[Math.floor(Math.random() * students.value.length)];
      newPassenger.firstName = randomStudent.first_name || '';
      newPassenger.middleName = randomStudent.middle_name || '';
      newPassenger.lastName = randomStudent.last_name || '';
      
      const assignGender = (firstName, providedGender) => {
        const g = (providedGender || '').toLowerCase();
        if (g === 'male' || g === 'm' || g === 'mr') return 'MR';
        if (g === 'female' || g === 'f' || g === 'mrs') return 'MRS';
        if (g === 'ms') return 'MS';
        const name = (firstName || '').toLowerCase();
        if (name.includes('june dominic')) return 'MR';
        if (name.includes('rose')) return ['MRS', 'MS'][Math.floor(Math.random() * 2)];
        const maleNames = ['james','john','robert','michael','william','david','richard','joseph','thomas','charles','christopher','daniel','matthew','anthony','mark','donald','steven','paul','andrew','joshua','kenneth','kevin','brian','george','edward','ronald','timothy','jason','jeffrey','ryan','jacob','gary','nicholas','eric','jonathan','stephen','larry','justin','scott','brandon','benjamin','samuel','gregory','frank','alexander','raymond','patrick','jack','dennis','jerry','tyler','aaron','jose','adam','henry','nathan','douglas','zachary','peter','kyle','walter','ethan','jeremy','christian','keith','roger','terry','gerald','harold','sean','austin','carl','arthur','lawrence','dylan','jesse','albert','bryan','joe','billy','bruce','willie','jordan','ralph','roy','noah','louis'];
        const femaleNames = ['rose','mary','patricia','jennifer','linda','elizabeth','barbara','susan','jessica','sarah','karen','nancy','lisa','betty','margaret','sandra','ashley','kimberly','emily','donna','michelle','dorothy','carol','amanda','melissa','deborah','stephanie','rebecca','sharon','laura','cynthia','kathleen','amy','shirley','angela','helen','anna','brenda','pamela','nicole','emma','samantha','katherine','christine','debora','rachel','catherine','carolyn','janet','ruth','maria','heather','diane','virginia','julie','joyce','victoria','olivia','kelly','christina','lauren','joan','evelyn','judith','megan','cheryl','andrea','hannah','martha','jacqueline','frances','gloria','ann','teresa','kathryn','sara','janice','jean','alice','madison','doris','abigail','julia','judy','grace','denise','amber','marilyn','beverly','danielle','theresa','sophia','marie','diana','brittany','natalie','isabella','charlotte','alexis','kayla'];
        const firstWord = name.split(' ')[0];
        if (maleNames.includes(firstWord)) return 'MR';
        if (femaleNames.includes(firstWord)) return ['MRS', 'MS'][Math.floor(Math.random() * 2)];
        if (/([aeiyou]|ah|ee|ie|ne|elle)$/.test(firstWord)) return ['MRS', 'MS'][Math.floor(Math.random() * 2)];
        return 'MR';
      };
      newPassenger.gender = assignGender(newPassenger.firstName, randomStudent.gender);
    }

    const birthDate = new Date();
    const pType = (type || '').toLowerCase();
    if (pType === 'infant') {
      const age = Math.floor(Math.random() * 2);
      birthDate.setFullYear(birthDate.getFullYear() - age);
    } else if (pType === 'child') {
      const age = Math.floor(Math.random() * 10) + 2;
      birthDate.setFullYear(birthDate.getFullYear() - age);
    } else {
      const age = Math.floor(Math.random() * 42) + 18;
      birthDate.setFullYear(birthDate.getFullYear() - age);
    }
    newPassenger.dob = birthDate.toISOString().split('T')[0];

    return newPassenger;
  }

  for (let i = 0; i < newAdultCount; i++) {
    newForms.push(getOrRestorePassenger('Adult', i))
    globalIndex++
  }
  for (let i = 0; i < newChildCount; i++) {
    newForms.push(getOrRestorePassenger('Child', i))
    globalIndex++
  }
  for (let i = 0; i < newInfantCount; i++) {
    newForms.push(getOrRestorePassenger('Infant', i))
    globalIndex++
  }

  passengerForms.value = newForms
  activityForm.instructions = generateDetailedInstructions()
}

const syncPassengerAddons = () => {
  if (!activityForm.require_addons) return;
  
  passengerForms.value.forEach(p => {
    // Infants never get add-ons
    if (p.type === 'Infant') {
      p.selected_addons = [];
      p.addon_requirements = {};
      return;
    }
    
    // Ensure all selected global addons are present in passenger's selection or if they are required
    activityForm.selected_addons.forEach(addonId => {
      const isGlobalRequired = addonRequirements[addonId]?.required;
      if (isGlobalRequired && !p.selected_addons.includes(addonId)) {
        p.selected_addons.push(addonId);
        p.addon_requirements[addonId] = { ...addonRequirements[addonId] };
      }
    });

    // Remove addons from passengers that are no longer in activityForm.selected_addons
    p.selected_addons = p.selected_addons.filter(id => activityForm.selected_addons.includes(id));
    Object.keys(p.addon_requirements).forEach(id => {
      if (!activityForm.selected_addons.includes(parseInt(id))) {
        delete p.addon_requirements[id];
      }
    });
  });
  
  activityForm.instructions = generateDetailedInstructions();
}

const getPassengersByType = (type) => {
  return passengerForms.value.filter(passenger => passenger.type === type)
}

const togglePassengerForms = () => {
  if (activityForm.require_passenger_details) {
    updatePassengerForms()
  } else {
    passengerForms.value = []
  }
}

const toggleAddons = () => {
  if (!activityForm.require_addons) {
    activityForm.selected_addons = []
    Object.keys(addonRequirements).forEach(key => {
      delete addonRequirements[key]
    })
  } else if (addons.value.length === 0) {
    fetchAirportsAndAddons()
  }
}

const toggleAddonRequirements = (addonId) => {
  if (activityForm.selected_addons.includes(addonId)) {
    if (!addonRequirements[addonId]) {
      addonRequirements[addonId] = {
        required: false,
        quantity: 1,
        notes: ''
      }
    }
  } else {
    delete addonRequirements[addonId]
  }
  syncPassengerAddons();
}

const togglePassengerAddon = (passenger, addonId) => {
  const index = passenger.selected_addons.indexOf(addonId);
  if (index === -1) {
    passenger.selected_addons.push(addonId);
    passenger.addon_requirements[addonId] = {
      ...(addonRequirements[addonId] || { required: false, quantity: 1, notes: '' })
    };
  } else {
    passenger.selected_addons.splice(index, 1);
    delete passenger.addon_requirements[addonId];
  }
  activityForm.instructions = generateDetailedInstructions();
}

const generateDetailedInstructions = () => {
  const formatDateSafe = (dateVal, options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) => {
    if (!dateVal) return 'Any';
    try {
      const d = new Date(dateVal);
      if (isNaN(d.getTime())) return 'Any';
      return d.toLocaleDateString('en-US', options);
    } catch (e) {
      return 'Any';
    }
  };

  let detailedInstructions = `ACADEMIC ASSESSMENT: ${activityForm.title || 'Untitled Activity'}\n\n`;
  
  if (activityForm.description) {
    detailedInstructions += `TASK OVERVIEW:\n${activityForm.description}\n\n`;
  }

  detailedInstructions += `TECHNICAL REQUIREMENTS:\n`;
  if (activityForm.total_points) {
    detailedInstructions += `• Total Points: ${activityForm.total_points} pts\n`;
  }
  if (activityForm.due_date) {
    detailedInstructions += `• Delivery Deadline: ${formatDateSafe(activityForm.due_date)}\n`;
  }
  detailedInstructions += `\n`;
  
  detailedInstructions += `TRIP DETAILS:\n`;
  const typeMap = { 'one_way': 'ONE-WAY', 'round_trip': 'ROUND-TRIP', 'multi_city': 'MULTI-CITY' };
  detailedInstructions += `You are required to book a ${typeMap[activityForm.required_trip_type] || 'FLIGHT'} trip `;
  detailedInstructions += `in ${activityForm.required_travel_class.toUpperCase().replace(/_/g, ' ')} class`;
  
  if (activityForm.required_seat_class && activityForm.required_seat_class.toLowerCase() !== 'any') {
    detailedInstructions += `, specifically the ${activityForm.required_seat_class.toUpperCase()} fare bundle.\n\n`;
  } else {
    detailedInstructions += `.\n\n`;
  }
  
  const originAirport = airports.value.find(a => a.code === activityForm.required_origin);
  const destinationAirport = airports.value.find(a => a.code === activityForm.required_destination);
  
  if (activityForm.required_trip_type === 'multi_city' && activityForm.segments.length > 0) {
    detailedInstructions += `ITINERARY SEGMENTS:\n`;
    activityForm.segments.forEach((seg, idx) => {
      const origin = airports.value.find(a => a.code === seg.origin)?.name || seg.origin || 'Any';
      const dest = airports.value.find(a => a.code === seg.destination)?.name || seg.destination || 'Any';
      const date = formatDateSafe(seg.departure_date, { month: 'long', day: 'numeric', year: 'numeric' });
      detailedInstructions += `Leg ${idx + 1}: ${seg.origin || 'Any'} (${origin}) to ${seg.destination || 'Any'} (${dest}) on ${date}\n`;
    });
    detailedInstructions += `\n`;
  } else {
    detailedInstructions += `ROUTE:\n`;
    
    if (originAirport) {
      detailedInstructions += `• Origin: ${originAirport.code} - ${originAirport.name}, ${originAirport.location}\n`;
    } else if (activityForm.required_origin) {
      detailedInstructions += `• Origin: ${activityForm.required_origin}\n`;
    } else {
      detailedInstructions += `• Origin: Any\n`;
    }
    
    if (destinationAirport) {
      detailedInstructions += `• Destination: ${destinationAirport.code} - ${destinationAirport.name}, ${destinationAirport.location}\n`;
    } else if (activityForm.required_destination) {
      detailedInstructions += `• Destination: ${activityForm.required_destination}\n`;
    } else {
      detailedInstructions += `• Destination: Any\n`;
    }
    
    detailedInstructions += `• Departure Date: ${formatDateSafe(activityForm.required_departure_date)}\n`;
    
    if (activityForm.required_trip_type === 'round_trip') {
      detailedInstructions += `• Return Date: ${formatDateSafe(activityForm.required_return_date)}\n`;
    }
    detailedInstructions += `\n`;
  }
  
  const totalPassengers = activityForm.required_passengers + activityForm.required_children + activityForm.required_infants;
  if (totalPassengers > 0) {
    detailedInstructions += `PASSENGERS:\n`;
    detailedInstructions += `You must book for the following passengers:\n`;
    if (activityForm.required_passengers > 0) {
      detailedInstructions += `• ${activityForm.required_passengers} Adult${activityForm.required_passengers > 1 ? 's' : ''} (12+ years)\n`;
    }
    if (activityForm.required_children > 0) {
      detailedInstructions += `• ${activityForm.required_children} Child${activityForm.required_children > 1 ? 'ren' : ''} (2-11 years)\n`;
    }
    if (activityForm.required_infants > 0) {
      detailedInstructions += `• ${activityForm.required_infants} Infant${activityForm.required_infants > 1 ? 's' : ''} (Under 2 years)\n`;
    }
    detailedInstructions += `\n`;
  }
  
  if (activityForm.require_passenger_details && passengerForms.value.length > 0) {
    detailedInstructions += `PASSENGER INFORMATION REQUIRED:\n`;
    detailedInstructions += `You MUST provide complete details for each passenger as follows:\n`;
    
    passengerForms.value.forEach((passenger) => {
      detailedInstructions += `\nPassenger ${passenger.globalIndex} (${passenger.type}):\n`;
      
      const fullName = [passenger.firstName, passenger.middleName, passenger.lastName].filter(n => n).join(' ');
      if (fullName) {
        detailedInstructions += `  • Full Name: ${fullName}\n`;
      }
      
      if (passenger.gender) {
        const gLabel = { 'MR': 'Mr.', 'MRS': 'Mrs.', 'MS': 'Ms.' }[passenger.gender.toUpperCase()] || passenger.gender;
        detailedInstructions += `  • Gender/Title: ${gLabel}\n`;
      }
      
      if (passenger.dob) {
        detailedInstructions += `  • Date of Birth: ${formatDateSafe(passenger.dob, { year: 'numeric', month: 'long', day: 'numeric' })}\n`;
      }
      
      if (passenger.nationality) {
        detailedInstructions += `  • Nationality: ${passenger.nationality}\n`;
      }
      
      const categoryMap = { 'none': 'Regular', 'senior': 'Senior Citizen', 'pwd': 'PWD' };
      const catLabel = categoryMap[passenger.passenger_category] || 'Regular';
      
      // Only show category for non-infants if it's not 'none', or if it's 'none' for clarity
      const pType = (passenger.type || '').toLowerCase();
      if (pType !== 'infant') {
        detailedInstructions += `  • Passenger Category: ${catLabel}\n`;
      } else if (passenger.associatedAdultIndex) {
        detailedInstructions += `  • Seating: Must sit on the lap of Passenger ${passenger.associatedAdultIndex} (Adult)\n`;
      }
      
      // ✅ PWD ID Number (only for PWD passengers)
      if (pType !== 'infant' && passenger.passenger_category === 'pwd' && passenger.pwd_id_number) {
        detailedInstructions += `  • PWD ID Number: ${passenger.pwd_id_number}\n`;
      }
      
      // ✅ Senior Citizen ID Number (only for Senior passengers)
      if (pType !== 'infant' && passenger.passenger_category === 'senior' && passenger.senior_id_number) {
        detailedInstructions += `  • Senior Citizen ID: ${passenger.senior_id_number}\n`;
      }
      
      // ✅ Passport Expiry Date (only for non-Philippines passengers)
      if (passenger.nationality && passenger.nationality !== 'Philippines' && passenger.passport_expiry_date) {
        detailedInstructions += `  • Passport Expiry Date: ${passenger.passport_expiry_date}\n`;
      }
      
      if (activityForm.require_passport && passenger.passportNumber) {
        detailedInstructions += `  • Passport Number: ${passenger.passportNumber}\n`;
      }

      // ✅ NEW: Display passenger-specific add-ons (Infants don't have them)
      if (activityForm.require_addons && passenger.selected_addons && passenger.selected_addons.length > 0) {
        detailedInstructions += `  • Add-ons:\n`;
        passenger.selected_addons.forEach(addonId => {
          const addon = addons.value.find(a => a.id === addonId);
          if (addon) {
            detailedInstructions += `    - ${addon.name} (Qty: ${passenger.addon_requirements[addonId]?.quantity || 1})\n`;
          }
        });
      }
    });
    detailedInstructions += `\n`;
  }
  


  
  detailedInstructions += `IMPORTANT NOTES:\n`;
  detailedInstructions += `• Double-check all passenger details for accuracy before submitting.\n`;
  detailedInstructions += `• Ensure the flight meets all the requirements specified above.\n`;
  detailedInstructions += `• Keep a record of your booking confirmation.\n`;
  if (activityForm.require_passport) {
    detailedInstructions += `• All passengers MUST have valid passport information.\n`;
  }
  if (activityForm.require_addons && activityForm.selected_addons.length > 0) {
    detailedInstructions += `• Add-ons must be selected according to the requirements above.\n`;
  }
  // ✅ PWD/Senior/Passport Expiry reminders
  const hasPwd = passengerForms.value.some(p => p.passenger_category === 'pwd');
  const hasSenior = passengerForms.value.some(p => p.passenger_category === 'senior');
  const hasNonPh = passengerForms.value.some(p => p.nationality && p.nationality !== 'Philippines');
  if (hasPwd) {
    detailedInstructions += `• PWD passengers must select the PWD discount category and provide their PWD ID number.\n`;
  }
  if (hasSenior) {
    detailedInstructions += `• Senior Citizen passengers must select the Senior Citizen discount and provide their Senior ID number.\n`;
  }
  if (hasNonPh) {
    detailedInstructions += `• Non-Philippine passport holders must provide a valid Passport Expiry Date.\n`;
  }
  
  return detailedInstructions;
};

// ✅ UPDATED: Randomize data using Students database and Valid Routes pool
const randomizeData = async () => {
  if (airports.value.length === 0 || addons.value.length === 0 || students.value.length === 0) {
    isLoadingData.value = true;
    await fetchAirportsAndAddons();
    isLoadingData.value = false;
  }

  if (airports.value.length === 0) {
    notificationStore.warn('⚠️ No airports available. Please check your database.');
    return;
  }

  if (students.value.length === 0) {
    notificationStore.warn('⚠️ No students available in the database. Please add students first.');
    return;
  }

  isLoadingData.value = true;

  // 1. Pick Basic Info (Outside retry)
  activityForm.title = sampleTitles[Math.floor(Math.random() * sampleTitles.length)] + ' ' + Math.floor(Math.random() * 1000);
  activityForm.activity_type = 'Flight Booking';
  activityForm.total_points = Math.floor(Math.random() * 50) + 50;
  
  const now = new Date();
  const dueDate = new Date(now.getTime() + (Math.floor(Math.random() * 14) + 7) * 24 * 60 * 60 * 1000);
  activityForm.due_date = dueDate.toISOString().slice(0, 16);

  const tripTypes = ['one_way', 'round_trip', 'multi_city'];
  
  // RETRY LOOP: Attempts to find a valid itinerary (max 5 tries)
  let attempts = 0;
  let success = false;
  
  while (attempts < 5 && !success) {
    attempts++;
    
    // 2. Pick Trip Type and Reset State
    activityForm.required_trip_type = tripTypes[Math.floor(Math.random() * tripTypes.length)];
    handleTripTypeChange();

    // 3. SMART Randomization from validRoutes
    if (validRoutes.value.length > 0) {
      const pool = [...validRoutes.value].sort(() => 0.5 - Math.random());
      
      if (activityForm.required_trip_type === 'one_way') {
        const route = pool[0];
        activityForm.required_origin = route.origin;
        activityForm.required_destination = route.destination;
        activityForm.required_departure_date = route.date;
        activityForm.required_return_date = '';
      } 
      else if (activityForm.required_trip_type === 'round_trip') {
        // Find a valid pair in the pool
        let pair = null;
        for (let outbound of pool) {
          let inbound = validRoutes.value.find(r => 
            r.origin === outbound.destination && 
            r.destination === outbound.origin && 
            new Date(r.date) > new Date(outbound.date)
          );
          if (inbound) {
            pair = { out: outbound, in: inbound };
            break;
          }
        }

        if (pair) {
          activityForm.required_origin = pair.out.origin;
          activityForm.required_destination = pair.out.destination;
          activityForm.required_departure_date = pair.out.date;
          activityForm.required_return_date = pair.in.date;
        } else {
          // Fallback: pick any route and guess return
          const route = pool[0];
          activityForm.required_origin = route.origin;
          activityForm.required_destination = route.destination;
          activityForm.required_departure_date = route.date;
          const retDate = new Date(new Date(route.date).getTime() + (Math.floor(Math.random() * 5) + 3) * 24 * 60 * 60 * 1000);
          activityForm.required_return_date = retDate.toISOString().split('T')[0];
        }
      }
      else if (activityForm.required_trip_type === 'multi_city') {
        activityForm.segments = [];
        let legs = [];
        let start = pool[Math.floor(Math.random() * Math.min(pool.length, 5))];
        legs.push(start);

        // Attempt to chain up to 3 additional segments (total 4 legs)
        let last = start;
        const targetSegments = Math.floor(Math.random() * 2) + 2; // Randomly pick 2 or 3 segments
        
        for (let i = 0; i < targetSegments; i++) {
          let next = validRoutes.value.find(r => 
            r.origin === last.destination && 
            new Date(r.date) >= new Date(last.date) &&
            !legs.some(l => l.origin === r.origin && l.destination === r.destination) // Avoid exact duplicates
          );
          
          if (!next) {
            // Fallback 1: Any flight from the current destination regardless of date
            next = validRoutes.value.find(r => r.origin === last.destination);
          }
          
          if (!next) {
            // Fallback 2: Any valid route that doesn't create a loop back to the start immediately
            next = validRoutes.value.find(r => r.origin !== last.origin && r.origin !== start.origin);
          }

          if (next) {
            legs.push(next);
            last = next;
          } else if (validRoutes.value.length > 0) {
            // Hard fallback: just pick a random valid route
            let flat = validRoutes.value[Math.floor(Math.random() * validRoutes.value.length)];
            legs.push(flat);
            last = flat;
          }
        }

        // 🚨 CRITICAL: Ensure we have at least 3 legs (at least 2 segments in the list)
        while (legs.length < 3 && validRoutes.value.length > 0) {
          let extra = validRoutes.value[Math.floor(Math.random() * validRoutes.value.length)];
          legs.push(extra);
        }

        activityForm.required_origin = legs[0].origin;
        activityForm.required_departure_date = legs[0].date;
        activityForm.required_destination = legs[0].destination;
        
        for (let i = 1; i < legs.length; i++) {
          activityForm.segments.push({
            origin: legs[i].origin,
            destination: legs[i].destination,
            departure_date: legs[i].date
          });
        }
      }
    } else {
      // Blind fallback
      const deptDate = new Date(now.getTime() + (Math.floor(Math.random() * 14) + 7) * 24 * 60 * 60 * 1000);
      activityForm.required_departure_date = deptDate.toISOString().split('T')[0];
      if (airports.value.length >= 2) {
        const shuffled = [...airports.value].sort(() => 0.5 - Math.random());
        activityForm.required_origin = shuffled[0].code;
        activityForm.required_destination = shuffled[1].code;
      }
    }

    // 4. VERIFY
    try {
      const params = {
        tripType: activityForm.required_trip_type,
        origin: activityForm.required_origin,
        destination: activityForm.required_destination,
        date: activityForm.required_departure_date,
        returnDate: activityForm.required_return_date,
        segments: activityForm.segments,
      }
      const available = await fetchFilteredTravelClasses(params)
      if (available && available.length > 0) {
        activityForm.required_travel_class = available[Math.floor(Math.random() * available.length)];
        
        const tc = activityForm.required_travel_class.toLowerCase();
        let bundles = [];
        if (tc.includes('economy') && !tc.includes('premium')) {
          bundles = ['Super Saver', 'Saver', 'Value', 'Flex'];
        } else if (tc.includes('premium')) {
          bundles = ['Premium Saver', 'Premium Value', 'Premium Flex'];
        } else if (tc.includes('business')) {
          bundles = ['Business Value', 'Business Flex'];
        }
        activityForm.required_seat_class = bundles.length > 0 ? bundles[Math.floor(Math.random() * bundles.length)] : '';
        
        success = true;
      }
    } catch (e) { success = false; }
  }

  isLoadingData.value = false;
  if (!success && travel_classes.value.length > 0) {
    activityForm.required_travel_class = travel_classes.value[0];
  }

  // 5. Populate rest of the data (Passengers, Addons, etc.)
  const pCategories = ['none', 'senior', 'pwd'];
  activityForm.required_passengers = Math.floor(Math.random() * 3) + 1;
  activityForm.required_children = Math.floor(Math.random() * 3);
  activityForm.required_infants = Math.min(Math.floor(Math.random() * 2), activityForm.required_passengers);
  activityForm.require_passenger_details = true;
  activityForm.require_passport = true;
  
  updatePassengerForms();

  passengerForms.value.forEach((p) => {
    if (!students.value || students.value.length === 0) return;
    const randomStudent = students.value[Math.floor(Math.random() * students.value.length)];
    p.firstName = randomStudent.first_name || '';
    p.middleName = randomStudent.middle_name || '';
    p.lastName = randomStudent.last_name || '';
    
    // Smart gender assignment based on name
    const assignGender = (firstName, providedGender) => {
      const g = (providedGender || '').toLowerCase();
      if (g === 'male' || g === 'm' || g === 'mr') return 'MR';
      if (g === 'female' || g === 'f' || g === 'mrs') return 'MRS';
      if (g === 'ms') return 'MS';
      
      const name = (firstName || '').toLowerCase();
      if (name.includes('june dominic')) return 'MR';
      if (name.includes('rose')) return ['MRS', 'MS'][Math.floor(Math.random() * 2)];
      
      const maleNames = ['james','john','robert','michael','william','david','richard','joseph','thomas','charles','christopher','daniel','matthew','anthony','mark','donald','steven','paul','andrew','joshua','kenneth','kevin','brian','george','edward','ronald','timothy','jason','jeffrey','ryan','jacob','gary','nicholas','eric','jonathan','stephen','larry','justin','scott','brandon','benjamin','samuel','gregory','frank','alexander','raymond','patrick','jack','dennis','jerry','tyler','aaron','jose','adam','henry','nathan','douglas','zachary','peter','kyle','walter','ethan','jeremy','christian','keith','roger','terry','gerald','harold','sean','austin','carl','arthur','lawrence','dylan','jesse','albert','bryan','joe','billy','bruce','willie','jordan','ralph','roy','noah','louis'];
      const femaleNames = ['rose','mary','patricia','jennifer','linda','elizabeth','barbara','susan','jessica','sarah','karen','nancy','lisa','betty','margaret','sandra','ashley','kimberly','emily','donna','michelle','dorothy','carol','amanda','melissa','deborah','stephanie','rebecca','sharon','laura','cynthia','kathleen','amy','shirley','angela','helen','anna','brenda','pamela','nicole','emma','samantha','katherine','christine','debora','rachel','catherine','carolyn','janet','ruth','maria','heather','diane','virginia','julie','joyce','victoria','olivia','kelly','christina','lauren','joan','evelyn','judith','megan','cheryl','andrea','hannah','martha','jacqueline','frances','gloria','ann','teresa','kathryn','sara','janice','jean','alice','madison','doris','abigail','julia','judy','grace','denise','amber','marilyn','beverly','danielle','theresa','sophia','marie','diana','brittany','natalie','isabella','charlotte','alexis','kayla'];
      
      const firstWord = name.split(' ')[0];
      if (maleNames.includes(firstWord)) return 'MR';
      if (femaleNames.includes(firstWord)) return ['MRS', 'MS'][Math.floor(Math.random() * 2)];
      
      // Fallback heuristic for unlisted names
      if (/([aeiyou]|ah|ee|ie|ne|elle)$/.test(firstWord)) return ['MRS', 'MS'][Math.floor(Math.random() * 2)];
      return 'MR';
    };

    p.gender = assignGender(p.firstName, randomStudent.gender);
    p.nationality = nationalities[Math.floor(Math.random() * nationalities.length)];
    p.passenger_category = pCategories[Math.floor(Math.random() * pCategories.length)];
    
    p.passportNumber = 'P' + Math.floor(10000000 + Math.random() * 90000000);

    const birthDate = new Date();
    const pType = (p.type || '').toLowerCase();
    
    if (pType === 'infant') {
      p.passenger_category = 'none';
      const age = Math.floor(Math.random() * 2);
      birthDate.setFullYear(birthDate.getFullYear() - age);
    } else if (pType === 'child') {
      if (p.passenger_category === 'senior') p.passenger_category = 'none';
      const age = Math.floor(Math.random() * 10) + 2;
      birthDate.setFullYear(birthDate.getFullYear() - age);
    } else {
      const age = p.passenger_category === 'senior' ? (Math.floor(Math.random() * 21) + 60) : (Math.floor(Math.random() * 42) + 18);
      birthDate.setFullYear(birthDate.getFullYear() - age);
    }
    p.dob = birthDate.toISOString().split('T')[0];

    // ✅ Generate PWD ID for PWD passengers (distinct format: PWD-XXXXXXX)
    if (p.passenger_category === 'pwd') {
      p.pwd_id_number = 'PWD-' + Math.floor(1000000 + Math.random() * 9000000);
      p.senior_id_number = '';
    } else if (p.passenger_category === 'senior') {
      // ✅ Generate Senior Citizen ID for Senior passengers (distinct format: SC-XXXXXXX)
      p.senior_id_number = 'SC-' + Math.floor(1000000 + Math.random() * 9000000);
      p.pwd_id_number = '';
    } else {
      p.pwd_id_number = '';
      p.senior_id_number = '';
    }

    // ✅ Generate Passport Expiry Date for ALL passengers
    const expiry = new Date();
    expiry.setFullYear(expiry.getFullYear() + Math.floor(Math.random() * 8) + 2); // 2–10 years from now
    expiry.setMonth(Math.floor(Math.random() * 12));
    expiry.setDate(Math.floor(Math.random() * 28) + 1);
    p.passport_expiry_date = expiry.toISOString().split('T')[0];
  });

  // ✅ Assign infants
  const adults = passengerForms.value.filter(p => (p.type || '').toLowerCase() === 'adult');
  const infants = passengerForms.value.filter(p => (p.type || '').toLowerCase() === 'infant');
  if (infants.length > 0 && adults.length > 0) {
    const shuffledAdults = [...adults].sort(() => 0.5 - Math.random());
    infants.forEach((infant, idx) => {
      infant.associatedAdultIndex = shuffledAdults[idx % shuffledAdults.length].globalIndex;
    });
  }

  // ✅ Addons randomization
  activityForm.selected_addons = [];
  Object.keys(addonRequirements).forEach(key => delete addonRequirements[key]);
  
  // Fetch relevant addons for the randomized route
  const pool = await fetchFilteredAddons();
  
  if (pool && pool.length > 0 && Math.random() > 0.3) {
    activityForm.require_addons = true;
    const numAddonsToSelect = Math.min(Math.floor(Math.random() * 3) + 1, pool.length);
    const shuffledAddons = [...pool].sort(() => 0.5 - Math.random());
    const selectedAddons = shuffledAddons.slice(0, numAddonsToSelect);
    
    selectedAddons.forEach((addon) => {
      activityForm.selected_addons.push(addon.id);
      addonRequirements[addon.id] = {
        required: Math.random() > 0.5,
        quantity: 1, // Default to 1 for randomization simplicity
        notes: Math.random() > 0.8 ? 'Special request for this add-on.' : ''
      };
    });

    passengerForms.value.forEach(p => {
      p.selected_addons = [];
      p.addon_requirements = {};
      
      const pType = (p.type || '').toLowerCase();
      if (pType === 'infant') return; // Infants never have add-ons

      activityForm.selected_addons.forEach(addonId => {
        const isRequired = addonRequirements[addonId].required;
        // If required globally, must select for passenger. Otherwise 50% chance.
        if (isRequired || Math.random() > 0.5) {
          p.selected_addons.push(addonId);
          p.addon_requirements[addonId] = {
            ...addonRequirements[addonId]
          };
        }
      });
    });
  }

  // ✅ Sync passengers to pool
  passengerForms.value.forEach(p => {
    const key = `${p.type}-${p.poolIndex ?? (passengerForms.value.filter(x => x.type === p.type).indexOf(p))}`;
    passengerPool.value[key] = { ...p };
  });

  activityForm.instructions = generateDetailedInstructions();
  showSuccess('Activity data randomized successfully!');
};

const validateActivityForm = () => {
  const errors = [];
  
  if (!activityForm.title?.trim()) errors.push("Activity title is required.");
  if (!activityForm.activity_type) errors.push("Activity type is required.");
  if (!activityForm.due_date) errors.push("Due date is required.");
  if (activityForm.total_points <= 0) errors.push("Total points must be greater than 0.");
  
  if (activityForm.require_passenger_details) {
    if (passengerForms.value.length === 0) {
      errors.push("At least one passenger is required when passenger details are enabled.");
    }
    
    passengerForms.value.forEach((p, index) => {
      const pLabel = `Passenger ${index + 1} (${p.type})`;
      if (!p.firstName?.trim()) errors.push(`${pLabel}: First name is required.`);
      if (!p.lastName?.trim()) errors.push(`${pLabel}: Last name is required.`);
      if (!p.dob) errors.push(`${pLabel}: Date of birth is required.`);
      if (!p.gender) errors.push(`${pLabel}: Gender is required.`);
      if (!p.nationality) errors.push(`${pLabel}: Nationality is required.`);
      
      if (activityForm.require_passport && !p.passportNumber?.trim()) {
        errors.push(`${pLabel}: Passport number is required.`);
      }
    });
  }
  
  if (activityForm.require_addons && activityForm.selected_addons.length === 0) {
     // If they enabled addons but didn't select any global ones, that might be okay depending on requirements,
     // but usually they should select at least one if the section is enabled.
     // However, let's keep it flexible unless there's a specific requirement.
  }

  return errors;
};

const submitActivity = async () => {
  const validationErrors = validateActivityForm();
  if (validationErrors.length > 0) {
    notificationStore.error(validationErrors[0]); // Show the first error
    return;
  }

  loading.value = true
  
  const hasAddons = passengerForms.value.some(p => p.selected_addons && p.selected_addons.length > 0);
  if (hasAddons) {
    activityForm.require_addons = true;
  }

  try {
    const sectionId = route.params.id

    const formattedPassengers = passengerForms.value.map((p, index) => {
      let passengerAddons = [];
      
      if (p.selected_addons && p.selected_addons.length > 0) {
        passengerAddons = p.selected_addons.map(addonId => ({
          id: addonId,
          is_required: p.addon_requirements[addonId]?.required || false,
          quantity: p.addon_requirements[addonId]?.quantity || 1,
          notes: p.addon_requirements[addonId]?.notes || ''
        }));
      }

      return {
        first_name: p.firstName,
        middle_name: p.middleName || "", 
        last_name: p.lastName,
        passenger_type: p.type.toLowerCase(), 
        gender: p.gender,
        date_of_birth: p.dob,
        nationality: p.nationality,
        passport_number: p.passportNumber || "",
        passport_expiry_date: p.passport_expiry_date || null,
        pwd_id_number: p.pwd_id_number || "",
        senior_id_number: p.senior_id_number || "",
        passenger_category: p.passenger_category || "none",
        associated_adult_index: p.associatedAdultIndex || null, // ✅ NEW
        selected_addons: passengerAddons
      }
    })

    const formData = {
      title: activityForm.title,
      activity_type: activityForm.activity_type,
      instructions: activityForm.instructions,
      description: activityForm.description,
      due_date: activityForm.due_date,
      total_points: activityForm.total_points,
      required_trip_type: activityForm.required_trip_type,
      required_travel_class: activityForm.required_travel_class,
      required_seat_class: activityForm.required_seat_class,
      required_origin: activityForm.required_origin,
      required_destination: activityForm.required_destination,
      required_departure_date: activityForm.required_departure_date || null,
      required_return_date: activityForm.required_return_date || null,
      required_passengers: activityForm.required_passengers,
      required_children: activityForm.required_children,
      required_infants: activityForm.required_infants,
      require_passport: activityForm.require_passport,
      require_passenger_details: activityForm.require_passenger_details,
      require_addons: activityForm.require_addons,
      passengers: formattedPassengers,
      segments: activityForm.required_trip_type === 'multi_city' ? activityForm.segments : []
    }
    
    console.log('Submitting activity data:', formData);
    
    const response = isEditing.value 
      ? await activityService.updateActivity(sectionId, editingActivityId.value, formData)
      : await activityService.createActivity(sectionId, formData);
    
    // Refresh data immediately so the list is updated
    fetchAllData()
    
    showSuccess(response.data.message || (isEditing.value ? 'Activity updated successfully!' : 'Activity created successfully!'))
    
    setTimeout(() => {
      closeActivityModal()
      resetActivityForm()
    }, 2000)
    
  } catch (error) {
    console.error("Submission error details:", error.response?.data)
    const errorMsg = error.response?.data?.error || error.response?.data?.detail || 'Failed to create activity.'
    notificationStore.error("Error: " + errorMsg)
  } finally {
    loading.value = false
  }
}

const toggleSidebar = () => { sidebarOpen.value = !sidebarOpen.value }
const toggleDropdown = () => { 
  dropdownOpen.value = !dropdownOpen.value 
  if (dropdownOpen.value) notificationDropdownOpen.value = false
}
const toggleNotificationDropdown = () => {
  notificationDropdownOpen.value = !notificationDropdownOpen.value
  if (notificationDropdownOpen.value) dropdownOpen.value = false
}

const userFullName = computed(() => userStore.user ? `${userStore.user.first_name} ${userStore.user.last_name}` : "Instructor")
const initials = computed(() => userStore.userInitials)

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const goToSection = (id) => { router.push(`/instructor/section/${id}`) }

const fetchAllData = async () => {
  isFetching.value = true
  try {
    const id = route.params.id;
    const detailData = await sectionDetailsService.getSectionDetails(id);
    section.value = detailData;
    activities.value = detailData.activities || [];
    
    const dashData = await instructorDashboardService.getDashboard();
    sidebarSections.value = dashData.sections || [];
    
    await userStore.ensureUserLoaded();
  } catch (error) {
    console.error("Failed to load section data", error)
  } finally {
    isFetching.value = false
  }
}

// Watchers
watch(() => activityForm.required_trip_type, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.title, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.activity_type, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.required_travel_class, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.required_seat_class, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.required_origin, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.required_destination, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.required_passengers, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.required_children, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.required_infants, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(passengerForms, () => {
  activityForm.instructions = generateDetailedInstructions();
}, { deep: true });

watch(() => activityForm.total_points, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.due_date, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.required_departure_date, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.required_return_date, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.required_passengers, () => {
  updatePassengerForms(); // ✅ This will preserve existing data
});

watch(() => activityForm.required_children, () => {
  updatePassengerForms(); // ✅ This will preserve existing data
});

watch(() => activityForm.required_infants, () => {
  updatePassengerForms(); // ✅ This will preserve existing data
});

watch(() => activityForm.segments, () => {
  activityForm.instructions = generateDetailedInstructions();
}, { deep: true });

watch(() => passengerForms.value, () => {
  activityForm.instructions = generateDetailedInstructions();
}, { deep: true });

watch(() => activityForm.require_addons, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.selected_addons, () => {
  activityForm.instructions = generateDetailedInstructions();
}, { deep: true });

watch(() => addonRequirements, () => {
  activityForm.instructions = generateDetailedInstructions();
}, { deep: true });





watch(() => activityForm.require_passport, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.description, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => activityForm.require_passenger_details, () => {
  activityForm.instructions = generateDetailedInstructions();
});

watch(() => route.params.id, () => { fetchAllData() })

onMounted(() => {
  fetchAllData()
  updatePassengerForms()
})
</script>

<style scoped>
/* Scrollable select for airport dropdowns */
select[size="5"] {
  height: auto !important;
  overflow-y: auto;
}

select[size="5"] option {
  padding: 8px 12px;
}

/* Success Modal Transition */
.success-fade-enter-active, .success-fade-leave-active {
  transition: opacity 0.3s ease;
}

.success-fade-enter-from, .success-fade-leave-to {
  opacity: 0;
}

.success-fade-enter-active > div {
  animation: success-bounce 0.5s ease;
}

@keyframes success-bounce {
  0% {
    transform: scale(0.8);
    opacity: 0;
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Animated Checkmark */
.success-checkmark {
  width: 80px;
  height: 80px;
  margin: 0 auto;
}

.check-icon {
  width: 80px;
  height: 80px;
  position: relative;
  border-radius: 50%;
  box-sizing: content-box;
  border: 4px solid #4CAF50;
}

.icon-line {
  height: 5px;
  background-color: #4CAF50;
  display: block;
  border-radius: 2px;
  position: absolute;
  z-index: 10;
}

.icon-line.line-tip {
  top: 46px;
  left: 14px;
  width: 25px;
  transform: rotate(45deg);
  animation: icon-line-tip 0.75s;
}

.icon-line.line-long {
  top: 38px;
  right: 8px;
  width: 47px;
  transform: rotate(-45deg);
  animation: icon-line-long 0.75s;
}

.icon-circle {
  top: -4px;
  left: -4px;
  z-index: 10;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  position: absolute;
  box-sizing: content-box;
  border: 4px solid rgba(76, 175, 80, 0.5);
}

.icon-fix {
  top: 8px;
  width: 5px;
  left: 26px;
  z-index: 1;
  height: 85px;
  position: absolute;
  transform: rotate(-45deg);
  background-color: #fff;
}

@keyframes icon-line-tip {
  0% {
    width: 0;
    left: 1px;
    top: 19px;
  }
  54% {
    width: 0;
    left: 1px;
    top: 19px;
  }
  70% {
    width: 50px;
    left: -8px;
    top: 37px;
  }
  84% {
    width: 17px;
    left: 21px;
    top: 48px;
  }
  100% {
    width: 25px;
    left: 14px;
    top: 45px;
  }
}

@keyframes icon-line-long {
  0% {
    width: 0;
    right: 46px;
    top: 54px;
  }
  65% {
    width: 0;
    right: 46px;
    top: 54px;
  }
  84% {
    width: 55px;
    right: 0px;
    top: 35px;
  }
  100% {
    width: 47px;
    right: 8px;
    top: 38px;
  }
}

/* Modal fade animation */
.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from, .modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active > div {
  animation: modal-slide 0.3s ease;
}

@keyframes modal-slide {
  0% {
    transform: translateY(-20px);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Line clamp for description */
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>