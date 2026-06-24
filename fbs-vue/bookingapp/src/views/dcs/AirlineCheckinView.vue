<template>
  <div class="space-y-6 font-sans selection:bg-[#FF579A]/30">

    <!-- ============================================================ -->
    <!-- STEP 0: AIRLINE SELECTION                                      -->
    <!-- ============================================================ -->
    <div v-if="!selectedAirline" class="flex items-center justify-center pt-20">
      <div class="bg-white p-10 shadow-2xl rounded-sm border border-slate-200 w-full max-w-2xl animate-in zoom-in duration-500">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-2 h-2 rounded-full bg-[#FF579A] animate-pulse"></div>
          <span class="text-[10px] font-black text-[#FF579A] uppercase tracking-[0.2em]">DCS Operator Terminal</span>
        </div>
        <h2 class="text-3xl font-black text-slate-900 tracking-tighter uppercase italic mb-2">Select Operator Station</h2>
        <p class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-10">Choose the airline system you will operate for this check-in session.</p>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- PAL -->
          <button @click="selectAirline('Philippine Airlines')"
            class="group flex flex-col items-center justify-center p-8 border-2 border-slate-100 hover:border-blue-700 rounded-sm transition-all hover:bg-blue-50/50 hover:-translate-y-2 hover:shadow-xl hover:shadow-blue-700/10">
            <div class="w-16 h-16 bg-blue-900 text-white flex items-center justify-center font-black text-2xl rounded shadow-lg group-hover:scale-110 transition-transform mb-4">PR</div>
            <span class="text-xs font-black text-slate-700 uppercase tracking-tight group-hover:text-blue-900 text-center">Philippine Airlines</span>
            <span class="text-[9px] font-bold text-slate-400 uppercase mt-1">Flag Carrier · Blue</span>
          </button>
          <!-- CEB -->
          <button @click="selectAirline('Cebu Pacific')"
            class="group flex flex-col items-center justify-center p-8 border-2 border-slate-100 hover:border-orange-500 rounded-sm transition-all hover:bg-orange-50/50 hover:-translate-y-2 hover:shadow-xl hover:shadow-orange-500/10">
            <div class="w-16 h-16 bg-orange-500 text-white flex items-center justify-center font-black text-2xl rounded shadow-lg group-hover:scale-110 transition-transform mb-4">5J</div>
            <span class="text-xs font-black text-slate-700 uppercase tracking-tight group-hover:text-orange-900 text-center">Cebu Pacific</span>
            <span class="text-[9px] font-bold text-slate-400 uppercase mt-1">Low Cost · Orange</span>
          </button>
          <!-- Z2 -->
          <button @click="selectAirline('AirAsia Philippines')"
            class="group flex flex-col items-center justify-center p-8 border-2 border-slate-100 hover:border-red-600 rounded-sm transition-all hover:bg-red-50/50 hover:-translate-y-2 hover:shadow-xl hover:shadow-red-600/10">
            <div class="w-16 h-16 bg-red-600 text-white flex items-center justify-center font-black text-2xl rounded shadow-lg group-hover:scale-110 transition-transform mb-4">Z2</div>
            <span class="text-xs font-black text-slate-700 uppercase tracking-tight group-hover:text-red-900 text-center">AirAsia Philippines</span>
            <span class="text-[9px] font-bold text-slate-400 uppercase mt-1">Regional · Red</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MAIN CHECK-IN FLOW (Steps 1 – 6)                              -->
    <!-- ============================================================ -->
    <div v-else class="max-w-4xl mx-auto">

      <!-- Dashboard Style Header -->
      <div :class="['border-b p-6 sm:p-8 rounded-t-sm shadow-sm relative overflow-hidden mb-1', theme.headerBg, theme.headerBorder]">
        <div class="absolute -right-10 -top-10 w-40 h-40 bg-white/5 rounded-full blur-2xl"></div>
        <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div class="flex items-center gap-3 mb-2">
              <div :class="['w-8 h-8 text-white rounded-sm flex items-center justify-center font-black text-sm shadow-lg', theme.brandBg]">
                {{ selectedAirline === 'Philippine Airlines' ? 'PR' : selectedAirline === 'Cebu Pacific' ? '5J' : 'Z2' }}
              </div>
              <div :class="['w-2 h-2 rounded-full animate-pulse', theme.accentColor]"></div>
              <span :class="['text-[10px] font-black uppercase tracking-[0.2em]', theme.labelText]">{{ selectedAirline }} · Online Check-in Portal</span>
            </div>
            <h1 class="text-2xl sm:text-3xl font-black text-white tracking-tighter uppercase">ONLINE CHECK-IN</h1>
          </div>
          <div class="flex items-center gap-3">
            <div class="flex items-center gap-3 bg-white/10 border border-white/10 px-4 py-2 rounded-sm shadow-inner">
              <i class="ph ph-shield-check text-xl" :class="theme.labelText"></i>
              <div>
                <p class="text-[8px] font-black text-white/50 uppercase tracking-widest">Protocol Sync</p>
                <p class="text-[10px] font-black text-white uppercase">Step {{ displayStep }} of {{ steps.length }}</p>
              </div>
            </div>
            <button @click="selectedAirline = null; resetFlow()" class="text-[9px] font-black uppercase tracking-widest text-white/50 hover:text-white transition-all px-3 py-2 border border-white/10 hover:border-white/30 rounded-sm">
              Switch
            </button>
          </div>
        </div>
      </div>

      <!-- Compact Step Indicator -->
      <div class="bg-white border-b border-slate-100 p-4 rounded-b-sm shadow-sm flex items-center justify-between mb-2">
        <div class="flex items-center gap-2 overflow-x-auto no-scrollbar py-1">
          <div v-for="(step, idx) in steps" :key="idx" class="flex items-center gap-2">
            <div :class="[
              'w-5 h-5 rounded-sm flex items-center justify-center text-[9px] font-black transition-all shrink-0',
              displayStep > idx + 1 ? 'bg-emerald-500 text-white' :
              displayStep === idx + 1 ? [theme.stepActiveBg, 'text-white shadow-lg lg:scale-110'] :
              'bg-slate-100 text-slate-400 border border-slate-200'
            ]">
              <span v-if="displayStep > idx + 1">✓</span>
              <span v-else>{{ idx + 1 }}</span>
            </div>
            <span :class="['text-[9px] font-black uppercase tracking-widest whitespace-nowrap hidden sm:block', displayStep >= idx + 1 ? 'text-slate-900' : 'text-slate-400']">
              {{ step.label }}
            </span>
            <div v-if="idx < steps.length - 1" class="w-4 h-px bg-slate-200 mx-1 hidden sm:block"></div>
          </div>
        </div>
        <div :class="['hidden lg:block text-[9px] font-black uppercase tracking-widest px-3 py-1 rounded-full border', theme.badgeBg, theme.badgeBorder, theme.badgeText]">
          {{ selectedAirline }} OPS
        </div>
      </div>

      <!-- Content Area -->
      <div class="bg-white rounded-sm shadow-xl border border-slate-100 overflow-hidden relative">
        <div class="p-6 md:p-10">

          <!-- STEP 1: IDENTIFICATION -->
          <div v-if="currentStep === 1" class="space-y-8 animate-in fade-in duration-500">
            <div :class="['text-left border-l-4 pl-5', theme.stepBorder]">
              <h2 class="text-xl font-black text-slate-900 uppercase tracking-tight">Identification</h2>
              <p class="text-slate-400 text-[11px] font-bold uppercase tracking-widest mt-1">Enter your reservation data to begin</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-2">
                <label class="text-[9px] font-black uppercase tracking-widest text-slate-400 ml-1">Booking Reference (PNR)</label>
                <div class="relative">
                  <i class="ph ph-key absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"></i>
                  <input v-model="form.pnr" type="text" placeholder="ABC123"
                    :class="['w-full bg-slate-50 border border-slate-200 rounded-sm px-10 py-4 focus:outline-none transition-all uppercase font-black tracking-[0.2em] text-sm', theme.inputFocus]">
                </div>
              </div>
              <div class="space-y-2">
                <label class="text-[9px] font-black uppercase tracking-widest text-slate-400 ml-1">Passenger Last Name</label>
                <div class="relative">
                  <i class="ph ph-user absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"></i>
                  <input v-model="form.lastName" type="text" placeholder="e.g. DELA CRUZ"
                    :class="['w-full bg-slate-50 border border-slate-200 rounded-sm px-10 py-4 focus:outline-none transition-all font-black uppercase text-sm', theme.inputFocus]">
                </div>
              </div>
            </div>

            <div v-if="error" class="bg-rose-50 border-l-4 border-rose-500 p-4 text-rose-600 text-[10px] font-bold uppercase tracking-widest flex items-center gap-3">
              <i class="ph ph-warning-circle text-lg"></i> {{ error }}
            </div>

            <div class="flex flex-col sm:flex-row gap-3 pt-6">
              <button @click="lookupBooking" :disabled="isLoading || !form.pnr || !form.lastName"
                :class="['flex-1 disabled:opacity-30 text-white font-black py-5 rounded-sm transition-all shadow-xl flex items-center justify-center gap-3 uppercase tracking-[0.2em] text-[10px]', theme.brandBg, theme.brandHover]">
                <span v-if="isLoading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                <span v-else>Authorize &amp; Search</span>
                <i v-if="!isLoading" class="ph ph-magnifying-glass text-lg"></i>
              </button>
            </div>
          </div>

          <!-- STEP 1.5: PASSENGER SELECTION -->
          <div v-else-if="currentStep === 1.5" class="space-y-8 animate-in slide-in-from-right-4 duration-500">
            <div :class="['flex items-center justify-between border-l-4 pl-5', theme.stepBorder]">
              <div class="text-left">
                <h2 class="text-xl font-black text-slate-900 uppercase tracking-tight">Active Manifest</h2>
                <p class="text-slate-400 text-[11px] font-bold uppercase tracking-widest mt-1">Found {{ foundBookings.length }} records associated with PNR {{ form.pnr }}</p>
              </div>
              <button @click="toggleAll" :class="['text-[9px] font-black uppercase tracking-widest px-3 py-1.5 rounded-sm border transition-all', theme.badgeBg, theme.badgeBorder, theme.badgeText, 'hover:opacity-80']">
                {{ selectedBookings.length === foundBookings.filter(b => !b.is_checked_in).length ? 'Deselect All' : 'Select All Party' }}
              </button>
            </div>

            <div class="space-y-2">
              <div v-for="booking in foundBookings" :key="booking.id" @click="selectBooking(booking)"
                :class="[
                  'p-6 border-2 rounded-sm cursor-pointer transition-all flex items-center justify-between group',
                  selectedBookings.find(b => b.id === booking.id) ? [theme.selectedBorder, theme.selectedBg] : 'border-slate-50 bg-slate-50/50 hover:border-slate-200'
                ]">
                <div class="flex items-center gap-5 text-left">
                  <div class="flex items-center gap-4">
                    <div :class="['w-5 h-5 border-2 rounded-sm flex items-center justify-center transition-all', selectedBookings.find(b => b.id === booking.id) ? [theme.brandBg, theme.selectedBorder] : 'border-slate-300 bg-white']">
                      <i v-if="selectedBookings.find(b => b.id === booking.id)" class="ph ph-check text-white text-[10px] font-black"></i>
                    </div>
                    <div class="w-12 h-12 bg-white rounded-sm border border-slate-100 flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                      <i :class="['ph ph-identification-badge text-2xl', theme.accentColor]"></i>
                    </div>
                  </div>
                  <div>
                    <div class="font-black text-sm uppercase text-slate-900 tracking-tight">{{ booking.passenger_name }}</div>
                    <div class="text-[9px] text-slate-400 font-black uppercase tracking-widest mt-1">
                      {{ booking.flight_number }} · {{ booking.origin }} → {{ booking.destination }}
                    </div>
                  </div>
                </div>
                <div v-if="booking.is_checked_in" class="bg-emerald-100 text-emerald-600 text-[9px] font-black uppercase px-3 py-1.5 rounded-full border border-emerald-200 shadow-sm">
                  AUTHORIZED
                </div>
              </div>
            </div>

            <div class="flex gap-3">
              <button @click="currentStep = 1" class="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-400 font-black py-5 rounded-sm transition-all uppercase tracking-widest text-[10px]">Back</button>
              <button @click="currentStep = 2" :disabled="selectedBookings.length === 0"
                :class="['flex-[2] disabled:opacity-30 text-white font-black py-5 rounded-sm transition-all shadow-xl uppercase tracking-[0.2em] text-[10px]', theme.brandBg, theme.brandHover]">
                Continue Verification ({{ selectedBookings.length }})
              </button>
            </div>
          </div>

          <!-- STEP 2: SAFETY DECLARATION -->
          <div v-else-if="currentStep === 2" class="space-y-8 animate-in slide-in-from-right-4 duration-500">
            <div class="text-left border-l-4 border-rose-500 pl-5">
              <h2 class="text-xl font-black text-slate-900 uppercase tracking-tight">Safety Declaration</h2>
              <p class="text-slate-400 text-[11px] font-bold uppercase tracking-widest mt-1">Review prohibited items protocol for {{ selectedBookings.length }} passengers</p>
            </div>

            <div class="bg-slate-50 border border-slate-100 rounded-sm p-8 space-y-8">
              <div class="grid grid-cols-4 gap-4 text-center">
                <div v-for="(icon, idx) in ['🔥', '🔋', '🧪', '🔫']" :key="idx"
                  class="bg-white aspect-square rounded-sm flex items-center justify-center text-3xl border border-slate-100 shadow-sm grayscale hover:grayscale-0 transition-all cursor-default">
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
                <input v-model="form.hasDeclaredSafety" type="checkbox"
                  class="mt-1 w-6 h-6 rounded-sm border-slate-300 text-[#FF579A] focus:ring-0 cursor-pointer">
                <span class="text-[11px] font-black text-slate-500 group-hover:text-slate-900 transition-colors uppercase leading-relaxed tracking-tight">
                  I acknowledge that I have read the policy and confirm that baggage for all passengers contains no prohibited items.
                </span>
              </label>
            </div>

            <div class="flex gap-3">
              <button @click="currentStep = 1.5" class="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-400 font-black py-5 rounded-sm transition-all uppercase tracking-widest text-[10px]">Back</button>
              <button @click="currentStep = 3" :disabled="!form.hasDeclaredSafety"
                :class="['flex-[2] disabled:opacity-30 text-white font-black py-5 rounded-sm transition-all shadow-xl uppercase tracking-[0.2em] text-[10px]', theme.brandBg, theme.brandHover]">
                Clear Security Protocol
              </button>
            </div>
          </div>

          <!-- STEP 3: DOSSIER AUDIT (Journey Summary) -->
          <div v-else-if="currentStep === 3" class="space-y-8 animate-in slide-in-from-right-4 duration-500">
            <div class="text-left border-l-4 border-emerald-500 pl-5">
              <h2 class="text-xl font-black text-slate-900 uppercase tracking-tight">Dossier Audit</h2>
              <p class="text-slate-400 text-[11px] font-bold uppercase tracking-widest mt-1">Review operational journey data for {{ selectedBookings.length }} passengers</p>
            </div>

            <div class="space-y-6">
              <div v-for="booking in selectedBookings" :key="booking.id" class="bg-slate-50 border border-slate-100 rounded-sm overflow-hidden p-6 space-y-6">
                <div class="flex items-center justify-between border-b border-slate-200 pb-4">
                  <div class="flex items-center gap-3">
                    <div :class="['w-8 h-8 text-white rounded-sm flex items-center justify-center font-black text-xs', theme.brandBg]">
                      {{ booking.passenger_name.charAt(0) }}
                    </div>
                    <div class="text-left">
                      <span class="block text-[9px] font-black text-slate-400 uppercase tracking-widest">Passenger Manifest Link</span>
                      <span class="block text-sm font-black text-slate-900 uppercase tracking-tight">{{ booking.passenger_name }}</span>
                    </div>
                  </div>
                  <div class="text-right">
                    <span class="block text-[9px] font-black text-slate-400 uppercase tracking-widest">Flight ID</span>
                    <span :class="['block text-xs font-black uppercase tracking-widest', theme.accentColor]">{{ booking.flight_number }}</span>
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button @click="activePassengerId = booking.id; openSeatSelection()"
                    :class="['flex items-center justify-between p-4 bg-white border border-slate-200 rounded-sm transition-all group', theme.hoverBorder]">
                    <div class="flex items-center gap-4">
                      <div :class="['w-10 h-10 bg-slate-50 rounded-sm flex items-center justify-center border border-slate-100 shadow-sm', theme.accentColor]">
                        <i class="ph ph-chair text-xl"></i>
                      </div>
                      <div class="text-left">
                        <span class="block text-[9px] font-black text-slate-400 uppercase tracking-widest">Seat Slot</span>
                        <span class="block text-xs font-black text-slate-900 uppercase tracking-tighter">
                          {{ tempSelections[booking.id]?.seat?.seat_number || 'NOT ASSIGNED' }}
                        </span>
                      </div>
                    </div>
                    <i :class="['ph ph-arrow-right text-slate-300 transition-all', theme.groupHoverAccent]"></i>
                  </button>

                  <button @click="activePassengerId = booking.id; openAddonSelection()"
                    :class="['flex items-center justify-between p-4 bg-white border border-slate-200 rounded-sm transition-all group', theme.hoverBorder]">
                    <div class="flex items-center gap-4">
                      <div :class="['w-10 h-10 bg-slate-50 rounded-sm flex items-center justify-center border border-slate-100 shadow-sm', theme.accentColor]">
                        <i class="ph ph-package text-xl"></i>
                      </div>
                      <div class="text-left">
                        <span class="block text-[9px] font-black text-slate-400 uppercase tracking-widest">Baggage &amp; Meals</span>
                        <div class="mt-1 flex flex-wrap gap-1">
                          <span v-if="!tempSelections[booking.id]?.addon_details?.length" class="text-[10px] font-bold text-slate-400 uppercase italic">No items secured</span>
                          <span v-for="(addon, idx) in tempSelections[booking.id]?.addon_details" :key="idx"
                            :class="['text-[10px] font-black px-2 py-0.5 rounded-full border uppercase', theme.addonBg, theme.addonText, theme.addonBorder]">
                            {{ addon }}
                          </span>
                        </div>
                      </div>
                    </div>
                    <i :class="['ph ph-plus-circle text-slate-300 transition-all text-xl', theme.groupHoverAccent]"></i>
                  </button>
                </div>
              </div>
            </div>

            <div class="flex gap-3">
              <button @click="currentStep = 2" class="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-400 font-black py-5 rounded-sm transition-all uppercase tracking-widest text-[10px]">Back</button>
              <button @click="currentStep = 4"
                :class="['flex-[2] text-white font-black py-5 rounded-sm transition-all shadow-xl uppercase tracking-[0.2em] text-[10px]', theme.brandBg, theme.brandHover]">
                Proceed to Contact Link
              </button>
            </div>
          </div>

          <!-- STEP 4: CONTACT INTEGRATION -->
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
                      <input v-model="form.passengers[booking.id].email" type="email" placeholder="AGENT@TURSIM.COM"
                        class="w-full bg-white border border-slate-200 rounded-sm px-5 py-4 focus:ring-1 focus:ring-blue-500 transition-all font-black uppercase text-sm">
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
                        <input v-model="form.passengers[booking.id].phone" type="tel" placeholder="09278874355"
                          class="w-full bg-white border border-slate-200 rounded-sm px-5 py-4 focus:ring-1 focus:ring-blue-500 transition-all font-black text-sm">
                      </div>
                    </div>
                  </div>
                </div>

                <div class="grid grid-cols-1 gap-4 pt-4">
                  <div class="space-y-2 text-left">
                    <label class="text-[9px] font-black uppercase tracking-widest text-slate-400 ml-1">Loyalty / Frequent Flyer (Opt)</label>
                    <select v-model="form.passengers[booking.id].loyalty_program" :class="['w-full bg-white border border-slate-200 rounded-sm px-5 py-4 font-black uppercase text-sm outline-none border-l-4 border-l-slate-200 transition-all', theme.loyaltyFocus]">
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
              <button @click="processCheckin" :disabled="isLoading"
                :class="['flex-[2] disabled:opacity-30 text-white font-black py-5 rounded-sm transition-all shadow-xl uppercase tracking-[0.2em] text-[10px]', theme.brandBg, theme.brandHover]">
                <span v-if="isLoading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></span>
                Finalize Group Authorization
              </button>
            </div>
          </div>

          <!-- STEP 5: BOARDING PASS ISSUANCE -->
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
                <div :class="['p-6 text-white relative', theme.brandBg]">
                  <div class="absolute -right-6 -top-6 w-24 h-24 bg-white/5 rounded-full blur-2xl"></div>
                  <div class="flex justify-between items-start text-left">
                    <div>
                      <p class="text-[8px] font-black text-white/50 uppercase tracking-widest mb-1.5">Operation Module</p>
                      <p class="text-lg font-black uppercase tracking-tight">{{ result.flight_number }}</p>
                      <p class="text-[9px] font-black text-white/70 mt-1">{{ result.passenger_name }}</p>
                    </div>
                    <div class="text-right">
                      <p class="text-[8px] font-black text-white/50 uppercase tracking-widest mb-1.5">Assigned Slot</p>
                      <p class="text-2xl font-black text-white leading-none">{{ result.seat_number || 'TBA' }}</p>
                    </div>
                  </div>
                </div>
                <div class="p-6 space-y-6">
                  <div class="bg-slate-50 border border-slate-100 p-4 rounded-sm flex flex-col items-center">
                    <div class="bg-white p-2 rounded-sm border border-slate-200 shadow-sm mb-3">
                      <img :src="`https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=${result.boarding_pass}`" alt="QR Pass" class="w-24 h-24">
                    </div>
                    <p class="text-[8px] font-black text-slate-400 uppercase tracking-[0.3em]">{{ result.boarding_pass }}</p>
                  </div>
                  <button @click="downloadIndividualPass(result.booking_detail)" class="w-full bg-slate-900 hover:bg-black text-white py-3 rounded-sm text-[9px] font-black uppercase tracking-widest transition-all">Download PDF</button>
                </div>
              </div>
            </div>

            <button @click="currentStep = 6"
              :class="['w-full max-w-sm text-white font-black py-5 rounded-sm transition-all shadow-xl uppercase tracking-[0.2em] text-[10px]', theme.brandBg, theme.brandHover]">
              Complete Group Protocol
            </button>

            <div class="max-w-md mx-auto space-y-4">
              <button @click="dispatchEmail" :disabled="isSendingEmail || emailSentStatus === 'success'"
                :class="[
                  'w-full py-5 rounded-sm font-black uppercase tracking-widest text-[10px] transition-all flex items-center justify-center gap-3',
                  emailSentStatus === 'success' ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-100' : 'bg-white border border-slate-200 text-slate-900 hover:bg-slate-50 shadow-sm'
                ]">
                <template v-if="isSendingEmail">
                  <span class="w-4 h-4 border-2 border-slate-300 border-t-slate-900 rounded-full animate-spin"></span>
                  Encrypting &amp; Dispatching...
                </template>
                <template v-else-if="emailSentStatus === 'success'">
                  <i class="ph ph-check-circle text-lg"></i>
                  Credentials Transmitted
                </template>
                <template v-else>
                  <i class="ph ph-mask-happy text-lg text-blue-500"></i>
                  Dispatch All via Secure Email
                </template>
              </button>
              <p v-if="emailSentStatus === 'success'" class="text-[9px] font-bold text-emerald-500 uppercase tracking-widest animate-pulse">Encryption sequence complete. Check your secure inbox.</p>
            </div>
          </div>

          <!-- STEP 6: SYSTEM CLEAR / DONE -->
          <div v-else-if="currentStep === 6" class="py-12 text-center animate-in zoom-in duration-500">
            <div class="w-24 h-24 bg-emerald-50 rounded-full flex items-center justify-center mx-auto mb-8 border border-emerald-100 shadow-inner">
              <i class="ph ph-shield-check text-5xl text-emerald-500"></i>
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
              <div class="flex flex-col sm:flex-row gap-3">
                <button @click="resetFlow(); selectedAirline = null"
                  class="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-black py-5 rounded-sm transition-all uppercase tracking-widest text-[11px]">
                  New Session
                </button>
                <button @click="$router.push('/dcs/dashboard')"
                  :class="['flex-[2] text-white font-black py-5 rounded-sm transition-all shadow-xl uppercase tracking-[0.2em] text-[11px]', theme.brandBg, theme.brandHover]">
                  Return to Terminal
                </button>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- MODALS                                                         -->
    <!-- ============================================================ -->
    <Teleport to="body">
      <!-- Seat Selection Modal -->
      <div v-if="showSeatModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
        <div class="absolute inset-0 bg-slate-900/80 backdrop-blur-md" @click="showSeatModal = false"></div>
        <div class="relative bg-white w-full max-w-4xl h-[90vh] flex flex-col rounded-sm overflow-hidden animate-in zoom-in shadow-2xl">
          <div class="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50">
            <div>
              <h2 class="text-lg font-black text-slate-900 uppercase tracking-widest">Select Your Slot</h2>
              <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Flight {{ selectedBooking?.flight_number }} · {{ seatMapData?.aircraft_model || 'Standard Configuration' }}</p>
            </div>
            <button @click="showSeatModal = false" class="w-10 h-10 flex items-center justify-center rounded-sm bg-white border border-slate-200 text-slate-400 hover:text-pink-500 transition-colors">
              <i class="ph ph-x text-xl"></i>
            </button>
          </div>

          <div class="flex-1 overflow-y-auto bg-slate-200/50 p-8 no-scrollbar">
            <div class="max-w-md mx-auto bg-white rounded-t-[100px] border-x border-t border-slate-200 p-10 pb-20 shadow-inner">
              <div class="w-full h-24 mb-10 flex flex-col items-center justify-center border-b border-slate-100">
                <div class="w-16 h-1 bg-slate-200 rounded-full mb-2"></div>
                <span class="text-[10px] font-black text-slate-300 tracking-[0.3em] uppercase">Flight Deck</span>
              </div>

              <div class="flex items-center justify-center gap-6 mb-12">
                <div class="flex items-center gap-2">
                  <div :class="['w-3 h-3 rounded-sm', theme.brandBg]"></div>
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

              <div v-if="seatMapData" class="space-y-4">
                <div v-for="rowNum in Math.max(...seatMapData.seats.map(s => s.row))" :key="rowNum" class="flex items-center justify-center gap-4">
                  <div class="flex gap-2">
                    <template v-for="col in ['A', 'B', 'C']" :key="col">
                      <div v-if="seatMapData.seats.find(s => s.row === rowNum && s.column === col)"
                        @click="seatMapData.seats.find(s => s.row === rowNum && s.column === col).is_available && (tempSelections[activePassengerId].seat = seatMapData.seats.find(s => s.row === rowNum && s.column === col))"
                        :class="[
                          'w-10 h-10 rounded-sm flex items-center justify-center text-[10px] font-black transition-all border outline-none',
                          !seatMapData.seats.find(s => s.row === rowNum && s.column === col).is_available ? 'bg-slate-800 border-slate-800 text-slate-500 cursor-not-allowed' :
                          tempSelections[activePassengerId]?.seat?.id === seatMapData.seats.find(s => s.row === rowNum && s.column === col).id ? [theme.brandBg, theme.selectedBorder, 'text-white shadow-lg'] :
                          'bg-white border-slate-200 text-slate-900 hover:border-pink-300 cursor-pointer active:scale-95'
                        ]">
                        {{ col }}
                      </div>
                    </template>
                  </div>
                  <div class="w-8 flex items-center justify-center">
                    <span class="text-[11px] font-black text-slate-300">{{ rowNum }}</span>
                  </div>
                  <div class="flex gap-2">
                    <template v-for="col in ['D', 'E', 'F']" :key="col">
                      <div v-if="seatMapData.seats.find(s => s.row === rowNum && s.column === col)"
                        @click="seatMapData.seats.find(s => s.row === rowNum && s.column === col).is_available && (tempSelections[activePassengerId].seat = seatMapData.seats.find(s => s.row === rowNum && s.column === col))"
                        :class="[
                          'w-10 h-10 rounded-sm flex items-center justify-center text-[10px] font-black transition-all border outline-none',
                          !seatMapData.seats.find(s => s.row === rowNum && s.column === col).is_available ? 'bg-slate-800 border-slate-800 text-slate-500 cursor-not-allowed' :
                          tempSelections[activePassengerId]?.seat?.id === seatMapData.seats.find(s => s.row === rowNum && s.column === col).id ? [theme.brandBg, theme.selectedBorder, 'text-white shadow-lg'] :
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

          <div class="p-6 border-t border-slate-100 flex items-center justify-between bg-white">
            <div class="text-left">
              <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest block">Selected Slot</span>
              <span class="text-xl font-black text-slate-900">{{ tempSelections[activePassengerId]?.seat?.seat_code || '---' }}</span>
            </div>
            <button @click="confirmChanges"
              :class="['text-white font-black px-10 py-4 rounded-sm transition-all shadow-xl uppercase tracking-widest text-[11px]', theme.brandBg, theme.brandHover]">
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
            <div>
              <h3 class="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] mb-4">Galley Services / Meals</h3>
              <div class="grid grid-cols-1 gap-3">
                <div v-for="meal in availableAddons.meals" :key="meal.id" @click="toggleAddon(meal)"
                  :class="['p-4 border transition-all flex items-center justify-between cursor-pointer rounded-sm',
                    tempSelections[activePassengerId]?.addons.some(a => a.id === meal.id) ? [theme.selectedBorder, theme.addonBg] : 'border-slate-100 hover:border-pink-200']">
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
            <div>
              <h3 class="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] mb-4">Logistics / Extra Baggage</h3>
              <div class="grid grid-cols-1 gap-3">
                <div v-for="bag in availableAddons.baggage" :key="bag.id" @click="toggleAddon(bag)"
                  :class="['p-4 border transition-all flex items-center justify-between cursor-pointer rounded-sm',
                    tempSelections[activePassengerId]?.addons.some(a => a.id === bag.id) ? [theme.selectedBorder, theme.addonBg] : 'border-slate-100 hover:border-pink-200']">
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
              <p class="text-lg text-slate-900">₱0</p>
            </div>
            <button @click="confirmChanges"
              :class="['text-white px-10 py-4 text-[11px] uppercase tracking-widest shadow-lg transition-all', theme.brandBg, theme.brandHover]">
              Review Dossier
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import axios from '@/services/api/axios'
import { seatService } from '@/services/booking/seatService'

// ── AIRLINE SELECTION ─────────────────────────────────────────────────────────
const selectedAirline = ref(null)

const selectAirline = (airline) => {
  selectedAirline.value = airline
  resetFlow()
}

// ── THEME ENGINE ──────────────────────────────────────────────────────────────
const theme = computed(() => {
  if (selectedAirline.value === 'Philippine Airlines') {
    return {
      headerBg: 'bg-[#002244]', headerBorder: 'border-blue-500/30',
      brandBg: 'bg-blue-900', brandHover: 'hover:bg-blue-950',
      stepBorder: 'border-blue-800',
      stepActiveBg: 'bg-blue-900',
      accentColor: 'text-blue-700',
      selectedBorder: 'border-blue-700', selectedBg: 'bg-blue-50/30',
      hoverBorder: 'hover:border-blue-700',
      groupHoverAccent: 'group-hover:text-blue-700',
      addonBg: 'bg-blue-50/50', addonText: 'text-blue-700', addonBorder: 'border-blue-200',
      badgeBg: 'bg-blue-50', badgeBorder: 'border-blue-200', badgeText: 'text-blue-800',
      inputFocus: 'focus:ring-1 focus:ring-blue-700 focus:border-blue-700',
      loyaltyFocus: 'focus:border-l-blue-700',
      labelText: 'text-blue-300',
    }
  } else if (selectedAirline.value === 'Cebu Pacific') {
    return {
      headerBg: 'bg-[#1E1B18]', headerBorder: 'border-orange-500/30',
      brandBg: 'bg-orange-500', brandHover: 'hover:bg-orange-600',
      stepBorder: 'border-orange-500',
      stepActiveBg: 'bg-orange-500',
      accentColor: 'text-orange-500',
      selectedBorder: 'border-orange-500', selectedBg: 'bg-orange-50/30',
      hoverBorder: 'hover:border-orange-500',
      groupHoverAccent: 'group-hover:text-orange-500',
      addonBg: 'bg-orange-50/50', addonText: 'text-orange-600', addonBorder: 'border-orange-200',
      badgeBg: 'bg-orange-50', badgeBorder: 'border-orange-200', badgeText: 'text-orange-700',
      inputFocus: 'focus:ring-1 focus:ring-orange-500 focus:border-orange-500',
      loyaltyFocus: 'focus:border-l-orange-500',
      labelText: 'text-orange-400',
    }
  } else if (selectedAirline.value === 'AirAsia Philippines') {
    return {
      headerBg: 'bg-[#1A1A1A]', headerBorder: 'border-red-600/30',
      brandBg: 'bg-red-600', brandHover: 'hover:bg-red-700',
      stepBorder: 'border-red-600',
      stepActiveBg: 'bg-red-600',
      accentColor: 'text-red-600',
      selectedBorder: 'border-red-600', selectedBg: 'bg-red-50/30',
      hoverBorder: 'hover:border-red-600',
      groupHoverAccent: 'group-hover:text-red-600',
      addonBg: 'bg-red-50/50', addonText: 'text-red-600', addonBorder: 'border-red-200',
      badgeBg: 'bg-red-50', badgeBorder: 'border-red-200', badgeText: 'text-red-700',
      inputFocus: 'focus:ring-1 focus:ring-red-600 focus:border-red-600',
      loyaltyFocus: 'focus:border-l-red-600',
      labelText: 'text-red-400',
    }
  }
  return {
    headerBg: 'bg-slate-900', headerBorder: 'border-slate-700',
    brandBg: 'bg-slate-900', brandHover: 'hover:bg-black',
    stepBorder: 'border-[#FF579A]',
    stepActiveBg: 'bg-[#FF579A]',
    accentColor: 'text-[#FF579A]',
    selectedBorder: 'border-[#FF579A]', selectedBg: 'bg-pink-50/30',
    hoverBorder: 'hover:border-[#FF579A]',
    groupHoverAccent: 'group-hover:text-[#FF579A]',
    addonBg: 'bg-pink-50/50', addonText: 'text-[#FF579A]', addonBorder: 'border-pink-200',
    badgeBg: 'bg-pink-50', badgeBorder: 'border-pink-100', badgeText: 'text-[#FF579A]',
    inputFocus: 'focus:ring-1 focus:ring-[#FF579A] focus:border-[#FF579A]',
    loyaltyFocus: 'focus:border-l-pink-500',
    labelText: 'text-[#FF579A]',
  }
})

// ── STEPS ─────────────────────────────────────────────────────────────────────
const steps = [
  { label: 'Details' },
  { label: 'Safety' },
  { label: 'Audit' },
  { label: 'Link' },
  { label: 'Pass' },
  { label: 'Clear' }
]

// Map fractional steps to display step integers
const displayStep = computed(() => Math.ceil(currentStep.value))

// ── STATE ─────────────────────────────────────────────────────────────────────
const currentStep = ref(1)
const isLoading = ref(false)
const error = ref(null)
const isSendingEmail = ref(false)
const emailSentStatus = ref(null)

const form = reactive({
  pnr: '',
  lastName: '',
  hasDeclaredSafety: false,
  passengers: {}
})

const foundBookings = ref([])
const selectedBookings = ref([])
const checkinResults = ref([])

const showSeatModal = ref(false)
const showAddonModal = ref(false)

const activePassengerId = ref(null)
const seatMapData = ref(null)
const availableAddons = ref({ meals: [], baggage: [], assistance: [] })
const tempSelections = reactive({})
const isProcessingPayment = ref(false)

// ── COMPUTED ──────────────────────────────────────────────────────────────────
const selectedBooking = computed(() =>
  selectedBookings.value.find(b => b.id === activePassengerId.value)
)

// ── LOOKUP ────────────────────────────────────────────────────────────────────
const lookupBooking = async () => {
  isLoading.value = true
  error.value = null
  try {
    const response = await axios.post('/api/checkins/lookup/', {
      pnr: form.pnr,
      last_name: form.lastName
    })
    foundBookings.value = response.data
    currentStep.value = 1.5
  } catch (err) {
    error.value = err.response?.data?.error || 'Authorization failed. Records inaccessible.'
  } finally {
    isLoading.value = false
  }
}

// ── SELECTION ─────────────────────────────────────────────────────────────────
const selectBooking = (booking) => {
  if (booking.is_checked_in) return
  const index = selectedBookings.value.findIndex(b => b.id === booking.id)
  if (index === -1) {
    selectedBookings.value.push(booking)
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
  if (selectedBookings.value.length === foundBookings.value.filter(b => !b.is_checked_in).length) {
    selectedBookings.value = []
  } else {
    foundBookings.value.forEach(b => {
      if (!b.is_checked_in && !selectedBookings.value.find(s => s.id === b.id)) {
        selectBooking(b)
      }
    })
  }
}

// ── SEAT MAP ──────────────────────────────────────────────────────────────────
const openSeatSelection = async () => {
  if (!activePassengerId.value) return
  const passenger = selectedBookings.value.find(b => b.id === activePassengerId.value)
  if (!passenger) return
  isLoading.value = true
  try {
    const data = await seatService.getSeatsBySchedule(passenger.schedule)
    seatMapData.value = data
    const currentSeatId = tempSelections[passenger.id].seat?.id || passenger.seat
    tempSelections[passenger.id].seat = data.seats.find(s => s.id === currentSeatId)
    showSeatModal.value = true
  } catch (err) {
    error.value = 'Terminal error: Could not synchronize seat map.'
  } finally {
    isLoading.value = false
  }
}

// ── ADD-ONS ───────────────────────────────────────────────────────────────────
const openAddonSelection = async () => {
  if (!activePassengerId.value) return
  isLoading.value = true
  try {
    const response = await axios.get('/api/add-ons/')
    availableAddons.value.meals = response.data.filter(a => a.addon_type_name === 'Meal')
    availableAddons.value.baggage = response.data.filter(a => a.addon_type_name === 'Baggage')
    availableAddons.value.assistance = response.data.filter(a => a.addon_type_name === 'Assistance')
    showAddonModal.value = true
  } catch (err) {
    error.value = 'Terminal error: Could not retrieve auxiliary catalog.'
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
    const di = current.addon_details.indexOf(addon.name)
    if (di !== -1) current.addon_details.splice(di, 1)
  }
}

const confirmChanges = () => {
  showSeatModal.value = false
  showAddonModal.value = false
  const passenger = selectedBookings.value.find(b => b.id === activePassengerId.value)
  if (passenger) {
    const selection = tempSelections[activePassengerId.value]
    passenger.seat_number = selection.seat?.seat_number || 'NOT ASSIGNED'
    passenger.addon_details = selection.addon_details
  }
}

// ── COPY UTILITIES ────────────────────────────────────────────────────────────
const copyEmailToAll = (id) => {
  const email = form.passengers[id].email
  Object.keys(form.passengers).forEach(pid => { form.passengers[pid].email = email })
}

const copyPhoneToAll = (id) => {
  const phone = form.passengers[id].phone
  const country = form.passengers[id].phone_country
  Object.keys(form.passengers).forEach(pid => {
    form.passengers[pid].phone = phone
    form.passengers[pid].phone_country = country
  })
}

// ── DOSSIER UPDATE ────────────────────────────────────────────────────────────
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
    error.value = 'Infrastructure Conflict: Failed to synchronize dossier changes.'
  } finally {
    isLoading.value = false
  }
}

// ── CHECKIN ───────────────────────────────────────────────────────────────────
const processCheckin = async () => {
  isLoading.value = true
  error.value = null
  try {
    await updateDossier()
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
    currentStep.value = 5
  } catch (err) {
    error.value = err.response?.data?.error || 'Protocol Failure: Could not finalize group check-in.'
  } finally {
    isLoading.value = false
  }
}

// ── EMAIL DISPATCH ────────────────────────────────────────────────────────────
const dispatchEmail = async () => {
  if (checkinResults.value.length === 0) return
  isSendingEmail.value = true
  emailSentStatus.value = null
  try {
    const bookingDetailIds = checkinResults.value.map(r => r.booking_detail.id || r.booking_detail)
    await axios.post('/api/checkins/dispatch_email/', { booking_detail_ids: bookingDetailIds })
    emailSentStatus.value = 'success'
    setTimeout(() => { emailSentStatus.value = null }, 5000)
  } catch (err) {
    emailSentStatus.value = 'error'
    error.value = 'Dispatch Protocol Failure: Could not transmit digital credentials.'
  } finally {
    isSendingEmail.value = false
  }
}

// ── DOWNLOAD ──────────────────────────────────────────────────────────────────
const downloadIndividualPass = (bookingId) => {
  window.open(`${axios.defaults.baseURL}api/dcs/boarding-pass/${bookingId}/`, '_blank')
}

// ── RESET ─────────────────────────────────────────────────────────────────────
const resetFlow = () => {
  currentStep.value = 1
  form.pnr = ''
  form.lastName = ''
  form.hasDeclaredSafety = false
  form.passengers = {}
  foundBookings.value = []
  selectedBookings.value = []
  checkinResults.value = []
  emailSentStatus.value = null
  error.value = null
  Object.keys(tempSelections).forEach(k => delete tempSelections[k])
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

.animate-in { animation-duration: 0.5s; animation-fill-mode: both; }

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

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
.fade-in { animation-name: fade-in; }
</style>
