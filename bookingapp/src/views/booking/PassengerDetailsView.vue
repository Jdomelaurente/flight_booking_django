<template>
  <div class="minimal-container">
    <div class="minimal-layout">
      <!-- Main Content - Forms -->
      <main class="main-content">
        <!-- Left Sidebar - Passenger Selection -->
        <aside class="passenger-sidebar">
          <div class="sidebar-card">
            <div class="sidebar-header">
              <h2 class="sidebar-title">Select Passenger</h2>
              <div class="passenger-count">{{ totalTravelers }} traveler(s)</div>
            </div>
            
            <div class="passenger-list">
              <div 
                v-for="n in totalTravelers" 
                :key="n"
                :class="['passenger-item', { 
                  active: activeIndex === n, 
                  complete: isPassengerComplete(n),
                  error: hasPassengerError(n),
                  infant: getPassengerType(n) === 'Infant'
                }]"
                @click="handleTabChange(n)"
              >
                <div class="item-number">{{ n }}</div>
                <div class="item-info">
                  <div class="item-type">{{ getPassengerType(n) }}
                    <span v-if="getPassengerType(n) === 'Infant' && getInfantAdultName(n)" class="infant-badge">
                      with {{ getInfantAdultName(n) }}
                    </span>
                  </div>
                  
                  <div class="item-status" v-if="isPassengerComplete(n)">
                    <span class="status-dot"></span>
                    Complete
                  </div>
                  <div class="item-status" v-else-if="hasPassengerError(n)">
                    <span class="status-dot error"></span>
                    Error
                  </div>
                  <div class="item-status" v-else>
                    <span class="status-dot incomplete"></span>
                    Incomplete
                  </div>
                </div>
                <div class="item-arrow">›</div>
              </div>
            </div>
            
            <div class="sidebar-footer">
              <div class="completion-status">
                <div class="completion-text">
                  {{ completedPassengersCount }} of {{ totalTravelers }} passengers complete
                </div>
                <div class="completion-bar">
                  <div class="completion-fill" :style="{ width: completionPercentage + '%' }"></div>
                </div>
              </div>
              
              <!-- Infant Assignment Status -->
              <div v-if="infantCount > 0" class="infant-status">
                <div class="infant-status-text">
                  <span v-if="allInfantsAssigned">
                    All infants assigned to adults
                  </span>
                  <span v-else class="infant-warning">
                    {{ unassignedInfantsCount }} infant(s) need adult assignment
                  </span>
                </div>
              </div>
            </div>
          </div>
        </aside>

        <!-- Forms Content Area -->
        <div class="forms-content">
          <!-- Header -->
          <div class="page-header">
            <div>
              <h1 class="page-title">Passenger Details</h1>
            </div>
            <div class="current-passenger">
              <span class="current-label">Currently editing:</span>
              <span class="current-info">Passenger {{ activeIndex }} - {{ getPassengerType(activeIndex) }}
                <span v-if="getPassengerType(activeIndex) === 'Infant' && getInfantAdultName(activeIndex)" class="infant-assignment">
                  (with {{ getInfantAdultName(activeIndex) }})
                </span>
              </span>
            </div>
          </div>

          <!-- Form Container -->
          <div class="form-container">
            <!-- Passenger Information -->
            <div class="form-section">
              <h2 class="form-title">Personal Information</h2>
              <p class="form-subtitle">Please enter details exactly as they appear on official ID</p>
              
              <div class="forms-wrapper">
                <div v-for="n in totalTravelers" :key="'form-'+n">
                  <div v-show="activeIndex === n">
                    <PassengerForm 
                      ref="passengerForms"
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

              <!-- Special Requests -->
              <div class="requests-section">
                <div class="requests-title">Special Requests</div>
                <div class="request-options">
                  <label class="option-label">
                    <input type="checkbox" class="option-checkbox">
                    I have a declaration / request
                  </label>
                  <label class="option-label">
                    <input type="checkbox" class="option-checkbox">
                    I am a Person with Disability (PWD)
                  </label>
                </div>
              </div>
            </div>

            <!-- Contact Information -->
            <div class="form-section">
              <h2 class="form-title">Contact Information</h2>
              <p class="form-subtitle">Your booking details will be sent here</p>
              
              <!-- Name Row: 3 columns -->
              <div class="contact-grid">
                <div class="input-group">
                  <label class="input-label">First Name <span class="required">*</span></label>
                  <input v-model="contact.firstName" type="text" class="input-field" 
                         placeholder="First Name" required
                         :class="{ 'error': showValidation && !contact.firstName.trim() }">
                  <span v-if="showValidation && !contact.firstName.trim()" class="field-error">
                    First name is required
                  </span>
                </div>
                
                <div class="input-group">
                  <label class="input-label">Middle Name</label>
                  <input v-model="contact.middleName" type="text" class="input-field" 
                         placeholder="Middle Name (Optional)">
                </div>
                
                <div class="input-group">
                  <label class="input-label">Last Name <span class="required">*</span></label>
                  <input v-model="contact.lastName" type="text" class="input-field" 
                         placeholder="Last Name" required
                         :class="{ 'error': showValidation && !contact.lastName.trim() }">
                  <span v-if="showValidation && !contact.lastName.trim()" class="field-error">
                    Last name is required
                  </span>
                </div>
              </div>
              
              <!-- Email and Phone Row: 2 columns -->
              <div class="contact-grid second-row">
                <div class="input-group">
                  <label class="input-label">Email Address <span class="required">*</span></label>
                  <input v-model="contact.email" type="email" class="input-field" 
                         placeholder="email@example.com" required
                         :class="{ 'error': showValidation && !isValidEmail(contact.email) }">
                  <span v-if="showValidation && !isValidEmail(contact.email)" class="field-error">
                    Valid email is required
                  </span>
                </div>
                
                <div class="input-group phone-group">
                  <label class="input-label">Phone Number <span class="required">*</span></label>
                  <div class="phone-wrapper">
                    <div class="country-code">+63</div>
                    <input v-model="contact.phone" type="tel" class="input-field phone-field" 
                           placeholder="912 345 6789" required
                           :class="{ 'error': showValidation && !isValidPhone(contact.phone) }">
                  </div>
                  <span v-if="showValidation && !isValidPhone(contact.phone)" class="field-error">
                    Valid phone number is required (10 digits)
                  </span>
                </div>
              </div>
            </div>

            <!-- Navigation -->
            <div class="navigation-section">
              <div class="nav-buttons">
                <button 
                  v-if="activeIndex > 1"
                  type="button" 
                  class="nav-button prev-button"
                  @click="handleTabChange(activeIndex - 1)"
                >
                  ← Previous
                </button>
                
                <button 
                  v-if="activeIndex < totalTravelers" 
                  type="button" 
                  class="nav-button next-button"
                  @click="goToNextGuest"
                >
                  Next →
                </button>
              </div>
              
              <button 
                type="button" 
                class="continue-button"
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

      <!-- Right Sidebar - Booking Summary -->
      <aside class="summary-sidebar">
        <BookingTimer variant="sidebar" />
        <div class="summary-card">
          <div class="summary-header">
            <h3 class="summary-title">Booking Summary</h3>
          </div>
          
          <!-- Flight Summary -->
          <div class="summary-section">
            <template v-if="bookingStore.isMultiCity">
              <div v-for="(segment, index) in bookingStore.multiCitySegments" :key="index" class="flight-summary">
                <div class="flight-header">
                  <span class="flight-label">Flight {{ index + 1 }}</span>
                  <span class="flight-price">₱{{ Number(segment.selectedFlight?.price || 0).toLocaleString() }}</span>
                </div>
                <div class="route" v-if="segment.selectedFlight">
                  <span class="city">{{ segment.selectedFlight.origin }}</span>
                  <span class="arrow">→</span>
                  <span class="city">{{ segment.selectedFlight.destination }}</span>
                </div>
                <div class="flight-date" v-if="segment.selectedFlight">
                  {{ segment.selectedFlight.departure_date }}
                </div>
              </div>
            </template>
            <template v-else>
              <div class="flight-summary">
                <div class="flight-header">
                  <span class="flight-label">Departure</span>
                  <span class="flight-price">₱{{ Number(selectedFlight?.price || 0).toLocaleString() }}</span>
                </div>
                <div class="route" v-if="selectedFlight">
                  <span class="city">{{ selectedFlight.origin }}</span>
                  <span class="arrow">→</span>
                  <span class="city">{{ selectedFlight.destination }}</span>
                </div>
                <div class="flight-date" v-if="selectedFlight">{{ selectedFlight.departure_date }}</div>
              </div>

              <div v-if="isRoundTrip && selectedReturn" class="flight-summary">
                <div class="flight-header">
                  <span class="flight-label">Return</span>
                  <span class="flight-price">₱{{ Number(selectedReturn?.price || 0).toLocaleString() }}</span>
                </div>
                <div class="route">
                  <span class="city">{{ selectedReturn.origin }}</span>
                  <span class="arrow">→</span>
                  <span class="city">{{ selectedReturn.destination }}</span>
                </div>
                <div class="flight-date">{{ selectedReturn.departure_date }}</div>
              </div>
            </template>
          </div>

          <!-- Travelers Summary -->
          <div class="summary-section">
            <div class="travelers-breakdown">
              <div class="breakdown-item">
                <span class="breakdown-label">Adults ({{ adultCount }})</span>
                <span class="breakdown-price">₱{{ (bookingStore.grandTotalForAdults || 0).toLocaleString() }}</span>
              </div>
              
              <div v-if="childCount > 0" class="breakdown-item">
                <span class="breakdown-label">Children ({{ childCount }})</span>
                <span class="breakdown-price">₱{{ (bookingStore.grandTotalForChildren || 0).toLocaleString() }}</span>
              </div>
              
              <div v-if="infantCount > 0" class="breakdown-item">
                <span class="breakdown-label">Infants ({{ infantCount }})</span>
                <span class="breakdown-price">₱{{ (bookingStore.grandTotalForInfants || 0).toLocaleString() }}</span>
              </div>
            </div>
            
            <!-- Infant Assignment Note -->
            <div v-if="infantCount > 0" class="infant-note">
              <span class="note-text">Infants will sit on an adult's lap</span>
            </div>
          </div>

          <!-- Total -->
          <div class="total-section">
            <div class="total-row">
              <span class="total-label">Total Amount</span>
              <span class="total-amount">₱{{ (calculateTotal() || 0).toLocaleString() }}</span>
            </div>
            <div class="tax-note">Inclusive of all taxes and fees</div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch, nextTick } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useNotificationStore } from '@/stores/notification';
import { useRouter } from 'vue-router';
import PassengerForm from '@/components/booking/PassengerForm.vue';
import BookingTimer from '@/components/booking/BookingTimer.vue';

const bookingStore = useBookingStore();
const notificationStore = useNotificationStore();
const router = useRouter();

// --- STATE ---
const activeIndex = ref(1);
const passengers = ref([]);
const passengerForms = ref([]);
const showValidation = ref(false);
const isSaving = ref(false);
const passengerValidation = ref({});

const contact = reactive({ 
  title: bookingStore.contactInfo.title || '',
  firstName: bookingStore.contactInfo.firstName || '', 
  middleName: bookingStore.contactInfo.middleName || '',
  lastName: bookingStore.contactInfo.lastName || '', 
  email: bookingStore.contactInfo.email || '', 
  phone: bookingStore.contactInfo.phone || '' 
});

// --- COMPUTED ---
const selectedFlight = computed(() => bookingStore.selectedOutbound);
const selectedReturn = computed(() => bookingStore.selectedReturn); 
const isRoundTrip = computed(() => bookingStore.isRoundTrip); 
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

// Check if all infants have adults assigned
const allInfantsAssigned = computed(() => {
  const infants = passengers.value.filter(p => p.type === 'Infant');
  if (infants.length === 0) return true;
  
  return infants.every(infant => {
    return infantAdultMapping.value[infant.key] && adultPassengers.value.some(adult => adult.key === infantAdultMapping.value[infant.key]);
  });
});

// Count unassigned infants
const unassignedInfantsCount = computed(() => {
  const infants = passengers.value.filter(p => p.type === 'Infant');
  return infants.filter(infant => !infantAdultMapping.value[infant.key]).length;
});

// Validation helpers
const isValidEmail = (email) => {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
};

const isValidPhone = (phone) => {
  const digitsOnly = phone.replace(/\D/g, '');
  return digitsOnly.length === 10; // Exactly 10 digits after +63
};

// Completion tracking
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
  const key = `pax_${index}`;
  const validation = passengerValidation.value[key];
  return validation === false;
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
  
  if (adult) {
    return `Adult ${adultNumber} (${adult.firstName} ${adult.lastName})`;
  }
  
  return `Adult ${adultNumber}`;
};

// Get available adults for a specific infant
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

// FIXED: Update passenger data with proper date construction
const updatePassengerData = (type, index, data) => {
  const key = data.key || `pax_${index}`;
  
  const idx = passengers.value.findIndex(p => p.key === key);
  
  const passengerEntry = { 
    ...data, 
    key,
    type,
  };

  // FIXED: Ensure dateOfBirth is constructed from individual parts if not provided
  if (!passengerEntry.dateOfBirth || passengerEntry.dateOfBirth === '') {
    console.log(`📅 No dateOfBirth provided for passenger ${index}, checking individual parts`);
    
    // Check if we have individual DOB parts in the data
    if (data.dobYear && data.dobMonth && data.dobDay) {
      try {
        const month = data.dobMonth.toString().padStart(2, '0');
        const day = data.dobDay.toString().padStart(2, '0');
        passengerEntry.dateOfBirth = `${data.dobYear}-${month}-${day}`;
        console.log(`📅 Constructed date of birth from parts: ${passengerEntry.dateOfBirth}`);
      } catch (error) {
        console.error('Error constructing date of birth:', error);
      }
    } else if (passengerEntry.dobYear && passengerEntry.dobMonth && passengerEntry.dobDay) {
      // Also check if DOB parts are already in passengerEntry
      try {
        const month = passengerEntry.dobMonth.toString().padStart(2, '0');
        const day = passengerEntry.dobDay.toString().padStart(2, '0');
        passengerEntry.dateOfBirth = `${passengerEntry.dobYear}-${month}-${day}`;
        console.log(`📅 Constructed date of birth from passengerEntry: ${passengerEntry.dateOfBirth}`);
      } catch (error) {
        console.error('Error constructing date of birth:', error);
      }
    } else {
      console.log(`❌ No DOB data available for passenger ${index}`);
    }
  } else {
    console.log(`✅ Date of birth already provided: ${passengerEntry.dateOfBirth}`);
  }

  // Handle infant-adult association
  if (type === 'Infant' && data.associatedAdult) {
    const adultKey = `pax_${data.associatedAdult}`;
    infantAdultMapping.value[key] = adultKey;
    console.log(`👶 Infant ${index} assigned to Adult ${data.associatedAdult} (${adultKey})`);
  } else if (type === 'Infant' && !data.associatedAdult) {
    if (infantAdultMapping.value[key]) {
      console.log(`👶 Infant ${index} unassigned from adult`);
      delete infantAdultMapping.value[key];
    }
  }

  // If adult data is updated, update any associated infants
  if (type === 'Adult') {
    Object.entries(infantAdultMapping.value).forEach(([infantKey, assignedAdultKey]) => {
      if (assignedAdultKey === key) {
        const infantIndex = parseInt(infantKey.replace('pax_', ''));
        const infantData = passengers.value.find(p => p.key === infantKey);
        if (infantData) {
          infantData.adultNameUpdated = true;
        }
      }
    });
  }

  if (idx > -1) {
    passengers.value[idx] = passengerEntry;
  } else {
    passengers.value.push(passengerEntry);
  }
  
  console.log(`✅ Updated passenger ${index} (${type}):`, passengerEntry);
  
  // Immediately check if passenger is complete
  const isComplete = isPassengerComplete(index);
  console.log(`📊 Passenger ${index} completion check: ${isComplete ? '✅ Complete' : '❌ Incomplete'}`);
};

const handlePassengerValidation = ({ index, isValid }) => {
  const key = `pax_${index}`;
  passengerValidation.value[key] = isValid;
  console.log(`📋 Passenger ${index} validation: ${isValid ? '✅ Valid' : '❌ Invalid'}`);
};

const calculateTotal = () => {
  // Passengers step shows base fare summary only (add-ons are selected on the next step)
  return (
    (bookingStore.grandTotalForAdults || 0) +
    (bookingStore.grandTotalForChildren || 0) +
    (bookingStore.grandTotalForInfants || 0)
  );
};

// FIXED: Enhanced passenger completion check
const isPassengerComplete = (index) => {
  const key = `pax_${index}`;
  const data = passengers.value.find(p => p.key === key);
  
  // Check store data as fallback
  if (!data && bookingStore.passengers.length > 0) {
    const storeData = bookingStore.passengers.find(p => p.key === key);
    if (storeData) {
      console.log(`📦 Using store data for passenger ${index}:`, storeData);
      
      // For infants, also check if they have an adult assigned
      if (storeData.type === 'Infant') {
        const hasAdultAssigned = bookingStore.infantAdultMapping && 
                                bookingStore.infantAdultMapping[storeData.key];
        // Infants need: firstName, lastName, dateOfBirth, AND adult assignment
        return !!(
          storeData.firstName?.trim() && 
          storeData.lastName?.trim() && 
          storeData.dateOfBirth &&
          hasAdultAssigned
        );
      }
      
      // Adults/Children need: firstName, lastName, dateOfBirth
      return !!(
        storeData.firstName?.trim() && 
        storeData.lastName?.trim() && 
        storeData.dateOfBirth
      );
    }
  }
  
  if (!data) {
    console.log(`❌ No data found for passenger ${index}`);
    return false;
  }
  
  // Debug log to see what data we have
  console.log(`🔍 Checking completion for passenger ${index} (${data.type}):`, {
    hasFirstName: !!data.firstName?.trim(),
    firstName: data.firstName,
    hasLastName: !!data.lastName?.trim(),
    lastName: data.lastName,
    hasDateOfBirth: !!data.dateOfBirth,
    dateOfBirth: data.dateOfBirth,
    isInfant: data.type === 'Infant',
    hasAdultAssigned: infantAdultMapping.value[data.key],
    associatedAdult: data.associatedAdult,
    // Debug individual DOB parts
    dobDay: data.dobDay,
    dobMonth: data.dobMonth,
    dobYear: data.dobYear
  });
  
  // Check basic required fields for all passengers
  const hasFirstName = !!data.firstName?.trim();
  const hasLastName = !!data.lastName?.trim();
  const hasDateOfBirth = !!data.dateOfBirth;
  
  if (!hasFirstName || !hasLastName || !hasDateOfBirth) {
    console.log(`❌ Passenger ${index} missing basic info:`, {
      hasFirstName,
      hasLastName,
      hasDateOfBirth,
      dateOfBirthValue: data.dateOfBirth
    });
    return false;
  }
  
  // Additional check for infants - they need adult assignment
  if (data.type === 'Infant') {
    const hasAdultAssigned = infantAdultMapping.value[data.key];
    const hasAssociatedAdult = data.associatedAdult;
    const hasAdult = hasAdultAssigned || hasAssociatedAdult;
    
    if (!hasAdult) {
      console.log(`❌ Infant ${index} has no adult assigned`);
      return false;
    }
    
    console.log(`✅ Infant ${index} is complete with adult: ${hasAdultAssigned || hasAssociatedAdult}`);
    return true;
  }
  
  // For Adults/Children, just basic info is enough
  console.log(`✅ Passenger ${index} (${data.type}) is complete`);
  return true;
};

const validateCurrentTab = () => {
  if (!isPassengerComplete(activeIndex.value)) {
    showValidation.value = true;
    nextTick(() => {
      const formElement = document.querySelector('.pal-card');
      if (formElement) {
        formElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
    
    const passengerType = getPassengerType(activeIndex.value);
    if (passengerType === 'Infant' && !infantAdultMapping.value[`pax_${activeIndex.value}`]) {
      notificationStore.warn(`Please select which adult the infant will sit with for Passenger ${activeIndex.value} before continuing.`);
    } else {
      notificationStore.warn(`Please complete all required fields for Passenger ${activeIndex.value} before continuing.`);
    }
    return false;
  }
  return true;
};

const handleTabChange = (n) => {
  console.log(`🔄 Switching to passenger ${n}, current is ${activeIndex.value}`);
  
  if (n > activeIndex.value) {
    const isCurrentComplete = isPassengerComplete(activeIndex.value);
    console.log(`📊 Current passenger ${activeIndex.value} complete? ${isCurrentComplete}`);
    
    if (isCurrentComplete) {
      activeIndex.value = n;
    } else {
      showValidation.value = true;
      nextTick(() => {
        const formElement = document.querySelector('.pal-card');
        if (formElement) {
          formElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
      
      const passengerType = getPassengerType(activeIndex.value);
      if (passengerType === 'Infant' && !infantAdultMapping.value[`pax_${activeIndex.value}`]) {
        notificationStore.warn(`Please select which adult the infant will sit with for Passenger ${activeIndex.value} before continuing.`);
      } else {
        notificationStore.warn(`Please complete all required fields for Passenger ${activeIndex.value} before continuing.`);
      }
    }
  } else {
    activeIndex.value = n;
  }
};

const goToNextGuest = () => {
  if (validateCurrentTab()) {
    activeIndex.value++;
  }
};

const saveAllPassengersToStore = async () => {
  try {
    isSaving.value = true;
    
    // Validate all passengers first
    const incompletePassengers = [];
    for (let i = 1; i <= totalTravelers.value; i++) {
      if (!isPassengerComplete(i)) {
        incompletePassengers.push(i);
      }
    }
    
    if (incompletePassengers.length > 0) {
      throw new Error(`Passengers ${incompletePassengers.join(', ')} are incomplete`);
    }
    
    // Validate contact info
    if (!contact.firstName.trim() || !contact.lastName.trim()) {
      throw new Error('Contact name is required');
    }
    
    if (!isValidEmail(contact.email)) {
      throw new Error('Valid email is required');
    }
    
    if (!isValidPhone(contact.phone)) {
      throw new Error('Valid phone number is required');
    }
    
    // Validate infant assignments
    if (infantCount.value > 0) {
      const infants = passengers.value.filter(p => p.type === 'Infant');
      const unassignedInfants = infants.filter(infant => !infantAdultMapping.value[infant.key]);
      
      if (unassignedInfants.length > 0) {
        throw new Error(`${unassignedInfants.length} infant(s) do not have an adult assigned`);
      }
      
      // Check if any adult has more than 1 infant
      const adultInfantCount = {};
      Object.values(infantAdultMapping.value).forEach(adultKey => {
        adultInfantCount[adultKey] = (adultInfantCount[adultKey] || 0) + 1;
      });
      
      const adultsWithMultipleInfants = Object.entries(adultInfantCount)
        .filter(([_, count]) => count > 1)
        .map(([adultKey]) => adultKey.replace('pax_', ''));
      
      if (adultsWithMultipleInfants.length > 0) {
        throw new Error(`Adult(s) ${adultsWithMultipleInfants.join(', ')} cannot have more than 1 infant`);
      }
    }
    
    // Ensure all passengers have complete data
    const validatedPassengers = passengers.value.map(passenger => {
      const passengerData = {
        ...passenger,
        title: passenger.title || '',
        nationality: passenger.nationality || 'Philippines'
      };
      
      // Add associated adult for infants
      if (passenger.type === 'Infant' && infantAdultMapping.value[passenger.key]) {
        passengerData.associatedAdult = infantAdultMapping.value[passenger.key].replace('pax_', '');
      }
      
      return passengerData;
    });
    
    // Save to Pinia store
    console.log('💾 Saving all passengers to store:', validatedPassengers);
    bookingStore.setPassengers(validatedPassengers);
    
    // Save infant-adult mappings to store
    bookingStore.infantAdultMapping = infantAdultMapping.value;
    
    // Save contact info
    console.log('💾 Saving contact info to store:', contact);
    bookingStore.setContactInfo({
      ...contact,
      title: contact.title || ''
    });
    
    // Verify save was successful
    console.log('✅ Store after save:', {
      passengers: bookingStore.passengers,
      contactInfo: bookingStore.contactInfo,
      infantAdultMapping: bookingStore.infantAdultMapping
    });
    
    return true;
  } catch (error) {
    console.error('❌ Error saving passengers:', error);
    // Let global axios interceptor handle user feedback
    return false;
  } finally {
    isSaving.value = false;
  }
};

const handleContinueToAddons = async () => {
  showValidation.value = true;
  
  // Check all passengers are complete
  const incompletePassengers = [];
  for (let i = 1; i <= totalTravelers.value; i++) {
    if (!isPassengerComplete(i)) {
      incompletePassengers.push(i);
    }
  }
  
  if (incompletePassengers.length > 0) {
    notificationStore.warn(`Passengers ${incompletePassengers.join(', ')} information is incomplete. Please complete all required fields.`);
    
    activeIndex.value = incompletePassengers[0];
    
    nextTick(() => {
      const formElement = document.querySelector('.pal-card');
      if (formElement) {
        formElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
    
    return;
  }

  // Validate infant assignments
  if (infantCount.value > 0) {
    const infants = passengers.value.filter(p => p.type === 'Infant');
    const unassignedInfants = infants.filter(infant => {
      const hasAdult = infantAdultMapping.value[infant.key] || infant.associatedAdult;
      return !hasAdult;
    });
    
    if (unassignedInfants.length > 0) {
      const infantNumbers = unassignedInfants.map(infant => 
        parseInt(infant.key.replace('pax_', ''))
      );
      notificationStore.warn(`Infant(s) ${infantNumbers.join(', ')} must be assigned to an adult before continuing.`);
      
      activeIndex.value = infantNumbers[0];
      
      nextTick(() => {
        const formElement = document.querySelector('.pal-card');
        if (formElement) {
          formElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
      
      return;
    }
    
    // Check if any adult has more than 1 infant
    const adultInfantCount = {};
    Object.values(infantAdultMapping.value).forEach(adultKey => {
      adultInfantCount[adultKey] = (adultInfantCount[adultKey] || 0) + 1;
    });
    
    const adultsWithMultipleInfants = Object.entries(adultInfantCount)
      .filter(([_, count]) => count > 1)
      .map(([adultKey]) => adultKey.replace('pax_', ''));
    
    if (adultsWithMultipleInfants.length > 0) {
      notificationStore.warn(`Adult(s) ${adultsWithMultipleInfants.join(', ')} cannot have more than 1 infant. Please reassign infants.`);
      return;
    }
  }

  // Validate contact info
  if (!contact.firstName.trim() || !contact.lastName.trim()) {
    notificationStore.warn("Please provide your first and last name.");
    return;
  }
  
  if (!isValidEmail(contact.email)) {
    notificationStore.warn("Please provide a valid email address.");
    return;
  }
  
  if (!isValidPhone(contact.phone)) {
    notificationStore.warn("Please provide a valid phone number (minimum 7 digits).");
    return;
  }

  if (!contact.title) {
    contact.title = '';
  }

  // Final validation
  if (passengers.value.length === 0) {
    notificationStore.warn('No passenger data found. Please fill in all passenger details.');
    return;
  }
  
  // Save all data to store
  const saveSuccess = await saveAllPassengersToStore();
  
  if (!saveSuccess) {
    return;
  }

  // CREATE DRAFT ON SERVER (Phase 11: Data Resilience)
  // We do this in the background/async, but wait just enough to ensure it's ongoing
  bookingStore.snapshotToServer();
  
  // Add a small delay for visual feedback
  setTimeout(() => {
    // Navigate to Add-ons
    router.push({ name: 'Addons' });
  }, 500);
};

// Auto-save contact info changes to store
watch(contact, (newContact) => {
  bookingStore.setContactInfo({
    firstName: newContact.firstName,
    lastName: newContact.lastName,
    email: newContact.email,
    phone: newContact.phone
  });
}, { deep: true });

// Watch for adult passenger updates to refresh infant displays
watch(adultPassengers, () => {
  const infants = passengers.value.filter(p => p.type === 'Infant');
  infants.forEach(infant => {
    const infantData = passengers.value.find(p => p.key === infant.key);
    if (infantData) {
      infantData._refresh = Date.now();
    }
  });
});

// Watch for infant adult mapping changes to update validation
watch(infantAdultMapping, () => {
  passengers.value.forEach(passenger => {
    if (passenger.type === 'Infant') {
      const index = parseInt(passenger.key.replace('pax_', ''));
      const isValid = isPassengerComplete(index);
      passengerValidation.value[passenger.key] = isValid;
    }
  });
}, { deep: true });

onMounted(() => {
  console.log('🔄 PassengerDetailsView mounted');
  
  // Check session
  const session = bookingStore.checkSession();
  if (!session.valid) {
    console.log('⚠️ Session invalid, starting fresh');
  } else {
    console.log('✅ Session valid, expires:', session.expiresAt);
  }
  
  // Load passengers from store if session is valid
  if (session.valid && bookingStore.passengers.length > 0) {
    passengers.value = [...bookingStore.passengers];
    console.log('📥 Loaded passengers from store:', passengers.value);
    
    // Load infant-adult mappings from store
    if (bookingStore.infantAdultMapping) {
      infantAdultMapping.value = { ...bookingStore.infantAdultMapping };
      console.log('📥 Loaded infant-adult mappings from store:', infantAdultMapping.value);
    }
    
    // Initialize validation state
    passengers.value.forEach(passenger => {
      const index = passenger.key.replace('pax_', '');
      const isValid = isPassengerComplete(parseInt(index));
      passengerValidation.value[passenger.key] = isValid;
      console.log(`📋 Initial validation for passenger ${index}: ${isValid ? '✅ Valid' : '❌ Invalid'}`);
    });
  } else {
    console.log('📝 No saved passengers in store or session invalid');
  }
  
  // Load contact info from store
  if (bookingStore.contactInfo.email) {
    console.log('📥 Loaded contact info from store:', bookingStore.contactInfo);
  }
  
  // Find first incomplete passenger to focus on
  for (let i = 1; i <= totalTravelers.value; i++) {
    if (!isPassengerComplete(i)) {
      activeIndex.value = i;
      console.log(`🎯 Focusing on first incomplete passenger: ${i}`);
      break;
    }
  }
  
  // Log initial completion status
  console.log(`📊 Initial completion: ${completedPassengersCount.value}/${totalTravelers.value} complete`);
});
</script>

<style scoped>
/* Base Styles */
.minimal-container {
  min-height: 100vh;
  background: #fafafa;
  padding: 40px 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.minimal-layout {
  max-width: 1500px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 10px;
  padding: 0 20px;
}

/* Main Content - Contains both passenger sidebar and forms */
.main-content {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 30px;
  align-items: start;
}

/* Left Sidebar - Passenger Selection (Inside main-content) */
.passenger-sidebar {
  position: sticky;
  top: 40px;
  height: fit-content;
}

.sidebar-card {
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e5e5;
  overflow: hidden;
}

.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid #e5e5e5;
}

.sidebar-title {
  font-size: 16px;
  font-weight: 600;
  color: #111;
  margin: 0 0 8px 0;
}

.passenger-count {
  font-size: 11px;
  color: #666;
}

/* Passenger List */
.passenger-list {
  padding: 16px 0;
}

.passenger-item {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  position: relative;
}

.passenger-item:hover {
  background: #f9f9f9;
}

.passenger-item.active {
  background: #fff5f7;
  border-left-color: #FF579A;
}

.passenger-item.complete {
  border-left-color: #10B981;
}

.passenger-item.error {
  border-left-color: #ef4444;
}

.passenger-item.infant {
  border-left-color: #FFB347;
}

.passenger-item.infant.active {
  border-left-color: #FF8C00;
  background: #FFF8F0;
}

.item-number {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e5e5e5;
  border-radius: 50%;
  font-size: 14px;
  font-weight: 600;
  margin-right: 16px;
  flex-shrink: 0;
}

.passenger-item.active .item-number {
  background: #FF579A;
  color: white;
}

.passenger-item.complete .item-number {
  background: #10B981;
  color: white;
}

.passenger-item.error .item-number {
  background: #ef4444;
  color: white;
}

.passenger-item.infant .item-number {
  background: #FFB347;
  color: white;
}

.passenger-item.infant.active .item-number {
  background: #FF8C00;
  color: white;
}

.item-info {
  flex: 1;
}

.item-type {
  font-size: 15px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.passenger-item.active .item-type {
  color: #FF579A;
  font-weight: 600;
}

.passenger-item.infant .item-type {
  color: #FF8C00;
}

.infant-badge {
  font-size: 11px;
  color: #666;
  font-weight: normal;
  margin-left: 8px;
  background: #FFF3CD;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
}

.item-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10B981;
}

.status-dot.incomplete {
  background: #9ca3af;
}

.status-dot.error {
  background: #ef4444;
}

.item-arrow {
  color: #9ca3af;
  font-size: 18px;
  font-weight: 300;
}

.passenger-item.active .item-arrow {
  color: #FF579A;
}

.passenger-item.infant.active .item-arrow {
  color: #FF8C00;
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 20px 24px;
  border-top: 1px solid #e5e5e5;
  background: #f9f9f9;
}

.completion-status {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.completion-text {
  font-size: 9px;
  color: #666;
  text-align: center;
}

.completion-bar {
  height: 6px;
  background: #e5e5e5;
  border-radius: 3px;
  overflow: hidden;
}

.completion-fill {
  height: 100%;
  background: #10B981;
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* Infant Status */
.infant-status {
  padding-top: 12px;
  border-top: 1px solid #e5e5e5;
}

.infant-status-text {
  font-size: 11px;
  text-align: center;
}

.infant-warning {
  color: #ef4444;
  font-weight: 500;
}

/* Forms Content Area */
.forms-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #111;
  margin: 0 0 4px 0;
}

.step-counter {
  font-size: 14px;
  color: #666;
}

.current-passenger {
  text-align: right;
}

.current-label {
  display: block;
  font-size: 11px;
  color: #666;
  margin-bottom: 4px;
}

.current-info {
  font-size: 16px;
  font-weight: 600;
  color: #FF579A;
}

.infant-assignment {
  font-size: 14px;
  font-weight: normal;
  color: #666;
  margin-left: 8px;
}

/* Form Container */
.form-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* Form Sections */
.form-section {
  margin: 2px;
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #bfbfbf;
}

.form-title {
  font-size: 18px;
  font-weight: 600;
  color: #111;
  margin: 0 0 8px 0;
}

.form-subtitle {
  font-size: 11px;
  color: #666;
  margin: 0 0 24px 0;
}

/* Forms Wrapper */
.forms-wrapper {
  margin-bottom: 30px;
}

/* Special Requests */
.requests-section {
  padding-top: 24px;
  border-top: 1px solid #eee;
}

.requests-title {
  font-size: 16px;
  font-weight: 600;
  color: #111;
  margin-bottom: 16px;
}

.request-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
}

.option-checkbox {
  width: 16px;
  height: 16px;
  accent-color: #FF579A;
  cursor: pointer;
}

/* Contact Information */
.contact-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.contact-grid.second-row {
  grid-template-columns: repeat(2, 1fr);
  margin-bottom: 0;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  display: flex;
  align-items: center;
  gap: 4px;
}

.required {
  color: #FF579A;
}

.input-field {
  padding: 12px 16px;
  border: 1px solid #5f5f5f;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
  background: white;
}

.input-field.error {
  border-color: #ef4444;
  background-color: #fef2f2;
}

.input-field::placeholder {
  color: #999;
}

.field-error {
  color: #ef4444;
  font-size: 0.8rem;
  margin-top: 4px;
  display: flex;
  align-items: center;
}

.field-error:before {
  margin-right: 5px;
  font-size: 0.7rem;
}

.phone-wrapper {
  display: flex;
  border: 1px solid #ddd;
  border-radius: 6px;
  overflow: hidden;
}

.country-code {
  padding: 12px 16px;
  background: #f5f5f5;
  border-right: 1px solid #ddd;
  font-size: 14px;
  color: #666;
  flex-shrink: 0;
}

.phone-field {
  flex: 1;
  border: none;
  border-radius: 0;
  min-width: 0;
}

.phone-field.error {
  border: none;
  background-color: #fef2f2;
}

/* Navigation */
.navigation-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 0;
  border-top: 1px solid #eee;
}

.nav-buttons {
  display: flex;
  gap: 12px;
}

.nav-button {
  padding: 12px 20px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-button:hover {
  border-color: #ccc;
  color: #333;
}

.next-button {
  border-color: #FF579A;
  color: #FF579A;
}

.next-button:hover {
  background: #FF579A;
  color: white;
}

.continue-button {
  padding: 14px 30px;
  background: #FF579A;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.continue-button:hover:not(:disabled) {
  background: #ff4081;
}

.continue-button:disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.7;
}

/* Right Sidebar - Booking Summary */
.summary-sidebar {
  position: sticky;
  top: 40px;
  height: fit-content;
}

.summary-card {
  background: white;
  border-radius: 5px;
  border: 1px solid #e5e5e5;
  overflow: hidden;
}

.summary-header {
  padding: 20px 24px;
  background: #e5e5e5;
  border-bottom: 1px solid #e5e5e5;
}

.summary-title {
  font-size: 16px;
  font-weight: 600;
  color: #111;
  margin: 0;
}

/* Summary Sections */
.summary-section {
  padding: 24px;
  border-bottom: 1px solid #eee;
}

.summary-section:last-child {
  border-bottom: none;
}

/* Flight Summary */
.flight-summary {
  padding-bottom: 20px;
  margin-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.flight-summary:last-child {
  padding-bottom: 0;
  margin-bottom: 0;
  border-bottom: none;
}

.flight-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.flight-label {
  font-size: 11px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.flight-price {
  font-size: 14px;
  font-weight: 600;
  color: #FF579A;
}

.route {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.city {
  font-size: 14px;
  font-weight: 600;
  color: #111;
}

.arrow {
  color: #999;
  font-size: 12px;
}

.flight-date {
  font-size: 13px;
  color: #666;
}

/* Travelers Breakdown */
.travelers-breakdown {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.breakdown-label {
  font-size: 14px;
  color: #333;
}

.breakdown-price {
  font-size: 14px;
  font-weight: 600;
  color: #111;
}

.infant-note {
  margin-top: 12px;
  padding: 8px;
  background: #FFF3CD;
  border-radius: 2px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.note-icon {
  font-size: 12px;
}

.note-text {
  font-size: 11px;
  color: #856404;
}

/* Total Section */
.total-section {
  padding: 24px;
  background: #ededed;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.total-label {
  font-size: 14px;
  font-weight: 600;
  color: #111;
}

.total-amount {
  font-size: 24px;
  font-weight: 700;
  color: #FF579A;
}

.tax-note {
  font-size: 11px;
  color: #666;
  text-align: right;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .minimal-layout {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  
  .main-content {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  
  .summary-sidebar {
    position: static;
  }
  
  .passenger-sidebar {
    position: static;
  }
}

@media (max-width: 1024px) {
  .minimal-layout {
    padding: 0 20px;
  }
  
  .passenger-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
    padding: 20px;
  }
  
  .passenger-item {
    flex-direction: column;
    text-align: center;
    padding: 16px;
  }
  
  .item-number {
    margin-right: 0;
    margin-bottom: 12px;
  }
  
  .item-arrow {
    display: none;
  }
  
  .contact-grid,
  .contact-grid.second-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
}

@media (max-width: 768px) {
  .contact-grid,
  .contact-grid.second-row {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .phone-wrapper {
    flex-direction: column;
    border: none;
    gap: 8px;
  }
  
  .country-code {
    border: 1px solid #ddd;
    border-radius: 6px;
    border-right: 1px solid #ddd;
  }
  
  .phone-field {
    border: 1px solid #ddd;
    border-radius: 6px;
  }
  
  .navigation-section {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .nav-buttons {
    order: 2;
  }
  
  .continue-button {
    order: 1;
    width: 100%;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .current-passenger {
    text-align: left;
  }
  
  .form-section {
    padding: 24px;
  }
  
  .summary-section {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .minimal-container {
    padding: 20px 0;
  }
  
  .minimal-layout {
    padding: 0 15px;
  }
  
  .sidebar-header,
  .summary-header {
    padding: 20px;
  }
  
  .infant-badge {
    margin-left: 0;
    margin-top: 4px;
  }
}
</style>