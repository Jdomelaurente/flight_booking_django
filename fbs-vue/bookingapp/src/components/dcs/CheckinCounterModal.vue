<template>
  <div class="fixed inset-0 bg-slate-900/60 backdrop-blur-md flex items-center justify-center p-4 z-[100] animate-in fade-in duration-300">
    <div class="bg-white rounded-[5px] shadow-2xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh] border border-slate-200">

      <!-- Modal Header -->
      <div class="bg-pink-600 px-10 py-8 flex justify-between items-center shrink-0 relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-pink-500 to-pink-700 opacity-50"></div>
        <div class="relative z-10">
          <h3 class="text-white font-black text-sm uppercase tracking-[0.2em]">Check-in Counter — Agent Terminal</h3>
          <p class="text-pink-100 text-[10px] font-black uppercase tracking-widest mt-1.5 opacity-80 flex items-center gap-3">
             <span class="bg-white/10 px-2 py-0.5 rounded-[2px] border border-white/10 font-mono tracking-widest text-white shadow-sm">{{ passenger?.pnr }}</span>
             <span class="w-1 h-1 bg-white/20 rounded-full"></span>
             {{ passenger?.passenger_name }}
             <span class="w-1 h-1 bg-white/20 rounded-full"></span>
             {{ dcsStore.selectedSchedule?.origin || 'MNL-T3' }} STATION
          </p>
        </div>
        <button @click="$emit('close')" class="relative z-10 text-white/60 hover:text-white transition-all p-3 rounded-[2px] hover:bg-white/10 active:scale-90 shadow-inner">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Step Progress Bar -->
      <div class="bg-slate-50 border-b border-slate-100 px-10 py-5 shrink-0">
        <div class="flex items-center gap-0">
          <div
            v-for="(step, idx) in steps"
            :key="idx"
            class="flex items-center"
            :class="idx < steps.length - 1 ? 'flex-1' : ''"
          >
            <!-- Circle -->
            <div class="flex flex-col items-center">
              <div :class="[
                'w-9 h-9 rounded-[2px] flex items-center justify-center text-[10px] font-black transition-all border-2',
                currentStep > idx
                  ? 'bg-pink-600 border-pink-600 text-white shadow-lg shadow-pink-100'
                  : currentStep === idx
                    ? 'bg-white border-pink-600 text-pink-600 shadow-xl shadow-pink-100 scale-110'
                    : 'bg-slate-100 border-slate-200 text-slate-400'
              ]">
                <svg v-if="currentStep > idx" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="4" d="M5 13l4 4L19 7"/>
                </svg>
                <span v-else>{{ idx + 1 }}</span>
              </div>
              <div class="text-[8px] mt-2 font-black uppercase tracking-widest text-center max-w-[64px] leading-tight" :class="currentStep >= idx ? 'text-slate-900' : 'text-slate-300'">
                {{ step.shortLabel }}
              </div>
            </div>
            <!-- Connector Line -->
            <div v-if="idx < steps.length - 1" class="flex-1 h-0.5 mb-6 mx-2 rounded-[2px]" :class="currentStep > idx ? 'bg-pink-400' : 'bg-slate-200'"></div>
          </div>
        </div>
      </div>

      <!-- Step Content -->
      <div class="p-10 overflow-y-auto flex-1">

        <!-- STEP 0: Identification -->
        <div v-if="currentStep === 0" class="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
          <div>
            <span class="text-[10px] font-black text-pink-600 uppercase tracking-widest">Protocol 01</span>
            <h4 class="text-slate-900 font-black text-2xl tracking-tighter mt-1">Passenger Identification</h4>
            <p class="text-slate-500 font-bold mt-2">Validate identity credentials and system reference match.</p>
          </div>

          <div class="bg-slate-900 rounded-[5px] p-8 text-white relative overflow-hidden group shadow-2xl shadow-pink-100">
             <div class="absolute inset-0 bg-gradient-to-tr from-pink-600/20 to-transparent"></div>
             <div class="relative z-10 grid grid-cols-2 gap-8">
               <div class="space-y-4">
                  <div class="text-[9px] font-black text-pink-400 uppercase tracking-[0.2em] opacity-80">Reference Unit</div>
                  <div class="font-mono font-black text-2xl tracking-[0.2em] text-white">{{ passenger?.pnr }}</div>
               </div>
               <div class="space-y-4">
                  <div class="text-[9px] font-black text-pink-400 uppercase tracking-[0.2em] opacity-80">Manifest Name</div>
                  <div class="font-black text-base text-white uppercase tracking-tight">{{ passenger?.passenger_name }}</div>
               </div>
               <div class="space-y-4 pt-4 border-t border-white/10">
                  <div class="text-[9px] font-black text-pink-400 uppercase tracking-[0.2em] opacity-80">Unit Classification</div>
                  <div class="font-black text-sm text-slate-300 uppercase tracking-widest">{{ passenger?.passenger_type }}</div>
               </div>
               <div class="space-y-4 pt-4 border-t border-white/10">
                  <div class="text-[9px] font-black text-pink-400 uppercase tracking-[0.2em] opacity-80">Transit Priority</div>
                  <div class="font-black text-sm text-emerald-400 uppercase tracking-widest">Standard-Y</div>
               </div>
             </div>
          </div>

          <div class="space-y-3">
            <label class="flex items-start gap-4 cursor-pointer group p-5 rounded-3xl border-2 border-slate-100 hover:border-pink-600 hover:bg-white transition-all shadow-sm">
              <input type="checkbox" v-model="checks.pnrConfirmed" class="mt-1 w-6 h-6 rounded-lg border-2 border-slate-200 text-pink-600 focus:ring-pink-100">
              <div>
                <div class="text-sm font-black text-slate-900 group-hover:text-pink-700 transition-colors">Manifest Authorization Sync</div>
                <div class="text-[10px] text-slate-400 font-bold uppercase tracking-tight mt-1 leading-relaxed">Confirm Reference matching active system records.</div>
              </div>
            </label>
            <label class="flex items-start gap-4 cursor-pointer group p-5 rounded-3xl border-2 border-slate-100 hover:border-pink-600 hover:bg-white transition-all shadow-sm">
              <input type="checkbox" v-model="checks.idVerified" class="mt-1 w-6 h-6 rounded-lg border-2 border-slate-200 text-pink-600 focus:ring-pink-100">
              <div>
                <div class="text-sm font-black text-slate-900 group-hover:text-pink-700 transition-colors">Credential Integrity Verification</div>
                <div class="text-[10px] text-slate-400 font-bold uppercase tracking-tight mt-1 leading-relaxed">Cross-check physical Gov-ID with digital manifest data.</div>
              </div>
            </label>
          </div>
        </div>

        <!-- STEP 1: Document Verification -->
        <div v-if="currentStep === 1" class="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
          <div>
            <span class="text-[10px] font-black text-pink-600 uppercase tracking-widest">Protocol 02</span>
            <h4 class="text-slate-900 font-black text-2xl tracking-tighter mt-1">Dossier Integrity Check</h4>
            <p class="text-slate-500 font-bold mt-2">Final validation of travel dossier and segment access rights.</p>
          </div>

          <div class="space-y-3">
            <label class="flex items-start gap-4 cursor-pointer group p-5 rounded-[5px] border-2 border-slate-100 hover:border-pink-600 hover:bg-white transition-all shadow-sm">
              <input type="checkbox" v-model="checks.travelDocsValid" class="mt-1 w-6 h-6 rounded-lg border-2 border-slate-200 text-pink-600 focus:ring-pink-100">
              <div>
                <div class="text-sm font-black text-slate-900 group-hover:text-pink-700 transition-colors">Operational Validity Period</div>
                <div class="text-[10px] text-slate-400 font-bold uppercase tracking-tight mt-1 leading-relaxed">Verify document expiration complies with regulatory standards.</div>
              </div>
            </label>
            <label class="flex items-start gap-4 cursor-pointer group p-5 rounded-[5px] border-2 border-slate-100 hover:border-pink-600 hover:bg-white transition-all shadow-sm">
              <input type="checkbox" v-model="checks.visaChecked" class="mt-1 w-6 h-6 rounded-lg border-2 border-slate-200 text-pink-600 focus:ring-pink-100">
              <div>
                <div class="text-sm font-black text-slate-900 group-hover:text-pink-700 transition-colors">Access Authorization / Visa</div>
                <div class="text-[10px] text-slate-400 font-bold uppercase tracking-tight mt-1 leading-relaxed">PH-Domestic check for entry rights and transit privileges.</div>
              </div>
            </label>
            <label class="flex items-start gap-4 cursor-pointer group p-5 rounded-3xl border-2 border-slate-100 hover:border-pink-600 hover:bg-white transition-all shadow-sm">
              <input type="checkbox" v-model="checks.specialNeedsReviewed" class="mt-1 w-6 h-6 rounded-lg border-2 border-slate-200 text-pink-600 focus:ring-pink-100">
              <div>
                <div class="text-sm font-black text-slate-900 group-hover:text-pink-700 transition-colors">SSR Protocol Sync</div>
                <div class="text-[10px] text-slate-400 font-bold uppercase tracking-tight mt-1 leading-relaxed">Review and authorize special handling requirements (SSRs).</div>
              </div>
            </label>
          </div>
        </div>

        <!-- STEP 2: Seat Confirmation -->
        <div v-if="currentStep === 2" class="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
          <div>
            <span class="text-[10px] font-black text-pink-600 uppercase tracking-widest">Protocol 03</span>
            <h4 class="text-slate-900 font-black text-2xl tracking-tighter mt-1">Slot Assignment Verification</h4>
            <p class="text-slate-500 font-bold mt-2">Designate and authorize cabin position for manifest finalization.</p>
          </div>

          <div class="bg-slate-900 rounded-[5px] p-10 flex items-center justify-between shadow-2xl shadow-pink-100 relative overflow-hidden">
            <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-pink-600 to-transparent opacity-50"></div>
            <div>
              <div class="text-[10px] text-pink-400 font-black uppercase tracking-[0.2em] mb-2 opacity-80">Designated Terminal Slot</div>
              <div class="text-6xl font-black text-white font-mono tracking-tighter">{{ passenger?.seat || 'TBA' }}</div>
            </div>
            <div class="w-24 h-24 bg-white/5 rounded-[2px] border border-white/10 flex items-center justify-center text-5xl backdrop-blur-sm grayscale opacity-30">💺</div>
          </div>

          <label class="flex items-start gap-4 cursor-pointer group p-6 rounded-[5px] border-2 border-slate-100 hover:border-pink-600 hover:bg-white transition-all shadow-sm">
            <input type="checkbox" v-model="checks.seatConfirmed" class="mt-1 w-7 h-7 rounded-xl border-2 border-slate-200 text-pink-600 focus:ring-pink-100">
            <div>
              <div class="text-base font-black text-slate-900 group-hover:text-pink-700 transition-colors">Authorize Slot Assignment</div>
              <div class="text-[11px] text-slate-400 font-bold uppercase tracking-tight mt-1 leading-relaxed">Passenger has formally acknowledged designated cabin position.</div>
            </div>
          </label>
        </div>

        <!-- STEP 3: Baggage Drop -->
        <div v-if="currentStep === 3" class="space-y-10 animate-in fade-in slide-in-from-right-4 duration-500">
          <div>
            <span class="text-[10px] font-black text-pink-600 uppercase tracking-widest">Protocol 04</span>
            <h4 class="text-slate-900 font-black text-2xl tracking-tighter mt-1">Aggregate Load Measurement</h4>
            <p class="text-slate-500 font-bold mt-2">Sync physical weight measurement with manifest allowance.</p>
          </div>

          <!-- Allowance -->
          <div class="bg-pink-50 border-2 border-pink-100 rounded-[5px] p-6 flex justify-between items-center shadow-inner">
            <div>
              <div class="text-[10px] text-pink-600 font-black uppercase tracking-widest mb-1.5 opacity-80">Sync Allowance Unit</div>
              <div class="text-sm font-black text-slate-800 uppercase tracking-widest">{{ passenger?.baggage_allowance_name }}</div>
            </div>
            <div class="text-right">
               <div class="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-1.5 opacity-80">Upper Bound</div>
               <div class="text-2xl font-black text-pink-600">
                  {{ passenger?.allowed_baggage_weight }} <span class="text-xs font-bold text-slate-400 uppercase">KG</span>
               </div>
            </div>
          </div>

          <!-- Scale -->
          <div class="space-y-4">
            <label class="block text-[10px] font-black text-slate-400 uppercase tracking-widest px-2">Terminal Sensor Reading (KG)</label>
            <div class="flex items-center gap-5">
               <input
                 type="number"
                 v-model="actualWeight"
                 min="0"
                 step="0.5"
                 placeholder="0.0"
                 class="flex-1 h-20 bg-white border-4 border-slate-100 rounded-[2px] px-8 text-4xl font-mono font-black text-slate-900 focus:border-pink-600 focus:ring-8 focus:ring-pink-100 outline-none transition-all shadow-sm"
               >
               <div class="w-20 h-20 bg-slate-900 rounded-[2px] flex flex-col items-center justify-center text-white shrink-0 shadow-xl">
                  <span class="text-[9px] font-black uppercase tracking-widest opacity-40 mb-1">UNIT</span>
                  <span class="text-xl font-black">KG</span>
               </div>
            </div>
            <!-- Weight status indicator -->
            <div class="px-2">
               <span v-if="actualWeight !== ''" :class="[
                 'text-[10px] font-black uppercase tracking-widest px-4 py-2 rounded-[2px] border-2 transition-all inline-flex items-center gap-2',
                 excessWeight > 0 ? 'bg-rose-50 text-rose-600 border-rose-100 shadow-sm' : 'bg-emerald-50 text-emerald-600 border-emerald-100 shadow-sm'
               ]">
                  <span class="w-2 h-2 rounded-full" :class="excessWeight > 0 ? 'bg-rose-500 animate-pulse' : 'bg-emerald-500'"></span>
                  {{ excessWeight > 0 ? `${excessWeight.toFixed(1)} KG EXCESS DETECTED` : 'LOAD PARAMETERS NORMAL' }}
               </span>
            </div>
          </div>

          <!-- Excess Warning -->
          <Transition
            enter-active-class="transition duration-400 ease-out"
            enter-from-class="-translate-y-4 opacity-0"
            enter-to-class="translate-y-0 opacity-100"
          >
            <div v-if="excessWeight > 0" class="bg-slate-950 rounded-[5px] p-8 relative overflow-hidden group shadow-2xl">
               <div class="absolute inset-0 bg-gradient-to-br from-rose-600/20 to-transparent"></div>
               <div class="relative z-10">
                 <div class="flex items-center gap-4 mb-6">
                    <div class="w-12 h-12 bg-rose-600 rounded-[2px] flex items-center justify-center text-white shadow-lg shadow-rose-900/40">
                       <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                         <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                       </svg>
                    </div>
                    <div>
                       <div class="text-[11px] font-black text-rose-400 uppercase tracking-widest">Revenue Leak Prevention</div>
                       <div class="text-lg font-black text-white tracking-tight mt-0.5">Authorize Charge Override</div>
                    </div>
                 </div>
                 <p class="text-[10px] text-slate-400 font-bold uppercase tracking-tight leading-relaxed mb-8">Execute manual fee collection for {{ excessWeight.toFixed(1) }} KG overflow before manifest slot locking.</p>
                 <label class="flex items-center gap-4 p-5 bg-white/5 border border-white/10 rounded-[2px] cursor-pointer hover:bg-white/10 transition-all">
                    <input type="checkbox" v-model="excessFeePaid" class="w-7 h-7 rounded-xl border-2 border-slate-700 text-pink-600 bg-transparent focus:ring-0">
                    <span class="text-xs font-black text-white uppercase tracking-widest">Authorize Payment Sync</span>
                 </label>
               </div>
            </div>
          </Transition>

          <label class="flex items-start gap-4 cursor-pointer group p-6 rounded-[5px] border-2 border-slate-100 hover:border-pink-600 hover:bg-white transition-all shadow-sm">
            <input type="checkbox" v-model="checks.baggageTagPrinted" class="mt-1 w-7 h-7 rounded-xl border-2 border-slate-200 text-pink-600 focus:ring-pink-100">
            <div>
              <div class="text-base font-black text-slate-900 group-hover:text-pink-700 transition-colors">Physical Load Finalization</div>
              <div class="text-[11px] text-slate-400 font-bold uppercase tracking-tight mt-1 leading-relaxed">System has output baggage identification tags; load is secured for transit.</div>
            </div>
          </label>
        </div>

        <!-- STEP 4: Issue Boarding Pass -->
        <div v-if="currentStep === 4" class="space-y-10 animate-in fade-in slide-in-from-right-4 duration-500">
          <div>
            <span class="text-[10px] font-black text-pink-600 uppercase tracking-widest">Final Audit</span>
            <h4 class="text-slate-900 font-black text-2xl tracking-tighter mt-1">Authorization Summary</h4>
            <p class="text-slate-500 font-bold mt-2">Confirm and execute final system synchronization for node issuance.</p>
          </div>

          <!-- Summary Card -->
          <div class="bg-slate-900 rounded-[5px] p-10 text-white shadow-2xl shadow-pink-100 relative overflow-hidden">
             <div class="absolute inset-0 bg-gradient-to-br from-pink-600/20 to-transparent"></div>
             <div class="relative z-10 grid grid-cols-2 gap-10">
                <div class="space-y-8">
                   <div>
                      <div class="text-[9px] font-black text-pink-400 uppercase tracking-[0.2em] mb-4">Individual Metadata</div>
                      <div class="space-y-4">
                         <div class="flex justify-between border-b border-white/10 pb-3">
                            <span class="text-[10px] font-black uppercase text-white/50 tracking-widest">ID Name</span>
                            <span class="text-xs font-black text-white uppercase">{{ passenger?.passenger_name }}</span>
                         </div>
                         <div class="flex justify-between border-b border-white/10 pb-3">
                            <span class="text-[10px] font-black uppercase text-white/50 tracking-widest">Reference</span>
                            <span class="text-xs font-mono font-black text-pink-400 tracking-[0.2em]">{{ passenger?.pnr }}</span>
                         </div>
                         <div class="flex justify-between">
                            <span class="text-[10px] font-black uppercase text-white/50 tracking-widest">Slot Unit</span>
                            <span class="text-xs font-black text-white font-mono">{{ passenger?.seat || 'TBA' }}</span>
                         </div>
                      </div>
                   </div>
                </div>

                <div class="space-y-8">
                   <div class="bg-white/5 rounded-[5px] p-8 border border-white/10">
                      <div class="text-[10px] font-black text-pink-400 uppercase tracking-widest mb-3 opacity-80">Sync Measure</div>
                      <div class="text-5xl font-black text-white tracking-tighter">
                         {{ numericWeight || 0 }} <span class="text-sm opacity-30 font-black">KG</span>
                      </div>
                      <div v-if="excessWeight > 0" class="text-[9px] font-black text-rose-400 uppercase tracking-widest mt-4 flex items-center gap-2">
                         <div class="w-1.5 h-1.5 bg-rose-400 rounded-full"></div>
                         Manual Revenue Sync Authorized
                      </div>
                   </div>
                </div>
             </div>
          </div>

          <div class="bg-white border-2 border-slate-100 rounded-[5px] p-8 flex items-center gap-6 shadow-sm">
             <div class="w-14 h-14 bg-emerald-50 rounded-[2px] flex items-center justify-center text-emerald-600 shadow-inner">
                <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
             </div>
             <div>
                <div class="text-[11px] font-black text-emerald-800 uppercase tracking-widest">Validation Status: CLEAR</div>
                <p class="text-[10px] font-bold text-slate-400 mt-1 uppercase tracking-tight leading-relaxed">Executing "Issue Boarding Pass" will finalize manifest state and unlock digital transit passes for physical output.</p>
             </div>
          </div>
        </div>

      </div>

      <!-- Footer -->
      <div class="px-10 py-8 bg-slate-50 border-t border-slate-100 shrink-0 flex items-center justify-between">
        <!-- Status indicator -->
        <div class="flex items-center gap-4">
           <div class="px-5 py-2.5 bg-white border border-slate-200 rounded-[2px] shadow-sm text-[10px] font-black text-slate-900 uppercase tracking-widest">
             Step {{ currentStep + 1 }} / {{ steps.length }}
           </div>
           <div v-if="canProceed" class="text-[9px] font-black text-emerald-600 uppercase tracking-[0.2em] animate-pulse">
             System Sync OK
           </div>
        </div>

        <div class="flex gap-4">
          <button
            v-if="currentStep > 0"
            @click="currentStep--"
            class="px-8 py-4 rounded-[2px] text-slate-500 font-black uppercase tracking-widest hover:bg-slate-200 transition-all text-[10px] active:scale-95"
          >
            Rollback
          </button>
          <button
            @click="$emit('close')"
            v-if="currentStep === 0"
            class="px-8 py-4 rounded-2xl text-slate-400 font-black uppercase tracking-widest hover:bg-slate-200 transition-all text-[10px] active:scale-95"
          >
            Abort
          </button>

          <!-- Next Step -->
          <button
            v-if="currentStep < steps.length - 1"
            @click="goNext"
            :disabled="!canProceed"
            class="px-10 py-4 rounded-[2px] font-black text-[10px] uppercase tracking-[0.2em] transition-all shadow-xl flex items-center gap-3 active:scale-95 group"
            :class="canProceed ? 'bg-pink-600 hover:bg-slate-900 text-white shadow-pink-100' : 'bg-slate-200 text-slate-400 cursor-not-allowed'"
          >
            Progress Link
            <svg class="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
              <path stroke-linecap="round" stroke-linejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>

          <!-- Final CTA -->
          <button
            v-if="currentStep === steps.length - 1"
            @click="processCheckin"
            :disabled="isProcessing"
            class="px-10 py-4 rounded-2xl font-black text-[10px] uppercase tracking-[0.2em] flex items-center gap-3 shadow-2xl transition-all active:scale-95 group"
            :class="!isProcessing ? 'bg-pink-600 hover:bg-slate-900 text-white shadow-pink-100' : 'bg-slate-200 text-slate-400 cursor-not-allowed'"
          >
            <span v-if="isProcessing" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
             Authorization Finish
             <svg v-if="!isProcessing" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
               <path stroke-linecap="round" stroke-linejoin="round" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
             </svg>
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDcsStore } from '@/stores/dcs'

const props = defineProps({
  passenger: { type: Object, required: true }
})
const emit = defineEmits(['close', 'checkin-complete'])

const dcsStore = useDcsStore()

const steps = [
  { shortLabel: 'Presence' },
  { shortLabel: 'Dossier' },
  { shortLabel: 'Slot' },
  { shortLabel: 'Load' },
  { shortLabel: 'Final' },
]

const currentStep = ref(0)
const isProcessing = ref(false)
const actualWeight = ref('')
const excessFeePaid = ref(false)

const checks = ref({
  pnrConfirmed: false,
  idVerified: false,
  checkinDeadlineMet: true, // Auto-verified in terminal session
  travelDocsValid: false,
  visaChecked: false,
  specialNeedsReviewed: true, // Default to true if not flagged
  seatConfirmed: false,
  baggageTagPrinted: false,
})

const numericWeight = computed(() => {
  const p = parseFloat(actualWeight.value)
  return isNaN(p) ? 0 : p
})

const excessWeight = computed(() => {
  if (!props.passenger || props.passenger.allowed_baggage_weight === undefined) return 0
  return Math.max(0, numericWeight.value - props.passenger.allowed_baggage_weight)
})

const canProceed = computed(() => {
  if (currentStep.value === 0) {
    return checks.value.pnrConfirmed && checks.value.idVerified
  }
  if (currentStep.value === 1) {
    return checks.value.travelDocsValid && checks.value.visaChecked
  }
  if (currentStep.value === 2) {
    return checks.value.seatConfirmed
  }
  if (currentStep.value === 3) {
    const baggageOk = excessWeight.value > 0 ? excessFeePaid.value : true
    return checks.value.baggageTagPrinted && baggageOk && actualWeight.value !== ''
  }
  return true
})

const goNext = () => {
  if (canProceed.value && currentStep.value < steps.length - 1) {
    currentStep.value++
  }
}

const processCheckin = async () => {
  isProcessing.value = true
  emit('checkin-complete', {
    booking_detail_id: props.passenger.booking_detail_id,
    actual_baggage_weight: numericWeight.value
  })
}
</script>

<style scoped>
/* No additional styles needed as Tailwind v4 handles animations and gradients better */
</style>
