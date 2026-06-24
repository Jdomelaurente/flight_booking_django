<template>
  <div class="min-h-screen bg-gray-50 pb-32 lg:pb-6">
    <BookingStatusHeader />

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">

      <!-- Page Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <div class="flex items-center gap-3">
          <button @click="$router.back()"
            class="flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-gray-800 transition-colors">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
            Add-ons
          </button>
          <span class="text-gray-300">/</span>
          <h1 class="text-base font-bold text-gray-900">Seat Selection</h1>
        </div>
        <div class="flex items-center gap-3 bg-white px-3 py-1.5 rounded-lg border border-gray-100 shadow-sm">
          <span class="text-xs text-gray-500 font-medium">{{ Object.keys(assignedSeats).length }}/{{ eligiblePassengers.length }} selected</span>
          <div class="h-1.5 bg-gray-100 rounded-full w-24 overflow-hidden">
            <div class="h-full bg-pink-500 rounded-full transition-all duration-700 ease-out"
              :style="{ width: (Object.keys(assignedSeats).length / Math.max(eligiblePassengers.length, 1) * 100) + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- Flight Segment Switcher & Itinerary Bar -->
      <div v-if="bookingStore.isRoundTrip || bookingStore.tripType.includes('multi')"
        class="flex gap-3 mb-6 overflow-x-auto pb-2 scrollbar-hide">
        <button
          v-for="segment in flightSegments"
          :key="segment.key"
          @click="switchFlightSegment(segment.key)"
          :class="[
            'flex items-center gap-3 px-5 py-3 rounded-xl text-sm font-bold transition-all flex-shrink-0 border-2',
            activeFlightSegment === segment.key
              ? 'bg-[#003870] text-white border-[#003870] shadow-lg shadow-blue-100 scale-[1.02]'
              : 'bg-white text-gray-600 border-gray-100 hover:border-blue-200'
          ]">
          <span class="text-lg">{{ segment.key === 'depart' ? '🛫' : segment.key === 'return' ? '🛬' : '📍' }}</span>
          <div class="text-left">
            <p class="leading-tight text-[13px]">{{ segment.label }}</p>
            <p class="text-[10px] font-medium opacity-70 mt-0.5">{{ segment.flight }}</p>
          </div>
          <span v-if="getSeatsForSegment(segment.key).length > 0"
            class="ml-2 text-[10px] font-black px-2 py-0.5 rounded-full"
            :class="activeFlightSegment === segment.key ? 'bg-white/20 text-white' : 'bg-green-100 text-green-700'">
            {{ getSeatsForSegment(segment.key).length }}
          </span>
        </button>
      </div>

      <!-- Main Layout -->
      <div v-if="!isLoading || rawSeats.length > 0" class="flex flex-col xl:grid xl:grid-cols-[280px_1fr_320px] gap-8 items-start">
        
        <!-- Sidebar Left: Passengers & Detailed Legend -->
        <div class="w-full space-y-6">
          <!-- Passenger Selection -->
          <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden md:block" :class="{'hidden': true, 'md:block': true}">
            <div class="bg-gray-50 px-5 py-4 border-b border-gray-100">
              <h3 class="text-[10px] font-black uppercase tracking-widest text-gray-400">Select Passenger</h3>
            </div>
            <div class="divide-y divide-gray-50">
              <div
                v-for="(p, index) in eligiblePassengers"
                :key="p.key"
                @click="p.type !== 'Infant' ? activePIndex = index : null"
                :class="[
                  'p-4 flex items-center justify-between gap-4 transition-all duration-300 relative',
                  p.type !== 'Infant' ? 'cursor-pointer' : 'cursor-default opacity-50',
                  activePIndex === index && p.type !== 'Infant' ? 'bg-pink-50/50 shadow-inner' : 'hover:bg-gray-50/50'
                ]">
                <div v-if="activePIndex === index" class="absolute left-0 top-0 bottom-0 w-1 bg-pink-500"></div>
                <div class="flex items-center gap-3 min-w-0">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black flex-shrink-0 transition-transform duration-300"
                    :class="activePIndex === index ? 'bg-pink-500 text-white scale-110 shadow-lg shadow-pink-100' : 'bg-gray-100 text-gray-400'">
                    {{ index + 1 }}
                  </div>
                  <div class="min-w-0">
                    <p class="text-[13px] font-bold text-gray-900 truncate">{{ p.firstName }} {{ p.lastName }}</p>
                    <p class="text-[9px] font-black text-gray-400 uppercase mt-0.5">{{ p.type }}</p>
                  </div>
                </div>
                <div v-if="assignedSeats[p.key]" class="flex items-center gap-1.5 bg-pink-100 px-2 py-1 rounded-lg">
                  <span class="text-[11px] font-black text-pink-600">{{ assignedSeats[p.key].seat_code }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Mobile Passenger Switcher -->
          <div class="md:hidden sticky top-[72px] z-30 -mx-4 px-4 py-3 bg-white border-b border-gray-100 overflow-x-auto no-scrollbar flex gap-3 shadow-sm shadow-slate-100/50">
            <div 
              v-for="(p, n) in eligiblePassengers" 
              :key="'mob-p-'+n"
              @click="activePIndex = n"
              :class="[
                'flex-shrink-0 flex flex-col items-center gap-1 p-2 rounded-xl transition-all duration-300 border',
                activePIndex === n ? 'bg-pink-50 border-pink-200 scale-105 shadow-sm' : 'bg-white border-gray-100 opacity-60'
              ]">
              <div class="w-9 h-9 rounded-full flex items-center justify-center text-xs font-black transition-colors"
                   :class="activePIndex === n ? 'bg-pink-500 text-white' : 'bg-gray-100 text-gray-400'">
                {{ n + 1 }}
              </div>
              <div class="flex items-center gap-1">
                <span class="text-[9px] font-black uppercase tracking-tighter" :class="activePIndex === n ? 'text-pink-600' : 'text-gray-400'">
                  {{ assignedSeats[p.key] ? assignedSeats[p.key].seat_code : '---' }}
                </span>
                <div v-if="assignedSeats[p.key]" class="w-1 h-1 rounded-full bg-emerald-500"></div>
              </div>
            </div>
          </div>

          <!-- Feature Legend -->
          <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-6">
            <div>
              <p class="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-4">Seat Status</p>
              <div class="grid grid-cols-1 gap-3">
                <div class="flex items-center gap-3">
                  <div class="w-6 h-6 rounded-lg border-2 border-gray-100 bg-white"></div>
                  <span class="text-[11px] font-bold text-gray-600">Available</span>
                </div>
                <div class="flex items-center gap-3">
                  <div class="w-6 h-6 rounded-lg bg-pink-500 shadow-lg shadow-pink-100"></div>
                  <span class="text-[11px] font-bold text-pink-600">Your Selection</span>
                </div>
                <div class="flex items-center gap-3">
                  <div class="w-6 h-6 rounded-lg bg-[#003870]"></div>
                  <span class="text-[11px] font-bold text-blue-900">Other Passengers</span>
                </div>
                <div class="flex items-center gap-3">
                  <div class="w-6 h-6 rounded-lg bg-[#f8fafc] border border-gray-200"></div>
                  <span class="text-[11px] font-bold text-gray-400">Already Booked</span>
                </div>
                <div class="flex items-center gap-3">
                  <div class="w-6 h-6 rounded-lg bg-gray-800 flex items-center justify-center text-[10px] text-white">🔒</div>
                  <span class="text-[11px] font-bold text-gray-800">Blocked / Crew</span>
                </div>
              </div>
            </div>

            <div class="pt-6 border-t border-gray-50">
              <p class="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-4">Seat Positions</p>
              <div class="flex flex-wrap gap-4">
                <div class="flex items-center gap-2">
                  <span class="text-xs text-gray-400">🪟</span>
                  <span class="text-[11px] font-bold text-gray-600">Window</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-xs text-gray-400">🚶</span>
                  <span class="text-[11px] font-bold text-gray-600">Aisle</span>
                </div>
              </div>
            </div>

            <div class="pt-6 border-t border-gray-50">
              <p class="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-4">Amenities & Features</p>
              <div class="grid grid-cols-2 gap-3">
                <div v-for="feat in amenityIcons" :key="feat.label" class="flex items-center gap-2">
                  <span class="text-xs">{{ feat.icon }}</span>
                  <span class="text-[10px] font-black text-gray-500 uppercase">{{ feat.label }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Center: The Interactive Airplane -->
        <div class="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden flex flex-col relative">
          <!-- Aircraft Header -->
          <div class="px-8 py-5 border-b border-gray-50 flex items-center justify-between bg-white sticky top-0 z-20">
            <div class="flex items-center gap-4">
              <div class="px-4 py-1.5 bg-[#003870] rounded-full text-white text-[10px] font-black tracking-widest italic uppercase">
                {{ aircraftModel || 'A321-NEO' }}
              </div>
              <div class="flex items-center gap-2">
                <span class="text-[10px] font-black text-gray-300 uppercase tracking-widest">Front</span>
                <div class="w-12 h-0.5 bg-gray-100"></div>
                <span class="text-[10px] font-black text-gray-300 uppercase tracking-widest">Back</span>
              </div>
            </div>
            
            <!-- Contextual Hover Info -->
            <transition name="fade">
              <div v-if="hoveredSeat" class="bg-blue-50 px-4 py-2 rounded-xl flex items-center gap-4 border border-blue-100">
                <div class="flex flex-col">
                  <span class="text-xs font-black text-blue-900 leading-none">Seat {{ hoveredSeat.seat_code }}</span>
                  <span class="text-[10px] font-bold text-blue-600/70 uppercase mt-0.5">{{ getSeatPosition(hoveredSeat) }}</span>
                </div>
                <div class="h-6 w-px bg-blue-200"></div>
                <div class="flex flex-col items-end">
                   <span class="text-xs font-black text-pink-600">{{ getSeatPriceLabel(hoveredSeat) }}</span>
                   <div class="flex flex-wrap justify-end gap-1 mt-1.5 max-w-[160px]">
                     <span v-for="feat in getSeatAmenities(hoveredSeat)" :key="feat.label" 
                       class="bg-white/50 px-1.5 py-0.5 rounded text-[8px] font-black text-blue-700 uppercase flex items-center gap-1 border border-blue-100/50">
                       <span>{{ feat.icon }}</span> {{ feat.label }}
                     </span>
                   </div>
                </div>
              </div>
            </transition>
          </div>

          <!-- Seat Map Scrolling Content -->
          <div class="flex-1 overflow-auto p-4 sm:p-12 bg-[#fcfcfd]" style="max-height: 750px">
            <div class="aircraft-body mx-auto max-w-sm">
              <!-- Nose with Cockpit -->
              <div class="flex justify-center mb-8 sm:mb-12 relative scale-75 sm:scale-100">
                <div class="w-32 h-15 bg-gray-50 border border-gray-100 flex items-center justify-center relative overflow-hidden" 
                  style="border-radius: 100% 100% 20% 20%">
                  <div class="flex gap-4">
                    <div class="w-6 h-4 bg-gray-200 rounded-sm opacity-50"></div>
                    <div class="w-6 h-4 bg-gray-200 rounded-sm opacity-50"></div>
                  </div>
                  <div class="absolute bottom-2 inset-x-0 text-center">
                    <span class="text-[8px] font-black text-gray-300 tracking-[0.3em] uppercase">Cockpit</span>
                  </div>
                </div>
              </div>

              <!-- Cabin Layout -->
              <div v-for="seatClass in seatClasses" :key="seatClass.id" class="mb-16 transition-all duration-500 relative">
                
                <!-- Class Banner -->
                <div class="flex flex-col items-center mb-10">
                  <div class="flex items-center gap-4 w-full">
                    <div class="h-px flex-1 bg-gradient-to-r from-transparent to-gray-200"></div>
                    <span class="text-[11px] font-black uppercase tracking-[0.2em] text-gray-400">
                      {{ seatClass.name }}
                    </span>
                    <div class="h-px flex-1 bg-gradient-to-l from-transparent to-gray-200"></div>
                  </div>
                </div>

                <!-- Seats Grid -->
                <div class="space-y-4">
                   <!-- Column Headers -->
                   <div class="flex justify-center gap-[4.5rem] mb-2 px-10">
                      <div class="flex gap-2.5">
                         <span v-for="seat in getRowGroupsByClass(seatClass.id)[0]?.leftSeats" :key="seat.column" 
                           class="w-[44px] text-center text-[10px] font-black text-gray-300">{{ seat.column }}</span>
                      </div>
                      <div class="flex gap-2.5">
                         <span v-for="seat in getRowGroupsByClass(seatClass.id)[0]?.rightSeats" :key="seat.column" 
                           class="w-[44px] text-center text-[10px] font-black text-gray-300">{{ seat.column }}</span>
                      </div>
                   </div>

                  <div v-for="rowGroup in getRowGroupsByClass(seatClass.id)" :key="rowGroup.row">
                    <!-- Special Area Notifications -->
                    <div v-if="rowGroup.isExitRow" class="flex items-center justify-center gap-3 my-4">
                      <div class="flex items-center gap-2 bg-red-50 px-4 py-1.5 rounded-full border border-red-100">
                         <span class="text-xs animate-pulse">🚪</span>
                         <span class="text-[9px] font-black text-red-500 tracking-widest uppercase">Emergency Exit Row</span>
                      </div>
                    </div>
                    
                    <div v-if="rowGroup.isBulkhead" class="flex items-center justify-center gap-3 my-4">
                      <div class="w-full h-1 bg-gray-100 max-w-[280px] rounded-full"></div>
                    </div>

                    <div class="flex items-center justify-center gap-4">
                      <!-- Left Section -->
                      <div class="flex gap-2.5">
                        <button
                          v-for="seat in rowGroup.leftSeats"
                          :key="seat.id"
                          @click="assignSeat(seat)"
                          @mouseenter="hoveredSeat = seat"
                          @mouseleave="hoveredSeat = null"
                          :disabled="isSeatInteractiveDisabled(seat)"
                          :class="[
                            'seat-premium group transition-all duration-300',
                            getSeatStatus(seat),
                            { 'has-extra': hasExtraLegroom(seat) },
                            { 'is-restricted': hasRestriction(seat) }
                          ]"
                          :style="getSeatStatus(seat) === 'available' ? { '--seat-accent': getClassColor(seatClass.name) } : {}">
                          <div class="seat-head"></div>
                          <div class="seat-base">
                            <span class="label">{{ seat.column }}</span>
                            <div class="seat-icons">
                               <div v-if="seat.has_bassinet" class="icon purple" title="Bassinet Position">👶</div>
                               <div v-if="hasExtraLegroom(seat)" class="icon gold" title="Extra Legroom">↕️</div>
                               <div v-if="seat.is_exit_row" class="icon red" title="Emergency Exit">🚪</div>
                               <div v-if="seat.has_medical_oxygen" class="icon blue" title="Medical Oxygen">💨</div>
                               <div v-if="seat.has_pet_in_cabin" class="icon orange" title="Pet in Cabin">🐾</div>
                               <div v-if="seat.is_wheelchair_accessible" class="icon blue" title="Wheelchair Accessible">♿</div>
                               <div v-if="seat.is_bulkhead" class="icon gray" title="Bulkhead Seat">🧱</div>
                            </div>
                            <!-- Price Tag mini -->
                            <div v-if="getSeatStatus(seat) === 'available' && seat.seat_price > 0" class="price-dot"></div>
                          </div>
                        </button>
                      </div>

                      <!-- Aisle Label -->
                      <div class="w-8 flex flex-col items-center justify-center">
                        <span class="text-[11px] font-black text-gray-400 bg-gray-100/50 w-6 h-6 rounded-lg flex items-center justify-center">{{ rowGroup.globalRow }}</span>
                      </div>

                      <!-- Right Section -->
                      <div class="flex gap-2.5">
                        <button
                          v-for="seat in rowGroup.rightSeats"
                          :key="seat.id"
                          @click="assignSeat(seat)"
                          @mouseenter="hoveredSeat = seat"
                          @mouseleave="hoveredSeat = null"
                          :disabled="isSeatInteractiveDisabled(seat)"
                          :class="[
                            'seat-premium group transition-all duration-300',
                            getSeatStatus(seat),
                            { 'has-extra': hasExtraLegroom(seat) },
                            { 'is-restricted': hasRestriction(seat) }
                          ]"
                          :style="getSeatStatus(seat) === 'available' ? { '--seat-accent': getClassColor(seatClass.name) } : {}">
                          <div class="seat-head"></div>
                          <div class="seat-base">
                            <span class="label">{{ seat.column }}</span>
                            <div class="seat-icons">
                               <div v-if="seat.has_bassinet" class="icon purple" title="Bassinet Position">👶</div>
                               <div v-if="hasExtraLegroom(seat)" class="icon gold" title="Extra Legroom">↕️</div>
                               <div v-if="seat.is_exit_row" class="icon red" title="Emergency Exit">🚪</div>
                               <div v-if="seat.has_medical_oxygen" class="icon blue" title="Medical Oxygen">💨</div>
                               <div v-if="seat.has_pet_in_cabin" class="icon orange" title="Pet in Cabin">🐾</div>
                               <div v-if="seat.is_wheelchair_accessible" class="icon blue" title="Wheelchair Accessible">♿</div>
                               <div v-if="seat.is_bulkhead" class="icon gray" title="Bulkhead Seat">🧱</div>
                            </div>
                            <div v-if="getSeatStatus(seat) === 'available' && seat.seat_price > 0" class="price-dot"></div>
                          </div>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Tail with Rear Galley -->
              <div class="flex justify-center mt-12 bg-gray-50 border border-gray-100 p-4 rounded-xl opacity-50">
                 <span class="text-[9px] font-bold text-gray-400 uppercase tracking-widest italic">Rear Galley & Lavatories</span>
              </div>
            </div>
          </div>
          
          <!-- Bottom Legend Context -->
          <div class="px-8 py-3 bg-white border-t border-gray-50 text-[10px] text-gray-400 flex justify-center gap-8">
             <div class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-blue-400"></span> Amenity Available</div>
             <div class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-pink-500"></span> Your Selection</div>
             <div class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full border border-gray-300"></span> Standard</div>
          </div>
        </div>

        <!-- Sidebar Right: Selection Summary & Actions -->
        <div class="w-full space-y-6">
          <div class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden flex flex-col">
            <div class="p-6 border-b border-gray-50 bg-gray-50/50">
              <h4 class="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-1">Total Fee</h4>
              <p class="text-3xl font-black text-[#003870] font-mono">₱{{ totalSeats.toLocaleString() }}</p>
            </div>
            
            <div class="p-6 space-y-6">
              <!-- Selected Seats List -->
              <div>
                <h4 class="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-4">Passenger Assignments</h4>
                <div class="space-y-5">
                  <div v-for="(p, idx) in eligiblePassengers" :key="p.key">
                    <div class="flex items-start justify-between">
                      <div class="flex gap-3">
                         <div class="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-[10px] font-black"
                           :class="assignedSeats[p.key] ? 'bg-pink-100 text-pink-600' : 'bg-gray-100 text-gray-400'">
                           {{ idx + 1 }}
                         </div>
                         <div class="min-w-0">
                           <p class="text-sm font-bold text-gray-900 truncate">{{ p.firstName }}</p>
                           <p v-if="assignedSeats[p.key]" class="text-[10px] font-medium text-gray-400 mt-0.5">
                             {{ assignedSeats[p.key].seat_code }} • {{ assignedSeats[p.key].seat_class?.name }}
                             <div v-if="assignedSeats[p.key].features?.length > 0" class="mt-1 flex flex-wrap gap-1.5">
                               <span v-for="f in assignedSeats[p.key].features" :key="f.label" 
                                 class="inline-flex items-center gap-1 px-1.5 py-0.5 bg-[#FF579A]/10 text-[#FF579A] text-[9px] font-black uppercase rounded-md border border-[#FF579A]/20">
                                 <span>{{ f.icon }}</span> {{ f.label }}
                               </span>
                             </div>
                           </p>
                           <p v-else class="text-[10px] font-black text-amber-500 uppercase mt-0.5">Seat pending</p>
                         </div>
                      </div>
                      <div v-if="assignedSeats[p.key]" class="text-right">
                         <p class="text-xs font-black text-gray-900">₱{{ (assignedSeats[p.key].seat_price || 0).toLocaleString() }}</p>
                         <button @click="removeSeat(p.key)" class="text-[9px] font-black text-red-400 hover:text-red-500 uppercase mt-1">Remove</button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Recommendation Engine / Notes -->
              <div class="bg-blue-50/50 rounded-xl p-4 border border-blue-100/50">
                 <p class="text-[10px] font-bold text-blue-900 uppercase flex items-center gap-2">
                   <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>
                   Fare Benefits
                 </p>
                 <p class="text-[11px] text-blue-700/70 mt-2 leading-relaxed">
                   Your <strong>{{ bookingStore.fareFamilies[activeFlightSegment === 'depart' ? 'outbound' : activeFlightSegment] || 'Economy' }}</strong> fare includes standard seat selection at no extra cost. Special seats like Extra Legroom may require an upgrade fee.
                 </p>
              </div>

              <!-- CTA -->
              <div class="space-y-3 pt-4">
                <button
                  @click="confirmSeats"
                  :disabled="!allPassengersHaveSeats"
                  :class="[
                    'w-full py-4 rounded-2xl text-sm font-black transition-all duration-300 shadow-xl active:scale-[0.98]',
                    allPassengersHaveSeats 
                      ? 'bg-[#FF579A] text-white shadow-pink-100 hover:bg-[#FF4081]' 
                      : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  ]">
                  {{ confirmButtonText.toUpperCase() }}
                </button>
                
                <button v-if="bookingStore.isRoundTrip && hasDepartSeats && activeFlightSegment === 'depart'"
                  @click="copySeatsToReturn"
                  class="w-full py-4 rounded-xl text-xs font-bold text-[#003870] border-2 border-blue-50 hover:bg-blue-50 transition-colors uppercase">
                  Repeat for Return Flight
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <MobileBookingFooter 
      :button-text="confirmButtonText.toUpperCase()" 
      :disabled="!allPassengersHaveSeats"
      @next="confirmSeats" 
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useBookingStore } from '@/stores/booking';
import { seatService } from '@/services/booking/seatService';
import { useModalStore } from '@/stores/modal';
import { useNotificationStore } from '@/stores/notification';
import BookingStatusHeader from '@/components/booking/BookingStatusHeader.vue';
import MobileBookingFooter from '@/components/booking/MobileBookingFooter.vue';

const router = useRouter();
const bookingStore = useBookingStore();
const notificationStore = useNotificationStore();
const modalStore = useModalStore();

const activePIndex = ref(0);
const activeFlightSegment = ref('');
const hoveredSeat = ref(null);
const rawSeats = ref([]);
const isLoading = ref(true);
const baseFlightPrice = ref(0);
const aircraftModel = ref('');
const aircraftCapacity = ref(0);
let pollInterval = null;

// Amenity Metadata
const amenityIcons = [
  { label: 'WiFi', icon: '📶' },
  { label: 'Power', icon: '🔌' },
  { label: 'Video', icon: '📺' },
  { label: 'Bassinet', icon: '👶' },
  { label: 'Legroom', icon: '↕️' },
  { label: 'Exit Row', icon: '🚪' },
  { label: 'Oxygen', icon: '💨' },
  { label: 'Pet', icon: '🐾' }
];

// Computed properties
const currentFlight = computed(() => {
  const isMulti = bookingStore.tripType === 'multi_city' || bookingStore.tripType === 'multi-city';
  if (isMulti) {
    const idx = parseInt(activeFlightSegment.value);
    return bookingStore.multiCitySegments[idx]?.selectedFlight;
  }
  return activeFlightSegment.value === 'return' 
    ? bookingStore.selectedReturn 
    : bookingStore.selectedOutbound;
});

const activeFlightSegmentLabel = computed(() => {
  return activeFlightSegment.value === 'depart' ? 'Depart' : 'Return';
});

const flightSegments = computed(() => {
  const tripType = bookingStore.tripType;
  
  if (tripType === 'multi_city' || tripType === 'multi-city') {
    return bookingStore.multiCitySegments.map((seg, idx) => ({
      key: idx.toString(),
      label: `Flight ${idx + 1}`,
      flight: seg.selectedFlight?.flight_number || 'N/A',
      route: `${seg.origin} → ${seg.destination}`
    }));
  }

  const segments = [{
      key: 'depart',
      label: 'Depart Flight',
      flight: bookingStore.selectedOutbound?.flight_number || 'N/A'
  }];
  
  if (bookingStore.isRoundTrip && bookingStore.selectedReturn) {
    segments.push({
      key: 'return',
      label: 'Return Flight',
      flight: bookingStore.selectedReturn.flight_number || 'N/A'
    });
  }
  return segments;
});

const assignedSeats = computed(() => bookingStore.getSeatsBySegment(activeFlightSegment.value));

const getSeatsForSegment = (segmentKey) => {
  const seats = bookingStore.getSeatsBySegment(segmentKey);
  return seats ? Object.values(seats) : [];
};

const allPassengersHaveSeats = computed(() => {
  const adultsAndChildren = bookingStore.passengers.filter(p => p.type !== 'Infant');
  const seats = assignedSeats.value || {};
  return adultsAndChildren.every(p => seats[p.key]);
});

const hasDepartSeats = computed(() => Object.keys(bookingStore.getSeatsBySegment('depart')).length > 0);

const confirmButtonText = computed(() => {
  if (bookingStore.isRoundTrip && activeFlightSegment.value === 'depart') {
    return allPassengersHaveSeats.value ? 'Next: Return Seats' : 'Assign All Seats';
  }
  return allPassengersHaveSeats.value ? 'Save & Continue' : 'Assign All Seats';
});

const totalSeats = computed(() => {
  let total = 0;
  flightSegments.value.forEach(seg => {
    Object.values(bookingStore.getSeatsBySegment(seg.key)).forEach(seat => {
      total += parseFloat(seat.seat_price) || 0;
    });
  });
  return total;
});

const eligiblePassengers = computed(() => bookingStore.passengers.filter(p => p.type !== 'Infant'));

// Seat Logic & UI Helpers
const getSeatStatus = (seat) => {
  if (seat.is_blocked || seat.is_crew_seat || seat.seat_code?.includes('CREW')) return 'blocked';
  
  const currentPKey = bookingStore.passengers[activePIndex.value]?.key;

  // 1. Check local state first (most accurate for current user's session)
  const localOccupantKey = Object.keys(assignedSeats.value).find(k => assignedSeats.value[k]?.id === seat.id);
  if (localOccupantKey) {
    return localOccupantKey === currentPKey ? 'selected' : 'taken-by-other';
  }

  // 2. Check API state for locks from this session/user
  if (seat.is_locked_by_me) {
    // If it's locked by me but NOT currently in assignedSeats locally, 
    // it means it's a seat we previously held or is reserved for our session.
    // We SHOULD let the user click it again.
    return 'available'; 
  }

  if (seat.is_booked || seat.is_locked || !seat.is_available) return 'occupied';
  if (isClassDimmed(seat.seat_class?.name) || !isSeatInBookedClass(seat)) return 'occupied';
  
  return 'available';
};

const isSeatInteractiveDisabled = (seat) => {
  const status = getSeatStatus(seat);
  return status === 'occupied' || status === 'taken-by-other' || status === 'blocked';
};

const getSeatPosition = (seat) => {
  if (!seat) return '';
  const col = seat.column?.toUpperCase();
  // Assume standard A-F layout
  if (col === 'A' || col === 'F') return 'Window Seat';
  if (col === 'C' || col === 'D') return 'Aisle Seat';
  return 'Middle Seat';
};

const getSeatPriceLabel = (seat) => {
  if (!isSeatInBookedClass(seat)) return 'Unavailable (Wrong Class)';
  if (isSeatIncluded(seat)) return 'Included';
  const price = parseFloat(seat.seat_price) || 0;
  return price > 0 ? `₱${price.toLocaleString()}` : 'Standard';
};

const isSeatInBookedClass = (seat) => {
  if (!seat || !currentFlight.value) return true;
  
  const booked = (currentFlight.value?.travel_class || 
                  currentFlight.value?.class_type || 
                  currentFlight.value?.selected_seat_class || '').toLowerCase();
  
  const target = (seat.seat_class?.name || '').toLowerCase();
  
  // Strict DCS enforcement
  if (booked.includes('premium economy')) {
     return target.includes('premium economy');
  }

  if (booked.includes('economy')) {
     // Economy passengers CANNOT select Premium Economy
     return target.includes('economy') && !target.includes('premium');
  }

  if (booked.includes('business')) return target.includes('business');
  if (booked.includes('first')) return target.includes('first');
  
  return true;
};

const hasExtraLegroom = (seat) => seat.has_extra_legroom || seat.seat_class?.name?.toLowerCase().includes('legroom');
const hasRestriction = (seat) => seat.is_exit_row || seat.has_limited_recline;

const getSeatAmenities = (seat) => {
  if (!seat) return [];
  const list = [];
  
  // 1. Position-based Features
  const isWindow = seat.is_window || seat.column === 'A' || seat.column === 'F';
  const isAisle = seat.is_aisle || seat.column === 'C' || seat.column === 'D';
  if (isWindow) list.push({ label: 'Window', icon: '🪟' });
  if (isAisle) list.push({ label: 'Aisle', icon: '🚶' });
  
  // 2. Direct Requirements / Booleans
  if (seat.has_wifi) list.push({ label: 'WiFi', icon: '📶' });
  if (seat.has_power || seat.has_usb) list.push({ label: 'Power', icon: '🔌' });
  if (seat.has_entertainment) list.push({ label: 'Video', icon: '📺' });
  if (seat.has_bassinet) list.push({ label: 'Bassinet', icon: '👶' });
  if (seat.has_extra_legroom) list.push({ label: 'Legroom', icon: '↕️' });
  if (seat.is_exit_row) list.push({ label: 'Exit Row', icon: '🚪' });
  if (seat.has_medical_oxygen) list.push({ label: 'Oxygen', icon: '💨' });
  if (seat.has_pet_in_cabin) list.push({ label: 'Pet', icon: '🐾' });
  if (seat.is_wheelchair_accessible) list.push({ label: 'Wheelchair', icon: '♿' });
  if (seat.is_bulkhead) list.push({ label: 'Bulkhead', icon: '🧱' });
  
  // 3. Dynamic features/requirements from backend
  const features = seat.seat_features || seat.special_requirements || seat.features || [];
  if (Array.isArray(features)) {
     features.forEach(f => {
        const name = (typeof f === 'string' ? f : f.name || '').toLowerCase();
        
        if (name.includes('wifi') && !list.some(i => i.label === 'WiFi')) list.push({ label: 'WiFi', icon: '📶' });
        if ((name.includes('power') || name.includes('usb')) && !list.some(i => i.label === 'Power')) list.push({ label: 'Power', icon: '🔌' });
        if (name.includes('bassinet') && !list.some(i => i.label === 'Bassinet')) list.push({ label: 'Bassinet', icon: '👶' });
        if (name.includes('medical') || name.includes('oxygen')) {
          if (!list.some(i => i.label === 'Oxygen')) list.push({ label: 'Oxygen', icon: '💨' });
        }
        if (name.includes('pet')) {
          if (!list.some(i => i.label === 'Pet')) list.push({ label: 'Pet', icon: '🐾' });
        }
     });
  }

  // 4. Default for classes if still empty of generic amenities
  const n = seat.seat_class?.name?.toLowerCase() || '';
  if (!list.some(i => i.label === 'WiFi' || i.label === 'Power' || i.label === 'Video')) {
    if (n.includes('business')) {
       list.push({ label: 'Power', icon: '🔌' }, { label: 'Video', icon: '📺' }, { label: 'WiFi', icon: '📶' });
    } else if (n.includes('premium')) {
       list.push({ label: 'Power', icon: '🔌' }, { label: 'Audio', icon: '🎧' });
    } else {
       list.push({ label: 'USB', icon: '🔋' });
    }
  }
  return list;
};

// Data Fetching
const fetchSeatData = async (silent = false) => {
  const scheduleId = currentFlight.value?.id;
  if (!scheduleId) return;

  try {
    if (!silent) isLoading.value = true;
    const response = await seatService.getSeatsBySchedule(scheduleId, bookingStore.bookingSessionId);
    
    if (response.success) {
      const seatsData = response.seats?.results || response.seats || [];
      rawSeats.value = Array.isArray(seatsData) ? seatsData : [];
      baseFlightPrice.value = response.schedule_price || 0;
      aircraftModel.value = response.aircraft_model;
    }
  } catch (err) {
    console.error("Fetch failed", err);
  } finally {
    isLoading.value = false;
  }
};

const getRowGroupsByClass = (classId) => {
  const classSeats = rawSeats.value.filter(s => s.seat_class?.id === classId);
  const rowMap = {};
  classSeats.forEach(seat => {
    if (!rowMap[seat.row]) rowMap[seat.row] = [];
    rowMap[seat.row].push(seat);
  });

  return Object.keys(rowMap).sort((a, b) => Number(a) - Number(b)).map(rowNum => {
    const seats = rowMap[rowNum].sort((a, b) => a.column.localeCompare(b.column));
    const mid = Math.ceil(seats.length / 2);
    // Determine if it's a bulkhead (e.g. first row of a class)
    const sortedGroupNums = Object.keys(rowMap).sort((a, b) => Number(a) - Number(b));
    const isBulkhead = rowNum === sortedGroupNums[0];

    return {
      row: Number(rowNum),
      globalRow: rowNum,
      leftSeats: seats.slice(0, mid),
      rightSeats: seats.slice(mid),
      isExitRow: seats.some(s => s.is_exit_row),
      isBulkhead: isBulkhead
    };
  });
};

const seatClasses = computed(() => {
  const unique = [];
  rawSeats.value.forEach(s => {
    if (s.seat_class && !unique.find(c => c.id === s.seat_class.id)) {
       unique.push(s.seat_class);
    }
  });
  return unique;
});

// UI Logic
const getClassColor = (name) => {
  const n = name?.toLowerCase() || '';
  if (n.includes('business')) return '#7c3aed';
  if (n.includes('premium')) return '#059669';
  if (n.includes('choice') || n.includes('extra')) return '#003870';
  return '#e5e7eb';
};

const isClassDimmed = (className) => {
  return false; // All seats are now selectable
};

const isSeatIncluded = (seat) => {
  // Check the flight's fare family
  const family = (bookingStore.fareFamilies[activeFlightSegment.value] || '').toLowerCase();
  
  // Check the selected travel class
  const travelClass = (currentFlight.value?.travel_class || currentFlight.value?.class_type || currentFlight.value?.selected_seat_class || '').toLowerCase();
  
  // Base rule: If they are flying Business/First/Premium or bought a Flex fare, standard seats are included
  if (family.includes('flex') || family.includes('premium') || family.includes('business') ||
      travelClass.includes('business') || travelClass.includes('first') || travelClass.includes('premium')) {
    
    // They still might pay extra for specific "Extra Legroom" marker inside their cabin, 
    // unless ALL seats in that cabin are considered extra legroom.
    return !seat.has_extra_legroom; 
  }
  
  return false;
};

const assignSeat = (seat) => {
  const status = getSeatStatus(seat);
  if (status === 'occupied' || status === 'blocked' || status === 'taken-by-other') return;
  
  const currentP = bookingStore.passengers[activePIndex.value];
  if (!currentP) return;

  // Toggle selection
  if (assignedSeats.value[currentP.key]?.id === seat.id) {
    bookingStore.removeSeat(currentP.key, activeFlightSegment.value);
    return;
  }

  // Update local store only (delay server-side locking till confirmSeats)
  const price = isSeatIncluded(seat) ? 0 : Math.max(0, (parseFloat(seat.final_price) || 0) - (currentFlight.value?.price || 0));
  const seatData = {
    id: seat.id,
    seat_code: seat.seat_code,
    seat_price: price,
    seat_class: { name: seat.seat_class?.name },
    features: getSeatAmenities(seat)
  };
  
  bookingStore.assignSeat(currentP.key, seatData, activeFlightSegment.value);
  
  // Auto-advance to next passenger
  const nextIdx = eligiblePassengers.value.findIndex((p, i) => i > activePIndex.value && !assignedSeats.value[p.key]);
  if (nextIdx !== -1) activePIndex.value = nextIdx;
  else {
     const firstEmpty = eligiblePassengers.value.findIndex(p => !assignedSeats.value[p.key]);
     if (firstEmpty !== -1) activePIndex.value = firstEmpty;
  }
};

const removeSeat = (pKey) => {
  const seat = assignedSeats.value[pKey];
  if (seat) seatService.unlockSeat(seat.id, bookingStore.bookingSessionId);
  bookingStore.removeSeat(pKey, activeFlightSegment.value);
};

const switchFlightSegment = (segment) => {
  activeFlightSegment.value = segment;
  activePIndex.value = 0;
  fetchSeatData();
};

const copySeatsToReturn = async () => {
  isLoading.value = true;
  const res = await bookingStore.copySeatsToReturn();
  if (res.success) {
    notificationStore.success('Seats synced to return flight');
    switchFlightSegment('return');
  } else {
    notificationStore.warn('Some seats unavailable on return flight');
  }
  isLoading.value = false;
};

const confirmSeats = async () => {
  if (!allPassengersHaveSeats.value) return;

  try {
    isLoading.value = true;
    
    const seatsToLock = Object.values(assignedSeats.value);
    const sessionId = bookingStore.bookingSessionId;

    for (const seat of seatsToLock) {
      // Find the live seat data from the raw seat list to check current lock status
      const liveSeat = rawSeats.value.find(s => s.id === seat.id);

      // If the seat is already locked by THIS session, skip re-locking — user is re-confirming
      if (liveSeat?.is_locked_by_me || liveSeat?.locked_by_session === sessionId) {
        console.log(`✅ Seat ${seat.seat_code} already held by this session. Skipping re-lock.`);
        continue;
      }

      const res = await seatService.lockSeat(seat.id, sessionId);

      if (!res.success) {
        // HTTP 423 = locked by another session; HTTP 409 = permanently booked
        const isOurLock = res.status === 423 && res.error?.toLowerCase().includes('another'); // someone else
        if (!isOurLock && res.status === 409) {
          notificationStore.error(`Seat ${seat.seat_code} is no longer available. Please choose a different seat.`);
        } else if (isOurLock) {
          notificationStore.error(`Seat ${seat.seat_code} was just taken by someone else. Please choose a different seat.`);
        } else {
          // Any other failure — try to re-lock silently (might be the user's own expired lock)
          console.warn(`⚠️ Seat ${seat.seat_code} lock returned: ${res.error}. Proceeding anyway.`);
          continue;
        }
        await fetchSeatData();
        return;
      }
    }

    if (bookingStore.isRoundTrip && activeFlightSegment.value === 'depart') {
      switchFlightSegment('return');
    } else {
      router.push({ name: 'Addons' });
    }
  } catch (err) {
    notificationStore.error("Unable to confirm seats. Please try again.");
    console.error("Lock error", err);
  } finally {
    isLoading.value = false;
  }
};

// Polling and Lifecycle
const startPolling = () => {
  pollInterval = setInterval(async () => {
    if (document.visibilityState === 'visible' && !isLoading.value) {
      await fetchSeatData(true);
    }
  }, 10000);
};

onMounted(() => {
  activeFlightSegment.value = bookingStore.tripType.includes('multi') ? '0' : 'depart';
  fetchSeatData();
  startPolling();
});

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval);
});
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }

/* PREMIUM SEAT COMPONENT */
.seat-premium {
  width: 44px;
  height: 52px;
  background: transparent;
  border: none;
  padding: 0;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  outline: none;
}

.seat-head {
  width: 34px;
  height: 10px;
  background: #fff;
  border: 1.5px solid #e2e8f0;
  border-bottom: none;
  border-radius: 8px 8px 0 0;
  transition: 0.3s;
}

.seat-base {
  width: 44px;
  height: 40px;
  background: #fff;
  border: 1.5px solid #e2e8f0;
  border-radius: 4px 4px 10px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: 0.3s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.seat-base .label {
  font-size: 11px;
  font-weight: 800;
  color: #94a3b8;
}

.seat-icons {
  display: flex;
  flex-direction: row-reverse;
  gap: 1px;
  position: absolute;
  top: -4px;
  right: -4px;
  z-index: 10;
}

.icon {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 8px;
  color: white;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
  border: 1px solid white;
  background: #cbd5e1;
}

.icon.gold { background: #f59e0b; }
.icon.red { background: #ef4444; }
.icon.blue { background: #3b82f6; }
.icon.orange { background: #f97316; }
.icon.purple { background: #a855f7; }
.icon.green { background: #10b981; }
.icon.gray { background: #64748b; }

.price-dot {
  position: absolute;
  bottom: 4px;
  width: 4px;
  height: 4px;
  background: #10b981;
  border-radius: 50%;
}

/* STATUSES */
.seat-premium.available:hover .seat-base {
  border-color: var(--seat-accent, #FF579A);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.seat-premium.selected .seat-head,
.seat-premium.selected .seat-base {
  background: #FF579A;
  border-color: #f43f5e;
}
.seat-premium.selected .label { color: #fff; }
.seat-premium.selected .icon { filter: brightness(0) invert(1); }

.seat-premium.occupied .seat-head,
.seat-premium.occupied .seat-base {
  background: #f8fafc;
  border-color: #f1f5f9;
  cursor: not-allowed;
}
.seat-premium.occupied .label { color: #cbd5e1; }

.seat-premium.taken-by-other .seat-head,
.seat-premium.taken-by-other .seat-base {
  background: #003870;
  border-color: #002d5a;
}
.seat-premium.taken-by-other .label { color: #fff; opacity: 0.7; }
.seat-premium.taken-by-other .icon { filter: brightness(0) invert(1); }

.seat-premium.blocked .seat-head,
.seat-premium.blocked .seat-base {
  background: #1e293b;
  border-color: #0f172a;
  cursor: not-allowed;
}
.seat-premium.blocked .label { color: #64748b; }

/* HIGHLIGHTS */
.seat-premium.has-extra .seat-base::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  border: 1px solid rgba(245, 158, 11, 0.3);
  pointer-events: none;
}

.seat-premium.is-restricted .seat-base {
  border-style: dashed;
}

/* ANIMATIONS */
.fade-enter-active, .fade-leave-active { transition: all 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(10px); }

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-4px); }
  100% { transform: translateY(0px); }
}

.seat-premium.selected {
  animation: float 2s infinite ease-in-out;
}
</style>
