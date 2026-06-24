<template>
  <div class="min-h-screen bg-slate-50 pb-20 lg:pb-10 font-sans">
    <BookingStatusHeader />
    
    <div class="max-w-[1100px] mx-auto px-5 lg:px-10 mt-10">
      <div>

        
        <!-- Main Content -->
        <main class="grid grid-cols-1 md:grid-cols-[220px_1fr] gap-8 items-start">
          
          <!-- Left Sidebar / Mobile Navigation -->
          <PassengerSidebar 
            :total-travelers="totalTravelers"
            :active-index="activeIndex"
            :infant-count="infantCount"
            :completed-count="completedPassengersCount"
            :completion-percentage="completionPercentage"
            :all-infants-assigned="allInfantsAssigned"
            :unassigned-infants-count="unassignedInfantsCount"
            :is-passenger-complete="isPassengerComplete"
            :has-passenger-error="hasPassengerError"
            :get-passenger-type="getPassengerType"
            :get-infant-adult-name="getInfantAdultName"
            @select="handleTabChange"
          />

          <!-- Forms Content Area -->
          <div class="flex flex-col gap-8">
            <!-- Header -->
            <div class="flex flex-col sm:flex-row justify-between items-start border-b border-slate-200 pb-5 gap-4">
              <div>
                <h1 class="text-2xl font-black text-slate-900 tracking-tight">Passenger Details</h1>
                <p class="text-[11px] text-slate-500 font-bold uppercase tracking-wider mt-1 md:hidden">
                  Completing {{ completedPassengersCount }} of {{ totalTravelers }} Travelers
                </p>
              </div>
              <div class="text-left sm:text-right w-full sm:w-auto p-3 bg-white sm:bg-transparent rounded-lg border border-slate-100 sm:border-0 shadow-sm sm:shadow-none">
                <span class="block text-[10px] sm:text-[11px] font-black text-slate-400 uppercase tracking-widest mb-1">Currently editing:</span>
                <span class="text-sm sm:text-lg font-black text-pink-500 flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full bg-pink-500 animate-pulse"></span>
                  PAX {{ activeIndex }} — {{ getPassengerType(activeIndex) }}
                </span>
                <div v-if="getPassengerType(activeIndex) === 'Infant' && getInfantAdultName(activeIndex)" class="text-[9px] font-bold text-slate-400 uppercase mt-1">
                  Assigned to {{ getInfantAdultName(activeIndex).split('(')[0] }}
                </div>
              </div>
            </div>

            <div class="flex flex-col gap-4">
              <!-- Passenger Information Card -->
              <div class="bg-white rounded-xl p-4 sm:p-8 border border-slate-200 shadow-sm">
                <div class="mb-6">
                  <h2 class="text-xl font-black text-slate-900 mb-1">Personal Information</h2>
                  <p class="text-[11px] text-slate-500 font-medium">Enter details exactly as they appear on official ID or Passport</p>
                </div>
                
                <div class="mb-2">
                  <div v-for="n in totalTravelers" :key="'form-'+n">
                    <div v-show="activeIndex === n">
                      <PassengerForm 
                        :ref="el => { if (el) passengerFormRefs[`pax_${n}`] = el }"
                        :type="getPassengerType(n)" 
                        :index="n"
                        :show-validation="showValidation"
                        :adult-passengers="availableAdultsForInfant(n)"
                        @update="(data) => updatePassengerData(getPassengerType(n), n, data)"
                        @validation="handlePassengerValidation"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Contact Information -->
              <ContactForm 
                v-model="contact"
                :show-validation="showValidation"
                :passenger1="passengers.find(p => p.key === 'pax_1')"
              />

              <!-- Navigation -->
              <div class="flex flex-col sm:flex-row justify-between items-center pt-6 border-t border-slate-200 gap-4">
                <div class="flex gap-3 w-full sm:w-auto">
                  <button 
                    v-if="activeIndex > 1"
                    type="button" 
                    class="flex-1 sm:flex-none py-3 px-5 border border-slate-300 bg-white rounded-md text-sm font-medium text-slate-600 hover:border-slate-400 hover:text-slate-800 transition-colors"
                    @click="handleTabChange(activeIndex - 1)"
                  >
                    ← Previous
                  </button>
                  
                  <button 
                    v-if="activeIndex < totalTravelers" 
                    type="button" 
                    class="flex-1 sm:flex-none py-3 px-5 border border-pink-500 text-pink-500 bg-white rounded-md text-sm font-medium hover:bg-pink-500 hover:text-white transition-all"
                    @click="goToNextGuest"
                  >
                    Next →
                  </button>
                </div>
                
                <button 
                  type="button" 
                  class="w-full sm:w-auto py-3.5 px-8 bg-pink-500 text-white rounded-md text-sm font-bold hover:bg-pink-600 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
                  @click="handleContinueToAddons"
                  :disabled="isSaving"
                >
                  <span v-if="isSaving">Saving...</span>
                  <span v-else>Continue to Add-ons</span>
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
    
    <MobileBookingFooter 
      button-text="Continue to Add-ons" 
      :loading="isSaving"
      @next="handleContinueToAddons" 
    />

    <LoadingOverlay 
      :show="isSaving" 
      title="Saving Traveler Details"
      subtitle="Please wait while we validate and save your information."
    />
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch, nextTick } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useNotificationStore } from '@/stores/notification';
import { useRouter } from 'vue-router';
import PassengerForm from '@/components/booking/PassengerForm.vue';
import BookingStatusHeader from '@/components/booking/BookingStatusHeader.vue';
import MobileBookingFooter from '@/components/booking/MobileBookingFooter.vue';
import PassengerSidebar from '@/components/booking/PassengerSidebar.vue';
import ContactForm from '@/components/booking/ContactForm.vue';
import LoadingOverlay from '@/components/common/LoadingOverlay.vue';

const bookingStore = useBookingStore();
const notificationStore = useNotificationStore();
const router = useRouter();

// --- STATE ---
const activeIndex = ref(1);
const passengers = ref([]);
const showValidation = ref(false);
const isSaving = ref(false);
const passengerValidation = ref({});
const passengerFormRefs = ref({});

const contact = ref({ 
  title: bookingStore.contactInfo.title || '',
  firstName: bookingStore.contactInfo.firstName || '', 
  middleName: bookingStore.contactInfo.middleName || '',
  lastName: bookingStore.contactInfo.lastName || '', 
  email: bookingStore.contactInfo.email || '', 
  phone: bookingStore.contactInfo.phone || '' 
});

// --- COMPUTED ---
const adultCount = computed(() => bookingStore.passengerCount.adults || 1);
const childCount = computed(() => bookingStore.passengerCount.children || 0);
const infantCount = computed(() => bookingStore.passengerCount.infants || 0);
const totalTravelers = computed(() => adultCount.value + childCount.value + infantCount.value);

// Infant assignment tracking
const infantAdultMapping = ref({});

// Adult passengers for infant assignment
const adultPassengers = computed(() => {
  return passengers.value.filter(p => p.type === 'Adult');
});

const allInfantsAssigned = computed(() => {
  const infants = passengers.value.filter(p => p.type === 'Infant');
  if (infants.length === 0) return true;
  return infants.every(infant => infantAdultMapping.value[infant.key] && adultPassengers.value.some(adult => adult.key === infantAdultMapping.value[infant.key]));
});

const unassignedInfantsCount = computed(() => {
  const infants = passengers.value.filter(p => p.type === 'Infant');
  return infants.filter(infant => !infantAdultMapping.value[infant.key]).length;
});

const isValidEmail = (email) => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
};

const isValidPhone = (phone) => {
  if (!phone) return false;
  let digitsOnly = phone.replace(/\D/g, '');
  if (digitsOnly.startsWith('0')) digitsOnly = digitsOnly.substring(1);
  return digitsOnly.length === 10;
};

const completedPassengersCount = computed(() => {
  let count = 0;
  for (let i = 1; i <= totalTravelers.value; i++) {
    if (isPassengerComplete(i)) count++;
  }
  return count;
});

const completionPercentage = computed(() => {
  return totalTravelers.value > 0 ? (completedPassengersCount.value / totalTravelers.value) * 100 : 0;
});

const hasPassengerError = (index) => {
  return passengerValidation.value[`pax_${index}`] === false && showValidation.value;
};

// --- METHODS ---
const getPassengerType = (n) => {
  if (n <= adultCount.value) return 'Adult';
  if (n <= adultCount.value + childCount.value) return 'Child';
  return 'Infant';
};

const getInfantAdultName = (infantIndex) => {
  const infantKey = `pax_${infantIndex}`;
  const adultKey = infantAdultMapping.value[infantKey];
  if (!adultKey) return null;
  const adultNumber = adultKey.replace('pax_', '');
  const adult = passengers.value.find(p => p.key === adultKey);
  return adult ? `Adult ${adultNumber} (${adult.firstName} ${adult.lastName})` : `Adult ${adultNumber}`;
};

const availableAdultsForInfant = (infantIndex) => {
  const infantKey = `pax_${infantIndex}`;
  const currentAdultKey = infantAdultMapping.value[infantKey];
  const adultInfantCount = {};
  Object.values(infantAdultMapping.value).forEach(adultKey => {
    adultInfantCount[adultKey] = (adultInfantCount[adultKey] || 0) + 1;
  });
  return adultPassengers.value.map(adult => {
    const hasOtherInfant = adultInfantCount[adult.key] > 0 && adult.key !== currentAdultKey;
    return {
      ...adult,
      key: adult.key,
      number: parseInt(adult.key.replace('pax_', '')),
      name: `${adult.firstName || ''} ${adult.lastName || ''}`.trim() || `Adult ${parseInt(adult.key.replace('pax_', ''))}`,
      isCurrent: adult.key === currentAdultKey,
      isAvailable: !hasOtherInfant || adult.key === currentAdultKey,
      alreadyHasInfant: hasOtherInfant && adult.key !== currentAdultKey
    };
  });
};

const updatePassengerData = (type, index, data) => {
  const key = data.key || `pax_${index}`;
  const idx = passengers.value.findIndex(p => p.key === key);
  const passengerEntry = { ...data, key, type };

  if (!passengerEntry.dateOfBirth && (data.dobYear && data.dobMonth && data.dobDay)) {
    passengerEntry.dateOfBirth = `${data.dobYear}-${data.dobMonth.toString().padStart(2, '0')}-${data.dobDay.toString().padStart(2, '0')}`;
  }

  if (type === 'Infant' && data.associatedAdult) {
    infantAdultMapping.value[key] = `pax_${data.associatedAdult}`;
  } else if (type === 'Infant' && !data.associatedAdult && infantAdultMapping.value[key]) {
    delete infantAdultMapping.value[key];
  }

  if (idx > -1) passengers.value[idx] = passengerEntry;
  else passengers.value.push(passengerEntry);
};

const handlePassengerValidation = ({ index, isValid }) => {
  passengerValidation.value[`pax_${index}`] = isValid;
};


const isPassengerComplete = (index) => {
  const key = `pax_${index}`;
  
  // Use the form validation directly if we have it
  if (passengerValidation.value[key] !== undefined) {
    return passengerValidation.value[key];
  }

  const data = passengers.value.find(p => p.key === key) || bookingStore.passengers.find(p => p.key === key);
  if (!data) return false;
  
  // If the data object itself has the isValid flag from emit
  if (data.isValid !== undefined) {
      return data.isValid;
  }
  
  const hasBasicInfo = !!(data.firstName?.trim() && data.lastName?.trim() && data.dateOfBirth);
  if (data.type === 'Infant') {
    return hasBasicInfo && !!(infantAdultMapping.value[key] || data.associatedAdult);
  }
  return hasBasicInfo;
};

const validateCurrentTab = () => {
  if (!isPassengerComplete(activeIndex.value)) {
    showValidation.value = true;
    const passengerType = getPassengerType(activeIndex.value);
    if (passengerType === 'Infant' && !infantAdultMapping.value[`pax_${activeIndex.value}`]) {
      notificationStore.warn(`Please select which adult the infant will sit with.`);
    } else {
      notificationStore.warn(`Please complete all required fields.`);
    }
    return false;
  }
  return true;
};

const handleTabChange = (n) => {
  if (n > activeIndex.value && !isPassengerComplete(activeIndex.value)) {
    showValidation.value = true;
    notificationStore.warn(`Please complete Passenger ${activeIndex.value} before moving to the next.`);
    return;
  }
  activeIndex.value = n;
};

const goToNextGuest = () => {
  if (validateCurrentTab()) activeIndex.value++;
};

const saveAllPassengersToStore = async () => {
  try {
    isSaving.value = true;
    for (let i = 1; i <= totalTravelers.value; i++) {
        if (!isPassengerComplete(i)) throw new Error(`Passenger ${i} incomplete`);
    }
    if (!contact.value.firstName?.trim() || !contact.value.lastName?.trim() || !isValidEmail(contact.value.email) || !isValidPhone(contact.value.phone)) {
        throw new Error('Contact information invalid');
    }
    
    bookingStore.setPassengers(passengers.value);
    bookingStore.infantAdultMapping = infantAdultMapping.value;
    bookingStore.setContactInfo(contact.value);
    return true;
  } catch (error) {
    showValidation.value = true;
    notificationStore.warn(error.message);
    return false;
  } finally {
    isSaving.value = false;
  }
};

const handleContinueToAddons = async () => {
  if (await saveAllPassengersToStore()) {
    bookingStore.snapshotToServer();
    
    // REDIRECTION LOGIC: If the fare includes a seat (Standard, Flex, Business, etc.), go directly to Seat Selection
    // This ensures users with bundled fares can "claim" their included seat immediately.
    const hasIncludedSeat = Object.values(bookingStore.fareFamilies).some(fare => 
      ['standard', 'flex', 'business', 'business_plus', 'premium'].includes(fare)
    );
    
    if (hasIncludedSeat) {
      console.log('💎 Tiered fare detected! Prioritizing Seat Selection...');
      router.push({ name: 'SeatSelection' });
    } else {
      router.push({ name: 'Addons' });
    }
  }
};

watch(contact, (newContact) => bookingStore.setContactInfo(newContact), { deep: true });

onMounted(() => {
  const session = bookingStore.checkSession();
  if (session.valid && bookingStore.passengers.length > 0) {
    passengers.value = [...bookingStore.passengers];
    infantAdultMapping.value = { ...bookingStore.infantAdultMapping };
  }
  for (let i = 1; i <= totalTravelers.value; i++) {
    if (!isPassengerComplete(i)) {
      activeIndex.value = i;
      break;
    }
  }
});
</script>