<template>
  <div class="p-0 m-0">
    <!-- Main Application UI (Hidden during print) -->
    <div class="max-w-7xl mx-auto p-4 lg:p-8 print:p-0 print:m-0 print:max-w-none">
      <!-- Main Content -->
      <div class="max-w-5xl mx-auto">
          
          <div class="flex justify-between items-center mb-6 print:hidden">
            <button @click="router.back()" class="flex items-center text-gray-500 hover:text-black font-bold text-sm uppercase">
              <span class="mr-2">←</span> BACK
            </button>
            <div class="flex gap-6 text-[11px] font-bold uppercase tracking-widest">
              <span 
                @click="activeTab = 'instructions'"
                :class="[activeTab === 'instructions' ? 'text-green-700 border-b-2 border-green-700 pb-1' : 'text-gray-400 cursor-pointer hover:text-gray-600']"
              >
                Instruction/s
              </span>
              <span 
                @click="activeTab = 'submissions'"
                :class="[activeTab === 'submissions' ? 'text-green-700 border-b-2 border-green-700 pb-1' : 'text-gray-400 cursor-pointer hover:text-gray-600']"
              >
                Student work
              </span>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-10 print:p-0 print:border-none print:shadow-none">
            <!-- Loading State (Skeleton UI) -->
            <div v-if="loading" class="animate-pulse">
              <div class="flex justify-between items-start mb-10">
                <div class="space-y-4 w-2/3">
                  <div class="h-10 bg-gray-200 rounded-lg w-3/4"></div>
                  <div class="h-4 bg-gray-100 rounded w-1/2"></div>
                  <div class="flex gap-2">
                    <div class="h-6 bg-gray-50 rounded w-20 border border-gray-100"></div>
                    <div class="h-6 bg-gray-50 rounded w-20 border border-gray-100"></div>
                  </div>
                </div>
                <div class="w-32 h-4 bg-gray-100 rounded"></div>
              </div>
              
              <div class="space-y-6">
                <!-- Activity Stats Skeleton -->
                <div class="grid grid-cols-3 gap-6 mb-10">
                  <div v-for="i in 3" :key="i" class="h-24 bg-gray-50 rounded-xl border border-gray-100"></div>
                </div>
                
                <!-- Content Placeholder -->
                <div class="space-y-4">
                  <div class="h-6 bg-gray-200 rounded w-48"></div>
                  <div class="space-y-2">
                    <div v-for="i in 5" :key="i" class="h-12 bg-gray-50 rounded border border-gray-100"></div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Activity Content -->
            <div v-else-if="activity" :class="isPrinting ? 'print:block' : ''">
              <div v-if="activeTab === 'instructions' && !isPrinting">
                <div class="flex justify-between items-start mb-8">
                  <div>
                    <h1 class="text-4xl font-light text-gray-900 tracking-wide">{{ activity.title || 'Untitled Activity' }}</h1>
                    <p class="text-xs text-gray-400 font-bold mt-2 uppercase tracking-widest">
                      {{ activity.section_code }} - {{ activity.section_name }}
                    </p>
                    <div class="flex gap-2 mt-3">
                      <span class="px-2 py-1 bg-blue-50 text-blue-600 text-xs font-bold rounded uppercase border border-blue-100">Flight Booking</span>
                      <span class="px-2 py-1 bg-green-50 text-green-600 text-xs font-bold rounded uppercase border border-green-100">
                        {{ activity.is_code_active ? 'Active' : 'Inactive' }}
                      </span>
                      <span class="px-2 py-1 bg-purple-50 text-purple-600 text-xs font-bold rounded uppercase border border-purple-100">
                        Weight: 100%
                      </span>
                    </div>
                  </div>
                  <div class="text-right">
                    <p class="text-xs font-bold text-gray-400 mb-2 uppercase tracking-widest">
                      Due: {{ activity.due_date || 'No due date' }}
                    </p>
                    <div v-if="activity.is_code_active" class="bg-green-100 text-green-700 px-4 py-2 rounded-lg text-xs font-bold border border-green-200">
                      Active Code: {{ activity.activity_code }}
                    </div>
                    <div v-else class="bg-gray-100 text-gray-400 px-4 py-2 rounded-lg text-xs font-bold">
                      Activity code: Not yet Activated
                    </div>
                  </div>
                </div>

                <hr class="mb-8 border-gray-100" />

                <!-- Instructions -->
                <div class="mb-10">
                  <h3 class="text-xs font-black uppercase text-gray-800 mb-4 tracking-widest">Instructions</h3>
                  <div class="border border-gray-100 bg-gray-50/50 p-6 rounded-xl italic text-gray-600 text-sm leading-relaxed whitespace-pre-wrap">
                    {{ activity.instructions || 'No instructions provided.' }}
                  </div>
                </div>

                <!-- Flight Requirements -->
                <div class="mb-10">
                  <h3 class="text-sm font-bold mb-4 text-gray-800">Flight Requirements</h3>
                  <div class="flex gap-2 mb-6">
                    <span class="bg-[#FFC145] px-6 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider">
                      {{ formatRequirement(activity.required_trip_type) || 'N/A' }}
                    </span>
                    <span class="bg-[#0D3111] text-white px-6 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider">
                      {{ formatRequirement(activity.required_travel_class) || 'N/A' }}
                    </span>
                    <span v-if="activity.required_seat_class" class="bg-gray-800 text-white px-6 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider">
                      {{ formatRequirement(activity.required_seat_class) }}
                    </span>
                  </div>

                  <!-- Dynamic Flight Requirements based on trip type -->
                  <div v-if="(activity.required_trip_type || '').toLowerCase().replace(/\s+/g, '_') !== 'multi_city'" class="border border-yellow-200 rounded-3xl py-6 px-10 flex items-center justify-between bg-white relative overflow-hidden">
                    <div class="text-center">
                      <p class="text-xs text-gray-400 uppercase font-bold tracking-widest">From</p>
                      <p class="text-xl font-bold text-gray-900">{{ activity.required_origin || '-' }}</p>
                    </div>
                    <div class="text-center">
                      <p class="text-xs text-gray-400 uppercase font-bold tracking-widest">To</p>
                      <p class="text-xl font-bold text-gray-900">{{ activity.required_destination || '-' }}</p>
                    </div>
                    <div class="h-10 w-[1px] bg-gray-200 mx-2"></div>
                    <div class="text-center">
                      <p class="text-xs text-gray-400 uppercase font-bold tracking-widest">Depart</p>
                      <p class="text-sm font-bold text-gray-800">{{ activity.required_departure_date || 'N/A' }}</p>
                    </div>
                    <div class="text-center" v-if="activity.required_trip_type !== 'one_way'">
                      <p class="text-xs text-gray-400 uppercase font-bold tracking-widest">Return</p>
                      <p class="text-sm font-bold text-gray-800">{{ activity.required_return_date || 'N/A' }}</p>
                    </div>
                    <div class="h-10 w-[1px] bg-gray-200 mx-2"></div>
                    <div class="text-center">
                      <p class="text-xs text-gray-400 uppercase font-bold tracking-widest">Passenger</p>
                      <p class="text-xs text-gray-700">
                        Adult: <b>{{ activity.required_passengers || 0 }}</b> 
                        child: <b>{{ activity.required_children || 0 }}</b> 
                        infant: <b>{{ activity.required_infants || 0 }}</b>
                      </p>
                    </div>
                  </div>

                  <!-- Multi-City / Round Trip Segments -->
                  <div v-else class="space-y-3">
                    <div v-for="(segment, idx) in activity.segments" :key="idx" class="border border-yellow-200 rounded-2xl py-4 px-8 flex items-center justify-between bg-white relative overflow-hidden">
                      <div class="absolute left-0 top-0 bottom-0 w-1.5 bg-yellow-400"></div>
                      <div class="flex items-center gap-6">
                        <div class="w-8 h-8 rounded-full bg-yellow-50 flex items-center justify-center font-bold text-yellow-600 text-xs shadow-sm">
                          {{ idx + 1 }}
                        </div>
                        <div class="flex items-center gap-10">
                          <div class="text-center">
                            <p class="text-[9px] text-gray-400 uppercase font-black tracking-widest">From</p>
                            <p class="text-lg font-bold text-gray-900 uppercase">{{ segment.origin }}</p>
                          </div>
                          <div class="flex flex-col items-center">
                            <div class="w-12 h-[1px] bg-gray-200 relative mb-1">
                              <div class="absolute -top-1 -right-0.5 text-[8px] text-gray-300">▶</div>
                            </div>
                          </div>
                          <div class="text-center">
                            <p class="text-[9px] text-gray-400 uppercase font-black tracking-widest">To</p>
                            <p class="text-lg font-bold text-gray-900 uppercase">{{ segment.destination }}</p>
                          </div>
                          <div class="ml-4">
                            <p class="text-[9px] text-gray-400 uppercase font-black tracking-widest">Departure Date</p>
                            <p class="text-xs font-bold text-gray-700">{{ segment.departure_date || 'N/A' }}</p>
                          </div>
                        </div>
                      </div>
                      
                      <div v-if="idx === 0" class="text-right border-l border-gray-100 pl-8">
                        <p class="text-[9px] text-gray-400 uppercase font-black tracking-widest mb-1">Passengers</p>
                        <p class="text-[10px] text-gray-700 font-medium">
                          Adult: <b>{{ activity.required_passengers || 0 }}</b><br>
                          Child: <b>{{ activity.required_children || 0 }}</b><br>
                          Infant: <b>{{ activity.required_infants || 0 }}</b>
                        </p>
                      </div>
                      <div v-else class="w-24"></div> <!-- Spacer for other rows -->
                    </div>
                  </div>
                </div>

                <!-- Passenger Information -->
                <div class="border border-gray-200 rounded-xl p-8 bg-white">
                  <h3 class="text-lg font-bold mb-8 text-gray-800">Passenger Information</h3>
                  <div v-if="activity.passengers && activity.passengers.length > 0">
                    <div v-for="(p, index) in activity.passengers" :key="index" class="mb-10 last:mb-0 border-b border-gray-50 pb-8 last:border-0">
                      <div class="flex justify-between items-center mb-6">
                        <h4 class="font-black text-sm text-gray-900 uppercase tracking-tight">
                          Passenger {{ index + 1 }} ({{ p.type || 'Adult' }})
                        </h4>
                        <span v-if="p.seat_preference" class="text-xs font-bold uppercase tracking-widest text-gray-800">
                          seat preference: <span class="text-gray-400">{{ p.seat_preference }}</span>
                        </span>
                      </div>
                      
                      <!-- Dynamic Passenger Fields Grid -->
                      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                        <!-- Gender -->
                        <div v-if="hasValue(p.gender)">
                          <label class="text-xs font-bold text-red-500 uppercase tracking-tight">Gender*</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 text-gray-700">
                            {{ formatGender(p.gender) }}
                          </div>
                        </div>
                        
                        <!-- First Name -->
                        <div v-if="hasValue(p.first_name)">
                          <label class="text-[9px] font-black text-red-500 uppercase">First Name*</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                            {{ p.first_name }}
                          </div>
                        </div>
                        
                        <!-- Middle Name -->
                        <div v-if="hasValue(p.middle_name)">
                          <label class="text-[9px] font-black text-gray-400 uppercase">Middle Name</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                            {{ p.middle_name }}
                          </div>
                        </div>
                        
                        <!-- Last Name -->
                        <div v-if="hasValue(p.last_name)">
                          <label class="text-[9px] font-black text-red-500 uppercase">Last Name*</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                            {{ p.last_name }}
                          </div>
                        </div>
                        
                        <!-- Date of Birth -->
                        <div v-if="hasValue(p.date_of_birth)">
                          <label class="text-[9px] font-black text-red-500 uppercase">Date of Birth*</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                            {{ formatDate(p.date_of_birth) }}
                          </div>
                        </div>
                        
                        <!-- Nationality -->
                        <div v-if="hasValue(p.nationality)">
                          <label class="text-[9px] font-black text-red-500 uppercase">Nationality*</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                            {{ p.nationality }}
                          </div>
                        </div>

                        <!-- Passenger Category -->
                        <div>
                          <label class="text-[9px] font-black text-red-500 uppercase">Category*</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                            {{ p.passenger_category === 'senior' ? 'Senior Citizen' : (p.passenger_category === 'pwd' ? 'PWD' : 'Regular') }}
                          </div>
                        </div>

                        <!-- PWD ID Number (shown only for PWD passengers) -->
                        <div v-if="p.passenger_category === 'pwd' && hasValue(p.pwd_id_number)">
                          <label class="text-[9px] font-black text-blue-600 uppercase">PWD ID Number*</label>
                          <div class="mt-1 p-3 border border-blue-200 rounded-lg text-xs bg-blue-50/50 uppercase text-blue-800 font-mono">
                            {{ p.pwd_id_number }}
                          </div>
                        </div>

                        <!-- Senior Citizen ID (shown only for Senior passengers) -->
                        <div v-if="p.passenger_category === 'senior' && hasValue(p.senior_id_number)">
                          <label class="text-[9px] font-black text-amber-600 uppercase">Senior Citizen ID*</label>
                          <div class="mt-1 p-3 border border-amber-200 rounded-lg text-xs bg-amber-50/50 uppercase text-amber-800 font-mono">
                            {{ p.senior_id_number }}
                          </div>
                        </div>

                        <!-- Passport Expiry Date (shown only for non-Philippines nationality) -->
                        <div v-if="p.nationality && p.nationality.toLowerCase() !== 'philippines' && hasValue(p.passport_expiry_date)">
                          <label class="text-[9px] font-black text-red-500 uppercase">Passport Expiry*</label>
                          <div class="mt-1 p-3 border border-red-200 rounded-lg text-xs bg-red-50/50 uppercase text-red-800">
                            {{ p.passport_expiry_date }}
                          </div>
                        </div>
                        
                        <!-- Passport Number -->
                        <div v-if="hasValue(p.passport_number)">
                          <label class="text-[9px] font-black text-red-500 uppercase">Passport Number*</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 uppercase text-gray-700">
                            {{ p.passport_number }}
                          </div>
                        </div>
                        
                        <!-- Email -->
                        <div v-if="hasValue(p.email)">
                          <label class="text-[9px] font-black text-gray-400 uppercase">Email</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 text-gray-700">
                            {{ p.email }}
                          </div>
                        </div>
                        
                        <!-- Phone -->
                        <div v-if="hasValue(p.phone)">
                          <label class="text-[9px] font-black text-gray-400 uppercase">Phone</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 text-gray-700">
                            {{ p.phone }}
                          </div>
                        </div>
                        
                        <!-- Special Requirements -->
                        <div v-if="hasValue(p.special_requirements)" class="md:col-span-4">
                          <label class="text-[9px] font-black text-gray-400 uppercase">Special Requirements</label>
                          <div class="mt-1 p-3 border border-gray-200 rounded-lg text-xs bg-gray-50/50 text-gray-700">
                            {{ p.special_requirements }}
                          </div>
                        </div>
                        
                        <!-- Passenger Add-ons -->
                        <div v-if="getPassengerAddons(p).length > 0" class="md:col-span-4 mt-2">
                          <label class="text-[9px] font-black text-pink-500 uppercase tracking-wide">Assigned Add-ons</label>
                          <div class="mt-1 flex flex-wrap gap-2">
                            <span v-for="addon in getPassengerAddons(p)" :key="addon.id" class="px-3 py-1.5 bg-pink-50 border border-pink-200 text-pink-700 rounded-md text-xs font-bold shadow-sm">
                              {{ addon.addon_name }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-center py-10 text-gray-400">
                    No passenger information available.
                  </div>
                </div>
                
                <!-- Add-on & Insurance Requirements -->
                <div v-if="activity.activity_addons && activity.activity_addons.length > 0" class="mt-10 mb-10">
                  <h3 class="text-xs font-black uppercase text-gray-800 mb-4 tracking-widest">Add-ons & Insurance Requirements</h3>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div v-for="aa in activity.activity_addons" :key="aa.id" class="border border-pink-100 rounded-xl p-4 bg-pink-50/30 flex items-center justify-between">
                      <div>
                        <p class="text-xs font-bold text-gray-900 leading-tight">{{ aa.addon_name }}</p>
                        <p class="text-[10px] text-gray-400 mt-1 uppercase font-bold tracking-tight">
                          Assign to: {{ aa.passenger?.first_name }} {{ aa.passenger?.last_name || 'Passenger' }}
                        </p>
                      </div>
                      <div class="bg-white text-pink-500 h-8 w-8 rounded-full flex items-center justify-center shadow-sm border border-pink-100">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                        </svg>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Activate Button -->
                <div class="mt-12 flex flex-col items-center">
                  <div v-if="activity.is_code_active && eligibleStudents.length > 0" class="mb-4 text-center">
                    <p class="text-xs text-gray-400 font-bold uppercase tracking-widest mb-2">
                       {{ eligibleStudents.length }} student(s) haven't received this activity yet
                    </p>
                    <button 
                      @click="openActivationModal"
                      :disabled="activating"
                      class="px-8 py-3 bg-pink-500 hover:bg-pink-600 text-white rounded-xl font-bold text-xs uppercase tracking-widest transition-all shadow-md active:scale-95 disabled:opacity-50"
                    >
                      Release to more students
                    </button>
                  </div>

                  <button 
                    v-if="!activity.is_code_active"
                    @click="openActivationModal"
                    :disabled="activating"
                    class="w-full max-w-lg bg-[#FFC145] hover:bg-yellow-500 disabled:bg-gray-200 disabled:text-gray-400 py-4 rounded-xl font-bold text-sm uppercase tracking-widest transition-all shadow-md active:scale-95 disabled:cursor-not-allowed"
                  >
                    {{ activating ? 'Processing...' : 'Activate' }}
                  </button>
                  
                  <div v-else-if="eligibleStudents.length === 0" class="text-center py-4 px-8 bg-green-50 rounded-xl border border-green-100">
                     <p class="text-xs font-bold text-green-700 uppercase tracking-widest">Released to all students</p>
                  </div>
                </div>
              </div>

              <!-- Student Work Tab Content -->
              <InstructorSubmission 
                v-else-if="activeTab === 'submissions' || isPrinting"
                :activity="activity"
                :submissions="submissions"
                :submissions_loading="submissionsLoading"
                :releasing_grades="releasingGrades"
                :is_printing="isPrinting"
                @release-grades="handleReleaseGrades"
                @print="handlePrint"
                @refresh="fetchSubmissions"
                @view-analysis="goToAnalysis"
              />
            </div>

            <!-- Error State -->
            <div v-else class="text-center py-20">
              <p class="text-red-400 font-bold uppercase mb-2">Failed to load activity details.</p>
              <p class="text-gray-400 text-xs italic mb-4">{{ errorMessage }}</p>
              <button 
                @click="fetchData" 
                class="px-6 py-2 bg-pink-500 text-white rounded-lg hover:bg-pink-600 transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
      </div>
    </div>

    <!-- Success Modal -->
    <div v-if="showSuccessModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-white p-10 rounded-2xl text-center shadow-2xl max-w-sm w-full border border-gray-100">
        <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6 text-4xl shadow-inner">✅</div>
        <h2 class="text-2xl font-black mb-2 uppercase text-gray-900 tracking-tight">Activated</h2>
        <p class="text-gray-500 text-[11px] mb-8 leading-relaxed font-medium">Activity has been assigned to the selected students. Share this code with them:</p>
        <div class="bg-gray-50 text-4xl font-mono font-black py-5 rounded-2xl tracking-widest text-pink-600 border-2 border-dashed border-pink-200 mb-8 uppercase shadow-sm">
          {{ activity?.activity_code }}
        </div>
        <button @click="showSuccessModal = false" class="w-full bg-slate-900 text-white py-4 rounded-xl font-bold uppercase text-xs tracking-widest hover:bg-black transition-all shadow-lg active:scale-95">Complete</button>
      </div>
    </div>

    <!-- Activation Student Selection Modal -->
    <div v-if="showActivationModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div class="bg-white rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden border border-gray-100 flex flex-col max-h-[90vh]">
        <!-- Modal Header -->
        <div class="p-8 border-b border-gray-50 bg-gray-50/30">
          <div class="flex justify-between items-start mb-2">
            <div>
              <h2 class="text-2xl font-black uppercase text-gray-900 tracking-tight">Select Students</h2>
              <p class="text-[10px] font-bold text-pink-500 uppercase tracking-widest mt-1">
                {{ activity?.is_code_active ? 'Re-releasing to remaining students' : 'Assigning students to activity' }}
              </p>
            </div>
            <button @click="showActivationModal = false" class="text-gray-400 hover:text-gray-600 p-2 rounded-full hover:bg-gray-100 transition-all">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Selection Controls -->
        <div class="px-8 py-4 bg-white border-b border-gray-50 flex items-center justify-between">
          <label class="flex items-center gap-3 cursor-pointer group">
            <div class="relative flex items-center justify-center w-5 h-5 border-2 border-gray-200 rounded-md group-hover:border-gray-200 transition-colors" :class="isAllSelected ? 'bg-pink-500 border-pink-500' : 'bg-white'">
              <input type="checkbox" class="absolute inset-0 opacity-0 cursor-pointer" :checked="isAllSelected" @change="toggleSelectAll">
              <svg v-if="isAllSelected" class="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="4">
                <path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </div>
            <span class="text-[11px] font-black uppercase tracking-widest text-gray-500 group-hover:text-pink-600 transition-colors">Select All ({{ eligibleStudents.length }})</span>
          </label>
          <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">{{ selectedStudentIds.length }} Selected</span>
        </div>

        <!-- Student List -->
        <div class="overflow-y-auto max-h-[400px] p-4 bg-gray-50/20">
          <div v-if="eligibleStudents.length === 0" class="text-center py-10 italic text-gray-400 text-sm">
            All enrolled students have already received this activity.
          </div>
          <div v-else class="space-y-2">
            <!-- Time Limit Input -->
            <div class="mb-6 p-4 bg-white rounded-2xl border border-pink-100 shadow-sm">
              <label class="block text-[10px] font-black text-pink-500 uppercase tracking-widest mb-2">Activity Time Limit (Minutes)</label>
              <div class="flex items-center gap-4">
                <input 
                  type="number" 
                  v-model="timeLimit"
                  min="1"
                  class="flex-1 bg-gray-50 border border-gray-100 rounded-xl px-4 py-3 text-sm font-bold focus:ring-2 focus:ring-pink-500 focus:border-transparent outline-none transition-all"
                  placeholder="Enter minutes..."
                >
                <div class="text-[10px] font-bold text-gray-400 uppercase">Minutes</div>
              </div>
              <p class="mt-2 text-[9px] text-gray-400 italic">Students will have this much time to complete the activity once they start.</p>
            </div>

            <div 
              v-for="student in eligibleStudents" 
              :key="student.id"
              @click="toggleStudentSelection(student.id)"
              class="flex items-center justify-between p-4 bg-white rounded-2xl border transition-all cursor-pointer hover:shadow-md active:scale-[0.98]"
              :class="selectedStudentIds.includes(student.id) ? 'border-pink-500 shadow-sm ring-1 ring-pink-500/10' : 'border-gray-100 hover:border-pink-200'"
            >
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center font-bold text-slate-500 uppercase text-xs">
                  {{ student.first_name[0] }}{{ student.last_name[0] }}
                </div>
                <div>
                  <h3 class="text-sm font-bold text-gray-900 leading-tight">{{ student.first_name }} {{ student.last_name }}</h3>
                  <p class="text-[10px] text-gray-400 font-bold tracking-widest mt-0.5">{{ student.student_number }}</p>
                </div>
              </div>
              <div class="w-6 h-6 border-2 rounded-lg flex items-center justify-center transition-colors" :class="selectedStudentIds.includes(student.id) ? 'bg-pink-500 border-pink-500' : 'bg-gray-100 border-gray-200'">
                <svg v-if="selectedStudentIds.includes(student.id)" class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                  <path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="p-8 border-t border-gray-50 bg-white">
          <button 
            @click="confirmActivation"
            :disabled="selectedStudentIds.length === 0 || activating"
            class="w-full bg-slate-900 hover:bg-black disabled:bg-gray-200 disabled:text-gray-400 text-white py-4 rounded-2xl font-black uppercase text-xs tracking-widest transition-all shadow-xl active:scale-95 flex items-center justify-center gap-3"
          >
            <span v-if="activating" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
             {{ activating ? 'Processing Activation...' : (activity?.is_code_active ? 'Release to Students' : 'Activate Activity') }}
          </button>
          <p v-if="selectedStudentIds.length === 0" class="text-center mt-4 text-[9px] font-bold text-red-400 uppercase tracking-widest italic animate-pulse">
            Select at least one student to continue
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import CTHM from '@/assets/image/cthm-logos.png'
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { activityDetailsService } from '@/services/instructor/activityDetailsService'
import { useNotificationStore } from '@/stores/notification'
import { useUserStore } from '@/stores/user'
import InstructorSubmission from '@/components/instructor/Instructor_submission.vue'
import { calculatePercentage, calculateTotalGrade } from '@/utils/gradingLogic'

const userStore = useUserStore()
const notificationStore = useNotificationStore()
const router = useRouter()
const route = useRoute()

// --- UI State ---
const showSuccessModal = ref(false)
const showActivationModal = ref(false)
const isPrinting = ref(false)
const loading = ref(true)
const activating = ref(false)
const errorMessage = ref('')
const activeTab = ref('instructions') // 'instructions' or 'submissions'
const submissionsLoading = ref(false)
const releasingGrades = ref(false)
const rankFilter = ref('all')
const searchQuery = ref('')
const filterStatus = ref('all')

// Selective Activation State
const eligibleStudents = ref([])
const selectedStudentIds = ref([])
const timeLimit = ref(60) // Default 60 minutes
const isAllSelected = computed(() => {
  return eligibleStudents.value.length > 0 && selectedStudentIds.value.length === eligibleStudents.value.length
})

// --- Data State ---
const sections = ref([])
const user = ref({ first_name: '', last_name: '', username: '' })
const activity = ref(null)
const submissions = ref([])

// --- Helper Functions ---
// --- Computed ---

const hasValue = (value) => {
  return value !== null && value !== undefined && value !== '' && value !== '-'
}

const formatRequirement = (val) => {
  if (!val) return ''
  return val.replace(/_/g, ' ').toUpperCase()
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
  } catch {
    return dateString
  }
}

const getPassengerAddons = (passenger) => {
  if (!activity.value?.activity_addons) return [];
  return activity.value.activity_addons.filter(aa => 
    aa.passenger?.first_name === passenger.first_name &&
    aa.passenger?.last_name === passenger.last_name
  );
}

// getPercentage must match Instructor_submission.vue and instructor_students_score.vue
// Formula: grade / totalPoints * 100, with rubric_breakdown ratio fallback
const getPercentage = (sub) => {
  const total = parseFloat(activity.value?.total_points || 100)
  if (total === 0) return 0

  // Priority 1: saved grade from backend grading service
  if (sub.grade !== null && sub.grade !== undefined) {
    return calculatePercentage(parseFloat(sub.grade), total)
  }

  // Priority 2: compute from rubric_breakdown ratios (matches instructor_students_score formula)
  //   calculatedScore = sumOfRatios * (totalPoints / 5)
  let rb = sub.rubric_breakdown || []
  if (typeof rb === 'string') { try { rb = JSON.parse(rb) } catch(e) { rb = [] } }
  if (Array.isArray(rb) && rb.length > 0) {
    const sumRatios = rb.reduce((sum, r) => sum + (r.ratio ?? 0), 0)
    const rawScore = sumRatios * (total / 5)
    return calculatePercentage(rawScore, total)
  }

  // Priority 3: legacy analysis fallback
  if (sub.analysis) {
    const rawScore = calculateTotalGrade(sub.analysis, total)
    return calculatePercentage(rawScore, total)
  }

  return 0
}

// --- Data Loaders ---
const fetchData = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const activityId = route.params.activityId
    if (!activityId) {
      errorMessage.value = "No activity ID found in URL"
      loading.value = false
      return
    }

    const data = await activityDetailsService.getActivity(activityId)
    activity.value = data
    
    // Once activity is loaded, fetch submissions and eligible students
    await Promise.all([
      fetchSubmissions(),
      fetchEligibleStudents()
    ])
  } catch (error) {
    console.error("Fetch error:", error)
    errorMessage.value = error.response?.data?.error || "Failed to load activity data."
  } finally {
    loading.value = false
  }
}

const fetchSubmissions = async () => {
  if (!activity.value) return
  submissionsLoading.value = true
  try {
    const res = await activityDetailsService.getSubmissions(activity.value.id)
    submissions.value = res.submissions || []
  } catch (error) {
    console.error("Submissions error:", error)
  } finally {
    submissionsLoading.value = false
  }
}

const fetchEligibleStudents = async () => {
  if (!activity.value) return
  try {
    const res = await activityDetailsService.getEligibleStudents(activity.value.id)
    eligibleStudents.value = res.eligible_students || []
  } catch (error) {
    console.error("Eligible students error:", error)
  }
}

// --- Activation Logic ---
const openActivationModal = async () => {
  await fetchEligibleStudents()
  selectedStudentIds.value = eligibleStudents.value.map(s => s.id) // Default checked all
  // Set default time limit from activity if available
  if (activity.value?.time_limit_minutes) {
    timeLimit.value = activity.value.time_limit_minutes
  }
  showActivationModal.value = true
}

const toggleStudentSelection = (studentId) => {
  const index = selectedStudentIds.value.indexOf(studentId)
  if (index === -1) {
    selectedStudentIds.value.push(studentId)
  } else {
    selectedStudentIds.value.splice(index, 1)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedStudentIds.value = []
  } else {
    selectedStudentIds.value = eligibleStudents.value.map(s => s.id)
  }
}

const confirmActivation = async () => {
  if (!activity.value || activating.value || selectedStudentIds.value.length === 0) return
  
  activating.value = true
  try {
    const res = await activityDetailsService.activateActivity(
      activity.value.id, 
      selectedStudentIds.value, 
      timeLimit.value
    )
    
    activity.value.activity_code = res.activity_code
    activity.value.is_code_active = true
    
    showActivationModal.value = false
    showSuccessModal.value = true
    
    await fetchEligibleStudents()
    if (activeTab.value === 'submissions') {
      await fetchSubmissions()
    }
    
    notificationStore.success(res.message)
  } catch (error) {
    console.error("Activation error:", error)
    notificationStore.error(error.response?.data?.error || 'Failed to activate activity.')
  } finally {
    activating.value = false
  }
}

const goToAnalysis = (sub) => {
  if (sub.status === 'submitted' || sub.status === 'graded') {
    router.push(`/instructor/activity/${activity.value.id}/student/${sub.student_id}/score`)
  }
}

const handlePrint = async () => {
  if (!submissions.value || submissions.value.length === 0) {
    notificationStore.error('No submissions to print.');
    return;
  }

  const incompleteStudents = submissions.value.filter(sub => 
    sub.status === 'assigned' || sub.status === 'not_assigned' || sub.status === 'in_progress'
  );

  if (incompleteStudents.length > 0) {
    const confirmMessage = `There are still ${incompleteStudents.length} student/s who haven't taken or finished their activities yet. \n\nDo you want to print the grade report anyway?`;
    if (!window.confirm(confirmMessage)) {
      return;
    }
  }

  isPrinting.value = true
  document.body.classList.add('print-mode')

  const devToolSelectors = [
    'vite-dev-toolbar',
    '#__vue-devtools-container__',
    '__vue-devtools-host__',
    '[data-v-inspector]',
  ]
  const hiddenDevEls = []
  devToolSelectors.forEach(sel => {
    document.querySelectorAll(sel).forEach(el => {
      el.style.setProperty('display', 'none', 'important')
      hiddenDevEls.push(el)
    })
  })
  document.body.childNodes.forEach(node => {
    if (node.nodeType === 1) {
      const tag = node.tagName?.toLowerCase() || ''
      if (tag.includes('vite') || tag.includes('devtools') || tag.includes('vue-devtools')) {
        node.style.setProperty('display', 'none', 'important')
        hiddenDevEls.push(node)
      }
    }
  })

  setTimeout(() => {
    if (activity.value) {
      instructorDashboardService.logPrintReport({
        activity_id: activity.value.id,
        report_type: 'Grade Report'
      })
    }

    window.print()

    // Reset state right after print dialog returns
    setTimeout(() => {
      isPrinting.value = false
      document.body.classList.remove('print-mode')
      hiddenDevEls.forEach(el => el.style.removeProperty('display'))
    }, 300)
  }, 300)
}

const handleReleaseGrades = async (revealedStudentIds = []) => {
  if (!activity.value || releasingGrades.value) return

  // Count students who are graded, currently unreleased, AND have been explicitly revealed by the instructor
  const toRelease = submissions.value.filter(s =>
    (s.grade !== null || s.status === 'submitted' || s.status === 'graded') && 
    !s.is_released &&
    revealedStudentIds.includes(s.student_id)
  )

  if (toRelease.length === 0) {
    alert('you need to show grade first before releasing the grade to the student')
    return
  }

  if (!confirm(`Release grades for ${toRelease.length} specifically revealed student(s)? They will be able to see their scores on their dashboard.`)) {
    return
  }

  releasingGrades.value = true
  try {
    const res = await activityDetailsService.releaseGrades(activity.value.id, revealedStudentIds)
    activity.value.grades_released = res.grades_released
    notificationStore.success(res.message || `Grades safely released to ${toRelease.length} student(s)!`)
    // Refresh to update is_released flags in the submissions table
    await fetchSubmissions()
  } catch (error) {
    console.error("Release error:", error)
    notificationStore.error(error.response?.data?.error || 'Failed to release grades.')
  } finally {
    releasingGrades.value = false
  }
}

// --- Watchers ---
watch(activeTab, (newTab) => {
  if (newTab === 'submissions') {
    fetchSubmissions()
  }
})

onMounted(() => {
  if (route.query.tab) {
    activeTab.value = route.query.tab
  }
  fetchData()
})

const formatGender = (g) => {
  if (!g) return '-';
  const val = g.toLowerCase().trim();
  if (val === 'mr' || val === 'male') return 'Mr.';
  if (val === 'mrs' || val === 'female') return 'Mrs.';
  if (val === 'ms') return 'Ms.';
  return g.charAt(0).toUpperCase() + g.slice(1);
};
</script>

<style>
</style>
