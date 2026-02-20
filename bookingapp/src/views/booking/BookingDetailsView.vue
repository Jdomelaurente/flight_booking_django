<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <!-- Loading State -->
    <div v-if="loading" class="max-w-3xl mx-auto">
      <div class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600 mb-4"></div>
        <h2 class="text-xl font-semibold text-gray-700">Loading booking details...</h2>
        <p class="text-gray-500 mt-2">Please wait while we fetch your booking information.</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="max-w-3xl mx-auto">
      <div class="bg-white rounded-lg shadow-md p-6 text-center">
        <div class="text-red-500 text-5xl mb-4">❌</div>
        <h1 class="text-2xl font-bold text-gray-800 mb-2">Unable to Load Booking</h1>
        <p class="text-gray-600 mb-6">{{ error }}</p>
        <div class="flex flex-col sm:flex-row gap-3 justify-center">
          <button 
            @click="fetchBookingDetails"
            class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition duration-200"
          >
            Try Again
          </button>
          <button 
            @click="$router.push({ name: 'Home' })"
            class="bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-6 rounded-lg transition duration-200"
          >
            Return to Home
          </button>
        </div>
      </div>
    </div>

    <!-- Booking Details Content -->
    <div v-else-if="bookingData" class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Booking Details</h1>
            <p class="text-gray-600 mt-1">{{ formatDate(bookingData.created_at) }}</p>
          </div>
          <div class="text-right">
            <span class="text-sm text-gray-500">Reference:</span>
            <span class="ml-2 font-bold text-lg text-blue-600">{{ bookingData.booking_reference || `BK${bookingData.id.toString().padStart(8, '0')}` }}</span>
          </div>
        </div>
        
        <!-- Status Banner -->
        <div :class="statusClasses" class="rounded-lg p-4 mb-6">
          <div class="flex items-center">
            <span class="text-2xl mr-3">{{ statusIcon }}</span>
            <div>
              <h3 class="font-semibold text-lg">{{ bookingStatusText }}</h3>
              <p class="text-sm opacity-90">{{ bookingStatusMessage }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="mb-8">
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex space-x-8">
            <button
              @click="activeTab = 'overview'"
              :class="activeTab === 'overview' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
              class="py-2 px-1 border-b-2 font-medium text-sm transition duration-150"
            >
              Overview
            </button>
            <button
              @click="activeTab = 'flights'"
              :class="activeTab === 'flights' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
              class="py-2 px-1 border-b-2 font-medium text-sm transition duration-150"
            >
              Flights
            </button>
            <button
              @click="activeTab = 'passengers'"
              :class="activeTab === 'passengers' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
              class="py-2 px-1 border-b-2 font-medium text-sm transition duration-150"
            >
              Passengers
            </button>
            <button
              @click="activeTab = 'payment'"
              :class="activeTab === 'payment' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
              class="py-2 px-1 border-b-2 font-medium text-sm transition duration-150"
            >
              Payment
            </button>
          </nav>
        </div>
      </div>

      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="space-y-8">
        <!-- Flight Summary -->
        <div class="bg-white rounded-xl shadow-md p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-6 pb-4 border-b">Flight Summary</h2>
          <div v-if="groupedFlights.length > 0" class="space-y-6">
            <div v-for="(flightGroup, index) in groupedFlights" :key="index" class="border rounded-lg p-4">
              <div class="flex items-center justify-between mb-4">
                <div>
                  <h3 class="font-semibold text-gray-700">
                    {{ flightGroup.origin }} → {{ flightGroup.destination }}
                  </h3>
                  <p class="text-sm text-gray-500">{{ formatFlightDate(flightGroup.departure_time) }}</p>
                </div>
                <span class="bg-blue-100 text-blue-800 text-xs font-semibold px-3 py-1 rounded-full">
                  {{ flightGroup.airline_code }}
                </span>
              </div>
              
              <div class="flex items-center justify-between py-4">
                <div class="text-center flex-1">
                  <div class="text-2xl font-bold text-gray-800">{{ formatTime(flightGroup.departure_time) }}</div>
                  <div class="text-sm text-gray-600">{{ flightGroup.origin_code }}</div>
                  <div class="text-xs text-gray-500">{{ flightGroup.origin_city }}</div>
                </div>
                
                <div class="flex-1 px-4">
                  <div class="flex items-center justify-center">
                    <div class="flex-1 border-t-2 border-gray-300"></div>
                    <div class="mx-2">
                      <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                      </svg>
                    </div>
                    <div class="flex-1 border-t-2 border-gray-300"></div>
                  </div>
                  <div class="text-center mt-1">
                    <span class="text-xs text-gray-500">{{ flightGroup.duration }}</span>
                  </div>
                </div>
                
                <div class="text-center flex-1">
                  <div class="text-2xl font-bold text-gray-800">{{ formatTime(flightGroup.arrival_time) }}</div>
                  <div class="text-sm text-gray-600">{{ flightGroup.destination_code }}</div>
                  <div class="text-xs text-gray-500">{{ flightGroup.destination_city }}</div>
                </div>
              </div>
              
              <div class="flex justify-between items-center pt-4 border-t">
                <div>
                  <span class="text-sm text-gray-600">Flight:</span>
                  <span class="ml-2 font-medium text-gray-800">{{ flightGroup.flight_number }}</span>
                </div>
                <div>
                  <span class="text-sm text-gray-600">Status:</span>
                  <span class="ml-2 font-medium text-gray-800 capitalize">{{ flightGroup.status }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-4 text-gray-500">
            No flight information available
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white rounded-xl shadow-md p-6">
            <div class="flex items-center">
              <div class="bg-blue-100 p-3 rounded-lg">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm text-gray-500">Passengers</p>
                <p class="text-2xl font-bold text-gray-800">{{ passengerCount }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-md p-6">
            <div class="flex items-center">
              <div class="bg-green-100 p-3 rounded-lg">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm text-gray-500">Total Amount</p>
                <p class="text-2xl font-bold text-gray-800">₱{{ bookingData.total_amount?.toLocaleString() || '0' }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-md p-6">
            <div class="flex items-center">
              <div class="bg-purple-100 p-3 rounded-lg">
                <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-sm text-gray-500">Booking Status</p>
                <p class="text-xl font-bold text-gray-800 capitalize">{{ bookingData.status }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Flights Tab -->
      <div v-else-if="activeTab === 'flights'" class="space-y-8">
        <div class="bg-white rounded-xl shadow-md p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-6 pb-4 border-b">Flight Details</h2>
          
          <div v-if="uniqueFlights.length > 0" class="space-y-8">
            <div v-for="(flight, index) in uniqueFlights" :key="index" class="border rounded-lg p-6">
              <!-- Flight Header -->
              <div class="flex justify-between items-start mb-6">
                <div>
                  <h3 class="font-semibold text-gray-800 text-lg">
                    {{ flight.airline_name }} ({{ flight.airline_code }})
                  </h3>
                  <p class="text-sm text-gray-600">Flight {{ flight.flight_number }}</p>
                </div>
                <div class="text-right">
                  <span class="inline-block px-3 py-1 rounded-full text-sm font-semibold"
                        :class="getStatusClass(flight.status)">
                    {{ flight.status }}
                  </span>
                  <p class="text-sm text-gray-500 mt-1">{{ formatDate(flight.departure_time) }}</p>
                </div>
              </div>

              <!-- Flight Route -->
              <div class="mb-6">
                <div class="flex items-center justify-between">
                  <div class="text-center">
                    <div class="text-2xl font-bold text-gray-800">{{ flight.origin_code }}</div>
                    <div class="text-sm text-gray-600">{{ flight.origin_city }}</div>
                    <div class="text-xs text-gray-500">{{ formatTime(flight.departure_time) }}</div>
                  </div>
                  
                  <div class="flex-1 px-4 relative">
                    <div class="flex items-center">
                      <div class="flex-1 border-t-2 border-gray-300"></div>
                      <div class="mx-4 flex flex-col items-center">
                        <svg class="w-8 h-8 text-blue-500 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7"/>
                        </svg>
                        <span class="text-xs text-gray-500">{{ flight.duration }}</span>
                      </div>
                      <div class="flex-1 border-t-2 border-gray-300"></div>
                    </div>
                  </div>
                  
                  <div class="text-center">
                    <div class="text-2xl font-bold text-gray-800">{{ flight.destination_code }}</div>
                    <div class="text-sm text-gray-600">{{ flight.destination_city }}</div>
                    <div class="text-xs text-gray-500">{{ formatTime(flight.arrival_time) }}</div>
                  </div>
                </div>
              </div>

              <!-- Flight Info Grid -->
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 pt-6 border-t">
                <div>
                  <p class="text-sm text-gray-500">Terminal</p>
                  <p class="font-medium text-gray-800">T1</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Gate</p>
                  <p class="font-medium text-gray-800">--</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Aircraft</p>
                  <p class="font-medium text-gray-800">A320</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Seat Class</p>
                  <p class="font-medium text-gray-800">Economy</p>
                </div>
              </div>

              <!-- Passengers on this flight -->
              <div v-if="getPassengersForFlight(flight).length > 0" class="mt-6 pt-6 border-t">
                <h4 class="font-medium text-gray-700 mb-3">Passengers on this flight</h4>
                <div class="space-y-2">
                  <div v-for="passenger in getPassengersForFlight(flight)" :key="passenger.id" 
                       class="flex items-center justify-between text-sm">
                    <span>{{ passenger.passenger?.first_name }} {{ passenger.passenger?.last_name }}</span>
                    <span class="text-gray-600">Seat: {{ passenger.seat?.seat_number || 'Not assigned' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-gray-500">
            No flight information available
          </div>
        </div>
      </div>

      <!-- Passengers Tab -->
      <div v-else-if="activeTab === 'passengers'" class="space-y-8">
        <div class="bg-white rounded-xl shadow-md p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-6 pb-4 border-b">Passenger Details</h2>
          
          <div v-if="bookingData.details && bookingData.details.length > 0" class="space-y-6">
            <div v-for="(detail, index) in uniquePassengers" :key="detail.passenger?.id || index" class="border rounded-lg p-6">
              <div class="flex justify-between items-start mb-4">
                <div>
                  <h4 class="font-semibold text-gray-800 text-lg">
                    {{ detail.passenger?.title || 'Mr.' }} {{ detail.passenger?.first_name }} {{ detail.passenger?.last_name }}
                  </h4>
                  <div class="flex items-center mt-2 space-x-4">
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                          :class="getPassengerTypeClass(detail.passenger?.passenger_type)">
                      {{ detail.passenger?.passenger_type || 'Adult' }}
                    </span>
                    <span class="text-sm text-gray-600">
                      {{ detail.passenger?.nationality || 'Philippines' }}
                    </span>
                  </div>
                </div>
                <span class="bg-gray-100 text-gray-800 text-sm font-medium px-3 py-1 rounded-full">
                  Passenger {{ index + 1 }}
                </span>
              </div>

              <!-- Personal Information -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <p class="text-sm text-gray-500">Date of Birth</p>
                  <p class="font-medium text-gray-800">
                    {{ formatDate(detail.passenger?.date_of_birth) || 'Not provided' }}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Passport Number</p>
                  <p class="font-medium text-gray-800">
                    {{ detail.passenger?.passport_number || 'Not provided' }}
                  </p>
                </div>
              </div>

              <!-- Flight Assignments -->
              <div v-if="getFlightsForPassenger(detail.passenger?.id).length > 0" class="mt-6 pt-6 border-t">
                <h5 class="font-medium text-gray-700 mb-3">Flight Assignments</h5>
                <div class="space-y-3">
                  <div v-for="flight in getFlightsForPassenger(detail.passenger?.id)" :key="flight.id" 
                       class="flex items-center justify-between text-sm bg-gray-50 p-3 rounded">
                    <div>
                      <span class="font-medium">{{ flight.origin_code }} → {{ flight.destination_code }}</span>
                      <span class="text-gray-500 ml-2">({{ formatDate(flight.departure_time) }})</span>
                    </div>
                    <div class="text-right">
                      <span class="text-gray-600">Seat: {{ flight.seat_number || 'Not assigned' }}</span>
                      <span class="block text-xs text-gray-500">{{ flight.flight_number }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Add-ons -->
              <div v-if="detail.addons && detail.addons.length > 0" class="mt-6 pt-6 border-t">
                <h5 class="font-medium text-gray-700 mb-3">Additional Services</h5>
                <div class="flex flex-wrap gap-2">
                  <span v-for="addon in detail.addons" :key="addon.id"
                        class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    {{ addon.name }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-gray-500">
            No passenger information available
          </div>
        </div>
      </div>

      <!-- Payment Tab -->
      <div v-else-if="activeTab === 'payment'" class="space-y-8">
        <!-- Payment Summary -->
        <div class="bg-white rounded-xl shadow-md p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-6 pb-4 border-b">Payment Summary</h2>
          
          <div class="space-y-6">
            <!-- Payment Status -->
            <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div class="flex items-center">
                <div :class="paymentStatusClasses" class="p-2 rounded-lg mr-3">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                </div>
                <div>
                  <p class="font-medium text-gray-800">Payment Status</p>
                  <p class="text-sm text-gray-600">Updated {{ formatDate(bookingData.updated_at) }}</p>
                </div>
              </div>
              <span :class="paymentStatusBadgeClasses" class="px-3 py-1 rounded-full text-sm font-medium">
                {{ paymentStatusText }}
              </span>
            </div>

            <!-- Payment Details -->
            <div class="space-y-4">
              <h3 class="font-semibold text-gray-700">Payment Details</h3>
              
              <div v-if="bookingData.payments && bookingData.payments.length > 0" class="space-y-3">
                <div v-for="payment in bookingData.payments" :key="payment.id" class="border rounded-lg p-4">
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <p class="text-sm text-gray-500">Payment ID</p>
                      <p class="font-medium text-gray-800">{{ payment.transaction_id || 'N/A' }}</p>
                    </div>
                    <div>
                      <p class="text-sm text-gray-500">Method</p>
                      <p class="font-medium text-gray-800">{{ payment.method }}</p>
                    </div>
                    <div>
                      <p class="text-sm text-gray-500">Amount</p>
                      <p class="font-medium text-gray-800">₱{{ payment.amount?.toLocaleString() }}</p>
                    </div>
                    <div>
                      <p class="text-sm text-gray-500">Date</p>
                      <p class="font-medium text-gray-800">{{ formatDate(payment.payment_date) }}</p>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-4 text-gray-500">
                No payment information available
              </div>
            </div>

            <!-- Price Breakdown -->
            <div class="space-y-3">
              <h3 class="font-semibold text-gray-700">Price Breakdown</h3>
              
              <div class="border rounded-lg p-4">
                <div class="space-y-3">
                  <div class="flex justify-between">
                    <span class="text-gray-600">Base Fare</span>
                    <span class="font-medium">₱{{ bookingData.base_fare_total?.toLocaleString() || '0' }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Taxes & Fees</span>
                    <span class="font-medium">₱{{ bookingData.tax_total?.toLocaleString() || '0' }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Insurance</span>
                    <span class="font-medium">₱{{ bookingData.insurance_total?.toLocaleString() || '0' }}</span>
                  </div>
                  <div class="flex justify-between text-lg font-bold pt-3 border-t">
                    <span>Total Amount</span>
                    <span class="text-blue-600">₱{{ bookingData.total_amount?.toLocaleString() || '0' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="bg-white rounded-xl shadow-md p-6 mt-8">
        <h2 class="text-xl font-bold text-gray-800 mb-6 pb-4 border-b">Manage Booking</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button 
            @click="downloadETicket"
            :disabled="!canDownloadETicket"
            :class="canDownloadETicket ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-300 cursor-not-allowed'"
            class="flex flex-col items-center justify-center p-4 text-white font-medium rounded-lg transition duration-200"
          >
            <svg class="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            <span>E-Ticket</span>
          </button>
          
          <button 
            @click="sendToEmail"
            class="flex flex-col items-center justify-center p-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition duration-200"
          >
            <svg class="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
            <span>Email Itinerary</span>
          </button>
          
          <button 
            @click="modifyBooking"
            :disabled="!canModify"
            :class="canModify ? 'bg-yellow-600 hover:bg-yellow-700' : 'bg-gray-300 cursor-not-allowed'"
            class="flex flex-col items-center justify-center p-4 text-white font-medium rounded-lg transition duration-200"
          >
            <svg class="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
            <span>Modify</span>
          </button>
          
          <button 
            @click="cancelBooking"
            :disabled="!canCancel"
            :class="canCancel ? 'bg-red-600 hover:bg-red-700' : 'bg-gray-300 cursor-not-allowed'"
            class="flex flex-col items-center justify-center p-4 text-white font-medium rounded-lg transition duration-200"
          >
            <svg class="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
            <span>Cancel</span>
          </button>
        </div>
      </div>

      <!-- Important Information -->
      <div class="mt-8 bg-yellow-50 border border-yellow-200 rounded-xl p-6">
        <h3 class="font-bold text-gray-800 mb-3 flex items-center">
          <svg class="w-5 h-5 mr-2 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          Important Information
        </h3>
        <ul class="list-disc pl-5 space-y-2 text-gray-700">
          <li>Please arrive at the airport at least 3 hours before departure for international flights.</li>
          <li>Online check-in opens 48 hours before departure and closes 2 hours before departure.</li>
          <li>Valid government-issued ID is required at check-in.</li>
          <li>Changes and cancellations are subject to airline policies and fees.</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/booking/api'
import { useNotificationStore } from '@/stores/notification'
import { useModalStore } from '@/stores/modal'

const route = useRoute()
const router = useRouter()
const notificationStore = useNotificationStore()
const modalStore = useModalStore()

const loading = ref(true)
const error = ref('')
const bookingData = ref(null)
const activeTab = ref('overview')

// Fetch booking details
const fetchBookingDetails = async () => {
  const bookingReference = route.params.reference
  
  if (!bookingReference) {
    error.value = 'No booking reference provided'
    loading.value = false
    return
  }

  try {
    loading.value = true
    error.value = ''
    
    // Extract booking ID from reference (BK00000071 -> 71)
    const bookingId = bookingReference.replace('BK', '')
    
    console.log(`Fetching booking details for reference: ${bookingReference}, ID: ${bookingId}`)
    
    // Try to fetch by booking ID first
    try {
      const response = await api.get(`booking/${bookingId}/`)
      if (response.data.success) {
        bookingData.value = response.data.booking
        console.log('Booking data loaded:', bookingData.value)
      } else {
        error.value = response.data.error || 'Failed to load booking details'
      }
    } catch (err) {
      console.error('Error fetching booking by ID:', err)
      
      // Fallback: Search for booking by reference in your list of bookings
      // You might need to implement a search endpoint in your backend
      error.value = 'Booking not found. Please check your reference number.'
    }
    
  } catch (err) {
    console.error('Error fetching booking details:', err)
    error.value = 'Failed to load booking details. Please try again.'
  } finally {
    loading.value = false
  }
}

// Helper functions
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  const date = new Date(dateTimeString)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

const formatFlightDate = (dateTimeString) => {
  if (!dateTimeString) return ''
  const date = new Date(dateTimeString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const getStatusClass = (status) => {
  const statusMap = {
    'confirmed': 'bg-green-100 text-green-800',
    'pending': 'bg-yellow-100 text-yellow-800',
    'cancelled': 'bg-red-100 text-red-800',
    'checkin': 'bg-blue-100 text-blue-800',
    'boarding': 'bg-purple-100 text-purple-800',
    'completed': 'bg-gray-100 text-gray-800'
  }
  return statusMap[status?.toLowerCase()] || 'bg-gray-100 text-gray-800'
}

const getPassengerTypeClass = (type) => {
  const typeMap = {
    'adult': 'bg-blue-100 text-blue-800',
    'child': 'bg-green-100 text-green-800',
    'infant': 'bg-pink-100 text-pink-800'
  }
  return typeMap[type?.toLowerCase()] || 'bg-gray-100 text-gray-800'
}

// Computed properties
const bookingStatusText = computed(() => {
  if (!bookingData.value) return ''
  const status = bookingData.value.status?.toLowerCase()
  const statusMap = {
    'confirmed': 'Booking Confirmed',
    'pending': 'Payment Pending',
    'cancelled': 'Cancelled',
    'checkin': 'Ready for Check-in',
    'boarding': 'Boarding',
    'completed': 'Completed'
  }
  return statusMap[status] || 'Booking Status'
})

const bookingStatusMessage = computed(() => {
  if (!bookingData.value) return ''
  const status = bookingData.value.status?.toLowerCase()
  const messageMap = {
    'confirmed': 'Your booking is confirmed. Safe travels!',
    'pending': 'Your booking is being processed. Please wait.',
    'cancelled': 'This booking has been cancelled.',
    'checkin': 'You can now check-in for your flight.',
    'boarding': 'Boarding is in progress.',
    'completed': 'This flight has been completed.'
  }
  return messageMap[status] || 'Booking status unknown.'
})

const statusClasses = computed(() => {
  if (!bookingData.value) return 'bg-gray-100 text-gray-800 border border-gray-200'
  const status = bookingData.value.status?.toLowerCase()
  const classMap = {
    'confirmed': 'bg-green-100 text-green-800 border border-green-200',
    'pending': 'bg-yellow-100 text-yellow-800 border border-yellow-200',
    'cancelled': 'bg-red-100 text-red-800 border border-red-200',
    'checkin': 'bg-blue-100 text-blue-800 border border-blue-200',
    'boarding': 'bg-purple-100 text-purple-800 border border-purple-200',
    'completed': 'bg-gray-100 text-gray-800 border border-gray-200'
  }
  return classMap[status] || 'bg-gray-100 text-gray-800 border border-gray-200'
})

const statusIcon = computed(() => {
  if (!bookingData.value) return '📋'
  const status = bookingData.value.status?.toLowerCase()
  const iconMap = {
    'confirmed': '✅',
    'pending': '⏳',
    'cancelled': '❌',
    'checkin': '🎫',
    'boarding': '✈️',
    'completed': '🏁'
  }
  return iconMap[status] || '📋'
})

const paymentStatusText = computed(() => {
  if (!bookingData.value) return 'Pending'
  const status = bookingData.value.status?.toLowerCase()
  const statusMap = {
    'confirmed': 'Paid',
    'pending': 'Pending',
    'cancelled': 'Refunded',
    'checkin': 'Paid',
    'boarding': 'Paid',
    'completed': 'Paid'
  }
  return statusMap[status] || 'Pending'
})

const paymentStatusClasses = computed(() => {
  if (!bookingData.value) return 'bg-gray-100 text-gray-800'
  const status = bookingData.value.status?.toLowerCase()
  const classMap = {
    'confirmed': 'bg-green-100 text-green-800',
    'pending': 'bg-yellow-100 text-yellow-800',
    'cancelled': 'bg-red-100 text-red-800',
    'checkin': 'bg-green-100 text-green-800',
    'boarding': 'bg-green-100 text-green-800',
    'completed': 'bg-green-100 text-green-800'
  }
  return classMap[status] || 'bg-gray-100 text-gray-800'
})

const paymentStatusBadgeClasses = computed(() => {
  if (!bookingData.value) return 'bg-gray-100 text-gray-800'
  const status = bookingData.value.status?.toLowerCase()
  const classMap = {
    'confirmed': 'bg-green-100 text-green-800',
    'pending': 'bg-yellow-100 text-yellow-800',
    'cancelled': 'bg-red-100 text-red-800'
  }
  return classMap[status] || 'bg-gray-100 text-gray-800'
})

const passengerCount = computed(() => {
  if (!bookingData.value?.details) return 0
  
  // Count unique passengers
  const passengerIds = new Set()
  bookingData.value.details.forEach(detail => {
    if (detail.passenger?.id) {
      passengerIds.add(detail.passenger.id)
    }
  })
  return passengerIds.size
})

const uniquePassengers = computed(() => {
  if (!bookingData.value?.details) return []
  
  // Get unique passengers
  const passengerMap = new Map()
  bookingData.value.details.forEach(detail => {
    if (detail.passenger?.id && !passengerMap.has(detail.passenger.id)) {
      passengerMap.set(detail.passenger.id, detail)
    }
  })
  return Array.from(passengerMap.values())
})

const uniqueFlights = computed(() => {
  if (!bookingData.value?.details) return []
  
  // Get unique flights from schedule data
  const flightMap = new Map()
  bookingData.value.details.forEach(detail => {
    if (detail.schedule?.id && !flightMap.has(detail.schedule.id)) {
      const flight = {
        id: detail.schedule.id,
        flight_number: detail.schedule.flight_number,
        airline_name: detail.schedule.airline_name,
        airline_code: detail.schedule.airline_code,
        origin_code: detail.schedule.origin,
        origin_city: detail.schedule.origin_city,
        destination_code: detail.schedule.destination,
        destination_city: detail.schedule.destination_city,
        departure_time: detail.schedule.departure_time,
        arrival_time: detail.schedule.arrival_time,
        duration: detail.schedule.flight_duration,
        status: detail.status,
        seat_number: detail.seat?.seat_number
      }
      flightMap.set(detail.schedule.id, flight)
    }
  })
  return Array.from(flightMap.values())
})

const groupedFlights = computed(() => {
  if (!bookingData.value?.details) return []
  
  // Group flights by route
  const groups = []
  const flightMap = new Map()
  
  bookingData.value.details.forEach(detail => {
    if (detail.schedule) {
      const key = `${detail.schedule.origin}-${detail.schedule.destination}`
      if (!flightMap.has(key)) {
        const group = {
          key,
          origin: detail.schedule.origin_city,
          origin_code: detail.schedule.origin,
          destination: detail.schedule.destination_city,
          destination_code: detail.schedule.destination,
          departure_time: detail.schedule.departure_time,
          arrival_time: detail.schedule.arrival_time,
          duration: detail.schedule.flight_duration,
          airline_code: detail.schedule.airline_code,
          flight_number: detail.schedule.flight_number,
          status: detail.status
        }
        flightMap.set(key, group)
        groups.push(group)
      }
    }
  })
  
  return groups
})

// Helper methods
const getPassengersForFlight = (flight) => {
  if (!bookingData.value?.details || !flight) return []
  return bookingData.value.details.filter(detail => 
    detail.schedule?.id === flight.id
  )
}

const getFlightsForPassenger = (passengerId) => {
  if (!bookingData.value?.details || !passengerId) return []
  return bookingData.value.details
    .filter(detail => detail.passenger?.id === passengerId)
    .map(detail => ({
      id: detail.schedule?.id,
      flight_number: detail.schedule?.flight_number,
      origin_code: detail.schedule?.origin,
      destination_code: detail.schedule?.destination,
      departure_time: detail.schedule?.departure_time,
      seat_number: detail.seat?.seat_number
    }))
}

// Action methods
const canModify = computed(() => {
  return bookingData.value?.status?.toLowerCase() === 'confirmed'
})

const canCancel = computed(() => {
  const status = bookingData.value?.status?.toLowerCase()
  return ['pending', 'confirmed'].includes(status)
})

const canDownloadETicket = computed(() => {
  return bookingData.value?.status?.toLowerCase() === 'confirmed'
})

const downloadETicket = () => {
  if (canDownloadETicket.value) {
    notificationStore.info('E-Ticket download functionality would be implemented here')
    // Implement PDF generation/download
  }
}

const sendToEmail = () => {
  notificationStore.info('Booking details would be sent to your email')
  // Implement email sending
}

const modifyBooking = () => {
  if (canModify.value) {
    router.push({
      name: 'ModifyBooking',
      params: { reference: route.params.reference }
    })
  }
}

const cancelBooking = async () => {
  if (!canCancel.value) return

  const confirmed = await modalStore.confirm({
    title: 'Cancel Booking?',
    message: 'Are you sure you want to cancel this booking? This action cannot be undone.',
    confirmText: 'Yes, Cancel',
    cancelText: 'No, Keep'
  })

  if (!confirmed) return

  try {
    // Implement cancel booking API call
    const bookingId = bookingData.value.id
    const response = await api.post(`cancel-booking/${bookingId}/`)
    
    if (response.data.success) {
      notificationStore.success('Booking cancelled successfully')
      // Refresh booking data
      await fetchBookingDetails()
    } else {
      notificationStore.error('Failed to cancel booking: ' + response.data.error)
    }
  } catch (err) {
    notificationStore.error('Failed to cancel booking: ' + err.message)
  }
}

// Initialize
onMounted(() => {
  fetchBookingDetails()
})
</script>

<style scoped>
/* Custom animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>