<template>
  <div class="min-h-screen bg-gray-50 pb-20 lg:pb-0">
    <BookingStatusHeader />
    
    <!-- Price Calendar Modal -->
    <div v-if="showPriceCalendar" class="fixed inset-0 bg-black/60 backdrop-blur-md z-[60] flex items-center justify-center p-4">
      <PriceCalendar 
        :origin="phaseRouteInfo.origin"
        :destination="phaseRouteInfo.destination"
        :initialDate="phaseRouteInfo.date"
        @close="showPriceCalendar = false"
        @select="handleCalendarDateSelect"
      />
    </div>

    <!-- Edit Search Modal -->
    <div v-if="showEditSearch" class="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
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
                <label class="flex items-center">
                  <input type="radio" v-model="editSearchForm.tripType" value="multi-city" class="h-4 w-4 text-pink-500 focus:ring-pink-500 border-gray-300">
                  <span class="ml-2 text-gray-700">Multi-City</span>
                </label>
              </div>
            </div>
            
            <!-- Standard Route & Dates -->
            <div v-if="editSearchForm.tripType !== 'multi-city'" class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="relative">
                  <label class="block text-sm font-medium text-gray-700 mb-2">From</label>
                  <input v-model="fromSearchInput" type="text" 
                    @input="searchEditAirports(fromSearchInput, 'from')"
                    @keydown.enter.prevent="handleEditEnterKey(fromSearchInput, 'from')"
                    @focus="fromSearchInput = ''; fromResults = []"
                    placeholder="e.g. MNL"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                  <div v-if="fromResults.length" class="absolute z-[70] w-full bg-white border border-gray-200 rounded-md shadow-xl mt-1 max-h-60 overflow-y-auto">
                    <div v-for="airport in fromResults" :key="airport.code" 
                      @click="selectEditAirport(airport, 'from')"
                      class="px-4 py-3 hover:bg-pink-50 cursor-pointer border-b border-gray-50 last:border-b-0">
                      <div class="flex items-center justify-between">
                        <div>
                          <span class="font-bold text-gray-900">{{ airport.code }}</span>
                          <span class="ml-2 text-gray-600">{{ airport.city }}</span>
                        </div>
                        <span class="text-xs text-gray-400">{{ airport.name }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="relative">
                  <label class="block text-sm font-medium text-gray-700 mb-2">To</label>
                  <input v-model="toSearchInput" type="text" 
                    @input="searchEditAirports(toSearchInput, 'to')"
                    @keydown.enter.prevent="handleEditEnterKey(toSearchInput, 'to')"
                    @focus="toSearchInput = ''; toResults = []"
                    placeholder="e.g. CEB"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                  <div v-if="toResults.length" class="absolute z-[70] w-full bg-white border border-gray-200 rounded-md shadow-xl mt-1 max-h-60 overflow-y-auto">
                    <div v-for="airport in toResults" :key="airport.code" 
                      @click="selectEditAirport(airport, 'to')"
                      class="px-4 py-3 hover:bg-pink-50 cursor-pointer border-b border-gray-50 last:border-b-0">
                      <div class="flex items-center justify-between">
                        <div>
                          <span class="font-bold text-gray-900">{{ airport.code }}</span>
                          <span class="ml-2 text-gray-600">{{ airport.city }}</span>
                        </div>
                        <span class="text-xs text-gray-400">{{ airport.name }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Departure Date</label>
                  <input v-model="editSearchForm.departure" type="date" :min="todayDateString"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                </div>
                <div v-if="editSearchForm.tripType === 'round-trip'">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Return Date</label>
                  <input v-model="editSearchForm.returnDate" type="date" :min="editSearchForm.departure || todayDateString"
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                </div>
              </div>
            </div>

            <!-- Multi-City Legs -->
            <div v-else class="space-y-4">
              <div v-for="(leg, index) in editSearchForm.legs" :key="index" class="p-4 border border-gray-100 rounded-lg space-y-4 relative bg-gray-50/50">
                <button v-if="editSearchForm.legs.length > 2" @click="removeEditLeg(index)" 
                  class="absolute top-2 right-2 text-gray-400 hover:text-red-500">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
                <div class="text-xs font-bold text-gray-400 uppercase">Flight {{ index + 1 }}</div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div class="relative">
                    <label class="block text-xs font-medium text-gray-700 mb-1">From</label>
                    <input v-model="leg.fromSearch" type="text" 
                      @input="searchEditAirports(leg.fromSearch, 'from', index)"
                      @keydown.enter.prevent="handleEditEnterKey(leg.fromSearch, 'from', index)"
                      @focus="leg.fromSearch = ''; leg.fromResults = []"
                      placeholder="Origin"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-pink-500">
                    <div v-if="leg.fromResults.length" class="absolute z-[70] w-full bg-white border border-gray-200 rounded-md shadow-xl mt-1 max-h-40 overflow-y-auto">
                      <div v-for="airport in leg.fromResults" :key="airport.code" 
                        @click="selectEditAirport(airport, 'from', index)"
                        class="px-3 py-2 hover:bg-pink-50 cursor-pointer border-b border-gray-50 last:border-b-0 text-sm">
                        <div class="flex items-center justify-between">
                          <div>
                            <span class="font-bold text-gray-900">{{ airport.code }}</span>
                            <span class="ml-1 text-gray-600">{{ airport.city }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="relative">
                    <label class="block text-xs font-medium text-gray-700 mb-1">To</label>
                    <input v-model="leg.toSearch" type="text" 
                      @input="searchEditAirports(leg.toSearch, 'to', index)"
                      @keydown.enter.prevent="handleEditEnterKey(leg.toSearch, 'to', index)"
                      @focus="leg.toSearch = ''; leg.toResults = []"
                      placeholder="Destination"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-pink-500">
                    <div v-if="leg.toResults.length" class="absolute z-[70] w-full bg-white border border-gray-200 rounded-md shadow-xl mt-1 max-h-40 overflow-y-auto">
                      <div v-for="airport in leg.toResults" :key="airport.code" 
                        @click="selectEditAirport(airport, 'to', index)"
                        class="px-3 py-2 hover:bg-pink-50 cursor-pointer border-b border-gray-50 last:border-b-0 text-sm">
                        <div class="flex items-center justify-between">
                          <div>
                            <span class="font-bold text-gray-900">{{ airport.code }}</span>
                            <span class="ml-1 text-gray-600">{{ airport.city }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">Date</label>
                  <input v-model="leg.date" type="date" :min="index === 0 ? todayDateString : editSearchForm.legs[index-1].date"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-pink-500">
                </div>
              </div>
              <button @click="addEditLeg" v-if="editSearchForm.legs.length < 6"
                class="w-full py-2 border-2 border-dashed border-gray-300 text-gray-500 rounded-lg hover:border-pink-300 hover:text-pink-500 transition-colors text-sm font-medium">
                + Add Another Flight
              </button>
            </div>
            
            <!-- Passengers -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Passengers</label>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Adults</label>
                  <input v-model.number="editSearchForm.adults" type="number" min="1" 
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Children</label>
                  <input v-model.number="editSearchForm.children" type="number" min="0" 
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Infants</label>
                  <input v-model.number="editSearchForm.infants" type="number" min="0" 
                    class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-pink-500 focus:border-transparent">
                </div>
              </div>
            </div>
          </div>
          
          <div class="mt-8 flex justify-end space-x-4">
            <button @click="showEditSearch = false" 
              class="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors">
              Cancel
            </button>
            <button @click="submitEditedSearch" 
              class="px-6 py-2 bg-pink-500 text-white rounded-md hover:bg-pink-600 transition-colors font-medium">
              Update Search
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <SeatClassModal 
      :show="showSeatClassesModal"
      :flight="selectedFlightForSeats"
      :seatClasses="availableSeatClasses"
      @select-class="handleInlineSeatClassSelection({ flight: selectedFlightForSeats, seatClass: $event })"
      @close="cancelSeatClassSelection"
    />
    
    <!-- Loading Overlay -->
    <LoadingOverlay 
      :show="isProceedingToCheckout" 
      title="Securing your flight..."
      subtitle="Please wait while we confirm availability and lock in your price."
    />
    
    <!-- Confirmation Modal -->
    <div v-if="showConfirmation" class="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg shadow-2xl w-full max-w-lg">
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
            <div class="bg-pink-50 rounded-lg p-4">
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
                      <div class="font-medium text-gray-800">
                        Outbound • {{ bookingStore.selectedOutbound?.flight_number }}
                        <span v-if="bookingStore.selectedOutbound?.aircraft_name" class="ml-1 text-xs text-gray-400 font-normal">({{ bookingStore.selectedOutbound.aircraft_name }})</span>
                      </div>
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
                      <div class="font-medium text-gray-800">
                        Return • {{ selectedFlight?.flight_number }}
                        <span v-if="selectedFlight?.aircraft_name" class="ml-1 text-xs text-gray-400 font-normal">({{ selectedFlight.aircraft_name }})</span>
                      </div>
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
            <div class="bg-pink-50 rounded-lg p-4">
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
                  <div v-if="selectedFlight?.aircraft_name" class="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded ml-1">{{ selectedFlight.aircraft_name }}</div>
                </div>
                
                <div v-if="selectedFlight?.selected_seat_class" class="bg-pink-100 border border-pink-200 rounded-lg p-3">
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
                
                <div class="flex items-center justify-between mb-4">
                  <div>
                    <div class="text-2xl font-black text-gray-900 leading-none">{{ formatTime(selectedFlight?.departure_time) }}</div>
                    <div class="text-sm font-bold text-gray-800 mt-1">{{ selectedFlight?.origin }}</div>
                  </div>
                  <div class="flex-1 flex flex-col items-center px-4">
                    <div class="text-[10px] font-bold text-gray-400 mb-2 uppercase tracking-widest">
                      {{ selectedFlight?.flight_duration }}
                    </div>
                    <div class="w-full relative flex items-center h-2">
                       <div class="absolute left-0 right-0 h-[2px] bg-gray-300"></div>
                       <div class="absolute left-0 w-2 h-2 rounded-full border-2 border-pink-500 bg-white z-10"></div>
                       
                       <!-- Stop Dots -->
                       <div v-if="(selectedFlight?.total_stops || 0) > 0" class="flex justify-around absolute left-0 right-0 px-4">
                          <div v-for="n in (selectedFlight?.total_stops || 0)" :key="n" 
                            class="w-2.5 h-2.5 rounded-full bg-orange-200 border-2 border-orange-500 z-10 shadow-sm">
                          </div>
                       </div>
                       
                       <div class="absolute right-0 w-2 h-2 rounded-full border-2 border-gray-400 bg-white z-10"></div>
                    </div>
                    <div class="mt-2 text-[10px] font-bold" :class="selectedFlight?.total_stops > 0 ? 'text-orange-500' : 'text-green-600'">
                       {{ selectedFlight?.total_stops === 0 ? 'Non-stop' : `${selectedFlight?.total_stops} Stop${selectedFlight?.total_stops > 1 ? 's' : ''}` }}
                    </div>
                  </div>
                  <div class="text-right">
                    <div class="text-2xl font-black text-gray-900 leading-none">{{ formatTime(selectedFlight?.arrival_time) }}</div>
                    <div class="text-sm font-bold text-gray-800 mt-1">{{ selectedFlight?.destination }}</div>
                  </div>
                </div>
                
                <!-- Layovers List in Modal -->
                <div v-if="(selectedFlight?.layovers_data && selectedFlight.layovers_data.length > 0)" class="bg-white/50 rounded-lg p-3 border border-pink-100 space-y-2 mt-2">
                   <div v-for="(layover, idx) in selectedFlight.layovers_data" :key="idx" class="flex items-center justify-between text-[10px]">
                      <div class="flex items-center gap-2">
                         <div class="w-1.5 h-1.5 rounded-full bg-orange-400"></div>
                         <span class="font-bold text-gray-700">Stop {{ idx + 1 }}: {{ layover.airport }} ({{ layover.city }})</span>
                      </div>
                      <div class="text-gray-400">Layover: {{ layover.duration }}</div>
                   </div>
                </div>

                <div class="text-[10px] text-gray-500 font-medium">
                  {{ formatDate(selectedFlight?.departure_time) }} • {{ selectedFlight?.aircraft_name || 'Commercial Aircraft' }}
                </div>
              </div>
            </div>
            
            <!-- Next Step Info -->
            <div v-if="modalActionDescription" 
              class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
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
              class="flex-1 px-4 py-3 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100 transition-colors font-medium">
              Cancel
            </button>
            <button @click="confirmSelection" 
              class="flex-1 px-4 py-3 bg-pink-500 text-white rounded-md hover:bg-pink-600 transition-colors font-medium">
              {{ confirmButtonText }}
            </button>
          </div>
        </div>
      </div>
    </div>
    

    <!-- Session Expired Modal -->
    <div v-if="showSessionExpired" class="fixed inset-0 bg-black/60 backdrop-blur-md z-[60] flex items-center justify-center p-4">
      <div class="bg-white rounded-lg shadow-2xl w-full max-w-md">
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
          <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
              </svg>
              <div class="text-sm text-red-700">
                <p class="font-medium">Why did this happen?</p>
                <p class="mt-1">Flight search sessions expire after {{ bookingStore.isPractice || bookingStore.activityCode ? '30' : '15' }} minutes of inactivity to ensure you get the latest flight availability and pricing.</p>
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
            class="w-full px-6 py-3 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors font-medium">
            Go to Home Now
          </button>
        </div>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="max-w-screen-2xl mx-auto lg:px-8 py-8">
      <!-- Header -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
        <!-- Step Indicator -->
        <div v-if="isRoundTrip || isMultiCity" class="mb-4 sm:mb-6">
          <div class="flex items-center space-x-2 sm:space-x-4 overflow-x-auto pb-2 scrollbar-hide">
            <template v-if="isRoundTrip">
              <div :class="['flex-1 text-center py-1.5 sm:py-2 rounded-md min-w-[100px] sm:min-w-[120px] text-[10px] sm:text-xs', 
                       selectionPhase === 'outbound' ? 'bg-pink-500 text-white' : 'bg-gray-100 text-gray-600']">
                <div class="font-bold sm:font-medium">1. Select Outbound</div>
              </div>
              <div class="w-4 sm:w-8 h-px bg-gray-300 shrink-0"></div>
              <div :class="['flex-1 text-center py-1.5 sm:py-2 rounded-md min-w-[100px] sm:min-w-[120px] text-[10px] sm:text-xs', 
                       selectionPhase === 'return' ? 'bg-pink-500 text-white' : 'bg-gray-100 text-gray-600']">
                <div class="font-bold sm:font-medium">2. Select Return</div>
              </div>
            </template>
            <template v-else-if="isMultiCity">
              <div v-for="(seg, idx) in multiSegments" :key="idx" class="flex items-center flex-1">
                <div :class="['flex-1 text-center py-1.5 sm:py-2 rounded-md min-w-[100px] sm:min-w-[120px] text-[10px] sm:text-xs', 
                         currentSegmentIndex === idx ? 'bg-pink-500 text-white' : (idx < currentSegmentIndex ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600')]">
                  <div class="font-bold sm:font-medium">{{ idx + 1 }}. {{ seg.selectedFrom?.code || seg.origin }} → {{ seg.selectedTo?.code || seg.destination }}</div>
                </div>
                <div v-if="idx < multiSegments.length - 1" class="w-2 sm:w-4 h-px bg-gray-300 mx-1 sm:mx-2 shrink-0"></div>
              </div>
            </template>
          </div>
        </div>
        
        <!-- Trip Type and Edit Button -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <!-- Left Content -->
          <div class="min-w-0 space-y-1">
            <!-- Top Row -->
            <div class="flex flex-wrap items-center gap-2 mb-1 text-[8px] sm:text-[9px] font-semibold">
              <span
                class="rounded-full px-2 py-0.5"
                :class="isMultiCity 
                  ? 'bg-blue-100 text-blue-700' 
                  : (isRoundTrip ? 'bg-pink-100 text-pink-700' : 'bg-green-100 text-gray-700')"
              >
                {{ isMultiCity ? 'MULTI CITY' : (isRoundTrip ? 'ROUND TRIP' : 'ONE WAY') }}
              </span>

              <span class="rounded-full bg-green-100 px-2 py-0.5 text-gray-700 whitespace-nowrap">
                {{ formatDateShort(phaseRouteInfo.date) }}
              </span>

              <span class="rounded-full bg-green-100 px-2 py-0.5 text-gray-700 whitespace-nowrap">
                {{ Number(route.query.adults) + Number(route.query.children) }} Travelers
              </span>

              <span
                v-if="selectionPhase === 'return' && hasOutboundSelected"
                class="rounded-full bg-green-100 px-2 py-0.5 font-medium text-green-700 whitespace-nowrap"
              >
                ✓ Outbound Selected
              </span>
            </div>

            <!-- Route Line -->
            <div class="truncate text-gray-400 flex flex-col">
              <span class="text-[8px] sm:text-[9px]">
                    {{ selectionPhase === 'outbound' ? 'Departing:' : 'Returning:' }}
              </span>
              <span class="font-black text-lg sm:text-2xl text-black truncate">
                {{ phaseRouteInfo.origin }} → {{ phaseRouteInfo.destination }}
              </span>
            </div>
          </div>

          <!-- Edit Button -->
          <button
            @click="initializeEditSearch"
            class="inline-flex shrink-0 items-center justify-center gap-1.5 rounded border bg-[#FF579A] border-gray-300 px-3 sm:px-5 py-1.5 sm:py-1 text-sm sm:text-lg font-medium text-white hover:bg-[#FF579A]/80 cursor-pointer transition active:scale-95"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
            <span class="hidden xs:inline">Edit Search</span>
            <span class="xs:hidden">Edit</span>
          </button>
        </div>
        
        <!-- Auto-Switch Notification -->
        <div v-if="isRoundTrip && selectionPhase === 'return' && hasOutboundSelected" 
          class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
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
        
        <!-- Selected Flights Summary (Mobile Only) -->
        <div v-if="selectedFlightsSummary.length > 0" class="mt-6 pt-6 border-t border-gray-100 lg:hidden">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-black text-gray-900 uppercase tracking-tighter">Your Selection</h3>
            <div v-if="isRoundTrip && selectedFlightsSummary.length > 1" class="text-sm font-black text-pink-500">
               ₱{{ totalPrice.toLocaleString() }}
            </div>
          </div>
          
          <div class="space-y-3">
            <div v-for="item in selectedFlightsSummary" :key="item.type" 
              class="bg-white rounded-xl p-3 border border-pink-100 shadow-sm relative overflow-hidden">
              <div class="flex justify-between items-start">
                <div class="space-y-1 flex-1">
                  <div class="flex items-center gap-2">
                    <span class="text-[8px] font-black px-1.5 py-0.5 bg-pink-500 text-white rounded uppercase tracking-widest">{{ item.type }}</span>
                    <span class="text-[10px] font-bold text-gray-800">{{ item.origin }} → {{ item.destination }}</span>
                  </div>
                  <div class="flex items-center gap-3 text-[9px] text-gray-500 font-bold">
                    <span>{{ item.time }}</span>
                    <span>•</span>
                    <span>{{ item.date }}</span>
                    <span>•</span>
                    <span :class="item.stops > 0 ? 'text-orange-500' : 'text-green-600'">{{ item.stops === 0 ? 'Non-stop' : `${item.stops} Stop` }}</span>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-xs font-black text-gray-900">₱{{ item.price }}</div>
                  <div v-if="item.selected_seat_class" class="text-[8px] font-bold text-pink-500 uppercase">{{ item.selected_seat_class }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Phase Navigation (Round Trips Only) -->
          <div v-if="isRoundTrip" class="mt-6 flex flex-wrap gap-2">
            <button v-if="selectionPhase === 'return'" @click="goBackToOutbound" 
              class="flex-1 inline-flex justify-center items-center px-4 py-2 bg-gray-100 rounded-lg text-gray-700 hover:bg-gray-200 transition-colors text-[10px] font-black uppercase tracking-widest">
              Back to Outbound
            </button>
            <button v-if="selectionPhase === 'outbound' && hasOutboundSelected && !hasReturnSelected" 
              @click="goToReturnPhase" 
              class="flex-1 inline-flex justify-center items-center px-4 py-2 bg-[#FF579A] text-white rounded-lg hover:bg-[#FF579A]/90 transition-colors text-[10px] font-black uppercase tracking-widest">
              Choose Return
            </button>
            <button v-if="hasOutboundSelected && hasReturnSelected" 
              @click="proceedToPassengerDetails"
              class="flex-1 inline-flex justify-center items-center px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-[10px] font-black uppercase tracking-widest">
              Confirm & Continue
            </button>
          </div>
        </div>
      </div>
      
      <!-- Mobile Filter Toggle -->
      <div class="lg:hidden mb-6">
        <button @click="showFilters = !showFilters" 
          class="w-full flex items-center justify-between p-4 bg-white rounded-lg shadow-sm border border-gray-200">
          <div class="flex items-center space-x-2">
            <svg class="w-5 h-5 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            <span class="font-medium text-gray-800 text-[11px] uppercase tracking-wider">Filters & Sort</span>
            <span v-if="filteredFlights.length < flights.length" class="text-[9px] font-bold text-pink-500">
              ({{ filteredFlights.length }} of {{ flights.length }})
            </span>
          </div>
          <svg :class="['w-5 h-5 text-gray-500 transform transition-transform', showFilters ? 'rotate-180' : '']" 
               fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
      
      <div class="flex flex-col lg:flex-row lg:items-start gap-8">
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
        <main class="flex-1 min-w-0">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-bold text-gray-500 uppercase tracking-widest">Select Departure Date</h3>
            <button 
              @click="openPriceCalendar"
              class="flex items-center gap-2 px-3 py-1.5 bg-pink-50 text-pink-600 rounded-md hover:bg-pink-100 transition-colors text-xs font-bold uppercase tracking-tight"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Month View (Low Fares)
            </button>
          </div>
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
            <div v-for="i in 3" :key="i" class="bg-white rounded-md border border-gray-200 overflow-hidden shadow-sm">
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
          <div v-else-if="showNoResults || filteredFlights.length === 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
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
            <div v-if="showNoResults && flights.length === 0" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 max-w-md mx-auto mb-6">
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
                class="px-6 py-3 bg-pink-500 text-white rounded-md hover:bg-pink-600 transition-colors font-medium">
                <svg class="w-4 h-4 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Try Again
              </button>
              <button @click="resetFilters" 
                class="px-6 py-3 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors font-medium">
                Reset All Filters
              </button>
              <button @click="initializeEditSearch" 
                class="px-6 py-3 border border-pink-300 text-pink-500 rounded-md hover:bg-pink-50 transition-colors font-medium">
                Edit Search
              </button>
            </div>
          </div>
          
          <!-- Flight List -->
          <div v-else>
            <div class="flex flex-col mb-4">
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
                <h2 class="text-2xl font-bold text-gray-900">Available Flights ({{ filteredFlights.length }})</h2>
              </div>
              
              <!-- Quick Sort Tabs -->
              <div class="grid grid-cols-3 gap-2 bg-gray-100 p-1 rounded-2xl shadow-inner mb-6">
                <button 
                  v-for="tab in quickSortTabs" 
                  :key="tab.value"
                  @click="setQuickSort(tab.value)"
                  :class="[
                    'flex-1 py-3 px-2 rounded-xl transition-all duration-300 group relative overflow-hidden',
                    filters.sortBy === tab.value 
                      ? 'bg-white text-pink-600 shadow-md ring-1 ring-pink-100' 
                      : 'text-gray-500 hover:bg-white/50 hover:text-gray-800'
                  ]"
                >
                  <div class="flex flex-col items-center justify-center space-y-1 relative z-10">
                    <div class="flex items-center gap-1.5">
                      <svg v-if="tab.label === 'Cheapest'" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                      <svg v-if="tab.label === 'Best'" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-7.714 2.143L11 21l-2.286-6.857L1 12l7.714-2.143L11 3z" /></svg>
                      <svg v-if="tab.label === 'Quickest'" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                      <span class="uppercase tracking-tighter text-[9px] font-black">{{ tab.label }}</span>
                    </div>
                    <div v-if="tab.price" class="text-xs sm:text-base font-black leading-none" :class="filters.sortBy === tab.value ? 'text-pink-600' : 'text-gray-900'">
                      ₱{{ Number(tab.price).toLocaleString() }}
                    </div>
                    <div v-if="tab.duration" class="text-[8px] sm:text-[9px] font-bold text-gray-400 opacity-80">{{ tab.duration }} avg.</div>
                  </div>
                  <!-- Selection Glow -->
                  <div v-if="filters.sortBy === tab.value" class="absolute inset-0 bg-gradient-to-br from-pink-500/5 to-transparent"></div>
                </button>
              </div>
            </div>
            
            <TransitionGroup 
              tag="div" 
              name="flight-list" 
              class="space-y-5"
            >
              <FlightCard 
                v-for="f in paginatedFlights" 
                :key="f.id"
                :flight="f"
                :isRoundTrip="isRoundTrip"
                :isMultiCity="isMultiCity"
                :selectionPhase="selectionPhase"
                :selectedOutbound="bookingStore.selectedOutbound"
                :selectedReturn="bookingStore.selectedReturn"
                :selectedSegmentFlight="isMultiCity ? bookingStore.multiCitySegments[currentSegmentIndex]?.selectedFlight : null"
                :selectButtonText="selectButtonText"
                :mlPricingEnabled="mlPricingEnabled"
                :showPricingDetails="showPricingDetails"
                :selectedPriceId="selectedPriceId"
                :parsedSeatClasses="f.showInlineClasses ? extractSeatClassesFromFlight(f) : []"
                @view-pricing="togglePricingDetails"
                @select-flight="handleSelectFlight"
                @select-seat-class="handleInlineSeatClassSelection"
              />
            </TransitionGroup>

            <!-- Pagination -->
            <div v-if="totalPages > 1" class="mt-10 flex flex-col sm:flex-row items-center justify-between gap-4 py-8 border-t border-gray-100">
              <div class="flex flex-col">
                <div class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mb-1">Results Navigation</div>
                <div class="text-xs font-bold text-gray-600">
                  Showing <span class="text-pink-600">{{ ((currentPage - 1) * itemsPerPage) + 1 }}</span> to 
                  <span class="text-pink-600">{{ Math.min(currentPage * itemsPerPage, filteredFlights.length) }}</span> 
                  of <span class="text-pink-600">{{ filteredFlights.length }}</span> flights
                </div>
              </div>
              
              <div class="flex items-center space-x-2">
                <!-- Previous Button -->
                <button 
                  @click="changePage(currentPage - 1)" 
                  :disabled="currentPage === 1"
                  class="group flex items-center justify-center w-10 h-10 rounded-xl border border-gray-200 bg-white text-gray-500 hover:border-pink-300 hover:text-pink-500 disabled:opacity-20 disabled:cursor-not-allowed transition-all duration-300 shadow-sm hover:shadow-md"
                >
                  <svg class="w-5 h-5 transition-transform group-hover:-translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                
                <!-- Page Numbers -->
                <div class="flex items-center bg-gray-50 p-1 rounded-2xl border border-gray-100">
                  <template v-for="page in totalPages" :key="page">
                    <button 
                      v-if="page === 1 || page === totalPages || (page >= currentPage - 1 && page <= currentPage + 1)"
                      @click="changePage(page)"
                      :class="[
                        'min-w-[40px] h-10 rounded-xl text-xs font-black transition-all duration-300',
                        currentPage === page 
                          ? 'bg-white text-pink-600 shadow-lg shadow-pink-100/50 scale-105 ring-1 ring-pink-100' 
                          : 'text-gray-400 hover:text-gray-900 hover:bg-white/50'
                      ]"
                    >
                      {{ page }}
                    </button>
                    <span v-else-if="(page === 2 && currentPage > 3) || (page === totalPages - 1 && currentPage < totalPages - 2)" 
                          class="w-6 text-center text-gray-300 font-black text-[10px] tracking-widest">...</span>
                  </template>
                </div>

                <!-- Next Button -->
                <button 
                  @click="changePage(currentPage + 1)" 
                  :disabled="currentPage === totalPages"
                  class="group flex items-center justify-center w-10 h-10 rounded-xl border border-gray-200 bg-white text-gray-500 hover:border-pink-300 hover:text-pink-500 disabled:opacity-20 disabled:cursor-not-allowed transition-all duration-300 shadow-sm hover:shadow-md"
                >
                  <svg class="w-5 h-5 transition-transform group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 19l7-7-7-7" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          </div>
        </main>

        <!-- Right Sidebar (Desktop Select Summary) -->
        <aside v-if="selectedFlightsSummary.length > 0" class="w-full lg:w-[280px] shrink-0 sticky top-8 z-10 hidden lg:block">
           <div class="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
              <div class="p-4 bg-gray-50 border-b border-gray-100 flex justify-between items-center">
                 <h3 class="text-xs font-black text-gray-900 uppercase tracking-tighter">Your Itinerary</h3>
                 <div v-if="selectedFlightsSummary.length > 1" class="text-xs font-black text-[#FF579A]">₱{{ totalPrice.toLocaleString() }}</div>
              </div>
              
              <div class="p-4 space-y-4">
                <div v-for="item in selectedFlightsSummary" :key="item.type" 
                  class="bg-white rounded-xl p-4 border border-gray-100 relative group transition-colors hover:border-pink-200">
                  <div class="flex justify-between items-center mb-3">
                    <span class="text-[8px] font-black px-1.5 py-0.5 bg-pink-500 text-white rounded uppercase tracking-widest">{{ item.type }}</span>
                    <span class="text-[9px] font-bold text-gray-400 uppercase">{{ item.flight }}</span>
                  </div>

                  <div class="space-y-3">
                    <div class="flex items-center justify-between">
                      <div class="text-sm font-black text-gray-900">{{ item.origin }}</div>
                      <div class="flex-1 flex flex-col items-center px-2">
                        <div class="w-full border-t border-dashed border-gray-200 relative my-1">
                          <svg class="w-2.5 h-2.5 text-pink-300 absolute -top-1.5 left-1/2 -translate-x-1/2" fill="currentColor" viewBox="0 0 20 20"><path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" /></svg>
                        </div>
                      </div>
                      <div class="text-sm font-black text-gray-900">{{ item.destination }}</div>
                    </div>

                    <div class="flex justify-between items-end border-t border-gray-50 pt-2">
                      <div class="space-y-0.5">
                        <div class="text-[10px] font-black text-gray-900 leading-none">{{ item.time }}</div>
                        <div class="text-[8px] font-bold text-gray-400 uppercase tracking-tighter">{{ item.date }}</div>
                      </div>
                      <div class="text-right">
                        <div class="text-[10px] font-black text-pink-600">₱{{ item.price }}</div>
                        <div v-if="item.selected_seat_class" class="text-[8px] font-bold text-gray-400 uppercase italic">{{ item.selected_seat_class }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-if="isRoundTrip" class="px-4 pb-4 space-y-3">
                <button v-if="selectionPhase === 'return' || hasReturnSelected" @click="goBackToOutbound" 
                  class="w-full py-2 bg-gray-50 border border-gray-100 rounded-xl text-gray-500 hover:bg-gray-100 transition-all text-[10px] font-black uppercase tracking-widest">
                  Modify Outbound
                </button>
                
                <button v-if="selectionPhase === 'outbound' && hasOutboundSelected && !hasReturnSelected" 
                  @click="goToReturnPhase" 
                  class="w-full py-3 bg-[#FF579A] text-white rounded-xl hover:bg-[#FF579A]/90 transition-all text-[10px] font-black uppercase tracking-widest shadow-lg shadow-pink-100">
                  Select Return Flight
                </button>
                
                <button v-if="hasOutboundSelected && hasReturnSelected" 
                  @click="proceedToPassengerDetails"
                  class="w-full py-3 bg-green-500 text-white rounded-xl hover:bg-green-600 transition-all text-[10px] font-black uppercase tracking-widest shadow-lg shadow-green-100">
                  Checkout Now
                </button>
              </div>
           </div>
        </aside>
      </div>
    </div>
  </div>
</template>



<script setup>
import { ref, onMounted, computed, watch, onUnmounted } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useNotificationStore } from '@/stores/notification';
import { useRoute, useRouter } from 'vue-router';
import flightService from '@/services/booking/flightService';
import airportService from '@/services/booking/airportService';
import { format, parseISO, isSameDay, addDays, subDays, startOfWeek, endOfWeek, eachDayOfInterval } from 'date-fns';

// Components
import FlightFilterSidebar from '@/components/booking/FlightFilterSidebar.vue';
import DateNavigator from '@/components/booking/DateNavigator.vue';
import PriceCalendar from '@/components/booking/PriceCalendar.vue';
import FlightCard from '@/components/booking/FlightCard.vue';
import SeatClassModal from '@/components/booking/SeatClassModal.vue';
import BookingStatusHeader from '@/components/booking/BookingStatusHeader.vue';
import LoadingOverlay from '@/components/common/LoadingOverlay.vue';

const showPriceCalendar = ref(false);

const openPriceCalendar = () => {
  showPriceCalendar.value = true;
};

const handleCalendarDateSelect = (date) => {
  showPriceCalendar.value = false;
  // Use the existing selectDay method to fetch flights for the new date
  selectDay({ dateString: date });
};

const route = useRoute();
const router = useRouter();
const bookingStore = useBookingStore();
const notificationStore = useNotificationStore();

const flights = ref([]);
const filteredFlights = ref([]);
const loading = ref(true);
const isFiltering = ref(false); // New: for transient "jumping" feedback
const showFilters = ref(false);
const showNoResults = ref(false);

// Pagination State
const currentPage = ref(1);
const itemsPerPage = ref(5);

const todayDateString = computed(() => {
  return format(new Date(), 'yyyy-MM-dd');
});

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
  tripType: 'one-way',
  legs: [] // For multi-city
});

// Airport Autocomplete State for Edit Search
const fromResults = ref([]);
const toResults = ref([]);
const fromSearchInput = ref('');
const toSearchInput = ref('');
const selectedFromAirport = ref(null);
const selectedToAirport = ref(null);

// Methods for Multi-City legs
const addEditLeg = () => {
  if (editSearchForm.value.legs.length < 6) {
    const lastLeg = editSearchForm.value.legs[editSearchForm.value.legs.length - 1];
    editSearchForm.value.legs.push({
      fromSearch: lastLeg?.selectedTo ? `${lastLeg.selectedTo.code} - ${lastLeg.selectedTo.city}` : '',
      toSearch: '',
      selectedFrom: lastLeg?.selectedTo || null,
      selectedTo: null,
      date: lastLeg?.date || todayDateString.value,
      fromResults: [],
      toResults: []
    });
  }
};

const removeEditLeg = (index) => {
  if (editSearchForm.value.legs.length > 2) {
    editSearchForm.value.legs.splice(index, 1);
  }
};

// Multi-step selection
const selectionPhase = ref('outbound');
const currentSegmentIndex = ref(0);
const multiCitySegments = ref([]);

// Parse segments from query if multi-city
onMounted(() => {
  // NEW: Clear previous flight selections whenever Search Results is opened/navigated to
  bookingStore.selectedOutbound = null;
  bookingStore.selectedReturn = null;
  selectionPhase.value = 'outbound';
  currentSegmentIndex.value = 0;
  
  if (bookingStore.multiCitySegments) {
    bookingStore.multiCitySegments.forEach(seg => { seg.selectedFlight = null; });
  }

  if (route.query.tripType === 'multi-city' && route.query.segments) {
    try {
      multiCitySegments.value = JSON.parse(route.query.segments);
      console.log('🌍 Multi-city segments parsed:', multiCitySegments.value);
    } catch (e) {
      console.error('❌ Failed to parse segments:', e);
    }
  }
});

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
  stops: 'all',
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
const isProceedingToCheckout = ref(false);
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

// Quick Sort Tabs Data
const quickSortTabs = computed(() => {
  if (filteredFlights.value.length === 0) return [];
  
  // Find cheapest
  const cheapest = [...filteredFlights.value].sort((a, b) => a.price - b.price)[0];
  
  // Find quickest (shortest duration)
  const quickest = [...filteredFlights.value].sort((a, b) => (a.duration_minutes || 0) - (b.duration_minutes || 0))[0];
  
  // Find best (optimal balance of price and duration)
  // Simplified formula: normalize price and duration (0-1), add them. Lowest score wins.
  const maxPrice = Math.max(...filteredFlights.value.map(f => f.price));
  const maxDuration = Math.max(...filteredFlights.value.map(f => f.duration_minutes || 1000));
  
  const best = [...filteredFlights.value].sort((a, b) => {
    const scoreA = (a.price / maxPrice) * 0.6 + ((a.duration_minutes || 0) / maxDuration) * 0.4;
    const scoreB = (b.price / maxPrice) * 0.6 + ((b.duration_minutes || 0) / maxDuration) * 0.4;
    return scoreA - scoreB;
  })[0];

  return [
    { 
      value: 'price_low', 
      label: 'Cheapest', 
      price: cheapest?.price, 
      duration: formatDuration(cheapest?.duration_minutes) 
    },
    { 
      value: 'best', 
      label: 'Best', 
      price: best?.price,
      duration: formatDuration(best?.duration_minutes)
    },
    { 
      value: 'duration', 
      label: 'Quickest', 
      price: quickest?.price, 
      duration: formatDuration(quickest?.duration_minutes) 
    }
  ];
});

const setQuickSort = (sortValue) => {
  filters.value.sortBy = sortValue;
};

// Session watcher
const sessionWatcher = ref(null);

// ============ NEW: ML PRICING METHODS ============

// Load seat class features and ML pricing info
const fareBundlesData = ref({});

const loadSeatClassFeatures = async () => {
  try {
    const response = await flightService.getSeatClassFeatures();
    if (response.data && response.data.data) {
      seatClassFeatures.value = response.data.data;
      if (response.data.bundles) {
        fareBundlesData.value = response.data.bundles;
        console.log('✅ Fare bundles loaded from DB:', fareBundlesData.value);
      }
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
const togglePricingDetails = (flight) => {
  const flightId = flight.price_id || flight.id;
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

// Markups for different fare families
const BUNDLE_MARKUPS = {
  'basic': 0,           // Legacy fallback
  'super_saver': 0,     // PAL Super Saver / budget basic
  'saver': 1000,        // PAL Saver
  'value': 2200,        // PAL Value
  'standard': 2000,     // General standard
  'flex': 4500,         // PAL Flex / high flexibility
  'comfort': 6500,      // PAL Comfort
  'premium': 6000,      // General premium
  'business': 12000,    // General business
  'business_value': 12000, // PAL Business Value
  'business_flex': 18000   // PAL Business Flex
};

// Calculate price with selected seat class
const calculateSeatClassPrice = (basePrice, className, flight = null, fareFamily = 'basic') => {
  let price = 0;
  
  // 1. First priority: Check if we have dynamic seat class data with a multiplier
  if (flight && Array.isArray(flight.available_seat_classes)) {
    const sc = flight.available_seat_classes.find(s => 
      s.name.toLowerCase() === className.toLowerCase() || 
      normalizeClassKey(s.name, flight.airline_code) === normalizeClassKey(className, flight.airline_code)
    );
    if (sc && sc.price_multiplier) {
      price = Math.round(basePrice * Number(sc.price_multiplier));
      // If we found a direct match with a multiplier, we can skip the next steps
    }
  }

  // 2. Second priority: ML predicted seat class prices (if not already set)
  if (price === 0) {
    if (flight && flight.seat_class_prices && flight.seat_class_prices[className.toLowerCase()]) {
      price = flight.seat_class_prices[className.toLowerCase()];
    } else {
      // 3. Fallback: Hardcoded multipliers
      const priceMultipliers = {
        'economy': 1.0,
        'business': 1.8,
        'first': 2.5,
        'premium_economy': 1.4,
        'comfort_class': 1.2,
        'first_class': 2.5,
        'business_class': 1.8,
      };
      
      const key = normalizeClassKey(className, flight?.airline_code);
      const multiplier = priceMultipliers[key] || 1.0;
      price = Math.round(basePrice * multiplier);
    }
  }

  // Add Fare Family markup
  let markup = 0;
  const key = normalizeClassKey(className, flight?.airline_code);
  
  // NEW: Dynamic DB markup overrides hardcoded fallback
  if (fareBundlesData.value && fareBundlesData.value[key]) {
    const bundle = fareBundlesData.value[key].find(b => (b.type_code || b.code) === fareFamily);
    if (bundle && bundle.markup_fee !== undefined) {
      markup = Number(bundle.markup_fee);
    } else {
      markup = BUNDLE_MARKUPS[fareFamily] || 0;
    }
  } else {
    markup = BUNDLE_MARKUPS[fareFamily] || 0;
  }

  price += markup;

  // NEW: Trip Type Pricing Logic - 10% discount for Round-Trip on budget carriers
  if (isRoundTrip.value && (flight?.airline_code === '5J' || flight?.airline_code === 'Z2')) {
    price = Math.round(price * 0.9);
  }

  return price;
};

// Helper to normalize seat class names into standardized keys
const normalizeClassKey = (name, airlineCode = null) => {
  if (!name) return 'unknown';
  let key = name.toLowerCase().replace(' ', '_');
  
  // Standard CABIN class normalization
  if (key.includes('economy') && !key.includes('premium')) return 'economy';
  // Standardize Business Class (including PAL's Mabuhay Class)
  if (key.includes('business') || key.includes('mabuhay')) return 'business';
  if (key.includes('first') && !key.includes('class')) return 'first';
  
  // BRANDED Cabin Normalization: 
  // ONLY use comfort_class if explicitly named 'comfort' or 'comfort_class'
  if (key.includes('comfort')) {
    return 'comfort_class';
  }
  
  // Standard Premium Economy
  if (key.includes('premium') && key.includes('economy')) return 'premium_economy';
  
  // Any other "Premium" class should have its own unique key to avoid de-duplication merging
  if (key.includes('premium')) return key;
  
  return key;
};

// =================================================

// Update seat class filter options dynamically
const updateSeatClassFilterOptions = () => {
  // Start with default "All Classes" option
  const seatClassOptions = [{ value: 'all', label: 'All Classes' }];
  
  // Collect all unique classes from the actual flight results
  const classesInResults = new Set();
  flights.value.forEach(f => {
    // Collect from all possible sources
    const classes = [
      ...(f.available_seat_classes || []).map(sc => sc.name),
      ...(f.available_classes || []),
      ...(f.seat_classes || []).map(sc => typeof sc === 'string' ? sc : (sc.name || sc.class_name || sc.value))
    ];

    classes.forEach(name => {
      if (!name) return;
      const key = normalizeClassKey(name, f.airline_code);
      classesInResults.add(key);
    });
  });

  // Always at least include what's in the results
  if (classesInResults.size > 0) {
    // Sort keys to maintain consistent order (Economy, Comfort, Business)
    const orderPriority = ['economy', 'premium_economy', 'comfort_class', 'business', 'first'];
    const sortedKeys = Array.from(classesInResults).sort((a, b) => {
      const posA = orderPriority.indexOf(a) !== -1 ? orderPriority.indexOf(a) : 99;
      const posB = orderPriority.indexOf(b) !== -1 ? orderPriority.indexOf(b) : 99;
      return posA - posB;
    });

    sortedKeys.forEach(key => {
      const label = key === 'economy' ? 'Economy' : 
                    key === 'business' ? 'Business' : 
                    key === 'comfort_class' ? 'Comfort Class' : 
                    key === 'premium_economy' ? 'Premium Economy' : 
                    key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
      
      seatClassOptions.push({ value: key, label });
    });
  } else {
    // Fallback if no flights or results yet
    seatClassOptions.push(
      { value: 'economy', label: 'Economy' },
      { value: 'comfort_class', label: 'Comfort Class' },
      { value: 'business', label: 'Business' }
    );
  }
  
  filterOptions.value.seatClasses = seatClassOptions;
};

// Define the prop value used by the sidebar component
const availableSeatClassOptions = computed(() => filterOptions.value.seatClasses);

// Use trip type from Pinia store
const tripType = computed(() => bookingStore.tripType || route.query.tripType);
const isRoundTrip = computed(() => tripType.value === 'round_trip' || tripType.value === 'round-trip');
const isMultiCity = computed(() => tripType.value === 'multi_city' || tripType.value === 'multi-city');

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
  return phaseRouteInfo.value.date;
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
    tripType: (route.query.tripType === 'round_trip' || route.query.tripType === 'round-trip') ? 'round-trip' : 
              (route.query.tripType === 'multi-city' ? 'multi-city' : 'one-way'),
    legs: []
  };

  if (editSearchForm.value.tripType === 'multi-city' && route.query.segments) {
    try {
      const segments = JSON.parse(route.query.segments);
      editSearchForm.value.legs = segments.map(s => ({
        fromSearch: `${s.origin}`,
        toSearch: `${s.destination}`,
        selectedFrom: { code: s.origin },
        selectedTo: { code: s.destination },
        date: s.date,
        fromResults: [],
        toResults: []
      }));
    } catch (e) {
      console.error('Failed to parse segments for edit:', e);
    }
  } else if (editSearchForm.value.tripType === 'multi-city') {
    // Fallback if multi-city but no segments
    editSearchForm.value.legs = [
      { fromSearch: '', toSearch: '', selectedFrom: null, selectedTo: null, date: todayDateString.value, fromResults: [], toResults: [] },
      { fromSearch: '', toSearch: '', selectedFrom: null, selectedTo: null, date: todayDateString.value, fromResults: [], toResults: [] }
    ];
  }
  
  // Set initial search strings for autocomplete
  fromSearchInput.value = route.query.origin || '';
  toSearchInput.value = route.query.destination || '';
  
  // Attempt to load full airport names if possible, but fallback to code
  selectedFromAirport.value = { code: route.query.origin };
  selectedToAirport.value = { code: route.query.destination };
  
  showEditSearch.value = true;
};

// Search airports for autocomplete
const searchEditAirports = async (query, target, index = null) => {
  if (query.includes(' - ')) return;

  const searchQuery = query.toUpperCase().trim();
  if (searchQuery.length < 3) {
    if (index !== null) {
      editSearchForm.value.legs[index][target === 'from' ? 'fromResults' : 'toResults'] = [];
    } else {
      if (target === 'from') fromResults.value = [];
      else toResults.value = [];
    }
    return;
  }

  try {
    const response = await airportService.searchAirports(searchQuery);
    const airports = response.data.results || response.data;
    
    // Filter out opposite selected airport
    let oppositeCode = null;
    if (index !== null) {
      const leg = editSearchForm.value.legs[index];
      oppositeCode = target === 'from' ? leg.selectedTo?.code : leg.selectedFrom?.code;
    } else {
      oppositeCode = target === 'from' ? selectedToAirport.value?.code : selectedFromAirport.value?.code;
    }
    const filtered = airports.filter(a => a.code !== oppositeCode);

    if (index !== null) {
      editSearchForm.value.legs[index][target === 'from' ? 'fromResults' : 'toResults'] = filtered;
    } else {
      if (target === 'from') fromResults.value = filtered;
      else toResults.value = filtered;
    }
  } catch (error) {
    console.error("Airport search error:", error);
  }
};

// Select airport from results
const selectEditAirport = (airport, target, index = null) => {
  const displayString = `${airport.code} - ${airport.city}`;

  if (index !== null) {
    const leg = editSearchForm.value.legs[index];
    if (target === 'from') {
      leg.selectedFrom = airport;
      leg.fromSearch = displayString;
      leg.fromResults = [];
    } else {
      leg.selectedTo = airport;
      leg.toSearch = displayString;
      leg.toResults = [];
      
      // Auto-fill next leg's 'from'
      if (index < editSearchForm.value.legs.length - 1) {
        const nextLeg = editSearchForm.value.legs[index + 1];
        if (!nextLeg.selectedFrom) {
          nextLeg.selectedFrom = airport;
          nextLeg.fromSearch = displayString;
        }
      }
    }
  } else {
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
  }
};

const handleEditEnterKey = (query, target, index = null) => {
  if (!query || query.includes(' - ')) return;
  
  const results = index !== null 
    ? editSearchForm.value.legs[index][target === 'from' ? 'fromResults' : 'toResults']
    : (target === 'from' ? fromResults.value : toResults.value);

  if (results && results.length > 0) {
    const searchQuery = query.toUpperCase().trim();
    // Prioritize exact code match, then exact city match, then first result
    const match = results.find(a => a.code === searchQuery) || 
                  results.find(a => a.city.toUpperCase() === searchQuery) || 
                  results[0];
    if (match) {
      selectEditAirport(match, target, index);
    }
  }
};

// Submit edited search
const submitEditedSearch = () => {
  const isMulti = editSearchForm.value.tripType === 'multi-city';
  
  const searchParams = {
    tripType: editSearchForm.value.tripType,
    adults: editSearchForm.value.adults.toString(),
    children: editSearchForm.value.children.toString(),
    infants: editSearchForm.value.infants.toString()
  };

  if (isMulti) {
    // Validate segments
    for (let i = 0; i < editSearchForm.value.legs.length; i++) {
      const leg = editSearchForm.value.legs[i];
      if (!leg.selectedFrom || !leg.selectedTo) {
        notificationStore.warn(`Please select both Origin and Destination for Flight ${i + 1}.`);
        return;
      }
    }
    
    searchParams.segments = JSON.stringify(editSearchForm.value.legs.map(l => ({
      origin: l.selectedFrom.code,
      destination: l.selectedTo.code,
      date: l.date
    })));
  } else {
    searchParams.origin = editSearchForm.value.origin;
    searchParams.destination = editSearchForm.value.destination;
    searchParams.departure = editSearchForm.value.departure;
    searchParams.returnDate = editSearchForm.value.returnDate;
  }
  
  // Update store
  bookingStore.setTripType(editSearchForm.value.tripType);
  bookingStore.setPassengerCount({
    adults: parseInt(editSearchForm.value.adults) || 1,
    children: parseInt(editSearchForm.value.children) || 0,
    infants: parseInt(editSearchForm.value.infants) || 0
  });
  
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
  
  // fetchFlights() call removed - now handled by route watcher
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

// Handle showing seat classes for a flight inline
const showSeatClasses = (flight) => {
  // NEW: Minimum Connecting Time (MCT) Validation for Multi-City
  if (bookingStore.isMultiCity) {
    const validation = bookingStore.validateMultiCityConnection(
      bookingStore.currentSegmentIndex, 
      flight
    );
    
    if (!validation.valid) {
      console.warn('❌ MCT Validation Failed:', validation.message);
      notificationStore.showNotification(
        validation.message,
        'error',
        5000
      );
      return; // Stop the process, don't show the modal
    }
  }

  // Close any previously expanded flights
  flights.value.forEach(f => {
    if (f.id !== flight.id) {
      f.showInlineClasses = false;
    }
  });

  // Toggle inline classes for the clicked flight
  flight.showInlineClasses = !flight.showInlineClasses;
  selectedFlightForSeats.value = flight;
};

// Extract seat classes from flight data
// 2026 Philippine Airline Fare Families Mapping
const AIRLINE_FARE_FAMILIES = {
  'PR': { // Philippine Airlines (2024 Domestic Fare Families)
    'economy': [
      { 
        name: 'Super Saver', 
        code: 'super_saver', 
        features: [
          '7kg Carry-on baggage only', 
          'No checked baggage included', 
          '10% Mabuhay Miles', 
          'Rebooking: ₱2,500 + fare diff', 
          'Non-refundable'
        ] 
      },
      { 
        name: 'Saver', 
        code: 'saver', 
        features: [
          '10kg Checked baggage included', 
          '7kg Carry-on baggage', 
          '50% Mabuhay Miles', 
          'Rebooking: ₱2,000 + fare diff', 
          'Refundable (₱2,500 fee)'
        ] 
      },
      { 
        name: 'Value', 
        code: 'value', 
        features: [
          '20kg Checked baggage included', 
          '7kg Carry-on baggage', 
          '75% Mabuhay Miles', 
          'Rebooking: ₱1,500 + fare diff', 
          'Refundable (₱2,000 fee)'
        ] 
      },
      { 
        name: 'Flex', 
        code: 'flex', 
        features: [
          '20kg Checked baggage included', 
          '7kg Carry-on baggage', 
          '100% Mabuhay Miles', 
          'FREE Rebooking (+ fare diff)', 
          'FREE Refund'
        ] 
      }
    ],
    'comfort_class': [
      { 
        name: 'Comfort', 
        code: 'comfort', 
        features: [
          '25kg Checked baggage included', 
          '115% Mabuhay Miles', 
          'Front cabin / Extra legroom', 
          'Priority check-in & boarding', 
          'FREE Rebooking (+ fare diff)', 
          'Refundable (₱1,000 fee)'
        ] 
      }
    ],
    'business': [
      { 
        name: 'Business Value', 
        code: 'business_value', 
        features: [
          '30kg Checked baggage included', 
          '125% Mabuhay Miles', 
          'Mabuhay Lounge access', 
          'Rebooking: ₱500 + fare diff', 
          'Refundable (₱1,200 fee)'
        ] 
      },
      { 
        name: 'Business Flex', 
        code: 'business_flex', 
        features: [
          '35kg Checked baggage included', 
          '150% Mabuhay Miles', 
          'Mabuhay Lounge access', 
          'FREE Rebooking (+ fare diff)', 
          'FREE Refund'
        ] 
      }
    ]
  },
  '5J': { // Cebu Pacific (GO Tiers)
    'economy': [
      { 
        name: 'Go Basic', 
        code: 'basic', 
        description: 'Best for light travelers',
        features: [
          '7kg Hand-carry (1 piece)', 
          'No checked baggage included', 
          'Seat Selection: Extra Fee', 
          'Flexibility: Change fees apply',
          'Non-refundable'
        ] 
      },
      { 
        name: 'Go Easy', 
        code: 'standard', 
        description: 'Essential for typical trips',
        features: [
          '7kg Hand-carry (1 piece)', 
          '20kg Checked baggage (1 piece)', 
          'Standard Seat included', 
          'Flexibility: Change fees apply',
          'Non-refundable'
        ] 
      },
      { 
        name: 'Go Flexi', 
        code: 'flex', 
        description: 'Maximum peace of mind',
        features: [
          '7kg Hand-carry (1 piece)', 
          '20kg Checked baggage (1 piece)', 
          'Standard Seat included', 
          'NO CHANGE FEES*', 
          'Refundable to Travel Fund'
        ] 
      }
    ]
  },
  'Z2': { // AirAsia Philippines (Weight Concept)
    'economy': [
      { 
        name: 'Low Fare', 
        code: 'basic', 
        description: 'Lowest price for minimal travel needs',
        features: [
          '7kg Hand-carry only', 
          'No checked baggage', 
          'Standard seats at extra fee',
          'Non-refundable'
        ] 
      },
      { 
        name: 'Value Pack', 
        code: 'standard', 
        description: 'Essential value with baggage and meal',
        features: [
          '7kg Hand-carry (1 piece)', 
          '20kg Checked Baggage (Weight Concept)', 
          'Standard Seat Selection', 
          '1 Complimentary Meal',
          'Non-refundable'
        ] 
      },
      { 
        name: 'Premium Flex', 
        code: 'flex', 
        description: 'Total flexibility and better service',
        features: [
          '7kg Hand-carry (1 piece)', 
          '20kg Checked Baggage (Weight Concept)', 
          'Premium Seat Selection', 
          'Xpress Boarding & Baggage',
          'UNLIMITED FLIGHT CHANGES*',
          'Subject to AirAsia Refund Policy'
        ] 
      }
    ]
  },
  'T6': { // AirSwift
    'economy': [
      { name: 'Promo/Basic', code: 'basic', features: ['7kg Hand-carry', 'Strict rebooking'] },
      { name: 'Value', code: 'standard', features: ['7kg Hand-carry', '10kg Checked Baggage'] },
      { name: 'Premium', code: 'premium', features: ['7kg Hand-carry', '20kg Checked Baggage', 'Free rebooking (fees apply)'] }
    ]
  }
};

const extractSeatClassesFromFlight = (flight) => {
  if (!flight) return [];
  
  // Deriving the airline primarily from the flight number prefix to ensure accuracy
  const flightNumber = flight.flight_number || '';
  const prefix2 = flightNumber.substring(0, 2).toUpperCase();
  const prefix3 = flightNumber.substring(0, 3).toUpperCase();
  const airlineName = (flight.airline_name || '').toLowerCase();
  
  let airline = 'Other';
  if (prefix2 === 'PR' || prefix3 === 'PAL' || airlineName.includes('philippine airlines') || airlineName.includes('pal')) {
    airline = 'PR';
  } else if (prefix2 === '5J' || prefix3 === 'CEB' || prefix2 === 'DG' || airlineName.includes('cebu pacific')) {
    airline = '5J';
  } else if (prefix2 === 'Z2' || airlineName.includes('airasia')) {
    airline = 'Z2';
  } else if (prefix2 === 'T6' || airlineName.includes('airswift')) {
    airline = 'T6';
  } else {
    airline = flight.airline_code || 'Other';
  }
                  
  const isPALDomestic = (airline === 'PR') && (flight.trip_category === 'domestic' || flight.is_domestic);
  
  let rawSeatClasses = [];
  
  // Extract raw seat classes based on available structures
  if (Array.isArray(flight.available_seat_classes) && flight.available_seat_classes.length > 0) {
    rawSeatClasses = flight.available_seat_classes.map(sc => ({
      name: sc.name,
      price_multiplier: sc.price_multiplier,
      id: sc.class_id
    }));
  } else if (Array.isArray(flight.available_classes) && flight.available_classes.length > 0) {
    rawSeatClasses = flight.available_classes.map(name => ({ name }));
  } else if (Array.isArray(flight.seat_classes) && flight.seat_classes.length > 0) {
    rawSeatClasses = flight.seat_classes.map(sc => typeof sc === 'string' ? { name: sc } : sc);
  } else if (Object.keys(seatClassFeatures.value).length > 0) {
    rawSeatClasses = Object.keys(seatClassFeatures.value).map(name => ({ name }));
  } else {
    rawSeatClasses = [{ name: 'Economy' }, { name: 'Business' }];
  }

  const finalClasses = [];
  const seenClassKeys = new Set();
  rawSeatClasses.forEach(sc => {
    let className = sc.name || sc.class_name || sc.value || 'Unknown';
    
    // No transformation here anymore, we use the original className from rawSeatClasses
    
    let classKey = normalizeClassKey(className, airline);
    
    // DE-DUPLICATION: Only process EACH classKey once!
    if (seenClassKeys.has(classKey)) return;
    seenClassKeys.add(classKey);

    // Standardize display name for the tab based on branding ONLY if it's standard.
    // If it's a specific custom class (like 'premium_class' vs 'premium_economy'), keep it!
    let displayClassName = className;
    if (classKey === 'economy') displayClassName = 'Economy';
    else if (classKey === 'business') displayClassName = 'Business';
    else if (classKey === 'comfort_class') displayClassName = 'Comfort Class';
    else if (classKey === 'premium_economy') displayClassName = 'Premium Economy';
    else if (classKey === 'first') displayClassName = 'First Class';
    // If airline is PR and it's domestic AND classKey is comfort_class, ensure Comfort Class name
    if (isPALDomestic && classKey === 'comfort_class') displayClassName = 'Comfort Class';
    // If it's the premium_class key specifically, keep it as Premium Class
    if (classKey.includes('premium')) displayClassName = className;

    // LCCs like Cebu Pacific (5J) and AirAsia (Z2) only operate Economy cabins
    const isStrictLCC = ['5J', 'Z2'].includes(airline);
    if (isStrictLCC && classKey !== 'economy') {
      return; 
    }

    // 1. Check specialized carrier families first (branded dynamic)
    const specializedFamilies = AIRLINE_FARE_FAMILIES[airline]?.[classKey];
    
    // 2. Check API-provided bundles (fully dynamic from DB)
    const dbBundles = fareBundlesData.value[classKey];

    // Priority: DB Bundles first (CRUD dynamic), then specialized mappings fallback
    const familiesToUse = (dbBundles && dbBundles.length > 0) ? dbBundles : specializedFamilies;

    if (familiesToUse && familiesToUse.length > 0) {
      familiesToUse.forEach(bundle => {
        finalClasses.push({
          travel_class: displayClassName,
          name: bundle.name,
          fare_family: bundle.name.toLowerCase().includes('flex') ? 'flex' : (bundle.code || bundle.type_code || 'standard'),
          description: bundle.description || getSeatClassDescription(displayClassName),
          price: calculateSeatClassPrice(flight.price, displayClassName, flight, bundle.code || bundle.type_code || 'standard'),
          icon: bundle.icon_svg || getSeatClassIcon(displayClassName),
          features: Array.isArray(bundle.features) ? bundle.features : [],
          ml_predicted: flight.ml_predicted
        });
      });
    } else {
      // Fallback: Default bundles for Economy if no specialized or DB rules exist
      if (classKey.includes('economy')) {
        const defaultBundles = [
          { name: 'Saver', code: 'basic', features: ['Hand-carry only'] },
          { name: 'Standard', code: 'standard', features: ['Hand-carry', '20kg Checked Bag'] },
          { name: 'Flex', code: 'flex', features: ['Hand-carry', '30kg Checked Bag', 'Free Rebook'] }
        ];
        
        defaultBundles.forEach(bundle => {
          finalClasses.push({
            travel_class: className,
            name: `${className} ${bundle.name}`,
            fare_family: bundle.code,
            description: getSeatClassDescription(className),
            price: calculateSeatClassPrice(flight.price, className, flight, bundle.code),
            icon: getSeatClassIcon(className),
            features: bundle.features,
            ml_predicted: flight.ml_predicted
          });
        });
      } else {
        // Standard non-economy class
        finalClasses.push({
          travel_class: className,
          name: className,
          fare_family: 'premium',
          description: sc.description || getSeatClassDescription(className),
          price: sc.price || calculateSeatClassPrice(flight.price, className, flight, 'premium'),
          icon: getSeatClassIcon(className),
          features: sc.features || getSeatClassFeatures(className),
          ml_predicted: sc.ml_predicted || flight.ml_predicted
        });
      }
    }
  });

  // SORTING ENGINE: Business > Premium/Comfort > Economy
  const CLASS_RANK = {
    'business': 100,
    'comfort': 80,
    'premium': 70,
    'economy': 50
  };

  return finalClasses.sort((a, b) => {
    const aKey = a.travel_class.toLowerCase();
    const bKey = b.travel_class.toLowerCase();
    
    let aRank = 0;
    Object.keys(CLASS_RANK).forEach(k => { if (aKey.includes(k)) aRank = Math.max(aRank, CLASS_RANK[k]); });
    
    let bRank = 0;
    Object.keys(CLASS_RANK).forEach(k => { if (bKey.includes(k)) bRank = Math.max(bRank, CLASS_RANK[k]); });

    // Primary sort by rank (descending), secondary by price (ascending)
    if (bRank !== aRank) return bRank - aRank;
    return a.price - b.price;
  });
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
    'comfort': 'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-7.714 2.143L11 21l-2.286-6.857L1 12l7.714-2.143L11 3z', // Star/Comfort icon
    'premium': 'M5 13l4 4L19 7M12 19l9 2-9-18-9 18 9-2zm0 0v-8', // Up/Premium icon
    'business': 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    'first': 'M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7'
  };
  
  const lowName = className.toLowerCase();
  if (lowName.includes('comfort')) return icons.comfort;
  if (lowName.includes('premium')) return icons.premium;
  if (lowName.includes('business')) return icons.business;
  if (lowName.includes('first')) return icons.first;
  return icons.economy;
};

// Helper function to get seat class color
const getClassColor = (name) => {
  if (!name) return '#003870';
  const n = name.toLowerCase();
  if (n.includes('business')) return '#7c3aed'; // Purple
  if (n.includes('premium') || n.includes('comfort')) return '#f59e0b'; // Amber/Gold
  return '#003870'; // PAL Blue / Default
};

// Helper function to get seat class features (Dynamically from API or fallback)
const getSeatClassFeatures = (className) => {
  if (!className) return [];
  
  const key = className.toLowerCase().replace(' ', '_');
  
  // Try to get from API data first
  if (seatClassFeatures.value[key] && seatClassFeatures.value[key].length > 0) {
    return parseFeatures(seatClassFeatures.value[key]);
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

// Handle seat class selection from inline FlightCard
const handleInlineSeatClassSelection = ({ flight, seatClass }) => {
  console.log('✅ Selected seat class inline:', seatClass.name, 'Travel Class:', seatClass.travel_class);
  
  // Construct the full class name (e.g., "Economy Saver" or "Business Flex")
  // Avoid duplication if the seat class name already includes the travel class
  const travelClass = seatClass.travel_class || 'Economy';
  const name = seatClass.name || '';
  const fullClassName = name.toLowerCase().includes(travelClass.toLowerCase()) 
    ? name 
    : `${travelClass} ${name}`;
  
  // Create a flight object with seat class info
  const flightWithSeatClass = {
    ...flight,
    price: seatClass.price,
    original_price: flight.original_price || flight.price,
    base_price: flight.base_price || flight.price,
    travel_class: travelClass,           // 'Economy', 'Business', etc.
    seat_class: seatClass.name,
    selected_seat_class: seatClass.name,
    fare_family: seatClass.fare_family || 'basic',
    fare_family_name: seatClass.name,           // Branded bundle name e.g. 'GO Basic', 'Value Pack'
    class_type: fullClassName, // Set the specific bundle as the class type for the backend
    seat_class_details: seatClass,
    seat_class_features: seatClass.features,
    ml_predicted: seatClass.ml_predicted || flight.ml_predicted
  };
  
  // Close inline expansion
  flight.showInlineClasses = false;
  selectedFlightForSeats.value = null;
  
  // Show confirmation modal
  selectedFlight.value = flightWithSeatClass;
  showConfirmation.value = true;
};

// Cancel seat class selection (legacy modal)
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
  
  if (route.query.adults !== undefined) {
    bookingStore.setPassengerCount({
      adults: parseInt(route.query.adults) || 1,
      children: parseInt(route.query.children) || 0,
      infants: parseInt(route.query.infants) || 0
    });
  }
  
  console.log('Trip Type from Store:', bookingStore.tripType);
  console.log('Trip Type from Route:', route.query.tripType);
  console.log('Is Round Trip:', isRoundTrip.value);
  console.log('Has Outbound Selected:', hasOutboundSelected.value);
  console.log('Has Return Selected:', hasReturnSelected.value);
  
  // Set stop preference if requested from home
  if (bookingStore.stopPreference !== 'all') {
    console.log('🛑 Stop preference active:', bookingStore.stopPreference);
    filters.value.stops = bookingStore.stopPreference;
  } else if (route.query.stops) {
    filters.value.stops = route.query.stops;
  }
  
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
  // NEW: Watch for route query changes to refresh search
  watch(() => route.query, () => {
    console.log('🔄 Route query changed, refreshing results...');
    // Reset date filters so fetchFlights pick up the new route date
    dateFilter.value.selectedDate = null;
    dateSelector.value.currentWeekStart = null;
    fetchFlights();
  }, { deep: true });

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
const prevWeek = async () => {
  // 1. Calculate the new selected date (7 days back)
  // Use current selection as anchor, or fallback to current week start
  const anchorDate = dateFilter.value.selectedDate ? parseISO(dateFilter.value.selectedDate) : (dateSelector.value.currentWeekStart || new Date());
  const newDate = subDays(anchorDate, 7);
  const newDateString = format(newDate, 'yyyy-MM-dd');
  
  // 2. Update navigation state
  dateSelector.value.currentWeekStart = subDays(dateSelector.value.currentWeekStart || startOfWeek(anchorDate, { weekStartsOn: 0 }), 7);
  
  // 3. Update the filter state to the new date
  dateFilter.value.selectedDate = newDateString;
  dateSelector.value.selectedDay = newDateString;
  dateFilter.value.dateRange = 'exact';
  
  updateWeekDays();
  await fetchFlights(); // Wait for data to load
  applyFilters();      // Now apply filters to the new data
};

// Navigate to next week
const nextWeek = async () => {
  // 1. Calculate the new selected date (7 days ahead)
  const anchorDate = dateFilter.value.selectedDate ? parseISO(dateFilter.value.selectedDate) : (dateSelector.value.currentWeekStart || new Date());
  const newDate = addDays(anchorDate, 7);
  const newDateString = format(newDate, 'yyyy-MM-dd');
  
  // 2. Update navigation state
  dateSelector.value.currentWeekStart = addDays(dateSelector.value.currentWeekStart || startOfWeek(anchorDate, { weekStartsOn: 0 }), 7);
  
  // 3. Update the filter state to the new date
  dateFilter.value.selectedDate = newDateString;
  dateSelector.value.selectedDay = newDateString;
  dateFilter.value.dateRange = 'exact';
  
  updateWeekDays();
  await fetchFlights(); // Wait for data to load
  applyFilters();      // Now apply filters to the new data
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
    const targetClass = filters.value.seatClass.toLowerCase();
    result = result.filter(f => {
      const flightClasses = f.available_classes || f.seat_classes || [];
      return flightClasses.some(sc => {
        const name = typeof sc === 'string' ? sc : (sc.name || sc.class_name || sc.value || '');
        const key = normalizeClassKey(name, f.airline_code);
        return key === targetClass;
      });
    });
  }
  
  // Stops filter
  if (filters.value.stops !== 'all') {
    if (filters.value.stops === 'nonstop' || filters.value.stops === 'direct') {
      result = result.filter(f => (f.total_stops || 0) === 0);
    } else if (filters.value.stops === '1-stop') {
      result = result.filter(f => (f.total_stops || 0) === 1);
    } else if (filters.value.stops === '2-stop') {
      result = result.filter(f => (f.total_stops || 0) === 2);
    } else if (filters.value.stops === 'connecting') {
      result = result.filter(f => (f.total_stops || 0) > 0);
    }
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
      case 'best':
        // Sort by "Best" algorithm: 60% weight to price, 40% weight to duration
        const maxPrice = Math.max(...flights.value.map(f => f.price)) || 1;
        const maxDuration = Math.max(...flights.value.map(f => f.duration_minutes || 1000)) || 1;
        const scoreA = (a.price / maxPrice) * 0.6 + ((a.duration_minutes || 0) / maxDuration) * 0.4;
        const scoreB = (b.price / maxPrice) * 0.6 + ((b.duration_minutes || 0) / maxDuration) * 0.4;
        return scoreA - scoreB;
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
    stops: 'all',
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
  const airlinesMap = new Map();
  flightsList.forEach(flight => {
    if (flight.airline_code && flight.airline_name && !airlinesMap.has(flight.airline_code)) {
      airlinesMap.set(flight.airline_code, {
        code: flight.airline_code,
        name: flight.airline_name
      });
    }
  });
  return Array.from(airlinesMap.values());
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
  
  // Navigate to passenger details with a loading transition
  isProceedingToCheckout.value = true;
  setTimeout(() => {
    isProceedingToCheckout.value = false;
    router.push({ name: 'PassengerDetails' });
  }, 2000);
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
    Object.assign(flight, enhancedFlight);
  }
  // =====================================================
  
  // Store the flight for seat class selection
  selectedFlightForSeats.value = flight;
  
  // Show seat classes inline for selection or modification
  showSeatClasses(flight);
};

// Confirm selection
const confirmSelection = () => {
  if (!selectedFlight.value) return;
  
  // Refresh session
  bookingStore.startSession();
  
  // Log complete booking details
  logCompleteBookingDetails();
  
  if (isMultiCity.value) {
    console.log(`✅ CONFIRMING FLIGHT FOR SEGMENT ${currentSegmentIndex.value + 1}`);
    
    // Save to store
    bookingStore.selectSegmentFlight(currentSegmentIndex.value, selectedFlight.value);
    
    if (currentSegmentIndex.value < multiCitySegments.value.length - 1) {
      console.log('🔄 Moving to next segment search...');
      currentSegmentIndex.value++;
      
      // Close confirmation modal
      showConfirmation.value = false;
      selectedFlight.value = null;
      
      // Reset week start for next leg
      dateSelector.value.currentWeekStart = null;
      
      // Fetch flights for next segment
      fetchFlights();
      window.scrollTo(0, 0);
    } else {
      console.log('🏁 All multi-city segments selected, proceeding...');
      isProceedingToCheckout.value = true;
      showConfirmation.value = false;
      setTimeout(() => {
        isProceedingToCheckout.value = false;
        router.push({ name: 'PassengerDetails' });
      }, 2000);
    }
  } else if (isRoundTrip.value) {
    if (selectionPhase.value === 'outbound') {
      console.log('✅ CONFIRMING OUTBOUND FLIGHT FOR ROUND-TRIP');
      
      // Save flight to store
      bookingStore.selectFlight(selectedFlight.value, 'outbound');
      
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
      
      // Save flight to store
      bookingStore.selectFlight(selectedFlight.value, 'return');
      
      // Log return flight selection
      logFlightSelection(selectedFlight.value, 'return');
      
      // Log complete booking
      logCompleteBooking();
      
      // Navigate to passenger details
      isProceedingToCheckout.value = true;
      showConfirmation.value = false;
      setTimeout(() => {
        isProceedingToCheckout.value = false;
        router.push({ name: 'PassengerDetails' });
      }, 2000);
    }
  } else {
    console.log('✅ CONFIRMING ONE-WAY BOOKING');
    
    // Save flight to store
    bookingStore.selectFlight(selectedFlight.value, 'outbound');
    
    logFlightSelection(selectedFlight.value, 'outbound');
    
    isProceedingToCheckout.value = true;
    showConfirmation.value = false;
    setTimeout(() => {
      isProceedingToCheckout.value = false;
      router.push({ name: 'PassengerDetails' });
    }, 2000);
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
    const searchDateStr = phaseRouteInfo.value.date;
    const searchDate = new Date(searchDateStr);
    
    // This allows re-fetching when navigating via prev/next week
    const rangeAnchorDate = dateSelector.value.currentWeekStart || startOfWeek(searchDate, { weekStartsOn: 0 });
    
    const startDate = format(rangeAnchorDate, 'yyyy-MM-dd');
    const endDate = format(addDays(rangeAnchorDate, 6), 'yyyy-MM-dd'); // Fetch full 7 days of the current view
    
    const params = {
      origin: phaseRouteInfo.value.origin,
      destination: phaseRouteInfo.value.destination,
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
    
    // Filter out flights that have already departed
    const now = new Date();
    fetchedFlights = fetchedFlights.filter(f => {
      if (!f.departure_time) return false;
      return new Date(f.departure_time) >= now;
    });
    
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
    
    // Only reset to current search date if no date is currently selected (e.g. initial load or new search)
    if (!dateFilter.value.selectedDate) {
      dateFilter.value.selectedDate = currentSearchDate.value;
    }
    
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

// Helper to safely parse features (in case they are JSON strings)
const parseFeatures = (features) => {
  if (!features) return [];
  if (Array.isArray(features)) {
    return features.map(f => {
      if (typeof f === 'string' && (f.startsWith('[') || f.startsWith('{'))) {
        try {
          return JSON.parse(f);
        } catch (e) {
          return f;
        }
      }
      return f;
    }).flat(); // Flatten in case a single feature string represents an array of features
  }
  return [];
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
  
  const processFlight = (flight, typeLabel) => {
    return {
      type: typeLabel,
      flight: flight.flight_number,
      airline: flight.airline_name,
      origin: flight.origin,
      origin_city: flight.origin_city,
      destination: flight.destination,
      destination_city: flight.destination_city,
      route: `${flight.origin} → ${flight.destination}`,
      time: formatTime(flight.departure_time),
      arrivalTime: formatTime(flight.arrival_time),
      date: formatDate(flight.departure_time),
      arrivalDate: formatDate(flight.arrival_time),
      duration: flight.flight_duration,
      aircraft: flight.aircraft_name || 'Commercial Aircraft',
      stops: flight.total_stops || 0,
      layovers: flight.layovers_data && flight.layovers_data.length > 0 
        ? flight.layovers_data 
        : (flight.total_stops > 0 ? Array.from({ length: flight.total_stops }, (_, i) => ({
            airport: ['HKG', 'SIN', 'BKK', 'ICN', 'NRT'][i % 5],
            city: ['Hong Kong', 'Singapore', 'Bangkok', 'Seoul', 'Tokyo'][i % 5],
            duration: '1h 30m'
          })) : []),
      price: Number(flight.price).toLocaleString(),
      selected_seat_class: flight.selected_seat_class || flight.seat_class,
      seat_class_price: flight.price,
      base_price: flight.original_price || flight.base_price || flight.price,
      ml_predicted: flight.ml_predicted
    };
  };

  if (isMultiCity.value) {
    bookingStore.multiCitySegments.forEach((seg, idx) => {
      if (seg.selectedFlight) {
        summary.push(processFlight(seg.selectedFlight, `Flight ${idx + 1}`));
      }
    });
    return summary;
  }

  if (bookingStore.selectedOutbound) {
    summary.push(processFlight(bookingStore.selectedOutbound, isRoundTrip.value ? 'Outbound' : 'Flight'));
  }
  
  if (bookingStore.selectedReturn) {
    summary.push(processFlight(bookingStore.selectedReturn, 'Return'));
  }
  
  return summary;
});

// Get total price
const totalPrice = computed(() => {
  return bookingStore.grandTotal;
});

// Get modal title based on trip type and phase
const modalTitle = computed(() => {
  if (isMultiCity.value) {
    return `Confirm Flight ${currentSegmentIndex.value + 1}`;
  }
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
  if (isMultiCity.value) {
    return currentSegmentIndex.value < multiCitySegments.value.length - 1 
      ? 'Confirm & Next Flight' 
      : 'Confirm & Continue';
  }
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
  if (isMultiCity.value) {
    return currentSegmentIndex.value < multiCitySegments.value.length - 1
      ? `After confirming, you will select Flight ${currentSegmentIndex.value + 2}.`
      : 'After confirming, click "Proceed to Passenger Details" to continue.';
  }
  if (isRoundTrip.value && selectionPhase.value === 'outbound') {
    return 'After confirming, click "Continue to Return Flight" to select your return flight.';
  } else if (isRoundTrip.value && selectionPhase.value === 'return') {
    return 'After confirming, click "Proceed to Passenger Details" to continue.';
  }
  return '';
});

// ============ PAGINATION LOGIC ============
const paginatedFlights = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredFlights.value.slice(start, end);
});

const totalPages = computed(() => {
  return Math.ceil(filteredFlights.value.length / itemsPerPage.value);
});

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }
};

// Reset to first page when filters or results change
watch(filteredFlights, () => {
  currentPage.value = 1;
});
// ==========================================

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
  if (isMultiCity.value && multiCitySegments.value[currentSegmentIndex.value]) {
    const seg = multiCitySegments.value[currentSegmentIndex.value];
    return {
      origin: seg.origin,
      destination: seg.destination,
      date: seg.date
    };
  }

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
  if (isMultiCity.value) {
    return `Select Flight ${currentSegmentIndex.value + 1}`;
  }
  if (isRoundTrip.value) {
    return selectionPhase.value === 'outbound' ? 'Select Outbound' : 'Select Return';
  }
  return 'Select Flight';
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
  appearance: none;
  margin: 0;
}

input[type="number"] {
  -webkit-appearance: textfield;
  -moz-appearance: textfield;
  appearance: textfield;
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
.flight-list-move,
.flight-list-enter-active,
.flight-list-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.flight-list-enter-from,
.flight-list-leave-to {
  opacity: 0;
  transform: translateY(15px);
}

.flight-list-leave-active {
  position: absolute;
}
</style>