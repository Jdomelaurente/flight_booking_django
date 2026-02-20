<template>
  <div class="min-h-screen bg-gray-50">
    
    <!-- Edit Search Modal -->
    <div v-if="showEditSearch" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-sm shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <h2 class="text-2xl font-bold text-gray-800">Edit Search</h2>
            <button @click="showEditSearch = false" class="text-gray-500 hover:text-gray-700">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <div class="p-6">
          <div class="space-y-6">
            <!-- Trip Type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Trip Type</label>
              <div class="flex space-x-4">
                <label class="flex items-center">
                  <input type="radio" v-model="editSearchForm.tripType" value="one-way" class="h-4 w-4 text-pink-500 focus:ring-pink-500 border-gray-300">
                  <span class="ml-2 text-gray-700">One Way</span>
                </label>
                <label class="flex items-center">
                  <input type="radio" v-model="editSearchForm.tripType" value="round-trip" class="h-4 w-4 text-pink-500 focus:ring-pink-500 border-gray-300">
                  <span class="ml-2 text-gray-700">Round Trip</span>
                </label>
              </div>
            </div>
            
            <!-- Route -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="relative">
                <label class="block text-sm font-medium text-gray-700 mb-2">From</label>
                <input v-model="fromSearchInput" type="text" 
                  @input="searchEditAirports(fromSearchInput, 'from')"
                  @focus="fromSearchInput = ''; fromResults = []"
                  placeholder="e.g. MNL"
                  class="w-full px-4 py-2 border border-gray-300 rounded-sm focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                
                <ul v-if="fromResults.length" class="absolute left-0 top-full z-[60] max-h-48 w-full overflow-y-auto border border-gray-200 bg-white shadow-xl rounded-b-sm">
                  <li v-for="a in fromResults" :key="a.code" @click="selectEditAirport(a, 'from')" class="cursor-pointer border-b border-gray-50 p-3 hover:bg-pink-50">
                    <div class="flex items-center gap-2">
                      <span class="font-bold text-pink-600">{{ a.code }}</span>
                      <span class="text-xs text-gray-600">- {{ a.city }}</span>
                    </div>
                  </li>
                </ul>
              </div>
              <div class="relative">
                <label class="block text-sm font-medium text-gray-700 mb-2">To</label>
                <input v-model="toSearchInput" type="text" 
                  @input="searchEditAirports(toSearchInput, 'to')"
                  @focus="toSearchInput = ''; toResults = []"
                  placeholder="e.g. CEB"
                  class="w-full px-4 py-2 border border-gray-300 rounded-sm focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                
                <ul v-if="toResults.length" class="absolute left-0 top-full z-[60] max-h-48 w-full overflow-y-auto border border-gray-200 bg-white shadow-xl rounded-b-sm">
                  <li v-for="a in toResults" :key="a.code" @click="selectEditAirport(a, 'to')" class="cursor-pointer border-b border-gray-50 p-3 hover:bg-pink-50">
                    <div class="flex items-center gap-2">
                      <span class="font-bold text-pink-600">{{ a.code }}</span>
                      <span class="text-xs text-gray-600">- {{ a.city }}</span>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
            
            <!-- Dates -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Departure Date</label>
                <input v-model="editSearchForm.departure" type="date" 
                  class="w-full px-4 py-2 border border-gray-300 rounded-sm focus:ring-2 focus:ring-pink-500 focus:border-transparent">
              </div>
              <div v-if="editSearchForm.tripType === 'round-trip'">
                <label class="block text-sm font-medium text-gray-700 mb-2">Return Date</label>
                <input v-model="editSearchForm.returnDate" type="date" 
                  class="w-full px-4 py-2 border border-gray-300 rounded-sm focus:ring-2 focus:ring-pink-500 focus:border-transparent">
              </div>
            </div>
            
            <!-- Passengers -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Passengers</label>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Adults</label>
                  <input v-model.number="editSearchForm.adults" type="number" min="1" 
                    class="w-full px-4 py-2 border border-gray-300 rounded-sm focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Children</label>
                  <input v-model.number="editSearchForm.children" type="number" min="0" 
                    class="w-full px-4 py-2 border border-gray-300 rounded-sm focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Infants</label>
                  <input v-model.number="editSearchForm.infants" type="number" min="0" 
                    class="w-full px-4 py-2 border border-gray-300 rounded-sm focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                </div>
              </div>
            </div>
          </div>
          
          <div class="mt-8 flex justify-end space-x-4">
            <button @click="showEditSearch = false" 
              class="px-6 py-2 border border-gray-300 rounded-sm text-gray-700 hover:bg-gray-50 transition-colors">
              Cancel
            </button>
            <button @click="submitEditedSearch" 
              class="px-6 py-2 bg-pink-500 text-white rounded-sm hover:bg-pink-600 transition-colors font-medium">
              Update Search
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Seat Classes Modal -->
    <SeatClassModal 
      :show="showSeatClassesModal"
      :flight="selectedFlightForSeats"
      :seatClasses="availableSeatClasses"
      @select-class="handleSeatClassSelection"
      @close="cancelSeatClassSelection"
    />
    
    <!-- Confirmation Modal -->
    <div v-if="showConfirmation" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-sm shadow-2xl w-full max-w-lg">
        <div class="p-6 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <h2 class="text-xl font-bold text-gray-800">{{ modalTitle }}</h2>
            <button @click="cancelSelection" class="text-gray-500 hover:text-gray-700">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        <div class="p-6">
          <div v-if="isRoundTrip && selectionPhase === 'return' && bookingStore.selectedOutbound" class="space-y-6">
            <!-- Round Trip Complete Summary -->
            <div class="bg-pink-50 rounded-sm p-4">
              <div class="flex justify-between items-center mb-4">
                <h3 class="font-semibold text-gray-800">Round-Trip Itinerary</h3>
                <div class="text-lg font-bold text-pink-500">
                  ₱{{ (Number(bookingStore.selectedOutbound?.price || 0) + Number(selectedFlight?.price || 0)).toLocaleString() }}
                </div>
              </div>
              
              <div class="space-y-4">
                <!-- Outbound -->
                <div class="border-l-4 border-pink-500 pl-4">
                  <div class="flex justify-between items-start">
                    <div>
                      <div class="font-medium text-gray-800">Outbound • {{ bookingStore.selectedOutbound?.flight_number }}</div>
                      <div v-if="bookingStore.selectedOutbound?.selected_seat_class" class="text-sm text-pink-600 mt-1">
                        Seat Class: {{ bookingStore.selectedOutbound.selected_seat_class }}
                      </div>
                      <div class="text-sm text-gray-600 mt-1">
                        {{ bookingStore.selectedOutbound?.origin }} → {{ bookingStore.selectedOutbound?.destination }}
                      </div>
                      <div class="text-sm text-gray-500 mt-1">
                        {{ formatTime(bookingStore.selectedOutbound?.departure_time) }} • {{ formatDate(bookingStore.selectedOutbound?.departure_time) }}
                      </div>
                    </div>
                    <div class="font-semibold text-pink-500">
                      ₱{{ Number(bookingStore.selectedOutbound?.price || 0).toLocaleString() }}
                      <div v-if="bookingStore.selectedOutbound?.original_price && bookingStore.selectedOutbound.price !== bookingStore.selectedOutbound.original_price" 
                           class="text-xs text-green-600">
                        (Base: ₱{{ Number(bookingStore.selectedOutbound.original_price).toLocaleString() }})
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Return -->
                <div class="border-l-4 border-pink-300 pl-4">
                  <div class="flex justify-between items-start">
                    <div>
                      <div class="font-medium text-gray-800">Return • {{ selectedFlight?.flight_number }}</div>
                      <div v-if="selectedFlight?.selected_seat_class" class="text-sm text-pink-600 mt-1">
                        Seat Class: {{ selectedFlight.selected_seat_class }}
                      </div>
                      <div class="text-sm text-gray-600 mt-1">
                        {{ selectedFlight?.origin }} → {{ selectedFlight?.destination }}
                      </div>
                      <div class="text-sm text-gray-500 mt-1">
                        {{ formatTime(selectedFlight?.departure_time) }} • {{ formatDate(selectedFlight?.departure_time) }}
                      </div>
                    </div>
                    <div class="font-semibold text-pink-500">
                      ₱{{ Number(selectedFlight?.price || 0).toLocaleString() }}
                      <div v-if="selectedFlight?.original_price && selectedFlight.price !== selectedFlight.original_price" 
                           class="text-xs text-green-600">
                        (Base: ₱{{ Number(selectedFlight.original_price).toLocaleString() }})
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="space-y-6">
            <!-- Single Flight Summary -->
            <div class="bg-pink-50 rounded-sm p-4">
              <div class="flex justify-between items-center mb-4">
                <h3 class="font-semibold text-gray-800">
                  {{ isRoundTrip && selectionPhase === 'outbound' ? 'Outbound Flight' : 'Flight Details' }}
                </h3>
                <div class="text-lg font-bold text-pink-500">
                  ₱{{ Number(selectedFlight?.price).toLocaleString() }}
                  <div v-if="selectedFlight?.original_price && selectedFlight.price !== selectedFlight.original_price" 
                       class="text-xs text-green-600">
                    (Base: ₱{{ Number(selectedFlight.original_price).toLocaleString() }})
                  </div>
                </div>
              </div>
              
              <div class="space-y-3">
                <div class="flex items-center space-x-2">
                  <div class="font-medium text-gray-800">{{ selectedFlight?.flight_number }}</div>
                  <div class="text-sm text-gray-500">• {{ selectedFlight?.airline_name }}</div>
                </div>
                
                <div v-if="selectedFlight?.selected_seat_class" class="bg-pink-100 border border-pink-200 rounded-sm p-3">
                  <div class="flex justify-between items-center">
                    <div>
                      <div class="text-sm font-medium text-pink-700">Selected Seat Class</div>
                      <div class="text-lg font-bold text-pink-600">{{ selectedFlight.selected_seat_class }}</div>
                    </div>
                    <div v-if="selectedFlight.original_price && selectedFlight.price !== selectedFlight.original_price" 
                         class="text-lg font-bold text-pink-500">
                      +₱{{ Number(selectedFlight.price - selectedFlight.original_price).toLocaleString() }}
                    </div>
                  </div>
                </div>
                
                <div class="flex items-center justify-between">
                  <div>
                    <div class="text-lg font-semibold text-gray-800">{{ formatTime(selectedFlight?.departure_time) }}</div>
                    <div class="text-sm text-gray-600">{{ selectedFlight?.origin }}</div>
                  </div>
                  <div class="flex flex-col items-center">
                    <div class="text-xs text-gray-500 mb-1">{{ selectedFlight?.flight_duration }}</div>
                    <div class="w-16 h-px bg-gray-300"></div>
                  </div>
                  <div class="text-right">
                    <div class="text-lg font-semibold text-gray-800">{{ formatTime(selectedFlight?.arrival_time) }}</div>
                    <div class="text-sm text-gray-600">{{ selectedFlight?.destination }}</div>
                  </div>
                </div>
                
                <div class="text-sm text-gray-500">
                  {{ formatDate(selectedFlight?.departure_time) }}
                </div>
              </div>
            </div>
            
            <!-- Next Step Info -->
            <div v-if="modalActionDescription" 
              class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-sm">
              <div class="flex items-center text-blue-700">
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
                <div class="text-sm">
                  <p class="font-medium">Next Steps:</p>
                  <p class="mt-1">{{ modalActionDescription }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="p-6 border-t border-gray-200 bg-gray-50 rounded-b-xl">
          <div class="flex space-x-4">
            <button @click="cancelSelection" 
              class="flex-1 px-4 py-3 border border-gray-300 rounded-sm text-gray-700 hover:bg-gray-100 transition-colors font-medium">
              Cancel
            </button>
            <button @click="confirmSelection" 
              class="flex-1 px-4 py-3 bg-pink-500 text-white rounded-sm hover:bg-pink-600 transition-colors font-medium">
              {{ confirmButtonText }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Session Expired Modal -->
    <div v-if="showSessionExpired" class="fixed inset-0 bg-black/70 z-[60] flex items-center justify-center p-4">
      <div class="bg-white rounded-sm shadow-2xl w-full max-w-md">
        <div class="p-6 border-b border-gray-200">
          <div class="flex items-center justify-center mb-4">
            <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
              <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <h2 class="text-xl font-bold text-center text-gray-800 mb-2">Session Expired</h2>
          <p class="text-gray-600 text-center">
            Your search session has expired. Please start a new search.
          </p>
        </div>
        
        <div class="p-6">
          <div class="bg-red-50 border border-red-200 rounded-sm p-4 mb-6">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
              </svg>
              <div class="text-sm text-red-700">
                <p class="font-medium">Why did this happen?</p>
                <p class="mt-1">Flight search sessions expire after 15 minutes of inactivity to ensure you get the latest flight availability and pricing.</p>
              </div>
            </div>
          </div>
          
          <div class="flex justify-center">
            <div class="text-center">
              <div class="text-4xl font-bold text-red-500 mb-2">5</div>
              <div class="text-sm text-gray-500">Redirecting in seconds...</div>
            </div>
          </div>
        </div>
        
        <div class="p-6 border-t border-gray-200 bg-gray-50 rounded-b-xl">
          <button @click="() => { bookingStore.resetBooking(); router.push({ name: 'Home' }); }" 
            class="w-full px-6 py-3 bg-red-500 text-white rounded-sm hover:bg-red-600 transition-colors font-medium">
            Go to Home Now
          </button>
        </div>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="max-w-screen-2xl mx-auto lg:px-8 py-8">
      <!-- Header -->
      <div class="bg-white rounded-sm shadow-sm border border-gray-200 p-6 mb-8">
        <!-- Step Indicator -->
        <div v-if="isRoundTrip" class="mb-6">
          <div class="flex items-center space-x-4">
            <div :class="['flex-1 text-center py-2 rounded-sm', 
                     selectionPhase === 'outbound' ? 'bg-pink-500 text-white' : 'bg-gray-100 text-gray-600']">
              <div class="font-medium">1. Select Outbound</div>
            </div>
            <div class="w-8 h-px bg-gray-300"></div>
            <div :class="['flex-1 text-center py-2 rounded-sm', 
                     selectionPhase === 'return' ? 'bg-pink-500 text-white' : 'bg-gray-100 text-gray-600']">
              <div class="font-medium">2. Select Return</div>
            </div>
          </div>
        </div>
        
        <!-- Trip Type and Edit Button -->
        <div class="flex items-center justify-between ">
          <!-- Left Content -->
          <div class="min-w-0">
            <!-- Top Row -->
            <div class="flex flex-wrap items-center gap-2 mb-1 text-[9px] font-semibold ">
              <span
                class="rounded-full px-2 py-0.5 "
                :class="isRoundTrip
                  ? 'bg-pink-100 text-pink-700'
                  : 'bg-green-100 text-gray-700'"
              >
                {{ isRoundTrip ? 'ROUND TRIP' : 'ONE WAY' }}
              </span>

              <span class="rounded-full bg-green-100 px-2 py-0.5  text-gray-700">
                {{ formatDateShort(phaseRouteInfo.date) }}
              </span>

              <span class="rounded-full bg-green-100 px-2 py-0.5 text-gray-700">
                {{ Number(route.query.adults) + Number(route.query.children) }} Travelers
              </span>

              <span
                v-if="selectionPhase === 'return' && hasOutboundSelected"
                class="rounded-full bg-green-100 px-2 py-0.5  font-medium text-green-700"
              >
                ✓ Outbound Selected
              </span>
            </div>

            <!-- Route Line -->
            <div class="truncate text-xs text-gray-300  ">
              {{ selectionPhase === 'outbound' ? 'Departing:' : 'Returning:' }}
              <span class="font-bold text-2xl text-black">
                {{ phaseRouteInfo.origin }} → {{ phaseRouteInfo.destination }}
              </span>
            </div>
          </div>

          <!-- Edit Button -->
          <button
            @click="initializeEditSearch"
            class="inline-flex shrink-0 items-center gap-1.5 rounded border bg-[#FF579A] border-gray-300 px-5 py-1 text-lg font-medium text-white hover:bg-[#FF579A]/80 cursor-pointer transition"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
            Edit Search
          </button>
        </div>
        
        <!-- Auto-Switch Notification -->
        <div v-if="isRoundTrip && selectionPhase === 'return' && hasOutboundSelected" 
          class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-sm">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
            <div class="text-sm text-blue-700">
              <p class="font-medium">Now Select Your Return Flight</p>
              <p class="mt-1">Your outbound flight is selected. Please choose your return flight below.</p>
            </div>
          </div>
        </div>
        
        <!-- Selected Flights Summary -->
        <div v-if="selectedFlightsSummary.length > 0" class="mt-6 pt-6 border-t border-gray-100">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Your Selection</h3>
          <div class="space-y-4">
            <div v-for="item in selectedFlightsSummary" :key="item.type" 
              class="bg-gray-50 rounded-sm p-4 border border-gray-200">
              <div class="flex justify-between items-start mb-2">
                <div class="flex items-center space-x-3">
                  <div v-if="isRoundTrip" class="font-medium text-gray-900">{{ item.type }}:</div>
                  <div class="px-2 py-1 bg-pink-500 text-white text-xs font-medium rounded">
                    {{ item.flight }}
                  </div>
                </div>
              </div>
              <div class="flex justify-between items-center">
                <div class="space-y-1">
                  <div class="text-sm text-gray-700">{{ item.route }}</div>
                  <div class="text-sm text-gray-500">{{ item.time }} • {{ item.date }}</div>
                  <div v-if="item.selected_seat_class" class="text-sm text-pink-600 font-medium">
                    Seat Class: {{ item.selected_seat_class }}
                    <span v-if="item.seat_class_price && item.base_price" class="text-xs">
                      (+₱{{ Number(item.seat_class_price - item.base_price).toLocaleString() }})
                    </span>
                  </div>
                </div>
                <div class="font-bold text-pink-500">₱{{ item.price }}</div>
              </div>
            </div>
            
            <!-- Total Price for Round Trips -->
            <div v-if="isRoundTrip && selectedFlightsSummary.length > 1" 
              class="flex justify-between items-center pt-4 mt-4 border-t border-gray-200">
              <div class="font-semibold text-gray-900">Total:</div>
              <div class="text-xl font-bold text-pink-500">₱{{ totalPrice.toLocaleString() }}</div>
            </div>
          </div>
          
          <!-- Progress Indicators for Round Trips -->
          <div v-if="isRoundTrip" class="mt-4">
            <div v-if="!hasOutboundSelected" class="p-3 bg-yellow-50 border border-yellow-200 rounded-sm">
              <div class="flex items-center text-yellow-700">
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                <span class="font-medium">Select your outbound flight to continue</span>
              </div>
            </div>
            
            <div v-else-if="!hasReturnSelected && selectionPhase === 'outbound'" class="p-3 bg-blue-50 border border-blue-200 rounded-sm">
              <div class="flex items-center text-blue-700">
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
                <span class="font-medium">Outbound flight selected! Click "Continue to Return Flight" above</span>
              </div>
            </div>
          </div>
          
          <!-- Phase Navigation (Round Trips Only) -->
          <div v-if="isRoundTrip" class="mt-6 flex flex-wrap gap-3">
            <button v-if="selectionPhase === 'return'" @click="goBackToOutbound" 
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-sm text-gray-700 hover:bg-gray-50 transition-colors text-sm">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Outbound Flight
            </button>
            
            <!-- Show "Continue to Return Flight" only when outbound is selected AND we're in outbound phase -->
            <button v-if="selectionPhase === 'outbound' && hasOutboundSelected && !hasReturnSelected" 
              @click="goToReturnPhase" 
              class="inline-flex items-center px-4 py-2 bg-pink-500 text-white rounded-sm hover:bg-pink-600 transition-colors text-sm">
              Continue to Return Flight
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </button>
            
            <!-- Show "Proceed to Passenger Details" when both flights are selected -->
            <button v-if="hasOutboundSelected && hasReturnSelected" 
              @click="proceedToPassengerDetails"
              class="inline-flex items-center px-4 py-2 bg-green-500 text-white rounded-sm hover:bg-green-600 transition-colors text-sm">
              Proceed to Passenger Details
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Mobile Filter Toggle -->
      <div class="lg:hidden mb-6">
        <button @click="showFilters = !showFilters" 
          class="w-full flex items-center justify-between p-4 bg-white rounded-sm shadow-sm border border-gray-200">
          <div class="flex items-center space-x-2">
            <svg class="w-5 h-5 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            <span class="font-medium text-gray-800">Filters & Sort</span>
            <span v-if="filteredFlights.length < flights.length" class="text-sm text-pink-500">
              ({{ filteredFlights.length }} of {{ flights.length }})
            </span>
          </div>
          <svg :class="['w-5 h-5 text-gray-500 transform transition-transform', showFilters ? 'rotate-180' : '']" 
               fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
      
      <div class="flex flex-col lg:flex-row gap-8">
        <!-- Filters Sidebar -->
        <FlightFilterSidebar 
          v-model:filters="filters"
          v-model:dateFilter="dateFilter"
          :showFilters="showFilters"
          :filterOptions="filterOptions"
          :totalCount="flights.length"
          :filteredCount="filteredFlights.length"
          :flightStats="flightStats"
          :uniqueDates="uniqueDates"
          :priceRange="priceRange"
          :availableSeatClassOptions="availableSeatClassOptions"
          :isDateFilterActive="isDateFilterActive"
          :dateFilterDisplay="dateFilterDisplay"
          @reset-filters="resetFilters"
          @reset-date-filter="resetDateFilter"
        />
        
        <!-- Main Content -->
        <main class="flex-1">
          <!-- 7-Day Date Selector -->
          <DateNavigator 
            :weekDays="dateSelector.weekDays"
            :weekRange="formatWeekRange"
            :currentWeekContainsSelectedDate="currentWeekContainsSelectedDate"
            :flights="flights"
            @prev-week="prevWeek"
            @next-week="nextWeek"
            @go-to-current="goToCurrentWeek"
            @select-day="selectDay"
          />
          
          <div class="relative min-h-[400px]">
            <!-- Transient Loading Overlay -->
            <div v-if="isFiltering" class="absolute inset-0 bg-white/60 z-20 flex flex-col items-center justify-center backdrop-blur-[2px] transition-all duration-300">
              <div class="w-12 h-12 border-4 border-pink-200 border-t-pink-500 rounded-full animate-spin mb-4"></div>
              <p class="text-pink-600 font-bold text-sm tracking-widest uppercase animate-pulse">Updating Results...</p>
            </div>
          
          <!-- Loading State (Skeleton UI) -->
          <div v-if="loading && !showNoResults" class="space-y-4 animate-pulse">
            <!-- Flight Count Skeleton -->
            <div class="flex justify-between items-center mb-6">
              <div class="h-8 bg-gray-200 rounded w-64"></div>
              <div class="h-4 bg-gray-100 rounded w-32"></div>
            </div>

            <!-- Skeleton Flight Cards -->
            <div v-for="i in 3" :key="i" class="bg-white rounded-sm border border-gray-200 overflow-hidden shadow-sm">
              <div class="px-6 py-4">
                <!-- Card Header Skeleton -->
                <div class="flex justify-between items-center mb-6 pb-6 border-b border-gray-100">
                  <div class="flex items-center gap-4">
                    <div class="space-y-2">
                      <div class="h-5 bg-pink-100 rounded w-32"></div>
                      <div class="h-3 bg-green-50 rounded w-20"></div>
                    </div>
                    <div class="h-6 bg-blue-50 rounded-full w-24"></div>
                  </div>
                  <div class="text-right">
                    <div class="h-8 bg-pink-200 rounded w-32 mb-1"></div>
                    <div class="h-3 bg-green-50 rounded w-20 ml-auto"></div>
                  </div>
                </div>

                <!-- Card Body Skeleton -->
                <div class="flex justify-between items-center gap-8 mb-4 px-4">
                  <div class="flex-1 space-y-2">
                    <div class="h-9 bg-gray-200 rounded w-28"></div>
                    <div class="h-4 bg-gray-100 rounded w-20"></div>
                  </div>
                  <div class="w-32 flex flex-col items-center">
                    <div class="w-full h-px bg-gray-200 mb-2"></div>
                    <div class="h-4 bg-gray-100 rounded w-20"></div>
                    <div class="w-full h-px bg-gray-200 mt-2"></div>
                  </div>
                  <div class="flex-1 text-right space-y-2">
                    <div class="h-9 bg-gray-200 rounded w-28 ml-auto"></div>
                    <div class="h-4 bg-gray-100 rounded w-20 ml-auto"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Search Status Info -->
            <div class="text-center py-6">
              <p class="text-xs text-gray-400 font-medium tracking-widest uppercase">
                Searching for the best deals... ({{ timeoutCountdown }}s)
              </p>
            </div>
          </div>
          
          <!-- No Results (including timeout case) -->
          <div v-else-if="showNoResults || filteredFlights.length === 0" class="bg-white rounded-sm shadow-sm border border-gray-200 p-12 text-center">
            <div class="w-16 h-16 mx-auto mb-6 text-gray-300">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-3">
              {{ showNoResults && flights.length === 0 ? 'No flights available' : 'No flights match your criteria.' }}
            </h3>
            <p class="text-gray-600 mb-4">
              {{ showNoResults && flights.length === 0 
                ? 'We could not find any available flights for your search criteria.' 
                : 'Try adjusting your filters or selecting a different date.' }}
            </p>
            
            <!-- Additional info for timeout case -->
            <div v-if="showNoResults && flights.length === 0" class="bg-yellow-50 border border-yellow-200 rounded-sm p-4 max-w-md mx-auto mb-6">
              <div class="flex items-start">
                <svg class="w-5 h-5 text-yellow-500 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                <div class="text-sm text-yellow-700">
                  <p class="font-medium">Search timeout or no flights found</p>
                  <p class="mt-1">The flight search took longer than expected or no flights were found. This could be due to high demand, system issues, or no available flights for your criteria.</p>
                </div>
              </div>
            </div>
            
            <div class="flex flex-col sm:flex-row gap-3 justify-center">
              <button @click="retryFetchFlights" 
                class="px-6 py-3 bg-pink-500 text-white rounded-sm hover:bg-pink-600 transition-colors font-medium">
                <svg class="w-4 h-4 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Try Again
              </button>
              <button @click="resetFilters" 
                class="px-6 py-3 border border-gray-300 rounded-sm text-gray-700 hover:bg-gray-50 transition-colors font-medium">
                Reset All Filters
              </button>
              <button @click="initializeEditSearch" 
                class="px-6 py-3 border border-pink-300 text-pink-500 rounded-sm hover:bg-pink-50 transition-colors font-medium">
                Edit Search
              </button>
            </div>
          </div>
          
          <!-- Flight List -->
          <div v-else>
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
              <h2 class="text-2xl font-bold text-gray-900">Available Flights ({{ filteredFlights.length }})</h2>
              <div class="text-sm text-gray-600">
                Sorted by: {{ filterOptions.sortOptions.find(s => s.value === filters.sortBy)?.label }}
              </div>
            </div>
            
            <div class="space-y-3">
              <FlightCard 
                v-for="f in filteredFlights" 
                :key="f.id"
                :flight="f"
                :isRoundTrip="isRoundTrip"
                :selectionPhase="selectionPhase"
                :selectedOutbound="bookingStore.selectedOutbound"
                :selectedReturn="bookingStore.selectedReturn"
                :selectButtonText="selectButtonText"
                :mlPricingEnabled="mlPricingEnabled"
                :showPricingDetails="showPricingDetails"
                :selectedPriceId="selectedPriceId"
                @view-pricing="togglePricingDetails"
                @select-flight="handleSelectFlight"
              />
            </div>
          </div>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>



<script setup>
import { ref, onMounted, computed, watch, onUnmounted } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useRoute, useRouter } from 'vue-router';
import flightService from '@/services/booking/flightService';
import airportService from '@/services/booking/airportService';
import { format, parseISO, isSameDay, addDays, subDays, startOfWeek, endOfWeek, eachDayOfInterval } from 'date-fns';

// Components
import FlightFilterSidebar from '@/components/booking/FlightFilterSidebar.vue';
import DateNavigator from '@/components/booking/DateNavigator.vue';
import FlightCard from '@/components/booking/FlightCard.vue';
import SeatClassModal from '@/components/booking/SeatClassModal.vue';

const route = useRoute();
const router = useRouter();
const bookingStore = useBookingStore();

const flights = ref([]);
const filteredFlights = ref([]);
const loading = ref(true);
const isFiltering = ref(false); // New: for transient "jumping" feedback
const showFilters = ref(false);
const showNoResults = ref(false);

// ============ NEW: ML PRICING STATE ============
const mlPricingEnabled = ref(true); // Toggle ML pricing on/off
const showPricingDetails = ref(false); // Show detailed pricing factors
const selectedPriceId = ref(null); // Track which flight's pricing details to show
// ================================================

// Timeout handling
const fetchTimeout = ref(null);
const timeoutCountdown = ref(15);
const countdownInterval = ref(null);

// Search Edit Feature State
const showEditSearch = ref(false);
const editSearchForm = ref({
  origin: '',
  destination: '',
  departure: '',
  returnDate: '',
  adults: 1,
  children: 0,
  infants: 0,
  tripType: 'one-way'
});

// Airport Autocomplete State for Edit Search
const fromResults = ref([]);
const toResults = ref([]);
const fromSearchInput = ref('');
const toSearchInput = ref('');
const selectedFromAirport = ref(null);
const selectedToAirport = ref(null);

// Multi-step selection
const selectionPhase = ref('outbound');

// Confirmation modal
const showConfirmation = ref(false);
const selectedFlight = ref(null);

// Session expired modal
const showSessionExpired = ref(false);

// Seat classes modal state
const showSeatClassesModal = ref(false);
const selectedFlightForSeats = ref(null);
const availableSeatClasses = ref([]);

// Seat class features from API
const seatClassFeatures = ref({});

// Filter State
const filters = ref({
  minPrice: null,
  maxPrice: null,
  departureTime: 'all',
  airline: 'all',
  flightType: 'all',
  sortBy: 'departure_time',
  hasAvailableSeats: false,
  seatClass: 'all',
});

// Date filter state
const dateFilter = ref({
  selectedDate: null,
  dateRange: 'exact',
  availableDates: []
});

// 7-day date selector state
const dateSelector = ref({
  currentWeekStart: null,
  weekDays: [],
  selectedDay: null
});

// Click outside handler for autocomplete
const handleSearchResultsClick = (e) => {
  if (!e.target.closest('.relative')) {
    fromResults.value = [];
    toResults.value = [];
  }
};

onMounted(() => {
  window.addEventListener('click', handleSearchResultsClick);
});

onUnmounted(() => {
  window.removeEventListener('click', handleSearchResultsClick);
});

// Filter options
const filterOptions = ref({
  departureTimes: [
    { value: 'all', label: 'Any Time' },
    { value: 'morning', label: 'Morning (5AM - 11AM)' },
    { value: 'afternoon', label: 'Afternoon (12PM - 5PM)' },
    { value: 'evening', label: 'Evening (6PM - 11PM)' },
    { value: 'night', label: 'Night (12AM - 4AM)' },
  ],
  flightTypes: [
    { value: 'all', label: 'All Flights' },
    { value: 'domestic', label: 'Domestic Only' },
    { value: 'international', label: 'International Only' },
  ],
  airlines: [],
  seatClasses: [
    { value: 'all', label: 'All Classes' },
  ],
  sortOptions: [
    { value: 'departure_time', label: 'Departure Time (Earliest)' },
    { value: 'price_low', label: 'Price (Low to High)' },
    { value: 'price_high', label: 'Price (High to Low)' },
    { value: 'duration', label: 'Duration (Shortest)' },
  ],
  dateRanges: [
    { value: 'exact', label: 'Exact date only' },
    { value: 'plusMinus1', label: '±1 day' },
    { value: 'plusMinus2', label: '±2 days' },
    { value: 'plusMinus3', label: '±3 days' },
  ]
});

// Session watcher
const sessionWatcher = ref(null);

// ============ NEW: ML PRICING METHODS ============

// Load seat class features and ML pricing info
const loadSeatClassFeatures = async () => {
  try {
    const response = await flightService.getSeatClassFeatures();
    if (response.data) {
      seatClassFeatures.value = response.data;
      console.log('✅ Seat class features loaded:', seatClassFeatures.value);
      
      // Update filter options dynamically
      updateSeatClassFilterOptions();
    }
  } catch (error) {
    console.error('❌ Failed to load seat class features:', error);
  }
};

// Get ML price prediction for a flight
const getMLPricePrediction = async (flight) => {
  if (!mlPricingEnabled.value) return flight.price;
  
  try {
    const flightData = {
      flight_number: flight.flight_number,
      airline_code: flight.airline_code,
      airline_name: flight.airline_name,
      origin: flight.origin,
      destination: flight.destination,
      departure_time: flight.departure_time,
      arrival_time: flight.arrival_time,
      total_stops: 0,
      is_domestic: flight.is_domestic,
      duration_hours: flight.flight_duration ? parseDuration(flight.flight_duration) : 1.5
    };
    
    const response = await flightService.getPricePrediction(flightData);
    
    if (response.data && response.data.success) {
      console.log(`💰 ML Price for ${flight.flight_number}: ₱${response.data.base_price.toLocaleString()}`);
      return {
        ...flight,
        price: response.data.base_price,
        ml_predicted: true,
        seat_class_prices: response.data.seat_class_prices,
        base_price: response.data.base_price,
        original_price: flight.price // Keep original for comparison
      };
    }
  } catch (error) {
    console.error('❌ Failed to get ML price prediction:', error);
  }
  
  return flight;
};

// Parse duration string like "1h 30m" to hours
const parseDuration = (durationStr) => {
  if (!durationStr) return 1.5;
  const hours = durationStr.match(/(\d+)h/);
  const minutes = durationStr.match(/(\d+)m/);
  let total = 0;
  if (hours) total += parseInt(hours[1]);
  if (minutes) total += parseInt(minutes[1]) / 60;
  return total;
};

// Toggle pricing details for a specific flight
const togglePricingDetails = (flightId) => {
  if (selectedPriceId.value === flightId) {
    selectedPriceId.value = null;
    showPricingDetails.value = false;
  } else {
    selectedPriceId.value = flightId;
    showPricingDetails.value = true;
  }
};

// Format price with ML indicator
const formatPrice = (flight) => {
  return {
    price: `₱${Number(flight.price).toLocaleString()}`,
    label: 'Price',
    tooltip: flight.ml_predicted ? 'This price is dynamically adjusted based on demand, time, and availability' : 'Standard fare',
    class: flight.ml_predicted ? 'text-pink-500' : 'text-gray-900'
  };
};

// Calculate price with selected seat class
const calculateSeatClassPrice = (basePrice, className, flight = null) => {
  // Use ML predicted seat class prices if available
  if (flight && flight.seat_class_prices && flight.seat_class_prices[className.toLowerCase()]) {
    return flight.seat_class_prices[className.toLowerCase()];
  }
  
  // Fallback to multipliers
  const priceMultipliers = {
    'economy': 1.0,
    'business': 1.8,
    'first': 2.5,
    'premium_economy': 1.3,
    'first_class': 2.5,
    'business_class': 1.8,
    'premium_economy': 1.3
  };
  
  const key = className.toLowerCase().replace(' ', '_');
  const multiplier = priceMultipliers[key] || 1.0;
  return Math.round(basePrice * multiplier);
};

// =================================================

// Update seat class filter options dynamically
const updateSeatClassFilterOptions = () => {
  // Start with default "All Classes" option
  const seatClassOptions = [{ value: 'all', label: 'All Classes' }];
  
  // Add seat classes from loaded features
  if (Object.keys(seatClassFeatures.value).length > 0) {
    Object.keys(seatClassFeatures.value).forEach(className => {
      const formattedName = className.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ');
      
      seatClassOptions.push({
        value: className,
        label: formattedName
      });
    });
  } else {
    // Fallback to default seat classes
    seatClassOptions.push(
      { value: 'economy', label: 'Economy' },
      { value: 'business', label: 'Business' },
      { value: 'first', label: 'First Class' },
      { value: 'premium_economy', label: 'Premium Economy' }
    );
  }
  
  filterOptions.value.seatClasses = seatClassOptions;
};

// Use trip type from Pinia store
const tripType = computed(() => bookingStore.tripType || route.query.tripType);
const isRoundTrip = computed(() => tripType.value === 'round_trip' || tripType.value === 'round-trip');

// Check if outbound is already selected
const hasOutboundSelected = computed(() => {
  return bookingStore.selectedOutbound !== null && bookingStore.selectedOutbound !== undefined;
});

// Check if return is already selected
const hasReturnSelected = computed(() => {
  return bookingStore.selectedReturn !== null && bookingStore.selectedReturn !== undefined;
});

// Computed for current search date
const currentSearchDate = computed(() => {
  return selectionPhase.value === 'outbound' ? route.query.departure : route.query.returnDate;
});

// Initialize edit search form with current route values
const initializeEditSearch = () => {
  // Check session first
  const sessionCheck = bookingStore.checkSession();
  if (!sessionCheck.valid) {
    showSessionExpiredModal();
    return;
  }

  editSearchForm.value = {
    origin: route.query.origin || '',
    destination: route.query.destination || '',
    departure: route.query.departure || '',
    returnDate: route.query.returnDate || '',
    adults: parseInt(route.query.adults) || 1,
    children: parseInt(route.query.children) || 0,
    infants: parseInt(route.query.infants) || 0,
    tripType: (route.query.tripType === 'round_trip' || route.query.tripType === 'round-trip') ? 'round-trip' : 'one-way'
  };
  
  // Set initial search strings for autocomplete
  fromSearchInput.value = route.query.origin || '';
  toSearchInput.value = route.query.destination || '';
  
  // Attempt to load full airport names if possible, but fallback to code
  selectedFromAirport.value = { code: route.query.origin };
  selectedToAirport.value = { code: route.query.destination };
  
  showEditSearch.value = true;
};

// Search airports for autocomplete
const searchEditAirports = async (query, target) => {
  if (query.includes(' - ')) return;

  const searchQuery = query.toUpperCase().trim();
  if (searchQuery.length < 3) {
    if (target === 'from') fromResults.value = [];
    else toResults.value = [];
    return;
  }

  try {
    const response = await airportService.searchAirports(searchQuery);
    const airports = response.data.results || response.data;
    
    // Filter out opposite selected airport
    const oppositeCode = target === 'from' ? selectedToAirport.value?.code : selectedFromAirport.value?.code;
    const filtered = airports.filter(a => a.code !== oppositeCode);

    if (target === 'from') fromResults.value = filtered;
    else toResults.value = filtered;
  } catch (error) {
    console.error("Airport search error:", error);
  }
};

// Select airport from results
const selectEditAirport = (airport, target) => {
  const displayString = `${airport.code} - ${airport.city}`;

  if (target === 'from') {
    selectedFromAirport.value = airport;
    fromSearchInput.value = displayString;
    fromResults.value = [];
    editSearchForm.value.origin = airport.code;
  } else {
    selectedToAirport.value = airport;
    toSearchInput.value = displayString;
    toResults.value = [];
    editSearchForm.value.destination = airport.code;
  }
};

// Submit edited search
const submitEditedSearch = () => {
  const searchParams = {
    ...editSearchForm.value,
    adults: editSearchForm.value.adults.toString(),
    children: editSearchForm.value.children.toString(),
    infants: editSearchForm.value.infants.toString()
  };
  
  // Update store
  bookingStore.setTripType(editSearchForm.value.tripType);
  
  // Navigate with new search params
  router.push({
    name: 'SearchResults',
    query: searchParams
  });
  
  // NEW: Clear previous selections when search is updated
  bookingStore.selectedOutbound = null;
  bookingStore.selectedReturn = null;
  selectionPhase.value = 'outbound';
  
  showEditSearch.value = false;
  
  // Reload flights with new params
  setTimeout(() => {
    fetchFlights();
  }, 100);
};

// Session expired modal handler
const showSessionExpiredModal = () => {
  showSessionExpired.value = true;
  
  // Auto redirect after 5 seconds
  setTimeout(() => {
    bookingStore.resetBooking();
    router.push({ name: 'Home' });
  }, 5000);
};

// Handle showing seat classes for a flight
const showSeatClasses = (flight) => {
  selectedFlightForSeats.value = flight;
  
  // Extract seat classes from flight data
  availableSeatClasses.value = extractSeatClassesFromFlight(flight);
  
  showSeatClassesModal.value = true;
};

// Extract seat classes from flight data
const extractSeatClassesFromFlight = (flight) => {
  if (!flight) return [];
  
  let seatClasses = [];
  
  // Structure 1: flight.available_classes array
  if (Array.isArray(flight.available_classes) && flight.available_classes.length > 0) {
    seatClasses = flight.available_classes.map(className => ({
      name: className,
      description: getSeatClassDescription(className),
      price: calculateSeatClassPrice(flight.price, className, flight),
      icon: getSeatClassIcon(className),
      features: getSeatClassFeatures(className),
      ml_predicted: flight.ml_predicted
    }));
  }
  // Structure 2: flight.seat_classes array
  else if (Array.isArray(flight.seat_classes) && flight.seat_classes.length > 0) {
    seatClasses = flight.seat_classes.map(seatClass => {
      if (typeof seatClass === 'string') {
        return {
          name: seatClass,
          description: getSeatClassDescription(seatClass),
          price: calculateSeatClassPrice(flight.price, seatClass, flight),
          icon: getSeatClassIcon(seatClass),
          features: getSeatClassFeatures(seatClass),
          ml_predicted: flight.ml_predicted
        };
      } else if (typeof seatClass === 'object') {
        return {
          name: seatClass.name || seatClass.class_name || seatClass.value || 'Unknown',
          description: seatClass.description || getSeatClassDescription(seatClass.name || seatClass.class_name),
          price: seatClass.price || calculateSeatClassPrice(flight.price, seatClass.name || seatClass.class_name, flight),
          icon: getSeatClassIcon(seatClass.name || seatClass.class_name),
          features: seatClass.features || getSeatClassFeatures(seatClass.name || seatClass.class_name),
          ml_predicted: flight.ml_predicted || seatClass.ml_predicted
        };
      }
      return null;
    }).filter(Boolean);
  }
  // Structure 3: Use loaded seat class features
  else if (Object.keys(seatClassFeatures.value).length > 0) {
    seatClasses = Object.keys(seatClassFeatures.value).map(className => {
      const formattedName = className.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ');
      
      return {
        name: formattedName,
        description: getSeatClassDescription(className),
        price: calculateSeatClassPrice(flight.price, className, flight),
        icon: getSeatClassIcon(className),
        features: seatClassFeatures.value[className],
        ml_predicted: flight.ml_predicted
      };
    });
  }
  // Default fallback
  else {
    seatClasses = [
      { 
        name: 'Economy', 
        description: getSeatClassDescription('economy'), 
        price: flight.price, 
        icon: getSeatClassIcon('economy'),
        features: getSeatClassFeatures('economy'),
        ml_predicted: flight.ml_predicted
      },
      { 
        name: 'Business', 
        description: getSeatClassDescription('business'), 
        price: calculateSeatClassPrice(flight.price, 'business', flight), 
        icon: getSeatClassIcon('business'),
        features: getSeatClassFeatures('business'),
        ml_predicted: flight.ml_predicted
      },
      { 
        name: 'First Class', 
        description: getSeatClassDescription('first'), 
        price: calculateSeatClassPrice(flight.price, 'first', flight), 
        icon: getSeatClassIcon('first'),
        features: getSeatClassFeatures('first'),
        ml_predicted: flight.ml_predicted
      }
    ];
  }
  
  return seatClasses;
};

// Helper function to get seat class description
const getSeatClassDescription = (className) => {
  const descriptions = {
    'economy': 'Standard seat with essential amenities, complimentary snacks, and in-flight entertainment',
    'business': 'Extra legroom, premium service, priority boarding, and enhanced meal options',
    'first': 'Luxury seating, gourmet meals, premium entertainment, and exclusive lounge access',
    'premium_economy': 'More legroom, enhanced meal service, and priority check-in',
    'first_class': 'Luxury seating, gourmet meals, premium entertainment, and exclusive lounge access',
    'business_class': 'Extra legroom, premium service, priority boarding, and enhanced meal options',
    'premium_economy': 'More legroom, enhanced meal service, and priority check-in'
  };
  
  const key = className.toLowerCase().replace(' ', '_');
  return descriptions[key] || 'Premium seating with enhanced services';
};

// Helper function to get seat class icon
const getSeatClassIcon = (className) => {
  const icons = {
    'economy': 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2',
    'business': 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    'first': 'M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7'
  };
  
  const key = className.toLowerCase().split(' ')[0];
  return icons[key] || icons.economy;
};

// Helper function to get seat class features (Dynamically from API or fallback)
const getSeatClassFeatures = (className) => {
  if (!className) return [];
  
  const key = className.toLowerCase().replace(' ', '_');
  
  // Try to get from API data first
  if (seatClassFeatures.value[key] && seatClassFeatures.value[key].length > 0) {
    return seatClassFeatures.value[key];
  }
  
  // If not found, check for similar keys
  for (const [apiKey, features] of Object.entries(seatClassFeatures.value)) {
    if (className.toLowerCase().includes(apiKey.replace('_', ' ')) || 
        apiKey.includes(className.toLowerCase().replace(' ', '_'))) {
      return features;
    }
  }
  
  // Fallback features
  const fallbackFeatures = {
    'economy': [
      'Standard legroom',
      'Complimentary snacks',
      'In-flight entertainment',
      'One carry-on bag'
    ],
    'business': [
      'Extra legroom',
      'Priority boarding',
      'Enhanced meal service',
      'Additional baggage allowance',
      'Premium entertainment'
    ],
    'first': [
      'Luxury seating',
      'Gourmet meals',
      'Premium entertainment',
      'Exclusive lounge access',
      'Priority everything',
      'Additional baggage'
    ],
    'premium_economy': [
      'More legroom than economy',
      'Enhanced meal service',
      'Priority check-in',
      'Additional baggage'
    ]
  };
  
  const fallbackKey = Object.keys(fallbackFeatures).find(k => 
    className.toLowerCase().includes(k.toLowerCase())
  ) || 'economy';
  
  return fallbackFeatures[fallbackKey] || fallbackFeatures.economy;
};

// Handle seat class selection
const handleSeatClassSelection = (seatClass) => {
  console.log('✅ Selected seat class:', seatClass.name);
  
  // Use the flight from the seat class modal
  const flightToStore = selectedFlightForSeats.value;
  
  if (!flightToStore) {
    console.error('❌ No flight found for seat class selection');
    return;
  }
  
  // Create a flight object with seat class info
  const flightWithSeatClass = {
    ...flightToStore,
    price: seatClass.price,
    original_price: flightToStore.original_price || flightToStore.price,
    base_price: flightToStore.base_price || flightToStore.price,
    seat_class: seatClass.name,
    selected_seat_class: seatClass.name,
    seat_class_details: seatClass,
    seat_class_features: seatClass.features,
    ml_predicted: seatClass.ml_predicted || flightToStore.ml_predicted
  };
  
  console.log('💾 Flight with seat class to store:', {
    flight_number: flightWithSeatClass.flight_number,
    seat_class: flightWithSeatClass.selected_seat_class,
    price: flightWithSeatClass.price,
    original_price: flightWithSeatClass.original_price,
    ml_predicted: flightWithSeatClass.ml_predicted,
    selection_phase: selectionPhase.value
  });
  
  // Store in Pinia based on selection phase
  if (isRoundTrip.value) {
    if (selectionPhase.value === 'outbound') {
      bookingStore.selectFlight(flightWithSeatClass, 'outbound');
      console.log('✅ Outbound flight with seat class saved to store');
    } else {
      bookingStore.selectFlight(flightWithSeatClass, 'return');
      console.log('✅ Return flight with seat class saved to store');
    }
  } else {
    bookingStore.selectFlight(flightWithSeatClass, 'outbound');
    console.log('✅ One-way flight with seat class saved to store');
  }
  
  // Close seat classes modal
  showSeatClassesModal.value = false;
  selectedFlightForSeats.value = null;
  
  // Show confirmation modal
  selectedFlight.value = flightWithSeatClass;
  showConfirmation.value = true;
};

// Cancel seat class selection
const cancelSeatClassSelection = () => {
  console.log('❌ Cancelled seat class selection');
  showSeatClassesModal.value = false;
  selectedFlightForSeats.value = null;
};

// Helper to log complete booking details
const logCompleteBookingDetails = () => {
  console.log('📊 COMPLETE BOOKING DETAILS:');
  console.log('============================');
  console.log(`Trip Type: ${bookingStore.tripType}`);
  
  if (bookingStore.selectedOutbound) {
    const outbound = bookingStore.selectedOutbound;
    console.log('Outbound Flight:');
    console.log(`  Flight: ${outbound.flight_number}`);
    console.log(`  Route: ${outbound.origin} → ${outbound.destination}`);
    console.log(`  Departure: ${formatTime(outbound.departure_time)}`);
    console.log(`  Seat Class: ${outbound.selected_seat_class || outbound.seat_class || 'Not selected'}`);
    console.log(`  Price with Seat Class: ₱${Number(outbound.price).toLocaleString()}`);
    console.log(`  ML Predicted: ${outbound.ml_predicted ? 'Yes' : 'No'}`);
    if (outbound.original_price) {
      console.log(`  Base Price: ₱${Number(outbound.original_price).toLocaleString()}`);
    }
  }
  
  if (bookingStore.selectedReturn) {
    const returnFlight = bookingStore.selectedReturn;
    console.log('Return Flight:');
    console.log(`  Flight: ${returnFlight.flight_number}`);
    console.log(`  Route: ${returnFlight.origin} → ${returnFlight.destination}`);
    console.log(`  Departure: ${formatTime(returnFlight.departure_time)}`);
    console.log(`  Seat Class: ${returnFlight.selected_seat_class || returnFlight.seat_class || 'Not selected'}`);
    console.log(`  Price with Seat Class: ₱${Number(returnFlight.price).toLocaleString()}`);
    console.log(`  ML Predicted: ${returnFlight.ml_predicted ? 'Yes' : 'No'}`);
    if (returnFlight.original_price) {
      console.log(`  Base Price: ₱${Number(returnFlight.original_price).toLocaleString()}`);
    }
  }
  
  const total = (bookingStore.selectedOutbound?.price || 0) + (bookingStore.selectedReturn?.price || 0);
  console.log(`Total: ₱${Number(total).toLocaleString()}`);
  console.log('============================');
};

// Sync route query with store on mount
onMounted(() => {
  console.log('🚀 SearchResults mounted');
  console.log('Route Query:', route.query);
  
  // Initialize session
  bookingStore.initSession();
  
  // Check session validity
  const sessionCheck = bookingStore.checkSession();
  if (!sessionCheck.valid) {
    console.log('❌ Session invalid, redirecting to home');
    router.push({ name: 'Home' });
    return;
  }
  
  if (route.query.tripType && !bookingStore.tripType) {
    bookingStore.setTripType(route.query.tripType);
  }
  
  console.log('Trip Type from Store:', bookingStore.tripType);
  console.log('Trip Type from Route:', route.query.tripType);
  console.log('Is Round Trip:', isRoundTrip.value);
  console.log('Has Outbound Selected:', hasOutboundSelected.value);
  console.log('Has Return Selected:', hasReturnSelected.value);
  
  // AUTO-SWITCH TO RETURN PHASE IF OUTBOUND IS ALREADY SELECTED
  if (isRoundTrip.value && hasOutboundSelected.value && !hasReturnSelected.value) {
    console.log('🔄 Outbound already selected, auto-switching to return phase');
    selectionPhase.value = 'return';
  }
  
  console.log('Initial Phase:', selectionPhase.value);
  
  // Load seat class features first
  loadSeatClassFeatures().then(() => {
    fetchFlights();
  });
  
  // Start session check interval
  sessionWatcher.value = setInterval(() => {
    const sessionCheck = bookingStore.checkSession();
    if (!sessionCheck.valid && sessionCheck.expired) {
      console.log('⏰ Session expired, redirecting to home');
      clearInterval(sessionWatcher.value);
      showSessionExpiredModal();
    }
  }, 30000);
});

onUnmounted(() => {
  // Clean up all intervals and timeouts
  if (sessionWatcher.value) {
    clearInterval(sessionWatcher.value);
  }
  if (fetchTimeout.value) {
    clearTimeout(fetchTimeout.value);
  }
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value);
  }
});

// Watch for filter changes
watch([filters, dateFilter], () => {
  applyFilters();
}, { deep: true });

// Extract unique dates from flights
const extractAvailableDates = (flightsList) => {
  const datesSet = new Set();
  flightsList.forEach(flight => {
    if (flight.departure_time) {
      const date = new Date(flight.departure_time);
      const dateString = format(date, 'yyyy-MM-dd');
      datesSet.add(dateString);
    }
  });
  return Array.from(datesSet).sort();
};

// Initialize 7-day date selector
const initializeDateSelector = () => {
  const searchDate = new Date(currentSearchDate.value);
  
  // Only set week start if it hasn't been set by navigation yet
  if (!dateSelector.value.currentWeekStart) {
    dateSelector.value.currentWeekStart = startOfWeek(searchDate, { weekStartsOn: 0 });
  }
  
  // Generate 7 days starting from week start
  dateSelector.value.weekDays = eachDayOfInterval({
    start: dateSelector.value.currentWeekStart,
    end: addDays(dateSelector.value.currentWeekStart, 6)
  }).map(date => ({
    date: date,
    dateString: format(date, 'yyyy-MM-dd'),
    dayName: format(date, 'EEE'),
    dayNumber: format(date, 'd'),
    monthName: format(date, 'MMM'),
    fullDate: format(date, 'yyyy-MM-dd'),
    isAvailable: dateFilter.value.availableDates.includes(format(date, 'yyyy-MM-dd')),
    isSelected: format(date, 'yyyy-MM-dd') === dateFilter.value.selectedDate,
    isToday: isSameDay(date, new Date()),
    isSearchDate: isSameDay(date, new Date(currentSearchDate.value))
  }));
  
  // Set selected day
  dateSelector.value.selectedDay = dateFilter.value.selectedDate;
};

// Navigate to previous week
const prevWeek = () => {
  dateSelector.value.currentWeekStart = subDays(dateSelector.value.currentWeekStart, 7);
  updateWeekDays();
  fetchFlights(); // Re-fetch for the new week
};

// Navigate to next week
const nextWeek = () => {
  dateSelector.value.currentWeekStart = addDays(dateSelector.value.currentWeekStart, 7);
  updateWeekDays();
  fetchFlights(); // Re-fetch for the new week
};

// Navigate to current week
const goToCurrentWeek = () => {
  const searchDate = new Date(currentSearchDate.value);
  dateSelector.value.currentWeekStart = startOfWeek(searchDate, { weekStartsOn: 0 });
  updateWeekDays();
  
  // Also reset date filter to search date
  dateFilter.value.selectedDate = currentSearchDate.value;
  dateFilter.value.dateRange = 'exact';
  
  fetchFlights(); // Re-fetch original week
  applyFilters();
};

// Update week days based on current week start
const updateWeekDays = () => {
  dateSelector.value.weekDays = eachDayOfInterval({
    start: dateSelector.value.currentWeekStart,
    end: addDays(dateSelector.value.currentWeekStart, 6)
  }).map(date => ({
    date: date,
    dateString: format(date, 'yyyy-MM-dd'),
    dayName: format(date, 'EEE'),
    dayNumber: format(date, 'd'),
    monthName: format(date, 'MMM'),
    fullDate: format(date, 'yyyy-MM-dd'),
    isAvailable: dateFilter.value.availableDates.includes(format(date, 'yyyy-MM-dd')),
    isSelected: format(date, 'yyyy-MM-dd') === dateFilter.value.selectedDate,
    isToday: isSameDay(date, new Date()),
    isSearchDate: isSameDay(date, new Date(currentSearchDate.value))
  }));
};

// Select a day from the 7-day selector
const selectDay = async (day) => {
  if (day.isAvailable) {
    isFiltering.value = true;
    dateSelector.value.selectedDay = day.dateString;
    dateFilter.value.selectedDate = day.dateString;
    dateFilter.value.dateRange = 'exact';
    
    // NEW: Update week days immediately so the indicator shows up instantly
    updateWeekDays();
    
    // Artificial delay to show the "jump" indicator
    await new Promise(resolve => setTimeout(resolve, 300));
    
    applyFilters();
    isFiltering.value = false;
  }
};

// Apply filters to flights
const applyFilters = () => {
  if (flights.value.length === 0) return;
  
  let result = [...flights.value];
  
  // Date filter
  if (dateFilter.value.selectedDate) {
    const selectedDate = new Date(dateFilter.value.selectedDate);
    
    result = result.filter(f => {
      if (!f.departure_time) return false;
      
      const flightDate = new Date(f.departure_time);
      const flightDateStr = format(flightDate, 'yyyy-MM-dd');
      const selectedDateStr = format(selectedDate, 'yyyy-MM-dd');
      
      if (dateFilter.value.dateRange === 'exact') {
        return flightDateStr === selectedDateStr;
      } else {
        const daysRange = parseInt(dateFilter.value.dateRange.replace('plusMinus', ''));
        const minDate = subDays(selectedDate, daysRange);
        const maxDate = addDays(selectedDate, daysRange);
        
        return flightDate >= minDate && flightDate <= maxDate;
      }
    });
  }
  
  // Price filter
  if (filters.value.minPrice) {
    result = result.filter(f => f.price >= parseFloat(filters.value.minPrice));
  }
  if (filters.value.maxPrice) {
    result = result.filter(f => f.price <= parseFloat(filters.value.maxPrice));
  }
  
  // Departure time filter
  if (filters.value.departureTime !== 'all') {
    result = result.filter(f => {
      const hour = new Date(f.departure_time).getHours();
      switch (filters.value.departureTime) {
        case 'morning': return hour >= 5 && hour <= 11;
        case 'afternoon': return hour >= 12 && hour <= 17;
        case 'evening': return hour >= 18 && hour <= 23;
        case 'night': return hour >= 0 && hour <= 4 || hour === 24;
        default: return true;
      }
    });
  }
  
  // Airline filter
  if (filters.value.airline !== 'all') {
    result = result.filter(f => f.airline_code === filters.value.airline);
  }
  
  // Flight type filter
  if (filters.value.flightType !== 'all') {
    result = result.filter(f => {
      if (filters.value.flightType === 'domestic') {
        return f.is_domestic === true;
      } else if (filters.value.flightType === 'international') {
        return f.is_domestic === false;
      }
      return true;
    });
  }
  
  // Available seats filter
  if (filters.value.hasAvailableSeats) {
    result = result.filter(f => f.available_seats > 0);
  }
  
  // Seat class filter
  if (filters.value.seatClass !== 'all') {
    result = result.filter(f => {
      if (f.available_classes && Array.isArray(f.available_classes)) {
        return f.available_classes.includes(filters.value.seatClass);
      }
      
      if (f.seat_classes && Array.isArray(f.seat_classes)) {
        return f.seat_classes.some(seatClass => {
          if (typeof seatClass === 'string') {
            return seatClass.toLowerCase() === filters.value.seatClass.toLowerCase();
          } else if (seatClass && typeof seatClass === 'object') {
            const className = seatClass.name || seatClass.class_name || seatClass.value || '';
            return className.toLowerCase() === filters.value.seatClass.toLowerCase();
          }
          return false;
        });
      }
      
      return true;
    });
  }
  
  // Sort flights
  result.sort((a, b) => {
    switch (filters.value.sortBy) {
      case 'price_low':
        return a.price - b.price;
      case 'price_high':
        return b.price - a.price;
      case 'duration':
        return (a.duration_minutes || 0) - (b.duration_minutes || 0);
      case 'departure_time':
      default:
        return new Date(a.departure_time) - new Date(b.departure_time);
    }
  });
  
  filteredFlights.value = result;
};

// Reset all filters
const resetFilters = () => {
  filters.value = {
    minPrice: null,
    maxPrice: null,
    departureTime: 'all',
    airline: 'all',
    flightType: 'all',
    sortBy: 'departure_time',
    hasAvailableSeats: false,
    seatClass: 'all',
  };
  
  dateFilter.value = {
    selectedDate: currentSearchDate.value,
    dateRange: 'exact',
    availableDates: []
  };
  
  goToCurrentWeek();
  filteredFlights.value = [...flights.value];
};

// Reset date filter only
const resetDateFilter = async () => {
  isFiltering.value = true;
  dateFilter.value.selectedDate = currentSearchDate.value;
  dateFilter.value.dateRange = 'exact';
  goToCurrentWeek();
  
  // NEW: Update week days immediately
  updateWeekDays();
  
  await new Promise(resolve => setTimeout(resolve, 300));
  
  applyFilters();
  isFiltering.value = false;
};

// Get unique airlines from flights
const extractAirlines = (flightsList) => {
  const airlinesSet = new Set();
  flightsList.forEach(flight => {
    if (flight.airline_code && flight.airline_name) {
      airlinesSet.add({
        code: flight.airline_code,
        name: flight.airline_name
      });
    }
  });
  return Array.from(airlinesSet);
};

// Get price range for price slider
const priceRange = computed(() => {
  if (flights.value.length === 0) return { min: 0, max: 1000 };
  
  const prices = flights.value.map(f => f.price);
  return {
    min: Math.min(...prices),
    max: Math.max(...prices)
  };
});

// Get unique dates for date filter dropdown
const uniqueDates = computed(() => {
  if (!dateFilter.value.availableDates.length) return [];
  
  return dateFilter.value.availableDates.map(dateStr => {
    const date = new Date(dateStr);
    return {
      value: dateStr,
      label: format(date, 'EEEE, MMMM d, yyyy'),
      shortLabel: format(date, 'MMM d, yyyy'),
      date: date
    };
  });
});

// Proceed to passenger details
const proceedToPassengerDetails = () => {
  console.log('🎟️ Proceeding to passenger details...');
  
  // Check session first
  const sessionCheck = bookingStore.checkSession();
  if (!sessionCheck.valid) {
    showSessionExpiredModal();
    return;
  }
  
  // Log complete booking details
  logCompleteBookingDetails();
  
  // Validate both flights are selected
  if (!hasOutboundSelected.value || (isRoundTrip.value && !hasReturnSelected.value)) {
    console.error('❌ Cannot proceed: Missing flight selections');
    notificationStore.warn('Please select both outbound and return flights before proceeding.');
    return;
  }
  
  // Navigate to passenger details
  router.push({ name: 'PassengerDetails' });
};

// Handle flight selection
const handleSelectFlight = async (flight) => {
  // Check session before proceeding
  const sessionCheck = bookingStore.checkSession();
  if (!sessionCheck.valid) {
    showSessionExpiredModal();
    return;
  }

  console.log('✈️ Flight clicked:', flight.flight_number, 'Phase:', selectionPhase.value);
  
  // Refresh session on user interaction
  bookingStore.startSession();
  
  // ============ NEW: Get ML price prediction ============
  if (mlPricingEnabled.value && !flight.ml_predicted) {
    const enhancedFlight = await getMLPricePrediction(flight);
    flight = enhancedFlight;
  }
  // =====================================================
  
  // Store the flight for seat class selection
  selectedFlightForSeats.value = flight;
  
  // Check if this flight is already selected
  let alreadySelected = false;
  let selectedFlightInStore = null;
  
  if (isRoundTrip.value) {
    selectedFlightInStore = selectionPhase.value === 'outbound' 
      ? bookingStore.selectedOutbound
      : bookingStore.selectedReturn;
  } else {
    selectedFlightInStore = bookingStore.selectedOutbound;
  }
  
  alreadySelected = selectedFlightInStore && selectedFlightInStore.flight_number === flight.flight_number;
  
  if (alreadySelected) {
    console.log('🔄 Flight already selected, showing seat classes for modification');
    showSeatClasses(flight);
  } else {
    // First show seat classes modal for new selection
    showSeatClasses(flight);
  }
};

// Confirm selection
const confirmSelection = () => {
  if (!selectedFlight.value) return;
  
  // Refresh session
  bookingStore.startSession();
  
  // Log complete booking details
  logCompleteBookingDetails();
  
  if (isRoundTrip.value) {
    if (selectionPhase.value === 'outbound') {
      console.log('✅ CONFIRMING OUTBOUND FLIGHT FOR ROUND-TRIP');
      
      // Log flight selection
      logFlightSelection(selectedFlight.value, 'outbound');
      
      // AUTO-SWITCH TO RETURN PHASE
      console.log('🔄 Auto-switching to return phase...');
      selectionPhase.value = 'return';
      
      // Close confirmation modal
      showConfirmation.value = false;
      selectedFlight.value = null;
      
      // Fetch return flights
      fetchFlights();
      window.scrollTo(0, 0);
      
    } else {
      console.log('✅ CONFIRMING COMPLETE ROUND-TRIP BOOKING');
      
      // Log return flight selection
      logFlightSelection(selectedFlight.value, 'return');
      
      // Log complete booking
      logCompleteBooking();
      
      // Navigate to passenger details
      router.push({ name: 'PassengerDetails' });
    }
  } else {
    console.log('✅ CONFIRMING ONE-WAY BOOKING');
    logFlightSelection(selectedFlight.value, 'outbound');
    router.push({ name: 'PassengerDetails' });
  }
  
  showConfirmation.value = false;
  selectedFlight.value = null;
};

// Cancel selection
const cancelSelection = () => {
  console.log('❌ Cancelled selection');
  showConfirmation.value = false;
  selectedFlight.value = null;
};

// Go to return phase (explicit user action)
const goToReturnPhase = () => {
  console.log('➡️ User clicked to go to return phase');
  
  // Clear any previous return selection if needed
  if (bookingStore.selectedReturn) {
    console.log('🧹 Clearing previous return selection before proceeding');
    bookingStore.selectedReturn = null;
  }
  
  // Switch phase and fetch flights
  selectionPhase.value = 'return';
  fetchFlights();
  window.scrollTo(0, 0);
};

// Go back to outbound phase (for round trip)
const goBackToOutbound = () => {
  console.log('⬅️ Going back to outbound phase');
  selectionPhase.value = 'outbound';
  fetchFlights();
  window.scrollTo(0, 0);
};

// Helper function to log flight selection
const logFlightSelection = (flight, type) => {
  console.log(`📝 ${type.toUpperCase()} FLIGHT SELECTED:`);
  console.log(`  Flight: ${flight.flight_number}`);
  console.log(`  Seat Class: ${flight.selected_seat_class || flight.seat_class || 'Not selected'}`);
  console.log(`  Route: ${flight.origin} → ${flight.destination}`);
  console.log(`  Departure: ${formatTime(flight.departure_time)} on ${formatDate(flight.departure_time)}`);
  console.log(`  Price: ₱${Number(flight.price).toLocaleString()}`);
  console.log(`  ML Predicted: ${flight.ml_predicted ? 'Yes' : 'No'}`);
  if (flight.original_price && flight.price !== flight.original_price) {
    console.log(`  Base Price: ₱${Number(flight.original_price).toLocaleString()}`);
    console.log(`  Seat Class Upcharge: ₱${Number(flight.price - flight.original_price).toLocaleString()}`);
  }
  console.log('');
};

// Helper function to log complete booking
const logCompleteBooking = () => {
  console.log('📊 COMPLETE BOOKING SUMMARY:');
  console.log('============================');
  console.log(`Trip Type: ${bookingStore.tripType || tripType.value}`);
  
  if (bookingStore.selectedOutbound) {
    const outbound = bookingStore.selectedOutbound;
    console.log('Outbound:');
    console.log(`  ${outbound.flight_number}: ${outbound.origin} → ${outbound.destination}`);
    console.log(`  Departure: ${formatTime(outbound.departure_time)}`);
    console.log(`  Seat Class: ${outbound.selected_seat_class || outbound.seat_class || 'Not selected'}`);
    console.log(`  Price: ₱${Number(outbound.price).toLocaleString()}`);
    console.log(`  ML Predicted: ${outbound.ml_predicted ? 'Yes' : 'No'}`);
  }
  
  if (bookingStore.selectedReturn) {
    const returnFlight = bookingStore.selectedReturn;
    console.log('Return:');
    console.log(`  ${returnFlight.flight_number}: ${returnFlight.origin} → ${returnFlight.destination}`);
    console.log(`  Departure: ${formatTime(returnFlight.departure_time)}`);
    console.log(`  Seat Class: ${returnFlight.selected_seat_class || returnFlight.seat_class || 'Not selected'}`);
    console.log(`  Price: ₱${Number(returnFlight.price).toLocaleString()}`);
    console.log(`  ML Predicted: ${returnFlight.ml_predicted ? 'Yes' : 'No'}`);
  }
  
  console.log('============================');
};

const fetchFlights = async () => {
  loading.value = true;
  showNoResults.value = false;
  timeoutCountdown.value = 15;
  
  // Clear any existing timeout and interval
  if (fetchTimeout.value) {
    clearTimeout(fetchTimeout.value);
  }
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value);
  }
  
  // Start countdown timer
  countdownInterval.value = setInterval(() => {
    if (timeoutCountdown.value > 0) {
      timeoutCountdown.value--;
    } else {
      clearInterval(countdownInterval.value);
    }
  }, 1000);
  
  // Set timeout to show no results after 15 seconds
  fetchTimeout.value = setTimeout(() => {
    if (loading.value) {
      console.log('⏰ Timeout reached - showing no flights message');
      showNoResults.value = true;
      loading.value = false;
      flights.value = [];
      filteredFlights.value = [];
      clearInterval(countdownInterval.value);
    }
  }, 15000);

  try {
    const isReturnPhase = selectionPhase.value === 'return';
    const searchDateStr = isReturnPhase ? route.query.returnDate : route.query.departure;
    const searchDate = new Date(searchDateStr);
    
    // Use currentWeekStart if it exists for the range, otherwise fallback to search date
    // This allows re-fetching when navigating via prev/next week
    const rangeAnchorDate = dateSelector.value.currentWeekStart || startOfWeek(searchDate, { weekStartsOn: 0 });
    
    const startDate = format(rangeAnchorDate, 'yyyy-MM-dd');
    const endDate = format(addDays(rangeAnchorDate, 6), 'yyyy-MM-dd'); // Fetch full 7 days of the current view
    
    const params = {
      origin: isReturnPhase ? route.query.destination : route.query.origin,
      destination: isReturnPhase ? route.query.origin : route.query.destination,
      start_date: startDate,
      end_date: endDate
    };

    console.log('📡 Fetching flights for date range:', startDate, 'to', endDate);

    const response = await flightService.getSchedules(params);
    
    console.log('📥 Raw API Response:', {
      status: response.status,
      data: response.data,
      dataType: typeof response.data
    });

    // Clear timeout and interval since we got a response
    clearInterval(countdownInterval.value);
    clearTimeout(fetchTimeout.value);
    
    // Handle paginated or flat response
    let fetchedFlights = [];
    if (response.data && Array.isArray(response.data.results)) {
      fetchedFlights = response.data.results;
    } else if (Array.isArray(response.data)) {
      fetchedFlights = response.data;
    }
    
    // Use directly - backend now provides ML-enhanced data
    flights.value = fetchedFlights;
    filteredFlights.value = [...flights.value];
    
    // DEBUG: Log flight data structure
    if (flights.value.length > 0) {
      console.log('First flight structure:', {
        flight_number: flights.value[0].flight_number,
        price: flights.value[0].price,
        ml_predicted: flights.value[0].ml_predicted,
        base_price: flights.value[0].base_price,
        seat_class_prices: flights.value[0].seat_class_prices
      });
    }
    
    // Check if response has data
    if (!fetchedFlights || fetchedFlights.length === 0) {
      showNoResults.value = true;
    } else {
      showNoResults.value = false;
    }
    
    // Extract unique airlines for filter dropdown
    const airlinesList = extractAirlines(flights.value);
    filterOptions.value.airlines = [
      { value: 'all', label: 'All Airlines' },
      ...airlinesList.map(a => ({ value: a.code, label: a.name }))
    ];
    
    // Extract unique dates for date filter
    dateFilter.value.availableDates = extractAvailableDates(flights.value);
    dateFilter.value.selectedDate = currentSearchDate.value;
    
    // Initialize date selector
    initializeDateSelector();
    
    console.log(`📊 Received ${flights.value.length} ${selectionPhase.value} flights`);
    console.log('Available dates:', dateFilter.value.availableDates);
    console.log('Airlines found:', airlinesList);
    
    // Apply initial filters
    applyFilters();
    
  } catch (error) {
    console.error("❌ API Error:", error);
    
    // Clear timeout and interval on error
    clearInterval(countdownInterval.value);
    clearTimeout(fetchTimeout.value);
    
    showNoResults.value = true;
    flights.value = [];
    filteredFlights.value = [];
  } finally {
    loading.value = false;
  }
};

// Retry fetching flights
const retryFetchFlights = () => {
  showNoResults.value = false;
  fetchFlights();
};

// Format seat classes for display
const formatSeatClasses = (seatClasses) => {
  if (!seatClasses || !Array.isArray(seatClasses)) return '';
  
  return seatClasses.map(sc => {
    if (typeof sc === 'string') {
      return sc;
    } else if (sc && typeof sc === 'object') {
      return sc.name || sc.class_name || sc.value || 'Unknown';
    }
    return 'Unknown';
  }).join(', ');
};

// Format time
const formatTime = (dateTimeString) => {
  if (!dateTimeString) return '';
  const date = new Date(dateTimeString);
  return date.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit', hour12: true });
};

// Format date
const formatDate = (dateTimeString) => {
  if (!dateTimeString) return '';
  const date = new Date(dateTimeString);
  return date.toLocaleDateString('en-PH', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' });
};

// Format date short
const formatDateShort = (dateTimeString) => {
  if (!dateTimeString) return '';
  const date = new Date(dateTimeString);
  return date.toLocaleDateString('en-PH', { month: 'short', day: 'numeric' });
};

// Format date for display
const formatDateDisplay = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return format(date, 'EEEE, MMMM d, yyyy');
};

// Format week range for display
const formatWeekRange = computed(() => {
  if (!dateSelector.value.currentWeekStart) return '';
  const weekEnd = addDays(dateSelector.value.currentWeekStart, 6);
  return `${format(dateSelector.value.currentWeekStart, 'MMM d')} - ${format(weekEnd, 'MMM d, yyyy')}`;
});

// Format duration
const formatDuration = (minutes) => {
  if (!minutes) return '';
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};

// Get selected flights summary for display
const selectedFlightsSummary = computed(() => {
  const summary = [];
  
  if (bookingStore.selectedOutbound) {
    // For one-way trips, don't show "Outbound" label
    const typeLabel = isRoundTrip.value ? 'Outbound' : 'Flight';
    
    summary.push({
      type: typeLabel,
      flight: bookingStore.selectedOutbound.flight_number,
      route: `${bookingStore.selectedOutbound.origin} → ${bookingStore.selectedOutbound.destination}`,
      time: formatTime(bookingStore.selectedOutbound.departure_time),
      date: formatDate(bookingStore.selectedOutbound.departure_time),
      price: Number(bookingStore.selectedOutbound.price).toLocaleString(),
      selected_seat_class: bookingStore.selectedOutbound.selected_seat_class || bookingStore.selectedOutbound.seat_class,
      seat_class_price: bookingStore.selectedOutbound.price,
      base_price: bookingStore.selectedOutbound.original_price || bookingStore.selectedOutbound.base_price || bookingStore.selectedOutbound.price,
      ml_predicted: bookingStore.selectedOutbound.ml_predicted
    });
  }
  
  if (bookingStore.selectedReturn) {
    summary.push({
      type: 'Return',
      flight: bookingStore.selectedReturn.flight_number,
      route: `${bookingStore.selectedReturn.origin} → ${bookingStore.selectedReturn.destination}`,
      time: formatTime(bookingStore.selectedReturn.departure_time),
      date: formatDate(bookingStore.selectedReturn.departure_time),
      price: Number(bookingStore.selectedReturn.price).toLocaleString(),
      selected_seat_class: bookingStore.selectedReturn.selected_seat_class || bookingStore.selectedReturn.seat_class,
      seat_class_price: bookingStore.selectedReturn.price,
      base_price: bookingStore.selectedReturn.original_price || bookingStore.selectedReturn.base_price || bookingStore.selectedReturn.price,
      ml_predicted: bookingStore.selectedReturn.ml_predicted
    });
  }
  
  return summary;
});

// Get total price
const totalPrice = computed(() => {
  let total = 0;
  if (bookingStore.selectedOutbound) {
    total += Number(bookingStore.selectedOutbound.price);
  }
  if (bookingStore.selectedReturn) {
    total += Number(bookingStore.selectedReturn.price);
  }
  return total;
});

// Get modal title based on trip type and phase
const modalTitle = computed(() => {
  if (isRoundTrip.value) {
    if (selectionPhase.value === 'outbound') {
      return 'Confirm Outbound Flight';
    } else {
      return 'Confirm Return Flight';
    }
  }
  return 'Confirm Flight Selection';
});

// Get confirm button text
const confirmButtonText = computed(() => {
  if (isRoundTrip.value) {
    if (selectionPhase.value === 'outbound') {
      return 'Confirm Outbound';
    } else {
      return 'Confirm Return';
    }
  }
  return 'Confirm Flight';
});

// Get modal action description
const modalActionDescription = computed(() => {
  if (isRoundTrip.value && selectionPhase.value === 'outbound') {
    return 'After confirming, click "Continue to Return Flight" to select your return flight.';
  } else if (isRoundTrip.value && selectionPhase.value === 'return') {
    return 'After confirming, click "Proceed to Passenger Details" to continue.';
  }
  return '';
});

// Get flight statistics
const flightStats = computed(() => {
  const total = flights.value.length;
  const filtered = filteredFlights.value.length;
  const lowestPrice = filteredFlights.value.length > 0 
    ? Math.min(...filteredFlights.value.map(f => f.price))
    : 0;
  const highestPrice = filteredFlights.value.length > 0
    ? Math.max(...filteredFlights.value.map(f => f.price))
    : 0;
  
  return {
    total,
    filtered,
    lowestPrice,
    highestPrice,
    priceRange: `${lowestPrice.toLocaleString()} - ${highestPrice.toLocaleString()}`
  };
});

// Get current date filter display
const dateFilterDisplay = computed(() => {
  if (!dateFilter.value.selectedDate) return 'No date selected';
  
  const dateLabel = formatDateDisplay(dateFilter.value.selectedDate);
  const rangeLabel = filterOptions.value.dateRanges.find(r => r.value === dateFilter.value.dateRange)?.label;
  
  return `${dateLabel} (${rangeLabel})`;
});

// Check if date filter is active
const isDateFilterActive = computed(() => {
  return dateFilter.value.selectedDate !== currentSearchDate.value || dateFilter.value.dateRange !== 'exact';
});

// Check if current week contains selected date
const currentWeekContainsSelectedDate = computed(() => {
  if (!dateFilter.value.selectedDate || !dateSelector.value.weekDays.length) return false;
  
  const selectedDateStr = dateFilter.value.selectedDate;
  return dateSelector.value.weekDays.some(day => day.dateString === selectedDateStr);
});

// Get phase-specific route info
const phaseRouteInfo = computed(() => {
  if (selectionPhase.value === 'outbound') {
    return {
      origin: route.query.origin,
      destination: route.query.destination,
      date: route.query.departure
    };
  } else {
    return {
      origin: route.query.destination,
      destination: route.query.origin,
      date: route.query.returnDate
    };
  }
});

// Get phase-specific button text
const selectButtonText = computed(() => {
  if (isRoundTrip.value) {
    return selectionPhase.value === 'outbound' ? 'Select Outbound' : 'Select Return';
  }
  return 'Select Flight';
});

// Get available seat class options from flights
const availableSeatClassOptions = computed(() => {
  // Start with "All Classes"
  const options = [{ value: 'all', label: 'All Classes' }];
  
  // Get unique seat classes from flights
  const uniqueClasses = new Set();
  
  flights.value.forEach(flight => {
    if (flight.available_classes && Array.isArray(flight.available_classes)) {
      flight.available_classes.forEach(className => {
        const key = className.toLowerCase().replace(' ', '_');
        uniqueClasses.add(key);
      });
    }
    
    if (flight.seat_classes && Array.isArray(flight.seat_classes)) {
      flight.seat_classes.forEach(seatClass => {
        if (typeof seatClass === 'string') {
          const key = seatClass.toLowerCase().replace(' ', '_');
          uniqueClasses.add(key);
        } else if (typeof seatClass === 'object') {
          const className = seatClass.name || seatClass.class_name || '';
          if (className) {
            const key = className.toLowerCase().replace(' ', '_');
            uniqueClasses.add(key);
          }
        }
      });
    }
  });
  
  // Convert to options
  Array.from(uniqueClasses).forEach(className => {
    const formattedName = className.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
    
    options.push({
      value: className,
      label: formattedName
    });
  });
  
  return options;
});
</script>



<style scoped>
/* Custom scrollbar */
::-webkit-scrollbar {
  width: 2px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

::-webkit-scrollbar-thumb {
  background: #FF579A;
  border-radius: 2px;
}

::-webkit-scrollbar-thumb:hover {
  background: #ff3d8b;
}

/* Smooth transitions */
* {
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

/* Focus styles */
:focus {
  outline: 2px solid #FF579A;
  outline-offset: 2px;
}

/* Hide number input arrows */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}

/* Animation for flight cards */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.flight-card-enter {
  animation: fadeInUp 0.3s ease-out;
}
</style>