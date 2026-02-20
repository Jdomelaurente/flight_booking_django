<template>
  <div class="flex flex-col h-screen bg-[#FDFCF7] font-sans">
    <div class="bg-gradient-to-r from-pink-500 to-pink-400 text-white px-6 py-4 flex items-center justify-between shadow-md z-20">
      <div class="flex items-center gap-4">
        <button @click="toggleSidebar" class="p-2 hover:bg-pink-600 rounded-lg transition-colors focus:outline-none">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center text-2xl shadow-inner">🎓</div>
          <div>
            <h1 class="text-sm font-bold uppercase tracking-tight">CABAGAN STATE UNIVERSITY</h1>
            <p class="text-[10px] opacity-90">Cabagan City</p>
          </div>
        </div>
      </div>

      <div class="relative">
        <button @click="toggleDropdown" class="flex items-center gap-3 hover:bg-pink-600 p-2 rounded-lg transition-colors focus:outline-none">
          <span class="text-sm font-medium">{{ userFullName }}</span>
          <div class="w-10 h-10 bg-white rounded-full flex items-center justify-center overflow-hidden border-2 border-pink-300">
             <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-gray-600 font-bold uppercase">{{ initials }}</div>
          </div>
        </button>
        <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-100">
           <button @click="handleLogout" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 font-medium">Logout</button>
        </div>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <div :class="['bg-gradient-to-b from-pink-500 to-pink-400 text-white transition-all duration-300 ease-in-out flex flex-col z-10 shadow-lg', sidebarOpen ? 'w-64' : 'w-20']">
        <div class="flex flex-col h-full overflow-y-auto">
           <button @click="$router.push('/instructor/dashboard')" class="flex items-center py-4 hover:bg-pink-600 transition-colors border-b border-pink-400 justify-center">
             <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
             </svg>
             <span v-show="sidebarOpen" class="text-lg font-medium ml-3">Home</span>
           </button>
           <div v-for="sidebarSection in sidebarSections" :key="sidebarSection.id" @click="goToSection(sidebarSection.id)" :class="['flex items-center py-3 px-6 hover:bg-pink-600 cursor-pointer transition-colors border-b border-pink-400/20', route.params.id == sidebarSection.id ? 'bg-pink-700' : '']">
              <div class="w-8 h-8 rounded-full bg-white text-pink-500 flex items-center justify-center font-black text-xs flex-shrink-0 shadow-sm uppercase">
                {{ sidebarSection.section_name.charAt(0) }}
              </div>
              <span v-show="sidebarOpen" class="ml-3 truncate text-sm font-bold tracking-wide uppercase">{{ sidebarSection.section_name }}</span>
           </div>
        </div>
      </div>

      <div class="flex-1 overflow-auto bg-[#FDFCF7]">
        <div class="p-8">
          <div>
            <h2 class="text-4xl font-serif text-black font-bold">
              Section , {{ section?.section_code }} - {{ section?.section_name }}
            </h2>
          </div>
          <br>
          
          <div class="flex items-center gap-8 border-b border-gray-300 mb-8 px-2 relative">
            <button class="pb-3 text-sm font-black uppercase border-b-4 border-[#0E8028] text-gray-800">Activity</button>
            <button 
              @click="$router.push(`/instructor/section/${route.params.id}/people`)"
              :class="[
                'pb-3 text-sm font-black uppercase transition-colors',
                route.name === 'SectionPeople' ? 'border-b-4 border-[#0E8028] text-gray-800' : 'text-gray-400 hover:text-gray-600'
              ]"
            >
              People
            </button>
            <button class="pb-3 text-sm font-black uppercase text-gray-400 hover:text-gray-600">Settings</button>
            
            <div class="ml-auto flex gap-3 mb-2">
              <button @click="openEnrollModal" class="bg-[#F4D03F] text-[#0A3D16] px-5 py-2 rounded font-black text-[10px] uppercase shadow-md hover:scale-105 transition-transform">Add Student</button>
              <button 
                  @click="openActivityModal" 
                  class="bg-[#0E8028] text-white px-5 py-2 rounded font-black text-[10px] uppercase shadow-md hover:scale-105 transition-transform">
                  Add Task
              </button>
            </div>
          </div>

          <!-- Description Section -->
          <div class="grid grid-cols-1 gap-6 mb-6">
            <div class="bg-white rounded-lg border border-gray-200 p-8 shadow-sm">
              <h3 class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-4">Description</h3>
              <p class="text-gray-600 leading-relaxed italic">
                {{ section?.description || 'No description provided for this class.' }}
              </p>
            </div>
          </div>

          <!-- Activities List Section -->
          <div class="space-y-4 px-35">
            <!-- Activity Card -->
            <div 
              v-for="activity in activities" 
              :key="activity.id"
              class="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
            >
              <div class="p-6">
                <div class="flex items-start gap-4 h-auto">
                  <!-- Activity Icon -->
                  <div class="w-12 h-12 rounded-full bg-teal-600 flex items-center justify-center text-white font-bold text-lg flex-shrink-0">
                    {{ getActivityIcon(activity.title) }}
                  </div>
                  
                  <!-- Activity Content -->
                  <div class="flex-1 min-w-0 cursor-pointer" @click="goToActivity(activity.id)">
                    <div class="flex items-start justify-between mb-2">
                      <div class="truncate"> <h3 class="text-lg font-bold text-gray-800 truncate">
                          {{ activity.activity_type }}: {{ activity.title }}
                        </h3>
                        <p class="text-sm text-gray-500">
                          {{ formatDate(activity.due_date) }}
                        </p>
                      </div>
                    </div>
                    
                    <p class="text-gray-600 text-sm leading-relaxed line-clamp-3 break-words">
                      {{ activity.description || 'No description provided for this activity.' }}
                    </p>
                  </div>

                  <!-- Three Dots Menu -->
                  <div class="relative">
                    <button 
                      @click.stop="toggleActivityDropdown(activity.id)"
                      class="p-2 hover:bg-gray-100 rounded-full transition-colors"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600" viewBox="0 0 24 24" fill="currentColor">
                        <circle cx="12" cy="5" r="2"/>
                        <circle cx="12" cy="12" r="2"/>
                        <circle cx="12" cy="19" r="2"/>
                      </svg>
                    </button>
                    
                    <!-- Dropdown Menu -->
                    <div 
                      v-if="activityDropdowns[activity.id]"
                      class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200"
                    >
                      <button 
                        @click="openDeleteModal(activity)"
                        class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 font-medium"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline-block mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <polyline points="3 6 5 6 21 6"></polyline>
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                        Delete Activity
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Empty State -->
            <div v-if="activities.length === 0" class="bg-white rounded-lg border border-gray-200 p-12 text-center">
              <div class="text-gray-400 mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold text-gray-700 mb-2">No Activities Yet</h3>
              <p class="text-gray-500 mb-4">Get started by creating your first activity for this section.</p>
              <button 
                @click="openActivityModal"
                class="bg-[#0E8028] text-white px-6 py-2 rounded font-bold text-sm uppercase shadow-md hover:scale-105 transition-transform"
              >
                Create Activity
              </button>
            </div>
          </div>
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
      <div v-if="showSuccessModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-[60] backdrop-blur-sm">
        <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-md mx-4 transform transition-all">
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
            <label class="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Enter Student Number</label>
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
        <div class="bg-[#FF579A] px-6 py-4 flex justify-between items-center sticky top-0">
          <h2 class="text-xl font-semibold text-white">Create New Activity</h2>
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
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Travel Class *</label>
                    <select v-model="activityForm.required_travel_class" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]">
                      <option value="economy">Economy</option>
                      <option value="premium_economy">Premium Economy</option>
                      <option value="business">Business</option>
                      <option value="first">First Class</option>
                    </select>
                  </div>
                  <!-- Origin Airport Dropdown -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Origin Airport *</label>
                    <select v-model="activityForm.required_origin" required 
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]"
                      :disabled="airports.length === 0">
                      <option value="">{{ airports.length === 0 ? 'Loading airports...' : 'Select Origin Airport' }}</option>
                      <option v-for="airport in airports" :key="airport.code" :value="airport.code">
                        {{ airport.code }} - {{ airport.name }} ({{ airport.location }})
                      </option>
                    </select>
                    <p v-if="airports.length === 0" class="text-xs text-blue-500 mt-1">Loading airports...</p>
                  </div>

                  <!-- Destination Airport Dropdown -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Destination Airport *</label>
                    <select v-model="activityForm.required_destination" required 
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]"
                      :disabled="airports.length === 0">
                      <option value="">{{ airports.length === 0 ? 'Loading airports...' : 'Select Destination Airport' }}</option>
                      <option v-for="airport in airports" :key="airport.code" :value="airport.code">
                        {{ airport.code }} - {{ airport.name }} ({{ airport.location }})
                      </option>
                    </select>
                    <p v-if="airports.length === 0" class="text-xs text-blue-500 mt-1">Loading airports...</p>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Departure Date</label>
                    <input type="date" v-model="activityForm.required_departure_date" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]">
                  </div>
                  <div v-show="showReturnDate">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Return Date</label>
                    <input type="date" v-model="activityForm.required_return_date" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]">
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Max Price ($)</label>
                    <input type="number" v-model="activityForm.required_max_price" step="0.01" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]">
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Time Limit (minutes)</label>
                    <input type="number" v-model="activityForm.time_limit_minutes" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#093704]" placeholder="Optional time limit">
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
                            <label class="block text-xs font-medium text-gray-600 mb-1">Gender *</label>
                            <select v-model="passenger.gender" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400 text-sm">
                              <option value="">Select Gender</option>
                              <option value="male">Male</option>
                              <option value="female">Female</option>
                              <option value="other">Other</option>
                            </select>
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Date of Birth *</label>
                            <input type="date" v-model="passenger.dob" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Nationality *</label>
                            <input type="text" v-model="passenger.nationality" placeholder="Enter nationality" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Passport Number</label>
                            <input type="text" v-model="passenger.passportNumber" placeholder="Enter passport number" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400 text-sm">
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
                              <option value="male">Male</option>
                              <option value="female">Female</option>
                              <option value="other">Other</option>
                            </select>
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Date of Birth *</label>
                            <input type="date" v-model="passenger.dob" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Nationality *</label>
                            <input type="text" v-model="passenger.nationality" placeholder="Enter nationality" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Passport Number</label>
                            <input type="text" v-model="passenger.passportNumber" placeholder="Enter passport number" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-400 text-sm">
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
                              <option value="male">Male</option>
                              <option value="female">Female</option>
                              <option value="other">Other</option>
                            </select>
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Date of Birth *</label>
                            <input type="date" v-model="passenger.dob" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Nationality</label>
                            <input type="text" v-model="passenger.nationality" placeholder="Enter nationality" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-400 text-sm">
                          </div>
                          <div>
                            <label class="block text-xs font-medium text-gray-600 mb-1">Passport Number</label>
                            <input type="text" v-model="passenger.passportNumber" placeholder="Enter passport number" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-violet-400 text-sm">
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Add-ons Section -->
              <div class="border-t border-gray-200 pt-4">
                <div class="mb-6">
                  <div class="flex items-center mb-4">
                    <input 
                      type="checkbox" 
                      v-model="activityForm.require_addons" 
                      @change="toggleAddons" 
                      class="h-4 w-4 text-[#093704] focus:ring-[#093704] border-gray-300 rounded"
                    >
                    <label class="ml-2 block text-sm font-medium text-gray-700">
                      Enable Add-ons for Passengers
                    </label>
                  </div>

                  <!-- Add-ons Selection -->
                  <div v-if="activityForm.require_addons" class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <h4 class="text-sm font-medium text-gray-900 mb-3">Available Add-ons</h4>
                    
                    <!-- Loading state -->
                    <div v-if="isLoadingData" class="text-center py-4">
                      <p class="text-sm text-gray-500">Loading add-ons...</p>
                    </div>
                    
                    <!-- No addons available -->
                    <div v-else-if="addons.length === 0" class="text-center py-4">
                      <p class="text-sm text-gray-500">No add-ons available</p>
                    </div>
                    
                    <!-- Add-ons list -->
                    <div v-else class="space-y-3">
                      <div 
                        v-for="addon in addons" 
                        :key="addon.id" 
                        class="flex items-start p-3 bg-white rounded border border-gray-200 hover:border-[#FF579A] transition-colors"
                      >
                        <input 
                          type="checkbox" 
                          v-model="activityForm.selected_addons" 
                          :value="addon.id" 
                          @change="toggleAddonRequirements(addon.id)"
                          class="h-4 w-4 text-[#093704] focus:ring-[#093704] border-gray-300 rounded mt-1"
                        >
                        
                        <div class="ml-3 flex-1">
                          <div class="flex justify-between items-start">
                            <div>
                              <label class="text-sm font-medium text-gray-700">
                                {{ addon.name }}
                                <span v-if="addon.airline" class="text-xs text-gray-500">({{ addon.airline.code }})</span>
                              </label>
                              <p v-if="addon.type" class="text-xs text-gray-500">{{ addon.type.name }}</p>
                              <p class="text-xs text-gray-600">{{ addon.description || '' }}</p>
                            </div>
                            <span class="text-sm font-semibold text-[#FF579A]">₱{{ addon.price }}</span>
                          </div>
                          
                          <!-- Add-on requirements (shown when selected) -->
                          <div v-if="activityForm.selected_addons.includes(addon.id)" class="mt-3 p-3 bg-gray-50 rounded border border-gray-200">
                            <div class="flex items-center space-x-4 mb-2">
                              <div class="flex items-center">
                                <input 
                                  type="checkbox" 
                                  v-model="addonRequirements[addon.id].required" 
                                  class="h-3 w-3 text-[#093704] focus:ring-[#093704] border-gray-300 rounded"
                                >
                                <label class="ml-1 text-xs text-gray-600">
                                  Required for passengers
                                </label>
                              </div>
                              
                              <div class="flex items-center">
                                <label class="text-xs text-gray-600 mr-2">Quantity per passenger:</label>
                                <input 
                                  type="number" 
                                  v-model.number="addonRequirements[addon.id].quantity" 
                                  min="1" 
                                  max="10"
                                  class="w-16 px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-[#093704]"
                                >
                              </div>
                            </div>
                            
                            <div>
                              <label class="text-xs text-gray-600 block mb-1">Notes (optional):</label>
                              <textarea 
                                v-model="addonRequirements[addon.id].notes" 
                                rows="2"
                                class="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-[#093704]"
                                placeholder="Special instructions for this add-on..."
                              ></textarea>
                            </div>
                          </div>
                        </div>
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
                <span v-else>Create Activity</span>
              </button>
            </div>

          </form>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, computed, onMounted, watch, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api/axios'
import { sectionDetailsService } from '@/services/instructor/sectionDetailsService'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { activityService } from '@/services/instructor/activityService'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const notificationStore = useNotificationStore()

const section = ref(null)
const sidebarSections = ref([])
const userData = ref(null)
const sidebarOpen = ref(false)
const dropdownOpen = ref(false)

// Activities list
const activities = ref([])
const activityDropdowns = ref({}) // Track which dropdown is open

// Enroll Student Modal Logic
const isModalOpen = ref(false)
const studentNumberInput = ref('')
const loading = ref(false)

// Activity Modal Logic
const activityModalOpen = ref(false)
const showReturnDate = ref(false)
const passengerForms = ref([])

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
const isLoadingData = ref(false)

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
  required_max_price: 50000,
  time_limit_minutes: 60,
  required_passengers: 1,
  required_children: 0,
  required_infants: 0,
  require_passport: true,
  require_passenger_details: true,
  require_addons: false,
  selected_addons: [],
  description: ''
})

const addonRequirements = reactive({})

// --- Randomizer Data Pools ---
const sampleTitles = ['Flight Booking Assessment', 'Advanced Reservation Task', 'Round Trip Coordination', 'Emergency Rebooking', 'Group Booking', 'Multi-city Itinerary', 'Flight Activity', 'Travel Planning', 'Luxury Flight Arrangement', 'International Travel Simulation' , 'Budget Travel Challenge', 'Family Vacation Planning', 'Business Trip Coordination', 'Last-minute Booking', 'Holiday Travel Arrangement', 'Student Travel Task', 'Airport Transfer Booking', 'Frequent Flyer Challenge', 'Airline Comparison Activity', 'Travel Class Upgrade Simulation', 'Flight Change Scenario'];
const firstNames = ['James', 'Mary', 'Robert', 'Patricia', 'John', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth', 'David', 'Maria', 'Richard', 'Susan', 'Joseph', 'Rose' , 'Pathrick', 'Kyle', 'Samantha', 'Brian', 'Jessica', 'Kevin', 'Sarah', 'Thomas', 'Karen' , 'Charles', 'Nancy', 'Christopher', 'Lisa', 'Daniel', 'Betty' , 'Matthew', 'Margaret', 'Anthony', 'Sandra', 'Mark', 'Ashley', 'Donald', 'Kimberly', 'Steven', 'Emily', 'Paul', 'Donna', 'Andrew', 'Michelle' , 'Joshua', 'Dorothy', 'Kenneth', 'Carol', 'Kevin', 'Amanda'];
const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts' ];
const middleNames = ['Lee', 'Garcia', 'Quinto', 'Santos', 'Reyes', 'Cruz', 'Bautista', 'Ocampo', 'Mae', 'Ann', 'Marie', 'Louise' , 'James', 'John', 'Ray', 'Lynn', 'Grace', 'Rose', 'Mae', 'Jean', 'Paul', 'Mark', 'Jane', 'Louise', 'Michael', 'Elizabeth', 'Ann', 'Lee', 'Marie', 'Ray', 'Lynn', 'Grace', 'Rose', 'Jean', 'Paul', 'Mark', 'Jane', 'Louise'];
const nationalities = ['Filipino', 'American', 'Japanese', 'Canadian', 'Australian', 'British', 'Singaporean', 'Korean' , 'Chinese', 'German', 'French', 'Italian', 'Spanish', 'Mexican', 'Brazilian', 'Indian', 'Russian', 'Dutch', 'Swedish', 'Norwegian'];

const showSuccess = (message) => {
  successMessage.value = message
  showSuccessModal.value = true
  
  setTimeout(() => {
    showSuccessModal.value = false
  }, 3000)
}

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
  activityModalOpen.value = true
  isLoadingData.value = true
  
  airports.value = []
  addons.value = []
  students.value = [] // ✅ NEW: Reset students
  
  await fetchAirportsAndAddons()
  
  isLoadingData.value = false
  updatePassengerForms()
}

const closeActivityModal = () => {
  activityModalOpen.value = false
}

const handleTripTypeChange = () => {
  showReturnDate.value = activityForm.required_trip_type === 'round_trip'
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
    students.value = response.data.students || [] // ✅ NEW: Store students data
    
  } catch (error) {
    console.error('Failed to fetch airports and addons:', error)
    airports.value = []
    addons.value = []
    students.value = [] // ✅ NEW
  }
}

// ✅ UPDATED: Preserve existing passenger data when adding/removing passengers
const updatePassengerForms = () => {
  if (!activityForm.require_passenger_details) {
    passengerForms.value = []
    return
  }
  
  // ✅ Store existing passenger data temporarily
  const existingPassengers = [...passengerForms.value]
  
  // Calculate new total
  const newAdultCount = activityForm.required_passengers
  const newChildCount = activityForm.required_children
  const newInfantCount = activityForm.required_infants
  
  // Clear and rebuild
  passengerForms.value = []
  let globalIndex = 1
  
  // ✅ Helper function to find existing passenger or create new one
  const getOrCreatePassenger = (type, indexInType) => {
    // Try to find existing passenger of this type at this index
    const existing = existingPassengers.find(p => 
      p.type === type && 
      existingPassengers.filter(ep => ep.type === type).indexOf(p) === indexInType
    )
    
    if (existing) {
      // Return existing passenger with updated globalIndex
      return {
        ...existing,
        globalIndex: globalIndex
      }
    } else {
      // Create new empty passenger
      return {
        type: type,
        globalIndex: globalIndex,
        firstName: '',
        middleName: '',
        lastName: '',
        gender: '',
        dob: '',
        nationality: '',
        passportNumber: ''
      }
    }
  }
  
  // Add adults (preserve existing data)
  for (let i = 0; i < newAdultCount; i++) {
    passengerForms.value.push(getOrCreatePassenger('Adult', i))
    globalIndex++
  }
  
  // Add children (preserve existing data)
  for (let i = 0; i < newChildCount; i++) {
    passengerForms.value.push(getOrCreatePassenger('Child', i))
    globalIndex++
  }
  
  // Add infants (preserve existing data)
  for (let i = 0; i < newInfantCount; i++) {
    passengerForms.value.push(getOrCreatePassenger('Infant', i))
    globalIndex++
  }
  
  // ✅ IMPORTANT: Regenerate instructions after updating passengers
  if (activityForm.instructions) {
    activityForm.instructions = generateDetailedInstructions()
  }
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
}

const generateDetailedInstructions = () => {
  let detailedInstructions = `FLIGHT BOOKING ACTIVITY\n\n`;
  
  detailedInstructions += `TRIP DETAILS:\n`;
  detailedInstructions += `You are required to book a ${activityForm.required_trip_type === 'one_way' ? 'ONE-WAY' : 'ROUND-TRIP'} flight `;
  detailedInstructions += `in ${activityForm.required_travel_class.toUpperCase().replace('_', ' ')} class.\n\n`;
  
  const originAirport = airports.value.find(a => a.code === activityForm.required_origin);
  const destinationAirport = airports.value.find(a => a.code === activityForm.required_destination);
  
  if (originAirport || destinationAirport || activityForm.required_departure_date) {
    detailedInstructions += `ROUTE:\n`;
    
    if (originAirport) {
      detailedInstructions += `• Origin: ${originAirport.code} - ${originAirport.name}, ${originAirport.location}\n`;
    } else if (activityForm.required_origin) {
      detailedInstructions += `• Origin: ${activityForm.required_origin}\n`;
    }
    
    if (destinationAirport) {
      detailedInstructions += `• Destination: ${destinationAirport.code} - ${destinationAirport.name}, ${destinationAirport.location}\n`;
    } else if (activityForm.required_destination) {
      detailedInstructions += `• Destination: ${activityForm.required_destination}\n`;
    }
    
    if (activityForm.required_departure_date) {
      detailedInstructions += `• Departure Date: ${new Date(activityForm.required_departure_date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}\n`;
    }
    
    if (activityForm.required_trip_type === 'round_trip' && activityForm.required_return_date) {
      detailedInstructions += `• Return Date: ${new Date(activityForm.required_return_date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}\n`;
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
        detailedInstructions += `  • Gender: ${passenger.gender.charAt(0).toUpperCase() + passenger.gender.slice(1)}\n`;
      }
      
      if (passenger.dob) {
        detailedInstructions += `  • Date of Birth: ${new Date(passenger.dob).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}\n`;
      }
      
      if (passenger.nationality) {
        detailedInstructions += `  • Nationality: ${passenger.nationality}\n`;
      }
      
      if (activityForm.require_passport && passenger.passportNumber) {
        detailedInstructions += `  • Passport Number: ${passenger.passportNumber}\n`;
      }
    });
    detailedInstructions += `\n`;
  }
  
  if (activityForm.require_addons && activityForm.selected_addons.length > 0) {
    detailedInstructions += `ADD-ONS:\n`;
    detailedInstructions += `The following add-ons have been configured for this booking:\n\n`;
    
    activityForm.selected_addons.forEach((addonId) => {
      const addon = addons.value.find(a => a.id === addonId);
      if (addon) {
        const req = addonRequirements[addonId];
        detailedInstructions += `• ${addon.name}`;
        
        if (addon.airline) {
          detailedInstructions += ` (${addon.airline.code})`;
        }
        
        detailedInstructions += ` - ₱${addon.price}\n`;
        
        if (req) {
          detailedInstructions += `  Status: ${req.required ? 'REQUIRED' : 'Optional'}\n`;
          detailedInstructions += `  Quantity per passenger: ${req.quantity}\n`;
          if (req.notes) {
            detailedInstructions += `  Notes: ${req.notes}\n`;
          }
        }
        detailedInstructions += `\n`;
      }
    });
    detailedInstructions += `\n`;
  }
  
  if (activityForm.required_max_price && activityForm.required_max_price > 0) {
    detailedInstructions += `BUDGET CONSTRAINT:\n`;
    detailedInstructions += `• Maximum Total Price: ₱${parseFloat(activityForm.required_max_price).toLocaleString()}\n`;
    detailedInstructions += `• Ensure the total cost (including all passengers and add-ons) does not exceed this amount.\n\n`;
  }
  
  if (activityForm.time_limit_minutes && activityForm.time_limit_minutes > 0) {
    detailedInstructions += `TIME LIMIT:\n`;
    detailedInstructions += `• You have ${activityForm.time_limit_minutes} minutes to complete this booking.\n\n`;
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
  
  return detailedInstructions;
};

// ✅ UPDATED: Randomize data using Students database
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

  activityForm.title = sampleTitles[Math.floor(Math.random() * sampleTitles.length)] + ' ' + Math.floor(Math.random() * 1000);
  activityForm.activity_type = 'Flight Booking';
  activityForm.total_points = Math.floor(Math.random() * 50) + 50;
  
  const now = new Date();
  const dueDate = new Date(now.getTime() + (Math.floor(Math.random() * 14) + 7) * 24 * 60 * 60 * 1000);
  const deptDate = new Date(now.getTime() + (Math.floor(Math.random() * 30) + 14) * 24 * 60 * 60 * 1000);
  
  activityForm.due_date = dueDate.toISOString().slice(0, 16);
  activityForm.required_departure_date = deptDate.toISOString().split('T')[0];
  
  const tripTypes = ['one_way', 'round_trip'];
  activityForm.required_trip_type = tripTypes[Math.floor(Math.random() * tripTypes.length)];
  handleTripTypeChange();

  if (activityForm.required_trip_type === 'round_trip') {
    const retDate = new Date(deptDate.getTime() + (Math.floor(Math.random() * 7) + 3) * 24 * 60 * 60 * 1000);
    activityForm.required_return_date = retDate.toISOString().split('T')[0];
  } else {
    activityForm.required_return_date = '';
  }
  
  const classes = ['economy', 'premium_economy', 'business', 'first'];
  activityForm.required_travel_class = classes[Math.floor(Math.random() * classes.length)];
  
  if (airports.value.length >= 2) {
    const shuffled = [...airports.value].sort(() => 0.5 - Math.random());
    activityForm.required_origin = shuffled[0].code;
    let destIndex = 1;
    while (destIndex < shuffled.length && shuffled[destIndex].code === activityForm.required_origin) {
      destIndex++;
    }
    if (destIndex < shuffled.length) {
      activityForm.required_destination = shuffled[destIndex].code;
    } else {
      activityForm.required_destination = shuffled[1].code;
    }
  }

  // ✅ Randomize passenger counts
  activityForm.required_passengers = Math.floor(Math.random() * 3) + 1;
  activityForm.required_children = Math.floor(Math.random() * 3);
  activityForm.required_infants = Math.min(Math.floor(Math.random() * 2), activityForm.required_passengers);
  
  activityForm.require_passenger_details = true;
  activityForm.require_passport = Math.random() > 0.3;
  
  // ✅ Generate passenger forms FIRST
  updatePassengerForms();

  // ✅ NEW: Populate passenger data from Students database
  passengerForms.value.forEach((p) => {
    // Get random student from database
    const randomStudent = students.value[Math.floor(Math.random() * students.value.length)];
    
    // ✅ Fetch from Students database: firstName, lastName, middleName, gender
    p.firstName = randomStudent.first_name || '';
    p.middleName = randomStudent.middle_name || '';
    p.lastName = randomStudent.last_name || '';
    p.gender = randomStudent.gender || ['male', 'female'][Math.floor(Math.random() * 2)];
    
    // ✅ HARDCODED: nationality, passport, date of birth
    p.nationality = nationalities[Math.floor(Math.random() * nationalities.length)];
    
    if (activityForm.require_passport || Math.random() > 0.5) {
      p.passportNumber = 'P' + Math.floor(10000000 + Math.random() * 90000000);
    }

    const birthDate = new Date();
    if (p.type === 'Adult') {
      birthDate.setFullYear(birthDate.getFullYear() - (Math.floor(Math.random() * 50) + 18));
    } else if (p.type === 'Child') {
      birthDate.setFullYear(birthDate.getFullYear() - (Math.floor(Math.random() * 9) + 2));
    } else {
      birthDate.setFullYear(birthDate.getFullYear() - Math.floor(Math.random() * 2));
      birthDate.setMonth(Math.floor(Math.random() * 12));
    }
    p.dob = birthDate.toISOString().split('T')[0];
  });

  // ✅ Addons randomization
  activityForm.selected_addons = [];
  Object.keys(addonRequirements).forEach(key => delete addonRequirements[key]);
  
  if (addons.value && addons.value.length > 0 && Math.random() > 0.3) {
    activityForm.require_addons = true;
    
    const numAddonsToSelect = Math.min(Math.floor(Math.random() * 4) + 1, addons.value.length);
    const shuffledAddons = [...addons.value].sort(() => 0.5 - Math.random());
    const selectedAddons = shuffledAddons.slice(0, numAddonsToSelect);
    
    selectedAddons.forEach((addon) => {
      activityForm.selected_addons.push(addon.id);
      addonRequirements[addon.id] = {
        required: Math.random() > 0.5,
        quantity: Math.floor(Math.random() * 3) + 1,
        notes: Math.random() > 0.7 ? 'Priority service requested' : ''
      };
    });
  } else {
    activityForm.require_addons = false;
  }

  activityForm.required_max_price = Math.floor(Math.random() * 50000) + 10000;
  activityForm.time_limit_minutes = [30, 45, 60, 90, 120][Math.floor(Math.random() * 5)];

  // ✅ Generate instructions AFTER all data is filled
  activityForm.instructions = generateDetailedInstructions();
  
  showSuccess('Activity data randomized successfully!');
};

const submitActivity = async () => {
  loading.value = true
  try {
    const sectionId = route.params.id

    const formattedPassengers = passengerForms.value.map((p, index) => {
      let passengerAddons = [];
      
      if (activityForm.require_addons && activityForm.selected_addons.length > 0) {
        passengerAddons = activityForm.selected_addons.map(addonId => ({
          id: addonId,
          is_required: addonRequirements[addonId]?.required || false,
          quantity: addonRequirements[addonId]?.quantity || 1,
          notes: addonRequirements[addonId]?.notes || ''
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
      required_origin: activityForm.required_origin,
      required_destination: activityForm.required_destination,
      required_departure_date: activityForm.required_departure_date || null,
      required_return_date: activityForm.required_return_date || null,
      required_max_price: activityForm.required_max_price,
      time_limit_minutes: activityForm.time_limit_minutes,
      required_passengers: activityForm.required_passengers,
      required_children: activityForm.required_children,
      required_infants: activityForm.required_infants,
      require_passport: activityForm.require_passport,
      require_passenger_details: activityForm.require_passenger_details,
      require_addons: activityForm.require_addons,
      passengers: formattedPassengers
    }
    
    console.log('Submitting activity data:', formData);
    
    const response = await activityService.createActivity(sectionId, formData);
    
    showSuccess(response.data.message || 'Activity created successfully!')
    
    setTimeout(() => {
      closeActivityModal()
      
      Object.keys(activityForm).forEach(key => {
        if (typeof activityForm[key] === 'string') activityForm[key] = ''
        else if (typeof activityForm[key] === 'number') activityForm[key] = key === 'total_points' ? 100 : key === 'required_passengers' ? 1 : 0
        else if (Array.isArray(activityForm[key])) activityForm[key] = []
        else if (typeof activityForm[key] === 'boolean') activityForm[key] = key === 'require_passenger_details'
      })
      
      Object.keys(addonRequirements).forEach(key => delete addonRequirements[key])
      passengerForms.value = []

      fetchAllData()
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
const toggleDropdown = () => { dropdownOpen.value = !dropdownOpen.value }

const userFullName = computed(() => userStore.user ? `${userStore.user.first_name} ${userStore.user.last_name}` : "Instructor")
const initials = computed(() => userStore.userInitials)

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const goToSection = (id) => { router.push(`/instructor/section/${id}`) }

const fetchAllData = async () => {
  try {
    const id = route.params.id;
    const detailData = await sectionDetailsService.getSectionDetails(id);
    section.value = detailData;
    activities.value = detailData.activities || [];
    
    const dashData = await instructorDashboardService.getDashboard();
    this.sidebarSections = dashData.sections || [];
    
    await this.userStore.ensureUserLoaded();
  } catch (error) { 
    console.error("Failed to load section data", error) 
  }
}

// Watchers
watch(() => activityForm.required_trip_type, () => {
  if (activityForm.instructions) {
    activityForm.instructions = generateDetailedInstructions();
  }
});

watch(() => activityForm.required_travel_class, () => {
  if (activityForm.instructions) {
    activityForm.instructions = generateDetailedInstructions();
  }
});

watch(() => activityForm.required_origin, () => {
  if (activityForm.instructions) {
    activityForm.instructions = generateDetailedInstructions();
  }
});

watch(() => activityForm.required_destination, () => {
  if (activityForm.instructions) {
    activityForm.instructions = generateDetailedInstructions();
  }
});

watch(() => activityForm.required_departure_date, () => {
  if (activityForm.instructions) {
    activityForm.instructions = generateDetailedInstructions();
  }
});

watch(() => activityForm.required_return_date, () => {
  if (activityForm.instructions) {
    activityForm.instructions = generateDetailedInstructions();
  }
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

watch(() => passengerForms.value, () => {
  if (activityForm.instructions) {
    activityForm.instructions = generateDetailedInstructions();
  }
}, { deep: true });

watch(() => activityForm.require_addons, () => {
  if (activityForm.instructions) {
    activityForm.instructions = generateDetailedInstructions();
  }
});

watch(() => activityForm.selected_addons, () => {
  if (activityForm.instructions) {
    activityForm.instructions = generateDetailedInstructions();
  }
}, { deep: true });

watch(() => addonRequirements, () => {
  if (activityForm.instructions) {
    activityForm.instructions = generateDetailedInstructions();
  }
}, { deep: true });

watch(() => activityForm.required_max_price, () => {
  if (activityForm.instructions) {
    activityForm.instructions = generateDetailedInstructions();
  }
});

watch(() => activityForm.time_limit_minutes, () => {
  if (activityForm.instructions) {
    activityForm.instructions = generateDetailedInstructions();
  }
});

watch(() => activityForm.require_passport, () => {
  if (activityForm.instructions) {
    activityForm.instructions = generateDetailedInstructions();
  }
});

watch(() => activityForm.require_passenger_details, () => {
  if (activityForm.instructions) {
    activityForm.instructions = generateDetailedInstructions();
  }
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
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>