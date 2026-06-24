<template>
  <div class="review-booking-container pb-32 lg:pb-0">
    <BookingStatusHeader />

    <!-- Loading State -->
    <LoadingOverlay 
      :show="isLoading" 
      title="Checking Reservation"
      subtitle="Just a moment while we bundle your selections."
    />

    <!-- No Data State -->
    <div v-if="!isLoading && !hasFlightData" class="no-data-message">
      <h3>No flight data found</h3>
      <p>Please go back and select a flight first.</p>
      <button @click="$router.push({ name: 'Home' })" class="btn-back">
        Back to Flight Search
      </button>
    </div>

    <!-- Main Content -->
    <div v-else-if="!isLoading" class="container review-layout">
      <main class="main-content">
        <h2 class="page-title">Review Your Booking</h2>

        <div class="itinerary-header mb-6 sm:mb-8">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-4 sm:p-6 rounded-xl border border-slate-200 shadow-sm">
            <div>
              <p class="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Electronic Ticket Identification (PNR)</p>
              <h2 class="text-3xl sm:text-4xl md:text-5xl font-black text-slate-900 tracking-tighter">{{ generatedPNR }}</h2>
            </div>
            <div class="text-left sm:text-right">
              <p class="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Booking Status</p>
              <span class="inline-flex px-3 py-1 bg-amber-50 text-amber-700 text-[10px] font-black rounded-md border border-amber-100 uppercase tracking-widest">Awaiting Confirmation</span>
            </div>
          </div>
        </div>

        <section class="review-section">
          <div class="section-header">
            <span class="icon">✈️</span>
            <h3>Flight Itinerary</h3>
            <span class="trip-type-badge" :class="{ 
              'round-trip': bookingStore.isRoundTrip, 
              'one-way': bookingStore.tripType === 'one_way',
              'multi-city': bookingStore.tripType === 'multi_city' || bookingStore.tripType === 'multi-city'
            }">
              {{ 
                bookingStore.tripType === 'multi_city' || bookingStore.tripType === 'multi-city' 
                  ? 'Multi-City' 
                  : (bookingStore.isRoundTrip ? 'Round Trip' : 'One Way') 
              }}
            </span>
          </div>
          
          <div class="space-y-4">
            <div v-for="(segment, index) in flightSegments" :key="index" class="boarding-pass-card bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col lg:flex-row">
              <div class="pass-left p-5 sm:p-8 flex-1 relative border-b lg:border-b-0 lg:border-r lg:border-dashed border-slate-200">
                <div class="absolute -bottom-3 -right-3 w-6 h-6 bg-slate-50 rounded-full hidden lg:block"></div>
                <div class="absolute -top-3 -right-3 w-6 h-6 bg-slate-50 rounded-full hidden lg:block"></div>
                
                <div class="flex items-center justify-between mb-8">
                  <div class="flex items-center gap-3">
                    <div class="airline-brand flex items-center gap-3">
                       <div :class="['w-10 h-10 rounded-lg flex items-center justify-center font-black text-white text-[10px]', segment.airline_class]">
                        {{ segment.airline_code }}
                       </div>
                       <div>
                         <div class="text-[10px] font-black text-slate-900 uppercase tracking-widest leading-none mb-1.5">{{ segment.airline_name }}</div>
                         <div class="flex items-center gap-2">
                           <span class="px-2 py-0.5 bg-slate-900 text-white text-[9px] font-black rounded uppercase tracking-tighter">{{ segment.flight_number }}</span>
                           <span class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">{{ segment.label }}</span>
                         </div>
                       </div>
                    </div>
                  </div>
                  <span class="text-[10px] font-black text-emerald-600 uppercase tracking-widest bg-emerald-50 px-2 py-1 rounded">Confirmed</span>
                </div>

                <div class="flex items-center justify-between gap-4 py-2">
                  <div class="text-left">
                    <h4 class="text-3xl sm:text-5xl font-black text-slate-900 tracking-tighter leading-none">{{ segment.origin }}</h4>
                    <p class="text-[9px] text-slate-400 font-bold uppercase tracking-[0.2em] mt-2">Departure</p>
                  </div>
                  
                  <div class="flex-1 flex flex-col items-center px-2">
                    <div class="w-full border-t-2 border-dashed border-slate-200 relative mt-2">
                      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 px-3 bg-white">
                        <svg class="w-5 h-5 text-pink-500 rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                      </div>
                    </div>
                  </div>

                  <div class="text-right">
                    <h4 class="text-3xl sm:text-5xl font-black text-slate-900 tracking-tighter leading-none">{{ segment.destination }}</h4>
                    <p class="text-[9px] text-slate-400 font-bold uppercase tracking-[0.2em] mt-2">Arrival</p>
                  </div>
                </div>

                <div class="mt-10 grid grid-cols-2 md:grid-cols-3 gap-y-8 gap-x-4">
                  <div>
                    <label class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] block mb-1.5">Schedule</label>
                    <p class="text-xs font-black text-slate-700 leading-tight">{{ formatDate(segment.departure_time) }}</p>
                  </div>
                  <div>
                    <label class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] block mb-1.5">Class & Fare</label>
                    <p class="text-xs font-black text-slate-700 uppercase tracking-tighter">
                      {{ segment.class_type }}
                      <span v-if="bookingStore.fareFamilyNames?.[segment.key] || bookingStore.fareFamilies[segment.key]" class="text-pink-600">
                        ({{ bookingStore.fareFamilyNames?.[segment.key] || formatFareFamily(bookingStore.fareFamilies[segment.key]) }})
                      </span>
                    </p>
                  </div>
                  <div class="hidden sm:block">
                    <label class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] block mb-1.5">Terminal</label>
                    <p class="text-xs font-black text-slate-700 uppercase tracking-tighter">Terminal 2</p>
                  </div>
                  <div v-if="segment.aircraft">
                    <label class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] block mb-1.5">Aircraft</label>
                    <p class="text-xs font-black text-slate-700 uppercase tracking-tighter">{{ segment.aircraft }}</p>
                  </div>
                </div>
              </div>
              
              <div class="pass-right bg-slate-50/80 p-5 sm:p-8 lg:w-64 flex flex-col justify-center relative">
                <!-- Tear Line for tear-off effect -->
                <div class="absolute top-0 left-0 bottom-0 w-px border-l-2 border-dashed border-slate-200 hidden lg:block"></div>
                
                <div class="flex lg:flex-col justify-between lg:justify-center items-center gap-6">
                  <div class="text-left lg:text-center">
                    <label class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] block mb-2">Gate Group</label>
                    <div class="flex items-center lg:justify-center gap-3">
                      <div class="w-12 h-12 bg-white rounded-xl flex items-center justify-center border border-slate-200 shadow-sm">
                        <span class="text-xl font-black text-slate-900">B</span>
                      </div>
                      <div class="text-left">
                        <p class="text-xs font-black text-slate-900 leading-none">Zone 3</p>
                        <p class="text-[9px] font-bold text-pink-600 uppercase tracking-widest mt-1">Standard</p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="flex flex-col items-center">
                    <div class="w-20 h-20 bg-white border border-slate-200 rounded-xl p-2 mb-2 shadow-sm ring-4 ring-slate-100/50">
                      <svg class="w-full h-full text-slate-800" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M3 3h8v8H3V3zm2 2v4h4V5H5zm8-2h8v8h-8V3zm2 2v4h4V5h-4zM3 13h8v8H3v-8zm2 2v4h4v-4H5zm13-2h3v2h-3v-2zm-3 0h2v2h-2v-2zm3 3h3v2h-3v-2zm-3 0h2v2h-2v-2zm3 3h3v2h-3v-2zm-3 0h2v2h-2v-2zm-3-3h2v2h-2v-2zm-3 0h2v2h-2v-2zm3 3h2v2h-2v-2zm-3 0h2v2h-2v-2z" />
                      </svg>
                    </div>
                    <p class="text-[7px] font-black text-slate-400 tracking-[0.3em] uppercase">{{ segment.flight_number }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="review-section">
          <div class="section-header">
            <span class="icon">👥</span>
            <h3>Passengers & Add-ons</h3>
          </div>
          
          <div v-for="(segment, index) in flightSegments" :key="'addons-' + index" class="review-card" :class="{ 'mt-3': index > 0 }">
            <div class="summary-header segment-summary-header" :class="{ 'return': segment.isReturn, 'multi': segment.isMultiCity }">
              <span class="badge" :class="{ 'return': segment.isReturn, 'multi': segment.isMultiCity }">{{ segment.typeLabel }}</span>
              <span class="segment-route">{{ segment.route }}</span>
            </div>
            <!-- Desktop Table View -->
            <div class="hidden md:block overflow-x-auto">
              <table class="review-table">
                <thead>
                  <tr>
                    <th>Passenger</th>
                    <th>Seat</th>
                    <th>Baggage</th>
                    <th>Meal</th>
                    <th>Assistance</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="p in bookingStore.passengers" :key="p.key">
                    <td class="whitespace-nowrap">
                      <div class="font-black text-slate-800">{{ formatTitle(p.title) }} {{ p.firstName }} {{ p.lastName }}</div>
                      <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-0.5">
                        {{ p.type }}
                        <span v-if="p.phDiscountType === 'senior'" class="text-pink-600 ml-1">(Senior Citizen)</span>
                        <span v-if="p.phDiscountType === 'pwd'" class="text-pink-600 ml-1">(PWD)</span>
                      </div>
                    </td>
                    <td class="font-bold text-slate-700">{{ getSeatLabel(p.key, segment.key) }}</td>
                    <td>
                      <div v-for="item in getBaggageBreakdown(p.key, segment.key)" :key="item.type" class="flex items-center gap-2 mb-1 last:mb-0">
                        <span class="text-xs">{{ item.icon }}</span>
                        <span class="text-[11px] font-bold text-slate-600">{{ item.label }}</span>
                      </div>
                    </td>
                    <td class="text-xs font-bold text-slate-700">{{ getMealLabel(p.key, segment.key) }}</td>
                    <td class="text-xs font-bold text-slate-700">{{ getAssistanceLabel(p.key, segment.key) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Mobile Card View -->
            <div class="md:hidden space-y-4">
              <div v-for="p in bookingStore.passengers" :key="'mob-'+p.key" class="p-4 bg-slate-50/50 rounded-xl border border-slate-100 flex flex-col gap-4">
                <div class="flex justify-between items-start">
                  <div>
                    <div class="font-black text-slate-800">{{ formatTitle(p.title) }} {{ p.firstName }} {{ p.lastName }}</div>
                    <div class="text-[9px] font-bold text-slate-400 uppercase tracking-widest mt-0.5">{{ p.type }}</div>
                  </div>
                  <div class="bg-white px-2 py-1 rounded border border-slate-200 text-[10px] font-black text-slate-900">
                    SEAT: {{ getSeatLabel(p.key, segment.key).split(' ')[0] }}
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                  <div class="bg-white p-3 rounded-lg border border-slate-100 shadow-sm">
                    <label class="text-[8px] font-black text-slate-400 uppercase tracking-widest block mb-1">Baggage</label>
                    <div v-for="item in getBaggageBreakdown(p.key, segment.key)" :key="'mob-bag-'+item.type" class="flex items-center gap-1.5 mt-1">
                      <span class="text-[9px] font-black text-slate-700 leading-tight">{{ item.label }}</span>
                    </div>
                  </div>
                  <div class="bg-white p-3 rounded-lg border border-slate-100 shadow-sm">
                    <label class="text-[8px] font-black text-slate-400 uppercase tracking-widest block mb-1">Meal & Special</label>
                    <p class="text-[9px] font-black text-slate-700 mt-1 truncate">{{ getMealLabel(p.key, segment.key) }}</p>
                    <p class="text-[8px] font-bold text-slate-400 mt-0.5 truncate">{{ getAssistanceLabel(p.key, segment.key) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Travel Protection Details -->
        <section v-if="selectedInsurancePlan" class="review-section">
          <div class="section-header">
            <span class="icon">🛡️</span>
            <h3>Travel Protection</h3>
          </div>
          <div class="review-card">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-4">
                <div class="w-12 h-12 bg-emerald-50 rounded-lg flex items-center justify-center border border-emerald-100">
                  <span class="text-2xl text-emerald-600">🛡️</span>
                </div>
                <div>
                  <h4 class="text-md font-bold text-gray-900">{{ selectedInsurancePlan.name }}</h4>
                  <p class="text-xs text-gray-500">Provided by {{ selectedInsurancePlan.provider_name || 'Our Partner' }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Coverage Status</p>
                <span class="px-3 py-1 bg-emerald-50 text-emerald-700 text-xs font-bold rounded-md border border-emerald-100 uppercase">Active</span>
              </div>
            </div>
            <div class="mt-4 pt-4 border-t border-gray-100 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="text-xs text-gray-600 leading-relaxed font-semibold">
                {{ selectedInsurancePlan.description }}
              </div>
              <div class="bg-blue-50 rounded-lg p-3 border border-blue-100 h-fit">
                <p class="text-[10px] font-bold text-blue-800 uppercase tracking-widest mb-1">Standard Policy Coverage Includes:</p>
                <ul class="text-[11px] text-blue-700 space-y-1 font-medium">
                  <li>✓ Emergency Medical Expenses abroad</li>
                  <li>✓ Trip Cancellation & Delays protection</li>
                  <li>✓ Lost, damaged or delayed baggage</li>
                  <li>✓ 24/7 Emergency Assistance Hotline</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <section class="review-section">
          <div class="section-header">
            <span class="icon">📜</span>
            <h3>Fare Rules & Conditions</h3>
          </div>
          <div class="bg-gray-50 border border-gray-100 rounded-lg p-5">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div v-for="(segment, idx) in flightSegments" :key="'rules-'+idx" class="space-y-4">
                <div class="flex items-center gap-2 mb-2">
                  <span class="text-[8px] font-black px-1.5 py-0.5 bg-pink-500 text-white rounded uppercase tracking-widest">{{ segment.label }}</span>
                  <span class="text-[9px] font-bold text-gray-400 uppercase tracking-widest">{{ segment.class_type }}</span>
                </div>
                
                <div class="flex items-start gap-3">
                  <div class="w-1.5 h-1.5 rounded-full bg-red-400 mt-1.5 flex-shrink-0"></div>
                  <div>
                    <p class="text-[10px] font-black text-gray-900 uppercase tracking-tighter">Cancellation / Refund</p>
                    <p class="text-[11px] text-gray-500 mt-0.5 leading-relaxed font-medium">
                      {{ getRefundRule(segment.key) }}
                    </p>
                  </div>
                </div>
                <div class="flex items-start gap-3">
                  <div class="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 flex-shrink-0"></div>
                  <div>
                    <p class="text-[10px] font-black text-gray-900 uppercase tracking-tighter">Change Policy / Rebooking</p>
                    <p class="text-[11px] text-gray-500 mt-0.5 leading-relaxed font-medium">
                      {{ getChangeRule(segment.key) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="mt-4 pt-4 border-t border-gray-100">
               <p class="text-[9px] text-gray-400 font-bold uppercase italic leading-tight">
                 * Fare rules may vary per airline. Free rebooking usually requires payment of the fare difference. 
                 Refunds may be processed as a travel fund or to the original payment method depending on the fare family.
               </p>
            </div>
          </div>
        </section>

        <section class="review-section">
          <div class="section-header">
            <span class="icon">📧</span>
            <h3>Contact Information</h3>
          </div>
          <div class="review-card contact-grid">
            <div class="contact-item flex items-center gap-4">
              <div class="w-10 h-10 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
              </div>
              <div>
                <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-0.5">Primary Contact Name</label>
                <p class="text-sm font-bold text-slate-800">{{ formatTitle(bookingStore.contactInfo.title) }} {{ bookingStore.contactInfo.firstName }} {{ bookingStore.contactInfo.lastName }}</p>
              </div>
            </div>
            <div class="contact-item flex items-center gap-4">
              <div class="w-10 h-10 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
              </div>
              <div>
                <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-0.5">Email Address</label>
                <p class="text-sm font-bold text-slate-800">{{ bookingStore.contactInfo.email }}</p>
              </div>
            </div>
            <div class="contact-item flex items-center gap-4">
              <div class="w-10 h-10 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
              </div>
              <div>
                <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-0.5">Phone Number</label>
                <p class="text-sm font-bold text-slate-800">{{ bookingStore.contactInfo.phone }}</p>
              </div>
            </div>
          </div>
        </section>

        <div class="footer-nav mt-10 pb-10">
          <button class="btn-back flex items-center" @click="$router.back()">
            <span class="text-lg mr-2">←</span>
            EDIT BOOKING DETAILS
          </button>
        </div>
      </main>

      <aside class="sidebar">
        <BookingTimer variant="sidebar" />
        <div class="summary-card sticky">
          <div class="summary-header">
            <div class="header-overlay"></div>
            <div class="header-content pt-8 pb-6 px-4 relative z-10">
              <div class="flex items-center justify-center gap-2 mb-1">
                <span class="text-2xl">💳</span>
                <span class="text-[10px] font-black text-white/60 uppercase tracking-[0.3em]">Secure Checkout</span>
              </div>
              <h3 class="text-xl font-black text-white text-center uppercase tracking-tighter">Payment Summary</h3>
            </div>
          </div>
          
          <div class="summary-body p-6">
            <!-- Flight Base Fares Breakdown -->
            <div class="summary-group mb-6" v-if="hasFlightData">
              <div class="group-header flex items-center gap-2 mb-3">
                <span class="w-1.5 h-1.5 rounded-full bg-pink-500"></span>
                <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Base Fares</span>
              </div>
              
              <div class="space-y-2">
                <div class="price-line flex justify-between items-center text-sm" v-if="bookingStore.passengerCount.adults > 0">
                  <span class="text-gray-500 font-medium">{{ bookingStore.passengerCount.adults }} Adult(s)</span> 
                  <span class="font-bold text-gray-900"><AnimatedNumber :value="adultTotalLine" prefix="₱" /></span>
                </div>
                
                <div class="price-line flex justify-between items-center text-sm" v-if="bookingStore.passengerCount.children > 0">
                  <span class="text-gray-500 font-medium">{{ bookingStore.passengerCount.children }} Child(ren)</span> 
                  <span class="font-bold text-gray-900"><AnimatedNumber :value="childTotalLine" prefix="₱" /></span>
                </div>
                
                <div class="price-line flex justify-between items-center text-sm" v-if="bookingStore.passengerCount.infants > 0">
                  <span class="text-gray-500 font-medium">{{ bookingStore.passengerCount.infants }} Infant(s)</span> 
                  <span class="font-bold text-gray-900"><AnimatedNumber :value="infantTotalLine" prefix="₱" /></span>
                </div>
              </div>
            </div>

            <!-- Taxes & Fees Breakdown -->
            <div class="summary-group mb-6">
              <div class="group-header flex items-center gap-2 mb-3">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Taxes & Fees</span>
              </div>
              
              <div class="space-y-2">
                <div v-if="backendTaxDetails && Object.keys(backendTaxDetails).length > 0">
                  <div v-for="(amount, label) in backendTaxDetails" :key="label" class="price-line flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">{{ label }}</span>
                    <span class="font-bold text-gray-900"><AnimatedNumber :value="amount" prefix="₱" /></span>
                  </div>
                </div>
                <div v-else class="price-line flex justify-between items-center text-sm">
                  <span class="text-gray-500 font-medium">Taxes, VAT & Fees</span>
                  <span class="font-bold text-gray-900"><AnimatedNumber :value="taxesPrice" prefix="₱" /></span>
                </div>
              </div>
            </div>

            <!-- Add-ons -->
            <div class="summary-group mb-6 border-t border-gray-50 pt-4" v-if="totalSeatsPrice > 0 || totalBaggagePrice > 0 || totalMealsPrice > 0 || totalAssistancePrice > 0 || insurancePrice > 0">
              <div class="group-header flex items-center gap-2 mb-3">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Optional Services</span>
              </div>
              
              <div class="space-y-2">
                <div class="price-line flex justify-between items-center text-sm" v-if="totalSeatsPrice > 0">
                  <span class="text-gray-500 font-medium">Seat Selection</span>
                  <span class="font-bold text-gray-900"><AnimatedNumber :value="totalSeatsPrice" prefix="₱" /></span>
                </div>
                <div class="price-line flex justify-between items-center text-sm" v-if="totalBaggagePrice > 0">
                  <span class="text-gray-500 font-medium">Extra Baggage</span>
                  <span class="font-bold text-gray-900"><AnimatedNumber :value="totalBaggagePrice" prefix="₱" /></span>
                </div>
                <div class="price-line flex justify-between items-center text-sm" v-if="totalMealsPrice > 0">
                  <span class="text-gray-500 font-medium">Meal Selection</span>
                  <span class="font-bold text-gray-900"><AnimatedNumber :value="totalMealsPrice" prefix="₱" /></span>
                </div>
                <div class="price-line flex justify-between items-center text-sm" v-if="totalAssistancePrice > 0">
                  <span class="text-gray-500 font-medium">Special Assistance</span>
                  <span class="font-bold text-gray-900"><AnimatedNumber :value="totalAssistancePrice" prefix="₱" /></span>
                </div>
                <div class="price-line flex justify-between items-center text-sm" v-if="insurancePrice > 0">
                  <span class="text-gray-500 font-medium">Travel Insurance</span>
                  <span class="font-bold text-gray-900"><AnimatedNumber :value="insurancePrice" prefix="₱" /></span>
                </div>
              </div>
            </div>

            <div class="total-section bg-gray-50/50 -mx-6 px-6 py-6 border-t border-gray-100">
              <div class="flex justify-between items-end mb-1">
                <div>
                  <span class="text-[11px] font-black text-gray-400 uppercase tracking-widest block mb-0.5">Total Amount</span>
                  <div class="pax-badge bg-white border border-gray-200 rounded px-2 py-0.5 inline-flex items-center gap-1">
                    <span class="text-[9px] font-black text-gray-900 uppercase">{{ payingPassengerCount }} Passengers</span>
                  </div>
                </div>
                <div class="text-right">
                  <div class="flex items-center justify-end">
                    <span class="text-pink-500 font-black  mr-1">₱</span>
                    <span class="text-2xl font-black text-gray-900 tracking-tighter leading-none">
                      <span v-if="isCalculatingPrice" class="text-sm text-gray-400 animate-pulse">Wait...</span>
                      <AnimatedNumber v-else :value="grandTotal" />
                    </span>
                  </div>
                </div>
              </div>
              
              <div v-if="isUsingFrontendEstimate && !isCalculatingPrice" class="mt-4 p-2 bg-amber-50 rounded border border-amber-100 flex items-center gap-2">
                <span class="text-amber-500">⚠️</span>
                <p class="text-[9px] font-bold text-amber-700 uppercase leading-tight">Estimated total — finalized at payment step</p>
              </div>
            </div>

            <button class="btn-pay-premium mt-6" @click="confirmBooking" :disabled="isProcessing">
              <div class="flex items-center justify-center gap-3">
                <span v-if="!isProcessing" class="text-lg">➔</span>
                <div v-else class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                <span class="tracking-widest uppercase">{{ isProcessing ? 'Processing' : 'Proceed to Payment' }}</span>
              </div>
            </button>
            
            <div class="secure-checkout mt-6 flex items-center justify-center gap-2 text-[9px] text-gray-400 font-black uppercase tracking-[0.2em]">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              Encrypted Checkout
            </div>
          </div>
        </div>
      </aside>
    </div>

    <LoadingOverlay 
      :show="isProcessing" 
      title="Finalizing Your Booking"
      subtitle="Just a few seconds while we create your official reservation."
    />

    <MobileBookingFooter 
      buttonText="Confirm & Pay"
      :disabled="isProcessing"
      :loading="isProcessing"
      @next="confirmBooking"
    />
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useRouter } from 'vue-router';
import api from '@/services/api/axios';
import { addonService } from '@/services/booking/addonService';
import { bookingService } from '@/services/booking/bookingService';
import { useNotificationStore } from '@/stores/notification';
import BookingTimer from '@/components/booking/BookingTimer.vue';
import BookingStatusHeader from '@/components/booking/BookingStatusHeader.vue';
import MobileBookingFooter from '@/components/booking/MobileBookingFooter.vue';
import AnimatedNumber from '@/components/common/AnimatedNumber.vue';
import LoadingOverlay from '@/components/common/LoadingOverlay.vue';

const bookingStore = useBookingStore();
const router = useRouter();
const notificationStore = useNotificationStore();

const isLoading = ref(true);
const isProcessing = ref(false);
const baggageOptions = ref([]);
const mealOptions = ref([]);
const assistanceOptions = ref([]);
const insurancePlans = ref([]);
const generatedPNR = ref(Math.random().toString(36).substring(2, 8).toUpperCase());

// Backend Price Data (kept for potential future use but no longer used for display)
const backendTotal = ref(null);
const backendBreakdown = ref(null);
const backendTaxDetails = ref(null);
const isCalculatingPrice = ref(false);

const baggagePolicies = {
  '5J': {
    airline: 'Cebu Pacific',
    pieces: '1-Piece', // Domestic GO Tiers (20kg)
    keyRule: 'Max weight per piece: 32kg'
  },
  'PR': {
    airline: 'Philippine Airlines',
    pieces: '1-Piece', // Domestic standard
    keyRule: 'Free baggage allowance applies'
  },
  'Z2': {
    airline: 'AirAsia Philippines',
    pieces: 'Weight Concept',
    keyRule: 'No piece limit'
  },
  'T6': {
    airline: 'AirSwift',
    pieces: 'Max 2 pieces',
    keyRule: 'Small cargo hold'
  }
};

onMounted(async () => {
  try {

    bookingStore.loadBookingFromStorage();
    bookingStore.migrateAddonsToNewFormat();
    
    const airlineId = bookingStore.selectedOutbound?.airline_code || bookingStore.selectedOutbound?.airline;
    if (!airlineId) {
      isLoading.value = false;
      return;
    }

    const results = await Promise.allSettled([
      addonService.getBaggageOptions(airlineId),
      addonService.getMealOptions(airlineId),
      addonService.getAssistanceServices(airlineId),
      api.get('/flightapp/api/insurance-plans/').catch(() => null)
    ]);

    if (results[0].status === 'fulfilled') {
      const data = results[0].value.data;
      baggageOptions.value = Array.isArray(data) ? data : (data?.results || []);
    }
    if (results[1].status === 'fulfilled') {
      const data = results[1].value.data;
      mealOptions.value = Array.isArray(data) ? data : (data?.results || []);
    }
    if (results[2].status === 'fulfilled') {
      const data = results[2].value.data;
      assistanceOptions.value = Array.isArray(data) ? data : (data?.results || []);
    }
    if (results[3].status === 'fulfilled' && results[3].value?.data) {
      const data = results[3].value.data;
      insurancePlans.value = Array.isArray(data) ? data : (data?.results || []);
    }

    // Fetch backend price to show authoritative breakdown
    await fetchBackendPrice();

  } catch (error) {
    console.error("Review page data fetch error:", error);
  } finally {
    isLoading.value = false;
  }
});

// Called on mount to confirm the backend total before the user proceeds to payment.
const fetchBackendPrice = async () => {
  if (!hasFlightData.value) return;
  
  isCalculatingPrice.value = true;
  try {
    const response = await bookingService.calculatePrice(bookingStore);
    if (response.success) {
      bookingStore.setBackendBreakdown(response);
      backendTotal.value = response.total_amount;
      backendBreakdown.value = response.breakdown;
      console.log('✅ Backend price confirmed:', response.total_amount);
      console.log('📑 Tax Details from store:', bookingStore.backendTaxDetails);
      
      // Warn if there's a significant mismatch with frontend estimate
      const diff = Math.abs(response.total_amount - bookingStore.grandTotal);
      if (diff > 50) {
        console.warn(`⚠️ Price mismatch: Frontend=${bookingStore.grandTotal}, Backend=${response.total_amount}, Diff=${diff}`);
      }
    }
  } catch (error) {
    console.error('Error fetching backend price:', error);
  } finally {
    isCalculatingPrice.value = false;
  }
};

const adultTotalLine = computed(() => bookingStore.authoritativeAdultBase);
const childTotalLine = computed(() => bookingStore.authoritativeChildBase);
const infantTotalLine = computed(() => bookingStore.authoritativeInfantBase);

const selectedInsurancePlan = computed(() => {
  const planId = bookingStore.addons?.insurance?.selectedPlanId;
  if (!planId || !insurancePlans.value.length) return null;
  return insurancePlans.value.find(p => p.id == planId);
});

// Helper functions
const getItemById = (list, id) => {
  if (!id || !list) return null;
  return list.find(item => item.id === id);
};

const getOptionById = (list, id) => {
  if (!id || !list) return null;
  return list.find(item => item.id == id);
};

const getBaggageBreakdown = (passengerKey, segment = 'depart') => {
  const p = bookingStore.passengers.find(p => p.key === passengerKey);
  if (p?.type === 'Infant') {
    return [
      { type: 'hand-carry', label: 'Incl. in Adult Allowance', status: 'Included', icon: '🎒' }
    ];
  }

  const ff = (bookingStore.fareFamilies[segment] || 'basic').toLowerCase();
  const ffName = (bookingStore.fareFamilyNames[segment] || '').toLowerCase();
  
  // Revised inclusion logic: exclude all 'basic' or 'saver' types for PAL/5J/Z2
  const isIncluded = ff !== 'basic' && 
                     !ffName.includes('saver') && 
                     !ffName.includes('supersaver') && 
                     !ffName.includes('promo') && 
                     !ffName.includes('low fare') && 
                     !ffName.includes('go basic');
                     
  const baggage = bookingStore.addons?.baggage?.[segment]?.[passengerKey];
  
  // Dynamic carry-on based on airline and class
  const segmentObj = flightSegments.value.find(s => s.key === segment);
  const flightNumber = segmentObj?.flight_number || '';
  const airlineCode = flightNumber.substring(0, 2).toUpperCase();
  
  let carryOnLabel = '1 x 7kg Carry-on';
  if (airlineCode === 'PR' && ffName.includes('business')) {
    carryOnLabel = '2 x 7kg Carry-on';
  }

  const breakdown = [
    { type: 'hand-carry', label: carryOnLabel, status: 'Included', icon: '🎒' }
  ];

  // ================= DYNAMIC BAGGAGE INCLUSION FROM FEATURES =================
  const flight = segment === 'depart' ? bookingStore.selectedOutbound : 
                 segment === 'return' ? bookingStore.selectedReturn : 
                 bookingStore.multiCitySegments[parseInt(segment.replace('multi_', ''))]?.selectedFlight;
  
  const features = Array.isArray(flight?.seat_class_features) ? flight.seat_class_features : [];
  const checkedBaggageFeature = features.find(f => typeof f === 'string' && (f.toLowerCase().includes('checked baggage') || f.toLowerCase().includes('check-in baggage')));
  const handCarryFeature = features.find(f => typeof f === 'string' && (f.toLowerCase().includes('hand-carry') || f.toLowerCase().includes('carry-on')));

  if (checkedBaggageFeature && typeof checkedBaggageFeature === 'string' && !checkedBaggageFeature.toLowerCase().includes('no ')) {
    // If we have a dynamic feature like "20kg Checked baggage included", use it!
    let weightLabel = checkedBaggageFeature.replace(' included', '').replace(' included*', '');
    
    // Add piece concept if PAL
    const policy = baggagePolicies[airlineCode];
    if (policy && policy.pieces && !weightLabel.includes('piece')) {
       weightLabel = `${weightLabel} (${policy.pieces})`;
    }

    if (baggage) {
      const option = baggageOptions.value.find(o => o.id == (baggage.id || baggage));
      weightLabel = option ? option.formatted_weight : (typeof baggage === 'object' ? baggage.formatted_weight : weightLabel);
    }
    
    breakdown.push({ type: 'checked', label: weightLabel, status: 'Included', icon: '🧳' });
  } else if (baggage) {
    const option = baggageOptions.value.find(o => o.id == (baggage.id || baggage));
    const labelText = option ? option.formatted_weight : (typeof baggage === 'object' ? baggage.formatted_weight : 'Extra Baggage');
    
    let finalLabel = labelText;
    const policy = baggagePolicies[airlineCode];
    if (policy && policy.pieces) {
      finalLabel = `${labelText} (${policy.pieces})`;
    }
    
    breakdown.push({ type: 'checked', label: finalLabel, status: 'Purchased', icon: '🧳' });
  } else {
    // Check if the feature specifically said "No checked baggage" or "Hand-carry only"
    const isExplicitlyNoBaggage = (typeof checkedBaggageFeature === 'string' && checkedBaggageFeature.toLowerCase().includes('no ')) || 
                                 features.some(f => typeof f === 'string' && f.toLowerCase().includes('hand-carry only'));
    
    breakdown.push({ 
      type: 'checked', 
      label: isExplicitlyNoBaggage ? 'No Checked Baggage' : 'Standard Allowance', 
      status: isExplicitlyNoBaggage ? 'None' : 'Included', 
      icon: '🧳' 
    });
  }

  return breakdown;
};

const getMealLabel = (passengerKey, segment = 'depart') => {
  const p = bookingStore.passengers.find(p => p.key === passengerKey);
  if (p?.type === 'Infant') return 'Not Available';

  const meals = bookingStore.addons?.meals?.[segment]?.[passengerKey];
  const ffName = (bookingStore.fareFamilyNames[segment] || '').toLowerCase();
  
  const getLabels = () => {
    if (!meals || (Array.isArray(meals) && meals.length === 0)) return [];
    const mealArray = Array.isArray(meals) ? meals : [meals];
    return mealArray.map(m => {
      if (typeof m === 'object' && m.name) return m.name;
      const option = mealOptions.value.find(opt => opt.id == (m.id || m));
      return option ? option.name : 'Pre-ordered Meal';
    });
  };

  const labels = getLabels();

  if (labels.length === 0) {
    const segmentObj = flightSegments.value.find(s => s.key === segment);
    const flightNumber = segmentObj?.flight_number || '';
    const airlineCode = flightNumber.substring(0, 2).toUpperCase();
    if (airlineCode === 'PR') return 'Meals & Snacks included';
    if (airlineCode === 'Z2' && (ffName.includes('value') || ffName.includes('premium'))) return '1 Complimentary Meal included';
    return 'No meal';
  }

  return labels.join(', ');
};

const getRefundRule = (segmentKey) => {
  const flight = segmentKey === 'depart' ? bookingStore.selectedOutbound : 
                 segmentKey === 'return' ? bookingStore.selectedReturn : 
                 bookingStore.multiCitySegments[parseInt(segmentKey.replace('multi_', ''))]?.selectedFlight;
  
  if (!flight) return 'Subject to airline terms.';
  
  const features = Array.isArray(flight.seat_class_features) ? flight.seat_class_features : [];
  const refundFeature = features.find(f => typeof f === 'string' && f.toLowerCase().includes('refund'));
  
  if (refundFeature) return refundFeature;
  
  // Airline Fallbacks
  const airline = flight.airline_code || (flight.flight_number?.substring(0, 2).toUpperCase());
  if (airline === '5J' || airline === 'Z2') return 'Non-refundable (Convertible to Travel Fund only).';
  return 'Cancellation fees apply. Non-refundable for promo fares.';
};

const getChangeRule = (segmentKey) => {
  const flight = segmentKey === 'depart' ? bookingStore.selectedOutbound : 
                 segmentKey === 'return' ? bookingStore.selectedReturn : 
                 bookingStore.multiCitySegments[parseInt(segmentKey.replace('multi_', ''))]?.selectedFlight;
  
  if (!flight) return 'Subject to airline terms.';
  
  const features = Array.isArray(flight.seat_class_features) ? flight.seat_class_features : [];
  const changeFeature = features.find(f => typeof f === 'string' && (f.toLowerCase().includes('rebook') || f.toLowerCase().includes('change')));
  
  if (changeFeature) return changeFeature;
  
  return 'Changes allowed with fee plus fare difference.';
};

const getAssistanceLabel = (passengerKey, segment = 'depart') => {
  const p = bookingStore.passengers.find(p => p.key === passengerKey);
  if (p?.type === 'Infant') return 'Not Available';

  const ffName = (bookingStore.fareFamilyNames[segment] || '').toLowerCase();
  
  const assistanceId = bookingStore.addons?.wheelchair?.[segment]?.[passengerKey];
  
  const getSelectedLabel = () => {
    if (!assistanceId || !Array.isArray(assistanceOptions.value)) return null;
    const option = assistanceOptions.value.find(a => a.id == assistanceId);
    return option ? option.name : 'Special Assistance';
  };

  const selectedLabel = getSelectedLabel();

  // Highlight PAL Lounge access for Comfort and Business classes
  const segmentObj = flightSegments.value.find(s => s.key === segment);
  const flightNumber = segmentObj?.flight_number || '';
  const airlineCode = flightNumber.substring(0, 2).toUpperCase();
  
  if (airlineCode === 'PR' && (ffName.includes('comfort') || ffName.includes('business'))) {
    const loungeMsg = 'Mabuhay Lounge access included';
    return selectedLabel ? `${selectedLabel}, ${loungeMsg}` : loungeMsg;
  }

  return selectedLabel || 'No assistance';
};

const getSeatLabel = (passengerKey, segmentKey = 'depart') => {
  const p = bookingStore.passengers.find(p => p.key === passengerKey);
  if (p?.type === 'Infant') {
    const adultKey = bookingStore.infantAdultMapping[passengerKey];
    if (adultKey && bookingStore.addons?.seats?.[segmentKey]?.[adultKey]) {
      const adultSeat = bookingStore.addons.seats[segmentKey][adultKey];
      return `Lap (${adultSeat.seat_code})`;
    }
    return 'On Lap';
  }

  const ffName = (bookingStore.fareFamilyNames[segmentKey] || '').toLowerCase();
  
  // Get correct airline to apply proper branding
  const segmentObj = flightSegments.value.find(s => s.key === segmentKey);
  const flightNumber = segmentObj?.flight_number || '';
  const airlineCode = flightNumber.substring(0, 2).toUpperCase();
  
  // Synchronized inclusion logic with baggage
  const isIncluded = !ffName.includes('saver') && 
                     !ffName.includes('supersaver') && 
                     !ffName.includes('promo') && 
                     !ffName.includes('low fare') && 
                     !ffName.includes('go basic');
                     
  const seat = bookingStore.addons?.seats?.[segmentKey]?.[passengerKey];
  
  if (!seat) {
    if (airlineCode === 'PR') {
      if (ffName.includes('saver')) return 'Standard seat (assigned at check-in)';
      if (ffName.includes('value')) return 'Free Standard Seat selection';
      if (ffName.includes('flex')) return 'Free Premium Seat selection';
      if (ffName.includes('comfort')) return 'Free Extra Legroom seat selection';
    } else if (airlineCode === 'Z2') {
      if (ffName.includes('value')) return 'Free Standard Seat selection';
      if (ffName.includes('premium')) return 'Free Premium Seat selection';
    }
    return 'Not selected';
  }
  
  const seatCode = seat.seat_code || 'N/A';
  const price = isIncluded ? 0 : (parseFloat(seat.seat_price) || 0);
  
  if (isIncluded || price === 0) {
    return `${seatCode} (Included)`;
  }
  
  return `${seatCode} (₱${price.toLocaleString()})`;
};

// Computed Properties
const flightSegments = computed(() => {
  const tripType = bookingStore.tripType;
  
  const getAirportLabel = (airport) => {
    if (!airport) return 'N/A';
    if (typeof airport === 'string') return airport;
    // Check if it's an object with city or name
    return airport.city || airport.name || airport.code || 'N/A';
  };
  
  const getAirlineBranding = (flightNumber) => {
    if (!flightNumber) return { name: 'Unknown Airline', code: '??', class: 'bg-gray-400' };
    const prefix = flightNumber.substring(0, 2).toUpperCase();
    const map = {
      'PR': { name: 'Philippine Airlines', code: 'PR', class: 'bg-[#003870]' },
      '5J': { name: 'Cebu Pacific Air', code: '5J', class: 'bg-[#FFCC00] !text-black' },
      'DG': { name: 'Cebgo', code: 'DG', class: 'bg-[#FFCC00] !text-black' },
      'Z2': { name: 'AirAsia Philippines', code: 'Z2', class: 'bg-[#E31C23]' },
      'T6': { name: 'AirSwift', code: 'T6', class: 'bg-[#00529B]' },
      'RW': { name: 'Royal Air Philippines', code: 'RW', class: 'bg-[#D4A017]' }
    };
    return map[prefix] || { name: 'Commercial Flight', code: prefix, class: 'bg-gray-900' };
  };
  
  const createSegmentData = (flightStoreObj, label, key, isReturn = false) => {
    if (!flightStoreObj) return null;
    const branding = getAirlineBranding(flightStoreObj.flight_number);
    return {
      key: key,
      label: label,
      origin: getAirportLabel(flightStoreObj.origin),
      destination: getAirportLabel(flightStoreObj.destination),
      flight_number: flightStoreObj.flight_number,
      airline_name: flightStoreObj.airline_name || branding.name,
      airline_code: branding.code,
      airline_class: branding.class,
      aircraft: flightStoreObj.aircraft || 'Airbus A320', // Fallback as a placeholder
      departure_time: flightStoreObj.departure_time,
      class_type: flightStoreObj.class_type,
      price: flightStoreObj.price || 0,
      isReturn: isReturn
    };
  };

  if (tripType === 'multi_city' || tripType === 'multi-city') {
    return bookingStore.multiCitySegments.map((seg, idx) => {
      const branding = getAirlineBranding(seg.selectedFlight?.flight_number);
      return {
        key: idx.toString(),
        label: `Flight ${idx + 1}`,
        origin: getAirportLabel(seg.origin),
        destination: getAirportLabel(seg.destination),
        flight_number: seg.selectedFlight?.flight_number || 'N/A',
        airline_name: seg.selectedFlight?.airline_name || branding.name,
        airline_code: branding.code,
        airline_class: branding.class,
        aircraft: seg.selectedFlight?.aircraft || 'Commercial Jet',
        departure_time: seg.selectedFlight?.departure_time,
        class_type: seg.selectedFlight?.class_type,
        price: seg.selectedFlight?.price || 0,
        isMulti: true
      };
    });
  }

  const segments = [];
  if (bookingStore.selectedOutbound) {
    segments.push(createSegmentData(bookingStore.selectedOutbound, 'Depart', 'depart'));
  }
  
  if (bookingStore.isRoundTrip && bookingStore.selectedReturn) {
    segments.push(createSegmentData(bookingStore.selectedReturn, 'Return', 'return', true));
  }
  
  return segments;
});

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  try {
    return new Date(dateStr).toLocaleString('en-US', {
      dateStyle: 'medium',
      timeStyle: 'short'
    });
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Invalid date';
  }
};

const formatTitle = (titleCode) => {
  if (!titleCode) return '';
  const map = {
    'MR': 'Mr.',
    'MRS': 'Mrs.',
    'MS': 'Ms.',
    'CHD': 'Mstr/Miss',
    'INF': 'Infant'
  };
  return map[titleCode.toUpperCase()] || titleCode;
};

const formatFareFamily = (ff) => {
  if (!ff) return 'Standard';
  // Capitalize first letter of each word
  return ff.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' ');
};

// Computed Properties
const hasFlightData = computed(() => {
  if (bookingStore.tripType === 'multi_city' || bookingStore.tripType === 'multi-city') {
    return bookingStore.multiCitySegments && 
           bookingStore.multiCitySegments.length > 0 && 
           bookingStore.multiCitySegments.every(seg => seg.selectedFlight);
  }
  const outbound = bookingStore.selectedOutbound;
  return !!outbound && typeof outbound === 'object' && 'price' in outbound;
});

const payingPassengerCount = computed(() => bookingStore.payingPassengerCount);
const departBaseFare = computed(() => bookingStore.departBaseFare);
const returnBaseFare = computed(() => bookingStore.returnBaseFare);
const totalSeatsPrice = computed(() => bookingStore.authoritativeSeats);
const totalBaggagePrice = computed(() => bookingStore.authoritativeBaggage);
const totalMealsPrice = computed(() => bookingStore.authoritativeMeals);
const totalAssistancePrice = computed(() => bookingStore.authoritativeAssistance);
const insurancePrice = computed(() => bookingStore.authoritativeInsurance);
const combinedBasePriceTotal = computed(() => bookingStore.authoritativeBaseFare);

const taxesPrice = computed(() => bookingStore.authoritativeTaxes);

const grandTotal = computed(() => bookingStore.authoritativeTotal);

const isUsingFrontendEstimate = computed(() => backendTotal.value === null || isNaN(backendTotal.value));

// Validation function
const validateBooking = () => {
  const errors = [];
  const tripType = bookingStore.tripType;
  
  if (tripType === 'multi_city' || tripType === 'multi-city') {
    bookingStore.multiCitySegments.forEach((seg, idx) => {
      if (!seg.selectedFlight) {
        errors.push(`Please select a flight for Segment ${idx + 1}`);
      }
    });
  } else {
    if (!bookingStore.selectedOutbound) {
      errors.push('Please select an outbound flight');
    }
    
    if (bookingStore.isRoundTrip && !bookingStore.selectedReturn) {
      errors.push('Please select a return flight for round trip');
    }
  }
  
  if (!bookingStore.passengers || bookingStore.passengers.length === 0) {
    errors.push('Please add passenger information');
  }
  
  // Validate each passenger
  bookingStore.passengers.forEach((p, index) => {
    const passengerNum = index + 1;
    
    if (!p.firstName || p.firstName.trim() === '') {
      errors.push(`Passenger ${passengerNum}: First name is required`);
    }
    
    if (!p.lastName || p.lastName.trim() === '') {
      errors.push(`Passenger ${passengerNum}: Last name is required`);
    }
    
    if (!p.title) {
      errors.push(`Passenger ${passengerNum}: Title (Mr/Ms/Mrs) is required`);
    }
    
    if (!p.dateOfBirth) {
      errors.push(`Passenger ${passengerNum}: Date of birth is required`);
    } else {
      const date = new Date(p.dateOfBirth);
      if (isNaN(date.getTime())) {
        errors.push(`Passenger ${passengerNum}: Invalid date of birth format`);
      }
    }
    
    if (!p.key) {
      errors.push(`Passenger ${passengerNum}: Missing passenger key`);
    }
  });
  
  // Validate contact info
  if (!bookingStore.contactInfo?.firstName || bookingStore.contactInfo?.firstName.trim() === '') {
    errors.push('Contact person first name is required');
  }
  
  if (!bookingStore.contactInfo?.lastName || bookingStore.contactInfo?.lastName.trim() === '') {
    errors.push('Contact person last name is required');
  }
  
  if (!bookingStore.contactInfo?.email || !/\S+@\S+\.\S+/.test(bookingStore.contactInfo.email)) {
    errors.push('Please enter a valid email address');
  }
  
  if (!bookingStore.contactInfo?.phone || bookingStore.contactInfo.phone.length < 7) {
    errors.push('Please enter a valid phone number');
  }
  
  return errors;
};

// Helper to get default date of birth
const getDefaultDOB = () => {
  const date = new Date();
  date.setFullYear(date.getFullYear() - 20);
  return date.toISOString().split('T')[0];
};

// Prepare passengers for submission
const preparePassengersForSubmission = () => {
  console.log('🔍 Preparing passengers for submission...');
  
  const preparedPassengers = bookingStore.passengers.map((p, index) => {
    let dateOfBirth = p.dateOfBirth;
    if (dateOfBirth) {
      const parsedDate = new Date(dateOfBirth);
      if (isNaN(parsedDate.getTime())) {
        dateOfBirth = getDefaultDOB();
      } else {
        dateOfBirth = parsedDate.toISOString().split('T')[0];
      }
    } else {
      dateOfBirth = getDefaultDOB();
    }
    
    return {
      key: p.key || `pax_${index + 1}`,
      firstName: p.firstName || '',
      lastName: p.lastName || '',
      middleName: p.middleName || '',
      title: p.title || 'MR',
      dateOfBirth: dateOfBirth,
      nationality: p.nationality || 'Philippines',
      passportNumber: p.passportNumber || '',
      phDiscountType: p.phDiscountType || 'none',
      phDiscountId: p.phDiscountId || '',
      type: p.type || 'Adult'
    };
  });
  
  console.log('✅ Prepared passengers:', preparedPassengers);
  return preparedPassengers;
};


const confirmBooking = async () => {
  if (isProcessing.value) return;
  isProcessing.value = true;
  
  try {
    const bookingData = bookingService.formatBookingData(bookingStore);
    const existingBookingId = bookingStore.booking_id || 
                             JSON.parse(localStorage.getItem('current_booking'))?.id;

    let response;
    if (existingBookingId) {
      console.log('🔄 Updating existing booking:', existingBookingId);
      response = await bookingService.updateBooking(existingBookingId, bookingData);
    } else {
      console.log('🆕 Creating new booking...');
      response = await bookingService.createBooking(bookingData);
    }
    
    if (response && response.success) {
      bookingStore.saveBookingConfirmation({
        booking_id: response.booking_id,
        booking_reference: response.booking_reference || `CSUCC${String(response.booking_id).padStart(8, '0')}`,
        status: response.status || 'pending',
        total_amount: response.total_amount
      });
      
      bookingStore.setBookingId(response.booking_id);
      bookingStore.booking_reference = response.booking_reference;
      bookingStore.booking_status = response.status;
      
      localStorage.setItem('current_booking', JSON.stringify({
        id: response.booking_id,
        reference: response.booking_reference,
        total: response.total_amount,
        status: response.status
      }));
      
      const confirmedAmount = bookingStore.booking_total || bookingStore.authoritativeTotal;
      router.push({ 
        name: 'Payment', 
        query: { 
          bookingId: response.booking_id,
          bookingReference: response.booking_reference,
          amount: confirmedAmount
        } 
      });
    }
  } catch (error) {
    console.error("Booking critical failure:", error);
    handleBookingError(error);
  } finally {
    isProcessing.value = false;
  }
};

const handleBookingError = (error) => {
  let errorMessage = 'Failed to process booking. Please try again.';
  
  if (error?.response?.data?.errors) {
    errorMessage = 'Validation errors:\n' + 
      Object.entries(error.response.data.errors)
        .map(([field, errs]) => `• ${field}: ${Array.isArray(errs) ? errs.join(', ') : errs}`)
        .join('\n');
  } else if (typeof error === 'string') {
    errorMessage = error;
  }
  
  notificationStore.error(errorMessage);
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

.pal-bg { 
  background: var(--color-slate-50);
  min-height: 100vh; 
  padding: 60px 0;
  font-family: 'Outfit', sans-serif;
  color: var(--color-slate-800);
}

.review-layout { 
  display: grid; 
  grid-template-columns: 1fr 380px; 
  gap: 30px; 
  max-width: 1240px; 
  margin: 0 auto; 
  padding: 0 15px;
}

@media (min-width: 640px) {
  .review-layout {
    padding: 0 20px;
  }
}

.page-title { 
  color: #0f172a; 
  font-weight: 900; 
  margin-bottom: 30px; 
  font-size: 2.6rem;
  letter-spacing: -1.5px;
}

/* Minimalist Review Section */
.review-section { 
  margin-bottom: 40px; 
  animation: fadeIn 0.5s ease-out both;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.section-header { 
  display: flex; 
  align-items: center; 
  gap: 12px; 
  margin-bottom: 20px; 
}

.section-header .icon {
  font-size: 1.4rem;
  background: var(--color-slate-50);
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px; /* sm/md */
  border: 1px solid var(--color-slate-200);
}

.section-header h3 { 
  color: var(--color-slate-950); 
  margin: 0; 
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

/* Boarding Pass Styling - Minimalist */
.boarding-pass-card {
  background: white;
  border: 1px solid var(--color-slate-200);
  border-radius: 12px; /* md */
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  transition: border-color 0.2s ease;
  position: relative;
  overflow: hidden;
}

.boarding-pass-card:hover {
  border-color: var(--color-slate-300);
}

.pass-left { padding: 24px; }
.pass-right { 
  background: var(--color-slate-50); 
  border-left: 1px dashed var(--color-slate-200);
  padding: 24px;
  position: relative;
}

.airline-brand .airline-code-badge {
  background: var(--color-slate-950);
  color: white;
  font-weight: 800;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
}

.airport-code {
  font-size: 3.5rem;
  font-weight: 900;
  color: var(--color-slate-950);
  line-height: 1;
  letter-spacing: -2px;
}

.flight-path-divider {
  flex: 1;
  height: 2px;
  background: var(--color-slate-100);
  position: relative;
  margin: 0 20px;
}

.path-airplane {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 0 10px;
  color: var(--color-pink-600);
}

/* Info Cards */
.review-card { 
  background: white;
  border-radius: 12px; /* md */
  padding: 24px; 
  border: 1px solid var(--color-slate-200);
}

.contact-grid { 
  display: grid; 
  grid-template-columns: repeat(3, 1fr); 
  gap: 32px;
}

.contact-item label {
  display: block;
  font-size: 0.65rem;
  font-weight: 800;
  color: var(--color-slate-400);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.contact-item p {
  font-weight: 600;
  color: var(--color-slate-800);
  margin: 0;
  font-size: 0.95rem;
}

.detail-grid { 
  display: grid; 
  grid-template-columns: repeat(3, 1fr); 
  gap: 25px;
}

.detail-item label {
  display: block;
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--color-slate-400);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 6px;
}

.detail-item p {
  font-weight: 700;
  color: var(--color-slate-800);
  margin: 0;
  font-size: 1rem;
}

/* Sidebar & Summary Redesign - Minimalist */
.summary-card { 
  background: white; 
  border-radius: 12px; /* md */
  box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
  overflow: hidden;
  position: sticky;
  top: 40px;
  border: 1px solid var(--color-slate-200);
}

.summary-header { 
  background: var(--color-slate-50);
  padding: 24px; 
  border-bottom: 1px solid var(--color-slate-200);
  position: relative;
}

.header-overlay { display: none; }

.header-content h3 {
  color: var(--color-slate-950) !important;
}

.header-content span {
  color: var(--color-slate-500) !important;
}

.price-line {
  transition: opacity 0.2s ease;
}

.btn-pay-premium {
  width: 100%;
  padding: 20px;
  background: var(--color-pink-500);
  color: white;
  border: none;
  border-radius: 8px; /* sm/md */
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
  position: relative;
}

.btn-pay-premium::before { display: none; }

.btn-pay-premium:hover:not(:disabled) {
  background-color: var(--color-pink-600);
}

.btn-pay-premium:active:not(:disabled) {
  background-color: var(--color-pink-700);
}

.btn-pay-premium:disabled {
  background: var(--color-slate-100);
  color: var(--color-slate-400);
  cursor: not-allowed;
}

.calculating-shimmer {
  display: inline-block;
  width: 80px;
  height: 20px;
  background: var(--color-slate-100);
  border-radius: 4px;
}

/* Footer Nav & Back Button */
.footer-nav {
  display: flex;
  justify-content: flex-start;
}

.btn-back {
  background: transparent;
  border: 1px solid var(--color-slate-200);
  color: var(--color-slate-500);
  padding: 14px 28px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.85rem;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 0.2s ease;
  text-transform: uppercase;
}

.btn-back:hover {
  background: var(--color-slate-50);
  color: var(--color-slate-900);
  border-color: var(--color-slate-300);
}

/* Trip Badge */
.trip-type-badge {
  margin-left: auto;
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
}

.trip-type-badge.round-trip { background: #eff6ff; color: #1d4ed8; }
.trip-type-badge.one-way { background: #faf5ff; color: #7c3aed; }

/* Review Table */
.review-table { 
  width: 100%; 
  border-collapse: collapse; 
  margin-top: 15px;
}

.review-table th { 
  text-align: left; 
  padding: 15px 20px; 
  font-size: 0.7rem; 
  font-weight: 800;
  color: var(--color-slate-400);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.review-table td { 
  padding: 20px; 
  border-top: 1px solid var(--color-slate-100); 
  font-size: 0.95rem; 
  font-weight: 600;
}

/* Baggage List */
.baggage-item-mini {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  padding: 10px;
  background: var(--color-slate-50);
  border-radius: 8px;
}

.baggage-status {
  font-size: 0.6rem;
  font-weight: 900;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 6px;
}

.baggage-status.included { background: #dcfce7; color: #166534; }
.baggage-status.purchased { background: #dbeafe; color: #1e40af; }

/* Loading Spinner */
.loading-spinner {
  border: 4px solid var(--color-slate-100);
  border-top: 4px solid var(--color-pink-500);
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
}

@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Shared Segment Header for Tables */
.segment-summary-header {
  text-align: left;
  padding: 18px 25px;
  display: flex;
  align-items: center;
  font-size: 1rem;
  background: var(--color-slate-900);
  color: white;
  border-radius: 8px 8px 0 0;
  margin: -30px -30px 20px -30px;
}

.segment-summary-header.return { background: var(--color-pink-600); }
.segment-summary-header.multi { background: #4f46e5; }

.badge { 
  background: rgba(255,255,255,0.2);
  color: white; 
  padding: 4px 10px; 
  border-radius: 6px; 
  font-size: 0.7rem; 
  font-weight: 900;
  margin-right: 12px;
}

/* Responsive - Minimalist Adjustments */
@media (max-width: 1024px) {
  .review-layout { grid-template-columns: 1fr; gap: 20px; }
  .summary-card { position: static; margin-top: 24px; border-radius: 12px; }
  .main-content { order: 1; }
  .sidebar { order: 2; }
}
@media (max-width: 768px) {
  .contact-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .page-title {
    font-size: 1.8rem;
    margin-bottom: 20px;
    text-align: center;
  }
}
</style>