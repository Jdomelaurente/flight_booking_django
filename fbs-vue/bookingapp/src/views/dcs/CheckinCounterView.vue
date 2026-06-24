<template>
  <div class="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
    <!-- Header / Nav -->
    <div class="flex items-center justify-between">
      <button
        @click="goBack"
        class="group flex items-center gap-3 text-sm font-black text-slate-400 hover:text-pink-600 transition-all uppercase tracking-widest"
      >
        <div class="w-8 h-8 rounded-full bg-white border border-slate-200 flex items-center justify-center group-hover:bg-pink-50 group-hover:border-pink-200 transition-all">
          <svg class="w-4 h-4 transition-transform group-hover:-translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M15 19l-7-7 7-7"/>
          </svg>
        </div>
        Flight Manifest
      </button>

      <div class="flex items-center gap-4">
        <div class="text-right">
          <h2 class="text-xs font-black text-slate-400 uppercase tracking-widest leading-none">Security Handling</h2>
          <p class="text-[10px] font-bold text-pink-500 mt-1 uppercase">Counter Alpha-01 · {{ schedule?.flight_number }}</p>
        </div>
        <div class="w-10 h-10 bg-pink-600 rounded-[5px] flex items-center justify-center text-white shadow-lg shadow-pink-100">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
      </div>
    </div>

    <!-- MODERN WIZARD STEPS -->
    <div v-if="!checkinSuccess" class="relative px-8">
      <div class="absolute top-1/2 left-0 w-full h-0.5 bg-slate-100 -translate-y-1/2 lg:block hidden"></div>
      <div class="relative flex justify-between items-center bg-white/50 backdrop-blur-sm lg:p-0 p-4 rounded-[5px]">
        <div v-for="(step, index) in steps" :key="index" class="relative flex flex-col items-center gap-3 z-10 lg:w-48">
          <div 
            :class="[
              'w-10 h-10 rounded-[2px] flex items-center justify-center font-black text-sm transition-all duration-500 border-2',
              currentStep > index ? 'bg-pink-600 border-pink-600 text-white' : 
              currentStep === index ? 'bg-white border-pink-600 text-pink-600 shadow-xl shadow-pink-100 scale-110' :
              'bg-white border-slate-200 text-slate-300'
            ]"
          >
            <svg v-if="currentStep > index" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
            </svg>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <span 
            :class="[
              'text-[10px] font-black uppercase tracking-widest text-center transition-colors lg:block hidden',
              currentStep >= index ? 'text-slate-900' : 'text-slate-300'
            ]"
          >
            {{ step.shortLabel }}
          </span>
        </div>
      </div>
    </div>

    <!-- MAIN CONTENT AREA -->
    <div v-if="checkinSuccess" class="bg-white rounded-[5px] border border-slate-200 shadow-2xl shadow-emerald-100/50 overflow-hidden flex flex-col items-center justify-center py-20 px-8 text-center animate-in zoom-in duration-700">
        <div class="relative mb-10">
           <div class="absolute inset-0 bg-emerald-500/20 blur-3xl rounded-full animate-pulse"></div>
           <div class="relative w-32 h-32 bg-emerald-600 rounded-[5px] flex items-center justify-center text-white shadow-2xl shadow-emerald-200">
              <svg class="w-16 h-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
           </div>
        </div>

        <div class="space-y-4 max-w-xl">
           <h3 class="text-4xl font-black text-slate-900 tracking-tighter">Mission Accomplished</h3>
           <p class="text-slate-500 font-bold leading-relaxed">The party of {{ selectedPassengers.length }} has been authorized and synchronized. Boarding passes have been dispatched to central repositories.</p>
        </div>

        <!-- Success Details Grid -->
        <div class="grid grid-cols-2 gap-4 w-full max-w-lg mt-12 mb-12">
           <div class="bg-slate-50 border border-slate-100 rounded-[5px] p-6 text-left">
              <div class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Load Status</div>
              <div class="text-2xl font-black text-slate-900">{{ numericWeight }} <span class="text-xs text-slate-400">KG</span></div>
              <div class="text-[9px] font-bold text-pink-500 mt-1 uppercase tracking-tighter">Weight Protocol: Clear</div>
           </div>
           <div class="bg-slate-50 border border-slate-100 rounded-[5px] p-6 text-left">
              <div class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Passes Issued</div>
              <div class="text-2xl font-black text-slate-900">{{ selectedPassengers.length }} <span class="text-xs text-slate-400">PAX</span></div>
              <div class="text-[9px] font-bold text-pink-500 mt-1 uppercase tracking-tighter">System ID Sync: OK</div>
           </div>
        </div>

        <div class="flex flex-col sm:flex-row gap-4 w-full max-w-md">
           <button 
             @click="downloadAllPasses"
             class="flex-1 bg-slate-900 text-white text-[11px] font-black uppercase tracking-widest px-8 py-5 rounded-[2px] hover:bg-black transition-all flex items-center justify-center gap-3 active:scale-95"
           >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              Bulk Output
           </button>
           <button 
             @click="goBack"
             class="flex-1 bg-white border border-slate-200 text-slate-500 text-[11px] font-black uppercase tracking-widest px-8 py-5 rounded-[2px] hover:bg-slate-50 transition-all active:scale-95"
           >
              Return to Terminal
           </button>
        </div>
    </div>

    <div v-else class="bg-white rounded-[5px] border border-slate-200 shadow-2xl shadow-pink-100/50 overflow-hidden min-h-[550px] flex flex-col">
      <!-- Loading State -->
      <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center p-20 animate-pulse">
         <div class="w-16 h-16 border-4 border-pink-100 border-t-pink-600 rounded-full animate-spin"></div>
         <p class="mt-6 text-[11px] font-black text-slate-400 uppercase tracking-widest">Retrieving Secure Dossier...</p>
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="flex-1 flex flex-col items-center justify-center p-20 text-center">
         <div class="w-20 h-20 bg-rose-50 rounded-[5px] flex items-center justify-center text-3xl mb-6">⚠️</div>
         <h3 class="text-xl font-black text-slate-900 tracking-tight">Access Protocol Violation</h3>
         <p class="mt-2 text-slate-500 font-bold max-w-sm">{{ error }}</p>
         <button @click="goBack" class="mt-8 bg-slate-900 text-white text-[10px] font-black uppercase tracking-widest px-8 py-4 rounded-[2px] hover:bg-pink-600 transition-all">Abort Procedure</button>
      </div>

      <div v-else class="flex-1 flex flex-col transition-all">
        <!-- STEP CONTENT -->
        <div class="flex-1 p-8 lg:p-12 overflow-y-auto">
          
          <!-- STEP 0: PARTY VERIFICATION -->
          <div v-if="currentStep === 0" class="space-y-10 animate-in fade-in slide-in-from-right-4 duration-500">
            <div class="grid lg:grid-cols-2 gap-12">
              <div class="space-y-8">
                <div>
                   <span class="text-[10px] font-black text-pink-600 uppercase tracking-widest">Protocol 01</span>
                   <h3 class="text-3xl font-black text-slate-900 tracking-tighter mt-1">Party Verification</h3>
                   <p class="text-slate-500 font-bold mt-2">Identify team members present at the counter.</p>
                </div>

                <!-- Member Selection -->
                <div class="bg-slate-50 border border-slate-100 rounded-[5px] p-1 overflow-hidden">
                   <div class="bg-white/50 px-6 py-4 flex justify-between items-center border-b border-slate-100/50">
                      <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Manifest Link: {{ pnr }}</span>
                      <button @click="toggleSelectAll" class="text-pink-600 text-[10px] font-black uppercase tracking-widest hover:underline">
                        {{ allSelected ? 'Reject All' : 'Verify All' }}
                      </button>
                   </div>
                   <div class="divide-y divide-slate-100 max-h-[300px] overflow-y-auto">
                      <label 
                        v-for="p in passengers" 
                        :key="p.booking_detail_id" 
                        class="flex items-center gap-4 p-5 cursor-pointer hover:bg-white transition-all group"
                        :class="selectedIds.has(p.booking_detail_id) ? 'bg-white shadow-sm ring-1 ring-slate-200/50' : ''"
                      >
                         <input 
                           type="checkbox" 
                           :checked="selectedIds.has(p.booking_detail_id)" 
                           @change="togglePassenger(p.booking_detail_id)"
                           :disabled="p.status === 'checkin'"
                           class="w-5 h-5 rounded-[2px] border-2 border-slate-200 text-pink-600 focus:ring-pink-100 transition-all"
                         >
                         <div class="flex-1">
                            <div class="flex items-center gap-2">
                               <span class="font-black text-slate-900 group-hover:text-pink-600 transition-colors">{{ p.passenger_name }}</span>
                               <span v-if="p.status === 'checkin'" class="bg-emerald-100 text-emerald-700 text-[8px] px-1.5 py-0.5 rounded-full font-black uppercase tracking-widest">CLEAR</span>
                            </div>
                            <div class="text-[10px] text-slate-400 font-bold uppercase tracking-tighter mt-0.5">{{ p.passenger_type }} · {{ p.pnr }}</div>
                         </div>
                      </label>
                   </div>
                </div>
              </div>

              <!-- Visual Summary -->
              <div class="bg-pink-50/30 rounded-[5px] border-2 border-dashed border-pink-200 p-10 flex flex-col items-center justify-center text-center">
                 <div class="w-20 h-20 bg-white rounded-[2px] flex items-center justify-center text-pink-600 shadow-xl mb-6 scale-110">
                    <svg class="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                       <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                 </div>
                 <h4 class="text-2xl font-black text-slate-900 tracking-tight">{{ selectedIds.size }} Members Present</h4>
                 <p class="text-sm text-slate-500 font-bold mt-2 max-w-[200px]">Synchronizing party data with central manifest...</p>
                 <div class="mt-10 flex gap-2">
                    <div v-for="i in selectedIds.size" :key="i" class="w-2 h-8 bg-pink-600 rounded-full animate-bounce" :style="{ animationDelay: (i * 0.1) + 's' }"></div>
                 </div>
              </div>
            </div>
          </div>

          <!-- STEP 1: DOCUMENTATION -->
          <div v-if="currentStep === 1" class="space-y-10 animate-in fade-in slide-in-from-right-4 duration-500">
             <div class="grid lg:grid-cols-2 gap-12">
               <div class="space-y-8">
                  <div>
                    <span class="text-[10px] font-black text-pink-600 uppercase tracking-widest">Protocol 02</span>
                    <h3 class="text-3xl font-black text-slate-900 tracking-tighter mt-1">Dossier Review</h3>
                    <p class="text-slate-500 font-bold mt-2">Validate travel credentials for the authorized group.</p>
                  </div>

                  <div class="space-y-3">
                     <label v-for="(check, key) in documentationChecks" :key="key" class="flex items-start gap-4 cursor-pointer group p-5 rounded-[5px] border-2 border-slate-100 hover:border-pink-600 hover:bg-white transition-all shadow-sm">
                        <input type="checkbox" v-model="checks[key]" class="mt-1 w-6 h-6 rounded-[2px] border-2 border-slate-200 text-pink-600 focus:ring-pink-100">
                        <div>
                           <div class="text-[10px] font-black text-pink-600 uppercase tracking-widest">{{ check.label }}</div>
                           <div class="text-sm font-black text-slate-900 mt-1 group-hover:text-pink-600 transition-colors">{{ check.desc }}</div>
                        </div>
                     </label>
                  </div>
               </div>

               <div class="bg-slate-900 rounded-[2.5rem] p-10 text-white relative overflow-hidden group">
                  <div class="absolute inset-0 bg-gradient-to-br from-pink-500/20 to-transparent"></div>
                  <div class="relative z-10 space-y-6">
                     <div class="w-16 h-16 bg-white/10 rounded-2xl flex items-center justify-center backdrop-blur-md">
                        <svg class="w-8 h-8 text-pink-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                           <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                        </svg>
                     </div>
                     <h4 class="text-2xl font-black tracking-tight">System Identity Vault</h4>
                     <p class="text-pink-100 font-bold text-sm leading-relaxed opacity-80">Agent must physically inspect each passport. System cross-check will occur upon final issuance.</p>
                     
                     <div class="pt-10 border-t border-white/10">
                        <div class="flex justify-between items-center text-[10px] font-black text-pink-400 uppercase tracking-widest">
                           <span>Encrypted Sector</span>
                           <span>Verified</span>
                        </div>
                        <div class="mt-4 flex flex-wrap gap-2">
                           <span v-for="p in selectedPassengers" :key="p.id" class="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-[10px] font-black uppercase text-pink-100">
                              {{ p.passenger_name.split(' ')[0] }}
                           </span>
                        </div>
                     </div>
                  </div>
               </div>
             </div>
          </div>

          <!-- STEP 2: SECURITY & SSRS -->
          <div v-if="currentStep === 2" class="space-y-10 animate-in fade-in slide-in-from-right-4 duration-500">
             <div class="grid lg:grid-cols-2 gap-12">
                <div class="space-y-8">
                   <div>
                    <span class="text-[10px] font-black text-pink-600 uppercase tracking-widest">Protocol 03</span>
                    <h3 class="text-3xl font-black text-slate-900 tracking-tighter mt-1">Security Sync</h3>
                    <p class="text-slate-500 font-bold mt-2">Final individual clearance checks required.</p>
                  </div>

                  <div class="space-y-4">
                     <div v-for="p in selectedPassengers" :key="p.booking_detail_id" class="bg-white border-2 border-slate-100 rounded-[5px] p-6 flex items-center justify-between shadow-sm group hover:border-pink-600 transition-all">
                        <div class="flex items-center gap-4">
                           <div class="w-10 h-10 bg-slate-50 rounded-[2px] flex items-center justify-center text-slate-400 group-hover:text-pink-600 transition-all">
                              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                              </svg>
                           </div>
                           <div>
                              <div class="text-sm font-black text-slate-700 leading-none group-hover:text-pink-700 transition-colors">{{ p.passenger_name }}</div>
                              <div class="text-[9px] font-bold text-slate-400 uppercase tracking-widest mt-1.5">Sector Clearance Code: ALPHA-{{ p.booking_detail_id }}</div>
                           </div>
                        </div>
                        <button 
                           @click="toggleSecurity(p.booking_detail_id)"
                           :class="[
                             'px-4 py-2 rounded-[2px] text-[9px] font-black uppercase tracking-widest transition-all',
                             securityClearance[p.booking_detail_id] ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' : 'bg-rose-50 text-rose-600 border border-rose-100'
                           ]"
                        >
                           {{ securityClearance[p.booking_detail_id] ? 'Authorized' : 'Pending' }}
                        </button>
                     </div>
                  </div>
                </div>

                <div class="space-y-8">
                   <div class="bg-slate-900 rounded-[5px] p-10 text-white flex flex-col items-center justify-center text-center relative overflow-hidden h-full">
                      <div class="absolute inset-0 bg-gradient-to-t from-pink-500/10 to-transparent"></div>
                      <div class="relative w-40 h-40 mb-8">
                         <div class="absolute inset-0 border-2 border-white/10 rounded-full"></div>
                         <div class="absolute inset-0 border-2 border-pink-500 rounded-full border-t-transparent animate-spin-slow"></div>
                         <div class="absolute inset-4 bg-white/5 rounded-full backdrop-blur-sm flex flex-col items-center justify-center">
                            <span class="text-[10px] font-black text-pink-400 uppercase tracking-[0.2em] mb-3">Internal Scan</span>
                            <span class="text-4xl font-black text-white">{{ Object.values(securityClearance).filter(v => v).length }}/{{ selectedIds.size }}</span>
                         </div>
                      </div>
                      <h4 class="text-xl font-black tracking-tight">Master Clearance Node</h4>
                      <p class="text-xs text-slate-400 font-bold mt-2 max-w-[200px] leading-relaxed">All party members must be individually authorized for system-wide sync.</p>
                   </div>
                </div>
             </div>
          </div>

          <!-- STEP 3: LUGGAGE & POOLING -->
          <div v-if="currentStep === 3" class="space-y-10 animate-in fade-in slide-in-from-right-4 duration-500">
             <div class="grid lg:grid-cols-2 gap-12">
                <div class="space-y-8">
                   <div>
                    <span class="text-[10px] font-black text-pink-600 uppercase tracking-widest">Protocol 04</span>
                    <h3 class="text-3xl font-black text-slate-900 tracking-tighter mt-1">Aggregate Load</h3>
                    <p class="text-slate-500 font-bold mt-2">Combined weight measurement for trim optimization.</p>
                  </div>

                  <div class="space-y-6">
                     <div class="bg-pink-50 border border-pink-100 rounded-3xl p-8">
                        <div class="flex justify-between items-end">
                           <div>
                              <div class="text-[10px] font-black text-pink-600 uppercase tracking-widest mb-1.5">Total Pool Allowance</div>
                              <div class="text-4xl font-black text-slate-900 tracking-tighter">{{ totalAllowedWeight }} <span class="text-sm text-slate-400">KG</span></div>
                           </div>
                           <div class="text-right">
                              <div class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Member Count</div>
                              <div class="text-xl font-black text-slate-900">{{ selectedIds.size }}</div>
                           </div>
                        </div>
                     </div>

                     <div class="space-y-4">
                        <label class="block text-[10px] font-black text-slate-400 uppercase tracking-widest px-1">Actual Measured Load (KG)</label>
                        <div class="flex items-center gap-4">
                           <input 
                              type="number" 
                              v-model.number="actualWeight"
                              class="flex-1 h-20 bg-white border-4 border-slate-100 rounded-[2px] px-8 text-4xl font-black text-slate-900 focus:border-pink-600 focus:ring-8 focus:ring-pink-100 outline-none transition-all"
                              placeholder="0.00"
                           >
                           <div class="w-20 h-20 bg-slate-900 rounded-[5px] flex flex-col items-center justify-center text-white text-[10px] font-black">
                              <span class="opacity-50 tracking-widest mb-1 uppercase">Unit</span>
                              <span class="text-xl">KG</span>
                           </div>
                        </div>
                     </div>
                  </div>
                </div>

                <div class="bg-slate-900 rounded-[5px] p-10 flex flex-col items-center justify-center text-center relative overflow-hidden">
                   <div class="absolute inset-0 bg-gradient-to-br from-pink-500/10 to-transparent"></div>
                   
                   <div class="relative w-full max-w-sm h-4 border-2 border-slate-800 rounded-full overflow-hidden bg-slate-800/50 mb-10">
                      <div 
                         :class="[
                            'h-full transition-all duration-1000 ease-out',
                            isOverWeight ? 'bg-rose-500' : 'bg-pink-500'
                         ]"
                         :style="{ width: Math.min(100, (numericWeight / (totalAllowedWeight || 1)) * 100) + '%' }"
                      ></div>
                   </div>

                   <div class="space-y-2">
                       <span :class="[
                          'text-[10px] font-black uppercase tracking-widest px-4 py-2 rounded-xl transition-all',
                          isOverWeight ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 'bg-pink-500/20 text-pink-400 border border-pink-500/30'
                       ]">
                          {{ isOverWeight ? '⚠️ Load Excess Protocol' : '🟢 Optimized Weight Sync' }}
                       </span>
                       <div class="pt-6">
                          <span v-if="isOverWeight" class="text-5xl font-black text-white tracking-tighter">+{{ excessWeight }} KG</span>
                          <span v-else class="text-5xl font-black text-white tracking-tighter">{{ (totalAllowedWeight - numericWeight).toFixed(1) }} <span class="text-xs text-slate-500">REMAINING</span></span>
                       </div>
                   </div>

                   <div v-if="isOverWeight" class="mt-12 w-full animate-in slide-in-from-bottom-4 duration-500">
                      <label class="flex items-center gap-4 p-5 bg-white/5 border border-white/10 rounded-[5px] cursor-pointer hover:bg-white/10 transition-all text-left group">
                         <input type="checkbox" v-model="excessFeePaid" class="w-6 h-6 rounded-[2px] border-2 border-slate-700 text-pink-500 bg-transparent focus:ring-0">
                         <div>
                            <div class="text-[9px] font-black text-pink-400 uppercase tracking-widest">Revenue Collection</div>
                            <div class="text-xs font-bold text-white mt-1 group-hover:text-pink-100 transition-colors">Confirm excess fee processed manually.</div>
                         </div>
                      </label>
                   </div>
                </div>
             </div>
          </div>

          <!-- STEP 4: SEATS & FINAL -->
          <div v-if="currentStep === 4" class="space-y-10 animate-in fade-in slide-in-from-right-4 duration-500">
             <div class="grid lg:grid-cols-2 gap-12">
                <div class="space-y-8">
                   <div>
                    <span class="text-[10px] font-black text-pink-600 uppercase tracking-widest">Protocol 05</span>
                    <h3 class="text-3xl font-black text-slate-900 tracking-tighter mt-1">Slot Assignment</h3>
                    <p class="text-slate-500 font-bold mt-2">Designate operational cabin positions for the party.</p>
                  </div>

                  <div class="space-y-4 max-h-[400px] overflow-y-auto pr-2">
                     <div v-for="p in selectedPassengers" :key="p.booking_detail_id" class="flex items-center justify-between p-6 bg-slate-50 rounded-[5px] border border-slate-100 hover:border-pink-600 transition-all cursor-pointer group" @click="activeSeatPicker = p">
                        <div class="flex items-center gap-4">
                           <div class="w-10 h-10 bg-white rounded-[2px] flex items-center justify-center text-slate-400 group-hover:text-pink-600 transition-all">
                              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
                              </svg>
                           </div>
                           <div class="text-sm font-black text-slate-700 group-hover:text-pink-700 transition-colors">{{ p.passenger_name }}</div>
                        </div>
                        <div class="text-right">
                           <div class="text-[9px] font-black text-slate-400 uppercase tracking-widest">SLOT</div>
                           <div class="text-xl font-black text-pink-600 tracking-tighter">{{ p.seat || 'TBA' }}</div>
                        </div>
                     </div>
                  </div>
                </div>

                <!-- Seat Picker — Aircraft Cabin Map -->
                <div class="bg-slate-950 rounded-[5px] border border-slate-800 overflow-hidden flex flex-col h-full">
                   <div v-if="activeSeatPicker" class="flex flex-col h-full animate-in zoom-in duration-300">

                      <!-- Header -->
                      <div class="px-5 pt-5 pb-3 border-b border-slate-800">
                         <span class="text-[9px] font-black text-pink-500 uppercase tracking-[0.2em]">Assigning Slot For</span>
                         <h4 class="text-base font-black text-white tracking-tight leading-tight mt-0.5">{{ activeSeatPicker.passenger_name }}</h4>
                      </div>

                      <!-- Cabin Map -->
                      <div class="flex-1 overflow-y-auto px-4 py-3">

                         <!-- Forward cabin label -->
                         <div class="flex items-center justify-center gap-2 mb-3">
                            <div class="h-px flex-1 bg-slate-800"></div>
                            <span class="text-[8px] font-black text-slate-500 uppercase tracking-[0.2em]">▲ Forward Cabin</span>
                            <div class="h-px flex-1 bg-slate-800"></div>
                         </div>

                         <!-- Column headers -->
                         <div class="flex items-center gap-1 mb-1.5 px-7">
                            <div class="w-5 shrink-0"></div> <!-- row num spacer -->
                            <div class="flex gap-1 flex-1">
                               <span v-for="col in ['A','B','C']" :key="col" class="flex-1 text-center text-[8px] font-black text-slate-500 uppercase">{{ col }}</span>
                            </div>
                            <div class="w-5 shrink-0"></div> <!-- aisle spacer -->
                            <div class="flex gap-1 flex-1">
                               <span v-for="col in ['D','E','F']" :key="col" class="flex-1 text-center text-[8px] font-black text-slate-500 uppercase">{{ col }}</span>
                            </div>
                         </div>

                         <!-- Seat rows -->
                         <div v-if="cabinLayout.length > 0" class="space-y-1">
                            <div v-for="rowData in cabinLayout" :key="rowData.row" class="flex items-center gap-1">
                               <!-- Row number -->
                               <span class="w-5 text-[8px] font-black text-slate-600 text-center shrink-0">{{ rowData.row }}</span>

                               <!-- Left seats: A B C -->
                               <div class="flex gap-1 flex-1">
                                  <template v-for="col in ['A','B','C']" :key="col">
                                     <button
                                        v-if="rowData.seats[col]"
                                        @click="getSeatState(rowData.seats[col], activeSeatPicker) === 'available' && assignSeat(activeSeatPicker.booking_detail_id, rowData.seats[col])"
                                        :disabled="isSavingSeat || getSeatState(rowData.seats[col], activeSeatPicker) !== 'available'"
                                        :class="[
                                          'flex-1 h-8 rounded-[3px] font-black text-[8px] transition-all border relative',
                                          getSeatState(rowData.seats[col], activeSeatPicker) === 'available'
                                            ? 'bg-white/10 border-slate-600 text-slate-300 hover:bg-pink-600 hover:border-pink-500 hover:text-white cursor-pointer active:scale-95'
                                          : getSeatState(rowData.seats[col], activeSeatPicker) === 'current'
                                            ? 'bg-pink-600 border-pink-500 text-white cursor-default'
                                          : getSeatState(rowData.seats[col], activeSeatPicker) === 'group'
                                            ? 'bg-amber-500/20 border-amber-500/40 text-amber-400 cursor-default'
                                          : 'bg-slate-800/50 border-slate-800 text-slate-700 cursor-not-allowed'
                                        ]"
                                     >
                                        <span v-if="isSavingSeat && getSeatState(rowData.seats[col], activeSeatPicker) === 'available'" class="absolute inset-0 flex items-center justify-center">
                                          <span class="w-2 h-2 border border-pink-400 border-t-transparent rounded-full animate-spin"></span>
                                        </span>
                                        <span v-else>{{ col }}</span>
                                     </button>
                                     <div v-else class="flex-1 h-8"></div>
                                  </template>
                               </div>

                               <!-- Aisle -->
                               <div class="w-5 flex items-center justify-center shrink-0">
                                  <div class="h-full w-px bg-slate-800"></div>
                               </div>

                               <!-- Right seats: D E F -->
                               <div class="flex gap-1 flex-1">
                                  <template v-for="col in ['D','E','F']" :key="col">
                                     <button
                                        v-if="rowData.seats[col]"
                                        @click="getSeatState(rowData.seats[col], activeSeatPicker) === 'available' && assignSeat(activeSeatPicker.booking_detail_id, rowData.seats[col])"
                                        :disabled="isSavingSeat || getSeatState(rowData.seats[col], activeSeatPicker) !== 'available'"
                                        :class="[
                                          'flex-1 h-8 rounded-[3px] font-black text-[8px] transition-all border relative',
                                          getSeatState(rowData.seats[col], activeSeatPicker) === 'available'
                                            ? 'bg-white/10 border-slate-600 text-slate-300 hover:bg-pink-600 hover:border-pink-500 hover:text-white cursor-pointer active:scale-95'
                                          : getSeatState(rowData.seats[col], activeSeatPicker) === 'current'
                                            ? 'bg-pink-600 border-pink-500 text-white cursor-default'
                                          : getSeatState(rowData.seats[col], activeSeatPicker) === 'group'
                                            ? 'bg-amber-500/20 border-amber-500/40 text-amber-400 cursor-default'
                                          : 'bg-slate-800/50 border-slate-800 text-slate-700 cursor-not-allowed'
                                        ]"
                                     >
                                        <span v-if="isSavingSeat && getSeatState(rowData.seats[col], activeSeatPicker) === 'available'" class="absolute inset-0 flex items-center justify-center">
                                          <span class="w-2 h-2 border border-pink-400 border-t-transparent rounded-full animate-spin"></span>
                                        </span>
                                        <span v-else>{{ col }}</span>
                                     </button>
                                     <div v-else class="flex-1 h-8"></div>
                                  </template>
                               </div>
                            </div>
                         </div>

                         <!-- Fallback: flat grid if seats don't follow A-F lettering -->
                         <div v-else class="grid grid-cols-5 gap-1.5">
                            <button
                               v-for="seat in availableSeats"
                               :key="seat.id"
                               @click="assignSeat(activeSeatPicker.booking_detail_id, seat)"
                               :disabled="isSavingSeat"
                               class="h-8 bg-white/10 border border-slate-700 rounded-[3px] font-black text-[9px] text-slate-300 hover:bg-pink-600 hover:border-pink-500 hover:text-white transition-all active:scale-95 disabled:opacity-30"
                            >
                               {{ seat.seat_number }}
                            </button>
                         </div>
                      </div>

                      <!-- Legend -->
                      <div class="px-5 py-3 border-t border-slate-800 flex items-center justify-center gap-4">
                         <div class="flex items-center gap-1.5">
                            <div class="w-3 h-3 rounded-[2px] bg-white/10 border border-slate-600"></div>
                            <span class="text-[8px] font-black text-slate-500 uppercase tracking-widest">Open</span>
                         </div>
                         <div class="flex items-center gap-1.5">
                            <div class="w-3 h-3 rounded-[2px] bg-pink-600 border border-pink-500"></div>
                            <span class="text-[8px] font-black text-slate-500 uppercase tracking-widest">Selected</span>
                         </div>
                         <div class="flex items-center gap-1.5">
                            <div class="w-3 h-3 rounded-[2px] bg-amber-500/20 border border-amber-500/40"></div>
                            <span class="text-[8px] font-black text-slate-500 uppercase tracking-widest">Group</span>
                         </div>
                         <div class="flex items-center gap-1.5">
                            <div class="w-3 h-3 rounded-[2px] bg-slate-800/50 border border-slate-800"></div>
                            <span class="text-[8px] font-black text-slate-500 uppercase tracking-widest">Taken</span>
                         </div>
                      </div>

                   </div>
                   <div v-else class="flex-1 flex flex-col items-center justify-center p-10">
                      <div class="w-12 h-12 border-2 border-slate-800 rounded-full border-t-pink-600 animate-spin mb-6"></div>
                      <h4 class="text-sm font-black text-slate-500 uppercase tracking-widest">Select Passenger</h4>
                      <p class="text-[9px] text-slate-600 font-bold uppercase tracking-widest mt-1">to open cabin map</p>
                   </div>
                </div>
             </div>
          </div>

          <!-- STEP 5: FINAL SUMMARY -->
          <div v-if="currentStep === 5" class="space-y-10 animate-in fade-in slide-in-from-right-4 duration-500">
             <div class="max-w-3xl mx-auto space-y-10">
                <div class="text-center">
                   <span class="text-[10px] font-black text-pink-600 uppercase tracking-widest">Final Protocol</span>
                   <h3 class="text-4xl font-black text-slate-900 tracking-tighter mt-1">Audit Summary</h3>
                   <p class="text-slate-500 font-bold mt-2">Final validation of the party's boarding credentials.</p>
                </div>

                <div class="bg-slate-900 rounded-[5px] p-12 text-white shadow-2xl shadow-pink-200 relative overflow-hidden">
                   <div class="absolute inset-0 bg-gradient-to-br from-pink-500/20 to-transparent"></div>
                   <div class="relative z-10 grid md:grid-cols-2 gap-12">
                      <div class="space-y-8">
                         <div>
                            <div class="text-[10px] font-black text-pink-400 uppercase tracking-[0.2em] mb-4">Group Data</div>
                            <div class="space-y-3">
                               <div v-for="p in selectedPassengers" :key="p.id" class="flex justify-between items-center text-xs font-bold border-b border-white/10 pb-2.5">
                                  <span class="text-white/70">{{ p.passenger_name }}</span>
                                  <span class="text-pink-400 font-mono tracking-widest">{{ p.seat || 'TBA' }}</span>
                               </div>
                            </div>
                         </div>
                      </div>

                      <div class="space-y-10">
                         <div class="bg-white/5 rounded-[5px] p-8 border border-white/10">
                            <div class="text-[10px] font-black text-pink-400 uppercase tracking-widest mb-1.5">Measured Load</div>
                            <div class="text-5xl font-black text-white tracking-tighter">{{ numericWeight }} <span class="text-sm opacity-30">KG</span></div>
                         </div>

                         <div class="flex items-center gap-5 text-emerald-400 bg-emerald-500/5 p-4 rounded-[2px] border border-emerald-500/20">
                            <div class="w-10 h-10 rounded-full border-2 border-emerald-500/30 flex items-center justify-center">
                               <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                               </svg>
                            </div>
                            <div class="text-[11px] font-black uppercase tracking-widest leading-none">Security authorized system-wide</div>
                         </div>
                      </div>
                   </div>
                </div>

                <div class="bg-white border-2 border-slate-100 rounded-[5px] p-8 flex items-center gap-6">
                   <div class="w-14 h-14 bg-pink-50 rounded-[2px] flex items-center justify-center text-pink-600 shadow-inner">
                      <svg class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                   </div>
                   <p class="text-[10px] font-bold text-slate-500 leading-relaxed uppercase tracking-[0.15em]">Special Notice: Finalizing Check-in will distribute digital passes immediately and lock the manifest slot for weight trimming optimization.</p>
                </div>
             </div>
          </div>

        </div>

        <!-- STICKY BOTTOM NAVIGATION -->
        <div v-if="!checkinSuccess" class="p-8 bg-slate-50 border-t border-slate-100 flex items-center justify-between shrink-0">
           <div class="flex items-center gap-8">
              <div v-if="currentStep > 0" @click="currentStep--" class="text-[10px] font-black text-slate-400 hover:text-pink-600 cursor-pointer uppercase tracking-widest transition-all">
                Rollback Procedure
              </div>
              <div v-else class="w-2 h-2 bg-pink-200 rounded-full"></div>
              
              <div class="h-6 w-px bg-slate-200 hidden sm:block"></div>
              
              <div class="hidden sm:flex items-center gap-3">
                 <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Protocol Sync</span>
                 <span class="text-[10px] font-black text-emerald-600 uppercase tracking-widest bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-100 shadow-sm">Verified Level {{ currentStep + 1 }}</span>
              </div>
           </div>

           <button 
             @click="goNext"
             :disabled="!canProceed"
             class="bg-pink-600 hover:bg-slate-900 disabled:opacity-30 disabled:hover:bg-pink-600 text-white text-[11px] font-black uppercase tracking-[0.2em] px-12 py-5 rounded-[2px] transition-all shadow-xl shadow-pink-100 flex items-center gap-3 active:scale-95 group"
           >
             <span v-if="isProcessing" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
             {{ currentStep === steps.length - 1 ? 'Execute Protocol' : 'Continue Step' }}
             <svg v-if="!isProcessing" class="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M14 5l7 7m0 0l-7 7m7-7H3" />
             </svg>
           </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDcsStore } from '@/stores/dcs'
import { dcsService } from '@/services/api/dcsService'

const route = useRoute()
const router = useRouter()
const dcsStore = useDcsStore()

const pnr = ref('')
const schedule = ref(null)
const passengers = ref([])
const selectedIds = ref(new Set())
const securityClearance = ref({})
const availableSeats = ref([])
const activeSeatPicker = ref(null)

const isLoading = ref(true)
const isProcessing = ref(false)
const isSavingSeat = ref(false)
const error = ref(null)
const checkinSuccess = ref(false)
const allSeats = ref([])  // ALL seats for cabin map (available + occupied)

const steps = [
  { shortLabel: 'Presence' },
  { shortLabel: 'Dossier' },
  { shortLabel: 'Clearance' },
  { shortLabel: 'Measured Load' },
  { shortLabel: 'Slot Assign' },
  { shortLabel: 'Audit' },
]

const currentStep = ref(0)
const actualWeight = ref('')
const excessFeePaid = ref(false)

const checks = ref({
  pnrVerified: false,
  passportsInspected: false,
  visaSyncOk: false,
})

const documentationChecks = {
  pnrVerified: { label: 'Auth Check', desc: 'Verify PNR matches active records' },
  passportsInspected: { label: 'Identity', desc: 'Inspect physical IDs/Passports for all' },
  visaSyncOk: { label: 'Rights', desc: 'Check entry documents for PH-Domestic' },
}

const numericWeight = computed(() => {
  const p = parseFloat(actualWeight.value)
  return isNaN(p) ? 0 : p
})

const selectedPassengers = computed(() => {
    return (passengers.value || []).filter(p => selectedIds.value.has(p.booking_detail_id))
})

const totalAllowedWeight = computed(() => {
    // Default to 20 KG standard domestic allowance if the backend doesn't provide the field
    return selectedPassengers.value.reduce((sum, p) => sum + (p.allowed_baggage_weight || 20), 0)
})

const excessWeight = computed(() => {
  return Math.max(0, numericWeight.value - totalAllowedWeight.value).toFixed(1)
})

const isOverWeight = computed(() => numericWeight.value > totalAllowedWeight.value)

const allSelected = computed(() => {
    const checkable = (passengers.value || []).filter(p => p.status !== 'checkin')
    return checkable.length > 0 && selectedIds.value.size === checkable.length
})

// Build a structured cabin layout from all seats
const cabinLayout = computed(() => {
  const rows = {}
  allSeats.value.forEach(seat => {
    const match = (seat.seat_number || '').match(/^(\d+)([A-Fa-f])$/)
    if (!match) return
    const [, row, col] = match
    if (!rows[row]) rows[row] = {}
    rows[row][col.toUpperCase()] = seat
  })
  return Object.keys(rows)
    .sort((a, b) => parseInt(a) - parseInt(b))
    .map(row => ({ row, seats: rows[row] }))
})

// Seats already assigned to passengers in the current group
const groupAssignedSeats = computed(() => {
  return new Set(selectedPassengers.value.map(p => p.seat).filter(Boolean))
})

// Get state of a seat cell for styling
const getSeatState = (seat, activePax) => {
  if (!seat) return 'empty'
  const currentPaxSeat = activePax?.seat
  if (seat.seat_number === currentPaxSeat) return 'current'
  if (groupAssignedSeats.value.has(seat.seat_number)) return 'group'
  if (!seat.is_available) return 'occupied'
  return 'available'
}

onMounted(async () => {
    try {
        const id = route.params.booking_detail_id || route.params.id
        const initResp = await dcsService.getPassengerDetails(id)
        const initData = initResp.data
        
        pnr.value = initData.pnr
        schedule.value = initData.schedule
        
        const groupResp = await dcsService.getPnrDetails(pnr.value, schedule.value.id)
        passengers.value = groupResp.data.passengers
        
        passengers.value.forEach(p => {
            if (p.status !== 'checkin') {
                selectedIds.value.add(p.booking_detail_id)
                securityClearance.value[p.booking_detail_id] = true
            }
        })

        // Fetch ALL seats to build the full cabin map
        const seatsRes = await dcsService.getAvailableSeats(schedule.value.id)
        const allSeatData = seatsRes.data.seats || []
        allSeats.value = allSeatData
        availableSeats.value = allSeatData.filter(s => s.is_available)

    } catch (err) {
        error.value = "Failed to synchronize node with central authority."
    } finally {
        isLoading.value = false
    }
})

const togglePassenger = (id) => {
    if (selectedIds.value.has(id)) {
        selectedIds.value.delete(id)
    } else {
        selectedIds.value.add(id)
        // Ensure security clearance is initialized when a passenger is added
        if (securityClearance.value[id] === undefined) {
            securityClearance.value[id] = true
        }
    }
}

const toggleSelectAll = () => {
    if (allSelected.value) {
        selectedIds.value.clear()
    } else {
        passengers.value.forEach(p => {
            if (p.status !== 'checkin') selectedIds.value.add(p.booking_detail_id)
        })
    }
}

const toggleSecurity = (id) => {
  securityClearance.value[id] = !securityClearance.value[id]
}

const assignSeat = async (pId, seat) => {
  if (isSavingSeat.value) return
  isSavingSeat.value = true
  try {
    // Call the backend to persist the seat assignment
    await dcsService.assignSeat(pId, seat.id)
    
    // Update local passenger state on success
    const p = passengers.value.find(px => px.booking_detail_id === pId)
    if (p) p.seat = seat.seat_number
    
    // Remove the seat from available pool so it can't be double-booked
    availableSeats.value = availableSeats.value.filter(s => s.id !== seat.id)
    
    activeSeatPicker.value = null
  } catch (err) {
    console.error('Failed to assign seat:', err)
    alert(`Seat assignment failed: ${err?.response?.data?.error || 'System error. Please try again.'}`)
  } finally {
    isSavingSeat.value = false
  }
}

const canProceed = computed(() => {
  if (selectedIds.value.size === 0) return false
  if (currentStep.value === 1) return checks.value.pnrVerified && checks.value.passportsInspected && checks.value.visaSyncOk
  // Bug fix: Only check clearance for SELECTED passengers, not all keys in the object
  if (currentStep.value === 2) return selectedPassengers.value.every(p => securityClearance.value[p.booking_detail_id])
  if (currentStep.value === 3) return actualWeight.value !== '' && (isOverWeight.value ? excessFeePaid.value : true)
  if (currentStep.value === 4) return selectedPassengers.value.every(p => p.seat && p.seat !== 'TBA')
  return true
})

const goNext = async () => {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++
  } else {
    await processFinalCheckin()
  }
}

const processFinalCheckin = async () => {
  isProcessing.value = true
  try {
    const payload = Array.from(selectedIds.value).map((id, index) => ({
      booking_detail_id: id,
      actual_weight: index === 0 ? numericWeight.value : 0,
      seat_number: selectedPassengers.value.find(p => p.booking_detail_id === id)?.seat
    }))

    const success = await dcsStore.processCheckin(payload)
    if (success) {
      checkinSuccess.value = true
    }
  } catch (err) {
    alert("Procedure Interrupted: System Handshake Failed.")
  } finally {
    isProcessing.value = false
  }
}

const goBack = () => {
  if (schedule.value?.id) {
    router.push(`/dcs/manifest/${schedule.value.id}`)
  } else {
    router.push('/dcs/dashboard')
  }
}

const downloadAllPasses = () => {
  selectedPassengers.value.forEach(p => {
    // UPDATED: Added /api/ prefix and use baseURL
    const url = `${dcsService.axiosInstance.defaults.baseURL}api/dcs/boarding-pass/${p.booking_detail_id}/`
    window.open(url, '_blank')
  })
}
</script>

<style scoped>
.animate-spin-slow {
  animation: spin 8s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>
