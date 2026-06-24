<template>
  <div class=" bg-gray-200  py-6 px-4">
    <div class="max-w-5xl mx-auto ">
      <!-- Back Button -->
      <div class="mb-4">
        <button 
          @click="goToHome" 
          class="flex items-center gap-2 text-gray-700 hover:text-gray-900 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          <span class="text-sm font-medium">Back</span>
        </button>
      </div>

      <!-- Loading State (Skeleton UI) -->
      <div v-if="loading" class="animate-pulse">
        <div class="bg-white rounded-lg shadow-sm border border-gray-300 overflow-hidden">
          <!-- Header Skeleton -->
          <div class="px-8 pt-8 pb-6 border-b border-gray-200">
            <div class="flex items-start justify-between mb-6">
              <div class="flex-1">
                <div class="h-9 bg-gray-200 rounded-lg w-3/4 mb-4"></div>
                <div class="h-4 bg-gray-100 rounded w-1/3"></div>
              </div>
              <div class="w-32 space-y-2">
                <div class="h-3 bg-gray-100 rounded ml-auto w-full"></div>
                <div class="h-3 bg-gray-100 rounded ml-auto w-3/4"></div>
              </div>
            </div>
            <div class="flex gap-2">
              <div v-for="i in 4" :key="i" class="h-6 bg-gray-50 rounded-full w-20 border border-gray-100"></div>
            </div>
          </div>
          
          <!-- Instructions Skeleton -->
          <div class="px-8 py-6 border-b border-gray-200">
            <div class="h-5 bg-gray-200 rounded w-32 mb-4"></div>
            <div class="space-y-2">
              <div class="h-4 bg-gray-100 rounded w-full"></div>
              <div class="h-4 bg-gray-100 rounded w-5/6"></div>
              <div class="h-4 bg-gray-100 rounded w-4/5"></div>
            </div>
          </div>

          <!-- Quick Info Bar Skeleton -->
          <div class="px-8 py-4 bg-gray-50/50 border-b border-gray-200 flex justify-around">
            <div v-for="i in 4" :key="i" class="text-center space-y-2">
              <div class="h-3 bg-gray-200 rounded w-12 mx-auto"></div>
              <div class="h-4 bg-gray-300 rounded w-20 mx-auto"></div>
            </div>
          </div>

          <!-- Passenger Info Skeleton -->
          <div class="px-8 py-6">
            <div class="h-5 bg-gray-200 rounded w-40 mb-6"></div>
            <div v-for="i in 2" :key="i" class="border border-gray-200 rounded-lg p-6 mb-6">
              <div class="flex justify-between mb-6">
                <div class="h-4 bg-gray-200 rounded w-48"></div>
                <div class="h-4 bg-gray-100 rounded w-32"></div>
              </div>
              <div class="grid grid-cols-12 gap-3 mb-4">
                <div class="col-span-2 h-10 bg-gray-50 rounded border border-gray-100"></div>
                <div class="col-span-4 h-10 bg-gray-50 rounded border border-gray-100"></div>
                <div class="col-span-5 h-10 bg-gray-50 rounded border border-gray-100"></div>
                <div class="col-span-1 h-10 bg-gray-50 rounded border border-gray-100"></div>
              </div>
              <div class="grid grid-cols-3 gap-3">
                <div v-for="j in 3" :key="j" class="h-10 bg-gray-50 rounded border border-gray-100"></div>
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
            <h3 class="text-sm font-semibold text-red-800 mb-1">Error Loading Activity</h3>
            <p class="text-sm text-red-600 mb-3">{{ error }}</p>
            <div class="flex gap-2">
              <button 
                @click="loadActivityDetails" 
                class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 transition-colors"
              >
                Try Again
              </button>
              <button 
                @click="goToHome" 
                class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg text-sm hover:bg-gray-300 transition-colors"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Card -->
      <div v-else class="bg-white rounded-lg shadow-sm border border-gray-300">
        <!-- Header -->
        <div class="px-8 pt-8 pb-6 border-b border-gray-200">
          <div class="flex items-start justify-between mb-3">
            <div>
              <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ activity.title }}</h1>
              <div class="flex items-center gap-2 text-sm text-gray-600">
                <span>{{ activity.section_code }}</span>
                <span>•</span>
                <span>Block {{ activity.section_name }}</span>
              </div>
            </div>
            <div class="text-right">
              <p class="text-xs text-gray-500 mb-1">Due: {{ formatDueDate(activity.due_date) }}</p>
              <p v-if="instructor" class="text-xs text-gray-500">Instructor: {{ instructor.first_name }} {{ instructor.last_name }}</p>
            </div>
          </div>
          
          <!-- Tags -->
          <div class="flex flex-wrap gap-2 mt-4">
            <span class="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
              {{ activity.activity_type || 'Flight Booking' }}
            </span>
            <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
              {{ activity.section_code }}
            </span>
            <span :class="[
              'px-3 py-1 text-xs font-medium rounded-full',
              activity.required_travel_class?.toLowerCase() === 'business' ? 'bg-green-800 text-white' : 'bg-yellow-100 text-yellow-700'
            ]">
              {{ activity.required_travel_class || 'Economy' }}
            </span>
            <span :class="[
              'px-3 py-1 text-xs font-medium rounded-full',
              activity.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
            ]">
              {{ activity.is_active ? 'Active' : 'Inactive' }}
            </span>
            <span 
              :class="[
                'px-3 py-1 text-xs font-bold rounded-full',
                activity.is_failed_due_to_time ? 'bg-red-100 text-red-700 border border-red-200 uppercase font-black' : 'bg-purple-100 text-purple-700'
              ]"
            >
              {{ activity.is_failed_due_to_time ? 'FAIL' : 'Grade Weight: 100%' }}
            </span>
            <span v-if="isOverdue && activity.status !== 'submitted' && activity.status !== 'graded'" class="px-3 py-1 bg-red-100 text-red-700 text-xs font-black rounded-full uppercase animate-pulse border border-red-200 shadow-sm">
              Overdue
            </span>
          </div>
        </div>

        <!-- Description Section -->
        <div v-if="activity.description" class="px-8 py-6 border-b border-gray-200 bg-gray-50/30">
          <h2 class="text-base font-bold text-gray-900 mb-2">Activity Overview</h2>
          <div class="text-sm text-gray-600 leading-relaxed italic">
            <p class="whitespace-pre-wrap">{{ activity.description }}</p>
          </div>
        </div>

        <!-- Instructions Section -->
        <div class="px-8 py-6 border-b border-gray-200">
          <h2 class="text-base font-bold text-gray-900 mb-3">Detailed Instructions</h2>
          <div class="text-sm text-gray-700 leading-relaxed space-y-3">
            <p class="whitespace-pre-wrap">{{ dynamicInstructions }}</p>
          </div>
        </div>

        <!-- Flight Requirements Section -->
        <div class="px-8 py-6 border-b border-gray-200">
          <h2 class="text-base font-bold text-gray-900 mb-4">Flight Requirements</h2>
          
          <!-- Trip Type Buttons -->
          <div class="flex gap-2 mb-6">
            <span class="bg-[#FFC145] px-6 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider text-black">
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
              <p class="text-sm font-bold text-gray-800">{{ activity.required_departure_date ? formatFullDate(activity.required_departure_date) : 'N/A' }}</p>
            </div>
            <div class="text-center">
              <p class="text-xs text-gray-400 uppercase font-bold tracking-widest">Return</p>
              <p class="text-sm font-bold text-gray-800">{{ activity.required_return_date ? formatFullDate(activity.required_return_date) : 'N/A' }}</p>
            </div>
            <div class="h-10 w-[1px] bg-gray-200 mx-2"></div>
            <div class="text-center">
              <p class="text-xs text-gray-400 uppercase font-bold tracking-widest">Passenger</p>
              <p class="text-xs text-gray-700">
                Adult: <b>{{ activity.required_passengers || 0 }}</b><br>
                Child: <b>{{ activity.required_children || 0 }}</b><br>
                Infant: <b>{{ activity.required_infants || 0 }}</b>
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
                    <p class="text-xs font-bold text-gray-700">{{ segment.departure_date ? formatFullDate(segment.departure_date) : 'N/A' }}</p>
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
            </div>
          </div>
        </div>

        <!-- Add-on & Insurance Requirements -->
        <div v-if="activity.activity_addons && activity.activity_addons.length > 0" class="px-8 py-6 border-b border-gray-200">
          <h2 class="text-base font-bold text-gray-900 mb-4">Add-ons & Insurance Requirements</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div v-for="aa in activity.activity_addons" :key="aa.id" class="border border-pink-100 rounded-xl p-4 bg-pink-50/30 flex items-center justify-between">
              <div>
                <p class="text-xs font-bold text-gray-900 leading-tight">{{ aa.addon_name }}</p>
                <p class="text-[10px] text-gray-400 mt-1 uppercase font-bold tracking-tight">
                  For: {{ aa.passenger?.first_name }} {{ aa.passenger?.last_name || 'Passenger' }}
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

        <!-- Passenger Information Section -->
        <div class="px-8 py-6">
          <h2 class="text-base font-bold text-gray-900 mb-4">Passenger Information</h2>
          
          <!-- No passengers message -->
          <div v-if="displayPassengers.length === 0" class="text-center py-8 text-gray-500">
            <p>No passenger information available for this activity.</p>
          </div>
          
          <!-- Passenger Cards -->
          <div v-for="(passenger, index) in displayPassengers" :key="index" class="mb-6">
            <div class="border border-gray-300 rounded-lg p-6">
              <!-- Passenger Header -->
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-sm font-bold text-gray-900 uppercase tracking-wide">
                  Passenger {{ index + 1 }} ({{ passenger.passenger_type || 'Adult' }})
                </h3>
                <div class="flex items-center gap-4">
                  <span class="text-xs text-gray-600 uppercase tracking-wide">
                    seat preference: <strong>{{ passenger.seat_preference || 'Window' }}</strong>
                  </span>
                  <span v-if="getAssignedSeat(index)" class="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-black uppercase tracking-wider border border-blue-200 shadow-sm flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                    Required Seat: {{ getAssignedSeat(index) }}
                  </span>
                </div>
              </div>

              <!-- Form Fields -->
              <div class="space-y-4">
                <!-- Row 1: Gender, First Name, Last Name, MI -->
                <div class="grid grid-cols-12 gap-3">
                  <div class="col-span-2">
                    <label class="block text-[10px] font-bold text-red-600 uppercase mb-1.5 tracking-wide">Gender*</label>
                    <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                      {{ formatGender(passenger.gender) }}
                    </div>
                  </div>
                  <div class="col-span-4">
                    <label class="block text-[10px] font-bold text-red-600 uppercase mb-1.5 tracking-wide">First Name*</label>
                    <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                      {{ passenger.first_name || 'N/A' }}
                    </div>
                  </div>
                  <div class="col-span-5">
                    <label class="block text-[10px] font-bold text-red-600 uppercase mb-1.5 tracking-wide">Last Name*</label>
                    <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                      {{ passenger.last_name || 'N/A' }}
                    </div>
                  </div>
                  <div class="col-span-1">
                    <label class="block text-[10px] font-bold text-gray-600 uppercase mb-1.5 tracking-wide">MI</label>
                    <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700 text-center">
                      {{ passenger.middle_initial || passenger.middle_name || '-' }}
                    </div>
                  </div>
                </div>

                <!-- Row 2: Date of Birth -->
                <div>
                  <label class="block text-[10px] font-bold text-gray-700 uppercase mb-1.5 tracking-wide">Date of Birth</label>
                  <div class="grid grid-cols-3 gap-3">
                    <div>
                      <label class="block text-[10px] text-gray-500 mb-1">Day*</label>
                      <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                        {{ passenger.birth_day || 'N/A' }}
                      </div>
                    </div>
                    <div>
                      <label class="block text-[10px] text-gray-500 mb-1">Month*</label>
                      <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                        {{ passenger.birth_month || 'N/A' }}
                      </div>
                    </div>
                    <div>
                      <label class="block text-[10px] text-gray-500 mb-1">Year*</label>
                      <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                        {{ passenger.birth_year || 'N/A' }}
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Row 3: Nationality and Passport -->
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label class="block text-[10px] font-bold text-red-600 uppercase mb-1.5 tracking-wide">Nationality*</label>
                    <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                      {{ passenger.nationality || 'N/A' }}
                    </div>
                  </div>
                  <div>
                    <label class="block text-[10px] font-bold text-red-600 uppercase mb-1.5 tracking-wide">Passport*</label>
                    <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                      {{ passenger.passport_number || passenger.passport || 'N/A' }}
                    </div>
                  </div>
                </div>

                <!-- Row 4: Passenger Category -->
                <div class="mt-4">
                  <label class="block text-[10px] font-bold text-red-600 uppercase mb-1.5 tracking-wide">Required Category*</label>
                  <div class="px-3 py-2.5 border border-gray-300 rounded text-sm bg-white text-gray-700">
                    {{ passenger.passenger_category === 'senior' ? 'Senior Citizen' : (passenger.passenger_category === 'pwd' ? 'PWD' : 'Regular') }}
                  </div>
                </div>

                <!-- Row 5: PWD ID Number (shown only for PWD passengers) -->
                <div v-if="passenger.passenger_category === 'pwd' && passenger.pwd_id_number" class="mt-3">
                  <label class="block text-[10px] font-bold text-blue-600 uppercase mb-1.5 tracking-wide">PWD ID Number*</label>
                  <div class="px-3 py-2.5 border border-blue-300 rounded text-sm bg-blue-50 text-blue-800 font-mono">
                    {{ passenger.pwd_id_number }}
                  </div>
                </div>

                <!-- Row 6: Senior Citizen ID (shown only for Senior passengers) -->
                <div v-if="passenger.passenger_category === 'senior' && passenger.senior_id_number" class="mt-3">
                  <label class="block text-[10px] font-bold text-amber-600 uppercase mb-1.5 tracking-wide">Senior Citizen ID*</label>
                  <div class="px-3 py-2.5 border border-amber-300 rounded text-sm bg-amber-50 text-amber-800 font-mono">
                    {{ passenger.senior_id_number }}
                  </div>
                </div>

                <!-- Row 7: Passport Expiry Date (shown only for non-Philippines nationality) -->
                <div v-if="passenger.nationality && passenger.nationality.toLowerCase() !== 'philippines' && passenger.passport_expiry_date" class="mt-3">
                  <label class="block text-[10px] font-bold text-red-600 uppercase mb-1.5 tracking-wide">Passport Expiry Date*</label>
                  <div class="px-3 py-2.5 border border-red-300 rounded text-sm bg-red-50 text-red-800">
                    {{ passenger.passport_expiry_date }}
                  </div>
                </div>

                <!-- Checkboxes -->
                <div class="space-y-2 pt-2">
                  <label class="flex items-center gap-2 text-xs text-gray-700 cursor-pointer">
                    <div :class="[
                      'w-4 h-4 border border-gray-400 rounded flex items-center justify-center flex-shrink-0',
                      passenger.has_reservation ? 'bg-blue-500 border-blue-500' : 'bg-white'
                    ]">
                      <svg v-if="passenger.has_reservation" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                      </svg>
                    </div>
                    <span>I have a reservation / request</span>
                  </label>
                  <label class="flex items-center gap-2 text-xs text-gray-700 cursor-pointer">
                    <div :class="[
                      'w-4 h-4 border border-gray-400 rounded flex items-center justify-center flex-shrink-0',
                      passenger.is_pwd ? 'bg-blue-500 border-blue-500' : 'bg-white'
                    ]">
                      <svg v-if="passenger.is_pwd" class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                      </svg>
                    </div>
                    <span>I am a Person with Disability</span>
                  </label>
                </div>

                <!-- Passenger Add-ons -->
                <div v-if="getPassengerAddons(passenger).length > 0" class="mt-4 border-t border-gray-100 pt-3">
                  <label class="block text-[10px] font-bold text-pink-500 uppercase tracking-wide mb-2">Assigned Add-ons</label>
                  <div class="flex flex-wrap gap-2">
                    <span v-for="addon in getPassengerAddons(passenger)" :key="addon.id" class="px-3 py-1.5 bg-pink-50 border border-pink-200 text-pink-700 rounded-md text-xs font-bold shadow-sm">
                      {{ addon.addon_name }}
                    </span>
                  </div>
                </div>

              </div>
            </div>
          </div>

          <!-- Submission & Grading Section (Always visible for clarity) -->
          <div class="mb-8 border-2 border-dashed border-gray-200 rounded-xl p-6 bg-gray-50/50">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-base font-bold text-gray-900 uppercase tracking-tight">Submission & Grading</h2>
              <span :class="['px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider', getStatusClass(activity.status)]">
                {{ getStatusLabel(activity.status) }}
              </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Grade Card -->
              <div class="bg-white p-5 rounded-lg border border-gray-200 shadow-sm flex items-center gap-4 relative overflow-hidden">
                <div v-if="activity.status === 'graded' && !activity.grades_released" class="absolute top-0 right-0">
                  <div class="bg-yellow-400 text-[8px] font-black px-2 py-0.5 uppercase tracking-tighter transform rotate-45 translate-x-4 translate-y-2 w-24 text-center">Pending Release</div>
                </div>
                <div class="w-12 h-12 bg-pink-50 rounded-full flex items-center justify-center text-pink-500">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                  </svg>
                </div>
                <div>
                  <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Performance Score</p>
                  <div v-if="activity.is_failed_due_to_time" class="flex flex-col">
                    <span class="text-2xl font-black text-red-600">0%</span>
                    <span class="text-[9px] text-red-400 font-bold uppercase tracking-tighter italic">Failed due to timeReached</span>
                  </div>
                  <div v-else-if="activity.status === 'assigned' && isOverdue" class="flex flex-col">
                    <span class="text-sm font-bold text-red-600 uppercase tracking-tighter">Missed Deadline</span>
                    <span class="text-[9px] text-gray-400 italic font-medium">Activity is no longer accessible</span>
                  </div>
                  <div v-else-if="!activity.grades_released" class="flex flex-col">
                    <span class="text-sm font-bold text-yellow-600">Pending Release</span>
                    <span class="text-[9px] text-gray-400 italic border-l-2 border-yellow-200 pl-1.5">Scores aren't published yet</span>
                  </div>
                  <p v-else class="text-2xl font-black text-gray-900 flex items-center gap-2">
                    <span v-if="activity.grade !== null" class="text-2xl font-black text-emerald-600">
                      {{ Math.round((activity.grade / activity.total_points) * 100) }}%
                    </span>
                    <span v-else class="text-gray-400">-</span>
                  </p>
                </div>
              </div>

              <!-- Date Submitted -->
              <div class="bg-white p-5 rounded-lg border border-gray-200 shadow-sm flex items-center gap-4">
                <div class="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center text-blue-500">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Submitted At</p>
                  <p class="text-sm font-bold text-gray-900">
                    {{ activity.submitted_at ? formatDateTime(activity.submitted_at) : 'Not submitted yet' }}
                  </p>
                </div>
              </div>
            </div>



            <!-- Feedback -->
            <div v-if="activity.feedback && activity.grades_released" class="mt-6 bg-white p-5 rounded-lg border border-gray-200 shadow-sm">
              <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mb-2 flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
                Feedback
              </p>
              <p class="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap italic">{{ activity.feedback }}</p>
            </div>
            
            <!-- View Analysis Button -->
            <div v-if="activity.status === 'graded' || activity.status === 'submitted'" class="mt-6 flex flex-col items-center gap-2">
              <template v-if="!activity.grades_released">
                <div class="px-6 py-3 bg-amber-50 border border-amber-200 text-amber-700 text-sm font-bold rounded-lg flex items-center gap-2 shadow-sm">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Results not released yet
                </div>
                <p class="text-[10px] text-gray-400 italic">Analysis will be available once the instructor releases the grades.</p>
              </template>
              
              <template v-else>
                <button 
                  @click="openComparisonModal"
                  class="px-8 py-3 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-bold rounded-lg flex items-center gap-2 shadow-md transition-all transform hover:scale-105"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  VIEW DETAILED ANALYSIS
                </button>
              </template>
            </div>
          </div>

          <!-- Start Button -->
          <div class="flex flex-col items-center gap-3 mt-8">
            <div v-if="timeLeftLive && !activity.completed && activity.status !== 'graded' && activity.status !== 'submitted'" class="mb-4 p-4 bg-pink-50 border border-pink-100 rounded-xl flex items-center justify-between shadow-sm animate-fade-in w-full max-w-md">
              <div class="flex items-center gap-3">
                <div :class="['w-10 h-10 rounded-full flex items-center justify-center', secondsLeftLive < 120 ? 'bg-red-100 text-red-600 animate-pulse' : 'bg-pink-100 text-pink-600']">
                  <i class="ph ph-timer text-xl"></i>
                </div>
                <div>
                  <p class="text-[10px] font-black text-pink-500 uppercase tracking-widest leading-none mb-1">Time Remaining</p>
                  <p class="text-lg font-mono font-black text-slate-800 leading-none">{{ timeLeftLive }}</p>
                </div>
              </div>
              <div v-if="secondsLeftLive < 120" class="text-[9px] font-black text-red-500 uppercase tracking-tighter animate-pulse">
                Hurry up!
              </div>
            </div>

            <button 
              @click="openCodeModal"
              :disabled="!activity.is_active || activity.grade !== null || activity.status === 'submitted' || activity.status === 'graded' || isOverdue || (activity.expires_at && secondsLeftLive <= 0) || activity.is_failed_due_to_time || activity.status === 'unassigned'"
              :class="[
                'w-full max-w-md py-4 rounded-lg font-bold text-sm uppercase tracking-wider transition-all shadow-md',
                activity.status === 'unassigned'
                  ? 'bg-rose-50 text-rose-600 border border-rose-200 cursor-not-allowed'
                  : (activity.is_active && activity.grade === null && !isOverdue && !(activity.expires_at && secondsLeftLive <= 0) && !activity.is_failed_due_to_time
                      ? 'bg-[#f5c842] hover:bg-[#e5b832] text-gray-900' 
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed')
              ]"
            >
              {{ getButtonText() }}
            </button>
            <p v-if="activity.grade !== null" class="text-[10px] text-gray-400 italic font-medium">
              Activity has been graded. You cannot re-submit.
            </p>
            <p v-else-if="isOverdue && activity.status !== 'submitted' && activity.status !== 'graded'" class="text-[10px] text-red-500 italic font-black uppercase tracking-wider">
              The deadline for this activity has passed.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Code Verification Modal -->
      <div
        v-if="showCodeModal"
        class="fixed inset-0 z-50 flex items-center justify-center px-4 bg-black/80"
        @click.self="closeCodeModal"
      >

      <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-8 transform transition-all">
        <!-- Modal Header -->
        <div class="text-center mb-6">
          <div class="mx-auto w-16 h-16 bg-[#f5c842] rounded-full flex items-center justify-center mb-4">
            <svg class="w-8 h-8 text-gray-900" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-gray-900 mb-2">Enter Activity Code</h3>
          <p class="text-sm text-gray-600">Please enter the code provided by your instructor</p>
        </div>

        <!-- Code Input -->
        <div class="mb-6">
          <input 
            v-model="enteredCode"
            type="text"
            placeholder="Enter code"
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg text-center text-lg font-mono uppercase tracking-widest focus:outline-none focus:border-[#f5c842] transition-colors"
            :class="{ 'border-red-500 animate-shake': showError }"
            @keyup.enter="verifyCode"
            @input="showError = false"
            maxlength="20"
            autocomplete="off"
          />
          
          <!-- Error Message -->
          <div v-if="showError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
            <svg class="w-5 h-5 text-red-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <p class="text-sm text-red-600 font-medium">{{ errorMessage }}</p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-3">
          <button 
            @click="closeCodeModal"
            class="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
            :disabled="verifying"
          >
            Cancel
          </button>
          <button 
            @click="verifyCode"
            :disabled="!enteredCode.trim() || verifying"
            class="flex-1 px-4 py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            :class="[
              enteredCode.trim() && !verifying
                ? 'bg-[#f5c842] hover:bg-[#e5b832] text-gray-900'
                : 'bg-gray-300 text-gray-500'
            ]"
          >
            <span v-if="verifying" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Verifying...
            </span>
            <span v-else>START</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Comparison Modal -->
    <ComparisonModal
      :is-open="showComparison"
      :is-loading="isLoadingBooking"
      :error-message="comparisonError"
      :activity="activity"
      :booking="comparisonBooking"
      :grade="activity.grade"
      @close="showComparison = false"
    />
  </div>
</template>

<script>
import { studentActivityDetailsService } from '@/services/Student/studentActivityDetailsService.js';
import { useBookingStore } from '@/stores/booking';
import ComparisonModal from '@/components/common/ComparisonModal.vue';
import { comparisonService } from '@/services/Student/comparisonService';
import { useUserStore } from '@/stores/user'
import api from '@/services/api/axios';
import { useModalStore } from '@/stores/modal';

export default {
  name: 'StudentActivityDetails',
  setup() {
    const userStore = useUserStore()
    const modalStore = useModalStore()
    return { userStore, modalStore }
  },
  components: {
    ComparisonModal
  },
  data() {
    return {
      activity: {
        id: null,
        title: '',
        description: '',
        activity_type: '',
        due_date: null,
        total_points: 0,
        section_code: '',
        section_name: '',
        required_trip_type: '',
        required_origin: '',
        required_destination: '',
        required_travel_class: '',
        required_passengers: 0,
        required_children: 0,
        required_infants: 0,
        departure_date: null,
        arrival_date: null,
        status: '',
        is_active: false,
        activity_code: '', // Store the activity code
        segments: [],
        analysis: null,
        grades_released: false,
        required_seat_class: '', // ✅ ADDED
        activity_addons: [] // ✅ ADDED
      },
      instructor: null,
      passengers: [],
      studentEmail: '',
      studentFirstName: '',
      studentLastName: '',
      loading: true,
      error: null,
      
      // Code Modal State
      showCodeModal: false,
      enteredCode: '',
      showError: false,
      errorMessage: '',
      verifying: false,

      // Comparison Modal State
      showComparison: false,
      isLoadingBooking: false,
      comparisonBooking: null,
      comparisonError: null,
      
      // Live Timer State
      timeLeftLive: '',
      secondsLeftLive: 0,
      timerInterval: null
    }
},
  computed: {
    fullName() {
      return `${this.studentFirstName} ${this.studentLastName}`.trim() || 'Student';
    },
    initials() {
      const first = this.studentFirstName?.charAt(0) || '';
      const last = this.studentLastName?.charAt(0) || '';
      return (first + last).toUpperCase() || 'ST';
    },
    normalizedTripType() {
      return (this.activity.required_trip_type || '').toLowerCase();
    },
    normalizedTravelClass() {
      return (this.activity.required_travel_class || '').toLowerCase();
    },
    displayPassengers() {
      if (this.passengers && this.passengers.length > 0) {
        console.log('✅ Using passengers from backend:', this.passengers.length);
        return this.passengers;
      }
      
      console.log('ℹ️ No passenger data from backend');
      return [];
    },
    dynamicInstructions() {
      if (!this.activity.instructions && !this.activity.description) return 'No instructions provided.';
      let text = this.activity.instructions || (this.activity.description ? 'Please refer to the activity overview above.' : '');
      
      if (!text && this.activity.description) {
        text = 'Follow the requirements outlined in the overview.';
      }
      
      // If we have assigned seats, try to inject them into the passenger list instructions
      if (this.activity.assigned_seats && this.activity.assigned_seats.length > 0) {
        const lines = text.split('\n');
        const newLines = [];
        let passengerCount = 0;
        
        for (let i = 0; i < lines.length; i++) {
          newLines.push(lines[i]);
          
          // Look for "Passenger X (Type):" pattern
          if (lines[i].trim().match(/^Passenger\s+\d+\s+\(.*\):$/i)) {
            const seat = this.getAssignedSeat(passengerCount);
            if (seat) {
              newLines.push(`  • Assigned Seat: ${seat}`);
            }
            passengerCount++;
          }
        }
        text = newLines.join('\n');
      }
      
      return text;
    },
    isOverdue() {
      if (!this.activity.due_date) return false;
      const now = new Date();
      const dueDate = new Date(this.activity.due_date);
      // If it's just a date, set time to end of day
      if (this.activity.due_date.length <= 10) {
        dueDate.setHours(23, 59, 59, 999);
      }
      return now > dueDate;
    }
  },
  async created() {
    console.log('🔐 Activity Details Component Created');
    
    if (!this.userStore.isAuthenticated) {
      console.error('❌ No token found!');
      this.error = "Authentication required. Please login.";
      this.loading = false;
      
      setTimeout(() => {
        this.$router.push('/login');
      }, 2000);
      return;
    }
    
    // Ensure user profile is loaded (handles cache clears)
    await this.userStore.ensureUserLoaded();

    if (this.userStore.studentProfile) {
      this.studentEmail = this.userStore.studentProfile.email || '';
      this.studentFirstName = this.userStore.studentProfile.first_name || '';
      this.studentLastName = this.userStore.studentProfile.last_name || '';
      console.log('✅ Student data loaded from store');
    }
    
    await this.loadActivityDetails();
  },
  methods: {
    async loadActivityDetails() {
      try {
        this.loading = true;
        this.error = null;
        
        const activityId = this.$route.params.id;
        console.log('\n' + '='.repeat(60));
        console.log('📡 LOADING ACTIVITY DETAILS');
        console.log('='.repeat(60));
        console.log('Activity ID:', activityId);
        
        if (!activityId) {
          throw new Error('No activity ID provided in route');
        }
        
        console.log('🌐 Making API request...');
        const response = await studentActivityDetailsService.getActivityDetails(activityId);
        
        console.log('✅ Response received:', response.data);
        
        if (!response.data || !response.data.activity) {
          throw new Error('Invalid response format from server');
        }
        
        const activityData = response.data.activity;
        
        // Populate activity data
        this.activity = {
          id: activityData.id,
          title: activityData.title || 'Untitled Activity',
          description: activityData.description || '',
          activity_type: activityData.activity_type || 'Flight Booking',
          instructions: activityData.instructions || '',
          due_date: activityData.due_date,
          total_points: activityData.total_points || 0,
          section_code: activityData.section_code || '',
          section_name: activityData.section_name || '',
          section_id: activityData.section_id,
          
          // Flight requirements
          required_trip_type: activityData.required_trip_type || '',
          required_origin: activityData.required_origin || '',
          required_destination: activityData.required_destination || '',
          required_travel_class: activityData.required_travel_class || '',
          required_passengers: activityData.required_passengers || 0,
          required_children: activityData.required_children || 0,
          required_infants: activityData.required_infants || 0,
          activity_addons: activityData.activity_addons || [], // ✅ ADDED
          
          // Dates
          required_departure_date: activityData.required_departure_date || activityData.departure_date,
          required_return_date: activityData.required_return_date || activityData.arrival_date,
          required_seat_class: activityData.required_seat_class || '',
          
          // Status
          status: activityData.status || 'assigned',
          is_active: activityData.is_active || false,
          is_failed_due_to_time: activityData.is_failed_due_to_time || false,
          
          // Activity Code
          activity_code: activityData.activity_code || '',
          
          // Metadata
          assigned_at: activityData.assigned_at,
          submitted_at: activityData.submitted_at,
          grade: activityData.grade,
          feedback: activityData.feedback || '',
          completed: activityData.completed || false,
          created_at: activityData.created_at,
          segments: activityData.segments || [],
          grades_released: activityData.grades_released || false,
          assigned_seats: activityData.assigned_seats || [],
          expires_at: activityData.expires_at // ✅ Added for live timer
        };
        
        if (this.activity.expires_at && !this.activity.completed && this.activity.status !== 'graded' && !this.activity.is_failed_due_to_time) {
          this.startLiveTimer();
        }
        
        console.log('✅ Activity populated with code:', this.activity.activity_code);
        
        // Load instructor
        if (response.data.instructor) {
          this.instructor = response.data.instructor;
          console.log('✅ Instructor loaded:', this.instructor.first_name, this.instructor.last_name);
        }
        
        // Load passengers
        if (response.data.passengers && Array.isArray(response.data.passengers)) {
          this.passengers = response.data.passengers;
          console.log('✅ Passengers loaded:', this.passengers.length);
        } else {
          console.log('ℹ️ No passengers in response');
        }
        
        console.log('='.repeat(60) + '\n');
        
      } catch (error) {
        console.error('\n' + '='.repeat(60));
        console.error('❌ ERROR LOADING ACTIVITY');
        console.error('='.repeat(60));
        console.error('Error:', error);
        
        if (error.response) {
          console.error('Response status:', error.response.status);
          console.error('Response data:', error.response.data);
          
          switch (error.response.status) {
            case 404:
              this.error = "Activity not found or you don't have access.";
              break;
            case 403:
              this.error = error.response.data?.error || "Access denied.";
              break;
            case 401:
              this.error = "Session expired. Redirecting to login...";
              localStorage.clear();
              setTimeout(() => this.$router.push('/login'), 2000);
              break;
            default:
              this.error = error.response.data?.error || `Error ${error.response.status}`;
          }
        } else if (error.request) {
          this.error = "Cannot connect to server. Please check your connection.";
        } else {
          this.error = error.message || "An unexpected error occurred.";
        }
        
        console.error('='.repeat(60) + '\n');
        
      } finally {
        this.loading = false;
      }
    },
    
    goToHome() {
      this.$router.push('/student/dashboard');
    },

    async openComparisonModal() {
      this.showComparison = true;
      this.isLoadingBooking = true;
      this.comparisonError = null;
      this.comparisonBooking = null;

      try {
        const activityId = this.activity.id;
        const res = await comparisonService.getComparisonData(activityId);
        if (res.success) {
          this.comparisonBooking = res.booking;
        } else {
          this.comparisonError = res.error || "Failed to load comparison data.";
        }
      } catch (err) {
        console.error('Failed to open comparison modal:', err);
        this.comparisonError = "Failed to load comparison data.";
      } finally {
        this.isLoadingBooking = false;
      }
    },
    
    openCodeModal() {
      if (!this.activity.is_active) return;
      console.log('🔓 Opening code modal');
      this.showCodeModal = true;
      this.enteredCode = '';
      this.showError = false;
      this.errorMessage = '';
      
      // Focus input after modal opens
      this.$nextTick(() => {
        const input = this.$el.querySelector('input[type="text"]');
        if (input) input.focus();
      });
    },
    
    closeCodeModal() {
      console.log('❌ Closing code modal');
      this.showCodeModal = false;
      this.enteredCode = '';
      this.showError = false;
      this.errorMessage = '';
      this.verifying = false;
    },
    
    async verifyCode() {
      if (!this.enteredCode.trim() || this.verifying) return;
      
      this.verifying = true;
      this.showError = false;
      this.errorMessage = '';
      
      console.log('🔍 Verifying code:', this.enteredCode);
      console.log('📋 Expected code:', this.activity.activity_code);
      
      // Simulate slight delay for better UX
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Compare codes (case-insensitive)
      const enteredCodeClean = this.enteredCode.trim().toUpperCase();
      const activityCodeClean = (this.activity.activity_code || '').trim().toUpperCase();
      
      if (enteredCodeClean === activityCodeClean) {
        console.log('✅ Code verified successfully! Starting activity timer...');
        
        try {
          // 1. Call the backend to start the timer
          const startRes = await studentActivityDetailsService.startActivity(this.activity.id);
          console.log('⏲️ Timer started:', startRes.data);
          
          // 2. Update the booking store with activity info and expiry
          const bookingStore = useBookingStore();
          bookingStore.setActivityCode(this.enteredCode, {
            id: this.activity.id,
            title: this.activity.title,
            expires_at: startRes.data.expires_at,
            time_limit_minutes: startRes.data.time_limit_minutes
          });
          
          // Store code verification in localStorage (optional)
          const verificationKey = `activity_${this.activity.id}_verified`;
          localStorage.setItem(verificationKey, 'true');
          localStorage.setItem(`${verificationKey}_timestamp`, Date.now().toString());
          
          // Close modal
          this.closeCodeModal();
          
          // Navigate to home route
          this.$router.push('/');
        } catch (error) {
          console.error('❌ Failed to start activity timer:', error);
          this.showError = true;
          this.errorMessage = error.response?.data?.error || 'Failed to initialize activity. Please try again.';
          this.verifying = false;
        }
      } else {
        console.log('❌ Invalid code entered');
        this.showError = true;
        this.errorMessage = 'Invalid code. Please check and try again.';
        this.verifying = false;
        
        // Shake animation
        setTimeout(() => {
          this.showError = false;
        }, 3000);
      }
    },
    
    formatDueDate(dateString) {
      if (!dateString) return 'No due date';
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'Invalid date';
        return date.toLocaleDateString('en-US', { 
          month: 'long', 
          day: 'numeric', 
          year: 'numeric' 
        });
      } catch (e) {
        return 'Invalid date';
      }
    },
    
    formatFullDate(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'N/A';
        return date.toLocaleDateString('en-US', { 
          month: 'long',
          day: 'numeric'
        });
      } catch (e) {
        return 'N/A';
      }
    },
    
    formatDateTime(dateString) {
      if (!dateString) return 'N/A';
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'N/A';
        return date.toLocaleDateString('en-US', { 
          month: 'long',
          day: 'numeric',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch (e) {
        return 'N/A';
      }
    },
    
    formatRequirement(val) {
      if (!val) return ''
      return val.replace(/_/g, ' ').toUpperCase()
    },

    getStatusLabel(status) {
      if (this.activity.is_failed_due_to_time) return 'FAILED (TIMEOUT)';
      const labels = {
        'unassigned': 'Missing',
        'assigned': 'Assigned',
        'in_progress': 'In Progress',
        'submitted': 'Submitted',
        'graded': 'Graded'
      };
      return labels[status] || (status ? status.charAt(0).toUpperCase() + status.slice(1) : '');
    },
    
    getStatusClass(status) {
      if (this.activity.is_failed_due_to_time) return 'bg-red-100 text-red-700 border border-red-200';
      const classes = {
        'unassigned': 'bg-rose-50 text-rose-700 border-rose-100',
        'assigned': 'bg-gray-100 text-gray-600',
        'in_progress': 'bg-blue-100 text-blue-600',
        'submitted': 'bg-green-100 text-green-700',
        'graded': 'bg-purple-100 text-purple-700'
      };
      return classes[status] || 'bg-gray-50 text-gray-500';
    },
    
    getButtonText() {
      if (this.activity.is_failed_due_to_time) {
        return 'Time Limit Reach';
      }
      if (this.activity.status === 'unassigned') {
        return 'MISSING';
      }
      if (this.activity.completed || this.activity.grade !== null || this.activity.status === 'submitted' || this.activity.status === 'graded') {
        return 'Activity Completed';
      }
      if (this.isOverdue) return 'Deadline Passed';
      if (!this.activity.is_active) return 'Activity Not Active';
      if (this.activity.expires_at) return 'Continue Activity';
      return 'Start';
    },

    getAssignedSeat(index) {
      if (!this.activity?.assigned_seats || !this.displayPassengers[index]) return null;
      if (this.displayPassengers[index].passenger_type === 'infant') return null;
      
      // Count how many non-infants are before this passenger
      let seatIdx = 0;
      for (let i = 0; i < index; i++) {
        if (this.displayPassengers[i].passenger_type !== 'infant') {
          seatIdx++;
        }
      }
      return this.activity.assigned_seats[seatIdx] || null;
    },

    getPassengerAddons(passenger) {
      if (!this.activity?.activity_addons || !this.activity.activity_addons.length) return [];
      return this.activity.activity_addons.filter(aa => 
        aa.passenger?.first_name === passenger.first_name &&
        aa.passenger?.last_name === passenger.last_name
      );
    },

    formatGender(g) {
      if (!g) return 'N/A';
      const val = g.toLowerCase().trim();
      if (val === 'mr' || val === 'male') return 'Mr.';
      if (val === 'mrs' || val === 'female') return 'Mrs.';
      if (val === 'ms') return 'Ms.';
      return g.charAt(0).toUpperCase() + g.slice(1);
    },
    
    startLiveTimer() {
      if (this.timerInterval) clearInterval(this.timerInterval);
      
      this.timerInterval = setInterval(() => {
        if (!this.activity.expires_at) {
          this.timeLeftLive = '';
          this.secondsLeftLive = 0;
          return;
        }
        
        const expiry = new Date(this.activity.expires_at).getTime();
        const now = Date.now();
        const diff = Math.max(0, Math.round((expiry - now) / 1000));
        
        this.secondsLeftLive = diff;
        
        const mins = Math.floor(diff / 60);
        const secs = diff % 60;
        this.timeLeftLive = `${mins}:${secs.toString().padStart(2, '0')}`;
        
        if (diff <= 0) {
          clearInterval(this.timerInterval);
          if (!this.activity.is_failed_due_to_time) {
            this.modalStore.error({
              title: 'Time Reached!',
              message: 'The time allocated for this activity has expired. This attempt will be marked as failed with a 0 score.',
              confirmText: 'Back to Dashboard'
            }).then(() => {
              this.$router.push('/student/dashboard');
            });
            this.loadActivityDetails();
          }
        }
      }, 1000);
    }
  },
  beforeUnmount() {
    if (this.timerInterval) clearInterval(this.timerInterval);
  }
}
</script>

<style scoped>
/* Shake animation for error state */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

.animate-shake {
  animation: shake 0.5s ease-in-out;
}

/* Modal fade-in animation */
.fixed {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Focus styles for input */
input:focus {
  box-shadow: 0 0 0 3px rgba(245, 200, 66, 0.3);
}
</style>