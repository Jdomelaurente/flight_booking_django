<template>
  <div class="pal-card">
    <div class="pal-card-header">
      PASSENGER {{ index }} - {{ type }}
      <span v-if="type === 'Infant'" class="infant-tag">(Sits on adult's lap)</span>
    </div>
    <div class="pal-card-body">
      <div class="form-row">
        <div class="field col-1">
          <label>Title</label>
          <select v-model="form.title" @change="emitData" required :class="{ 'error-border': showErrors && !form.title }">
            <option value="">Title</option>
            <option value="MR">Mr.</option>
            <option value="MS">Ms.</option>
            <option value="MRS">Mrs.</option>
          </select>
          <span v-if="showErrors && !form.title" class="small-error">Title is required</span>
        </div>
        <div class="field col-3">
          <label>First Name <span class="required">*</span></label>
          <input v-model="form.firstName" type="text" placeholder="First Name" 
                 @input="handleNameInput('firstName')" 
                 :class="{ 'error-border': showErrors && !isNameValid(form.firstName) }"
                 required>
          <span v-if="showErrors && !form.firstName.trim()" class="small-error">First name is required</span>
          <span v-else-if="showErrors && !isNameValid(form.firstName)" class="small-error">Letters, spaces, and hyphens only</span>
        </div>
        <div class="field col-1">
          <label>M.I.</label>
          <input v-model="form.middleInitial" type="text" maxlength="1" @input="debounceEmit">
        </div>
        <div class="field col-3">
          <label>Last Name <span class="required">*</span></label>
          <input v-model="form.lastName" type="text" placeholder="Last Name" 
                 @input="handleNameInput('lastName')" 
                 :class="{ 'error-border': showErrors && !isNameValid(form.lastName) }"
                 required>
          <span v-if="showErrors && !form.lastName.trim()" class="small-error">Last name is required</span>
          <span v-else-if="showErrors && !isNameValid(form.lastName)" class="small-error">Letters, spaces, and hyphens only</span>
        </div>
      </div>

      <label class="section-label">Date of Birth <span class="required">*</span></label>
      <div class="form-row">
        <div class="field">
          <select v-model="form.dobDay" @change="emitData" required>
            <option value="">Day</option>
            <option v-for="d in 31" :key="d" :value="d">{{ d }}</option>
          </select>
        </div>
        <div class="field">
          <select v-model="form.dobMonth" @change="emitData" required>
            <option value="">Month</option>
            <option v-for="(m, i) in months" :key="i" :value="i+1">{{ m }}</option>
          </select>
        </div>
        <div class="field">
          <input v-model="form.dobYear" type="number" placeholder="Year (YYYY)" min="1900" 
                :max="new Date().getFullYear()" @input="debounceEmit" 
                :class="{ 'error-border': showErrors && !isDOBValid }"
                required>
        </div>
      </div>
      <span v-if="showErrors && !isDOBValid" class="small-error">Date of birth is required</span>

      <!-- Age Display -->
      <div v-if="form.dobDay && form.dobMonth && form.dobYear" class="age-display">
        Age: {{ calculatedAge }} years old
        <span v-if="showAgeWarning" class="age-warning">
          Age indicates this should be a {{ correctPassengerType }}
        </span>
      </div>

      <div class="form-row mt-3">
        <div class="field col-2">
          <label>Nationality</label>
          <select v-model="form.nationality" @change="emitData" :class="{ 'error-border': showErrors && !form.nationality }">
            <option value="">Select Nationality</option>
            <option value="Philippines">Philippines</option>
            <option value="United States">United States</option>
            <option value="Canada">Canada</option>
            <option value="Japan">Japan</option>
            <option value="South Korea">South Korea</option>
            <option value="Singapore">Singapore</option>
            <option value="Australia">Australia</option>
            <option value="United Kingdom">United Kingdom</option>
          </select>
          <span v-if="showErrors && !form.nationality" class="small-error">Nationality is required</span>
        </div>
        <div class="field col-2">
          <label>Passport Number</label>
          <input v-model="form.passport" type="text" placeholder="Passport No." @input="debounceEmit">
        </div>
      </div>

      <!-- INFANT ONLY: Adult Seat Assignment -->
      <div v-if="type === 'Infant'" class="infant-section">
        <label class="section-label">Select Adult to sit with <span class="required">*</span></label>
        <p class="section-note">This infant will sit on the selected adult's lap during the flight.</p>
        
        <div v-if="adultOptions && adultOptions.length > 0" class="adult-options">
          <div 
            v-for="adult in adultOptions" 
            :key="adult.key"
            :class="['adult-option', { 
              selected: form.associatedAdult === adult.number,
              unavailable: adult.alreadyHasInfant && adult.number !== form.associatedAdult
            }]"
            @click="selectAdult(adult)"
          >
            <div class="adult-info">
              <div class="adult-details">
                <div class="adult-name">{{ adult.name }}</div>
                <div class="adult-number">Adult {{ adult.number }}</div>
              </div>
              <div class="adult-status">
                <span v-if="adult.isCurrent" class="status-selected">Selected</span>
                <span v-else-if="adult.alreadyHasInfant" class="status-unavailable">
                  Already has infant
                </span>
                <span v-else class="status-available">Available</span>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="no-adults-message">
          <span>No adult passengers found. Please complete adult information first.</span>
        </div>
        <span v-if="showErrors && type === 'Infant' && !form.associatedAdult" class="small-error">Please select which adult this infant will sit with</span>
      </div>

      <!-- Validation error messages removed to be placed below inputs -->
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
    associatedAdult: null
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
  
  return basicValid;
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
  if (props.type === 'Infant' && form.associatedAdult) {
    const currentAdult = newAdults.find(a => a.number === form.associatedAdult);
    if (!currentAdult || currentAdult.alreadyHasInfant) {
      form.associatedAdult = null;
      emitData();
    }
  }
}, { deep: true });

watch(() => bookingStore.isSessionValid, (isValid) => {
  if (!isValid) {
    console.log(`Session invalid, resetting form for passenger ${props.index}`);
    resetForm();
  }
});

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
.pal-card { 
  background: white; 
  border: 1px solid #ddd; 
  border-radius: 2px; 
  margin-bottom: 15px; 
  box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
  position: relative;
}
.pal-card-header { 
  background: #f0f3f5; 
  padding: 12px 20px; 
  font-weight: 800; 
  color: #FF579A; 
  font-size: 0.85rem; 
  border-bottom: 1px solid #ddd; 
  display: flex;
  align-items: center;
  gap: 8px;
}
.infant-tag {
  font-size: 0.7rem;
  font-weight: normal;
  color: #666;
  background: #FFF3CD;
  padding: 2px 6px;
  border-radius: 2px;
}
.pal-card-body { 
  padding: 20px; 
}
.form-row { 
  display: flex; 
  gap: 7px; 
  margin-bottom: 7px; 
}
.section-label { 
  display: block; 
  font-size: 0.75rem; 
  font-weight: 700; 
  color: #555; 
  margin-bottom: 2px; 
  text-transform: uppercase; 
}
.section-note {
  font-size: 0.75rem;
  color: #666;
  margin: 4px 0 12px 0;
  font-style: italic;
}
.field { 
  display: flex; 
  flex-direction: column; 
  flex: 1; 
}
.col-1 { flex: 1; } 
.col-2 { flex: 2; } 
.col-3 { flex: 3; }
label { 
  font-size: 0.75rem; 
  font-weight: 700; 
  color: #555; 
  margin-bottom: 4px; 
  text-transform: uppercase; 
}
.required {
  color: #FF579A;
}
input, select { 
  border: 1px solid #ccc; 
  padding: 10px; 
  border-radius: 2px; 
  font-size: 0.9rem; 
  width: 100%;
  box-sizing: border-box;
}
input:focus, select:focus {
  border-color: #FF579A;
  outline: none;
}
input:invalid, select:invalid {
  border-color: #ef4444;
}
.mt-3 { 
  margin-top: 7px; 
}

/* Age Display */
.age-display {
  margin: 8px 0;
  font-size: 0.8rem;
  color: #666;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.age-warning {
  color: #ef4444;
  font-weight: 500;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Infant section */
.infant-section {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 5px;
  border: 1px solid #e9ecef;
}

.adult-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.adult-option {
  padding: 12px 15px;
  border: 2px solid #e9ecef;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.adult-option:hover:not(.unavailable) {
  border-color: #FF579A;
  background: #fff5f7;
}

.adult-option.selected {
  border-color: #FF579A;
  background: #fff5f7;
}

.adult-option.unavailable {
  opacity: 0.6;
  cursor: not-allowed;
  background: #f8f9fa;
}

.adult-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.adult-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.adult-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #333;
}

.adult-number {
  font-size: 0.75rem;
  color: #666;
}

.adult-status {
  font-size: 0.75rem;
  font-weight: 500;
}

.status-selected {
  color: #10B981;
}

.status-available {
  color: #666;
}

.status-unavailable {
  color: #ef4444;
}

.error-border {
  border-color: #ef4444 !important;
  background-color: #fef2f2;
}

.small-error {
  color: #ef4444;
  font-size: 0.7rem;
  margin-top: 4px;
  font-weight: 500;
  display: block;
}

.no-adults-message {
  padding: 12px;
  background: #fff3cd;
  border-radius: 2px;
  text-align: center;
  color: #856404;
  font-size: 0.8rem;
}

/* Validation styles */
.validation-errors {
  margin-top: 15px;
  padding: 12px;
  background-color: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 5px;
}

.error-message {
  color: #ef4444;
  font-size: 0.8rem;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
}

.error-message:before {
  margin-right: 6px;
  font-size: 0.7rem;
}

.error-message:last-child {
  margin-bottom: 0;
}
</style>