<template>
  <div class="min-h-screen bg-gray-200 py-6 sm:py-12 px-4 sm:px-6 lg:px-8 font-sans selection:bg-[#FF579A]/30">
    <div class="max-w-4xl mx-auto">
      
      <!-- Dashboard Style Header -->
      <div class="bg-white border-b border-slate-200 p-6 sm:p-8 rounded-t-sm shadow-sm relative overflow-hidden mb-1">
        <div class="absolute -right-10 -top-10 w-40 h-40 bg-pink-50/50 rounded-full blur-2xl"></div>
        <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <router-link to="/" class="flex items-center gap-1.5 text-[9px] font-black text-slate-400 hover:text-[#FF579A] transition-colors uppercase tracking-[0.2em] group mb-4">
              <i class="ph ph-arrow-left transition-transform group-hover:-translate-x-1"></i>
              Back to Flight Booking
            </router-link>
            <div class="flex items-center gap-2 mb-2">
              <div class="w-2 h-2 rounded-full bg-[#FF579A] animate-pulse"></div>
              <span class="text-[10px] font-black text-[#FF579A] uppercase tracking-[0.2em]">Self-Service Portal</span>
            </div>
            <h1 class="text-2xl sm:text-3xl font-black text-slate-900 tracking-tighter uppercase">ONLINE CHECK-IN</h1>
          </div>
          <div class="flex items-center gap-3 bg-slate-50 border border-slate-100 px-4 py-2 rounded-sm shadow-inner">
            <i class="ph ph-shield-check text-[#FF579A] text-xl"></i>
            <div>
              <p class="text-[8px] font-black text-slate-400 uppercase tracking-widest">Protocol Sync</p>
              <p class="text-[10px] font-black text-slate-900 uppercase">Step {{ currentStep }} of {{ steps.length }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Compact Step Indicator -->
      <div class="bg-white border-b border-slate-100 p-4 rounded-b-sm shadow-sm flex items-center justify-between mb-2">
        <div class="flex items-center gap-2 overflow-x-auto no-scrollbar py-1">
          <div v-for="(step, idx) in steps" :key="idx" class="flex items-center gap-2">
            <div 
              :class="[
                'w-5 h-5 rounded-sm flex items-center justify-center text-[9px] font-black transition-all shrink-0',
                currentStep > idx + 1 ? 'bg-emerald-500 text-white' : 
                currentStep === idx + 1 ? 'bg-[#FF579A] text-white shadow-lg lg:scale-110' : 
                'bg-slate-100 text-slate-400 border border-slate-200'
              ]"
            >
              <span v-if="currentStep > idx + 1">✓</span>
              <span v-else>{{ idx + 1 }}</span>
            </div>
            <span :class="['text-[9px] font-black uppercase tracking-widest whitespace-nowrap hidden sm:block', currentStep >= idx + 1 ? 'text-slate-900' : 'text-slate-400']">
              {{ step.label }}
            </span>
            <div v-if="idx < steps.length - 1" class="w-4 h-px bg-slate-200 mx-1 hidden sm:block"></div>
          </div>
        </div>
        <div class="hidden lg:block text-[9px] font-black text-[#FF579A] uppercase tracking-widest bg-pink-50 px-3 py-1 rounded-full border border-pink-100">
          Airline OPS Simulation
        </div>
      </div>

      <!-- Content Area -->
      <div class="bg-white rounded-sm shadow-xl border border-slate-100 overflow-hidden relative">
        <div class="p-6 md:p-10">
          
          <!-- STEP 1: IDENTIFICATION (Direct Access) -->
          <div v-if="currentStep === 1" class="space-y-8 animate-in fade-in duration-500">
            <div class="text-left border-l-4 border-[#FF579A] pl-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h2 class="text-xl font-black text-slate-900 uppercase tracking-tight">Access Protocol</h2>
                <p class="text-slate-400 text-[11px] font-bold uppercase tracking-widest mt-1">Select your authorization method</p>
              </div>
              
              <!-- Choice Toggle: Premium Style -->
              <div class="inline-flex p-1.5 bg-slate-100 rounded-sm gap-2">
                 <button @click="searchMode = 'reference'" 
                   :class="['flex items-center gap-2 px-5 py-2.5 text-[9px] font-black uppercase tracking-[0.2em] transition-all rounded-sm', 
                            searchMode === 'reference' ? 'bg-[#FF579A] text-white shadow-xl lg:scale-105' : 'text-slate-400 hover:text-slate-600']">
                   <i class="ph ph-keyboard-bold text-base"></i>
                   Reference
                 </button>
                 <button @click="searchMode = 'qrcode'" 
                   :class="['flex items-center gap-2 px-5 py-2.5 text-[9px] font-black uppercase tracking-[0.2em] transition-all rounded-sm', 
                            searchMode === 'qrcode' ? 'bg-[#FF579A] text-white shadow-xl lg:scale-105' : 'text-slate-400 hover:text-slate-600']">
                   <i class="ph ph-qr-code-bold text-base"></i>
                   Scan QR
                 </button>
              </div>
            </div>

            <!-- MODE: REFERENCE (Card Style) -->
            <div v-if="searchMode === 'reference'" class="animate-in fade-in slide-in-from-bottom-2 duration-400 space-y-6">
              <div class="bg-slate-50 border border-slate-100 rounded-sm p-8 shadow-inner relative overflow-hidden">
                <div class="absolute -right-20 -bottom-20 w-64 h-64 bg-slate-200/20 rounded-full blur-3xl"></div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 relative z-10">
                  <div class="space-y-3">
                    <label class="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400 ml-1">PNR / Reference</label>
                    <div class="relative group">
                      <div class="absolute inset-y-0 left-0 w-1 bg-[#FF579A] opacity-0 group-focus-within:opacity-100 transition-opacity"></div>
                      <i class="ph ph-ticket absolute left-4 top-1/2 -translate-y-1/2 text-slate-300 group-focus-within:text-[#FF579A] transition-colors"></i>
                      <input 
                        v-model="form.pnr"
                        type="text" 
                        placeholder="PNR NUMBER" 
                        class="w-full bg-white border border-slate-200 rounded-sm px-12 py-5 focus:outline-none focus:border-[#FF579A] transition-all uppercase font-black tracking-[0.3em] text-sm shadow-sm"
                      >
                    </div>
                  </div>
                  <div class="space-y-3">
                    <label class="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400 ml-1">Family Name</label>
                    <div class="relative group">
                      <div class="absolute inset-y-0 left-0 w-1 bg-[#FF579A] opacity-0 group-focus-within:opacity-100 transition-opacity"></div>
                      <i class="ph ph-user-focus absolute left-4 top-1/2 -translate-y-1/2 text-slate-300 group-focus-within:text-[#FF579A] transition-colors"></i>
                      <input 
                        v-model="form.lastName"
                        type="text" 
                        placeholder="LAST NAME" 
                        class="w-full bg-white border border-slate-200 rounded-sm px-12 py-5 focus:outline-none focus:border-[#FF579A] transition-all font-black uppercase text-sm tracking-widest shadow-sm"
                      >
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- MODE: QR SCANNER (Visual Sensor Style) -->
            <div v-if="searchMode === 'qrcode'" class="animate-in fade-in slide-in-from-bottom-2 duration-400">
              <div class="bg-slate-900 rounded-sm p-10 flex flex-col items-center justify-center space-y-8 relative overflow-hidden border-b-4 border-slate-800">
                <div class="absolute inset-0 bg-gradient-to-b from-slate-800/20 to-transparent"></div>
                
                <div class="w-56 h-56 bg-black rounded-sm border-2 border-slate-700 flex items-center justify-center relative shadow-[0_0_50px_rgba(0,0,0,0.5)] overflow-hidden">
                   <!-- Real QR Reader Div -->
                   <div id="checkin-qr-reader" class="absolute inset-0 w-full h-full" v-show="isCameraActive"></div>
                   
                   <div v-if="isCameraActive" class="absolute inset-0 pointer-events-none">
                      <div class="absolute inset-0 border-[40px] border-black/60"></div>
                      <!-- Scanning HUD Layers -->
                      <div class="absolute top-0 left-0 w-full h-full border border-[#FF579A]/20"></div>
                      <div class="absolute top-1/4 left-0 w-full h-0.5 bg-pink-500 shadow-[0_0_20px_#FF579A] animate-scan-line"></div>
                   </div>

                   <div v-if="!isCameraActive" class="relative z-0 text-center space-y-3">
                     <i class="ph ph-aperture text-slate-700 text-6xl animate-spin-slow"></i>
                     <p class="text-[8px] font-black text-slate-600 uppercase tracking-[0.4em]">Optical Lens Standby</p>
                   </div>
                   
                   <!-- Industrial Corner Borders -->
                   <div class="absolute top-4 left-4 w-8 h-8 border-t-2 border-l-2 border-[#FF579A] pointer-events-none"></div>
                   <div class="absolute top-4 right-4 w-8 h-8 border-t-2 border-r-2 border-[#FF579A] pointer-events-none"></div>
                   <div class="absolute bottom-4 left-4 w-8 h-8 border-b-2 border-l-2 border-[#FF579A] pointer-events-none"></div>
                   <div class="absolute bottom-4 right-4 w-8 h-8 border-b-2 border-r-2 border-[#FF579A] pointer-events-none"></div>
                </div>
                
                <div class="text-center space-y-4 relative z-10">
                   <div class="space-y-2">
                      <p class="text-[11px] font-black text-white uppercase tracking-[0.3em] flex items-center justify-center gap-3">
                        <span class="w-1.5 h-1.5 bg-[#FF579A] rounded-full animate-pulse"></span>
                        {{ isCameraActive ? 'Analyzing Itinerary...' : 'Visual Authorization System' }}
                      </p>
                      <p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest max-w-[280px] leading-relaxed mx-auto">
                        Place the QR code from your mobile or printed itinerary within the frame
                      </p>
                   </div>
                   
                   <div class="flex flex-wrap gap-4 justify-center pt-2">
                      <button v-if="!isCameraActive" @click="startCamera" 
                        class="bg-[#FF579A] text-white px-8 py-4 rounded-sm text-[10px] font-black uppercase tracking-[0.2em] shadow-2xl shadow-pink-500/20 active:scale-95 transition-all">
                        Initiate Scanner
                      </button>
                      <button v-else @click="stopCamera" 
                        class="bg-slate-700 text-white px-8 py-4 rounded-sm text-[10px] font-black uppercase tracking-[0.2em] transition-all">
                        Terminate Feed
                      </button>
                      <button @click="showFileSelect" 
                        class="bg-slate-800 border border-slate-700 px-8 py-4 rounded-sm text-[10px] font-black uppercase tracking-[0.2em] text-slate-300 hover:text-white transition-all">
                        Direct Upload
                      </button>
                      <input type="file" ref="fileInputRef" accept="image/*" class="hidden" @change="handleFileUpload">
                      <!-- Hidden container for file scan -->
                      <div id="hidden-qr-reader" style="display: none;"></div>
                   </div>
                </div>
              </div>
            </div>

            <div v-if="error" class="bg-rose-50 border-l-4 border-rose-500 p-4 text-rose-600 text-[10px] font-bold uppercase tracking-widest flex items-center gap-3">
              <i class="ph ph-warning-circle text-lg"></i> {{ error }}
            </div>

            <div class="flex flex-col sm:flex-row gap-3 pt-6">
              <button 
                @click="lookupBooking"
                :disabled="isLoading || !form.pnr || !form.lastName"
                class="flex-1 bg-gray-900 hover:bg-black disabled:opacity-30 text-white font-black py-5 rounded-sm transition-all shadow-xl shadow-slate-200 flex items-center justify-center gap-3 uppercase tracking-[0.2em] text-[10px]"
              >
                <span v-if="isLoading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                <span v-else>Authorize & Search</span>
                <i v-if="!isLoading" class="ph ph-magnifying-glass text-lg"></i>
              </button>
            </div>
          </div>

          <!-- STEP 1.5: PASSENGER SELECTION -->
          <div v-else-if="currentStep === 1.5" class="space-y-8 animate-in slide-in-from-right-4 duration-500">
            <div class="flex items-center justify-between border-l-4 border-[#FF579A] pl-5">
              <div class="text-left">
                <h2 class="text-xl font-black text-slate-900 uppercase tracking-tight">Active Manifest</h2>
                <p class="text-slate-400 text-[11px] font-bold uppercase tracking-widest mt-1">Found {{ foundBookings.length }} records associated with PNR {{ form.pnr }}</p>
              </div>
              <button @click="toggleAll" class="text-[9px] font-black uppercase tracking-widest text-[#FF579A] bg-pink-50 px-3 py-1.5 rounded-sm border border-pink-100 hover:bg-pink-100 transition-all">
                {{ selectedBookings.length > 0 && selectedBookings.length === foundBookings.filter(b => !b.is_checked_in).length ? 'Deselect All' : 'Select All Party' }}
              </button>
            </div>

            <div class="space-y-2">
              <div 
                v-for="booking in foundBookings" 
                :key="booking.id"
                @click="selectBooking(booking)"
                :class="[
                  'p-6 border-2 rounded-sm cursor-pointer transition-all flex items-center justify-between group',
                  selectedBookings.find(b => b.id === booking.id) ? 'border-[#FF579A] bg-pink-50/30' : 'border-slate-50 bg-slate-50/50 hover:border-slate-200'
                ]"
              >
                <div class="flex items-center gap-5 text-left">
                  <div class="flex items-center gap-4">
                     <div :class="['w-5 h-5 border-2 rounded-sm flex items-center justify-center transition-all', selectedBookings.find(b => b.id === booking.id) ? 'bg-[#FF579A] border-[#FF579A]' : 'border-slate-300 bg-white']">
                        <i v-if="selectedBookings.find(b => b.id === booking.id)" class="ph ph-check text-white text-[10px] font-black"></i>
                     </div>
                     <div class="w-12 h-12 bg-white rounded-sm border border-slate-100 flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                       <i class="ph ph-identification-badge text-[#FF579A] text-2xl"></i>
                     </div>
                  </div>
                  <div>
                    <div class="flex items-center gap-2">
                      <div class="font-black text-sm uppercase text-slate-900 tracking-tight">{{ booking.passenger_name }}</div>
                      <span class="text-[8px] font-black px-2 py-0.5 rounded-full uppercase tracking-[0.1em] border"
                        :class="[
                          booking.passenger_type === 'Adult' ? 'bg-slate-100 text-slate-400 border-slate-200' :
                          booking.passenger_type === 'Child' ? 'bg-blue-50 text-blue-500 border-blue-100' :
                          'bg-amber-50 text-amber-600 border-amber-100'
                        ]"
                      >
                        {{ booking.passenger_type }}
                      </span>
                    </div>
                    <div class="text-[9px] text-slate-400 font-black uppercase tracking-widest mt-1">
                      {{ booking.flight_number }} · {{ booking.origin }} → {{ booking.destination }}
                    </div>
                  </div>
                </div>
                <div v-if="booking.is_checked_in" class="bg-emerald-100 text-emerald-600 text-[9px] font-black uppercase px-3 py-1.5 rounded-full border border-emerald-200 shadow-sm">
                  AUTHORIZED
                </div>
                <div v-else-if="booking.checkin_window_status === 'early'" class="bg-amber-100 text-amber-600 text-[9px] font-black uppercase px-3 py-1.5 rounded-full border border-amber-200">
                  TOO EARLY
                </div>
                <div v-else-if="booking.checkin_window_status === 'late'" class="bg-rose-100 text-rose-600 text-[9px] font-black uppercase px-3 py-1.5 rounded-full border border-rose-200">
                  WINDOW CLOSED
                </div>
              </div>
            </div>

            <!-- Empty State for manifestation -->
            <div v-if="foundBookings.length === 0" class="py-12 text-center bg-slate-50 border-2 border-dashed border-slate-200 rounded-sm">
               <i class="ph ph-mask-sad text-4xl text-slate-300 mb-4"></i>
               <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">No pending authorizations found for this PNR</p>
            </div>

            <!-- Help Text for Window Rules -->
            <div class="p-4 bg-slate-50 border border-slate-200 rounded-sm text-left">
              <p class="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] flex items-center gap-2">
                <i class="ph ph-info text-blue-500"></i>
                DCS Protocol: Check-in window opens 48h before and closes 1h before departure.
              </p>
            </div>

            <div v-if="error" class="bg-rose-50 border-l-4 border-rose-500 p-4 text-rose-600 text-[10px] font-bold uppercase tracking-widest flex items-center gap-3">
              <i class="ph ph-warning-circle text-lg"></i> {{ error }}
            </div>

            <div class="flex gap-3">
              <button @click="currentStep = 1" class="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-400 font-black py-5 rounded-sm transition-all uppercase tracking-widest text-[10px]">Back</button>
              <button 
                @click="currentStep = 2"
                :disabled="selectedBookings.length === 0"
                class="flex-[2] bg-gray-900 hover:bg-black disabled:opacity-30 text-white font-black py-5 rounded-sm transition-all shadow-xl uppercase tracking-[0.2em] text-[10px]"
              >
                Continue Verification ({{ selectedBookings.length }})
              </button>
            </div>
          </div>

          <!-- STEP 2: SAFETY -->
          <div v-else-if="currentStep === 2" class="space-y-8 animate-in slide-in-from-right-4 duration-500">
            <div class="text-left border-l-4 border-rose-500 pl-5">
              <h2 class="text-xl font-black text-slate-900 uppercase tracking-tight">Safety Declaration</h2>
              <p class="text-slate-400 text-[11px] font-bold uppercase tracking-widest mt-1">Review prohibited items protocol for {{ selectedBookings.length }} passengers</p>
            </div>

            <div class="bg-slate-50 border border-slate-100 rounded-sm p-8 space-y-8">
              <div class="grid grid-cols-4 gap-4 text-center">
                <div v-for="(icon, idx) in ['🔥', '🔋', '🧪', '🔫']" :key="idx" class="bg-white aspect-square rounded-sm flex items-center justify-center text-3xl border border-slate-100 shadow-sm opacity-100 grayscale hover:grayscale-0 transition-all cursor-default">
                  {{ icon }}
                </div>
              </div>
              <div class="text-[11px] text-slate-500 leading-relaxed text-left space-y-4 font-bold uppercase tracking-tight">
                <p>For safety reasons, prohibited items include but are not limited to: compressed gases, corrosives, explosives, flammable liquids, and infectious substances.</p>
                <div class="p-4 bg-rose-50 text-rose-500 border border-rose-100 rounded-sm italic">
                  Critical: All baggage for the entire party must be cleared of dangerous materials before system authorization.
                </div>
              </div>

              <label class="flex items-start gap-4 p-6 rounded-sm bg-white border border-slate-200 cursor-pointer group hover:border-[#FF579A] transition-all text-left shadow-sm">
                <input 
                  v-model="form.hasDeclaredSafety"
                  type="checkbox" 
                  class="mt-1 w-6 h-6 rounded-sm border-slate-300 text-[#FF579A] focus:ring-0 cursor-pointer"
                >
                <span class="text-[11px] font-black text-slate-500 group-hover:text-slate-900 transition-colors uppercase leading-relaxed tracking-tight">
                  I acknowledge that I have read the policy and confirm that baggage for all passengers contains no prohibited items.
                </span>
              </label>
            </div>

            <div class="flex gap-3">
              <button @click="currentStep = 1.5" class="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-400 font-black py-5 rounded-sm transition-all uppercase tracking-widest text-[10px]">Back</button>
              <button 
                @click="currentStep = 3"
                :disabled="!form.hasDeclaredSafety"
                class="flex-[2] bg-gray-900 hover:bg-black disabled:opacity-30 text-white font-black py-5 rounded-sm transition-all shadow-xl uppercase tracking-[0.2em] text-[10px]"
              >
                Clear Security Protocol
              </button>
            </div>
          </div>

          <!-- STEP 2: SAFETY remains same -->

          <!-- STEP 3: JOURNEY SUMMARY / DOSSIER AUDIT -->
          <div v-else-if="currentStep === 3" class="space-y-8 animate-in slide-in-from-right-4 duration-500">
            <div class="text-left border-l-4 border-emerald-500 pl-5">
              <h2 class="text-xl font-black text-slate-900 uppercase tracking-tight">Dossier Audit</h2>
              <p class="text-slate-400 text-[11px] font-bold uppercase tracking-widest mt-1">Review operational journey data for {{ selectedBookings.length }} passengers</p>
            </div>

            <div class="space-y-6">
               <div v-for="booking in selectedBookings" :key="booking.id" class="bg-slate-50 border border-slate-100 rounded-sm overflow-hidden p-6 space-y-6">
                  <div class="flex items-center justify-between border-b border-slate-200 pb-4">
                     <div class="flex items-center gap-3">
                        <div class="w-8 h-8 bg-slate-900 text-white rounded-sm flex items-center justify-center font-black text-xs">
                           {{ booking.passenger_name.charAt(0) }}
                        </div>
                        <div class="text-left flex items-center gap-2">
                           <div>
                              <span class="block text-[9px] font-black text-slate-400 uppercase tracking-widest">Passenger Manifest Link</span>
                              <div class="flex items-center gap-2">
                                <span class="block text-sm font-black text-slate-900 uppercase tracking-tight">{{ booking.passenger_name }}</span>
                                <span class="text-[8px] font-black px-1.5 py-0.5 rounded-full uppercase tracking-widest border"
                                  :class="[
                                    booking.passenger_type === 'Adult' ? 'bg-white text-slate-400 border-slate-200' :
                                    booking.passenger_type === 'Child' ? 'bg-blue-50 text-blue-500 border-blue-100' :
                                    'bg-amber-50 text-amber-600 border-amber-100'
                                  ]"
                                >
                                  {{ booking.passenger_type }}
                                </span>
                              </div>
                           </div>
                        </div>
                     </div>
                     <div class="text-right">
                        <span class="block text-[9px] font-black text-slate-400 uppercase tracking-widest">Flight ID</span>
                        <span class="block text-xs font-black text-[#FF579A] uppercase tracking-widest">{{ booking.flight_number }}</span>
                     </div>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <button @click="activePassengerId = booking.id; showSeatModal = true;" class="flex items-center justify-between p-4 bg-white border border-slate-200 rounded-sm hover:border-[#FF579A] transition-all group">
                       <div class="flex items-center gap-4">
                          <div class="w-10 h-10 bg-slate-50 rounded-sm flex items-center justify-center text-[#FF579A] border border-slate-100 shadow-sm">
                             <i class="ph ph-chair text-xl"></i>
                          </div>
                          <div class="text-left">
                             <span class="block text-[9px] font-black text-slate-400 uppercase tracking-widest">Seat Slot</span>
                             <span class="block text-xs font-black text-slate-900 uppercase tracking-tighter">
                               {{ booking.passenger_type === 'Infant' ? (tempSelections[booking.id]?.seat?.seat_number || 'SEAT ON LAP') : (tempSelections[booking.id]?.seat?.seat_number || 'NOT ASSIGNED') }}
                             </span>
                          </div>
                       </div>
                       <i class="ph ph-arrow-right text-slate-300 group-hover:text-[#FF579A] transition-all"></i>
                    </button>
                    
                    <button @click="activePassengerId = booking.id; showAddonModal = true;" class="flex items-center justify-between p-4 bg-white border border-slate-200 rounded-sm hover:border-[#FF579A] transition-all group">
                       <div class="flex items-center gap-4">
                          <div class="w-10 h-10 bg-slate-50 rounded-sm flex items-center justify-center text-[#FF579A] border border-slate-100 shadow-sm">
                             <i class="ph ph-package text-xl"></i>
                          </div>
                          <div class="text-left">
                             <span class="block text-[9px] font-black text-slate-400 uppercase tracking-widest">Baggage & Meals</span>
                             <div class="mt-1 flex flex-wrap gap-1">
                               <span v-if="!tempSelections[booking.id]?.addon_details || tempSelections[booking.id].addon_details.length === 0" class="text-[10px] font-bold text-slate-400 uppercase italic">No items secured</span>
                               <span 
                                  v-for="(addon, idx) in tempSelections[booking.id]?.addon_details" 
                                  :key="idx"
                                  class="bg-pink-50 text-[10px] font-black text-[#FF579A] px-2 py-0.5 rounded-full border border-pink-100 uppercase"
                               >
                                  {{ addon }}
                               </span>
                             </div>
                          </div>
                       </div>
                       <i class="ph ph-plus-circle text-slate-300 group-hover:text-[#FF579A] transition-all text-xl"></i>
                    </button>
                  </div>
               </div>
            </div>

            <div class="flex gap-3">
              <button @click="currentStep = 2" class="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-400 font-black py-5 rounded-sm transition-all uppercase tracking-widest text-[10px]">Back</button>
              <button 
                @click="currentStep = 4"
                class="flex-[2] bg-gray-900 hover:bg-black text-white font-black py-5 rounded-sm transition-all shadow-xl uppercase tracking-[0.2em] text-[10px]"
              >
                Proceed to Contact Link
              </button>
            </div>
          </div>

          <!-- STEP 4: CONTACT & FINAL -->
          <div v-else-if="currentStep === 4" class="space-y-8 animate-in slide-in-from-right-4 duration-500">
            <div class="text-left border-l-4 border-blue-500 pl-5">
              <h2 class="text-xl font-black text-slate-900 uppercase tracking-tight">Contact Integration</h2>
              <p class="text-slate-400 text-[11px] font-bold uppercase tracking-widest mt-1">Dispatch digital credentials for {{ selectedBookings.length }} passengers</p>
            </div>

            <div class="space-y-6">
               <div v-for="booking in selectedBookings" :key="booking.id" class="bg-slate-50 border border-slate-100 rounded-sm p-6 space-y-6">
                  <div class="flex items-center gap-3 border-b border-slate-200 pb-4">
                     <div class="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center font-black text-[10px]">
                        {{ selectedBookings.indexOf(booking) + 1 }}
                     </div>
                     <span class="text-sm font-black text-slate-900 uppercase tracking-tight">{{ booking.passenger_name }}</span>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="space-y-4">
                      <div class="space-y-2 text-left">
                        <label class="text-[9px] font-black uppercase tracking-widest text-slate-400 ml-1 flex items-center justify-between">
                           Email Address
                           <button v-if="selectedBookings.indexOf(booking) === 0" @click="copyEmailToAll(booking.id)" class="text-[8px] text-blue-500 hover:underline">Copy to All</button>
                        </label>
                        <input 
                          v-model="form.passengers[booking.id].email"
                          type="email" 
                          placeholder="AGENT@TURSIM.COM"
                          class="w-full bg-white border border-slate-200 rounded-sm px-5 py-4 focus:ring-1 focus:ring-blue-500 transition-all font-black uppercase text-sm"
                        >
                      </div>
                    </div>

                    <div class="space-y-4">
                      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div class="space-y-2 text-left">
                          <label class="text-[9px] font-black uppercase tracking-widest text-slate-400 ml-1 flex items-center justify-between">
                             Mobile Phone Country
                             <button v-if="selectedBookings.indexOf(booking) === 0" @click="copyPhoneToAll(booking.id)" class="text-[8px] text-blue-500 hover:underline">Copy to All</button>
                          </label>
                          <select v-model="form.passengers[booking.id].phone_country" class="w-full bg-white border border-slate-200 rounded-sm px-5 py-4 font-black uppercase text-sm outline-none transition-all">
                            <option value="PH +63">Philippines (+63)</option>
                            <option value="US +1">United States (+1)</option>
                            <option value="AE +971">United Arab Emirates (+971)</option>
                            <option value="SG +65">Singapore (+65)</option>
                            <option value="JP +81">Japan (+81)</option>
                          </select>
                        </div>
                        <div class="space-y-2 text-left">
                          <label class="text-[9px] font-black uppercase tracking-widest text-slate-400 ml-1">Mobile Phone Number</label>
                          <input 
                            v-model="form.passengers[booking.id].phone"
                            type="tel" 
                            placeholder="09278874355"
                            class="w-full bg-white border border-slate-200 rounded-sm px-5 py-4 focus:ring-1 focus:ring-blue-500 transition-all font-black text-sm"
                          >
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="grid grid-cols-1 gap-4 pt-4">
                      <div class="space-y-2 text-left">
                         <label class="text-[9px] font-black uppercase tracking-widest text-slate-400 ml-1">Loyalty / Frequent Flyer (Opt)</label>
                         <select v-model="form.passengers[booking.id].loyalty_program" class="w-full bg-white border border-slate-200 rounded-sm px-5 py-4 font-black uppercase text-sm outline-none border-l-4 border-l-slate-200 focus:border-l-pink-500 transition-all">
                            <option value="">No Program Linked</option>
                            <option value="miles">FlyHigh Miles</option>
                            <option value="sky">SkyPriority Rewards</option>
                            <option value="global">Global Connect Loyalty</option>
                         </select>
                      </div>
                  </div>
               </div>
            </div>

            <div v-if="error" class="bg-rose-50 border-l-4 border-rose-500 p-4 text-rose-600 text-[10px] font-bold uppercase tracking-widest flex items-center gap-3">
              <i class="ph ph-warning-circle text-lg"></i> {{ error }}
            </div>

            <div class="flex gap-3">
              <button @click="currentStep = 3" class="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-400 font-black py-5 rounded-sm transition-all uppercase tracking-widest text-[10px]">Back</button>
              <button 
                @click="processCheckin"
                :disabled="isLoading"
                class="flex-[2] bg-gray-900 hover:bg-black disabled:opacity-30 text-white font-black py-5 rounded-sm transition-all shadow-xl uppercase tracking-[0.2em] text-[10px]"
              >
                <span v-if="isLoading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></span>
                Finalize Group Authorization
              </button>
            </div>
          </div>

          <!-- STEP 5: ISSUANCE -->
          <div v-else-if="currentStep === 5" class="space-y-10 animate-in zoom-in duration-500 text-center">
            <div class="space-y-4">
              <div class="w-20 h-20 bg-emerald-50 rounded-full flex items-center justify-center mx-auto border border-emerald-100 shadow-inner">
                <i class="ph ph-ticket text-4xl text-emerald-500"></i>
              </div>
              <h2 class="text-3xl font-black text-slate-900 uppercase tracking-tighter">Passes Issued</h2>
              <p class="text-slate-400 text-[11px] font-bold uppercase tracking-widest">{{ checkinResults.length }} digital credentials generated and encrypted</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
               <div v-for="result in checkinResults" :key="result.id" class="bg-white border border-slate-200 rounded-sm shadow-2xl relative overflow-hidden text-slate-900">
                  <div class="bg-gray-900 p-6 text-white relative">
                    <div class="absolute -right-6 -top-6 w-24 h-24 bg-white/5 rounded-full blur-2xl"></div>
                    <div class="flex justify-between items-start text-left">
                       <div>
                          <p class="text-[8px] font-black text-slate-400 uppercase tracking-widest mb-1.5 opacity-70">Operation Module</p>
                          <p class="text-lg font-black uppercase tracking-tight">{{ result.flight_number }}</p>
                          <p class="text-[9px] font-black text-[#FF579A] mt-1">{{ result.passenger_name }}</p>
                       </div>
                       <div class="text-right">
                          <p class="text-[8px] font-black text-slate-400 uppercase tracking-widest mb-1.5 opacity-70">Assigned Slot</p>
                          <p class="text-2xl font-black text-[#FF579A] leading-none">{{ result.seat_number || 'TBA' }}</p>
                       </div>
                    </div>
                  </div>
                  <div class="p-6 space-y-6">
                     <div class="bg-slate-50 border border-slate-100 p-4 rounded-sm flex flex-col items-center">
                        <div class="bg-white p-2 rounded-sm border border-slate-200 shadow-sm mb-3">
                           <img 
                             :src="`https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=${result.boarding_pass}`" 
                             alt="QR Pass"
                             class="w-24 h-24"
                           >
                        </div>
                        <p class="text-[8px] font-black text-slate-400 uppercase tracking-[0.3em]">{{ result.boarding_pass }}</p>
                     </div>
                     <button @click="downloadIndividualPass(result.booking_detail)" class="w-full bg-slate-900 hover:bg-black text-white py-3 rounded-sm text-[9px] font-black uppercase tracking-widest transition-all">Download PDF</button>
                  </div>
               </div>
            </div>

            <button @click="currentStep = 6" class="w-full max-w-sm bg-gray-900 hover:bg-black text-white font-black py-5 rounded-sm transition-all shadow-xl uppercase tracking-[0.2em] text-[10px]">Complete Group Protocol</button>
            
            <div class="max-w-md mx-auto space-y-4">
               <button 
                 @click="dispatchEmail"
                 :disabled="isSendingEmail || emailSentStatus === 'success'"
                 :class="[
                   'w-full py-5 rounded-sm font-black uppercase tracking-widest text-[10px] transition-all flex items-center justify-center gap-3',
                   emailSentStatus === 'success' ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-100' : 'bg-white border border-slate-200 text-slate-900 hover:bg-slate-50 shadow-sm'
                 ]"
               >
                  <template v-if="isSendingEmail">
                    <span class="w-4 h-4 border-2 border-slate-300 border-t-slate-900 rounded-full animate-spin"></span>
                    Encrypting & Dispatching...
                  </template>
                  <template v-else-if="emailSentStatus === 'success'">
                    <i class="ph ph-check-circle text-lg"></i>
                    Boarding Passes Transmitted
                  </template>
                  <template v-else>
                    <i class="ph ph-mask-happy text-lg text-blue-500"></i>
                    Resend All via Secure Email
                  </template>
               </button>
               <p v-if="emailSentStatus === 'success'" class="text-[9px] font-bold text-emerald-500 uppercase tracking-widest animate-pulse">Boarding passes have been automatically dispatched to your secure inbox.</p>
            </div>
          </div>

          <!-- STEP 6: DONE -->
          <div v-else-if="currentStep === 6" class="py-12 text-center animate-in zoom-in duration-500">
             <div class="w-24 h-24 bg-emerald-50 rounded-full flex items-center justify-center mx-auto mb-8 border border-emerald-100 shadow-inner">
               <i class="ph ph-shield-check text-5x text-emerald-500"></i>
             </div>
             <h2 class="text-4xl font-black mb-4 uppercase tracking-tighter text-slate-900">System Clear</h2>
             <div class="max-w-md mx-auto space-y-8">
                <p class="text-slate-400 text-[11px] font-bold uppercase tracking-[0.2em] leading-relaxed">Authorization complete. All digital passes have been dispatched to the secure link provided. Safe travels, agent.</p>
                <div class="grid grid-cols-1 gap-2">
                   <div class="flex items-center gap-4 bg-slate-50 p-4 rounded-sm border border-slate-100 text-left">
                      <div class="w-8 h-8 bg-emerald-500 text-white rounded-sm flex items-center justify-center shadow-lg shadow-emerald-100">
                         <i class="ph ph-check-bold"></i>
                      </div>
                      <span class="text-[10px] font-black uppercase tracking-widest text-slate-700">Identity Verified</span>
                   </div>
                   <div class="flex items-center gap-4 bg-slate-50 p-4 rounded-sm border border-slate-100 text-left">
                      <div class="w-8 h-8 bg-emerald-500 text-white rounded-sm flex items-center justify-center shadow-lg shadow-emerald-100">
                         <i class="ph ph-check-bold"></i>
                      </div>
                      <span class="text-[10px] font-black uppercase tracking-widest text-slate-700">Boarding Pass Encrypted</span>
                   </div>
                </div>
                <button @click="$router.push('/student/dashboard')" class="w-full bg-[#FF579A] hover:bg-[#ff3d8b] text-white font-black py-5 rounded-sm transition-all shadow-xl shadow-pink-100 uppercase tracking-[0.2em] text-[11px]">Return to Ops Center</button>
             </div>
          </div>

        </div>
      </div>

    </div>

    <!-- MODALS SECTION -->
    <Teleport to="body">
      <!-- Seat Selection Modal -->
      <div v-if="showSeatModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
        <div class="absolute inset-0 bg-slate-900/80 backdrop-blur-md" @click="showSeatModal = false"></div>
        <div class="relative bg-white w-full max-w-4xl h-[90vh] flex flex-col rounded-sm overflow-hidden animate-in zoom-in shadow-2xl">
          <!-- Header -->
          <div class="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50">
            <div>
              <h2 class="text-lg font-black text-slate-900 uppercase tracking-widest">Select Your Slot</h2>
              <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Flight {{ selectedBooking?.flight_number }} · {{ seatMapData?.aircraft_model || 'Standard Configuration' }}</p>
            </div>
            <button @click="showSeatModal = false" class="w-10 h-10 flex items-center justify-center rounded-sm bg-white border border-slate-200 text-slate-400 hover:text-pink-500 transition-colors">
              <i class="ph ph-x text-xl"></i>
            </button>
          </div>

          <!-- Seat Map Content -->
          <div class="flex-1 overflow-y-auto bg-slate-200/50 p-8 no-scrollbar">
            <div class="max-w-md mx-auto bg-white rounded-t-[100px] border-x border-t border-slate-200 p-10 pb-20 shadow-inner">
               <!-- Cockpit section -->
               <div class="w-full h-24 mb-10 flex flex-col items-center justify-center border-b border-slate-100">
                  <div class="w-16 h-1 bg-slate-200 rounded-full mb-2"></div>
                  <span class="text-[10px] font-black text-slate-300 tracking-[0.3em] uppercase">Flight Deck</span>
               </div>

               <!-- Legend -->
               <div class="flex items-center justify-center gap-6 mb-12">
                  <div class="flex items-center gap-2">
                     <div class="w-3 h-3 bg-pink-500 rounded-sm"></div>
                     <span class="text-[9px] font-black text-slate-400 uppercase">You</span>
                  </div>
                  <div class="flex items-center gap-2">
                     <div class="w-3 h-3 bg-slate-100 border border-slate-200 rounded-sm"></div>
                     <span class="text-[9px] font-black text-slate-400 uppercase">Vacant</span>
                  </div>
                  <div class="flex items-center gap-2">
                     <div class="w-3 h-3 bg-slate-800 rounded-sm"></div>
                     <span class="text-[9px] font-black text-slate-400 uppercase">Occupied</span>
                  </div>
               </div>

               <!-- Grid -->
               <div v-if="seatMapData" class="space-y-4">
                  <div v-for="rowNum in Math.max(...seatMapData.seats.map(s => s.row))" :key="rowNum" class="flex items-center justify-center gap-4">
                     <!-- Left Seats -->
                     <div class="flex gap-2">
                        <template v-for="col in ['A', 'B', 'C']" :key="col">
                           <div v-if="seatMapData.seats.find(s => s.row === rowNum && s.column === col)"
                              @click="seatMapData.seats.find(s => s.row === rowNum && s.column === col).is_available && (tempSelections[activePassengerId].seat = seatMapData.seats.find(s => s.row === rowNum && s.column === col))"
                              :class="[
                                 'w-10 h-10 rounded-sm flex items-center justify-center text-[10px] font-black transition-all border outline-none',
                                 !seatMapData.seats.find(s => s.row === rowNum && s.column === col).is_available ? 'bg-slate-800 border-slate-800 text-slate-500 cursor-not-allowed' :
                                 tempSelections[activePassengerId]?.seat?.id === seatMapData.seats.find(s => s.row === rowNum && s.column === col).id ? 'bg-pink-500 border-pink-500 text-white shadow-lg shadow-pink-200' :
                                 'bg-white border-slate-200 text-slate-900 hover:border-pink-300 cursor-pointer active:scale-95'
                              ]">
                              {{ col }}
                           </div>
                        </template>
                     </div>
                     <!-- Aisle -->
                     <div class="w-8 flex items-center justify-center">
                        <span class="text-[11px] font-black text-slate-300">{{ rowNum }}</span>
                     </div>
                     <!-- Right Seats -->
                     <div class="flex gap-2">
                        <template v-for="col in ['D', 'E', 'F']" :key="col">
                           <div v-if="seatMapData.seats.find(s => s.row === rowNum && s.column === col)"
                              @click="seatMapData.seats.find(s => s.row === rowNum && s.column === col).is_available && (tempSelections[activePassengerId].seat = seatMapData.seats.find(s => s.row === rowNum && s.column === col))"
                              :class="[
                                 'w-10 h-10 rounded-sm flex items-center justify-center text-[10px] font-black transition-all border outline-none',
                                 !seatMapData.seats.find(s => s.row === rowNum && s.column === col).is_available ? 'bg-slate-800 border-slate-800 text-slate-500 cursor-not-allowed' :
                                 tempSelections[activePassengerId]?.seat?.id === seatMapData.seats.find(s => s.row === rowNum && s.column === col).id ? 'bg-pink-500 border-pink-500 text-white shadow-lg shadow-pink-200' :
                                 'bg-white border-slate-200 text-slate-900 hover:border-pink-300 cursor-pointer active:scale-95'
                              ]">
                              {{ col }}
                           </div>
                        </template>
                     </div>
                  </div>
               </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="p-6 border-t border-slate-100 flex items-center justify-between bg-white">
            <div class="text-left">
              <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest block">Selected Slot</span>
              <span class="text-xl font-black text-slate-900">{{ tempSelections[activePassengerId]?.seat?.seat_code || '---' }}</span>
            </div>
            <button @click="confirmChanges" 
               class="bg-[#FF579A] hover:bg-[#ff3d8b] text-white font-black px-10 py-4 rounded-sm transition-all shadow-xl shadow-pink-100 uppercase tracking-widest text-[11px]">
               Confirm Assignment
            </button>
          </div>
        </div>
      </div>

      <!-- Ancillaries Modal -->
      <div v-if="showAddonModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
        <div class="absolute inset-0 bg-slate-900/80 backdrop-blur-md" @click="showAddonModal = false"></div>
        <div class="relative bg-white w-full max-w-2xl h-[80vh] flex flex-col rounded-sm overflow-hidden animate-in zoom-in shadow-2xl">
           <div class="p-6 border-b border-slate-100 flex items-center justify-between">
              <h2 class="text-lg font-black text-slate-900 uppercase tracking-widest">Auxiliary Catalog</h2>
              <button @click="showAddonModal = false" class="text-slate-400 hover:text-pink-500 transition-colors"><i class="ph ph-x text-2xl"></i></button>
           </div>
           
           <div class="flex-1 overflow-y-auto p-6 space-y-8 no-scrollbar">
              <!-- Meals -->
              <div>
                 <h3 class="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] mb-4">Galley Services / Meals</h3>
                 <div class="grid grid-cols-1 gap-3">
                    <div v-for="meal in availableAddons.meals" :key="meal.id" 
                       @click="toggleAddon(meal)"
                       :class="['p-4 border transition-all flex items-center justify-between cursor-pointer rounded-sm', 
                          tempSelections[activePassengerId]?.addons.some(a => a.id === meal.id) ? 'border-pink-500 bg-pink-50/50' : 'border-slate-100 hover:border-pink-200']">
                       <div class="flex items-center gap-4">
                          <div class="w-10 h-10 bg-slate-50 flex items-center justify-center rounded-sm text-slate-400 border border-slate-100">
                             <i class="ph ph-bowl-food text-xl"></i>
                          </div>
                          <div class="text-left">
                             <p class="text-xs font-black text-slate-900 leading-none mb-1">{{ meal.name }}</p>
                             <p class="text-[9px] font-bold text-slate-400 uppercase">{{ meal.description || 'Verified Airline Meal' }}</p>
                          </div>
                       </div>
                       <span class="text-xs font-black text-emerald-500 uppercase tracking-widest">Complimentary</span>
                    </div>
                 </div>
              </div>

              <!-- Baggage -->
              <div>
                 <h3 class="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] mb-4">Logistics / Extra Baggage</h3>
                 <div class="grid grid-cols-1 gap-3">
                    <div v-for="bag in availableAddons.baggage" :key="bag.id" 
                       @click="toggleAddon(bag)"
                       :class="['p-4 border transition-all flex items-center justify-between cursor-pointer rounded-sm', 
                          tempSelections[activePassengerId]?.addons.some(a => a.id === bag.id) ? 'border-pink-500 bg-pink-50/50' : 'border-slate-100 hover:border-pink-200']">
                       <div class="flex items-center gap-4">
                          <div class="w-10 h-10 bg-slate-50 flex items-center justify-center rounded-sm text-slate-400 border border-slate-100">
                             <i class="ph ph-suitcase text-xl"></i>
                          </div>
                          <div class="text-left">
                             <p class="text-xs font-black text-slate-900 leading-none mb-1">{{ bag.name }}</p>
                             <p class="text-[9px] font-bold text-slate-400 uppercase">Weight Class Expansion</p>
                          </div>
                       </div>
                       <span class="text-xs font-black text-emerald-500 uppercase tracking-widest">Complimentary</span>
                    </div>
                 </div>
              </div>
           </div>

           <div class="p-6 border-t border-slate-100 bg-slate-50 flex items-center justify-between font-black">
              <div class="text-left">
                 <p class="text-[10px] text-slate-400 uppercase tracking-widest leading-none mb-1">Total Auxiliary</p>
                 <p class="text-lg text-slate-900">₱{{ additionalCharges.toLocaleString() }}</p>
              </div>
              <button @click="confirmChanges" class="bg-[#FF579A] text-white px-10 py-4 text-[11px] uppercase tracking-widest shadow-lg shadow-pink-100 transition-all hover:bg-[#ff3d8b]">Review Dossier</button>
           </div>
        </div>
      </div>

      <!-- Payment Modal (Simulation) -->
      <div v-if="showPaymentModal" class="fixed inset-0 z-[110] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-950/90 backdrop-blur-xl" @click="showPaymentModal = false"></div>
        <div class="relative bg-white w-full max-w-md p-8 rounded-sm animate-in zoom-in shadow-2xl text-center">
           <div class="w-16 h-16 bg-slate-50 border border-slate-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <i class="ph ph-credit-card text-3xl text-slate-400"></i>
           </div>
           <h2 class="text-lg font-black text-slate-900 uppercase tracking-[0.2em] mb-2">Secure Authorization</h2>
           <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-8">Authorizing Charge: ₱{{ additionalCharges.toLocaleString() }}</p>

           <div class="space-y-4 text-left mb-8">
              <div class="space-y-1">
                 <label class="text-[9px] font-black text-slate-400 uppercase tracking-widest ml-1">Mock Card Number</label>
                 <input type="text" value="**** **** **** 4455" readonly class="w-full bg-slate-50 border border-slate-100 p-4 rounded-sm text-sm font-black text-slate-900 outline-none">
              </div>
              <div class="grid grid-cols-2 gap-4">
                 <div class="space-y-1">
                    <label class="text-[9px] font-black text-slate-400 uppercase tracking-widest ml-1">Expiry</label>
                    <input type="text" value="12/28" readonly class="w-full bg-slate-50 border border-slate-100 p-4 rounded-sm text-sm font-black text-slate-900 outline-none">
                 </div>
                 <div class="space-y-1">
                    <label class="text-[9px] font-black text-slate-400 uppercase tracking-widest ml-1">CVV</label>
                    <input type="text" value="***" readonly class="w-full bg-slate-50 border border-slate-100 p-4 rounded-sm text-sm font-black text-slate-900 outline-none">
                 </div>
              </div>
           </div>

           <button @click="processPayment" 
              :disabled="isProcessingPayment"
              class="w-full bg-slate-900 hover:bg-black text-white py-5 rounded-sm font-black text-[11px] uppercase tracking-[0.3em] transition-all disabled:opacity-50">
              <span v-if="isProcessingPayment" class="flex items-center justify-center gap-2">
                 <div class="w-3 h-3 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                 Authorizing...
              </span>
              <span v-else>Authorize Transaction</span>
           </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Html5Qrcode, Html5QrcodeSupportedFormats } from 'html5-qrcode'
import axios from '@/services/api/axios'
import { seatService } from '@/services/booking/seatService'
import { addonService } from '@/services/booking/addonService'

const steps = [
  { label: 'Details' },
  { label: 'Safety' },
  { label: 'Audit' },
  { label: 'Link' },
  { label: 'Pass' },
  { label: 'Clear' }
]

const currentStep = ref(1)
const isLoading = ref(false)
const error = ref(null)

const form = reactive({
  pnr: '',
  lastName: '',
  hasDeclaredSafety: false,
  // Per-passenger contact info
  passengers: {} 
})

const searchMode = ref('reference') // 'reference' or 'qrcode'
const isCameraActive = ref(false)
const html5QrCodeRef = ref(null)
const fileInputRef = ref(null)

const startCamera = async () => {
  try {
    error.value = null
    const html5QrCode = new Html5Qrcode("checkin-qr-reader")
    
    // Attempt back camera first, fallback to any
    const cameraConfig = { facingMode: "environment" }
    
    await html5QrCode.start(
      cameraConfig,
      { 
        fps: 30, // Increased for smoother detection
        aspectRatio: 1,
        disableFlip: false,
        formatsToSupport: [ Html5QrcodeSupportedFormats.QR_CODE ], // Limit to QR only to drastically speed up
        experimentalFeatures: {
            useBarCodeDetectorIfSupported: true // Hardware native APIs
        }
      },
      (decodedText) => {
        form.pnr = decodedText.trim()
        form.lastName = 'QR_VERIFIED'
        stopCamera()
        lookupBooking() // Auto authorize and search
      },
      (err) => {
        // ignore ongoing decode errs
      }
    ).catch(async (e) => {
      // Fallback to front camera or default if environment fails
      await html5QrCode.start(
        { facingMode: "user" },
        { 
          fps: 30, 
          aspectRatio: 1, 
          disableFlip: false,
          formatsToSupport: [ Html5QrcodeSupportedFormats.QR_CODE ],
          experimentalFeatures: { useBarCodeDetectorIfSupported: true }
        },
        (decodedText) => {
          form.pnr = decodedText.trim()
          form.lastName = 'QR_VERIFIED'
          stopCamera()
          lookupBooking()
        },
        () => {}
      )
    })
    
    isCameraActive.value = true
    html5QrCodeRef.value = html5QrCode
  } catch (err) {
    console.error("Camera access error:", err)
    error.value = "Hardware Access Denied: Could not activate camera sensor. Try 'Direct Upload'."
  }
}

const stopCamera = () => {
  if (html5QrCodeRef.value) {
    html5QrCodeRef.value.stop().catch(e => console.error("Stop error", e))
    html5QrCodeRef.value = null
  }
  isCameraActive.value = false
}

const showFileSelect = () => {
  fileInputRef.value?.click()
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  isLoading.value = true
  error.value = null
  
  try {
    const html5QrCode = new Html5Qrcode("hidden-qr-reader")
    const decodedText = await html5QrCode.scanFile(file, true)
    
    form.pnr = decodedText.trim()
    form.lastName = 'QR_VERIFIED'
    lookupBooking() // Auto authorize and search
  } catch (err) {
    console.error("File scan failed", err)
    error.value = "Failed to parse QR code from image."
  } finally {
    isLoading.value = false
    event.target.value = '' // reset input
  }
}



const foundBookings = ref([])
const selectedBookings = ref([]) // plural
const checkinResults = ref([]) // plural

// NEW: Modal and Selection State
const showSeatModal = ref(false)
const showAddonModal = ref(false)
const showPaymentModal = ref(false)

const activePassengerId = ref(null) // which passenger is being edited in modal
const seatMapData = ref(null)
const availableAddons = ref({
  meals: [],
  baggage: [],
  assistance: []
})

// Stores pending changes per passenger
const tempSelections = reactive({})

const paymentForm = reactive({
  cardNumber: '',
  expiry: '',
  cvv: '',
  name: ''
})

const isProcessingPayment = ref(false)
const isUpdatingDossier = ref(false)
const isSendingEmail = ref(false)
const emailSentStatus = ref(null) // null, 'success', 'error'

const dispatchEmail = async () => {
  if (checkinResults.value.length === 0) return
  
  isSendingEmail.value = true
  emailSentStatus.value = null
  
  try {
    const bookingDetailIds = checkinResults.value.map(r => {
      const bd = r.booking_detail
      return (bd && typeof bd === 'object') ? bd.id : bd
    })
    await axios.post('/api/checkins/dispatch_email/', {
      booking_detail_ids: bookingDetailIds
    })
    emailSentStatus.value = 'success'
    setTimeout(() => { emailSentStatus.value = null }, 5000)
  } catch (err) {
    emailSentStatus.value = 'error'
    error.value = "Dispatch Protocol Failure: Could not transmit digital credentials."
  } finally {
    isSendingEmail.value = false
  }
}

// Computed for total additional charges - SET TO 0 AS PER REQUEST (FREE ALL)
const additionalCharges = computed(() => {
  return 0
})

const lookupBooking = async () => {
  isLoading.value = true
  error.value = null
  try {
    const response = await axios.post('/api/checkins/lookup/', {
      pnr: form.pnr,
      last_name: form.lastName
    })
    const allRecords = response.data
    const pending = allRecords.filter(b => !b.is_checked_in)
    
    if (allRecords.length > 0 && pending.length === 0) {
      error.value = 'All passengers in this reservation are already authorized and checked in.'
      return
    }
    
    foundBookings.value = pending
    currentStep.value = 1.5
  } catch (err) {
    error.value = err.response?.data?.error || 'Authorization failed. Records inaccessible.'
  } finally {
    isLoading.value = false
  }
}

const selectBooking = (booking) => {
  if (booking.is_checked_in) return
  if (booking.checkin_window_status !== 'open') {
    error.value = `This flight is outside the check-in window. (${booking.checkin_window_status === 'early' ? 'Too early' : 'Window closed'})`
    return
  }
  
  error.value = null
  
  const index = selectedBookings.value.findIndex(b => b.id === booking.id)
  if (index === -1) {
    selectedBookings.value.push(booking)
    // Initialize state if not exists
    if (!tempSelections[booking.id]) {
      tempSelections[booking.id] = {
        seat: booking.seat ? { id: booking.seat, seat_number: booking.seat_number } : null,
        addons: [], 
        addon_details: booking.addon_details || []
      }
    }
    if (!form.passengers[booking.id]) {
      form.passengers[booking.id] = {
        email: '',
        phone_country: 'PH +63',
        phone: '',
        loyalty_program: ''
      }
    }
  } else {
    selectedBookings.value.splice(index, 1)
  }
}

const toggleAll = () => {
  const available = foundBookings.value.filter(b => !b.is_checked_in)
  if (available.length === 0) return

  if (selectedBookings.value.length === available.length) {
    selectedBookings.value = []
  } else {
    // Select all available and in-window
    available.forEach(b => {
      if (b.checkin_window_status === 'open' && !selectedBookings.value.find(s => s.id === b.id)) {
        selectBooking(b)
      }
    })
    
    if (selectedBookings.value.length === 0 && available.some(b => b.checkin_window_status !== 'open')) {
      error.value = "Some passengers are outside the check-in window and cannot be selected."
    }
  }
}


const downloadIndividualPass = (bookingDetail) => {
    // Extract ID whether booking_detail is an object or a raw ID
    const id = (bookingDetail && typeof bookingDetail === 'object') ? bookingDetail.id : bookingDetail
    window.open(`${axios.defaults.baseURL}api/dcs/boarding-pass/${id}/`, '_blank')
}

// NEW: Interactive Logic
const openSeatSelection = async () => {
  if (!activePassengerId.value) return
  const passenger = selectedBookings.value.find(b => b.id === activePassengerId.value)
  if (!passenger) return
  
  isLoading.value = true
  try {
    const data = await seatService.getSeatsBySchedule(passenger.schedule)
    seatMapData.value = data
    // Keep seat from temp selection if already modified, otherwise from original
    const currentSeatId = tempSelections[passenger.id].seat?.id || passenger.seat
    tempSelections[passenger.id].seat = data.seats.find(s => s.id === currentSeatId)
    showSeatModal.value = true
  } catch (err) {
    error.value = "Terminal error: Could not synchronize seat map."
  } finally {
    isLoading.value = false
  }
}

const openAddonSelection = async () => {
  if (!activePassengerId.value) return
  const passenger = selectedBookings.value.find(b => b.id === activePassengerId.value)
  if (!passenger) return

  isLoading.value = true
  try {
    const response = await axios.get('/api/add-ons/')
    availableAddons.value.meals = response.data.filter(a => a.addon_type_name === 'Meal')
    availableAddons.value.baggage = response.data.filter(a => a.addon_type_name === 'Baggage')
    availableAddons.value.assistance = response.data.filter(a => a.addon_type_name === 'Assistance')
    
    showAddonModal.value = true
  } catch (err) {
    error.value = "Terminal error: Could not retrieve auxiliary catalog."
  } finally {
    isLoading.value = false
  }
}

const toggleAddon = (addon) => {
  if (!activePassengerId.value) return
  const current = tempSelections[activePassengerId.value]
  const index = current.addons.findIndex(a => a.id === addon.id)
  if (index === -1) {
    current.addons.push(addon)
    current.addon_details.push(addon.name)
  } else {
    current.addons.splice(index, 1)
    const detailIndex = current.addon_details.indexOf(addon.name)
    if (detailIndex !== -1) current.addon_details.splice(detailIndex, 1)
  }
}

const confirmChanges = () => {
  // Logic updated to support future payment check if needed
  // For now, always close modals
  showSeatModal.value = false
  showAddonModal.value = false
  
  // Update the original booking data in selectedBookings to reflect changes in UI
  const passenger = selectedBookings.value.find(b => b.id === activePassengerId.value)
  if (passenger) {
     const selection = tempSelections[activePassengerId.value]
     passenger.seat_number = selection.seat?.seat_number || 'NOT ASSIGNED'
     passenger.addon_details = selection.addon_details
  }
}

const processPayment = async () => {
  isProcessingPayment.value = true
  setTimeout(() => {
    isProcessingPayment.value = false
    showPaymentModal.value = false
    updateDossier()
  }, 2000)
}

const copyEmailToAll = (id) => {
  const email = form.passengers[id].email
  Object.keys(form.passengers).forEach(pid => {
    form.passengers[pid].email = email
  })
}

const copyPhoneToAll = (id) => {
  const phone = form.passengers[id].phone
  const country = form.passengers[id].phone_country
  Object.keys(form.passengers).forEach(pid => {
    form.passengers[pid].phone = phone
    form.passengers[pid].phone_country = country
  })
}

const updateDossier = async () => {
  isLoading.value = true
  try {
    for (const passenger of selectedBookings.value) {
      const selection = tempSelections[passenger.id]
      await axios.patch(`/api/booking-details/${passenger.id}/`, {
        seat: selection.seat?.id,
        addons: selection.addons.map(a => a.id)
      })
    }
  } catch (err) {
    error.value = "Infrastructure Conflict: Failed to synchronize dossier changes."
  } finally {
    isLoading.value = false
  }
}

const processCheckin = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    // 1. Sync dossier changes first
    await updateDossier()
    
    // 2. Perform bulk check-in
    const payload = {
      passengers: selectedBookings.value.map(p => ({
        booking_detail_id: p.id,
        email: form.passengers[p.id].email,
        phone: form.passengers[p.id].phone
      })),
      has_declared_safety: true
    }
    
    const response = await axios.post('/api/checkins/self_checkin/', payload)
    checkinResults.value = response.data.results
    emailSentStatus.value = 'success' // Automatically sent by backend now
    currentStep.value = 5
  } catch (err) {
    error.value = err.response?.data?.error || "Protocol Failure: Could not finalize group check-in."
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

.poppins { font-family: 'Poppins', sans-serif; }

/* Override html5-qrcode default styles for CheckInView */
:deep(#checkin-qr-reader) {
  border: none !important;
  width: 100% !important;
  height: 100% !important;
}
:deep(#checkin-qr-reader video) {
  border-radius: 0 !important;
  object-fit: cover !important;
  width: 100% !important;
  height: 100% !important;
}
:deep(#checkin-qr-reader__scan_region) {
  min-height: auto !important;
}
:deep(#checkin-qr-reader__dashboard),
:deep(#checkin-qr-reader__dashboard_section_csr),
:deep(#checkin-qr-reader__dashboard_section_swaplink),
:deep(#checkin-qr-reader__header_message),
:deep(#checkin-qr-reader img[alt="Info icon"]),
:deep(#checkin-qr-reader__scan_region br) {
  display: none !important;
}

.animate-in {
  animation-duration: 0.5s;
  animation-fill-mode: both;
}

@keyframes zoom-in {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}
.zoom-in { animation-name: zoom-in; }

@keyframes slide-in-from-right {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}
.slide-in-from-right-4 { animation-name: slide-in-from-right; }

@keyframes scan-line {
  0% { top: 0%; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

.animate-scan-line {
  animation: scan-line 2s linear infinite;
}

@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.animate-spin-slow {
  animation: spin-slow 10s linear infinite;
}
</style>