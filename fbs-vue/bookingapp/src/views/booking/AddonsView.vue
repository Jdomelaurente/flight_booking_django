<template>
  <div class="min-h-screen bg-gray-50 pb-32 lg:pb-6">
    <BookingStatusHeader />
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="flex flex-col lg:flex-row gap-6 items-start">

        <!-- MAIN CONTENT -->
        <main class="flex-1 min-w-0 space-y-5">

          <!-- Page Header -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h1 class="text-2xl font-bold text-gray-900 tracking-tight">Customize Your Trip</h1>
              <p class="text-sm text-gray-500 mt-0.5">Enhance your journey with our premium services</p>
            </div>
            <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold uppercase tracking-wide w-fit"
              :class="bookingStore.isRoundTrip ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'bg-pink-50 text-pink-600 border border-pink-200'">
              {{ tripTypeInfo }}
            </span>
          </div>

          <!-- Flight Strip Banner -->
          <div v-if="flightInfo.length > 0" class="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
            <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-3">Your Flights</p>
            <div class="flex flex-wrap gap-4">
              <div v-for="flight in flightInfo" :key="flight.type" class="flex items-center gap-3 flex-1 min-w-[200px]">
                <div class="w-8 h-8 rounded-sm flex items-center justify-center flex-shrink-0"
                  :class="flight.type === 'Return' ? 'bg-blue-100' : 'bg-pink-100'">
                  <svg class="w-4 h-4" :class="flight.type === 'Return' ? 'text-blue-600' : 'text-pink-600'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400">{{ flight.type }}</p>
                  <p class="text-sm font-bold text-gray-900 truncate">{{ flight.route }}</p>
                  <p class="text-xs text-gray-500">{{ flight.flight }}</p>
                </div>
                <p class="text-sm font-bold text-pink-500 flex-shrink-0">&#8369;{{ flight.price.toLocaleString() }}</p>
              </div>
            </div>
          </div>

          <!-- Segment Roadmap -->
          <div v-if="segmentRoadmap.length > 0" class="bg-white rounded-xl border border-gray-100 shadow-sm px-4 sm:px-5 py-4 overflow-hidden">
            <p class="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-3">Add-on Progress</p>
            <div class="flex items-center overflow-x-auto no-scrollbar pb-1 -mx-2 px-2 gap-4 sm:gap-2">
              <template v-for="(seg, idx) in segmentRoadmap" :key="seg.key">
                <div class="flex items-center gap-2.5 flex-shrink-0 min-w-fit">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all"
                    :class="seg.isComplete ? 'bg-green-500 border-green-500 text-white' : activeSegment === seg.key ? 'border-pink-500 text-pink-500 bg-white' : 'border-gray-300 text-gray-400 bg-white'">
                    <svg v-if="seg.isComplete" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                    <span v-else>{{ idx + 1 }}</span>
                  </div>
                  <div class="hidden sm:block">
                    <p class="text-xs font-semibold text-gray-800">{{ seg.label }}</p>
                    <div class="flex gap-1 mt-0.5">
                      <span :class="seg.baggageDone ? 'opacity-100' : 'opacity-25 grayscale'" class="text-[10px]">&#x1F9F3;</span>
                      <span :class="seg.mealsDone ? 'opacity-100' : 'opacity-25 grayscale'" class="text-[10px]">&#x1F371;</span>
                      <span :class="seg.seatsDone ? 'opacity-100' : 'opacity-25 grayscale'" class="text-[10px]">&#x1F4BA;</span>
                    </div>
                  </div>
                  <!-- Mobile simplified label -->
                  <div class="sm:hidden">
                    <p class="text-[10px] font-bold text-gray-800">Flight {{ idx + 1 }}</p>
                  </div>
                </div>
                <div v-if="idx < segmentRoadmap.length - 1" class="flex-grow sm:flex-1 h-px bg-gray-200 min-w-[20px] mx-1 sm:mx-3"></div>
              </template>
            </div>
          </div>

          <!-- TABS CARD -->
          <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <!-- Tab Nav -->
            <div class="flex border-b border-gray-100 overflow-x-auto no-scrollbar scroll-smooth">
              <button @click="currentTab = 'baggage'"
                :class="['flex-1 min-w-[100px] flex flex-col items-center gap-1 py-4 px-2 text-[10px] sm:text-xs font-semibold transition-all relative', currentTab === 'baggage' ? 'text-pink-600 bg-pink-50/60' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50']">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
                <span>Baggage</span>
                <div v-if="currentTab === 'baggage'" class="absolute bottom-0 inset-x-0 h-0.5 bg-pink-500"></div>
              </button>
              <button @click="$router.push({ name: 'SeatSelection' })"
                class="flex-1 min-w-[100px] flex flex-col items-center gap-1 py-4 px-2 text-[10px] sm:text-xs font-semibold text-gray-500 hover:text-gray-700 hover:bg-gray-50 transition-all relative">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" /></svg>
                <span>Seats</span>
                <span class="absolute top-2 right-2 text-[9px] bg-amber-100 text-amber-700 px-1 py-0.5 rounded font-bold">Go</span>
              </button>
              <button @click="currentTab = 'meals'"
                :class="['flex-1 min-w-[100px] flex flex-col items-center gap-1 py-4 px-2 text-[10px] sm:text-xs font-semibold transition-all relative', currentTab === 'meals' ? 'text-pink-600 bg-pink-50/60' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50']">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
                <span>Meals</span>
                <div v-if="currentTab === 'meals'" class="absolute bottom-0 inset-x-0 h-0.5 bg-pink-500"></div>
              </button>
              <button @click="currentTab = 'wheelchair'"
                :class="['flex-1 min-w-[100px] flex flex-col items-center gap-1 py-4 px-2 text-[10px] sm:text-xs font-semibold transition-all relative', currentTab === 'wheelchair' ? 'text-pink-600 bg-pink-50/60' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50']">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                <span>Assistance</span>
                <div v-if="currentTab === 'wheelchair'" class="absolute bottom-0 inset-x-0 h-0.5 bg-pink-500"></div>
              </button>
              <button @click="currentTab = 'protection'"
                :class="['flex-1 min-w-[100px] flex flex-col items-center gap-1 py-4 px-2 text-[10px] sm:text-xs font-semibold transition-all relative', currentTab === 'protection' ? 'text-emerald-600 bg-emerald-50/60' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50']">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                <span>Protection</span>
                <div v-if="currentTab === 'protection'" class="absolute bottom-0 inset-x-0 h-0.5 bg-emerald-500"></div>
              </button>
            </div>

            <!-- Tab Content -->
            <div class="p-5">
              <!-- Loading -->
              <div v-if="isLoading" class="flex flex-col items-center justify-center py-16 gap-3">
                <div class="w-10 h-10 border-4 border-pink-100 border-t-pink-500 rounded-full animate-spin"></div>
                <p class="text-sm text-gray-400">Loading available services...</p>
              </div>

              <template v-else>
                <!-- BAGGAGE TAB -->
                <div v-if="currentTab === 'baggage'" class="space-y-6">
                  <div>
                    <p class="text-xs font-bold uppercase tracking-wider text-gray-700">Extra Baggage Allowance</p>
                    <p class="text-xs text-gray-500 mt-0.5">Standard cabin bag included. Select extra checked baggage per passenger.</p>
                  </div>
                  
                  <!-- BAGGAGE POLICY CARD -->
                  <div v-if="currentBaggagePolicy" class="bg-blue-50 border border-blue-100 rounded-sm p-4 animate-fade-in relative overflow-hidden group">
                    <div class="absolute -right-4 -bottom-4 opacity-[0.03] group-hover:scale-110 transition-transform duration-700">
                      <svg class="w-24 h-24" fill="currentColor" viewBox="0 0 24 24"><path d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/></svg>
                    </div>
                    <div class="flex items-start gap-3">
                      <div class="w-8 h-8 rounded-sm bg-blue-100 flex items-center justify-center flex-shrink-0">
                        <svg class="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                      </div>
                      <div class="flex-1 min-w-0">
                        <h4 class="text-[10px] font-black uppercase tracking-widest text-blue-600 mb-1">Airline Baggage Policy: {{ currentBaggagePolicy.airline }}</h4>
                        <div class="space-y-2">
                          <p class="text-xs font-bold text-blue-900 leading-tight">{{ currentBaggagePolicy.concept }}</p>
                          <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1">
                            <div v-if="currentBaggagePolicy.pieces" class="flex items-center gap-1.5">
                              <div class="w-1 h-1 rounded-full bg-blue-400"></div>
                              <span class="text-[10px] text-blue-700 font-medium">Piece Limit: {{ currentBaggagePolicy.pieces }}</span>
                            </div>
                            <div v-if="currentBaggagePolicy.weightLimits" class="flex items-center gap-1.5">
                              <div class="w-1 h-1 rounded-full bg-blue-400"></div>
                              <span class="text-[10px] text-blue-700 font-medium">{{ currentBaggagePolicy.weightLimits }}</span>
                            </div>
                            <div v-if="currentBaggagePolicy.pooling" class="flex items-center gap-1.5">
                              <div class="w-1 h-1 rounded-full bg-blue-400"></div>
                              <span class="text-[10px] text-blue-700 font-medium">Pooling: {{ currentBaggagePolicy.pooling }}</span>
                            </div>
                          </div>
                          <p v-if="currentBaggagePolicy.keyRule" class="text-[10px] text-blue-600 italic bg-blue-100/50 px-2 py-1 rounded-sm w-fit">
                            💡 Tip: {{ currentBaggagePolicy.keyRule }}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-for="segment in flightSegments" :key="segment.key" class="space-y-4">
                    <div class="flex items-center gap-2 py-2 px-3 rounded-sm" :class="segment.key === 'return' ? 'bg-blue-50 border border-blue-100' : 'bg-pink-50 border border-pink-100'">
                      <span class="text-sm">{{ segment.key === "depart" ? "✈️" : segment.key === "return" ? "🔄" : "📍" }}</span>
                      <span class="text-sm font-bold text-gray-700">{{ segment.label }}</span>
                      <span class="text-xs text-gray-500">· {{ segment.flight }}</span>
                      <span class="ml-2 px-1.5 py-0.5 rounded-sm text-[10px] font-black uppercase tracking-tight bg-white border border-gray-200 text-gray-700 shadow-sm">
                        {{ getAirlineName(segment.key) }}
                      </span>
                      <!-- Fare Family Badge -->
                      <span v-if="bookingStore.fareFamilies[segment.key]" 
                        class="ml-auto text-[9px] font-black px-2 py-0.5 bg-gray-100 text-gray-600 rounded uppercase tracking-widest">
                        {{ bookingStore.fareFamilies[segment.key] }}
                      </span>
                    </div>
                    <!-- If baggage is included in the fare, show banner, but STILL show add-on options. -->
                    <div v-if="isAnyBaggageIncludedForSegment(segment.key)" class="flex items-center gap-3 p-4 rounded-sm bg-emerald-50 border border-emerald-200 mb-4">
                      <div class="w-9 h-9 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
                        <svg class="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
                      </div>
                      <div>
                        <p class="text-sm font-bold text-emerald-800">Checked Baggage Included</p>
                        <p class="text-[11px] text-emerald-600 mt-0.5">Your selected fare already includes checked baggage for all passengers on this flight. You may purchase additional baggage below if needed.</p>
                      </div>
                    </div>

                    <div v-for="p in eligiblePassengers" :key="p.key" class="rounded-sm border border-gray-100 bg-gray-50/60 p-4 mb-3 last:mb-0">
                      <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center gap-2">
                          <div class="w-7 h-7 rounded-full bg-[#003870] flex items-center justify-center text-white text-[10px] font-bold flex-shrink-0">
                            {{ p.firstName?.charAt(0) }}{{ p.lastName?.charAt(0) }}
                          </div>
                          <div>
                            <p class="text-sm font-semibold text-gray-900">{{ p.firstName }} {{ p.lastName }}</p>
                            <p class="text-[10px] text-gray-500 uppercase tracking-wide">{{ p.type }}</p>
                          </div>
                        </div>
                        <button v-if="getBaggageSelection(p.key, segment.key) && segmentRoadmap.length > 1"
                          class="text-[10px] font-bold text-blue-600 bg-blue-50 border border-blue-200 px-2 py-1 rounded-md hover:bg-blue-100 transition-colors"
                          @click="handleCopyAddon('baggage', p)">Apply to all flights</button>
                      </div>
                      <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                        <div v-for="opt in (baggageOptionsMap[getAirlineId(segment.key)] || []).filter(o => !isBaggageIncluded(o, segment.key))" :key="opt.id"
                          @click="selectBaggageDirect(p, opt, segment.key, $event)"
                          :class="['relative cursor-pointer rounded-sm border-2 p-3 text-center transition-all hover:-translate-y-0.5 hover:shadow-sm', getBaggageSelection(p.key, segment.key)?.id === opt.id ? 'border-pink-500 bg-pink-50' : 'border-gray-200 bg-white hover:border-pink-300']">
                          
                          <div v-if="getBaggageSelection(p.key, segment.key)?.id === opt.id" class="absolute -top-2 -right-2 w-5 h-5 bg-pink-500 rounded-full flex items-center justify-center z-10">
                            <svg class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                          </div>
                          <div class="text-2xl mb-1">&#x1F9F3;</div>
                          <p class="text-sm font-black text-gray-900">{{ opt.formatted_weight }}</p>
                          <p class="text-xs font-bold text-pink-500 mt-0.5">+ ₱{{ parseFloat(opt.price).toLocaleString() }}</p>
                        </div>
                        <div v-if="!(baggageOptionsMap[getAirlineId(segment.key)] || []).filter(o => !isBaggageIncluded(o, segment.key)).length" class="col-span-3 text-center text-xs text-gray-400 py-4">
                          No extra baggage options available for this flight.
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- MEALS TAB -->
                <div v-if="currentTab === 'meals'" class="space-y-6">
                  <div>
                    <p class="text-xs font-bold uppercase tracking-wider text-gray-700">In-Flight Meal Selection</p>
                    <p class="text-xs text-gray-500 mt-0.5">Pre-order your meal for a guaranteed selection. Available meals vary by route.</p>
                  </div>
                  <div v-for="segment in flightSegments" :key="segment.key" class="space-y-4">
                    <div class="flex items-center gap-2 py-2 px-3 rounded-sm" :class="segment.key === 'return' ? 'bg-blue-50 border border-blue-100' : 'bg-pink-50 border border-pink-100'">
                      <span class="text-sm">{{ segment.key === "depart" ? "✈️" : segment.key === "return" ? "🔄" : "📍" }}</span>
                      <span class="text-xs font-bold text-gray-700">{{ segment.label }}</span>
                      <span class="text-xs text-gray-500">· {{ segment.flight }}</span>
                      <span class="ml-2 px-1.5 py-0.5 rounded-sm text-[10px] font-black uppercase tracking-tight bg-white border border-gray-200 text-gray-700 shadow-sm">
                        {{ getAirlineName(segment.key) }}
                      </span>
                      <!-- Fare Family Badge -->
                      <span v-if="bookingStore.fareFamilies[segment.key]" 
                        class="ml-auto text-[9px] font-black px-2 py-0.5 bg-gray-100 text-gray-600 rounded uppercase tracking-widest">
                        {{ bookingStore.fareFamilies[segment.key] }}
                      </span>
                    </div>
                    <div v-for="p in eligiblePassengers" :key="p.key" class="rounded-sm border border-gray-100 bg-gray-50/60 p-4">
                      <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center gap-2">
                          <div class="w-7 h-7 rounded-full bg-[#003870] flex items-center justify-center text-white text-[10px] font-bold flex-shrink-0">
                            {{ p.firstName?.charAt(0) }}{{ p.lastName?.charAt(0) }}
                          </div>
                          <div>
                            <p class="text-sm font-semibold text-gray-900">{{ p.firstName }} {{ p.lastName }}</p>
                            <p class="text-[10px] text-gray-500 uppercase tracking-wide">{{ p.type }}</p>
                          </div>
                        </div>
                        <div class="flex items-center gap-2">
                          <button v-if="getMealSelection(p.key, segment.key).length > 0"
                            class="text-[10px] font-bold text-red-600 bg-red-50 border border-red-200 px-2 py-1 rounded-md hover:bg-red-100 transition-colors"
                            @click="selectMealDirect(p, null, segment.key, $event)">Clear All</button>
                          <button v-if="getMealSelection(p.key, segment.key).length > 0 && segmentRoadmap.length > 1"
                            class="text-[10px] font-bold text-blue-600 bg-blue-50 border border-blue-200 px-2 py-1 rounded-md hover:bg-blue-100 transition-colors"
                            @click="handleCopyAddon('meals', p)">Apply to all flights</button>
                        </div>
                      </div>

                      <!-- Selected Meals List -->
                      <div v-if="getMealSelection(p.key, segment.key).length > 0" class="mb-4 flex flex-wrap gap-2">
                         <div v-for="m in getMealSelection(p.key, segment.key)" :key="m.id" 
                           class="flex items-center gap-2 bg-pink-100 text-pink-700 px-2 py-1 rounded-full text-[10px] font-bold border border-pink-200">
                           <span>{{ m.name }}</span>
                           <button @click.stop="bookingStore.removeMealAddon(p.key, m.id, segment.key); syncSelectionsFromStore()" class="hover:text-pink-900">
                             <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                           </button>
                         </div>
                      </div>

                      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                        <div v-for="meal in (mealOptionsMap[getAirlineId(segment.key)] || [])" :key="meal.id"
                          @click="selectMealDirect(p, meal, segment.key, $event)"
                          :class="['relative cursor-pointer rounded-sm border-2 p-3 flex items-start gap-3 transition-all hover:-translate-y-0.5', getMealSelection(p.key, segment.key).some(m => m.id === meal.id) ? 'border-pink-500 bg-pink-50' : 'border-gray-200 bg-white hover:border-pink-300']">
                          
                          <!-- Included Badge for Meals -->
                          <div v-if="isMealIncluded(segment.key)" 
                            class="absolute top-1 right-1 bg-emerald-500 text-white text-[7px] font-black px-1.5 py-0.5 rounded uppercase tracking-tighter">
                            Included
                          </div>

                          <div v-if="getMealSelection(p.key, segment.key).some(m => m.id === meal.id)" class="absolute -top-2 -right-2 w-5 h-5 bg-pink-500 rounded-full flex items-center justify-center z-10">
                            <svg class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                          </div>
                          <div class="text-2xl flex-shrink-0">
                            <span v-if="meal.meal_type === 'vegetarian'">&#x1F96C;</span>
                            <span v-else-if="meal.meal_type === 'vegan'">&#x1F331;</span>
                            <span v-else-if="meal.meal_type === 'halal'">&#x262A;&#xFE0F;</span>
                            <span v-else-if="meal.meal_type === 'kosher'">&#x2721;&#xFE0F;</span>
                            <span v-else-if="meal.meal_type === 'child'">&#x1F476;</span>
                            <span v-else>&#x1F37D;&#xFE0F;</span>
                          </div>
                          <div class="flex-1 min-w-0">
                            <p class="text-sm font-bold text-gray-900 line-clamp-1">{{ meal.name }}</p>
                            <div class="flex flex-wrap gap-1 mt-1">
                              <span class="px-1.5 py-0.5 text-[9px] font-bold uppercase rounded"
                                :class="['vegetarian','vegan'].includes(meal.meal_type) ? 'bg-green-100 text-green-700' : meal.meal_type === 'halal' ? 'bg-emerald-100 text-emerald-700' : 'bg-orange-100 text-orange-700'">
                                {{ meal.get_meal_type_display || meal.meal_type }}
                              </span>
                            </div>
                            <p v-if="!isMealIncluded(segment.key)" class="text-sm font-black mt-1.5 text-pink-500">
                              ₱{{ parseFloat(meal.price).toLocaleString() }}
                            </p>
                            <p v-else class="text-sm font-black mt-1.5 text-emerald-600">
                              INCLUDED
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- ASSISTANCE TAB -->
                <div v-if="currentTab === 'wheelchair'" class="space-y-6">
                  <div>
                    <p class="text-xs font-bold uppercase tracking-wider text-gray-700">Special Assistance</p>
                    <p class="text-xs text-gray-500 mt-0.5">We coordinate with ground staff to ensure your comfort throughout the journey.</p>
                  </div>
                  <div v-for="segment in flightSegments" :key="segment.key" class="space-y-4">
                    <div class="flex items-center gap-2 py-2 px-3 rounded-sm" :class="segment.key === 'return' ? 'bg-blue-50 border border-blue-100' : 'bg-pink-50 border border-pink-100'">
                      <span class="text-sm">{{ segment.key === "depart" ? "✈️" : segment.key === "return" ? "🔄" : "📍" }}</span>
                      <span class="text-xs font-bold text-gray-700">{{ segment.label }}</span>
                      <span class="text-xs text-gray-500">· {{ segment.flight }}</span>
                      <span class="ml-2 px-1.5 py-0.5 rounded-sm text-[10px] font-black uppercase tracking-tight bg-white border border-gray-200 text-gray-700 shadow-sm">
                        {{ getAirlineName(segment.key) }}
                      </span>
                    </div>
                    <div v-for="p in eligiblePassengers" :key="p.key" class="rounded-sm border border-gray-100 bg-gray-50/60 p-4">
                      <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center gap-2">
                          <div class="w-7 h-7 rounded-full bg-[#003870] flex items-center justify-center text-white text-[10px] font-bold flex-shrink-0">
                            {{ p.firstName?.charAt(0) }}{{ p.lastName?.charAt(0) }}
                          </div>
                          <div>
                            <p class="text-sm font-semibold text-gray-900">{{ p.firstName }} {{ p.lastName }}</p>
                            <p class="text-[10px] text-gray-500 uppercase tracking-wide">{{ p.type }}</p>
                          </div>
                        </div>
                        <button v-if="getAssistanceSelection(p.key, segment.key) && segmentRoadmap.length > 1"
                          class="text-[10px] font-bold text-blue-600 bg-blue-50 border border-blue-200 px-2 py-1 rounded-md hover:bg-blue-100 transition-colors"
                          @click="handleCopyAddon('wheelchair', p)">Apply to all flights</button>
                      </div>
                      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                        <div @click="selectAssistanceDirect(p, null, segment.key, $event)"
                          :class="['relative cursor-pointer rounded-sm border-2 p-3 flex items-center gap-3 transition-all', !getAssistanceSelection(p.key, segment.key) ? 'border-pink-500 bg-pink-50' : 'border-gray-200 bg-white hover:border-pink-300']">
                          <div v-if="!getAssistanceSelection(p.key, segment.key)" class="absolute -top-2 -right-2 w-5 h-5 bg-pink-500 rounded-full flex items-center justify-center">
                            <svg class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                          </div>
                          <span class="text-2xl">&#x1F6B6;</span>
                          <div><p class="text-sm font-bold text-gray-800">No Assistance Needed</p><p class="text-[10px] text-gray-500">I can manage independently</p></div>
                        </div>
                        <div v-for="service in (assistanceOptionsMap[getAirlineId(segment.key)] || [])" :key="service.id"
                          @click="selectAssistanceDirect(p, service, segment.key, $event)"
                          :class="['relative cursor-pointer rounded-sm border-2 p-3 flex items-start gap-3 transition-all hover:-translate-y-0.5', getAssistanceSelection(p.key, segment.key)?.id === service.id ? 'border-pink-500 bg-pink-50' : service.price === 0 ? 'border-emerald-200 bg-emerald-50/40 hover:border-emerald-400' : 'border-gray-200 bg-white hover:border-pink-300']">
                          <div v-if="getAssistanceSelection(p.key, segment.key)?.id === service.id" class="absolute -top-2 -right-2 w-5 h-5 bg-pink-500 rounded-full flex items-center justify-center">
                            <svg class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                          </div>
                          <div class="text-2xl flex-shrink-0">
                            <span v-if="service.service_type === 'wheelchair'">&#x267F;</span>
                            <span v-else-if="service.service_type === 'boarding'">&#x1F475;</span>
                            <span v-else-if="service.service_type === 'medical'">&#x1F3E5;</span>
                            <span v-else-if="service.service_type === 'unaccompanied_minor'">&#x1F466;</span>
                            <span v-else-if="service.service_type === 'pet'">&#x1F415;</span>
                            <span v-else>&#x1F6C2;</span>
                          </div>
                          <div class="flex-1 min-w-0">
                            <div class="flex items-start justify-between gap-1">
                              <p class="text-sm font-bold text-gray-900">{{ service.name }}</p>
                              <span v-if="service.price === 0" class="text-[9px] font-black uppercase bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded flex-shrink-0">FREE</span>
                            </div>
                            <p class="text-[10px] text-gray-500 italic mt-0.5">{{ service.get_service_type_display || service.service_type }}</p>
                            <p class="text-xs text-gray-600 mt-1 line-clamp-2">{{ service.description }}</p>
                            <p v-if="service.advance_notice_text" class="text-[10px] text-amber-600 mt-1 font-bold tracking-tight">&#x23F0; {{ service.advance_notice_text }}</p>
                            <p v-if="service.price > 0" class="text-sm font-black text-pink-500 mt-1.5">&#8369;{{ parseFloat(service.price).toLocaleString() }}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <!-- PROTECTION TAB -->
                <div v-if="currentTab === 'protection'" class="space-y-6">
                  <div>
                    <p class="text-xs font-bold uppercase tracking-wider text-gray-700">Travel Protection</p>
                    <p class="text-xs text-gray-500 mt-0.5">Protect your journey against unexpected medical emergencies, cancellations, and delays.</p>
                  </div>

                  <div v-if="filteredInsurancePlans.length === 0 && !isLoading" class="py-12 text-center border-2 border-dashed border-gray-100 rounded-sm">
                    <p class="text-xs text-gray-400">No protection plans available for this itinerary.</p>
                  </div>

                  <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    <!-- No Insurance Option -->
                    <div @click="removeInsurance()"
                      :class="['relative cursor-pointer rounded-sm border-2 p-5 transition-all hover:shadow-md flex flex-col items-center justify-center text-center leading-relaxed', !selectedInsurancePlanId ? 'border-pink-500 bg-pink-50' : 'border-gray-100 bg-white hover:border-pink-200']">
                      <div v-if="!selectedInsurancePlanId" class="absolute top-3 right-3 w-5 h-5 bg-pink-500 rounded-full flex items-center justify-center">
                        <svg class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                      </div>
                      <div class="w-12 h-12 rounded-full bg-gray-50 flex items-center justify-center mb-3">
                        <svg class="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                      </div>
                      <h4 class="text-sm font-black text-gray-900 tracking-tight">No Insurance</h4>
                      <p class="text-[10px] text-gray-400 mt-1 uppercase font-bold">Recommended: Yes</p>
                    </div>

                    <div v-for="plan in filteredInsurancePlans" :key="plan.id"
                      @click="selectInsurance(plan)"
                      :class="['relative cursor-pointer rounded-sm border-2 p-5 transition-all hover:shadow-md flex flex-col h-full', selectedInsurancePlanId === plan.id ? 'border-emerald-500 bg-emerald-50/50 scale-[1.02] shadow-lg shadow-emerald-50' : 'border-gray-200 bg-white hover:border-emerald-300']">
                      
                      <div v-if="selectedInsurancePlanId === plan.id" class="absolute top-3 right-3 w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center">
                        <svg class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                      </div>

                      <!-- Airline Indicator Badge -->
                      <div class="flex flex-wrap gap-1.5 mb-3">
                        <span v-for="airlineId in (plan.airlines || [])" :key="airlineId"
                          class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-tight"
                          :class="getPlanAirlineStyle(airlineId)">
                          <span>✈</span>
                          {{ getPlanAirlineName(airlineId) }}
                        </span>
                        <span v-if="!plan.airlines || plan.airlines.length === 0"
                          class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-tight bg-gray-100 text-gray-600">
                          <span>✈</span> All Airlines
                        </span>
                      </div>

                      <div class="flex items-center gap-3 mb-3">
                        <div class="w-10 h-10 rounded-sm bg-emerald-100 flex items-center justify-center flex-shrink-0">
                          <svg class="w-6 h-6 text-emerald-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
                        </div>
                        <div>
                          <h4 class="text-sm font-black text-gray-900 tracking-tight">{{ plan.name }}</h4>
                          <p class="text-[10px] text-gray-500">By {{ plan.provider_name }}</p>
                        </div>
                      </div>

                      <p class="text-xs text-gray-600 flex-1 leading-relaxed">{{ plan.description }}</p>
                      
                      <div class="mt-4 pt-4 border-t border-emerald-100 flex items-center justify-between">
                        <span class="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded uppercase tracking-wider">Per Passenger</span>
                        <span class="text-base font-black text-emerald-600">&#8369;{{ parseFloat(plan.retail_price).toLocaleString() }}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div class="bg-blue-50 border border-blue-100 rounded-sm p-4 mt-6">
                    <div class="flex gap-3">
                      <div class="text-blue-600 text-lg">&#x2139;&#xFE0F;</div>
                      <div>
                        <p class="text-xs font-bold text-blue-900">Why buy protection?</p>
                        <p class="text-[11px] text-blue-700 mt-1 leading-relaxed">
                          Medical costs abroad can exceed ₱1,000,000. Travel protection reimburses you for these costs, plus flight delays and lost baggage. 
                          <a href="#" class="font-bold underline ml-1">View Full Policy Terms</a>
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>

          <!-- Footer Nav -->
          <div class="flex items-center justify-between pt-2">
            <button @click="$router.back()" class="flex items-center gap-2 px-5 py-2.5 border border-gray-300 rounded-sm text-sm font-semibold text-gray-600 hover:bg-gray-50 transition-colors">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
              Back
            </button>
            <button @click="saveAndContinue" class="hidden lg:flex items-center gap-2 px-6 py-2.5 bg-[#FF579A] hover:bg-[#FF4081] text-white rounded-sm text-sm font-bold shadow-lg shadow-pink-200 transition-all active:scale-[0.98]">
              Continue to Review
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
            </button>
          </div>
        </main>

        <!-- STICKY SIDEBAR -->
        <aside class="w-full lg:w-72 xl:w-80 flex-shrink-0">
          <BookingTimer variant="sidebar" />
          <div class="sticky top-5 space-y-3 mt-3">
            <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
              <div class="bg-gradient-to-r from-[#003870] to-[#004f9e] px-5 py-3.5">
                <p class="text-xs font-bold uppercase tracking-widest text-white/70">Price Breakdown</p>
              </div>
              <div class="p-5 space-y-2.5">
                <!-- Base Fares -->
                <p class="text-[9px] font-bold uppercase tracking-widest text-white/50 mb-1">Base Fares</p>
                <div v-if="bookingStore.passengerCount.adults > 0" class="flex justify-between items-center">
                  <span class="text-xs text-gray-500">{{ bookingStore.passengerCount.adults }} Adult(s) Base</span>
                  <AnimatedNumber :value="bookingStore.grandTotalForAdults" prefix="&#8369;" class="text-xs font-semibold text-gray-900" />
                </div>
                <div v-if="bookingStore.passengerCount.children > 0" class="flex justify-between items-center">
                  <span class="text-xs text-gray-500">{{ bookingStore.passengerCount.children }} Child(ren)</span>
                  <AnimatedNumber :value="bookingStore.grandTotalForChildren" prefix="&#8369;" class="text-xs font-semibold text-gray-900" />
                </div>
                <div v-if="bookingStore.passengerCount.infants > 0" class="flex justify-between items-center">
                  <span class="text-xs text-gray-500">{{ bookingStore.passengerCount.infants }} Infant(s) (50%)</span>
                  <AnimatedNumber :value="bookingStore.grandTotalForInfants" prefix="&#8369;" class="text-xs font-semibold text-gray-900" />
                </div>

                <!-- Add-ons Breakdown -->
                <div v-if="totalSeats > 0 || totalBaggage > 0 || totalMeals > 0 || totalAssistance > 0 || insurancePrice > 0" class="border-t border-dashed border-gray-100 pt-2.5 mt-2 space-y-2.5">
                  <p class="text-[9px] font-bold uppercase tracking-widest text-gray-400 mb-1">Add-ons</p>
                  <div v-if="totalSeats > 0 || isAnySegmentPremium" id="sidebar-seats" class="flex justify-between items-center">
                    <span class="text-xs text-gray-500 flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-blue-400 flex-shrink-0"></span>Seat Selection</span>
                    <span v-if="totalSeats === 0 && isAnySegmentPremium" class="text-[10px] font-bold text-emerald-600">INCLUDED</span>
                    <AnimatedNumber v-else :value="totalSeats" prefix="&#8369;" class="text-xs font-semibold text-gray-900" />
                  </div>
                  <div v-if="totalBaggage > 0" id="sidebar-baggage" class="flex justify-between items-center">
                    <span class="text-xs text-gray-500 flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-pink-400 flex-shrink-0"></span>Baggage</span>
                    <AnimatedNumber :value="totalBaggage" prefix="&#8369;" class="text-xs font-semibold text-gray-900" />
                  </div>
                  <div v-if="totalMeals > 0" id="sidebar-meals" class="flex justify-between items-center">
                    <span class="text-xs text-gray-500 flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-orange-400 flex-shrink-0"></span>Meals</span>
                    <AnimatedNumber :value="totalMeals" prefix="&#8369;" class="text-xs font-semibold text-gray-900" />
                  </div>
                  <div v-if="totalAssistance > 0" id="sidebar-assistance" class="flex justify-between items-center">
                    <span class="text-xs text-gray-500 flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-purple-400 flex-shrink-0"></span>Assistance</span>
                    <AnimatedNumber :value="totalAssistance" prefix="&#8369;" class="text-xs font-semibold text-gray-900" />
                  </div>
                  <div v-if="insurancePrice > 0" id="sidebar-insurance" class="flex justify-between items-center">
                    <span class="text-xs text-gray-500 flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400 flex-shrink-0"></span>Insurance</span>
                    <AnimatedNumber :value="insurancePrice" prefix="&#8369;" class="text-xs font-semibold text-gray-900" />
                  </div>
                </div>



                <!-- Grand Total -->
                <div class="border-t border-gray-200 pt-3 mt-4">
                  <div id="sidebar-total" class="flex justify-between items-center">
                    <span class="text-gray-900 font-black text-lg">Total Amount</span>
                    <span class="text-3xl font-black text-gray-900 flex items-center">
                      <span class="text-pink-500 text-xl mr-1">₱</span>
                      <AnimatedNumber :value="grandTotal" />
                    </span>
                  </div>
                  <p class="text-[10px] text-gray-400 mt-1 text-right">Inclusive of taxes &amp; fees</p>
                </div>
              </div>
            </div>
            <button @click="saveAndContinue" class="w-full py-3.5 bg-[#FF579A] hover:bg-[#FF4081] text-white rounded-sm text-sm font-bold shadow-lg shadow-pink-200 transition-all active:scale-[0.98] flex items-center justify-center gap-2">
              Continue to Review
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
            </button>
          </div>
        </aside>
      </div>
    </div>

    <MobileBookingFooter button-text="Continue to Review" @next="saveAndContinue" />

    <!-- CONFIRMATION MODAL -->
    <Transition name="fade">
      <div v-if="showConfirmationModal" class="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-end sm:items-center justify-center p-4" @click.self="closeConfirmationModal">
        <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl overflow-hidden">
          <div class="relative px-6 py-5 border-b border-gray-100">
            <h3 class="text-base font-bold text-gray-900">{{ modalTitle }}</h3>
            <button @click="closeConfirmationModal" class="absolute right-4 top-4 w-7 h-7 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors">
              <svg class="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
          <div class="px-6 py-5 space-y-3">
            <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-sm">
              <div class="w-9 h-9 rounded-full bg-[#003870] flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                {{ modalData.passenger?.firstName?.charAt(0) }}{{ modalData.passenger?.lastName?.charAt(0) }}
              </div>
              <div>
                <p class="text-sm font-semibold text-gray-900">{{ modalData.passenger?.firstName }} {{ modalData.passenger?.lastName }}</p>
                <p class="text-xs text-gray-500">{{ modalData.passenger?.type }}</p>
              </div>
            </div>
            <template v-if="modalType === 'baggage'">
              <div v-if="modalData.option" class="flex items-center justify-between p-3 rounded-sm border border-pink-100 bg-pink-50">
                <div class="flex items-center gap-2"><span class="text-xl">&#x1F9F3;</span><span class="text-sm font-bold text-gray-900">{{ modalData.option.formatted_weight }} Extra Baggage</span></div>
                <span class="text-sm font-black text-pink-500">&#8369;{{ parseFloat(modalData.option.price).toLocaleString() }}</span>
              </div>
              <p v-if="modalData.option" class="text-xs text-amber-600 bg-amber-50 rounded-sm p-3">&#x26A0;&#xFE0F; Baggage cannot be changed after payment.</p>
              <p v-else class="text-xs text-red-600 bg-red-50 rounded-sm p-3">&#x26A0;&#xFE0F; You are removing the baggage selection.</p>
            </template>
            <template v-if="modalType === 'meal'">
              <div v-if="modalData.option" class="flex items-start gap-3 p-3 rounded-sm border border-pink-100 bg-pink-50">
                <span class="text-xl">&#x1F37D;&#xFE0F;</span>
                <div><p class="text-sm font-bold text-gray-900">{{ modalData.option.name }}</p><p class="text-sm font-black text-pink-500 mt-1">&#8369;{{ parseFloat(modalData.option.price).toLocaleString() }}</p></div>
              </div>
              <p class="text-xs text-amber-600 bg-amber-50 rounded-sm p-3">&#x23F0; Meals cannot be changed within 24 hours of departure.</p>
            </template>
            <template v-if="modalType === 'assistance'">
              <div v-if="modalData.option" class="flex items-start gap-3 p-3 rounded-sm border border-pink-100 bg-pink-50">
                <span class="text-xl">&#x267F;</span>
                <div>
                  <p class="text-sm font-bold text-gray-900">{{ modalData.option.name }}</p>
                  <p class="text-sm font-black mt-1" :class="modalData.option.price > 0 ? 'text-pink-500' : 'text-emerald-600'">
                    {{ modalData.option.price > 0 ? "&#8369;" + parseFloat(modalData.option.price).toLocaleString() : "FREE" }}
                  </p>
                </div>
              </div>
              <p class="text-xs text-blue-600 bg-blue-50 rounded-sm p-3">&#x2139;&#xFE0F; Please arrive 2 hours before departure for assistance check-in.</p>
            </template>
          </div>
          <div class="px-6 py-4 border-t border-gray-100 flex items-center gap-3">
            <button @click="closeConfirmationModal" class="flex-1 py-2.5 rounded-sm border border-gray-200 text-sm font-semibold text-gray-600 hover:bg-gray-50 transition-colors">Cancel</button>
            <button @click="confirmSelection" class="flex-1 py-2.5 rounded-sm bg-[#FF579A] hover:bg-[#FF4081] text-white text-sm font-bold shadow-sm transition-all active:scale-[0.98]">Confirm</button>
          </div>
        </div>
      </div>
    </Transition>

    <FlyingIcon ref="flyingIconRef" />

    <LoadingOverlay 
      :show="isNavigating" 
      title="Preparing Your Review"
      subtitle="Just a moment while we bundle your selections."
    />
  </div>
</template>
<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useRouter, useRoute } from 'vue-router';
import { addonService } from '@/services/booking/addonService';
import api from '@/services/api/axios';
import BookingTimer from '@/components/booking/BookingTimer.vue';
import AnimatedNumber from '@/components/common/AnimatedNumber.vue';
import FlyingIcon from '@/components/common/FlyingIcon.vue';
import BookingStatusHeader from '@/components/booking/BookingStatusHeader.vue';
import MobileBookingFooter from '@/components/booking/MobileBookingFooter.vue';
import LoadingOverlay from '@/components/common/LoadingOverlay.vue';

const bookingStore = useBookingStore();
const router = useRouter();
const route = useRoute();
const currentTab = ref('baggage');
const activeSegment = ref('depart');
const isLoading = ref(true);
const isNavigating = ref(false);
const showConfirmationModal = ref(false);
const modalType = ref('');
const modalTitle = ref('');
const modalData = ref({ passenger: null, option: null, passengerKey: '', isDeselecting: false, segment: 'depart' });
const instance = ref(null);
const flyingIconRef = ref(null);
const baggageOptionsMap = reactive({});
const mealOptionsMap = reactive({});
const assistanceOptionsMap = reactive({});
const insurancePlans = ref([]);
const selectedAddons = reactive({
  baggage: {},
  meals: {},
  wheelchair: {},
  seats: bookingStore.addons?.seats || {},
  insurance: bookingStore.addons?.insurance || { selectedPlanId: null, price: 0 }
});
const backendBreakdown = ref(null);

// Map airline codes (from flight API) → DB IDs (stored on insurance plans)
const AIRLINE_CODE_TO_ID = { 'PR': 81, '5J': 82, 'Z2': 83, 'T6': 84 };

const resolveAirlineNumericId = (flight) => {
  if (!flight) return null;
  // If we already have a numeric airline_id, use it
  if (flight.airline_id && !isNaN(Number(flight.airline_id))) return Number(flight.airline_id);
  // If airline is an object with id
  if (flight.airline && typeof flight.airline === 'object' && flight.airline.id) return Number(flight.airline.id);
  // Map from airline_code string (e.g. 'PR') → numeric ID
  const code = flight.airline_code || (typeof flight.airline === 'string' ? flight.airline : '') || '';
  if (code && AIRLINE_CODE_TO_ID[code.toUpperCase()]) return AIRLINE_CODE_TO_ID[code.toUpperCase()];
  // Try flight_number prefix as last resort
  if (flight.flight_number) {
    const prefix = flight.flight_number.substring(0, 2).toUpperCase();
    if (AIRLINE_CODE_TO_ID[prefix]) return AIRLINE_CODE_TO_ID[prefix];
  }
  return null;
};

const filteredInsurancePlans = computed(() => {
  const tripAirlineIds = new Set();
  const flightObjects = [];
  if (bookingStore.selectedOutbound) flightObjects.push(bookingStore.selectedOutbound);
  if (bookingStore.selectedReturn) flightObjects.push(bookingStore.selectedReturn);
  if (bookingStore.isMultiCity) {
     bookingStore.multiCitySegments.forEach(seg => { if (seg.selectedFlight) flightObjects.push(seg.selectedFlight); });
  }
  flightObjects.forEach(f => {
    const id = resolveAirlineNumericId(f);
    if (id) tripAirlineIds.add(id);
  });

  if (insurancePlans.value.length === 0) return [];

  // Try to get airline-specific plans first
  const airlineSpecific = insurancePlans.value.filter(plan =>
    plan.airlines && plan.airlines.length > 0 &&
    plan.airlines.some(airlineId => tripAirlineIds.has(Number(airlineId)))
  );

  // If we have airline-specific plans, return only those
  if (airlineSpecific.length > 0) return airlineSpecific;

  // Fallback: show global plans (no airline assigned)
  return insurancePlans.value.filter(plan => !plan.airlines || plan.airlines.length === 0);
});

// Airline lookup helpers for insurance plan badges
const AIRLINE_MAP = {
  81: { name: 'Philippine Airlines', style: 'bg-blue-100 text-blue-800 border border-blue-200' },
  82: { name: 'Cebu Pacific',         style: 'bg-orange-100 text-orange-800 border border-orange-200' },
  83: { name: 'AirAsia Philippines',  style: 'bg-red-100 text-red-800 border border-red-200' },
};

const getPlanAirlineName = (airlineId) => {
  return AIRLINE_MAP[airlineId]?.name || `Airline #${airlineId}`;
};

const getPlanAirlineStyle = (airlineId) => {
  return AIRLINE_MAP[airlineId]?.style || 'bg-gray-100 text-gray-700';
};

const baggagePolicies = {
  '5J': {
    airline: 'Cebu Pacific',
    concept: 'Weight Concept with Piece Limit',
    pieces: 'Max 3 pieces total per passenger',
    weightLimits: 'Options: 20kg, 24kg, 28kg, or 32kg',
    keyRule: 'No single bag can exceed 32kg.',
    pooling: 'Allowed for companions on same booking'
  },
  'PR': {
    airline: 'Philippine Airlines',
    concept: 'Piece Concept (Extra Bags Allowed)',
    pieces: 'Typically 1-2 pieces included; 1 extra bag (20kg) add-on',
    pooling: 'Sharing weight allowed with companions on same booking',
    keyRule: 'Pooling requires passengers to be on the same PNR/Booking.'
  },
  'Z2': {
    airline: 'AirAsia Philippines',
    concept: 'Weight Concept',
    pieces: 'No strict limit on pieces (total weight focus)',
    weightLimits: 'Options: 20kg up to 60kg total',
    keyRule: 'Bring as many bags as you want, as long as combined weight is within limit.'
  },
  'T6': {
    airline: 'AirSwift',
    concept: 'Restrictive Weight & Piece Concept',
    pieces: 'Max 2 pieces maximum due to cargo hold size',
    weightLimits: 'Max 20kg or 30kg total allowance',
    keyRule: 'Stricter due to small aircraft size (ATR).'
  }
};

const resolveAirlineId = (flight) => {
  return resolveAirlineNumericId(flight);
};

const getAirlineId = (segmentKey) => {
  const flight = segmentKey === 'depart' ? bookingStore.selectedOutbound : 
                 segmentKey === 'return' ? bookingStore.selectedReturn : 
                 bookingStore.multiCitySegments[parseInt(segmentKey)]?.selectedFlight;
  return resolveAirlineId(flight);
};

const getAirlineName = (segmentKey) => {
  const flight = segmentKey === 'depart' ? bookingStore.selectedOutbound : 
                 segmentKey === 'return' ? bookingStore.selectedReturn : 
                 bookingStore.multiCitySegments[parseInt(segmentKey)]?.selectedFlight;
  if (!flight) return '';
  return flight.airline_name || flight.airline?.name || 
         (flight.flight_number?.startsWith('PR') ? 'Philippine Airlines' : 
          flight.flight_number?.startsWith('5J') ? 'Cebu Pacific' : 
          flight.flight_number?.startsWith('Z2') ? 'AirAsia' : '');
};

const currentBaggagePolicy = computed(() => {
  const flight = bookingStore.selectedOutbound;
  if (!flight) return null;
  
  // Try to get a string code (PR, 5J, etc.)
  let code = flight.airline_code || '';
  if (!code) {
    const raw = resolveAirlineId(flight);
    if (typeof raw === 'string' && raw.length === 2) code = raw;
    else if (flight.flight_number) code = flight.flight_number.substring(0, 2);
  }
  
  return baggagePolicies[code.toUpperCase()] || null;
});

const syncSelectionsFromStore = () => {
  const tripType = bookingStore.tripType;
  const segments = [];
  if (tripType === 'multi_city' || tripType === 'multi-city') {
    bookingStore.multiCitySegments.forEach((_, idx) => segments.push(idx.toString()));
  } else {
    segments.push('depart');
    if (tripType === 'round_trip' || tripType === 'round-trip') segments.push('return');
  }
  segments.forEach(seg => {
    if (!selectedAddons.baggage[seg]) selectedAddons.baggage[seg] = {};
    if (!selectedAddons.meals[seg]) selectedAddons.meals[seg] = {};
    if (!selectedAddons.wheelchair[seg]) selectedAddons.wheelchair[seg] = {};
    selectedAddons.baggage[seg] = { ...bookingStore.addons.baggage?.[seg] };
    
    // Ensure meals are arrays
    const storedMeals = bookingStore.addons.meals?.[seg] || {};
    Object.keys(storedMeals).forEach(pKey => {
      selectedAddons.meals[seg][pKey] = Array.isArray(storedMeals[pKey]) ? [...storedMeals[pKey]] : [];
    });
    
    selectedAddons.wheelchair[seg] = { ...bookingStore.addons.wheelchair?.[seg] };
  });
  selectedAddons.seats = bookingStore.addons?.seats ? { ...bookingStore.addons.seats } : {};
  selectedAddons.insurance = {
    selectedPlanId: bookingStore.addons?.insurance?.selectedPlanId || null,
    price: bookingStore.addons?.insurance?.price || 0
  };
};

const tripTypeInfo = computed(() => bookingStore.isRoundTrip ? 'Round Trip' : 'One Way');

const flightSegments = computed(() => {
  const tripType = bookingStore.tripType;
  if (tripType === 'multi_city' || tripType === 'multi-city') {
    return bookingStore.multiCitySegments.map((seg, idx) => ({
      key: idx.toString(), label: `Flight ${idx + 1}`, flight: seg.selectedFlight?.flight_number || 'N/A'
    }));
  }
  const segments = [{ key: 'depart', label: 'Depart Flight', flight: bookingStore.selectedOutbound?.flight_number || 'N/A' }];
  if (bookingStore.isRoundTrip) segments.push({ key: 'return', label: 'Return Flight', flight: bookingStore.selectedReturn?.flight_number || 'N/A' });
  return segments;
});

const activeSegmentLabel = computed(() => {
  const s = flightSegments.value.find(s => s.key === activeSegment.value);
  return s ? s.label : 'Flight';
});

const flightInfo = computed(() => {
  const info = [];
  const tripType = bookingStore.tripType;
  if (tripType === 'multi_city' || tripType === 'multi-city') {
    bookingStore.multiCitySegments.forEach((seg, idx) => {
      if (seg.selectedFlight) info.push({ type: `Flight ${idx + 1}`, flight: seg.selectedFlight.flight_number, route: `${seg.selectedFlight.origin} -> ${seg.selectedFlight.destination}`, price: parseFloat(seg.selectedFlight.price || 0) });
    });
    return info;
  }
  if (bookingStore.selectedOutbound) info.push({ type: 'Outbound', flight: bookingStore.selectedOutbound.flight_number, route: `${bookingStore.selectedOutbound.origin} -> ${bookingStore.selectedOutbound.destination}`, price: parseFloat(bookingStore.selectedOutbound.price || 0) });
  if (bookingStore.isRoundTrip && bookingStore.selectedReturn) info.push({ type: 'Return', flight: bookingStore.selectedReturn.flight_number, route: `${bookingStore.selectedReturn.origin} -> ${bookingStore.selectedReturn.destination}`, price: parseFloat(bookingStore.selectedReturn.price || 0) });
  return info;
});

const getBaggageSelection = (passengerKey, segment) => selectedAddons.baggage[segment]?.[passengerKey] || null;
const getMealSelection = (passengerKey, segment) => {
  return selectedAddons.meals[segment]?.[passengerKey] || [];
};
const getAssistanceSelection = (passengerKey, segment) => selectedAddons.wheelchair[segment]?.[passengerKey] || null;
const selectedInsurancePlanId = computed(() => bookingStore.addons?.insurance?.selectedPlanId || null);
const insurancePrice = computed(() => bookingStore.insurancePrice);

const segmentRoadmap = computed(() => {
  return flightSegments.value.map(seg => {
    const segKey = seg.key;
    const pax = bookingStore.passengers;
    const baggageDone = pax.every(p => !!bookingStore.addons.baggage[segKey]?.[p.key]);
    const mealsDone = pax.every(p => !!bookingStore.addons.meals[segKey]?.[p.key]);
    const seatsDone = pax.every(p => !!bookingStore.addons.seats[segKey]?.[p.key]);
    return { ...seg, baggageDone, mealsDone, seatsDone, isComplete: baggageDone && mealsDone && seatsDone };
  });
});

const handleCopyAddon = (type, passenger) => { bookingStore.copyAddonToAllSegments(type, passenger.key, activeSegment.value); };
const selectInsurance = (plan) => { if (!plan) return; bookingStore.selectInsurancePlan(plan.id, plan.retail_price); selectedAddons.insurance = { selectedPlanId: plan.id, price: parseFloat(plan.retail_price) || 0 }; };
const removeInsurance = () => { bookingStore.clearInsurance(); selectedAddons.insurance = { selectedPlanId: null, price: 0 }; };

onMounted(async () => {
  try {
    bookingStore.migrateAddonsToNewFormat();
    
    // Identify all unique airlines in the booking
    const uniqueAirlines = new Set();
    const flightObjects = [];
    if (bookingStore.selectedOutbound) flightObjects.push(bookingStore.selectedOutbound);
    if (bookingStore.selectedReturn) flightObjects.push(bookingStore.selectedReturn);
    if (bookingStore.isMultiCity) {
      bookingStore.multiCitySegments.forEach(seg => { if (seg.selectedFlight) flightObjects.push(seg.selectedFlight); });
    }

    flightObjects.forEach(f => {
      const id = resolveAirlineId(f);
      if (id) uniqueAirlines.add(id);
    });

    const airlineIds = Array.from(uniqueAirlines);
    
    // Fetch for each unique airline
    const insurancePromise = api.get('/flightapp/api/insurance-plans/').catch(() => null);
    
    const fetchPromises = airlineIds.map(async (id) => {
      try {
        const [bagRes, mealRes, assistRes] = await Promise.all([
          addonService.getBaggageOptions(id),
          addonService.getMealOptions(id),
          addonService.getAssistanceServices(id)
        ]);
        
        baggageOptionsMap[id] = bagRes.data.results || bagRes.data || [];
        mealOptionsMap[id] = mealRes.data.results || mealRes.data || [];
        assistanceOptionsMap[id] = assistRes.data.results || assistRes.data || [];
      } catch (err) {
        console.error(`Failed to load addons for airline ${id}:`, err);
      }
    });

    const [insuranceRes] = await Promise.all([insurancePromise, ...fetchPromises]);

    if (insuranceRes && insuranceRes.data) {
      const data = insuranceRes.data;
      insurancePlans.value = Array.isArray(data) ? data : (data?.results || []);
    } else { insurancePlans.value = []; }
    
    syncSelectionsFromStore();
  } catch (error) { console.error('Failed to load add-ons:', error); } finally { isLoading.value = false; }
});

const getOptionById = (list, id) => list.find(i => i.id === id) || null;

// BENEFIT TRACKING (Real-time synchronization with Fare Families)
const isBaggageIncluded = (opt, segmentKey) => {
  const flight = segmentKey === 'depart' ? bookingStore.selectedOutbound : 
                 segmentKey === 'return' ? bookingStore.selectedReturn : 
                 bookingStore.multiCitySegments[parseInt(segmentKey)]?.selectedFlight;
  
  // If price is 0 or less, definitely "included" (free), so hide it from extra baggage
  if (parseFloat(opt.price) <= 0) return true;
  
  if (!flight) return false;
  
  const features = Array.isArray(flight.seat_class_features) ? flight.seat_class_features : [];
  const checkedBaggageFeature = features.find(f => typeof f === 'string' && (f.toLowerCase().includes('checked baggage') || f.toLowerCase().includes('check-in baggage')));
  
  if (!checkedBaggageFeature || (typeof checkedBaggageFeature === 'string' && checkedBaggageFeature.toLowerCase().includes('no '))) {
    return false;
  }
  
  // Extract allowance from features (e.g., "10kg Checked baggage", "20kg")
  const weightMatch = checkedBaggageFeature.match(/(\d+)kg/i);
  if (!weightMatch) return false;
  
  const allowance = parseInt(weightMatch[1]);
  const weight = opt.weight_kg || opt.weight || 0;
  
  // If the baggage option weight is less than or equal to what's already included, it should be $0 (hidden)
  return weight > 0 && weight <= allowance;
};

const selectBaggageDirect = (passenger, option, segment, event) => {
  const passengerKey = passenger.key;
  const cur = getBaggageSelection(passengerKey, segment);
  
  // If it's included, it's basically "selected" by default or should be $0
  const isIncluded = isBaggageIncluded(option, segment);
  
  if (cur && cur.id === option.id) {
    selectedAddons.baggage[segment][passengerKey] = null;
    bookingStore.removeBaggageAddon(passengerKey, segment);
  } else {
    const price = isIncluded ? 0 : (parseFloat(option.price) || 0);
    const obj = { 
      id: option.id, 
      price: price, 
      formatted_weight: option.formatted_weight, 
      name: option.formatted_weight,
      is_included: isIncluded
    };
    selectedAddons.baggage[segment][passengerKey] = obj;
    bookingStore.updateBaggageAddon(passengerKey, obj, segment);
    if (event && flyingIconRef.value) flyingIconRef.value.fly(event.currentTarget, '#sidebar-baggage', 'bag');
  }
  bookingStore.snapshotToServer();
};

const isMealIncluded = (segmentKey) => {
  const flight = segmentKey === 'depart' ? bookingStore.selectedOutbound : 
                 segmentKey === 'return' ? bookingStore.selectedReturn : 
                 bookingStore.multiCitySegments[parseInt(segmentKey)]?.selectedFlight;
  
  if (!flight) return false;
  
  const features = Array.isArray(flight.seat_class_features) ? flight.seat_class_features : [];
  return features.some(f => typeof f === 'string' && (f.toLowerCase().includes('meal') || f.toLowerCase().includes('snack') || f.toLowerCase().includes('food')));
};

const selectMealDirect = (passenger, option, segment, event) => {
  const passengerKey = passenger.key;
  if (!option) {
    // Clear all meals
    selectedAddons.meals[segment][passengerKey] = [];
    bookingStore.clearMealsForPassenger(passengerKey, segment);
  } else {
    // Toggle meal: check if already in array
    const meals = getMealSelection(passengerKey, segment);
    const exists = meals.some(m => m.id === option.id);
    
    if (exists) {
      bookingStore.removeMealAddon(passengerKey, option.id, segment);
    } else {
      const isIncluded = isMealIncluded(segment);
      const price = isIncluded ? 0 : (parseFloat(option.price) || 0);
      
      const obj = { 
        id: option.id, 
        price: price, 
        name: option.name, 
        meal_type: option.meal_type, 
        description: option.description,
        is_included: isIncluded
      };
      bookingStore.updateMealAddon(passengerKey, obj, segment);
      if (event && flyingIconRef.value) flyingIconRef.value.fly(event.currentTarget, '#sidebar-meals', 'meal');
    }
  }
  syncSelectionsFromStore();
  bookingStore.snapshotToServer();
};

const selectAssistanceDirect = (passenger, option, segment, event) => {
  const passengerKey = passenger.key;
  if (!option) {
    selectedAddons.wheelchair[segment][passengerKey] = null;
    bookingStore.removeAssistanceAddon(passengerKey, segment);
  } else if (getAssistanceSelection(passengerKey, segment)?.id === option.id) {
    selectedAddons.wheelchair[segment][passengerKey] = null;
    bookingStore.removeAssistanceAddon(passengerKey, segment);
  } else {
    const obj = { 
      id: option.id, 
      price: parseFloat(option.price) || 0, 
      name: option.name, 
      service_type: option.service_type, 
      description: option.description 
    };
    selectedAddons.wheelchair[segment][passengerKey] = obj;
    bookingStore.updateAssistanceAddon(passengerKey, obj, segment);
    if (event && flyingIconRef.value && option) flyingIconRef.value.fly(event.currentTarget, '#sidebar-assistance', 'assist');
  }
  bookingStore.snapshotToServer();
};

const showMealConfirmation = (passenger, option, segment) => { modalType.value = 'meal'; modalTitle.value = option ? 'Confirm Meal Selection' : 'Remove Meal'; modalData.value = { passenger, option, passengerKey: passenger.key, isDeselecting: false, segment }; showConfirmationModal.value = true; };
const showAssistanceConfirmation = (passenger, option, segment) => { modalType.value = 'assistance'; modalTitle.value = option ? 'Confirm Assistance' : 'Remove Assistance'; modalData.value = { passenger, option, passengerKey: passenger.key, isDeselecting: false, segment }; showConfirmationModal.value = true; };

const closeConfirmationModal = () => {
  showConfirmationModal.value = false;
  modalData.value = { passenger: null, option: null, passengerKey: '', isDeselecting: false, segment: 'depart' };
  modalType.value = '';
  modalTitle.value = '';
};

const confirmSelection = () => {
  const { passengerKey, option, segment } = modalData.value;
  if (modalType.value === 'meal') {
    if (!option) { selectedAddons.meals[segment][passengerKey] = null; bookingStore.removeMealAddon(passengerKey, segment); }
    else { const obj = { id: option.id, price: parseFloat(option.price) || 0, name: option.name, meal_type: option.meal_type, description: option.description }; selectedAddons.meals[segment][passengerKey] = obj; bookingStore.updateMealAddon(passengerKey, obj, segment); }
  } else if (modalType.value === 'assistance') {
    if (!option) { 
      selectedAddons.wheelchair[segment][passengerKey] = null; 
      bookingStore.removeAssistanceAddon(passengerKey, segment); 
    } else { 
      const obj = { 
        id: option.id, 
        price: parseFloat(option.price) || 0, 
        name: option.name, 
        service_type: option.service_type, 
        description: option.description 
      };
      selectedAddons.wheelchair[segment][passengerKey] = obj; 
      bookingStore.updateAssistanceAddon(passengerKey, obj, segment); 
    }
  }
  bookingStore.snapshotToServer();
  closeConfirmationModal();
};

const eligiblePassengers = computed(() => bookingStore.passengers.filter(p => p.type !== 'Infant'));

// Returns true if ANY baggage option for this segment is already included in the fare
const isAnyBaggageIncludedForSegment = (segmentKey) => {
  const options = baggageOptionsMap[getAirlineId(segmentKey)] || [];
  if (!options.length) return false;
  return options.some(opt => isBaggageIncluded(opt, segmentKey));
};
const indicatorStyle = computed(() => {
  const tabs = ['baggage', 'seat', 'meals', 'wheelchair'];
  const idx = tabs.indexOf(currentTab.value);
  return { left: `${(idx * 100 / 4) + 12.5}%`, transform: 'translateX(-50%)' };
});
const baseFare = computed(() => bookingStore.combinedBasePriceTotal);
const totalBaggage = computed(() => bookingStore.totalBaggagePrice);
const totalMeals = computed(() => bookingStore.totalMealsPrice);
const totalAssistance = computed(() => bookingStore.totalAssistancePrice);
const totalSeats = computed(() => bookingStore.totalSeatsPrice);
const isAnySegmentPremium = computed(() => {
  return Object.values(bookingStore.fareFamilies).some(f => f === 'premium');
});

const addonsSubtotal = computed(() => {
  return (totalBaggage.value || 0) + (totalMeals.value || 0) + (totalSeats.value || 0) + 
         (totalAssistance.value || 0) + (bookingStore.insurancePrice || 0);
});
const grandTotal = computed(() => bookingStore.authoritativeTotal);
const saveAndContinue = () => { 
  isNavigating.value = true;
  setTimeout(() => {
    router.push({ name: 'ReviewBooking' }); 
  }, 800);
};
</script>

<style scoped>
.pal-bg { background: #f4f7f9; min-height: 100vh; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: scale(0.97); }
</style>
