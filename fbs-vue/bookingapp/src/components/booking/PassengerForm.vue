<template>
  <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden transition-all duration-300 hover:shadow-md">
    <!-- Card Header -->
    <div class="px-4 sm:px-6 py-3 sm:py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-pink-100 flex items-center justify-center text-pink-600 font-bold text-sm">
          {{ index }}
        </div>
        <div>
          <h3 class="font-bold text-slate-800 uppercase tracking-tight text-sm">
            Passenger {{ index }} — {{ type }}
          </h3>
          <p v-if="type === 'Infant'" class="text-[10px] text-slate-500 font-medium">
            Sits on adult's lap
          </p>
        </div>
      </div>
      
      <div v-if="isFormValid" class="flex items-center gap-1.5 text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider border border-emerald-100">
        <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
        </svg>
        Complete
      </div>
    </div>

    <div class="p-4 sm:p-6 space-y-6 sm:space-y-8">
      <!-- Section: Personal Information -->
      <section>
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1.5 h-4 bg-pink-500 rounded-full"></div>
          <h4 class="text-xs font-bold text-slate-400 uppercase tracking-[0.15em]">Personal Information</h4>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-12 gap-5">
          <!-- Title selection -->
          <div class="md:col-span-2">
            <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1.5 ml-1">Title</label>
            <div class="relative">
              <select 
                v-model="form.title" 
                @change="emitData"
                class="w-full h-11 px-4 bg-white border rounded-lg text-sm font-medium transition-all outline-none appearance-none focus:ring-2 focus:ring-pink-500/20"
                :class="[showErrors && !form.title ? 'border-pink-500 bg-pink-50' : 'border-slate-200 hover:border-slate-300 focus:border-pink-500']"
              >
                <option value="">Select</option>
                <option value="MR">Mr.</option>
                <option value="MRS">Mrs.</option>
                <option value="MS">Ms.</option>
              </select>
              <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
              </div>
            </div>
            <p v-if="showErrors && !form.title" class="mt-1 text-[9px] text-pink-500 font-medium ml-1">
              Title is required
            </p>
          </div>

          <!-- First Name -->
          <div class="md:col-span-4">
            <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1.5 ml-1">
              First Name <span class="text-pink-500">*</span>
            </label>
            <input 
              v-model="form.firstName" 
              type="text" 
              placeholder="e.g. Juan"
              @input="handleNameInput('firstName')"
              class="w-full h-11 px-4 bg-white border rounded-lg text-sm font-medium transition-all outline-none focus:ring-2 focus:ring-pink-500/20"
              :class="[showErrors && !isNameValid(form.firstName) ? 'border-pink-500 bg-pink-50' : 'border-slate-200 hover:border-slate-300 focus:border-pink-500']"
            >
            <p v-if="showErrors && !form.firstName.trim()" class="mt-1 text-[9px] text-pink-500 font-medium ml-1">
              First name is required
            </p>
            <p v-else-if="showErrors && !isNameValid(form.firstName)" class="mt-1 text-[9px] text-pink-500 font-medium ml-1">
              Invalid characters in name
            </p>
          </div>

          <!-- Middle Initial -->
          <div class="md:col-span-2">
            <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1.5 ml-1">M.I.</label>
            <input 
              v-model="form.middleInitial" 
              type="text" 
              maxlength="1" 
              placeholder="A"
              @input="debounceEmit"
              class="w-full h-11 px-4 bg-white border border-slate-200 rounded-lg text-sm font-medium transition-all outline-none hover:border-slate-300 focus:border-pink-500 focus:ring-2 focus:ring-pink-500/20"
            >
          </div>

          <!-- Last Name -->
          <div class="md:col-span-4">
            <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1.5 ml-1">
              Last Name <span class="text-pink-500">*</span>
            </label>
            <input 
              v-model="form.lastName" 
              type="text" 
              placeholder="e.g. Dela Cruz"
              @input="handleNameInput('lastName')"
              class="w-full h-11 px-4 bg-white border rounded-lg text-sm font-medium transition-all outline-none focus:ring-2 focus:ring-pink-500/20"
              :class="[showErrors && !isNameValid(form.lastName) ? 'border-pink-500 bg-pink-50' : 'border-slate-200 hover:border-slate-300 focus:border-pink-500']"
            >
             <p v-if="showErrors && !form.lastName.trim()" class="mt-1 text-[9px] text-pink-500 font-medium ml-1">
              Last name is required
            </p>
            <p v-else-if="showErrors && !isNameValid(form.lastName)" class="mt-1 text-[9px] text-pink-500 font-medium ml-1">
              Invalid characters in name
            </p>
          </div>
        </div>

        <!-- Date of Birth Row -->
        <div class="mt-6">
          <label class="block text-[11px] font-bold text-slate-500 uppercase mb-2 ml-1">
            Date of Birth <span class="text-pink-500">*</span>
          </label>
          <div class="grid grid-cols-6 gap-2 sm:gap-3">
            <!-- Day -->
            <div class="col-span-2 md:col-span-1 relative">
              <select v-model="form.dobDay" @change="emitData" 
                class="w-full h-11 px-3 bg-white border rounded-lg text-sm font-medium focus:border-pink-500 focus:ring-2 focus:ring-pink-500/20 outline-none appearance-none"
                :class="[showErrors && !form.dobDay ? 'border-pink-500 bg-pink-50' : 'border-slate-200 hover:border-slate-300']"
              >
                <option value="">Day</option>
                <option v-for="d in 31" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
            <!-- Month -->
            <div class="col-span-4 md:col-span-2 relative">
              <select v-model="form.dobMonth" @change="emitData" 
                class="w-full h-11 px-3 bg-white border rounded-lg text-sm font-medium focus:border-pink-500 focus:ring-2 focus:ring-pink-500/20 outline-none appearance-none"
                :class="[showErrors && !form.dobMonth ? 'border-pink-500 bg-pink-50' : 'border-slate-200 hover:border-slate-300']"
              >
                <option value="">Month</option>
                <option v-for="(m, i) in months" :key="i" :value="i+1">{{ m }}</option>
              </select>
            </div>
            <!-- Year -->
            <div class="col-span-4 md:col-span-2">
              <input 
                v-model="form.dobYear" 
                type="number" 
                placeholder="Year (YYYY)" 
                min="1900" 
                :max="new Date().getFullYear()"
                @input="debounceEmit"
                class="w-full h-11 px-4 bg-white border rounded-lg text-sm font-medium focus:border-pink-500 focus:ring-2 focus:ring-pink-500/20 outline-none"
                :class="[showErrors && !form.dobYear ? 'border-pink-500 bg-pink-50' : 'border-slate-200 hover:border-slate-300']"
              >
            </div>
            <!-- Age Badge (Responsive) -->
            <div v-if="calculatedAge !== null" class="col-span-2 md:col-span-1 flex items-center justify-end md:justify-center">
              <div class="px-2 py-1 bg-slate-100 rounded-full text-[9px] font-bold text-slate-600 uppercase tracking-wider whitespace-nowrap">
                Age: {{ calculatedAge }}
              </div>
            </div>
          </div>
          <p v-if="showErrors && (!form.dobDay || !form.dobMonth || !form.dobYear)" class="mt-1 text-[9px] text-pink-500 font-medium ml-1">
            Complete date of birth is required
          </p>
          <p v-if="showAgeWarning" class="mt-2 text-[10px] text-amber-600 font-bold bg-amber-50 p-2 rounded border border-amber-100 flex items-center gap-2">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
            <span v-if="type === 'Adult'">This passenger must be an Adult (12+ years old)</span>
            <span v-else-if="type === 'Child'">This passenger must be a Child (2-11 years old)</span>
            <span v-else>This passenger must be an Infant (Under 2 years old)</span>
          </p>
        </div>
      </section>

      <!-- Section: Travel Documents -->
      <section class="p-4 sm:p-5 bg-slate-50/50 rounded-xl border border-slate-100 space-y-6">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1.5 h-4 bg-slate-400 rounded-full"></div>
          <h4 class="text-xs font-bold text-slate-400 uppercase tracking-[0.15em]">Travel Documents</h4>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Nationality -->
          <div>
            <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1.5 ml-1">Nationality</label>
            <div class="relative">
              <select 
                v-model="form.nationality" 
                @change="emitData"
                class="w-full h-11 px-4 bg-white border border-slate-200 rounded-lg text-sm font-medium transition-all outline-none appearance-none focus:ring-2 focus:ring-pink-500/20 focus:border-pink-500"
              >
                <option value="Philippines">Philippines</option>
                <option value="United States">United States</option>
                <option value="Japan">Japan</option>
                <option value="South Korea">South Korea</option>
                <option value="Singapore">Singapore</option>
                <option value="Australia">Australia</option>
              </select>
              <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
              </div>
            </div>
            <div class="mt-2">
              <span v-if="requiresPassport" class="text-[9px] font-black text-pink-500 uppercase tracking-tighter flex items-center gap-1">
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
                ID/Passport Required
              </span>
              <span v-else class="text-[9px] font-black text-emerald-500 uppercase tracking-tighter flex items-center gap-1">
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                Local ID Accepted
              </span>
            </div>
          </div>

          <!-- Passport Number -->
          <div>
            <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1.5 ml-1">
              {{ documentLabel }}
            </label>
            <input 
              v-model="form.passport" 
              type="text" 
              :placeholder="requiresPassport && bookingStore.isInternational ? 'P0000000A' : 'ID or Passport Number'"
              @input="debounceEmit"
              class="w-full h-11 px-4 bg-white border rounded-lg text-sm font-medium transition-all outline-none focus:ring-2 focus:ring-pink-500/20"
              :class="[showErrors && requiresPassport && !form.passport ? 'border-pink-500 bg-pink-50' : 'border-slate-200 hover:border-slate-300 focus:border-pink-500']"
            >
            <p class="mt-1 text-[8px] text-slate-400 font-medium ml-1">
               Enter if available or required by your destination
            </p>
          </div>
        </div>

        <!-- Passport Expiry -->
        <div v-if="requiresPassport || form.passport" class="space-y-2">
          <label class="block text-[11px] font-bold text-slate-500 uppercase mb-1.5 ml-1">
            {{ requiresPassport ? 'Passport Expiry' : 'Expiry Date' }}
          </label>
          <div class="grid grid-cols-6 gap-2 sm:gap-3">
            <div class="col-span-2 md:col-span-1 relative">
              <select 
                v-model="form.expiryDay" 
                @change="emitData" 
                class="w-full h-11 px-3 rounded-lg text-sm font-medium focus:border-pink-500 outline-none transition-colors appearance-none"
                :class="[(showErrors || (form.expiryDay && form.expiryMonth && form.expiryYear)) && (requiresPassport || form.passport) && !passportStatus.isValid ? 'border-2 border-pink-500 bg-pink-50 text-pink-700' : 'border border-slate-200 bg-white hover:border-slate-300 focus:ring-2 focus:ring-pink-500/20']"
              >
                <option value="">Day</option>
                <option v-for="d in 31" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
            
            <div class="col-span-4 md:col-span-2 relative">
              <select 
                v-model="form.expiryMonth" 
                @change="emitData" 
                class="w-full h-11 px-3 rounded-lg text-sm font-medium focus:border-pink-500 outline-none transition-colors appearance-none"
                :class="[(showErrors || (form.expiryDay && form.expiryMonth && form.expiryYear)) && (requiresPassport || form.passport) && !passportStatus.isValid ? 'border-2 border-pink-500 bg-pink-50 text-pink-700' : 'border border-slate-200 bg-white hover:border-slate-300 focus:ring-2 focus:ring-pink-500/20']"
              >
                <option value="">Month</option>
                <option v-for="(m, i) in months" :key="i" :value="i+1">{{ m }}</option>
              </select>
            </div>
            
            <div class="col-span-6 md:col-span-2">
              <input 
                v-model="form.expiryYear" 
                type="number" 
                placeholder="Year" 
                :min="new Date().getFullYear()" 
                @input="debounceEmit" 
                class="w-full h-11 px-4 rounded-lg text-sm font-medium focus:border-pink-500 outline-none transition-colors"
                :class="[(showErrors || (form.expiryDay && form.expiryMonth && form.expiryYear)) && (requiresPassport || form.passport) && !passportStatus.isValid ? 'border-2 border-pink-500 bg-pink-50 text-pink-700 placeholder-pink-300' : 'border border-slate-200 bg-white hover:border-slate-300 focus:ring-2 focus:ring-pink-500/20']"
              >
            </div>
          </div>
          <p v-if="(showErrors || (form.expiryDay && form.expiryMonth && form.expiryYear)) && (requiresPassport || form.passport) && !passportStatus.isValid" class="text-[9px] text-pink-500 font-medium mt-1 ml-1">
            {{ passportStatus.message }}
          </p>
        </div>
      </section>

      <!-- Section: PH Discounts -->
      <div v-if="type === 'Adult'" class="p-4 sm:p-5 bg-emerald-50/30 rounded-xl border border-emerald-100/50">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1.5 h-4 bg-emerald-500 rounded-full"></div>
          <h4 class="text-xs font-bold text-emerald-700 uppercase tracking-[0.15em]">PH Resident Discounts</h4>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <label 
            class="flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all shrink-0"
            :class="[form.phDiscountType === 'none' ? 'bg-emerald-500 border-emerald-500 text-white shadow-md shadow-emerald-100' : 'bg-white border-slate-200 hover:border-slate-300']"
          >
            <input type="radio" v-model="form.phDiscountType" value="none" @change="emitData" class="sr-only">
            <div class="w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0" :class="[form.phDiscountType === 'none' ? 'border-white bg-white' : 'border-slate-300']">
               <div v-if="form.phDiscountType === 'none'" class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></div>
            </div>
            <span class="text-xs font-black uppercase tracking-widest">None</span>
          </label>

          <label 
            class="flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all shrink-0"
            :class="[
              isSeniorDisabled ? 'opacity-40 cursor-not-allowed border-slate-100 bg-slate-50' : 
              form.phDiscountType === 'senior' ? 'bg-emerald-500 border-emerald-500 text-white shadow-md shadow-emerald-100' : 'bg-white border-slate-200 hover:border-slate-300'
            ]"
          >
            <input type="radio" v-model="form.phDiscountType" value="senior" :disabled="isSeniorDisabled" @change="emitData" class="sr-only">
            <div class="w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0" :class="[form.phDiscountType === 'senior' ? 'border-white bg-white' : 'border-slate-300']">
               <div v-if="form.phDiscountType === 'senior'" class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></div>
            </div>
            <span class="text-xs font-black uppercase tracking-widest">Senior ID</span>
          </label>

          <label 
            class="flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-all shrink-0"
            :class="[form.phDiscountType === 'pwd' ? 'bg-emerald-500 border-emerald-500 text-white shadow-md shadow-emerald-100' : 'bg-white border-slate-200 hover:border-slate-300']"
          >
            <input type="radio" v-model="form.phDiscountType" value="pwd" @change="emitData" class="sr-only">
            <div class="w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0" :class="[form.phDiscountType === 'pwd' ? 'border-white bg-white' : 'border-slate-300']">
               <div v-if="form.phDiscountType === 'pwd'" class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></div>
            </div>
            <span class="text-xs font-black uppercase tracking-widest">PWD ID</span>
          </label>
        </div>

        <div v-if="form.phDiscountType !== 'none'" class="mt-5 w-full sm:max-w-sm">
          <label class="block text-[10px] font-bold text-emerald-700 uppercase mb-1.5 ml-1">
            {{ form.phDiscountType === 'senior' ? 'Senior ID Number' : 'PWD ID Number' }}
          </label>
          <input 
            v-model="form.phDiscountId" 
            type="text" 
            placeholder="Enter ID Number"
            @input="debounceEmit"
            class="w-full h-11 px-4 bg-white border border-emerald-200 rounded-lg text-sm font-medium focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 outline-none"
          >
          <p v-if="showErrors && form.phDiscountType !== 'none' && !form.phDiscountId.trim()" class="mt-1 text-[9px] text-pink-500 font-medium ml-1">
            ID number is required for discount
          </p>
        </div>
      </div>

      <!-- Section: Infant Lap Selection -->
       <div v-if="type === 'Infant'" class="p-5 bg-pink-50/50 rounded-xl border border-pink-100">
        <div class="flex items-center gap-2 mb-4">
          <div class="w-1.5 h-4 bg-pink-500 rounded-full"></div>
          <h4 class="text-xs font-bold text-pink-700 uppercase tracking-[0.15em]">Associate with Adult</h4>
        </div>
        
        <p class="text-xs text-pink-600/70 italic mb-4">This infant must be assigned to an adult's lap.</p>
        
        <div v-if="adultOptions && adultOptions.length > 0" class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button 
            v-for="adult in adultOptions" 
            :key="adult.key"
            type="button"
            @click="selectAdult(adult)"
            :disabled="adult.alreadyHasInfant && adult.number !== form.associatedAdult"
            class="flex items-center justify-between p-4 rounded-xl border-2 transition-all text-left"
            :class="[
              form.associatedAdult === adult.number 
                ? 'bg-white border-pink-500 shadow-sm' 
                : adult.alreadyHasInfant ? 'bg-slate-50 border-slate-100 opacity-50 cursor-not-allowed' : 'bg-white border-slate-100 hover:border-pink-200'
            ]"
          >
            <div>
              <div class="text-sm font-bold text-slate-800">{{ adult.name || 'Passenger ' + adult.number }}</div>
              <div class="text-[10px] text-slate-500 font-medium uppercase tracking-wider">Adult {{ adult.number }}</div>
            </div>
            
            <div v-if="form.associatedAdult === adult.number" class="w-5 h-5 bg-pink-500 rounded-full flex items-center justify-center text-white">
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
            </div>
            <div v-else-if="adult.alreadyHasInfant" class="text-[8px] font-black text-pink-400 uppercase">Assigned</div>
          </button>
        </div>
        
        <div v-else class="p-4 bg-amber-50 border border-amber-100 rounded-lg text-center">
          <p class="text-xs font-bold text-amber-700">No adult passengers found yet.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted, onUnmounted, watch, computed, nextTick } from 'vue';
import { useBookingStore } from '@/stores/booking';

const props = defineProps({
  type: String,
  index: Number,
  showValidation: { type: Boolean, default: false },
  adultPassengers: { type: Array, default: () => [] }
});
const emit = defineEmits(['update', 'validation']);

const bookingStore = useBookingStore();

const months = ["January", "February", "March", "April", "May", "June", 
                "July", "August", "September", "October", "November", "December"];

const form = reactive({
    title: '',
    firstName: '',
    middleInitial: '',
    lastName: '',
    dobDay: '',
    dobMonth: '',
    dobYear: '',
    nationality: 'Philippines',
    passport: '',
    expiryDay: '',
    expiryMonth: '',
    expiryYear: '',
    phDiscountType: 'none',
    phDiscountId: '',
    associatedAdult: null
});

const requiresPassport = computed(() => false);

const documentLabel = computed(() => {
  // Use "ID / Passport" for domestic Filipino travel, otherwise "Passport"
  if (form.nationality === 'Philippines' && !bookingStore.isInternational) {
    return 'ID / Passport Number';
  }
  return 'Passport Number';
});

const passportStatus = computed(() => {
  if (!form.expiryDay || !form.expiryMonth || !form.expiryYear) return { isValid: false, message: 'Complete date required', type: 'error' };
  
  const expDate = new Date(form.expiryYear, form.expiryMonth - 1, form.expiryDay);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // 1. Check if actually expired
  if (expDate <= today) {
    const label = requiresPassport.value ? 'Passport' : 'ID';
    return { isValid: false, message: `${label} has expired`, type: 'error' };
  }

  // 2. Check 6-month validity (International Only)
  if (bookingStore.isInternational) {
    const travelDate = bookingStore.lastTravelDate ? new Date(bookingStore.lastTravelDate) : new Date();
    const sixMonthsFromTravel = new Date(travelDate);
    sixMonthsFromTravel.setMonth(sixMonthsFromTravel.getMonth() + 6);
    
    if (expDate < sixMonthsFromTravel) {
      return { 
        isValid: false, 
        message: 'Passport must be valid for at least 6 months from travel', 
        type: 'warning' 
      };
    }
  }

  return { isValid: true, message: '', type: 'success' };
});

// Validation Regex
const nameRegex = /^[a-zA-Z\s-]+$/;

const isNameValid = (name) => {
  if (!name || !name.trim()) return false;
  return nameRegex.test(name.trim());
};

const handleNameInput = (field) => {
  // Allow typing but flag for validation
  debounceEmit();
};

// Computed properties
const showErrors = computed(() => props.showValidation);
const isDOBValid = computed(() => form.dobDay && form.dobMonth && form.dobYear);

// Age calculation
const calculatedAge = computed(() => {
  if (!form.dobYear || !form.dobMonth || !form.dobDay) return null;
  
  try {
    const birthDate = new Date(form.dobYear, form.dobMonth - 1, form.dobDay);
    const today = new Date();
    
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    const dayDiff = today.getDate() - birthDate.getDate();
    
    if (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) {
      age--;
    }
    
    return age;
  } catch (error) {
    console.error('Error calculating age:', error);
    return null;
  }
});

// Age validation warnings
const showAgeWarning = computed(() => {
  if (!calculatedAge.value) return false;
  
  if (props.type === 'Adult' && calculatedAge.value < 12) return true;
  if (props.type === 'Child' && (calculatedAge.value < 2 || calculatedAge.value >= 12)) return true;
  if (props.type === 'Infant' && calculatedAge.value >= 2) return true;
  
  return false;
});

const correctPassengerType = computed(() => {
  if (!calculatedAge.value) return '';
  
  if (calculatedAge.value >= 12) return 'Adult';
  if (calculatedAge.value >= 2) return 'Child';
  return 'Infant';
});

// Adult options for infant assignment
const adultOptions = computed(() => {
  if (!props.adultPassengers || props.adultPassengers.length === 0) return [];
  
  return props.adultPassengers.map(adult => {
    const hasOtherInfant = adult.alreadyHasInfant && adult.number !== form.associatedAdult;
    
    return {
      ...adult,
      isCurrent: adult.number === form.associatedAdult,
      isAvailable: !hasOtherInfant || adult.number === form.associatedAdult
    };
  });
});

const isFormValid = computed(() => {
  const basicValid = form.title && 
                     isNameValid(form.firstName) && 
                     isNameValid(form.lastName) && 
                     form.dobDay && 
                     form.dobMonth && 
                     form.dobYear &&
                     form.nationality &&
                     !showAgeWarning.value; // Important: Age must match type
  
  if (props.type === 'Infant' && !form.associatedAdult) return false;
  
  // 1. Validate Passport if required OR if user provided one
  if (requiresPassport.value || form.passport) {
    if (requiresPassport.value && (!form.passport || !form.passport.trim())) return false;
    if (!passportStatus.value.isValid) return false;
  }

  // 2. Validate PH Discount ID if claimed
  if (props.type === 'Adult' && form.phDiscountType !== 'none' && !form.phDiscountId.trim()) return false;
  
  return basicValid;
});

// Computed properties for discounts
const isSeniorDisabled = computed(() => {
  return !calculatedAge.value || calculatedAge.value < 60;
});

// Watch age changes to reset senior choice if they drop below 60
watch(calculatedAge, (newAge) => {
  if (form.phDiscountType === 'senior' && (!newAge || newAge < 60)) {
    form.phDiscountType = 'none';
    form.phDiscountId = '';
    emitData();
  }
});

// Get saved passenger data for this index
const savedPassenger = computed(() => {
  const key = `pax_${props.index}`;
  return bookingStore.passengers.find(p => p.key === key);
});

const shouldLoadSavedData = computed(() => {
  if (!bookingStore.isSessionValid) return false;
  return !!savedPassenger.value;
});

// Methods
const selectAdult = (adult) => {
  if (adult.alreadyHasInfant && adult.number !== form.associatedAdult) {
    return;
  }
  
  if (form.associatedAdult === adult.number) {
    form.associatedAdult = null;
  } else {
    form.associatedAdult = adult.number;
  }
  
  emitData();
};

// Load saved data from store
const loadSavedData = () => {
  if (shouldLoadSavedData.value) {
    console.log(`📥 Loading saved data for passenger ${props.index}:`, savedPassenger.value);
    
    form.title = savedPassenger.value.title || '';
    form.firstName = savedPassenger.value.firstName || '';
    form.middleInitial = savedPassenger.value.middleName || '';
    form.lastName = savedPassenger.value.lastName || '';
    form.nationality = savedPassenger.value.nationality || 'Philippines';
    form.passport = savedPassenger.value.passportNumber || '';
    form.phDiscountType = savedPassenger.value.phDiscountType || 'none';
    form.phDiscountId = savedPassenger.value.phDiscountId || '';

    // Parse passport expiry
    if (savedPassenger.value.passportExpiry) {
      try {
        const expiry = new Date(savedPassenger.value.passportExpiry);
        if (!isNaN(expiry.getTime())) {
          form.expiryDay = expiry.getDate();
          form.expiryMonth = expiry.getMonth() + 1;
          form.expiryYear = expiry.getFullYear();
        }
      } catch (error) {
        console.error('Error parsing passport expiry:', error);
      }
    }
    
    // Parse date of birth - FIXED: Check for dateOfBirth field
    if (savedPassenger.value.dateOfBirth) {
      console.log(`📅 Found dateOfBirth in saved data: ${savedPassenger.value.dateOfBirth}`);
      try {
        const dob = new Date(savedPassenger.value.dateOfBirth);
        if (!isNaN(dob.getTime())) {
          form.dobDay = dob.getDate();
          form.dobMonth = dob.getMonth() + 1;
          form.dobYear = dob.getFullYear();
          console.log(`📅 Parsed DOB: Day=${form.dobDay}, Month=${form.dobMonth}, Year=${form.dobYear}`);
        } else {
          console.log('❌ Invalid date format in saved data');
        }
      } catch (error) {
        console.error('Error parsing date of birth:', error);
      }
    } else {
      console.log('📝 No dateOfBirth found in saved data');
    }
    
    // Load infant association
    if (props.type === 'Infant' && bookingStore.infantAdultMapping) {
      const infantKey = `pax_${props.index}`;
      const adultKey = bookingStore.infantAdultMapping[infantKey];
      if (adultKey) {
        form.associatedAdult = parseInt(adultKey.replace('pax_', ''));
        console.log(`👶 Loaded infant association: ${infantKey} -> ${adultKey}`);
      }
    }
    
    nextTick(() => {
      emitData();
    });
  } else {
    console.log(`🆕 No saved data for passenger ${props.index}, starting fresh`);
    resetForm();
  }
};

// Reset form to initial state
const resetForm = () => {
  form.title = '';
  form.firstName = '';
  form.middleInitial = '';
  form.lastName = '';
  form.dobDay = '';
  form.dobMonth = '';
  form.dobYear = '';
  form.nationality = 'Philippines';
  form.passport = '';
  form.expiryDay = '';
  form.expiryMonth = '';
  form.expiryYear = '';
  form.phDiscountType = 'none';
  form.phDiscountId = '';
  form.associatedAdult = null;
  
  emitData();
};

// Watch for changes
watch(savedPassenger, () => {
  loadSavedData();
});

watch(() => props.index, () => {
  loadSavedData();
});

watch(() => props.adultPassengers, (newAdults) => {
  if (props.type === 'Infant') {
    // If we have an associated adult, check if they are still valid
    if (form.associatedAdult) {
      const currentAdult = newAdults.find(a => a.number === form.associatedAdult);
      if (!currentAdult || currentAdult.alreadyHasInfant) {
        form.associatedAdult = null;
        emitData();
      }
    } 
    // Auto-assign if there's exactly 1 available adult and we have none assigned
    else if (!form.associatedAdult && newAdults.length === 1 && !newAdults[0].alreadyHasInfant) {
      form.associatedAdult = newAdults[0].number;
      emitData();
    }
  }
}, { deep: true, immediate: true });

watch(() => bookingStore.isSessionValid, (isValid) => {
  if (!isValid) {
    console.log(`Session invalid, resetting form for passenger ${props.index}`);
    resetForm();
  }
});

// FIXED: Always emit validation when isFormValid changes
watch(isFormValid, (newValid) => {
  emit('validation', { index: props.index, isValid: newValid });
}, { immediate: true });

// Debounce timer
let debounceTimer = null;

// Debounced emit function
const debounceEmit = () => {
  if (debounceTimer) {
    clearTimeout(debounceTimer);
  }
  
  debounceTimer = setTimeout(() => {
    emitData();
  }, 300);
};

// FIXED: Properly construct dateOfBirth string
const emitData = () => {
  console.log(`🔄 Emitting data for passenger ${props.index}`);
  console.log(`📅 DOB Fields: Day=${form.dobDay}, Month=${form.dobMonth}, Year=${form.dobYear}`);
  
  // Validate DOB - FIXED: Proper construction
  let dateOfBirth = '';
  if (form.dobYear && form.dobMonth && form.dobDay) {
    try {
      const month = form.dobMonth.toString().padStart(2, '0');
      const day = form.dobDay.toString().padStart(2, '0');
      const year = form.dobYear.toString();
      
      // Create the date string
      dateOfBirth = `${year}-${month}-${day}`;
      
      // Validate date
      const dobDate = new Date(dateOfBirth);
      if (isNaN(dobDate.getTime())) {
        console.log(`❌ Invalid date constructed: ${dateOfBirth}`);
        dateOfBirth = '';
      } else {
        console.log(`✅ Valid date constructed: ${dateOfBirth}`);
      }
    } catch (error) {
      console.error('Error formatting date of birth:', error);
      dateOfBirth = '';
    }
  } else {
    console.log('❌ Missing DOB fields');
  }

  const formattedData = {
    title: form.title,
    firstName: form.firstName.trim(),
    middleName: form.middleInitial.trim(),
    lastName: form.lastName.trim(),
    dateOfBirth: dateOfBirth,
    nationality: form.nationality,
    passportNumber: form.passport.trim(),
    passportExpiry: form.expiryYear && form.expiryMonth && form.expiryDay 
                   ? `${form.expiryYear}-${form.expiryMonth.toString().padStart(2, '0')}-${form.expiryDay.toString().padStart(2, '0')}` 
                   : '',
    phDiscountType: form.phDiscountType,
    phDiscountId: form.phDiscountId.trim(),
    type: props.type,
    key: `pax_${props.index}`,
    isValid: isFormValid.value,
    // Also include individual DOB fields for debugging
    dobDay: form.dobDay,
    dobMonth: form.dobMonth,
    dobYear: form.dobYear
  };
  
  // Add infant-specific data
  if (props.type === 'Infant') {
    formattedData.associatedAdult = form.associatedAdult;
  }
  
  console.log(`📤 Emitting passenger ${props.index}:`, formattedData);
  emit('update', formattedData);
  emit('validation', { index: props.index, isValid: isFormValid.value });
};

// Lifecycle hooks
onMounted(() => {
  console.log(`🚀 PassengerForm ${props.index} mounted`);
  
  const session = bookingStore.checkSession();
  if (!session.valid) {
    console.log('Session invalid, starting fresh');
    resetForm();
  } else {
    loadSavedData();
  }
});

onUnmounted(() => {
  if (debounceTimer) {
    clearTimeout(debounceTimer);
  }
});
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>

<style scoped>
/* Scoped styles removed in favor of Tailwind CSS */
/* Any complex animations can be added here if needed */
</style>
