<template>
  <div class="flex flex-col lg:flex-row items-start justify-center bg-gray-50 min-h-screen py-10 px-4 lg:px-10 gap-8 poppins">

    <!-- Debug Panel -->
    <div v-if="debugMode" class="fixed top-0 left-0 bg-black text-green-400 p-4 text-xs font-mono z-50 max-w-md overflow-auto max-h-screen">
      <p>Schedule: {{ selectedScheduleId }}</p>
      <p>Airline ID: {{ aircraftInfo.airline_id }}</p>
      <p>Capacity: {{ aircraftInfo.capacity }}</p>
      <p>Available Airlines: {{ airlines.length }}</p>
      <p>Airline IDs: {{ airlines.map(a => a.id).join(', ') }}</p>
      <p>Layout Config Keys: {{ Object.keys(layoutConfig) }}</p>
      <p>Class Order: {{ classOrder }}</p>
      <p>Has Valid Layout: {{ hasValidLayout }}</p>
      <p>Raw API Data: {{ rawApiData }}</p>
      <p>Special Seats Count: {{ specialSeatsCount }}</p>
    </div>

    <div v-if="debugMode" class="bg-black text-green-400 p-2 text-xs">
      <p>aircraftInfo.aircraft: {{ aircraftInfo.aircraft }}</p>
      <p>aircraftInfo.aircraft_id: {{ aircraftInfo.aircraft_id }}</p>
      <p>rawApiData.flight: {{ rawApiData?.flight }}</p>
    </div>

    <!-- Left Panel -->
    <div class="w-full lg:w-80 order-2 lg:order-1">
      <div class="bg-white rounded-[1px] shadow-sm p-6 border border-gray-200 sticky top-10 space-y-6">
        
        <!-- Header -->
        <div class="text-center pb-4 border-b border-gray-100">
          <div class="w-12 h-12 bg-[#002D1E] rounded-[1px] flex items-center justify-center mx-auto mb-3">
            <i class="ph ph-airplane-tilt text-white text-xl"></i>
          </div>
          <h2 class="font-bold text-[#002D1E] text-lg uppercase tracking-tight poppins">Aircraft Config</h2>
          <button @click="debugMode = !debugMode" class="text-[10px] text-gray-400 mt-1 hover:text-[#fe3787] poppins">
            {{ debugMode ? 'Hide Debug' : 'Show Debug' }}
          </button>
        </div>

        <!-- Schedule Selection -->
        <div class="bg-gray-50 rounded-[1px] p-4 border border-gray-200">
          <label for="schedule-select" class="flex items-center gap-2 text-[11px] font-bold uppercase text-gray-500 mb-2 poppins">
            <i class="ph ph-calendar-blank"></i>
            Select Schedule
          </label>
          <div class="relative">
            <select 
              id="schedule-select"
              name="schedule"
              v-model="selectedScheduleId" 
              @change="handleScheduleChange" 
              class="w-full bg-white border border-gray-300 p-3 pr-10 text-sm rounded-[1px] outline-none focus:border-[#fe3787] poppins"
            >
              <option value="">Choose a flight schedule...</option>
              <option v-for="s in schedules" :key="s.id" :value="s.id">
                {{ s.flight_number }} — {{ s.aircraft_name }}
              </option>
            </select>
            <i class=" absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"></i>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="!selectedScheduleId" class="py-8 text-center">
          <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <i class="ph ph-seat text-gray-400 text-2xl"></i>
          </div>
          <p class="text-sm text-gray-500 font-medium mb-1">No Schedule Selected</p>
          <p class="text-[11px] text-gray-400">Select a schedule to view the aircraft seat layout.</p>
        </div>

        <!-- Content when schedule selected -->
        <template v-else>
          
          <!-- Aircraft Info -->
          <div class="bg-gradient-to-br from-[#002D1E] to-[#004d2e] rounded-[1px] p-4 text-white relative overflow-hidden shadow-md">
            <div class="relative z-10">
              <p class="text-[10px] font-bold text-white/60 uppercase tracking-wider mb-1 poppins">Current Aircraft</p>
              <h3 class="font-bold text-lg mb-1 poppins">{{ aircraftInfo.name || 'Loading...' }}</h3>
              <div class="flex items-center gap-3 mt-2">
                <span class="bg-white/20 px-2 py-1 rounded-[1px] text-[10px] font-medium poppins">
                  <i class="ph ph-users mr-1"></i>
                  {{ aircraftInfo.capacity }} Seats
                </span>
              </div>
              <p class="text-[10px] text-white/70 mt-2 poppins">
                Airline: {{ currentAirlineName }}
              </p>
            </div>
            <!-- Decorative icon -->
            <i class="ph ph-airplane absolute -right-4 -bottom-4 text-white/10 text-8xl transform rotate-12"></i>
          </div>

          <!-- Loading State -->
          <div v-if="isLoading" class="py-8 text-center">
            <i class="ph ph-spinner animate-spin text-3xl text-[#fe3787] mb-2"></i>
            <p class="text-sm text-gray-500">Loading seat configuration...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="hasError" class="bg-red-50 border border-red-200 rounded-[1px] p-4">
            <div class="flex items-start gap-3">
              <i class="ph ph-warning-circle text-red-500 text-lg mt-0.5"></i>
              <div>
                <p class="text-sm font-bold text-red-800 mb-1 poppins">Error Loading Data</p>
                <p class="text-[11px] text-red-700 mb-3 poppins">{{ errorMessage }}</p>
                <button 
                  @click="handleScheduleChange" 
                  class="w-full py-2 bg-[#fe3787] text-white rounded-[1px] text-[11px] font-bold uppercase hover:bg-[#fb1873] transition-colors poppins"
                >
                  Retry
                </button>
              </div>
            </div>
          </div>

          <!-- CRITICAL ERROR: Invalid Airline -->
          <div v-else-if="aircraftInfo.airline_id && !isValidAirline(aircraftInfo.airline_id)" class="bg-red-50 border-2 border-red-300 rounded-lg p-4">
            <div class="flex items-start gap-3">
              <i class="ph ph-warning-circle text-red-600 text-xl mt-0.5"></i>
              <div class="w-full">
                <p class="text-sm font-bold text-red-800 mb-1">⚠️ Broken Airline Reference</p>
                <p class="text-[11px] text-red-700 mb-2">
                  This schedule's aircraft references <strong>Airline ID {{ aircraftInfo.airline_id }}</strong> which doesn't exist.
                </p>
                <p class="text-[10px] text-red-600 mb-3">
                  This usually happens when an airline was deleted but aircraft/flight data still references it.
                </p>
                
                <!-- Auto-fix option -->
                <div v-if="airlines.length > 0" class="space-y-2">
                  <p class="text-[10px] font-bold text-gray-600 uppercase">Quick Fix Options:</p>
                  <button 
                    @click="fixAirlineReference(airlines[0].id)" 
                    class="w-full py-2 bg-[#fe3787] text-white rounded-lg text-[11px] font-bold uppercase hover:bg-[#e62e7a] transition-colors flex items-center justify-center gap-2"
                  >
                    <i class="ph ph-wrench"></i>
                    Assign to {{ airlines[0].name }} (ID: {{ airlines[0].id }})
                  </button>
                  <select 
                    v-if="airlines.length > 1"
                    v-model="selectedFixAirlineId"
                    class="w-full border border-gray-300 p-2 text-xs rounded-lg"
                  >
                    <option v-for="al in airlines" :key="al.id" :value="al.id">
                      {{ al.name }} (ID: {{ al.id }})
                    </option>
                  </select>
                  <button 
                    v-if="airlines.length > 1 && selectedFixAirlineId"
                    @click="fixAirlineReference(selectedFixAirlineId)" 
                    class="w-full py-2 bg-[#002D1E] text-white rounded-lg text-[11px] font-bold uppercase hover:bg-[#004d2e] transition-colors"
                  >
                    Assign to Selected Airline
                  </button>
                </div>

                <!-- Create new airline -->
                <div class="mt-3 pt-3 border-t border-red-200">
                  <p class="text-[10px] font-bold text-gray-600 uppercase mb-2">Or Create New Airline:</p>
                  <button 
                    @click="showCreateAirlineModal = true" 
                    class="w-full py-2 bg-emerald-500 text-white rounded-lg text-[11px] font-bold uppercase hover:bg-emerald-600 transition-colors flex items-center justify-center gap-2"
                  >
                    <i class="ph ph-plus-circle"></i>
                    Create New Airline
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- NO AIRLINE ID FOUND -->
          <div v-else-if="!aircraftInfo.airline_id" class="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <div class="flex items-start gap-3">
              <i class="ph ph-warning-circle text-amber-500 text-lg mt-0.5"></i>
              <div>
                <p class="text-sm font-bold text-amber-800 mb-1">No Airline Detected</p>
                <p class="text-[11px] text-amber-700 mb-3">Could not determine airline from schedule data.</p>
                <div class="space-y-2">
                  <button 
                    v-if="airlines.length > 0"
                    @click="useFirstAirline" 
                    class="w-full py-2 bg-[#fe3787] text-white rounded-lg text-[11px] font-bold uppercase hover:bg-[#e62e7a] transition-colors"
                  >
                    Use First Available Airline
                  </button>
                  <button 
                    @click="showCreateAirlineModal = true" 
                    class="w-full py-2 bg-[#002D1E] text-white rounded-lg text-[11px] font-bold uppercase hover:bg-[#004d2e] transition-colors"
                  >
                    Create New Airline
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Seat Classes List -->
          <div v-else-if="seatClassesForAirline.length === 0" class="bg-amber-50 border border-amber-200 rounded-[1px] p-4">
            <div class="flex items-start gap-3">
              <i class="ph ph-warning-circle text-amber-500 text-lg mt-0.5"></i>
              <div>
                <p class="text-sm font-bold text-amber-800 mb-1 poppins">No Seat Classes</p>
                <p class="text-[11px] text-amber-700 mb-3 poppins">No seat classes for airline {{ currentAirlineName }}.</p>
                <button 
                  @click="openClassModal()" 
                  class="w-full py-2 bg-[#fe3787] text-white rounded-[1px] text-[11px] font-bold uppercase hover:bg-[#fb1873] transition-colors poppins"
                >
                  <i class="ph ph-plus-circle mr-1"></i>
                  Create Seat Class
                </button>
              </div>
            </div>
          </div>

          <!-- Auto-Generate Button -->
          <div v-else-if="!hasExistingLayout && totalConfiguredSeats === 0" class="bg-blue-50 border border-blue-200 rounded-[1px] p-4">
            <div class="flex items-start gap-3">
              <i class="ph ph-info text-blue-500 text-lg mt-0.5"></i>
              <div>
                <p class="text-sm font-bold text-blue-800 mb-1 poppins">New Aircraft</p>
                <p class="text-[11px] text-blue-700 mb-3 poppins">Generate seat layout for this aircraft.</p>
                <button 
                  @click="autoGenerateLayout" 
                  class="w-full py-2.5 bg-[#fe3787] text-white rounded-[1px] text-[11px] font-bold uppercase hover:bg-[#fb1873] transition-colors flex items-center justify-center gap-2 poppins"
                >
                  <i class="ph ph-magic-wand"></i>
                  Auto-Generate Layout
                </button>
              </div>
            </div>
          </div>

          <!-- Seat Classes List -->
          <div v-else class="pt-4 border-t border-gray-200">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-[11px] font-black text-gray-700 uppercase tracking-widest flex items-center gap-2 poppins">
                <i class="ph ph-armchair text-[#fe3787]"></i>
                Seat Classes
                <span class="bg-gray-100 text-gray-500 px-2 py-0.5 rounded-[1px] text-[9px]">
                  {{ seatClassesForAirline.length }}
                </span>
              </h3>
              <button 
                @click="openClassModal()" 
                class="bg-[#fe3787] hover:bg-[#fb1873] text-white px-3 py-1.5 rounded-[1px] text-[10px] font-bold uppercase poppins"
              >
                <i class="ph ph-plus-circle"></i> ADD
              </button>
            </div>

            <div class="space-y-3 max-h-[400px] overflow-y-auto pr-1">
              <div 
                v-for="(sc, index) in orderedAirlineSeatClasses" 
                :key="sc.id" 
                :draggable="true"
                @dragstart="handleDragStart($event, sc.id)"
                @dragend="handleDragEnd"
                @dragover.prevent="handleDragOver($event, sc.id)"
                @drop="handleDrop($event, sc.id)"
                class="p-4 rounded-[1px] border border-gray-200 bg-white relative group transition-all hover:border-[#fe3787]/30"
              >
                <div class="absolute left-2 top-1/2 -translate-y-1/2 text-gray-300 cursor-grab opacity-0 group-hover:opacity-100">
                  <i class="ph ph-dots-six-vertical text-lg"></i>
                </div>

                <div class="flex items-start justify-between ml-6">
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-2">
                      <div 
                        class="w-4 h-4 rounded-full border-2 border-white shadow-sm"
                        :style="{ backgroundColor: sc.color }"
                      ></div>
                      <h4 class="text-sm font-bold text-gray-800">{{ sc.name }}</h4>
                      <span class="text-[9px] px-2 py-0.5 rounded-full font-bold bg-gray-100 text-gray-600">
                        #{{ index + 1 }}
                      </span>
                    </div>

                    <p class="text-[10px] text-emerald-600 font-medium mb-2">
                      <i class="ph ph-check-circle mr-1"></i>
                      {{ getLayoutSeatCount(sc.id) }} seats
                    </p>

                    <div class="flex items-center gap-2">
                      <span class="text-[10px] text-gray-500">Price:</span>
                      <span class="text-[11px] font-mono font-bold text-[#fe3787]">x{{ sc.price_multiplier }}</span>
                    </div>
                    
                    <div class="mt-3 flex items-center gap-2">
                      <label :for="'color-' + sc.id" class="sr-only">Color</label>
                      <input 
                        :id="'color-' + sc.id"
                        type="color" 
                        v-model="sc.color" 
                        @change="updateSeatClassColor(sc)"
                        class="w-6 h-6 rounded cursor-pointer border-0 p-0"
                      />
                      <span class="text-[10px] font-mono text-gray-400">{{ sc.color }}</span>
                    </div>
                  </div>

                  <div class="flex flex-col gap-1 ml-2">
                    <button @click="openClassModal(sc)" class="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-[1px]">
                      <i class="ph ph-pencil-simple text-sm"></i>
                    </button>
                    <button @click="deleteSeatClass(sc.id)" class="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-[1px]">
                      <i class="ph ph-trash text-sm"></i>
                    </button>
                  </div>
                </div>
                
                <!-- Layout Configuration -->
                <div class="mt-4 pt-4 border-t border-gray-100" v-if="layoutConfig[sc.id]">
                  <div class="grid grid-cols-2 gap-3">
                    <div>
                      <label :for="'rows-' + sc.id" class="text-[9px] font-bold text-gray-500 uppercase mb-1 block poppins">Rows</label>
                      <input 
                        :id="'rows-' + sc.id"
                        v-model.number="layoutConfig[sc.id].rows" 
                        type="number" 
                        min="1" 
                        max="50"
                        class="w-full border border-gray-200 p-2 text-sm rounded-[1px] text-center font-mono focus:border-[#fe3787] outline-none"
                        @change="updateLayout"
                      />
                    </div>
                    <div>
                      <label :for="'cols-' + sc.id" class="text-[9px] font-bold text-gray-500 uppercase mb-1 block poppins">Columns</label>
                      <select 
                        :id="'cols-' + sc.id"
                        v-model.number="layoutConfig[sc.id].columns"
                        class="w-full border border-gray-200 p-2 text-sm rounded-[1px] text-center focus:border-[#fe3787] outline-none poppins"
                        @change="updateLayout"
                      >
                        <option :value="4">4 (2-2)</option>
                        <option :value="6">6 (3-3)</option>
                        <option :value="8">8 (4-4)</option>
                        <option :value="10">10 (5-5)</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div v-else class="mt-4 pt-4 border-t border-gray-100">
                  <p class="text-[10px] text-amber-600">Layout not configured</p>
                </div>
              </div>
            </div>

            <!-- Capacity Summary -->
            <div class="mt-4 p-4 bg-gray-50 rounded-[1px] border border-gray-200 shadow-sm transition-all duration-300">
              <div class="flex justify-between items-center mb-2">
                <span class="text-[10px] font-bold text-gray-500 uppercase tracking-widest poppins">Total Capacity</span>
                <span class="text-sm font-bold poppins" :class="{
                  'text-emerald-600': capacityStatus === 'exact',
                  'text-amber-600': capacityStatus === 'under',
                  'text-red-600': capacityStatus === 'over'
                }">
                  {{ totalConfiguredSeats }} / {{ aircraftInfo.capacity }}
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-[1px] h-2">
                <div 
                  class="h-2 rounded-[1px] transition-all duration-500"
                  :class="{
                    'bg-emerald-500': capacityStatus === 'exact',
                    'bg-amber-500': capacityStatus === 'under',
                    'bg-red-500': capacityStatus === 'over'
                  }"
                  :style="{ width: Math.min((totalConfiguredSeats / Math.max(aircraftInfo.capacity, 1)) * 100, 100) + '%' }"
                ></div>
              </div>
              <p v-if="capacityStatus === 'under'" class="text-[10px] text-amber-600 mt-2 font-medium poppins">
                <i class="ph ph-warning mr-1"></i>
                {{ aircraftInfo.capacity - totalConfiguredSeats }} seats remaining
              </p>
              <p v-else-if="capacityStatus === 'over'" class="text-[10px] text-red-600 mt-2 font-medium poppins">
                <i class="ph ph-warning mr-1"></i>
                {{ totalConfiguredSeats - aircraftInfo.capacity }} seats over capacity
              </p>
              <p v-else-if="capacityStatus === 'exact'" class="text-[10px] text-emerald-600 mt-2 font-medium poppins">
                <i class="ph ph-check-circle mr-1"></i>
                Configuration Complete
              </p>
            </div>
          </div>

          <!-- Stats -->
          <div v-if="totalConfiguredSeats > 0" class="pt-4 border-t border-gray-200 space-y-3">
            <h3 class="text-[11px] font-black text-gray-700 uppercase tracking-widest flex items-center gap-2 poppins">
              <i class="ph ph-chart-bar text-[#fe3787]"></i>
              Inventory
            </h3>
            <div class="grid grid-cols-3 gap-2">
              <div class="bg-white border border-gray-100 rounded-[1px] p-3 text-center shadow-sm">
                <p class="text-lg font-bold text-[#002D1E] poppins">{{ totalConfiguredSeats }}</p>
                <p class="text-[9px] text-gray-400 uppercase font-bold tracking-tighter poppins">Total</p>
              </div>
              <div class="bg-red-50/50 border border-red-100 rounded-[1px] p-3 text-center shadow-sm">
                <p class="text-lg font-bold text-red-600 poppins">{{ occupiedCount }}</p>
                <p class="text-[9px] text-red-400 uppercase font-bold tracking-tighter poppins">Sold</p>
              </div>
              <div class="bg-emerald-50/50 border border-emerald-100 rounded-[1px] p-3 text-center shadow-sm">
                <p class="text-lg font-bold text-emerald-600 poppins">{{ availableCount }}</p>
                <p class="text-[9px] text-emerald-400 uppercase font-bold tracking-tighter poppins">Free</p>
              </div>
            </div>
            
            <!-- Special Seats Stats -->
            <div v-if="specialSeatsCount > 0" class="pt-4 border-t border-gray-200">
              <h3 class="text-[11px] font-black text-gray-700 uppercase mb-3 tracking-widest flex items-center gap-2 poppins">
                <i class="ph ph-star-four text-amber-500"></i>
                Attributes
              </h3>
              <div class="grid grid-cols-2 gap-2">
                <div class="bg-white border border-gray-100 rounded-[1px] p-2 text-center shadow-sm">
                  <p class="text-sm font-bold text-red-600 poppins">{{ exitRowSeatsCount }}</p>
                  <p class="text-[9px] text-gray-400 uppercase font-bold poppins">Exit Row</p>
                </div>
                <div class="bg-white border border-gray-100 rounded-[1px] p-2 text-center shadow-sm">
                  <p class="text-sm font-bold text-blue-600 poppins">{{ wheelchairSeatsCount }}</p>
                  <p class="text-[9px] text-gray-400 uppercase font-bold poppins">Accessible</p>
                </div>
                <div class="bg-white border border-gray-100 rounded-[1px] p-2 text-center shadow-sm">
                  <p class="text-sm font-bold text-purple-600 poppins">{{ bassinetSeatsCount }}</p>
                  <p class="text-[9px] text-gray-400 uppercase font-bold poppins">Bassinet</p>
                </div>
                <div class="bg-white border border-gray-100 rounded-[1px] p-2 text-center shadow-sm">
                  <p class="text-sm font-bold text-emerald-600 poppins">{{ unaccompaniedMinorSeatsCount }}</p>
                  <p class="text-[9px] text-gray-400 uppercase font-bold poppins">U.M.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Save Options -->
          <div v-if="totalConfiguredSeats > 0" class="pt-4 border-t border-gray-200 space-y-3">
            
            <!-- Mode Selection -->
            <div class="flex gap-2 mb-4">
              <button 
                @click="saveMode = 'schedule'"
                :class="['flex-1 py-2 text-[10px] font-bold uppercase rounded-[1px] poppins transition-all', 
                  saveMode === 'schedule' ? 'bg-[#002D1E] text-white shadow-md' : 'bg-gray-100 text-gray-400 hover:bg-gray-200']"
              >
                Flight Only
              </button>
              <button 
                @click="saveMode = 'aircraft'"
                :class="['flex-1 py-2 text-[10px] font-bold uppercase rounded-[1px] poppins transition-all',
                  saveMode === 'aircraft' ? 'bg-[#fe3787] text-white shadow-md' : 'bg-gray-100 text-gray-400 hover:bg-gray-200']"
              >
                Global Template
              </button>
            </div>
            
            <!-- Description -->
            <p v-if="saveMode === 'schedule'" class="text-[10px] text-gray-500">
              Creates seats for THIS flight only. Other flights using this aircraft won't be affected.
            </p>
            <p v-else class="text-[10px] text-gray-500">
              Saves this layout as the default for {{ aircraftInfo.name }}. Future schedules can auto-apply it.
            </p>
            
            <!-- Replace the save button section with this -->
            <div v-if="totalConfiguredSeats > 0 && aircraftInfo.aircraft" class="pt-4 border-t border-gray-200 space-y-3">
              
              <div class="bg-blue-50 border border-blue-100 rounded-[1px] p-3 shadow-sm">
                <p class="text-[11px] text-blue-800 poppins italic">
                  <i class="ph ph-info mr-1"></i>
                  Saves to <strong>{{ aircraftInfo.name }}</strong> master layout.
                </p>
              </div>
              
              <button 
                @click="saveLayout" 
                :disabled="isSaving"
                class="w-full py-4 bg-[#002D1E] text-white font-bold text-[13px] uppercase tracking-[2px] rounded-[1px] hover:bg-[#004d2e] transition-all disabled:opacity-50 flex items-center justify-center gap-2 poppins shadow-lg hover:shadow-xl active:scale-95"
              >
                <i v-if="!isSaving" class="ph ph-floppy-disk text-lg"></i>
                <i v-else class="ph ph-spinner animate-spin text-lg"></i>
                {{ isSaving ? 'Synchronizing...' : 'Commit Layout' }}
              </button>
              
              <p class="text-[10px] text-center text-gray-400 poppins font-medium">
                {{ totalConfiguredSeats }} of {{ aircraftInfo.capacity }} utilization
              </p>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Center Panel - Seat Map -->
    <div class="max-w-lg lg:flex-1 order-1 lg:order-2 w-full">
      <!-- Empty State -->
      <div v-if="!selectedScheduleId" class="bg-white rounded-[1px] shadow-sm p-12 text-center min-h-[500px] flex flex-col items-center justify-center border border-gray-200 poppins">
        <div class="w-24 h-24 bg-gray-50 rounded-[1px] flex items-center justify-center mb-4">
          <i class="ph ph-airplane-tilt text-gray-200 text-4xl"></i>
        </div>
        <h3 class="text-xl font-bold text-[#002D1E] mb-2 poppins">Select a Schedule</h3>
        <p class="text-gray-400 max-w-xs mx-auto poppins">Choose a flight schedule to view the aircraft seat layout.</p>
      </div>

      <!-- Loading -->
      <div v-else-if="isLoading" class="bg-white rounded-2xl shadow-lg p-12 text-center min-h-[500px] flex flex-col items-center justify-center border border-gray-200">
        <i class="ph ph-spinner animate-spin text-4xl text-[#fe3787] mb-4"></i>
        <p class="text-gray-500">Loading seat configuration...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="hasError" class="bg-white rounded-[1px] shadow-sm p-12 text-center min-h-[500px] flex flex-col items-center justify-center border border-gray-200 poppins">
        <div class="w-24 h-24 bg-red-50 rounded-[1px] flex items-center justify-center mb-4">
          <i class="ph ph-warning-circle text-red-500 text-4xl"></i>
        </div>
        <h3 class="text-xl font-bold text-red-800 mb-2 poppins">Critical Error</h3>
        <p class="text-gray-400 max-w-xs mx-auto mb-4 poppins">{{ errorMessage }}</p>
        <button 
          @click="handleScheduleChange" 
          class="px-8 py-3 bg-[#fe3787] text-white rounded-[1px] font-bold hover:bg-[#fb1873] transition-all poppins shadow-lg"
        >
          Retry Connection
        </button>
      </div>

      <!-- Invalid Airline - Critical Error -->
      <div v-else-if="!aircraftInfo.airline_id && !aircraftInfo.airline" class="bg-white rounded-2xl shadow-lg p-12 text-center min-h-[500px] flex flex-col items-center justify-center border border-gray-200">
        <div class="w-24 h-24 bg-amber-100 rounded-full flex items-center justify-center mb-4">
          <i class="ph ph-warning-circle text-amber-500 text-4xl"></i>
        </div>
        <h3 class="text-xl font-bold text-gray-800 mb-2">No Airline Data</h3>
        <p class="text-gray-500 max-w-xs mx-auto mb-4">Could not find airline information from flight data.</p>
        <button 
          v-if="airlines.length > 0"
          @click="useFirstAirline" 
          class="w-full px-6 py-3 bg-[#fe3787] text-white rounded-xl font-bold hover:bg-[#e62e7a] transition-colors"
        >
          Use Available Airline
        </button>
      </div>

      <!-- No Airline ID -->
      <div v-else-if="!aircraftInfo.airline_id" class="bg-white rounded-2xl shadow-lg p-12 text-center min-h-[500px] flex flex-col items-center justify-center border border-gray-200">
        <div class="w-24 h-24 bg-amber-100 rounded-full flex items-center justify-center mb-4">
          <i class="ph ph-warning-circle text-amber-500 text-4xl"></i>
        </div>
        <h3 class="text-xl font-bold text-gray-800 mb-2">No Airline Detected</h3>
        <p class="text-gray-500 max-w-xs mx-auto mb-4">Could not determine airline from schedule data.</p>
        <div class="space-y-2 w-full max-w-xs">
          <button 
            v-if="airlines.length > 0"
            @click="useFirstAirline" 
            class="w-full px-6 py-3 bg-[#fe3787] text-white rounded-xl font-bold hover:bg-[#e62e7a] transition-colors"
          >
            Use First Available Airline
          </button>
          <button 
            @click="showCreateAirlineModal = true" 
            class="w-full px-6 py-3 bg-[#002D1E] text-white rounded-xl font-bold hover:bg-[#004d2e] transition-colors"
          >
            Create New Airline
          </button>
        </div>
      </div>

      <!-- No Layout State -->
      <div v-else-if="!hasValidLayout" class="bg-white rounded-[1px] shadow-sm p-12 text-center min-h-[500px] flex flex-col items-center justify-center border border-gray-200 poppins">
        <div class="w-24 h-24 bg-amber-50 rounded-[1px] flex items-center justify-center mb-4">
          <i class="ph ph-seat text-amber-500 text-4xl"></i>
        </div>
        <h3 class="text-xl font-bold text-[#002D1E] mb-2 poppins">No Seat Layout</h3>
        <p class="text-gray-400 max-w-xs mx-auto mb-6 poppins">This aircraft requires a seat configuration.</p>
        <button 
          v-if="seatClassesForAirline.length > 0"
          @click="autoGenerateLayout" 
          class="px-8 py-3 bg-[#fe3787] text-white rounded-[1px] font-bold hover:bg-[#fb1873] transition-all flex items-center gap-2 poppins shadow-lg"
        >
          <i class="ph ph-magic-wand text-lg"></i>
          Generate Map
        </button>
      </div>

      <!-- Enhanced Seat Map -->
      <div v-else class="bg-white border-x-[16px] border-t-[80px] border-b-[32px] border-gray-100 rounded-t-[140px] rounded-b-[60px] w-full px-8 py-12 shadow-xl relative poppins">
        
        <!-- Cockpit -->
        <div class="absolute -top-[60px] left-1/2 -translate-x-1/2 text-center">
          <div class="w-12 h-12 bg-gray-100 rounded-[1px] mx-auto mb-2 flex items-center justify-center border border-gray-200">
            <i class="ph ph-gauge text-gray-400 text-xl"></i>
          </div>
          <span class="text-[9px] font-bold text-gray-300 uppercase tracking-[3px] poppins">Flight Deck</span>
        </div>


        <div class="text-center mb-8">
          <h1 class="font-black text-[#002D1E] tracking-[4px] uppercase text-2xl mb-1 poppins">{{ aircraftInfo.name }}</h1>
          <p class="text-[10px] text-gray-400 uppercase font-bold tracking-widest poppins">
            Configuration: {{ totalConfiguredSeats }} Units
          </p>
        </div>

        <!-- Seat Grid - Enhanced -->
        <div class="space-y-8">
          <div v-for="classId in orderedClassIds" :key="classId" class="relative">
            <!-- Class Header -->
            <div class="flex items-center justify-center mb-4">
              <div 
                class="px-4 py-2 rounded-full border-2 flex items-center gap-2 shadow-sm relative group"
                :style="{ 
                  backgroundColor: getSeatClassColor(classId) + '15', 
                  borderColor: getSeatClassColor(classId),
                }"
              >
                <div class="w-2 h-2 rounded-[1px]" :style="{ backgroundColor: getSeatClassColor(classId) }"></div>
                <span class="text-[10px] font-bold uppercase tracking-widest poppins" :style="{ color: getSeatClassColor(classId) }">
                  {{ getSeatClassName(classId) }}
                </span>
                <span class="text-[9px] text-gray-400 font-bold poppins">x{{ getSeatClassMultiplier(classId) }}</span>
                
                <!-- Special features tooltip -->
                <div v-if="hasSpecialSeatsInClass(classId)" class="absolute -top-2 -right-2">
                  <div class="relative group">
                    <div class="w-5 h-5 bg-white border border-gray-200 rounded-[1px] flex items-center justify-center shadow-sm">
                      <i class="ph ph-star-four text-[8px] text-amber-500"></i>
                    </div>
                    <div class="absolute bottom-full right-0 mb-2 hidden group-hover:block w-48 bg-gray-900 text-white text-[10px] rounded-lg p-2 z-50">
                      <div class="space-y-1">
                        <div v-if="getExitRowCountInClass(classId) > 0" class="flex items-center gap-2">
                          <i class="ph ph-door-open text-red-400"></i>
                          <span>{{ getExitRowCountInClass(classId) }} Exit Row(s)</span>
                        </div>
                        <div v-if="getBassinetSeatsInClass(classId).length > 0" class="flex items-center gap-2">
                          <i class="ph ph-baby text-purple-400"></i>
                          <span>{{ getBassinetSeatsInClass(classId).length }} Bassinet seat(s)</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Rows -->
            <div v-if="layoutConfig[classId] && layoutConfig[classId].rows" v-for="rowNum in layoutConfig[classId].rows" :key="`${classId}-${rowNum}`" class="mb-4">
              <div class="flex justify-center items-center gap-3">
                <!-- Left Side Seats -->
                <div class="flex gap-2">
                  <button
                    v-for="colIdx in getLeftColumns(classId)"
                    :key="`L-${colIdx}`"
                    @click="selectSeat(classId, rowNum, colIdx)"
                    @contextmenu.prevent="showSeatContextMenu($event, classId, rowNum, colIdx)"
                    :class="getSeatStyle(classId, rowNum, colIdx)"
                    :style="getSeatColorStyle(classId, rowNum, colIdx)"
                    class="w-10 h-10 rounded-[1px] border flex items-center justify-center text-[11px] font-bold transition-all hover:scale-105 relative group shadow-sm poppins"
                  >
                    <!-- Seat number -->
                    <span>{{ getColumnLabel(colIdx) }}</span>
                    
                    <!-- Special Indicators -->
                    <div v-if="hasSpecialSeat(classId, rowNum, colIdx)" class="absolute -top-1 -right-1 flex flex-col gap-0.5">
                      <!-- Exit Row Indicator -->
                      <div v-if="isExitRow(classId, rowNum)" class="w-3 h-3 bg-red-500 rounded-[1px] flex items-center justify-center shadow-sm">
                        <i class="ph ph-door-open text-white text-[6px]"></i>
                      </div>
                      
                      <!-- Wheelchair Indicator -->
                      <div v-if="isWheelchairSeat(classId, rowNum, colIdx)" class="w-3 h-3 bg-blue-500 rounded-[1px] flex items-center justify-center shadow-sm">
                        <i class="ph ph-wheelchair text-white text-[6px]"></i>
                      </div>
                      
                      <!-- Bassinet Indicator -->
                      <div v-if="isBassinetSeat(classId, rowNum, colIdx)" class="w-3 h-3 bg-purple-500 rounded-[1px] flex items-center justify-center shadow-sm">
                        <i class="ph ph-baby text-white text-[6px]"></i>
                      </div>
                      
                      <!-- Nut Allergy Indicator -->
                      <div v-if="hasNutAllergy(classId, rowNum, colIdx)" class="w-3 h-3 bg-amber-500 rounded-[1px] flex items-center justify-center shadow-sm">
                        <i class="ph ph-nut text-white text-[6px]"></i>
                      </div>
                      
                      <!-- Unaccompanied Minor Indicator -->
                      <div v-if="isUnaccompaniedMinor(classId, rowNum, colIdx)" class="w-3 h-3 bg-green-500 rounded-[1px] flex items-center justify-center shadow-sm">
                        <i class="ph ph-user-focus text-white text-[6px]"></i>
                      </div>
                    </div>
                    
                    <!-- Seat Tooltip -->
                    <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-48 bg-gray-900 text-white text-[10px] rounded-lg p-2 z-50">
                      <div class="space-y-1">
                        <p class="font-bold">{{ getSeatNumber(classId, rowNum, colIdx) }}</p>
                        <p>{{ getSeatClassName(classId) }}</p>
                        
                        <div v-if="hasSpecialSeat(classId, rowNum, colIdx)" class="pt-1 border-t border-gray-700">
                          <p class="font-semibold text-amber-300">Special Requirements:</p>
                          <ul class="pl-2 space-y-0.5">
                            <li v-if="isExitRow(classId, rowNum)" class="flex items-center gap-1">
                              <i class="ph ph-door-open text-red-400"></i>
                              <span>Exit Row</span>
                            </li>
                            <li v-if="isWheelchairSeat(classId, rowNum, colIdx)" class="flex items-center gap-1">
                              <i class="ph ph-wheelchair text-blue-400"></i>
                              <span>Wheelchair Accessible</span>
                            </li>
                            <li v-if="isBassinetSeat(classId, rowNum, colIdx)" class="flex items-center gap-1">
                              <i class="ph ph-baby text-purple-400"></i>
                              <span>Bassinet Position</span>
                            </li>
                            <li v-if="hasNutAllergy(classId, rowNum, colIdx)" class="flex items-center gap-1">
                              <i class="ph ph-nut text-amber-400"></i>
                              <span>Nut Allergy - No Nuts Zone</span>
                            </li>
                            <li v-if="isUnaccompaniedMinor(classId, rowNum, colIdx)" class="flex items-center gap-1">
                              <i class="ph ph-user-focus text-green-400"></i>
                              <span>Unaccompanied Minor</span>
                            </li>
                          </ul>
                        </div>
                        
                        <div v-if="!hasSpecialSeat(classId, rowNum, colIdx)" class="text-gray-400 italic">
                          Standard seat
                        </div>
                      </div>
                    </div>
                  </button>
                </div>

                <!-- Row Number with special indicators -->
                <div class="w-10 h-10 flex items-center justify-center bg-gray-50 border border-gray-200 rounded-[1px] relative group shadow-inner poppins">
                  <span class="text-[11px] font-black text-gray-300">{{ getGlobalRowNumber(classId, rowNum) }}</span>
                  
                  <!-- Row-level indicators -->
                  <div v-if="isExitRow(classId, rowNum)" class="absolute -top-1 -left-1 w-4 h-4 bg-red-500 rounded-[1px] flex items-center justify-center shadow-sm">
                    <i class="ph ph-door-open text-white text-[8px]"></i>
                  </div>
                  
                  <!-- Bulkhead row indicator -->
                  <div v-if="isBulkheadRow(classId, rowNum)" class="absolute -bottom-1 -left-1 w-4 h-4 bg-cyan-500 rounded-[1px] flex items-center justify-center shadow-sm">
                    <i class="ph ph-wall text-white text-[8px]"></i>
                  </div>
                  
                  <!-- Row Tooltip -->
                  <div class="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 hidden group-hover:block w-40 bg-gray-900 text-white text-[10px] rounded-lg p-2 z-50">
                    <p class="font-bold">Row {{ getGlobalRowNumber(classId, rowNum) }}</p>
                    <div class="space-y-1 mt-1">
                      <div v-if="isExitRow(classId, rowNum)" class="flex items-center gap-1 text-red-300">
                        <i class="ph ph-door-open"></i>
                        <span>Emergency Exit Row</span>
                      </div>
                      <div v-if="isBulkheadRow(classId, rowNum)" class="flex items-center gap-1 text-cyan-300">
                        <i class="ph ph-wall"></i>
                        <span>Bulkhead Row (Extra Legroom)</span>
                      </div>
                      <div v-if="hasExtraLegroom(classId, rowNum)" class="flex items-center gap-1 text-emerald-300">
                        <i class="ph ph-ruler"></i>
                        <span>Extra Legroom</span>
                      </div>
                      <div v-if="hasWheelchairSeatsInRow(classId, rowNum)" class="flex items-center gap-1 text-blue-300">
                        <i class="ph ph-wheelchair"></i>
                        <span>Wheelchair positions</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Right Side Seats -->
                <div class="flex gap-2">
                  <button
                    v-for="colIdx in getRightColumns(classId)"
                    :key="`R-${colIdx}`"
                    @click="selectSeat(classId, rowNum, colIdx)"
                    @contextmenu.prevent="showSeatContextMenu($event, classId, rowNum, colIdx)"
                    :class="getSeatStyle(classId, rowNum, colIdx)"
                    :style="getSeatColorStyle(classId, rowNum, colIdx)"
                    class="w-10 h-10 rounded-[1px] border flex items-center justify-center text-[11px] font-bold transition-all hover:scale-105 relative group shadow-sm poppins"
                  >
                    <span>{{ getColumnLabel(colIdx) }}</span>
                    
                    <!-- Special Indicators (same as left side) -->
                    <div v-if="hasSpecialSeat(classId, rowNum, colIdx)" class="absolute -top-1 -right-1 flex flex-col gap-0.5">
                      <div v-if="isExitRow(classId, rowNum)" class="w-3 h-3 bg-red-500 rounded-[1px] flex items-center justify-center shadow-sm">
                        <i class="ph ph-door-open text-white text-[6px]"></i>
                      </div>
                      <div v-if="isWheelchairSeat(classId, rowNum, colIdx)" class="w-3 h-3 bg-blue-500 rounded-[1px] flex items-center justify-center shadow-sm">
                        <i class="ph ph-wheelchair text-white text-[6px]"></i>
                      </div>
                      <div v-if="isBassinetSeat(classId, rowNum, colIdx)" class="w-3 h-3 bg-purple-500 rounded-[1px] flex items-center justify-center shadow-sm">
                        <i class="ph ph-baby text-white text-[6px]"></i>
                      </div>
                      <div v-if="hasNutAllergy(classId, rowNum, colIdx)" class="w-3 h-3 bg-amber-500 rounded-[1px] flex items-center justify-center shadow-sm">
                        <i class="ph ph-nut text-white text-[6px]"></i>
                      </div>
                      <div v-if="isUnaccompaniedMinor(classId, rowNum, colIdx)" class="w-3 h-3 bg-green-500 rounded-[1px] flex items-center justify-center shadow-sm">
                        <i class="ph ph-user-focus text-white text-[6px]"></i>
                      </div>
                    </div>
                  </button>
                </div>
              </div>
            </div>

            <!-- Divider between classes -->
            <div v-if="getClassPosition(classId) < orderedClassIds.length" class="flex items-center justify-center py-6">
              <div class="w-32 h-1 bg-gradient-to-r from-transparent via-gray-300 to-transparent rounded-full"></div>
            </div>
          </div>
        </div>

        <!-- Rear section -->
        <div class="mt-12 pt-8 border-t-2 border-gray-100 text-center relative">
          <!-- Lavatory indicators -->
          <div class="absolute left-8 top-8 flex items-center gap-2 poppins">
            <div class="w-8 h-8 bg-gray-50 border border-gray-200 rounded-[1px] flex items-center justify-center">
              <i class="ph ph-toilet text-gray-400"></i>
            </div>
            <span class="text-[9px] font-bold text-gray-300 uppercase tracking-widest">Lav</span>
          </div>
          
          <div class="absolute right-8 top-8 flex items-center gap-2 poppins">
            <div class="w-8 h-8 bg-gray-50 border border-gray-200 rounded-[1px] flex items-center justify-center">
              <i class="ph ph-toilet text-gray-400"></i>
            </div>
            <span class="text-[9px] font-bold text-gray-300 uppercase tracking-widest">Lav</span>
          </div>
          
          <div class="w-12 h-12 bg-gray-50 border border-gray-200 rounded-[1px] mx-auto mb-3 flex items-center justify-center poppins">
            <i class="ph ph-arrow-down text-gray-300 text-xl"></i>
          </div>
          <span class="text-[9px] font-black text-gray-300 uppercase tracking-[4px] poppins">Aft Galley System</span>
        </div>
      </div>
    </div>

    <!-- Right Panel - Enhanced Seat Details -->
    <div class="w-full lg:w-80 order-3">
      <div class="bg-white rounded-[1px] shadow-sm border border-gray-200 sticky top-10 overflow-hidden poppins">
        <div class="bg-[#002D1E] p-4 text-white">
          <h3 class="text-[10px] font-black uppercase tracking-[3px] flex items-center gap-2 poppins">
            <i class="ph ph-fingerprint text-[#fe3787]"></i>
            Unit Registry
          </h3>
        </div>

        <div class="p-6">
          <div v-if="!activeSeat" class="py-12 text-center">
            <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <i class="ph ph-cursor-click text-gray-400 text-2xl"></i>
            </div>
            <p class="text-sm text-gray-500 font-medium">No Seat Selected</p>
            <p class="text-[11px] text-gray-400 mt-1">Click a seat to view details or right-click to mark special needs.</p>
          </div>

          <div v-else>
            <!-- Seat Header -->
            <div class="text-center mb-6">
              <div 
                class="w-20 h-20 rounded-[1px] mx-auto mb-4 flex items-center justify-center text-3xl font-black text-white shadow-xl relative poppins border-4 border-white"
                :style="{ backgroundColor: activeSeat.color }"
              >
                {{ activeSeat.seat_number }}
                
                <!-- Special Indicator on Seat Display -->
                <div v-if="hasSpecialSeatForActiveSeat" class="absolute -top-2 -right-2 flex flex-col gap-1">
                  <div v-if="activeSeat.is_exit_row" class="w-6 h-6 bg-red-500 rounded-[1px] flex items-center justify-center shadow-md">
                    <i class="ph ph-door-open text-white text-[8px]"></i>
                  </div>
                  <div v-if="activeSeat.is_wheelchair_accessible" class="w-6 h-6 bg-blue-500 rounded-[1px] flex items-center justify-center shadow-md">
                    <i class="ph ph-wheelchair text-white text-[8px]"></i>
                  </div>
                </div>
              </div>
              <h2 class="text-2xl font-black text-[#002D1E] mb-1 poppins tracking-tighter">{{ activeSeat.seat_number }}</h2>
              <p class="text-[11px] font-bold uppercase tracking-widest poppins" :style="{ color: activeSeat.color }">{{ activeSeat.seat_class_name }}</p>
            </div>

            <!-- Special Requirements Section -->
            <div v-if="hasSpecialSeatForActiveSeat" class="mb-6">
              <h4 class="text-xs font-bold text-gray-700 mb-3 flex items-center gap-2">
                <i class="ph ph-warning-circle text-amber-500"></i>
                Special Requirements
              </h4>
              <div class="space-y-2">
                <div v-if="activeSeat.is_exit_row" class="flex items-center gap-3 p-3 bg-red-50 rounded-lg border border-red-200">
                  <div class="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                    <i class="ph ph-door-open text-red-600"></i>
                  </div>
                  <div>
                    <p class="text-sm font-bold text-red-800">Exit Row</p>
                    <p class="text-[11px] text-red-600">Passenger must be capable of assisting in emergency</p>
                  </div>
                </div>
                
                <div v-if="activeSeat.is_wheelchair_accessible" class="flex items-center gap-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    <i class="ph ph-wheelchair text-blue-600"></i>
                  </div>
                  <div>
                    <p class="text-sm font-bold text-blue-800">Wheelchair Accessible</p>
                    <p class="text-[11px] text-blue-600">Priority for passengers with reduced mobility</p>
                  </div>
                </div>
                
                <div v-if="activeSeat.has_bassinet" class="flex items-center gap-3 p-3 bg-purple-50 rounded-lg border border-purple-200">
                  <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                    <i class="ph ph-baby text-purple-600"></i>
                  </div>
                  <div>
                    <p class="text-sm font-bold text-purple-800">Bassinet Position</p>
                    <p class="text-[11px] text-purple-600">For passengers with infants (bulkhead rows)</p>
                  </div>
                </div>
                
                <div v-if="activeSeat.has_nut_allergy" class="flex items-center gap-3 p-3 bg-amber-50 rounded-lg border border-amber-200">
                  <div class="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center">
                    <i class="ph ph-nut text-amber-600"></i>
                  </div>
                  <div>
                    <p class="text-sm font-bold text-amber-800">Nut Allergy Zone</p>
                    <p class="text-[11px] text-amber-600">No nuts to be served in this area</p>
                  </div>
                </div>
                
                <div v-if="activeSeat.is_unaccompanied_minor" class="flex items-center gap-3 p-3 bg-green-50 rounded-lg border border-green-200">
                  <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                    <i class="ph ph-user-focus text-green-600"></i>
                  </div>
                  <div>
                    <p class="text-sm font-bold text-green-800">Unaccompanied Minor</p>
                    <p class="text-[11px] text-green-600">Special supervision required</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Basic Seat Info -->
            <div class="space-y-3 mb-6">
              <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span class="text-[11px] text-gray-500 uppercase font-medium">Price Multiplier</span>
                <span class="text-lg font-black text-[#fe3787]">x{{ activeSeat.price_multiplier }}</span>
              </div>
              
              <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span class="text-[11px] text-gray-500 uppercase font-medium">Status</span>
                <span :class="[
                  'px-2 py-1 rounded-full text-[10px] font-bold uppercase',
                  activeSeat.is_available ? 'bg-emerald-100 text-emerald-700' : (activeSeat.is_booked ? 'bg-indigo-100 text-indigo-700' : 'bg-red-100 text-red-700')
                ]">
                  {{ activeSeat.is_available ? 'Available' : (activeSeat.is_booked ? 'Booked' : 'Blocked') }}
                </span>
              </div>

              <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span class="text-[11px] text-gray-500 uppercase font-medium">Row</span>
                <span class="text-sm font-bold text-gray-700">{{ activeSeat.row }}</span>
              </div>

              <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span class="text-[11px] text-gray-500 uppercase font-medium">Column</span>
                <span class="text-sm font-bold text-gray-700">{{ activeSeat.column }}</span>
              </div>
              
              <!-- Seat Features -->
              <div v-if="activeSeat.features && activeSeat.features.length > 0" class="p-3 bg-gray-50 rounded-lg">
                <p class="text-[11px] text-gray-500 uppercase font-medium mb-2">Seat Features</p>
                <div class="flex flex-wrap gap-1">
                  <span v-for="feature in activeSeat.features" :key="feature" class="px-2 py-1 bg-white text-[10px] font-medium rounded-full border">
                    {{ feature }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="space-y-3">
              <button 
                @click="toggleAvailability" 
                :class="[
                  'w-full py-4 rounded-[1px] font-black text-[11px] uppercase tracking-[2px] transition-all flex items-center justify-center gap-2 poppins shadow-sm',
                  activeSeat.is_available 
                    ? 'bg-red-500 hover:bg-red-600 text-white' 
                    : 'bg-emerald-500 hover:bg-emerald-600 text-white'
                ]"
              >
                <i :class="activeSeat.is_available ? 'ph ph-prohibit' : 'ph ph-check-circle'"></i>
                {{ activeSeat.is_available ? 'Block Unit' : (activeSeat.is_booked ? 'Reserved' : 'Release Unit') }}
              </button>
              
              <button 
                @click="showSpecialRequirementsModal = true"
                class="w-full py-4 bg-white border border-gray-200 hover:border-[#fe3787] text-gray-700 font-black text-[11px] uppercase tracking-[2px] rounded-[1px] flex items-center justify-center gap-2 poppins transition-all"
              >
                <i class="ph ph-sliders"></i>
                Special Config
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Seat Class Modal -->
    <div v-if="isClassModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-md rounded-[1px] shadow-2xl overflow-hidden poppins">
        <div class="bg-[#002D1E] p-4 text-white flex items-center justify-between">
          <h2 class="text-sm font-bold uppercase tracking-widest poppins">{{ isEditingClass ? 'Modify Class' : 'Register Class' }}</h2>
          <button @click="isClassModalOpen = false" class="text-white/70 hover:text-white">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        <form @submit.prevent="saveSeatClass" class="p-6 space-y-4">
          <div>
            <label for="class-name" class="block text-xs font-bold text-gray-500 uppercase mb-2 poppins">Label</label>
            <input id="class-name" name="className" v-model="classForm.name" type="text" class="w-full border border-gray-200 p-3 rounded-[1px] outline-none focus:border-[#fe3787] poppins text-sm" placeholder="e.g. Business Class" required>
          </div>
          <div>
            <label for="class-multiplier" class="block text-xs font-bold text-gray-500 uppercase mb-2 poppins">Multiplier Rate</label>
            <input id="class-multiplier" name="multiplier" v-model="classForm.price_multiplier" type="number" step="0.01" min="0.1" class="w-full border border-gray-200 p-3 rounded-[1px] outline-none focus:border-[#fe3787] poppins text-sm" required>
          </div>
          <div>
            <label for="class-color" class="block text-xs font-bold text-gray-500 uppercase mb-2 poppins">Ident Color</label>
            <div class="flex gap-3">
              <input id="class-color" name="color" v-model="classForm.color" type="color" class="w-16 h-12 rounded-[1px] border border-gray-200 cursor-pointer p-1 bg-white">
              <input v-model="classForm.color" type="text" class="flex-1 border border-gray-200 p-3 rounded-[1px] outline-none focus:border-[#fe3787] font-mono text-sm uppercase poppins">
            </div>
          </div>
          
          <!-- Airline Selection (show if invalid airline or editing) -->
          <div v-if="!isValidAirline(aircraftInfo.airline_id) || isEditingClass">
            <label for="class-airline" class="block text-xs font-bold text-gray-500 uppercase mb-2">
              Airline <span class="text-red-500">*</span>
            </label>
            <select 
              id="class-airline" 
              v-model="classForm.airline" 
              class="w-full border border-gray-300 p-3 rounded-lg outline-none focus:border-[#fe3787]"
              required
            >
              <option value="">Select an airline...</option>
              <option v-for="airline in airlines" :key="airline.id" :value="airline.id">
                {{ airline.name }} ({{ airline.code }}) - ID: {{ airline.id }}
              </option>
            </select>
            <p v-if="airlines.length === 0" class="text-[10px] text-red-500 mt-1">
              No airlines available. Please create an airline first.
            </p>
          </div>

          <div class="flex justify-end gap-3 mt-8">
            <button type="button" @click="isClassModalOpen = false" class="px-6 py-2.5 text-gray-500 font-bold text-[11px] uppercase tracking-widest hover:bg-gray-50 rounded-[1px] poppins transition-all">Cancel</button>
            <button 
              type="submit" 
              class="px-6 py-2.5 bg-[#fe3787] text-white font-black text-[11px] uppercase tracking-widest rounded-[1px] poppins hover:bg-[#fb1873] shadow-lg transition-all"
              :disabled="!isEditingClass && !isValidAirline(aircraftInfo.airline_id) && !classForm.airline"
            >
              Commit Changes
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Create Airline Modal -->
    <div v-if="showCreateAirlineModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-md rounded-[1px] shadow-2xl overflow-hidden poppins">
        <div class="bg-[#002D1E] p-4 text-white flex items-center justify-between">
          <h2 class="text-sm font-bold uppercase tracking-widest poppins">New Airline Entity</h2>
          <button @click="showCreateAirlineModal = false" class="text-white/70 hover:text-white">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        <form @submit.prevent="createAirline" class="p-6 space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Airline Name</label>
            <input v-model="airlineForm.name" type="text" class="w-full border border-gray-300 p-3 rounded-lg outline-none focus:border-[#fe3787]" placeholder="e.g. Philippine Airlines" required>
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Airline Code</label>
            <input v-model="airlineForm.code" type="text" class="w-full border border-gray-300 p-3 rounded-lg outline-none focus:border-[#fe3787]" placeholder="e.g. PAL" maxlength="10" required>
          </div>
          <div class="bg-amber-50 border border-amber-200 rounded-lg p-3">
            <p class="text-[11px] text-amber-800">
              <i class="ph ph-info mr-1"></i>
              This will create a new airline. You'll then need to assign it to fix the broken reference.
            </p>
          </div>
          <div class="flex justify-end gap-3 mt-8">
            <button type="button" @click="showCreateAirlineModal = false" class="px-6 py-2.5 text-gray-500 font-bold text-[11px] uppercase tracking-widest hover:bg-gray-50 rounded-[1px] poppins transition-all">Dismiss</button>
            <button 
              type="submit" 
              class="px-6 py-2.5 bg-[#fe3787] text-white font-black text-[11px] uppercase tracking-widest rounded-[1px] poppins hover:bg-[#fb1873] shadow-lg transition-all"
              :disabled="isCreatingAirline"
            >
              <i v-if="isCreatingAirline" class="ph ph-spinner animate-spin mr-1"></i>
              {{ isCreatingAirline ? 'Processing...' : 'Register Airline' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Context Menu for Special Requirements -->
    <div v-if="showContextMenu" 
         :style="{ top: contextMenuY + 'px', left: contextMenuX + 'px' }"
         class="fixed z-50 w-56 bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden">
      <div class="bg-gray-900 text-white p-3">
        <p class="font-bold text-sm">Seat {{ contextMenuSeat?.seat_number }}</p>
        <p class="text-[10px] text-gray-300">{{ contextMenuSeat?.seat_class_name }}</p>
      </div>
      
      <div class="p-2 space-y-1">
        <button 
          v-for="req in seatRequirements"
          :key="req.id"
          @click="toggleRequirement(req)"
          :class="['w-full text-left px-3 py-2.5 rounded-lg text-sm flex items-center gap-3', 
                   hasRequirement(contextMenuSeat, req.code) ? 'bg-blue-50 text-blue-700' : 'hover:bg-gray-100 text-gray-700']"
        >
          <div :class="['w-6 h-6 rounded-full flex items-center justify-center', 
                       hasRequirement(contextMenuSeat, req.code) ? 'bg-blue-500' : 'bg-gray-200']">
            <i :class="[req.icon || 'ph ph-star', 'text-white text-xs']"></i>
          </div>
          <span>{{ hasRequirement(contextMenuSeat, req.code) ? 'Remove ' + req.name : 'Mark as ' + req.name }}</span>
        </button>
        
        <div class="border-t border-gray-200 pt-1">
          <button 
            @click="clearSpecialRequirements"
            class="w-full text-left px-3 py-2.5 rounded-lg text-sm flex items-center gap-3 text-red-600 hover:bg-red-50"
          >
            <div class="w-6 h-6 rounded-full bg-red-100 flex items-center justify-center">
              <i class="ph ph-trash text-red-600 text-xs"></i>
            </div>
            <span>Clear All Special Markings</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Special Requirements Modal -->
    <div v-if="showSpecialRequirementsModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-md rounded-[1px] shadow-2xl overflow-hidden poppins">
        <div class="bg-[#002D1E] p-4 text-white flex items-center justify-between">
          <h2 class="text-sm font-bold uppercase tracking-widest poppins">Unit Configuration</h2>
          <button @click="showSpecialRequirementsModal = false" class="text-white/70 hover:text-white">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <div class="p-6">
          <div class="mb-6">
            <h3 class="text-sm font-bold text-gray-700 mb-2">Seat {{ activeSeat?.seat_number }}</h3>
            <p class="text-[11px] text-gray-500">{{ activeSeat?.seat_class_name }}</p>
          </div>
          
          <div class="space-y-4">
            <!-- Dynamic Requirements -->
            <div v-for="req in seatRequirements" :key="req.id" class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div :class="['w-10 h-10 rounded-lg flex items-center justify-center', hasRequirement(activeSeat, req.code) ? 'bg-blue-100' : 'bg-gray-100']">
                  <i :class="[req.icon || 'ph ph-star', hasRequirement(activeSeat, req.code) ? 'text-blue-600' : 'text-gray-400']"></i>
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-800">{{ req.name }}</p>
                  <p class="text-[10px] text-blue-600 font-bold" v-if="req.price > 0">+ ₱{{ req.price }}</p>
                  <p class="text-[10px] text-gray-500">{{ req.description }}</p>
                </div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" 
                       :value="req.id" 
                       v-model="activeSeat.requirements" 
                       @change="updateSeatSpecialFeatures" 
                       class="sr-only peer">
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
              </label>
            </div>

          </div>
          
          <div class="mt-8 flex justify-end gap-3">
            <button @click="showSpecialRequirementsModal = false" class="px-6 py-2.5 text-gray-500 font-bold text-[11px] uppercase tracking-widest hover:bg-gray-50 rounded-[1px] poppins transition-all">Close</button>
            <button @click="saveSpecialRequirements" class="px-6 py-2.5 bg-[#fe3787] text-white font-black text-[11px] uppercase tracking-widest rounded-[1px] poppins hover:bg-[#fb1873] shadow-lg transition-all">Save Matrix</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import api from '@/services/admin/api';
import { useModalStore } from '@/stores/modal';

const modalStore = useModalStore();

// ----- State -----
const debugMode = ref(false);
const isLoading = ref(false);
const hasError = ref(false);
const errorMessage = ref('');
const schedules = ref([]);
const seats = ref([]);
const seatClasses = ref([]);
const airlines = ref([]);
const aircraftInfo = ref({ name: '', capacity: 0, airline_id: null });
const rawApiData = ref(null);
const selectedScheduleId = ref('');
const activeSeat = ref(null);
const isClassModalOpen = ref(false);
const isEditingClass = ref(false);
const currentClassId = ref(null);
const classForm = ref({ name: '', price_multiplier: 1.00, color: '#3B82F6', airline: null });
const isSaving = ref(false);
const hasExistingLayout = ref(false);
const showCreateAirlineModal = ref(false);
const isCreatingAirline = ref(false);
const airlineForm = ref({ name: '', code: '' });
const selectedFixAirlineId = ref(null);
const saveMode = ref('schedule'); // 'schedule' or 'aircraft'
const seatRequirements = ref([]); 

// Special seat features state
const showContextMenu = ref(false);
const contextMenuX = ref(0);
const contextMenuY = ref(0);
const contextMenuSeat = ref(null);
const showSpecialRequirementsModal = ref(false);

const layoutConfig = ref({});
const classOrder = ref([]);

const columnLabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'];
const defaultColors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

// ----- Computed -----
const currentAirlineName = computed(() => {
  if (!aircraftInfo.value.airline_id) return 'Unknown';
  const airline = airlines.value.find(a => a.id === aircraftInfo.value.airline_id);
  return airline?.name || `ID: ${aircraftInfo.value.airline_id} (Not Found)`;
});

const seatClassesForAirline = computed(() => {
  if (!aircraftInfo.value.airline_id) return [];
  
  const airlineId = aircraftInfo.value.airline_id;
  
  return seatClasses.value.filter(sc => {
    let scAirlineId = sc.airline;
    if (typeof sc.airline === 'object' && sc.airline !== null) {
      scAirlineId = sc.airline.id;
    }
    
    return scAirlineId === airlineId || scAirlineId === null || scAirlineId === undefined;
  });
});

const orderedAirlineSeatClasses = computed(() => {
  const classes = [...seatClassesForAirline.value];
  
  classes.sort((a, b) => {
    const indexA = classOrder.value.indexOf(a.id);
    const indexB = classOrder.value.indexOf(b.id);
    
    if (indexA !== -1 && indexB !== -1) return indexA - indexB;
    if (indexA !== -1) return -1;
    if (indexB !== -1) return 1;
    
    return b.price_multiplier - a.price_multiplier;
  });
  
  return classes;
});

const orderedClassIds = computed(() => {
  // Only include class IDs that exist in both layoutConfig AND seatClasses
  return classOrder.value.filter(id => {
    const existsInLayout = layoutConfig.value[id];
    const existsInSeatClasses = seatClasses.value.some(sc => sc.id === id);
    return existsInLayout && existsInSeatClasses;
  });
});

const totalConfiguredSeats = computed(() => {
  return Object.values(layoutConfig.value).reduce((sum, config) => {
    return sum + ((config?.rows || 0) * (config?.columns || 0));
  }, 0);
});

const hasValidLayout = computed(() => {
  return orderedClassIds.value.length > 0 && 
         orderedClassIds.value.every(id => {
           const config = layoutConfig.value[id];
           return config && typeof config.rows === 'number' && config.rows > 0;
         });
});

const hasSpecialSeatForActiveSeat = computed(() => {
  if (!activeSeat.value) return false;
  return activeSeat.value.is_exit_row || 
         activeSeat.value.is_wheelchair_accessible || 
         activeSeat.value.has_bassinet || 
         activeSeat.value.has_nut_allergy || 
         activeSeat.value.is_unaccompanied_minor;
});

const exitRowSeatsCount = computed(() => {
  return Array.from(seatMapData.value.values()).filter(s => s.is_exit_row).length;
});

const wheelchairSeatsCount = computed(() => {
  return Array.from(seatMapData.value.values()).filter(s => s.is_wheelchair_accessible).length;
});

const bassinetSeatsCount = computed(() => {
  return Array.from(seatMapData.value.values()).filter(s => s.has_bassinet).length;
});

const nutAllergySeatsCount = computed(() => {
  return Array.from(seatMapData.value.values()).filter(s => s.has_nut_allergy).length;
});

const unaccompaniedMinorSeatsCount = computed(() => {
  return Array.from(seatMapData.value.values()).filter(s => s.is_unaccompanied_minor).length;
});

const specialSeatsCount = computed(() => {
  return exitRowSeatsCount.value + wheelchairSeatsCount.value + bassinetSeatsCount.value + 
         nutAllergySeatsCount.value + unaccompaniedMinorSeatsCount.value;
});

const occupiedCount = computed(() => 
  Array.from(seatMapData.value.values()).filter(s => !s.is_available).length
);

const availableCount = computed(() => 
  Array.from(seatMapData.value.values()).filter(s => s.is_available).length
);

const capacityMismatch = computed(() => {
  if (!aircraftInfo.value.capacity) return false;
  return totalConfiguredSeats.value !== aircraftInfo.value.capacity;
});

const capacityStatus = computed(() => {
  if (!aircraftInfo.value.capacity) return 'unknown';
  if (totalConfiguredSeats.value === aircraftInfo.value.capacity) return 'exact';
  if (totalConfiguredSeats.value < aircraftInfo.value.capacity) return 'under';
  return 'over';
});

// ----- Methods -----
const isValidAirline = (airlineId) => {
  if (!airlineId) return false;
  
  const found = airlines.value.some(a => a.id === parseInt(airlineId));
  if (found) return true;
  
  if (aircraftInfo.value.airline && aircraftInfo.value.airline.id === parseInt(airlineId)) {
    return true;
  }
  
  return false;
};

const handleScheduleChange = async () => {
  if (!selectedScheduleId.value) {
    resetState();
    return;
  }

  isLoading.value = true;
  hasError.value = false;
  errorMessage.value = '';
  
  try {
    if (airlines.value.length === 0) {
      await fetchAirlines();
    }

    const schedRes = await api.get(`/schedules/${selectedScheduleId.value}/?depth=2`);
    rawApiData.value = schedRes.data;

    const data = schedRes.data;
    
    let aircraftData = null;
    let airlineData = null;
    
    if (data.flight_detail) {
      aircraftData = data.flight_detail.aircraft;
      airlineData = data.flight_detail.airline;
    } else if (data.flight) {
      if (typeof data.flight === 'object') {
        aircraftData = data.flight.aircraft;
        airlineData = data.flight.airline;
      }
    }
    
    if (!aircraftData && data.flight) {
      const flightId = typeof data.flight === 'object' ? data.flight.id : data.flight;
      try {
        const flightRes = await api.get(`/flights/${flightId}/`);
        aircraftData = flightRes.data.aircraft;
        if (typeof aircraftData === 'number') {
          const aircraftRes = await api.get(`/aircraft/${aircraftData}/`);
          aircraftData = aircraftRes.data;
        }
      } catch (e) {
        console.error('Failed to fetch flight details:', e);
      }
    }
    
    if (aircraftData && typeof aircraftData === 'number') {
      try {
        const aircraftRes = await api.get(`/aircraft/${aircraftData}/`);
        aircraftData = aircraftRes.data;
      } catch (e) {
        console.error('Failed to fetch aircraft:', e);
      }
    }
    
    let airlineId = null;
    if (airlineData) {
      airlineId = typeof airlineData === 'object' ? airlineData.id : airlineData;
    } else if (aircraftData?.airline) {
      airlineId = typeof aircraftData.airline === 'object' ? aircraftData.airline.id : aircraftData.airline;
    }
    
    aircraftInfo.value = {
      name: data.aircraft_name || aircraftData?.model || 'Unknown Aircraft',
      capacity: data.aircraft_capacity || aircraftData?.capacity || 150,
      airline_id: airlineId,
      aircraft: aircraftData,
      airline: airlineData,
      aircraft_id: aircraftData?.id,
      flight_id: typeof data.flight === 'object' ? data.flight.id : data.flight
    };
    
    if (!aircraftInfo.value.aircraft) {
      aircraftInfo.value.aircraft = {
        id: aircraftData?.id || data.flight?.aircraft,
        model: aircraftInfo.value.name,
        capacity: aircraftInfo.value.capacity,
        airline: airlineId
      };
    }

    const seatRes = await api.get(`/seats/?schedule=${selectedScheduleId.value}`);
    seats.value = seatRes.data.results || seatRes.data || [];

    if (seats.value.length > 0) {
      hasExistingLayout.value = true;
      loadLayoutFromSeats(seats.value);
    } else {
      hasExistingLayout.value = false;
      layoutConfig.value = {};
      classOrder.value = [];
      
      if (aircraftInfo.value.aircraft?.id) {
        await applyAircraftTemplate(aircraftInfo.value.aircraft.id);
      }
    }

  } catch (err) {
    console.error('Error in handleScheduleChange:', err);
    hasError.value = true;
    errorMessage.value = err.message || 'Failed to load schedule data';
  } finally {
    isLoading.value = false;
  }
};

const fetchAirlines = async () => {
  try {
    const response = await api.get('/airlines/');
    airlines.value = response.data.results || response.data || [];
  } catch (err) {
    console.error('Error fetching airlines:', err);
  }
};

const useFirstAirline = () => {
  if (airlines.value.length > 0) {
    const firstAirline = airlines.value[0];
    aircraftInfo.value.airline_id = firstAirline.id;
    
    if (seatClassesForAirline.value.length > 0) {
      autoPopulateLayout();
    }
  } else {
    alert('No airlines available. Please create an airline first.');
    showCreateAirlineModal.value = true;
  }
};

const fixAirlineReference = async (newAirlineId) => {
  if (!newAirlineId) {
    alert('Please select a valid airline');
    return;
  }

  const confirmed = await modalStore.confirm({
    title: 'Update Airline Reference?',
    message: `This will attempt to update the aircraft to use Airline ID ${newAirlineId}. Continue?`,
    variant: 'danger',
    confirmText: 'Update',
    loadingText: 'Updating...'
  });

  if (!confirmed) {
    return;
  }

  try {
    aircraftInfo.value.airline_id = parseInt(newAirlineId);
    
    alert(`Airline reference updated to ID ${newAirlineId}. You can now create seat classes.`);
  } catch (err) {
    console.error('Error fixing airline reference:', err);
    alert('Failed to fix airline reference: ' + err.message);
  }
};

const createAirline = async () => {
  if (!airlineForm.value.name || !airlineForm.value.code) {
    alert('Please fill in all fields');
    return;
  }

  isCreatingAirline.value = true;
  
  try {
    const response = await api.post('/airlines/', {
      name: airlineForm.value.name,
      code: airlineForm.value.code.toUpperCase()
    });
    
    const newAirline = response.data;
    airlines.value.push(newAirline);
    
    showCreateAirlineModal.value = false;
    airlineForm.value = { name: '', code: '' };
    
    alert(`Airline "${newAirline.name}" created successfully!`);
    
    await fetchSeatClasses();
    
  } catch (err) {
    console.error('Error creating airline:', err);
    alert('Failed to create airline: ' + JSON.stringify(err.response?.data || err.message));
  } finally {
    isCreatingAirline.value = false;
  }
};

const fetchSeatClasses = async () => {
  try {
    const response = await api.get('/seat-classes/');
    seatClasses.value = (response.data.results || response.data || []).map((sc, index) => ({
      ...sc,
      color: sc.color || defaultColors[index % defaultColors.length]
    }));
  } catch (err) {
    console.error('Error fetching seat classes:', err);
  }
};

const resetState = () => {
  seats.value = [];
  activeSeat.value = null;
  layoutConfig.value = {};
  classOrder.value = [];
  aircraftInfo.value = { name: '', capacity: 0, airline_id: null };
  hasExistingLayout.value = false;
  rawApiData.value = null;
  selectedFixAirlineId.value = null;
  hasError.value = false;
  errorMessage.value = '';
  isLoading.value = false;
};

const autoPopulateLayout = () => {
  const classes = seatClassesForAirline.value;
  if (classes.length === 0) {
    alert('No seat classes available. Please create seat classes first.');
    return;
  }

  const sortedClasses = [...classes].sort((a, b) => b.price_multiplier - a.price_multiplier);
  
  const newLayoutConfig = {};
  const newClassOrder = [];

  const capacity = aircraftInfo.value.capacity || 150;
  const totalClasses = sortedClasses.length;
  
  const baseSeatsPerClass = Math.floor(capacity / totalClasses);
  const remainderSeats = capacity % totalClasses;
  
  let currentRow = 1;

  sortedClasses.forEach((sc, index) => {
    const classCapacity = baseSeatsPerClass + (index < remainderSeats ? 1 : 0);
    
    let columns;
    if (index === 0 && totalClasses > 1) {
      columns = 4;
    } else if (index === 1 && totalClasses > 2) {
      columns = 6;
    } else {
      columns = 6;
    }
    
    const rows = Math.ceil(classCapacity / columns);
    
    newLayoutConfig[sc.id] = {
      rows: rows,
      columns: columns,
      startRow: currentRow,
      airline: aircraftInfo.value.airline_id
    };
    
    newClassOrder.push(sc.id);
    currentRow += rows;
  });
  
  layoutConfig.value = newLayoutConfig;
  classOrder.value = newClassOrder;
};

const autoGenerateLayout = () => {
  autoPopulateLayout();
  hasExistingLayout.value = true;
};

const loadLayoutFromSeats = (fetchedSeats) => {
  if (!fetchedSeats || fetchedSeats.length === 0) {
    hasExistingLayout.value = false;
    layoutConfig.value = {};
    classOrder.value = [];
    return;
  }

  const seatsByClass = {};
  
  fetchedSeats.forEach(seat => {
    const classId = seat.seat_class;
    if (!seatsByClass[classId]) seatsByClass[classId] = [];
    seatsByClass[classId].push(seat);
  });

  const newLayoutConfig = {};
  const newClassOrder = [];

  Object.keys(seatsByClass).forEach(classId => {
    const classSeats = seatsByClass[classId];
    if (!classSeats || classSeats.length === 0) return;
    
    const numericClassId = parseInt(classId);
    if (isNaN(numericClassId)) return;
    
    const maxRow = Math.max(...classSeats.map(s => s.row || 1));
    const minRow = Math.min(...classSeats.map(s => s.row || 1));
    const rows = maxRow - minRow + 1;
    
    const cols = Math.max(...classSeats.map(s => {
      const col = s.column;
      return typeof col === 'string' ? col.charCodeAt(0) - 64 : parseInt(col) || 1;
    }));

    newLayoutConfig[numericClassId] = {
      rows: rows || 1,
      columns: cols || 6,
      airline: aircraftInfo.value.airline_id
    };
    
    newClassOrder.push(numericClassId);
  });

  if (newClassOrder.length > 0) {
    newClassOrder.sort((a, b) => {
      const minRowA = Math.min(...seatsByClass[a].map(s => s.row || 1));
      const minRowB = Math.min(...seatsByClass[b].map(s => s.row || 1));
      return minRowA - minRowB;
    });
  }

  layoutConfig.value = newLayoutConfig;
  classOrder.value = newClassOrder;
  hasExistingLayout.value = newClassOrder.length > 0;
};

const getLayoutSeatCount = (classId) => {
  const config = layoutConfig.value[classId];
  return config ? (config.rows || 0) * (config.columns || 0) : 0;
};

const updateLayout = () => {
  layoutConfig.value = { ...layoutConfig.value };
};

// ----- Seat Class CRUD -----
const saveSeatClass = async () => {
  try {
    const payload = { ...classForm.value };
    
    let targetAirlineId = null;
    
    if (isEditingClass.value) {
      targetAirlineId = payload.airline || aircraftInfo.value.airline_id;
    } else {
      if (isValidAirline(aircraftInfo.value.airline_id)) {
        targetAirlineId = aircraftInfo.value.airline_id;
      } else {
        targetAirlineId = payload.airline;
      }
      
      if (!isValidAirline(targetAirlineId) && airlines.value.length > 0) {
        targetAirlineId = airlines.value[0].id;
      }
    }

    if (!isValidAirline(targetAirlineId)) {
      alert('Please select a valid airline. No valid airline found.');
      return;
    }

    payload.airline = parseInt(targetAirlineId);

    if (isEditingClass.value) {
      await api.put(`/seat-classes/${currentClassId.value}/`, payload);
      const idx = seatClasses.value.findIndex(sc => sc.id === currentClassId.value);
      if (idx !== -1) seatClasses.value[idx] = { ...seatClasses.value[idx], ...payload };
    } else {
      const response = await api.post('/seat-classes/', payload);
      const newClass = {
        ...response.data,
        color: response.data.color || defaultColors[seatClasses.value.length % defaultColors.length]
      };
      seatClasses.value.push(newClass);
      
      if (isValidAirline(aircraftInfo.value.airline_id) && selectedScheduleId.value) {
        layoutConfig.value[newClass.id] = {
          rows: 5,
          columns: 6,
          airline: aircraftInfo.value.airline_id
        };
        classOrder.value.push(newClass.id);
        layoutConfig.value = { ...layoutConfig.value };
      }
    }

    isClassModalOpen.value = false;
    classForm.value = { name: '', price_multiplier: 1.00, color: '#3B82F6', airline: null };
  } catch (err) {
    console.error('Save seat class error:', err);
    const errorMsg = err.response?.data?.airline?.[0] || err.response?.data?.detail || err.message;
    alert('Error: ' + JSON.stringify(err.response?.data || errorMsg));
  }
};

const deleteSeatClass = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Delete Seat Class?',
    message: 'Are you sure you want to delete this seat class? This will also remove its layout configuration.',
    variant: 'danger',
    confirmText: 'Delete',
    loadingText: 'Deleting...'
  });

  if (!confirmed) return;
  
  try {
    await api.delete(`/seat-classes/${id}/`);
    
    // IMPORTANT: Remove all references to this class ID
    delete layoutConfig.value[id];
    classOrder.value = classOrder.value.filter(cid => cid !== id);
    seatClasses.value = seatClasses.value.filter(sc => sc.id !== id);
    
    // Reset active seat if it belongs to deleted class
    if (activeSeat.value && activeSeat.value.seat_class === id) {
      activeSeat.value = null;
    }
    
    // Force reactivity update
    layoutConfig.value = { ...layoutConfig.value };
    
    // Optional: Reset if no seat classes left
    if (seatClassesForAirline.value.length === 0) {
      hasExistingLayout.value = false;
      layoutConfig.value = {};
      classOrder.value = [];
    }
    
    console.log(`Seat class ${id} deleted and removed from layout`);
    
  } catch (err) {
    console.error('Error deleting seat class:', err);
    alert('Error deleting seat class: ' + (err.response?.data?.detail || err.message));
  }
};

const openClassModal = (sc = null) => {
  isEditingClass.value = !!sc;
  currentClassId.value = sc?.id || null;

  const usedColors = seatClasses.value.map(c => c.color);
  const availableColor = defaultColors.find(c => !usedColors.includes(c)) || '#3B82F6';

  if (sc) {
    let airlineId = sc.airline;
    if (typeof sc.airline === 'object' && sc.airline !== null) {
      airlineId = sc.airline.id;
    }
    classForm.value = { 
      name: sc.name, 
      price_multiplier: sc.price_multiplier, 
      color: sc.color || availableColor,
      airline: airlineId
    };
  } else {
    const validAirlineId = isValidAirline(aircraftInfo.value.airline_id) ? aircraftInfo.value.airline_id : null;
    classForm.value = { 
      name: '', 
      price_multiplier: 1.0, 
      color: availableColor,
      airline: validAirlineId || (airlines.value[0]?.id || null)
    };
  }

  isClassModalOpen.value = true;
};

const updateSeatClassColor = async (sc) => {
  try {
    await api.patch(`/seat-classes/${sc.id}/`, { color: sc.color });
  } catch (err) {
    console.error('Error updating color:', err);
  }
};

// ----- Drag & Drop -----
const draggedClassId = ref(null);
const dragOverClassId = ref(null);

const handleDragStart = (event, classId) => {
  draggedClassId.value = classId;
  event.dataTransfer.setData('text/plain', classId);
};

const handleDragEnd = () => {
  draggedClassId.value = null;
  dragOverClassId.value = null;
};

const handleDragOver = (event, classId) => {
  if (draggedClassId.value && draggedClassId.value !== classId) {
    dragOverClassId.value = classId;
  }
};

const handleDrop = (event, targetClassId) => {
  event.preventDefault();
  dragOverClassId.value = null;
  
  if (!draggedClassId.value || draggedClassId.value === targetClassId) return;

  const fromIndex = classOrder.value.indexOf(draggedClassId.value);
  const toIndex = classOrder.value.indexOf(targetClassId);
  
  if (fromIndex !== -1 && toIndex !== -1) {
    const newOrder = [...classOrder.value];
    newOrder.splice(fromIndex, 1);
    newOrder.splice(toIndex, 0, draggedClassId.value);
    classOrder.value = newOrder;
  }
  
  draggedClassId.value = null;
};

// ----- Seat Map Helpers -----
const getSeatClassName = (classId) => {
  const sc = seatClasses.value.find(c => c.id === parseInt(classId));
  return sc?.name || 'Unknown';
};

const getSeatClassMultiplier = (classId) => {
  const sc = seatClasses.value.find(c => c.id === parseInt(classId));
  return sc?.price_multiplier || 1.0;
};

const getSeatClassColor = (classId) => {
  const sc = seatClasses.value.find(c => c.id === parseInt(classId));
  return sc?.color || '#3B82F6';
};

const getColumnLabel = (index) => columnLabels[index - 1] || '?';

const getLeftColumns = (classId) => {
  const cols = layoutConfig.value[classId]?.columns || 6;
  const half = Math.ceil(cols / 2);
  return Array.from({ length: half }, (_, i) => i + 1);
};

const getRightColumns = (classId) => {
  const cols = layoutConfig.value[classId]?.columns || 6;
  const half = Math.ceil(cols / 2);
  return Array.from({ length: cols - half }, (_, i) => half + i + 1);
};

const getGlobalRowNumber = (classId, localRow) => {
  const currentIndex = orderedClassIds.value.indexOf(parseInt(classId));
  if (currentIndex === -1) return localRow;
  
  let offset = 0;
  
  for (let i = 0; i < currentIndex; i++) {
    const prevId = orderedClassIds.value[i];
    const prevConfig = layoutConfig.value[prevId];
    if (prevConfig && prevConfig.rows) {
      offset += prevConfig.rows;
    }
  }
  
  return offset + localRow;
};

const getClassPosition = (classId) => {
  return orderedClassIds.value.indexOf(parseInt(classId)) + 1;
};

// ----- Seat Data -----
const seatMapData = computed(() => {
  const map = new Map();
  
  seats.value.forEach(seat => {
    const key = `${seat.seat_class}-${seat.row}-${seat.column}`;
    // FIX: Ensure all special fields exist on seat object
    const seatWithDefaults = {
      is_exit_row: seat.is_exit_row || false,
      is_wheelchair_accessible: seat.is_wheelchair_accessible || false,
      has_bassinet: seat.has_bassinet || false,
      has_nut_allergy: seat.has_nut_allergy || false,
      is_unaccompanied_minor: seat.is_unaccompanied_minor || false,
      has_extra_legroom: seat.has_extra_legroom || false,
      is_bulkhead: seat.is_bulkhead || false,
      is_window: seat.is_window || false,
      is_aisle: seat.is_aisle || false,
      is_booked: seat.is_booked || false,
      ...seat,
      isExisting: true,
      seat_class_id: seat.seat_class,
      seat_class_name: getSeatClassName(seat.seat_class),
      color: getSeatClassColor(seat.seat_class),
      price_multiplier: getSeatClassMultiplier(seat.seat_class)
    };
    map.set(key, seatWithDefaults);
  });
  
  orderedClassIds.value.forEach(classId => {
    const config = layoutConfig.value[classId];
    if (!config || !config.rows || !config.columns) return;
    
    for (let row = 1; row <= config.rows; row++) {
      for (let col = 1; col <= config.columns; col++) {
        const colLetter = getColumnLabel(col);
        const globalRow = getGlobalRowNumber(classId, row);
        const key = `${classId}-${globalRow}-${colLetter}`;
        
        if (!map.has(key)) {
          const sc = seatClasses.value.find(c => c.id === parseInt(classId));
          
          const seat = {
            id: `virtual-${key}`,
            seat_class_id: classId,
            seat_class: classId,
            row: globalRow,
            column: colLetter,
            seat_number: `${globalRow}${colLetter}`,
            seat_class_name: sc?.name || 'Unknown',
            price_multiplier: sc?.price_multiplier || 1.0,
            color: sc?.color || '#3B82F6',
            is_available: true,
            is_booked: false,
            isExisting: false,
            schedule: selectedScheduleId.value
          };
          
          initializeSeatFeatures(seat);
          map.set(key, seat);
        }
      }
    }
  });
  
  return map;
});

// ----- Special Seat Features -----
const hasSpecialSeat = (classId, row, col) => {
  const seat = getSeat(classId, row, col);
  if (!seat) return false;
  
  return seat.is_exit_row || 
         seat.is_wheelchair_accessible || 
         seat.has_bassinet || 
         seat.has_nut_allergy || 
         seat.is_unaccompanied_minor;
};

const isExitRow = (classId, row) => {
  // Check if any seat in this row is marked as an exit row
  if (!seatMapData.value) return false;
  
  // iterate through all columns in this row
  const config = layoutConfig.value[classId];
  if (!config) return false;
  
  for (let col = 1; col <= config.columns; col++) {
    const seat = getSeat(classId, row, col);
    if (seat && seat.is_exit_row) return true;
  }
  return false;
};

const isBulkheadRow = (classId, row) => {
  // Check if any seat in this row is marked as a bulkhead
  if (!seatMapData.value) return false;
  
  const config = layoutConfig.value[classId];
  if (!config) return false;
  
  for (let col = 1; col <= config.columns; col++) {
    const seat = getSeat(classId, row, col);
    if (seat && seat.is_bulkhead) return true;
  }
  return false;
};

const hasExtraLegroom = (classId, row) => {
  // Check if any seat in this row has extra legroom
  if (!seatMapData.value) return false;
  
  const config = layoutConfig.value[classId];
  if (!config) return false;
  
  for (let col = 1; col <= config.columns; col++) {
    const seat = getSeat(classId, row, col);
    if (seat && seat.has_extra_legroom) return true;
  }
  return false;
};

const isWheelchairSeat = (classId, row, col) => {
  const seat = getSeat(classId, row, col);
  return seat?.is_wheelchair_accessible || false;
};

const isBassinetSeat = (classId, row, col) => {
  const seat = getSeat(classId, row, col);
  return seat?.has_bassinet || false;
};

const hasNutAllergy = (classId, row, col) => {
  const seat = getSeat(classId, row, col);
  return seat?.has_nut_allergy || false;
};

const isUnaccompaniedMinor = (classId, row, col) => {
  const seat = getSeat(classId, row, col);
  return seat?.is_unaccompanied_minor || false;
};

const getSeatNumber = (classId, row, col) => {
  const globalRow = getGlobalRowNumber(classId, row);
  const colLetter = getColumnLabel(col);
  return `${globalRow}${colLetter}`;
};

const hasSpecialSeatsInClass = (classId) => {
  return getExitRowCountInClass(classId) > 0 || 
         getBassinetSeatsInClass(classId).length > 0;
};

const getExitRowCountInClass = (classId) => {
  const config = layoutConfig.value[classId];
  if (!config || !config.rows) return 0;
  
  let count = 0;
  for (let row = 1; row <= config.rows; row++) {
    if (isExitRow(classId, row)) {
      count++;
    }
  }
  return count;
};

const getBassinetSeatsInClass = (classId) => {
  const seats = [];
  const config = layoutConfig.value[classId];
  if (!config || !config.rows) return seats;
  
  // Check all seats in class (not just row 1)
  for (let row = 1; row <= config.rows; row++) {
    for (let col = 1; col <= config.columns; col++) {
        const seat = getSeat(classId, row, col);
        if (seat && seat.has_bassinet) {
            seats.push(seat);
        }
    }
  }
  return seats;
};

const hasWheelchairSeatsInRow = (classId, row) => {
  const config = layoutConfig.value[classId];
  if (!config || !config.columns) return false;
  
  for (let col = 1; col <= config.columns; col++) {
    if (isWheelchairSeat(classId, row, col)) {
      return true;
    }
  }
  return false;
};

// Initialize seat with default special features
const initializeSeatFeatures = (seat) => {
  const globalRow = seat.row;
  
  // Set default features based on position
  // REMOVED HARDCODED DEFAULTS - Logic is now data-driven.
  // User must explicitly set these properties.
  
  // Preserve existing values if they exist (e.g. from backend)
  seat.is_exit_row = seat.is_exit_row || false;
  seat.has_extra_legroom = seat.has_extra_legroom || false;
  seat.is_bulkhead = seat.is_bulkhead || false;
  
  seat.is_window = seat.column === 'A' || seat.column === getColumnLabel(layoutConfig.value[seat.seat_class]?.columns || 6);
  seat.is_aisle = seat.column === 'C' || seat.column === 'D' || seat.column === 'F';
  
  // Set defaults for new fields
  seat.is_wheelchair_accessible = seat.is_wheelchair_accessible || false;
  seat.has_bassinet = seat.has_bassinet || false;
  seat.has_nut_allergy = seat.has_nut_allergy || false;
  seat.is_unaccompanied_minor = seat.is_unaccompanied_minor || false;
  
  // Build features list
  seat.features = [];
  if (seat.is_exit_row) seat.features.push("Exit Row");
  if (seat.is_wheelchair_accessible) seat.features.push("Wheelchair");
  if (seat.has_bassinet) seat.features.push("Bassinet");
  if (seat.has_extra_legroom) seat.features.push("Extra Legroom");
  if (seat.is_bulkhead) seat.features.push("Bulkhead");
  if (seat.is_window) seat.features.push("Window");
  if (seat.is_aisle) seat.features.push("Aisle");
  
  return seat;
};

const getSeat = (classId, row, col) => {
  const colLetter = typeof col === 'number' ? getColumnLabel(col) : col;
  const globalRow = getGlobalRowNumber(classId, row);
  const key = `${classId}-${globalRow}-${colLetter}`;
  return seatMapData.value.get(key);
};

const selectSeat = (classId, row, col) => {
  const seat = getSeat(classId, row, col);
  if (seat) activeSeat.value = seat;
};

const getSeatStyle = (classId, row, col) => {
  const seat = getSeat(classId, row, col);
  if (!seat) return 'invisible';
  
  if (activeSeat.value?.id === seat.id) {
    return 'bg-[#fe3787] text-white border-[#fe3787] scale-110 shadow-lg';
  }
  
  if (!seat.is_available) {
    if (seat.is_booked) {
      return 'bg-[#002D1E] text-white border-[#002D1E] cursor-not-allowed opacity-80';
    }
    return 'bg-gray-300 text-gray-500 border-gray-300 cursor-not-allowed';
  }

  return 'bg-white hover:shadow-md';
};

const getSeatColorStyle = (classId, row, col) => {
  const seat = getSeat(classId, row, col);
  if (!seat || activeSeat.value?.id === seat.id || !seat.is_available) return {};
  
  const color = seat.color || '#3B82F6';
  return {
    backgroundColor: color + '20',
    borderColor: color,
    color: color,
  };
};

const toggleAvailability = async () => {
  if (!activeSeat.value) return;
  
  const seat = activeSeat.value;
  const newStatus = !seat.is_available;

  try {
    if (seat.isExisting && !String(seat.id).startsWith('virtual-')) {
      await api.patch(`/seats/${seat.id}/`, { is_available: newStatus });
    } else {
      const response = await api.post('/seats/', {
        schedule: parseInt(selectedScheduleId.value),
        seat_class: seat.seat_class_id,
        seat_number: seat.seat_number,
        row: seat.row,
        column: seat.column,
        is_available: newStatus
      });
      
      seat.id = response.data.id;
      seat.isExisting = true;
      seats.value.push(response.data);
    }
    
    seat.is_available = newStatus;
  } catch (err) {
    alert('Failed to update seat status');
  }
};

// ----- Context Menu for Special Requirements -----
const showSeatContextMenu = (event, classId, row, col) => {
  event.preventDefault();
  
  const seat = getSeat(classId, row, col);
  if (!seat) return;
  
  contextMenuSeat.value = seat;
  contextMenuX.value = event.pageX;
  contextMenuY.value = event.pageY;
  showContextMenu.value = true;
  
  document.addEventListener('click', closeContextMenu);
};

const closeContextMenu = () => {
  showContextMenu.value = false;
  document.removeEventListener('click', closeContextMenu);
};

const toggleRequirement = async (requirement) => {
  if (!contextMenuSeat.value) return;
  
  // Initialize requirements array if it doesn't exist
  if (!contextMenuSeat.value.requirements) {
    contextMenuSeat.value.requirements = [];
  }
  
  const index = contextMenuSeat.value.requirements.indexOf(requirement.id);
  if (index > -1) {
    contextMenuSeat.value.requirements.splice(index, 1);
  } else {
    contextMenuSeat.value.requirements.push(requirement.id);
  }
  
  // Also update legacy boolean if code matches
  if (requirement.code && typeof contextMenuSeat.value[requirement.code] !== 'undefined') {
    contextMenuSeat.value[requirement.code] = !contextMenuSeat.value[requirement.code];
  }
  
  await updateSeatSpecialRequirements(contextMenuSeat.value);
  closeContextMenu();
};

const hasRequirement = (seat, code) => {
  if (!seat) return false;
  
  // Check Many-to-Many requirements
  if (seat.requirements_detail) {
    return seat.requirements_detail.some(r => r.code === code);
  }
  
  // Fallback to booleans
  return seat[code] || false;
};

// Keep old toggle functions for safety but map them to toggleRequirement
const toggleExitRow = async () => {
  const req = seatRequirements.value.find(r => r.code === 'is_exit_row');
  if (req) await toggleRequirement(req);
};

const toggleWheelchairAccessible = async () => {
  const req = seatRequirements.value.find(r => r.code === 'is_wheelchair_accessible');
  if (req) await toggleRequirement(req);
};

const toggleBassinet = async () => {
  const req = seatRequirements.value.find(r => r.code === 'has_bassinet');
  if (req) await toggleRequirement(req);
};

const toggleNutAllergy = async () => {
  const req = seatRequirements.value.find(r => r.code === 'has_nut_allergy');
  if (req) await toggleRequirement(req);
};

const toggleUnaccompaniedMinor = async () => {
  const req = seatRequirements.value.find(r => r.code === 'is_unaccompanied_minor');
  if (req) await toggleRequirement(req);
};

const clearSpecialRequirements = async () => {
  if (!contextMenuSeat.value) return;
  contextMenuSeat.value.requirements = [];
  contextMenuSeat.value.is_exit_row = false;
  contextMenuSeat.value.is_wheelchair_accessible = false;
  contextMenuSeat.value.has_bassinet = false;
  contextMenuSeat.value.has_nut_allergy = false;
  contextMenuSeat.value.is_unaccompanied_minor = false;
  await updateSeatSpecialRequirements(contextMenuSeat.value);
  closeContextMenu();
};

// FIXED: Update seat special requirements - only include fields that exist
const updateSeatSpecialRequirements = async (seat) => {
  try {
    // Only include fields that exist in the database
    const payload = {
      is_exit_row: seat.is_exit_row || false,
      has_extra_legroom: seat.has_extra_legroom || false,
      is_bulkhead: seat.is_bulkhead || false,
      is_window: seat.is_window || false,
      is_aisle: seat.is_aisle || false,
      requirements: seat.requirements || []
    };
    
    // Add new fields only if they exist in the API response
    if (typeof seat.is_wheelchair_accessible !== 'undefined') {
      payload.is_wheelchair_accessible = seat.is_wheelchair_accessible || false;
    }
    if (typeof seat.has_bassinet !== 'undefined') {
      payload.has_bassinet = seat.has_bassinet || false;
    }
    if (typeof seat.has_nut_allergy !== 'undefined') {
      payload.has_nut_allergy = seat.has_nut_allergy || false;
    }
    if (typeof seat.is_unaccompanied_minor !== 'undefined') {
      payload.is_unaccompanied_minor = seat.is_unaccompanied_minor || false;
    }
    
    if (seat.isExisting && !String(seat.id).startsWith('virtual-')) {
      await api.patch(`/seats/${seat.id}/`, payload);
    } else {
      const response = await api.post('/seats/', {
        schedule: parseInt(selectedScheduleId.value),
        seat_class: seat.seat_class_id,
        seat_number: seat.seat_number,
        row: seat.row,
        column: seat.column,
        is_available: true,
        ...payload
      });
      
      seat.id = response.data.id;
      seat.isExisting = true;
      seats.value.push(response.data);
    }
    
    // Update seat features list
    seat.features = [];
    if (seat.is_exit_row) seat.features.push("Exit Row");
    if (seat.is_wheelchair_accessible) seat.features.push("Wheelchair");
    if (seat.has_bassinet) seat.features.push("Bassinet");
    if (seat.has_extra_legroom) seat.features.push("Extra Legroom");
    if (seat.is_bulkhead) seat.features.push("Bulkhead");
    if (seat.is_window) seat.features.push("Window");
    if (seat.is_aisle) seat.features.push("Aisle");
    
  } catch (err) {
    console.error('Error updating seat requirements:', err);
    console.error('Error details:', err.response?.data);
    alert('Failed to update seat requirements. Check if all fields exist in database.');
  }
};

const updateSeatSpecialFeatures = async () => {
  if (!activeSeat.value) return;
  await updateSeatSpecialRequirements(activeSeat.value);
};

const saveSpecialRequirements = async () => {
  if (!activeSeat.value) return;
  await updateSeatSpecialRequirements(activeSeat.value);
  showSpecialRequirementsModal.value = false;
};

// ----- Save Layout -----
const saveLayout = async () => {
  isSaving.value = true;
  
  try {
    const seatClassesConfig = orderedClassIds.value.map(classId => {
      const config = layoutConfig.value[classId];
      const sc = seatClasses.value.find(c => c.id === parseInt(classId));
      
      let startRow = 1;
      for (const prevId of orderedClassIds.value) {
        if (prevId === classId) break;
        const prevConfig = layoutConfig.value[prevId];
        if (prevConfig) startRow += prevConfig.rows;
      }
      
      return {
        class_id: parseInt(classId),
        name: sc?.name,
        rows: config.rows,
        columns: config.columns,
        start_row: startRow,
        color: sc?.color,
        price_multiplier: sc?.price_multiplier
      };
    });

    const totalSeats = seatClassesConfig.reduce((sum, c) => sum + (c.rows * c.columns), 0);
    const layoutPayload = {
      layout_config: {
        seat_classes: seatClassesConfig,
        total_seats: totalSeats
      }
    };

    if (saveMode.value === 'schedule') {
      // Save to currently selected schedule
      if (!selectedScheduleId.value) {
        alert('No schedule selected!');
        return;
      }
      
      const response = await api.post(`/schedules/${selectedScheduleId.value}/generate-seats/`, layoutPayload);
      
      alert(`✅ Seats generated for this flight!\n${response.data.message}`);
      
      // Refresh seats
      await handleScheduleChange();
      
    } else {
      // Existing logic: Save to Aircraft Template
      let aircraftId = aircraftInfo.value.aircraft?.id 
        || aircraftInfo.value.aircraft_id 
        || rawApiData.value?.flight?.aircraft;
      
      if (!aircraftId) {
        if (rawApiData.value?.flight) {
          const flightId = typeof rawApiData.value.flight === 'object' 
            ? rawApiData.value.flight.id 
            : rawApiData.value.flight;
          
          try {
            const flightRes = await api.get(`/flights/${flightId}/`);
            aircraftId = flightRes.data.aircraft;
          } catch (e) {
            console.error('Failed to get aircraft from flight:', e);
          }
        }
      }
      
      if (!aircraftId) {
        alert('No aircraft information available. Cannot save layout.');
        return;
      }

      // 1. Save to Aircraft Template
      await api.post(`/aircraft/${aircraftId}/save-layout/`, layoutPayload);
      
      let message = `✅ Layout saved to Aircraft Template!\nAircraft ID: ${aircraftId}`;

      // 2. ALSO generate seats for current schedule (if selected)
      if (selectedScheduleId.value) {
        try {
          const seatRes = await api.post(`/schedules/${selectedScheduleId.value}/generate-seats/`, layoutPayload);
          message += `\n\n✅ AND generated seats for this flight!\n${seatRes.data.message}`;
        } catch (seatErr) {
          console.error('Error generating seats after template save:', seatErr);
          message += `\n\n⚠️ Template saved, but failed to generate seats for flight: ${seatErr.message}`;
        }
      }
      
      alert(message);
      
      // Refresh seats
      if (selectedScheduleId.value) {
        await handleScheduleChange();
      }
    }
    
  } catch (err) {
    console.error('Error:', err);
    alert('Failed: ' + (err.response?.data?.error || err.message));
  } finally {
    isSaving.value = false;
  }
};

const applyAircraftTemplate = async (aircraftId) => {
  try {
    const res = await api.get(`/aircraft/${aircraftId}/layout/`);
    const layout = res.data.layout;
    
    if (layout?.seat_classes?.length > 0) {
      const newConfig = {};
      const newOrder = [];
      
      for (const sc of layout.seat_classes) {
        newConfig[sc.class_id] = {
          rows: sc.rows,
          columns: sc.columns,
          airline: aircraftInfo.value.airline_id
        };
        newOrder.push(sc.class_id);
      }
      
      layoutConfig.value = newConfig;
      classOrder.value = newOrder;
      hasExistingLayout.value = true;
    }
  } catch (err) {
    console.log('No template found for this aircraft, starting fresh');
  }
};

// ----- Fetch Initial Data -----
const fetchData = async () => {
  try {
    const [schedRes, scRes, aRes, reqRes] = await Promise.all([
      api.get('/schedules/'),
      api.get('/seat-classes/'),
      api.get('/airlines/'),
      api.get('/seat-requirements/')
    ]);
    
    schedules.value = schedRes.data.results || schedRes.data || [];
    seatClasses.value = (scRes.data.results || scRes.data || []).map((sc, index) => ({
      ...sc,
      color: sc.color || defaultColors[index % defaultColors.length]
    }));
    airlines.value = aRes.data.results || aRes.data || [];
    seatRequirements.value = reqRes.data.results || reqRes.data || [];
    
  } catch (err) {
    console.error('Error fetching data:', err);
  }
};

onMounted(() => {
  fetchData();
  
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeContextMenu();
    }
  });
});
</script>

<style scoped>
/* Context menu styles */
.fixed {
  z-index: 9999;
}

/* Seat hover effects */
.group:hover .group-hover\:block {
  display: block;
}

/* Tooltip arrow */
.tooltip-arrow {
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid #1f2937;
}

/* Smooth transitions */
button {
  transition: all 0.2s ease;
}

/* Scrollbar styling */
.max-h-\[400px\]::-webkit-scrollbar {
  width: 6px;
}
.max-h-\[400px\]::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}
.max-h-\[400px\]::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

/* Special seat glow effect */
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 5px currentColor; }
  50% { box-shadow: 0 0 15px currentColor; }
}

.seat-exit-row {
  animation: pulse-glow 2s infinite;
  border-color: #ef4444 !important;
}

.seat-wheelchair {
  animation: pulse-glow 3s infinite;
  border-color: #3b82f6 !important;
}

.seat-bassinet {
  animation: pulse-glow 4s infinite;
  border-color: #8b5cf6 !important;
}
</style>