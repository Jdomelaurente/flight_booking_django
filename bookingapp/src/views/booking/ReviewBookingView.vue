<template>
  <div class="pal-bg">
    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading your booking details...</p>
    </div>

    <!-- No Data State -->
    <div v-else-if="!hasFlightData" class="no-data-message">
      <h3>No flight data found</h3>
      <p>Please go back and select a flight first.</p>
      <button @click="$router.push({ name: 'SearchFlights' })" class="btn-back">
        Back to Flight Search
      </button>
    </div>

    <!-- Main Content -->
    <div v-else class="container review-layout">
      <main class="main-content">
        <h2 class="page-title">Review Your Booking</h2>

        <section class="review-section">
          <div class="section-header">
            <span class="icon">✈️</span>
            <h3>Flight Details</h3>
            <span class="trip-type-badge" :class="{ 'round-trip': bookingStore.isRoundTrip, 'one-way': !bookingStore.isRoundTrip }">
              {{ bookingStore.isRoundTrip ? 'Round Trip' : 'One Way' }}
            </span>
          </div>
          <div class="review-card">
            <div class="flight-summary" v-if="bookingStore.selectedOutbound">
              <div class="route-info">
                <span class="badge">Depart</span>
                <strong>{{ bookingStore.selectedOutbound.origin }} → {{ bookingStore.selectedOutbound.destination }}</strong>
              </div>
              <div class="detail-grid">
                <div><small>Flight:</small> {{ bookingStore.selectedOutbound.flight_number }}</div>
                <div><small>Departure:</small> {{ formatDate(bookingStore.selectedOutbound.departure_time) }}</div>
                <div><small>Class:</small> {{ bookingStore.selectedOutbound.class_type || 'Economy' }}</div>
                <div><small>Price per person:</small> ₱{{ parseFloat(bookingStore.selectedOutbound.price).toLocaleString() }}</div>
              </div>
            </div>

            <div class="flight-summary mt-3" v-if="bookingStore.selectedReturn">
              <div class="route-info">
                <span class="badge return">Return</span>
                <strong>{{ bookingStore.selectedReturn.origin }} → {{ bookingStore.selectedReturn.destination }}</strong>
              </div>
              <div class="detail-grid">
                <div><small>Flight:</small> {{ bookingStore.selectedReturn.flight_number }}</div>
                <div><small>Departure:</small> {{ formatDate(bookingStore.selectedReturn.departure_time) }}</div>
                <div><small>Price per person:</small> ₱{{ parseFloat(bookingStore.selectedReturn.price).toLocaleString() }}</div>
              </div>
            </div>
          </div>
        </section>

        <section class="review-section">
          <div class="section-header">
            <span class="icon">👥</span>
            <h3>Passengers & Add-ons</h3>
          </div>
          
          <!-- Depart Flight Add-ons -->
          <div class="review-card" v-if="bookingStore.selectedOutbound">
            <div class="segment-header">
              <h4>Depart Flight Add-ons</h4>
              <span class="flight-badge">{{ bookingStore.selectedOutbound.flight_number }}</span>
            </div>
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
                  <td>
                    <strong>{{ p.title }} {{ p.firstName }} {{ p.lastName }}</strong>
                    <div class="sub-text">{{ p.type }}</div>
                  </td>
                  <td>{{ getSeatLabel(p.key) }}</td>
                  <td>{{ getBaggageLabel(p.key, 'depart') }}</td>
                  <td>{{ getMealLabel(p.key, 'depart') }}</td>
                  <td>{{ getAssistanceLabel(p.key, 'depart') }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Return Flight Add-ons (only for round trips) -->
          <div class="review-card mt-3" v-if="bookingStore.isRoundTrip && bookingStore.selectedReturn">
            <div class="segment-header">
              <h4>Return Flight Add-ons</h4>
              <span class="flight-badge return">{{ bookingStore.selectedReturn.flight_number }}</span>
            </div>
            <table class="review-table">
              <thead>
                <tr>
                  <th>Passenger</th>
                  <th>Baggage</th>
                  <th>Meal</th>
                  <th>Assistance</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in bookingStore.passengers" :key="p.key">
                  <td>
                    <strong>{{ p.title }} {{ p.firstName }} {{ p.lastName }}</strong>
                    <div class="sub-text">{{ p.type }}</div>
                  </td>
                  <td>{{ getBaggageLabel(p.key, 'return') }}</td>
                  <td>{{ getMealLabel(p.key, 'return') }}</td>
                  <td>{{ getAssistanceLabel(p.key, 'return') }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="review-section">
          <div class="section-header">
            <span class="icon">📧</span>
            <h3>Contact Information</h3>
          </div>
          <div class="review-card contact-grid">
            <div class="contact-item">
              <label>Full Name</label>
              <p>{{ bookingStore.contactInfo.title }} {{ bookingStore.contactInfo.firstName }} {{ bookingStore.contactInfo.lastName }}</p>
            </div>
            <div class="contact-item">
              <label>Email Address</label>
              <p>{{ bookingStore.contactInfo.email }}</p>
            </div>
            <div class="contact-item">
              <label>Phone Number</label>
              <p>{{ bookingStore.contactInfo.phone }}</p>
            </div>
          </div>
        </section>

        <div class="footer-nav">
          <button class="btn-back" @click="$router.back()">EDIT DETAILS</button>
          <button class="btn-continue" @click="confirmBooking" :disabled="isProcessing">
            <span v-if="isProcessing">Processing...</span>
            <span v-else>PROCEED TO PAYMENT</span>
          </button>
        </div>
      </main>

      <aside class="sidebar">
        <div class="summary-card sticky">
          <div class="summary-header">Payment Summary</div>
          <div class="summary-body" v-if="isCalculatingPrice">
            <div class="price-loading">
              <div class="loading-dots">
                <span></span><span></span><span></span>
              </div>
              <p>Verifying price with server...</p>
            </div>
          </div>
          <div class="summary-body" v-else>
            <!-- Flight Base Fares -->
            <div class="flight-base-summary" v-if="bookingStore.selectedOutbound">
              <div class="price-line">
                <span>Depart Flight ({{ payingPassengerCount }} Pax)</span>
                <span>₱{{ departBaseFare.toLocaleString() }}</span>
              </div>
              <div class="price-line" v-if="bookingStore.selectedReturn">
                <span>Return Flight ({{ payingPassengerCount }} Pax)</span>
                <span>₱{{ returnBaseFare.toLocaleString() }}</span>
              </div>
            </div>

            <!-- Add-ons -->
            <div class="addons-summary">
              <div class="price-line" v-if="totalSeatsPrice > 0">
                <span>Seat Selection</span>
                <span>₱{{ totalSeatsPrice.toLocaleString() }}</span>
              </div>
              <div class="price-line" v-if="totalBaggagePrice > 0">
                <span>Extra Baggage</span>
                <span>₱{{ totalBaggagePrice.toLocaleString() }}</span>
              </div>
              <div class="price-line" v-if="totalMealsPrice > 0">
                <span>Meal Selection</span>
                <span>₱{{ totalMealsPrice.toLocaleString() }}</span>
              </div>
              <div class="price-line" v-if="totalAssistancePrice > 0">
                <span>Special Assistance</span>
                <span>₱{{ totalAssistancePrice.toLocaleString() }}</span>
              </div>
            </div>

            <hr>
            <div class="total-row">
              <span>Grand Total</span>
              <span class="final-amt">₱{{ grandTotal.toLocaleString() }}</span>
            </div>
            <div class="passenger-count">
              <small>{{ payingPassengerCount }} paying passengers</small>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useRouter } from 'vue-router';
import { addonService } from '@/services/booking/addonService';
import { bookingService } from '@/services/booking/bookingService';
import { useNotificationStore } from '@/stores/notification';

const bookingStore = useBookingStore();
const router = useRouter();
const notificationStore = useNotificationStore();

const isLoading = ref(true);
const isProcessing = ref(false);
const baggageOptions = ref([]);
const mealOptions = ref([]);
const assistanceOptions = ref([]);

// Backend Price Data
const backendTotal = ref(null);
const backendBreakdown = ref(null);
const isCalculatingPrice = ref(false);

onMounted(async () => {
  try {

    bookingStore.loadBookingFromStorage();
    
    // Debug: Log current store state
    console.log('📊 ========== PINIA STORE STATE ==========');
    console.log('🎫 Trip Type:', bookingStore.tripType, '(Round Trip:', bookingStore.isRoundTrip + ')');
    console.log('📋 Booking ID:', bookingStore.booking_id);
    console.log('📋 Booking Reference:', bookingStore.booking_reference);
    console.log('📋 Booking Status:', bookingStore.booking_status);
    console.log('💰 Booking Total:', bookingStore.booking_total);
    // Debug: Log current store state
    console.log('📊 ========== PINIA STORE STATE ==========');
    console.log('🎫 Trip Type:', bookingStore.tripType, '(Round Trip:', bookingStore.isRoundTrip + ')');
    
    // Flight data
    console.log('✈️ Outbound Flight:', bookingStore.selectedOutbound);
    console.log('🔄 Return Flight:', bookingStore.selectedReturn);
    
    // Passenger data
    console.log('👥 Passenger Count:', bookingStore.passengerCount);
    console.log('📋 Passengers:', JSON.parse(JSON.stringify(bookingStore.passengers)));
    
    // Contact info
    console.log('📞 Contact Info:', JSON.parse(JSON.stringify(bookingStore.contactInfo)));
    
    // Add-ons (deep clone to avoid reactivity issues)
    console.log('🎯 Add-ons Structure:', JSON.parse(JSON.stringify(bookingStore.addons)));
    
    // Financial calculations
    console.log('💰 Financial Summary:');
    console.log('  - Combined Base Price:', bookingStore.combinedBasePrice);
    console.log('  - Total Add-ons Price:', bookingStore.totalAddonsPrice);
    console.log('  - Grand Total (computed):', bookingStore.grandTotal);
    console.log('  - Booking Total (stored):', bookingStore.booking_total);
    
    // Session info
    const sessionStatus = bookingStore.checkSession();
    console.log('⏰ Session Status:', sessionStatus);
    
    console.log('📊 ========== END PINIA STORE ==========');

    // Rest of your existing code...
    bookingStore.migrateAddonsToNewFormat();
    
    const airlineId = bookingStore.selectedOutbound?.airline_code || bookingStore.selectedOutbound?.airline;
    if (!airlineId) {
      isLoading.value = false;
      return;
    }

    const results = await Promise.allSettled([
      addonService.getBaggageOptions(airlineId),
      addonService.getMealOptions(airlineId),
      addonService.getAssistanceServices(airlineId)
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

    // Fetch backend-calculated price
    await fetchBackendPrice();

  } catch (error) {
    console.error("Review page data fetch error:", error);
  } finally {
    isLoading.value = false;
  }
});

const fetchBackendPrice = async () => {
  isCalculatingPrice.value = true;
  try {
    console.log('🔍 Fetching authoritative backend price...');
    const result = await bookingService.calculatePrice(bookingStore);
    if (result.success) {
      backendTotal.value = result.totalAmount;
      backendBreakdown.value = result.breakdown;
      console.log('✅ Backend price confirmed:', backendTotal.value);
    } else {
      console.warn('⚠️ Could not get backend price, falling back to store calculation:', result.error);
    }
  } catch (error) {
    console.error('❌ Error in fetchBackendPrice:', error);
  } finally {
    isCalculatingPrice.value = false;
  }
};

// Helper functions
const getItemById = (list, id) => {
  if (!id || !list) return null;
  return list.find(item => item.id === id);
};

const getOptionById = (list, id) => {
  if (!id || !list) return null;
  return list.find(item => item.id == id);
};

const getBaggageLabel = (passengerKey, segment = 'depart') => {
  const baggage = bookingStore.addons?.baggage?.[segment]?.[passengerKey];
  if (!baggage) return 'Standard (Free)';
  
  // Handle null or undefined baggage
  if (baggage === null || baggage === undefined) return 'Standard (Free)';
  
  if (typeof baggage === 'object' && baggage.formatted_weight) {
    return `${baggage.formatted_weight} (₱${parseFloat(baggage.price).toLocaleString()})`;
  }
  
  const option = baggageOptions.value.find(o => o.id == baggage);
  return option ? `${option.formatted_weight} (₱${parseFloat(option.price).toLocaleString()})` : 'Extra Baggage';
};

const getMealLabel = (passengerKey, segment = 'depart') => {
  const meal = bookingStore.addons?.meals?.[segment]?.[passengerKey];
  if (!meal) return 'No meal';
  
  if (typeof meal === 'object' && meal.name) {
    return meal.name;
  }
  
  const option = mealOptions.value.find(m => m.id == meal);
  return option ? option.name : 'Pre-ordered Meal';
};

const getAssistanceLabel = (passengerKey, segment = 'depart') => {
  const assistanceId = bookingStore.addons?.wheelchair?.[segment]?.[passengerKey];
  if (!assistanceId || !Array.isArray(assistanceOptions.value)) return 'No assistance';
  
  const option = assistanceOptions.value.find(a => a.id == assistanceId);
  return option ? option.name : 'Special Assistance';
};

const getSeatLabel = (passengerKey) => {
  const seat = bookingStore.addons?.seats?.[passengerKey];
  if (!seat) return 'Not selected';
  
  // Use seat_price instead of final_price
  const price = parseFloat(seat.seat_price) || 0;
  return `${seat.seat_code || 'N/A'} (₱${price.toLocaleString()})`;
};

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

// Computed Properties
const hasFlightData = computed(() => {
  const outbound = bookingStore.selectedOutbound;
  return !!outbound && typeof outbound === 'object' && 'price' in outbound;
});

const payingPassengerCount = computed(() => bookingStore.payingPassengerCount);
const departBaseFare = computed(() => bookingStore.departBaseFare);
const returnBaseFare = computed(() => bookingStore.returnBaseFare);
const totalSeatsPrice = computed(() => bookingStore.totalSeatsPrice);
const totalBaggagePrice = computed(() => bookingStore.totalBaggagePrice);
const totalMealsPrice = computed(() => bookingStore.totalMealsPrice);
const totalAssistancePrice = computed(() => bookingStore.totalAssistancePrice);

const grandTotal = computed(() => {
  // Prioritize backend-calculated total if available
  if (backendTotal.value !== null) return backendTotal.value;
  return bookingStore.calculatedGrandTotal;
});

// Validation function
const validateBooking = () => {
  const errors = [];
  
  if (!bookingStore.selectedOutbound) {
    errors.push('Please select an outbound flight');
  }
  
  if (bookingStore.isRoundTrip && !bookingStore.selectedReturn) {
    errors.push('Please select a return flight for round trip');
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
      type: p.type || 'Adult'
    };
  });
  
  console.log('✅ Prepared passengers:', preparedPassengers);
  return preparedPassengers;
};


const confirmBooking = async () => {
  isProcessing.value = true;
  
  try {
    // 1. Prepare data using your existing formatBookingData
    const bookingData = bookingService.formatBookingData(bookingStore);
    
    // 2. Check for an existing ID (from store or local storage)
    const existingBookingId = bookingStore.booking_id || 
                             JSON.parse(localStorage.getItem('current_booking'))?.id;

    let response;
    
    if (existingBookingId) {
      // SCENARIO: User went back from Add-ons/Review to change details
      console.log('🔄 Updating existing booking:', existingBookingId);
      response = await bookingService.updateBooking(existingBookingId, bookingData);
    } else {
      // SCENARIO: First time clicking "Confirm"
      console.log('🆕 Creating new booking...');
      response = await bookingService.createBooking(bookingData);
    }
    
    console.log('📊 FULL BOOKING RESPONSE:', response);
    
    if (response.success) {
      // 3. Save ALL booking data to the store using saveBookingConfirmation
      bookingStore.saveBookingConfirmation({
        booking_id: response.booking_id,
        booking_reference: response.booking_reference || `CSUCC${String(response.booking_id).padStart(8, '0')}`,
        status: response.status || 'pending',
        total_amount: response.total_amount || bookingStore.grandTotal
      });
      
      // 4. Also set individual fields (for backward compatibility)
      bookingStore.setBookingId(response.booking_id);
      bookingStore.booking_reference = response.booking_reference || `CSUCC${String(response.booking_id).padStart(8, '0')}`;
      bookingStore.booking_status = response.status || 'pending';
      
      // 5. Persist to LocalStorage so a page refresh doesn't lose the ID
      localStorage.setItem('current_booking', JSON.stringify({
        id: response.booking_id,
        reference: response.booking_reference || `CSUCC${String(response.booking_id).padStart(8, '0')}`,
        total: response.total_amount || bookingStore.grandTotal,
        status: response.status || 'pending'
      }));
      
      console.log('✅ Booking saved to store:', {
        id: bookingStore.booking_id,
        reference: bookingStore.booking_reference,
        status: bookingStore.booking_status,
        total: bookingStore.booking_total
      });
      
      // 6. Move to Payment
      router.push({ 
        name: 'Payment', 
        query: { 
          bookingId: response.booking_id,
          bookingReference: response.booking_reference || `CSUCC${String(response.booking_id).padStart(8, '0')}`
        } 
      });
    } else {
      notificationStore.error(`Booking Error: ${response.error}`);
    }
  } catch (error) {
    console.error("Booking critical failure:", error);
    notificationStore.error("An unexpected error occurred. Please try again.");
  } finally {
    isProcessing.value = false;
  }
};

/**
 * Extracted error handler to keep confirmBooking clean
 */
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
.pal-bg { 
  background: #f4f7f9; 
  min-height: 100vh; 
  padding: 40px 0; 
}

.review-layout { 
  display: grid; 
  grid-template-columns: 1fr 350px; 
  gap: 30px; 
  max-width: 1100px; 
  margin: 0 auto; 
}

.page-title { 
  color: #003870; 
  font-weight: 800; 
  margin-bottom: 25px; 
  font-size: 1.8rem;
}

.review-section { 
  margin-bottom: 30px; 
}

.section-header { 
  display: flex; 
  align-items: center; 
  gap: 10px; 
  margin-bottom: 15px; 
}

.section-header h3 { 
  color: #003870; 
  margin: 0; 
  font-size: 1.2rem; 
}

.review-card { 
  background: white; 
  border-radius: 12px; 
  padding: 25px; 
  box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
  border: 1px solid #eee; 
}

.review-card.no-padding { 
  padding: 0; 
  overflow: hidden; 
}

.badge { 
  background: #003870; 
  color: white; 
  padding: 2px 8px; 
  border-radius: 4px; 
  font-size: 0.7rem; 
  text-transform: uppercase; 
  margin-right: 10px; 
}

.badge.return { 
  background: #d11241; 
}

.flight-summary { 
  padding-bottom: 15px; 
}

.detail-grid { 
  display: grid; 
  grid-template-columns: repeat(3, 1fr); 
  margin-top: 10px; 
  color: #555; 
}

.review-table { 
  width: 100%; 
  border-collapse: collapse; 
}

.review-table th { 
  background: #f8f9fa; 
  text-align: left; 
  padding: 12px 20px; 
  font-size: 0.85rem; 
  color: #666; 
}

.review-table td { 
  padding: 15px 20px; 
  border-top: 1px solid #eee; 
  font-size: 0.95rem; 
}

.sub-text { 
  font-size: 0.75rem; 
  color: #888; 
}

.contact-grid { 
  display: grid; 
  grid-template-columns: repeat(3, 1fr); 
  gap: 20px; 
}

.contact-item label { 
  display: block; 
  font-size: 0.75rem; 
  color: #888; 
  text-transform: uppercase; 
}

.contact-item p { 
  margin: 5px 0 0; 
  font-weight: 600; 
  color: #333; 
}

/* Sticky Sidebar */
.summary-card { 
  background: white; 
  border-radius: 12px; 
  box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
}

.sticky { 
  position: sticky; 
  top: 20px; 
}

.summary-header { 
  background: #003870; 
  color: white; 
  padding: 20px; 
  text-align: center; 
  font-weight: 700; 
  border-radius: 12px 12px 0 0; 
}

.summary-body { 
  padding: 20px; 
}

.price-line { 
  display: flex; 
  justify-content: space-between; 
  margin-bottom: 10px; 
  font-size: 0.9rem; 
}

.total-row { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-top: 15px; 
  font-weight: 700; 
}

.final-amt { 
  color: #d11241; 
  font-size: 1.4rem; 
}

.footer-nav { 
  display: flex; 
  justify-content: space-between; 
  margin-top: 30px; 
}

.btn-back { 
  padding: 12px 25px; 
  border: 1px solid #ccc; 
  background: white; 
  border-radius: 6px; 
  cursor: pointer; 
  font-weight: 600;
}

.btn-continue { 
  padding: 12px 40px; 
  background: #d11241; 
  color: white; 
  border: none; 
  border-radius: 6px; 
  font-weight: 700; 
  cursor: pointer; 
}

.btn-continue:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Loading and Error States */
.loading-state, .no-data-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
  padding: 40px;
}

.loading-state p {
  color: #666;
  font-size: 1.2rem;
  margin-top: 15px;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #003870;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-data-message {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  margin: 40px auto;
  padding: 40px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.no-data-message h3 {
  color: #003870;
  margin-bottom: 15px;
  font-size: 1.5rem;
}

.no-data-message p {
  color: #666;
  margin-bottom: 25px;
  font-size: 1rem;
}

.no-data-message .btn-back {
  background: #003870;
  color: white;
  border: none;
  padding: 12px 30px;
}

/* Responsive Styles */
@media (max-width: 768px) {
  .review-layout {
    grid-template-columns: 1fr;
  }
  
  .contact-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .footer-nav {
    flex-direction: column;
    gap: 10px;
  }
  
  .footer-nav button {
    width: 100%;
  }
  
  .review-table {
    display: block;
    overflow-x: auto;
  }
}

@media (max-width: 480px) {
  .pal-bg {
    padding: 20px 0;
  }
  
  .review-card {
    padding: 15px;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
}

.trip-type-badge {
  margin-left: auto;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.trip-type-badge.round-trip {
  background: #e3f2fd;
  color: #1565c0;
  border: 1px solid #1565c0;
}

.trip-type-badge.one-way {
  background: #f3e5f5;
  color: #7b1fa2;
  border: 1px solid #7b1fa2;
}

.segment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.segment-header h4 {
  margin: 0;
  color: #003870;
  font-size: 1.1rem;
}

.flight-badge {
  background: #003870;
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.flight-badge.return {
  background: #d11241;
}

.flight-base-summary {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #eee;
}

.flight-base-summary .price-line {
  font-size: 0.85rem;
  color: #666;
}

.addons-summary {
  margin-top: 10px;
}

.passenger-count {
  text-align: center;
  margin-top: 10px;
  color: #888;
  font-size: 0.85rem;
}

.mt-3 {
  margin-top: 15px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .segment-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .trip-type-badge {
    margin-left: 0;
    align-self: flex-start;
  }
}

/* Price Loading Styles */
.price-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 10px;
  text-align: center;
}

.price-loading p {
  margin-top: 15px;
  color: #666;
  font-size: 0.9rem;
  font-style: italic;
}

.loading-dots {
  display: flex;
  gap: 6px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background-color: #003870;
  border-radius: 50%;
  display: inline-block;
  animation: dot-pulse 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes dot-pulse {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
}
</style>