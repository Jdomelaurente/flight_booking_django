<template>
  <div class="pal-bg">
    <div class="container pal-layout">
      <main class="main-content">
        <div class="trip-type-header">
          <h2 class="page-title">Flight Add-ons</h2>
          <div class="trip-type-badge" :class="{ 'round-trip': bookingStore.isRoundTrip, 'one-way': !bookingStore.isRoundTrip }">
            {{ tripTypeInfo }}
          </div>
        </div>

        <!-- Show flight summary -->
        <div v-if="flightInfo.length > 0" class="flight-summary-card">
          <div class="flight-summary-header">
            <h3>Your Flights</h3>
          </div>
          <div class="flight-summary-body">
            <div v-for="flight in flightInfo" :key="flight.type" class="flight-item">
              <div class="flight-type">{{ flight.type }}</div>
              <div class="flight-details">
                <span class="flight-number">{{ flight.flight }}</span>
                <span class="flight-route">{{ flight.route }}</span>
              </div>
              <div class="flight-price">₱{{ flight.price.toLocaleString() }}</div>
            </div>
          </div>
        </div>

        <!-- Visual Roadmap Indicator -->
        <div v-if="segmentRoadmap.length > 1" class="visual-roadmap">
          <div v-for="(seg, idx) in segmentRoadmap" :key="seg.key" class="roadmap-item">
            <div class="roadmap-dot" :class="{ 'done': seg.isComplete, 'active': activeSegment === seg.key }">
              <span v-if="seg.isComplete">✅</span>
              <span v-else>{{ idx + 1 }}</span>
            </div>
            <div class="roadmap-info">
              <div class="roadmap-label">{{ seg.label }}</div>
              <div class="roadmap-status">
                <span :class="{ 'check-done': seg.baggageDone }">🧳</span>
                <span :class="{ 'check-done': seg.mealsDone }">🍱</span>
                <span :class="{ 'check-done': seg.seatsDone }">💺</span>
              </div>
            </div>
            <div v-if="idx < segmentRoadmap.length - 1" class="roadmap-connector"></div>
          </div>
        </div>

        <div class="square-tabs-container">
          <div class="square-tabs-grid">
            <div 
              @click="currentTab = 'baggage'"
              :class="['square-tab', { active: currentTab === 'baggage' }]"
            >
              <div class="tab-icon">🧳</div>
              <div class="tab-label">Baggage</div>
            </div>
            
            <div 
              @click="$router.push({ name: 'SeatSelection' })"
              :class="['square-tab seat-tab', { active: $route.name === 'SeatSelection' }]"
            >
              <div class="tab-icon">💺</div>
              <div class="tab-label">Seats</div>
            </div>
            
            <div 
              @click="currentTab = 'meals'"
              :class="['square-tab', { active: currentTab === 'meals' }]"
            >
              <div class="tab-icon">🍱</div>
              <div class="tab-label">Meals</div>
            </div>
            
            <div 
              @click="currentTab = 'wheelchair'"
              :class="['square-tab', { active: currentTab === 'wheelchair' }]"
            >
              <div class="tab-icon">♿</div>
              <div class="tab-label">Assistance</div>
            </div>
          </div>
          
          <div class="active-tab-indicator" :style="indicatorStyle"></div>
        </div>

        <div class="addon-workspace">
          <div v-if="isLoading" class="loading-state">
            <p>Fetching available services for your flight...</p>
          </div>

          <template v-else>
            <!-- Insurance Section (always visible above tabs content) -->
            <div class="tab-pane insurance-pane">
              <h3>Travel Insurance</h3>
              <p class="insurance-intro">
                Protect your trip with travel insurance. Covers medical emergencies, trip interruptions, and lost baggage.
              </p>
              <div v-if="insurancePlans && insurancePlans.length" class="insurance-grid">
                <div
                  v-for="plan in insurancePlans"
                  :key="plan.id"
                  class="insurance-card"
                  :class="{ selected: selectedInsurancePlanId === plan.id }"
                >
                  <div class="insurance-header">
                    <div>
                      <h4>{{ plan.name }}</h4>
                      <p class="insurance-provider">
                        Provided by {{ plan.provider_name || 'Our Insurance Partner' }}
                      </p>
                    </div>
                    <div class="insurance-price">
                      ₱{{ parseFloat(plan.retail_price).toLocaleString() }}
                    </div>
                  </div>

                  <p class="insurance-description">
                    {{ plan.description || 'Recommended coverage for medical, baggage, and trip interruptions.' }}
                  </p>

                  <p v-if="plan.coverage_summary" class="insurance-coverage">
                    {{ plan.coverage_summary }}
                  </p>

                  <div class="insurance-actions">
                    <button
                      v-if="selectedInsurancePlanId === plan.id"
                      class="insurance-toggle-btn remove"
                      @click="removeInsurance"
                    >
                      Remove
                    </button>
                    <button
                      v-else
                      class="insurance-toggle-btn"
                      @click="selectInsurance(plan)"
                    >
                      Add
                    </button>
                  </div>
                </div>
              </div>

              <p v-else class="insurance-unavailable">
                Travel insurance is not available for this itinerary.
              </p>
            </div>

            <!-- Baggage Tab - Card Layout -->
            <div v-if="currentTab === 'baggage'" class="tab-pane">
              <h3>Select Extra Baggage</h3>

              <div v-for="segment in flightSegments" :key="segment.key" class="segment-block">
                <div class="segment-notice">
                  <span class="notice-icon">
                    <span v-if="segment.key === 'depart'">✈️</span>
                    <span v-else-if="segment.key === 'return'">🔄</span>
                    <span v-else>📍</span>
                  </span>
                  <span><strong>{{ segment.label }}</strong> ({{ segment.flight }})</span>
                </div>
                
                <div v-for="p in bookingStore.passengers" :key="p.key" class="p-addon-row">
                  <div class="p-info">
                    <strong>{{ p.firstName }} {{ p.lastName }}</strong> ({{ p.type }})
                    
                    <button 
                      v-if="getBaggageSelection(p.key, segment.key) && segmentRoadmap.length > 1"
                      class="copy-addon-btn"
                      @click="handleCopyAddon('baggage', p)"
                      title="Copy this selection to all flights"
                    >
                      <span>🔄 Apply to all flights</span>
                    </button>
                  </div>
                  <div class="option-grid">
                    <div 
                      v-for="opt in baggageOptions" 
                      :key="opt.id"
                      :class="['opt-card', { selected: getBaggageSelection(p.key, segment.key)?.id === opt.id }]"
                      @click="selectBaggageDirect(p, opt, segment.key, $event)"
                    >
                      <span class="weight">{{ opt.formatted_weight }}</span>
                      <span class="price">₱{{ parseFloat(opt.price).toLocaleString() }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Meals Tab - Card Layout -->
            <div v-if="currentTab === 'meals'" class="tab-pane">
              <h3>Select In-flight Meals</h3>

              <div v-for="segment in flightSegments" :key="segment.key" class="segment-block">
                <div class="segment-notice">
                  <span class="notice-icon">
                    <span v-if="segment.key === 'depart'">✈️</span>
                    <span v-else-if="segment.key === 'return'">🔄</span>
                    <span v-else>📍</span>
                  </span>
                  <span><strong>{{ segment.label }}</strong> ({{ segment.flight }})</span>
                </div>
                
                <div v-for="p in bookingStore.passengers" :key="p.key" class="p-addon-row">
                  <div class="p-info"><strong>{{ p.firstName }} {{ p.lastName }}</strong> ({{ p.type }})
                    
                    <button 
                      v-if="getMealSelection(p.key, segment.key) && segmentRoadmap.length > 1"
                      class="copy-addon-btn"
                      @click="handleCopyAddon('meals', p)"
                      title="Copy this selection to all flights"
                    >
                      <span>🔄 Apply to all flights</span>
                    </button>
</div>
                  <div class="meal-options-grid">
                    <!-- No Meal Option -->
                    <div 
                      :class="['meal-card', { selected: !getMealSelection(p.key, segment.key) }]"
                      @click="selectMealDirect(p, null, segment.key, $event)"
                    >
                      <div class="meal-icon">🚫</div>
                      <div class="meal-details">
                        <div class="meal-name">No Meal</div>
                        <div class="meal-price">No additional cost</div>
                      </div>
                    </div>
                    
                    <!-- Meal Options -->
                    <div 
                      v-for="meal in mealOptions" 
                      :key="meal.id"
                      :class="['meal-card', { selected: getMealSelection(p.key, segment.key)?.id === meal.id }]"
                      @click="selectMealDirect(p, meal, segment.key, $event)"
                    >
                      <div class="meal-icon">
                        <span v-if="meal.meal_type === 'vegetarian'">🥬</span>
                        <span v-else-if="meal.meal_type === 'vegan'">🌱</span>
                        <span v-else-if="meal.meal_type === 'halal'">☪️</span>
                        <span v-else-if="meal.meal_type === 'kosher'">✡️</span>
                        <span v-else-if="meal.meal_type === 'child'">👶</span>
                        <span v-else-if="meal.meal_type === 'infant'">🍼</span>
                        <span v-else>🍽️</span>
                      </div>
                      <div class="meal-details">
                        <div class="meal-name">{{ meal.name }}</div>
                        <div class="meal-type">{{ meal.get_meal_type_display }}</div>
                        <div class="meal-description">{{ meal.description }}</div>
                        <div v-if="meal.calories" class="meal-calories">{{ meal.calories }} calories</div>
                        <div class="meal-price">₱{{ parseFloat(meal.price).toLocaleString() }}</div>
                      </div>
                      <div v-if="meal.allergens" class="meal-allergens">
                        <small>⚠️ Contains: {{ meal.allergens }}</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Assistance Tab - Card Layout -->
            <div v-if="currentTab === 'wheelchair'" class="tab-pane">
              <h3>Select Special Assistance</h3>

              <div v-for="segment in flightSegments" :key="segment.key" class="segment-block">
                <div class="segment-notice">
                  <span class="notice-icon">
                    <span v-if="segment.key === 'depart'">✈️</span>
                    <span v-else-if="segment.key === 'return'">🔄</span>
                    <span v-else>📍</span>
                  </span>
                  <span><strong>{{ segment.label }}</strong> ({{ segment.flight }})</span>
                </div>
                
                <div v-for="p in bookingStore.passengers" :key="p.key" class="p-addon-row">
                  <div class="p-info"><strong>{{ p.firstName }} {{ p.lastName }}</strong> ({{ p.type }})
                    
                    <button 
                      v-if="getAssistanceSelection(p.key, segment.key) && segmentRoadmap.length > 1"
                      class="copy-addon-btn"
                      @click="handleCopyAddon('wheelchair', p)"
                      title="Copy this selection to all flights"
                    >
                      <span>🔄 Apply to all flights</span>
                    </button>
</div>
                  <div class="assistance-options-grid">
                    <!-- No Assistance Option -->
                    <div 
                      :class="['assistance-card', { selected: !getAssistanceSelection(p.key, segment.key) }]"
                      @click="selectAssistanceDirect(p, null, segment.key, $event)"
                    >
                      <div class="assistance-icon">🚶</div>
                      <div class="assistance-details">
                        <div class="assistance-name">No Assistance Needed</div>
                        <div class="assistance-description">I can manage without special assistance</div>
                      </div>
                    </div>
                    
                    <!-- Assistance Options -->
                    <div 
                      v-for="service in assistanceOptions" 
                      :key="service.id"
                      :class="['assistance-card', { selected: getAssistanceSelection(p.key, segment.key) === service.id, free: service.price === 0 }]"
                      @click="selectAssistanceDirect(p, service, segment.key, $event)"
                    >
                      <div class="assistance-icon">
                        <span v-if="service.service_type === 'wheelchair'">♿</span>
                        <span v-else-if="service.service_type === 'boarding'">👵</span>
                        <span v-else-if="service.service_type === 'medical'">🏥</span>
                        <span v-else-if="service.service_type === 'unaccompanied_minor'">👦</span>
                        <span v-else-if="service.service_type === 'pet'">🐕</span>
                        <span v-else>🛂</span>
                      </div>
                      <div class="assistance-details">
                        <div class="assistance-name">{{ service.name }}</div>
                        <div class="assistance-type">{{ service.get_service_type_display }}</div>
                        <div class="assistance-description">{{ service.description }}</div>
                        <div class="assistance-notice">{{ service.advance_notice_text }}</div>
                        <div v-if="service.special_requirements" class="assistance-requirements">
                          <small>📋 {{ service.special_requirements }}</small>
                        </div>
                        <div class="assistance-price">
                          <span v-if="service.price > 0">₱{{ parseFloat(service.price).toLocaleString() }}</span>
                          <span v-else>Free service</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>

        <div class="footer-nav">
          <button class="btn-back" @click="$router.back()">BACK</button>
          <button class="btn-continue" @click="saveAndContinue">CONTINUE TO PAYMENT</button>
        </div>
      </main>

      <aside class="sidebar">
        <BookingTimer variant="sidebar" />
        <div class="summary-card sticky">
          <div class="summary-header">Price Breakdown</div>
          <div class="summary-body">
            <!-- Show flight breakdown -->
            <div v-if="flightInfo.length > 0" class="flight-breakdown">
              <!-- Adults Breakdown -->
              <div class="price-line" v-if="bookingStore.passengerCount.adults > 0">
                <span>{{ bookingStore.passengerCount.adults }} Adult(s) (Base Fare)</span> 
                <span>₱{{ (bookingStore.combinedBasePrice * bookingStore.passengerCount.adults).toLocaleString() }}</span>
              </div>
              
              <!-- Children Breakdown -->
              <div class="price-line" v-if="bookingStore.passengerCount.children > 0">
                <span>{{ bookingStore.passengerCount.children }} Child(ren) (Base Fare)</span> 
                <span>₱{{ (bookingStore.combinedBasePrice * bookingStore.passengerCount.children).toLocaleString() }}</span>
              </div>

              <!-- Infants Breakdown (50% Base Fare) -->
              <div class="price-line infant-line" v-if="bookingStore.passengerCount.infants > 0">
                <span>{{ bookingStore.passengerCount.infants }} Infant(s) (50% Base Fare)</span> 
                <span>₱{{ ((bookingStore.combinedBasePrice * 0.5) * bookingStore.passengerCount.infants).toLocaleString() }}</span>
              </div>

              <div class="price-line taxes-line">
                <span>Estimated Taxes & Fees (12%)</span>
                <span>₱{{ (bookingStore.totalTaxes).toLocaleString() }}</span>
              </div>
            </div>

            <div class="price-line" v-if="totalSeats > 0" id="sidebar-seats">
              <span>Seat Selection Fee</span> 
              <AnimatedNumber :value="totalSeats" prefix="₱" />
            </div>

            <div class="price-line" v-if="totalBaggage > 0" id="sidebar-baggage">
              <span>Baggage</span> 
              <AnimatedNumber :value="totalBaggage" prefix="₱" />
            </div>

            <div class="price-line" v-if="totalMeals > 0" id="sidebar-meals">
              <span>Meals</span> 
              <AnimatedNumber :value="totalMeals" prefix="₱" />
            </div>

            <div class="price-line" v-if="totalAssistance > 0" id="sidebar-assistance">
              <span>Assistance</span> 
              <AnimatedNumber :value="totalAssistance" prefix="₱" />
            </div>

            <div class="price-line" v-if="insurancePrice > 0" id="sidebar-insurance">
              <span>Travel Insurance</span> 
              <AnimatedNumber :value="insurancePrice" prefix="₱" />
            </div>

            <hr>

            <div class="total-row" id="sidebar-total">
              <span>Total</span> 
              <span class="final-amt">
                <AnimatedNumber :value="grandTotal" prefix="₱" />
              </span>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showConfirmationModal" class="modal-overlay" @click.self="closeConfirmationModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ modalTitle }}</h3>
          <button class="modal-close" @click="closeConfirmationModal">×</button>
        </div>
        
        <div class="modal-body">
          <div v-if="modalType === 'baggage'">
            <p><strong>Passenger:</strong> {{ modalData.passenger.firstName }} {{ modalData.passenger.lastName }} ({{ modalData.passenger.type }})</p>
            <p><strong>Flight:</strong> {{ activeSegmentLabel }}</p>
            <template v-if="modalData.option">
              <p><strong>Baggage:</strong> {{ modalData.option.formatted_weight }} Extra Baggage</p>
              <p><strong>Price:</strong> ₱{{ parseFloat(modalData.option.price).toLocaleString() }}</p>
              <p class="modal-note">This baggage will be added to your booking and cannot be changed after payment.</p>
            </template>
            <template v-else>
              <p><strong>Action:</strong> Remove Baggage Selection</p>
              <p class="modal-note warning">You are removing the selected baggage for this passenger. This action cannot be undone.</p>
            </template>
          </div>
          
          <div v-if="modalType === 'meal'">
            <p><strong>Passenger:</strong> {{ modalData.passenger.firstName }} {{ modalData.passenger.lastName }}</p>
            <p><strong>Flight:</strong> {{ modalData.segment === 'depart' ? 'Depart Flight' : 'Return Flight' }}</p>
            <template v-if="modalData.option">
              <p><strong>Meal:</strong> {{ modalData.option.name }}</p>
              <p><strong>Type:</strong> {{ modalData.option.get_meal_type_display }}</p>
              <p><strong>Description:</strong> {{ modalData.option.description }}</p>
              <p v-if="modalData.option.calories"><strong>Calories:</strong> {{ modalData.option.calories }}</p>
              <p v-if="modalData.option.allergens"><strong>Allergens:</strong> {{ modalData.option.allergens }}</p>
              <p><strong>Price:</strong> ₱{{ parseFloat(modalData.option.price).toLocaleString() }}</p>
              <p class="modal-note">Meals cannot be changed within 24 hours of departure.</p>
            </template>
            <template v-else>
              <p><strong>Action:</strong> No Meal Selected</p>
              <p class="modal-note">You are selecting no meal for this passenger.</p>
            </template>
          </div>
          
          <div v-else-if="modalType === 'assistance'">
            <p><strong>Passenger:</strong> {{ modalData.passenger.firstName }} {{ modalData.passenger.lastName }}</p>
            <p><strong>Flight:</strong> {{ modalData.segment === 'depart' ? 'Depart Flight' : 'Return Flight' }}</p>
            <template v-if="modalData.option">
              <p><strong>Service:</strong> {{ modalData.option.name }}</p>
              <p><strong>Type:</strong> {{ modalData.option.get_service_type_display }}</p>
              <p><strong>Description:</strong> {{ modalData.option.description }}</p>
              <p><strong>Notice Required:</strong> {{ modalData.option.advance_notice_text }}</p>
              <p v-if="modalData.option.special_requirements"><strong>Requirements:</strong> {{ modalData.option.special_requirements }}</p>
              <p v-if="modalData.option.price > 0">
                <strong>Price:</strong> ₱{{ parseFloat(modalData.option.price).toLocaleString() }}
              </p>
              <p v-else>
                <strong>Price:</strong> Free service
              </p>
              <p class="modal-note">Please ensure you arrive at the airport 2 hours before departure for assistance services.</p>
            </template>
            <template v-else>
              <p><strong>Action:</strong> No Assistance Selected</p>
              <p class="modal-note">You are selecting no special assistance for this passenger.</p>
            </template>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="modal-cancel" @click="closeConfirmationModal">Cancel</button>
          <button class="modal-confirm" @click="confirmSelection">Confirm Selection</button>
        </div>
      </div>
    </div>
    
    <!-- Animation Component -->
    <FlyingIcon ref="flyingIconRef" />
  </div>
</template>
<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useBookingStore } from '@/stores/booking';
import { useRouter, useRoute } from 'vue-router';
import { addonService } from '@/services/booking/addonService';
import api from '@/services/api/axios';
import BookingTimer from '@/components/booking/BookingTimer.vue';
import AnimatedNumber from '@/components/common/AnimatedNumber.vue';
import FlyingIcon from '@/components/common/FlyingIcon.vue';

const bookingStore = useBookingStore();
const router = useRouter();
const route = useRoute();

const currentTab = ref('baggage');
// activeSegment is no longer used for tab UI, but we keep it for fallback if needed inside modal state.
const activeSegment = ref('depart'); 
const isLoading = ref(true);

// Modal state
const showConfirmationModal = ref(false);
const modalType = ref(''); // 'baggage', 'meal', 'assistance'
const modalTitle = ref('');
const modalData = ref({
  passenger: null,
  option: null,
  passengerKey: '',
  isDeselecting: false,
  segment: 'depart'
});

const instance = ref(null);
const flyingIconRef = ref(null);

// API Data
const baggageOptions = ref([]);
const mealOptions = ref([]);
const assistanceOptions = ref([]);
const insurancePlans = ref([]);

// Update selectedAddons structure to support both depart and return for round trips
const selectedAddons = reactive({
  baggage: {},
  meals: {},
  wheelchair: {},
  seats: bookingStore.addons?.seats || {},
  insurance: bookingStore.addons?.insurance || { selectedPlanId: null, price: 0 }
});

// Sync local state with store
const syncSelectionsFromStore = () => {
  const tripType = bookingStore.tripType;
  const segments = [];
  
  if (tripType === 'multi_city' || tripType === 'multi-city') {
    bookingStore.multiCitySegments.forEach((_, idx) => segments.push(idx.toString()));
  } else {
    segments.push('depart');
    if (tripType === 'round_trip' || tripType === 'round-trip') segments.push('return');
  }

  segments.forEach(seg => {
    if (!selectedAddons.baggage[seg]) selectedAddons.baggage[seg] = {};
    if (!selectedAddons.meals[seg]) selectedAddons.meals[seg] = {};
    if (!selectedAddons.wheelchair[seg]) selectedAddons.wheelchair[seg] = {};
    
    selectedAddons.baggage[seg] = { ...bookingStore.addons.baggage?.[seg] };
    selectedAddons.meals[seg] = { ...bookingStore.addons.meals?.[seg] };
    selectedAddons.wheelchair[seg] = { ...bookingStore.addons.wheelchair?.[seg] };
  });

  selectedAddons.seats = bookingStore.addons?.seats ? { ...bookingStore.addons.seats } : {};
  selectedAddons.insurance = {
    selectedPlanId: bookingStore.addons?.insurance?.selectedPlanId || null,
    price: bookingStore.addons?.insurance?.price || 0
  };
};

// Add trip type info
const tripTypeInfo = computed(() => {
  return bookingStore.isRoundTrip ? 'Round Trip' : 'One Way';
});

// Flight segments for all trip types
const flightSegments = computed(() => {
  const tripType = bookingStore.tripType;
  
  if (tripType === 'multi_city' || tripType === 'multi-city') {
    return bookingStore.multiCitySegments.map((seg, idx) => ({
      key: idx.toString(),
      label: `Flight ${idx + 1}`,
      flight: seg.selectedFlight?.flight_number || 'N/A',
      route: `${seg.origin} → ${seg.destination}`
    }));
  }

  const segments = [
    {
      key: 'depart',
      label: 'Depart Flight',
      flight: bookingStore.selectedOutbound?.flight_number || 'N/A'
    }
  ];
  
  if (bookingStore.isRoundTrip) {
    segments.push({
      key: 'return',
      label: 'Return Flight',
      flight: bookingStore.selectedReturn?.flight_number || 'N/A'
    });
  }
  
  return segments;
});

// Active segment label
const activeSegmentLabel = computed(() => {
  const segment = flightSegments.value.find(s => s.key === activeSegment.value);
  return segment ? segment.label : 'Flight';
});

// Sync local state with store
// This helper was moved and is now defined above.

// Flight info computed
const flightInfo = computed(() => {
  const info = [];
  const tripType = bookingStore.tripType;

  if (tripType === 'multi_city' || tripType === 'multi-city') {
    bookingStore.multiCitySegments.forEach((seg, idx) => {
      if (seg.selectedFlight) {
        info.push({
          type: `Flight ${idx + 1}`,
          flight: seg.selectedFlight.flight_number,
          route: `${seg.selectedFlight.origin} → ${seg.selectedFlight.destination}`,
          price: parseFloat(seg.selectedFlight.price || 0)
        });
      }
    });
    return info;
  }
  
  if (bookingStore.selectedOutbound) {
    info.push({
      type: 'Outbound',
      flight: bookingStore.selectedOutbound.flight_number,
      route: `${bookingStore.selectedOutbound.origin} → ${bookingStore.selectedOutbound.destination}`,
      price: parseFloat(bookingStore.selectedOutbound.price || 0)
    });
  }
  
  if (bookingStore.isRoundTrip && bookingStore.selectedReturn) {
    info.push({
      type: 'Return',
      flight: bookingStore.selectedReturn.flight_number,
      route: `${bookingStore.selectedReturn.origin} → ${bookingStore.selectedReturn.destination}`,
      price: parseFloat(bookingStore.selectedReturn.price || 0)
    });
  }
  
  return info;
});

// Helper to get selection for current segment
const getBaggageSelection = (passengerKey, segment) => {
  return selectedAddons.baggage[segment]?.[passengerKey] || null;
};

const getMealSelection = (passengerKey, segment) => {
  return selectedAddons.meals[segment]?.[passengerKey] || null;
};

const getAssistanceSelection = (passengerKey, segment) => {
  return selectedAddons.wheelchair[segment]?.[passengerKey] || null;
};

const selectedInsurancePlanId = computed(() => {
  return bookingStore.addons?.insurance?.selectedPlanId || null;
});

const insurancePrice = computed(() => {
  return bookingStore.addons?.insurance?.price || 0;
});

// Roadmap logic: track completion for each segment
const segmentRoadmap = computed(() => {
  const segments = flightSegments.value;
  const pax = bookingStore.passengers;
  
  return segments.map(seg => {
    const segKey = seg.key;
    const baggageDone = pax.every(p => !!bookingStore.addons.baggage[segKey]?.[p.key]);
    const mealsDone = pax.every(p => !!bookingStore.addons.meals[segKey]?.[p.key]);
    const seatsDone = pax.every(p => !!bookingStore.addons.seats[segKey]?.[p.key]);
    const assistanceDone = pax.every(p => !!bookingStore.addons.wheelchair[segKey]?.[p.key]);
    
    return {
      ...seg,
      baggageDone,
      mealsDone,
      seatsDone,
      assistanceDone,
      isComplete: baggageDone && mealsDone && seatsDone
    };
  });
});

const handleCopyAddon = (type, passenger) => {
  bookingStore.copyAddonToAllSegments(type, passenger.key, activeSegment.value);
  // Optional: show a mini toast or notification
  console.log(`📋 Copied ${type} for ${passenger.firstName} to all segments`);
};

const selectInsurance = (plan) => {
  if (!plan) return;
  bookingStore.selectInsurancePlan(plan.id, plan.retail_price);
  selectedAddons.insurance = {
    selectedPlanId: plan.id,
    price: parseFloat(plan.retail_price) || 0
  };
};

const removeInsurance = () => {
  bookingStore.clearInsurance();
  selectedAddons.insurance = { selectedPlanId: null, price: 0 };
};

onMounted(async () => {
  try {
    // First, migrate store to new format
    bookingStore.migrateAddonsToNewFormat();
    
    const airlineId = bookingStore.selectedOutbound?.airline_id || bookingStore.selectedOutbound?.airline;
    
    const [bagRes, mealRes, assistRes, insuranceRes] = await Promise.all([
      addonService.getBaggageOptions(airlineId),
      addonService.getMealOptions(airlineId),
      addonService.getAssistanceServices(airlineId),
      api.get('/flightapp/api/insurance-plans/').catch(() => null)
    ]);
    
    // Handle paginated responses (response.data.results) or flat arrays (response.data)
    baggageOptions.value = bagRes.data.results || bagRes.data || [];
    mealOptions.value = mealRes.data.results || mealRes.data || [];
    assistanceOptions.value = assistRes.data.results || assistRes.data || [];

    if (insuranceRes && insuranceRes.data) {
      const data = insuranceRes.data;
      insurancePlans.value = Array.isArray(data) ? data : (data?.results || []);
    } else {
      insurancePlans.value = [];
    }

    // Load existing selections from store if they exist
    console.log("📦 Loading existing add-ons from store...");
    syncSelectionsFromStore();
    
    console.log("✅ Final selectedAddons:", selectedAddons);
  } catch (error) {
    console.error("Failed to load add-ons:", error);
  } finally {
    isLoading.value = false;
  }
});

// Helper for dynamic price lookup
const findPrice = (list, id) => {
  const item = list.find(i => i.id === id);
  return item ? parseFloat(item.price) : 0;
};

const getOptionById = (list, id) => {
  return list.find(i => i.id === id) || null;
};

// Direct selection handlers for cards - UPDATED with store calls
const selectBaggageDirect = (passenger, option, segment, event) => {
  const passengerKey = passenger.key;
  const currentSelection = getBaggageSelection(passengerKey, segment);
  
  // Check if already selected (compare by ID)
  if (currentSelection && currentSelection.id === option.id) {
    // Deselect
    selectedAddons.baggage[segment][passengerKey] = null;
    bookingStore.removeBaggageAddon(passengerKey, segment);
    console.log(`❌ Removed baggage for passenger ${passengerKey} on ${segment}`);
  } else {
    // Select - store full object
    const baggageObj = {
      id: option.id,
      price: parseFloat(option.price) || 0,
      formatted_weight: option.formatted_weight,
      name: option.formatted_weight
    };
    selectedAddons.baggage[segment][passengerKey] = baggageObj;
    bookingStore.updateBaggageAddon(passengerKey, baggageObj, segment);
    if (event && flyingIconRef.value) flyingIconRef.value.fly(event.currentTarget, '#sidebar-baggage', '🧳');
    console.log(`✅ Added ${option.formatted_weight} baggage for passenger ${passengerKey} on ${segment}: ₱${option.price}`);
  }
  // Phase 11: Background sync to preserve progress
  bookingStore.snapshotToServer();
};

const selectMealDirect = (passenger, option, segment, event) => {
  const passengerKey = passenger.key;
  const currentSelection = getMealSelection(passengerKey, segment);
  
  if (!option) {
    // Select "No Meal"
    selectedAddons.meals[segment][passengerKey] = null;
    bookingStore.removeMealAddon(passengerKey, segment);
    console.log(`❌ No meal for passenger ${passengerKey} on ${segment}`);
  } else {
    // Check if already selected (compare by ID)
    if (currentSelection && currentSelection.id === option.id) {
      // Deselect if already selected
      selectedAddons.meals[segment][passengerKey] = null;
      bookingStore.removeMealAddon(passengerKey, segment);
      console.log(`❌ Removed meal for passenger ${passengerKey} on ${segment}`);
    } else {
      // Select new meal - store full object
      const mealObj = {
        id: option.id,
        price: parseFloat(option.price) || 0,
        name: option.name,
        meal_type: option.meal_type,
        description: option.description
      };
      selectedAddons.meals[segment][passengerKey] = mealObj;
      bookingStore.updateMealAddon(passengerKey, mealObj, segment);
      if (event && flyingIconRef.value && option) flyingIconRef.value.fly(event.currentTarget, '#sidebar-meals', '🍱');
      console.log(`✅ Added ${option.name} meal for passenger ${passengerKey} on ${segment}: ₱${option.price}`);
    }
  }
  // Phase 11: Background sync to preserve progress
  bookingStore.snapshotToServer();
};

const selectAssistanceDirect = (passenger, option, segment, event) => {
  const passengerKey = passenger.key;
  
  if (!option) {
    // Select "No Assistance"
    selectedAddons.wheelchair[segment][passengerKey] = null;
    bookingStore.removeAssistanceAddon(passengerKey, segment);
    console.log(`❌ No assistance for passenger ${passengerKey} on ${segment}`);
  } else {
    // Select assistance
    if (getAssistanceSelection(passengerKey, segment) === option.id) {
      // Deselect if already selected
      selectedAddons.wheelchair[segment][passengerKey] = null;
      bookingStore.removeAssistanceAddon(passengerKey, segment);
      console.log(`❌ Removed assistance for passenger ${passengerKey} on ${segment}`);
    } else {
      // Select new assistance - store ID only
      selectedAddons.wheelchair[segment][passengerKey] = option.id;
      bookingStore.updateAssistanceAddon(passengerKey, option.id, segment);
      if (event && flyingIconRef.value && option) flyingIconRef.value.fly(event.currentTarget, '#sidebar-assistance', '♿');
      console.log(`✅ Added ${option.name} assistance for passenger ${passengerKey} on ${segment}: ${option.price > 0 ? '₱' + option.price : 'Free'}`);
    }
  }
  // Phase 11: Background sync to preserve progress
  bookingStore.snapshotToServer();
};

// Confirmation Modal Functions - UPDATED with store calls
const showMealConfirmation = (passenger, option, segment) => {
  const passengerKey = passenger.key;
  const currentSelection = getMealSelection(passengerKey, segment);
  let currentOption = null;
  
  if (currentSelection && typeof currentSelection === 'object') {
    currentOption = getOptionById(mealOptions.value, currentSelection.id);
  } else if (currentSelection) {
    currentOption = getOptionById(mealOptions.value, currentSelection);
  }
  
  modalType.value = 'meal';
  modalTitle.value = option ? 'Confirm Meal Selection' : 'Remove Meal Selection';
  modalData.value = {
    passenger,
    option: option,
    passengerKey: passenger.key,
    isDeselecting: !option && currentOption,
    segment: segment
  };
  showConfirmationModal.value = true;
};

const showAssistanceConfirmation = (passenger, option, segment) => {
  const passengerKey = passenger.key;
  const currentOption = getOptionById(assistanceOptions.value, getAssistanceSelection(passengerKey, segment));
  
  modalType.value = 'assistance';
  modalTitle.value = option ? 'Confirm Assistance Service' : 'Remove Assistance Service';
  modalData.value = {
    passenger,
    option: option,
    passengerKey: passenger.key,
    isDeselecting: !option && currentOption,
    segment: segment
  };
  showConfirmationModal.value = true;
};

const closeConfirmationModal = () => {
  showConfirmationModal.value = false;
  
  // Reset modal data
  modalData.value = { passenger: null, option: null, passengerKey: '', isDeselecting: false, segment: 'depart' };
  modalType.value = '';
  modalTitle.value = '';
};

const confirmSelection = () => {
  const { passengerKey, option, isDeselecting, segment } = modalData.value;
  
  if (modalType.value === 'meal') {
    if (!option) {
      // Remove meal selection
      selectedAddons.meals[segment][passengerKey] = null;
      bookingStore.removeMealAddon(passengerKey, segment);
      console.log(`❌ Removed meal for passenger ${passengerKey} on ${segment}`);
    } else {
      // Select meal - store as object
      const mealObj = {
        id: option.id,
        price: parseFloat(option.price) || 0,
        name: option.name,
        meal_type: option.meal_type,
        description: option.description
      };
      selectedAddons.meals[segment][passengerKey] = mealObj;
      bookingStore.updateMealAddon(passengerKey, mealObj, segment);
      console.log(`✅ Added ${option.name} meal for passenger ${passengerKey} on ${segment}: ₱${option.price}`);
    }
  }
  else if (modalType.value === 'assistance') {
    if (!option) {
      // Remove assistance selection
      selectedAddons.wheelchair[segment][passengerKey] = null;
      bookingStore.removeAssistanceAddon(passengerKey, segment);
      console.log(`❌ Removed assistance for passenger ${passengerKey} on ${segment}`);
    } else {
      // Select assistance
      selectedAddons.wheelchair[segment][passengerKey] = option.id;
      bookingStore.updateAssistanceAddon(passengerKey, option.id, segment);
      console.log(`✅ Added ${option.name} assistance for passenger ${passengerKey} on ${segment}: ${option.price > 0 ? '₱' + option.price : 'Free'}`);
    }
  }
  
  // Phase 11: Background sync after modal confirmation
  bookingStore.snapshotToServer();
  closeConfirmationModal();
};

// Indicator Position Logic
const indicatorStyle = computed(() => {
  const tabs = ['baggage', 'seat', 'meals', 'wheelchair'];
  const activeTab = currentTab.value === 'seat' ? 'seat' : currentTab.value;
  const currentIndex = tabs.indexOf(activeTab);
  return {
    left: `${(currentIndex * 100 / 4) + 12.5}%`,
    transform: 'translateX(-50%)'
  };
});

// Updated Base Fare Calculation for all trip types
const baseFare = computed(() => bookingStore.combinedBasePriceTotal);

// Updated totals to include all segments
const totalBaggage = computed(() => bookingStore.totalBaggagePrice);
const totalMeals = computed(() => bookingStore.totalMealsPrice);

const totalAssistance = computed(() => bookingStore.totalAssistancePrice);

// FIXED: Calculate seat total correctly using seat_price across all segments
const totalSeats = computed(() => bookingStore.totalSeatsPrice);

const taxesPrice = computed(() => {
  // If backend provided taxes, use them. Otherwise estimate 12%
  if (backendBreakdown.value && backendBreakdown.value.taxes) {
    return parseFloat(backendBreakdown.value.taxes);
  }
  return bookingStore.totalTaxes;
});
// Use bookingStore.grandTotal for consistency
const grandTotal = computed(() => bookingStore.grandTotal);

const saveAndContinue = () => {
  // ...

  // --- DEBUG LOG START ---
  console.group("🛒 ADD-ONS PURCHASE SUMMARY");
  console.log("Trip Type:", tripTypeInfo.value);

  // Show flight info
  console.log("✈️ FLIGHT DETAILS:");
  flightInfo.value.forEach(flight => {
    console.log(`  ${flight.type}: ${flight.flight} (${flight.route}) - ₱${flight.price.toLocaleString()}`);
  });

  // Check seat data structure
  console.log("💺 SEAT SELECTIONS:");
  const seatsState = selectedAddons.seats || {};
  const isSegmented = typeof seatsState === 'object' && (seatsState.depart || seatsState.return);

  const logSeatEntries = (entries, segmentLabel) => {
    if (!entries || entries.length === 0) return;
    console.log(`  Segment: ${segmentLabel}`);
    entries.forEach(([passengerKey, seat]) => {
      if (!seat || typeof seat !== 'object') return;

      console.log(`    Passenger ${passengerKey}:`, {
        seat_code: seat.seat_code,
        seat_price: seat.seat_price,
        seat_total_price: seat.seat_total_price,
        final_price: seat.final_price,
        seat_class: seat.seat_class?.name
      });
    });
  };

  if (isSegmented) {
    const departEntries = Object.entries(seatsState.depart || {});
    const returnEntries = Object.entries(seatsState.return || {});
    if (departEntries.length === 0 && returnEntries.length === 0) {
      console.log("  No seats selected");
    } else {
      logSeatEntries(departEntries, 'depart');
      logSeatEntries(returnEntries, 'return');
    }
  } else {
    const flatEntries = Object.entries(seatsState);
    if (flatEntries.length === 0) {
      console.log("  No seats selected");
    } else {
      logSeatEntries(flatEntries, 'all');
    }
  }

  // Calculate individual totals
  const baggageTotal = totalBaggage.value;
  const mealsTotal = totalMeals.value;
  const assistanceTotal = totalAssistance.value;
  const seatExtrasTotal = totalSeats.value; // This uses the fixed calculation
  const baseFareTotal = baseFare.value;
  const insuranceTotal = insurancePrice.value;
  
  const receipt = {
    "Base Fare": `₱${baseFareTotal.toLocaleString()}`,
    "Seat Selection": `₱${seatExtrasTotal.toLocaleString()}`,
    "Baggage": `₱${baggageTotal.toLocaleString()}`,
    "Meals": `₱${mealsTotal.toLocaleString()}`,
    "Assistance": `₱${assistanceTotal.toLocaleString()}`,
    "Travel Insurance": `₱${insuranceTotal.toLocaleString()}`
  };
  
  console.table(receipt);
  
  // Summary of totals
  console.log("📊 TOTALS SUMMARY:");
  console.log("Add-ons Total:", `₱${(baggageTotal + mealsTotal + assistanceTotal + seatExtrasTotal + insuranceTotal).toLocaleString()}`);
  console.log("Flight Base Total:", `₱${baseFareTotal.toLocaleString()}`);
  console.log("Store Grand Total:", `₱${bookingStore.grandTotal.toLocaleString()}`);
  console.log("Calculated Grand Total:", `₱${grandTotal.value.toLocaleString()}`);
  
  // Verify seat price calculation
  console.log("🔍 SEAT PRICE VERIFICATION:");
  console.log("totalSeats computed value:", totalSeats.value);
  
  console.groupEnd();
  // --- DEBUG LOG END ---

  router.push({ name: 'ReviewBooking' });
};
</script>

<style scoped>
/* Updated color theme to #FF579A */
.pal-bg { background: #f4f7f9; min-height: 100vh; padding: 40px 0; }
.pal-layout { display: grid; grid-template-columns: 1fr 350px; gap: 30px; max-width: 1200px; margin: 0 auto; }
.page-title { color: #FF579A; font-weight: 800; margin-bottom: 25px; font-size: 1.8rem; }

.square-tabs-container { position: relative; margin-bottom: 30px; background: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.square-tabs-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; position: relative; z-index: 2; }
.square-tab { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px 15px; background: #f8f9fa; border: 2px solid #e9ecef; border-radius: 8px; cursor: pointer; transition: all 0.3s ease; text-align: center; min-height: 100px; }
.square-tab.active { background: linear-gradient(135deg, #FF579A 0%, #FF4081 100%); border-color: #FF579A; color: white; }
.square-tab.seat-tab { border-style: dashed; }
.tab-icon { font-size: 1.8rem; margin-bottom: 8px; }
.tab-label { font-weight: 600; font-size: 0.95rem; }
.active-tab-indicator { position: absolute; bottom: 0; left: 0; width: 25%; height: 4px; background: #FF579A; border-radius: 2px; transition: left 0.4s ease; z-index: 1; }

.addon-workspace { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eaeaea; min-height: 400px; }
.loading-state { display: flex; align-items: center; justify-content: center; height: 200px; color: #666; }

.tab-pane h3 { color: #FF579A; margin-bottom: 25px; font-size: 1.3rem; padding-bottom: 10px; border-bottom: 2px solid #f0f0f0; }

.insurance-pane {
  margin-bottom: 25px;
}

.insurance-intro {
  color: #666;
  margin-bottom: 15px;
  line-height: 1.5;
}

.insurance-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.insurance-card {
  border: 2px solid #e0e0e0;
  padding: 18px;
  border-radius: 10px;
  background: white;
  transition: all 0.2s ease;
}

.insurance-card.selected {
  border-color: #FF579A;
  background: #FFF0F7;
}

.insurance-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 10px;
}

.insurance-header h4 {
  margin: 0;
  color: #FF579A;
  font-size: 1.05rem;
}

.insurance-provider {
  margin: 6px 0 0 0;
  color: #777;
  font-size: 0.85rem;
}

.insurance-price {
  font-weight: 800;
  color: #FF579A;
  white-space: nowrap;
}

.insurance-description {
  color: #555;
  margin: 10px 0;
  line-height: 1.4;
  font-size: 0.9rem;
}

.insurance-coverage {
  margin: 0 0 12px 0;
  color: #666;
  font-size: 0.85rem;
  background: #f8f9fa;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #eee;
}

.insurance-actions {
  display: flex;
  justify-content: flex-end;
}

.insurance-toggle-btn {
  padding: 10px 14px;
  background: #FF579A;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
}

.insurance-toggle-btn.remove {
  background: #666;
}

.insurance-unavailable {
  color: #888;
  font-style: italic;
}

/* Baggage Grid Styles */
.option-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 15px; }
.opt-card { border: 2px solid #e0e0e0; padding: 20px 15px; border-radius: 8px; cursor: pointer; text-align: center; transition: all 0.2s; background: white; }
.opt-card.selected { border-color: #FF579A; background: #FFF0F7; font-weight: bold; }
.opt-card .weight { display: block; font-size: 1.1rem; margin-bottom: 8px; font-weight: 700; color: #FF579A; }
.opt-card .price { display: block; color: #FF579A; font-weight: 700; }

/* Meal Grid Styles */
.meal-options-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px; }
.meal-card { border: 2px solid #e0e0e0; padding: 15px; border-radius: 8px; cursor: pointer; transition: all 0.2s; background: white; display: flex; flex-direction: column; min-height: 180px; }
.meal-card.selected { border-color: #FF579A; background: #FFF0F7; }
.meal-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
.meal-icon { font-size: 2rem; text-align: center; margin-bottom: 10px; }
.meal-details { flex: 1; }
.meal-name { font-weight: 700; color: #FF579A; margin-bottom: 5px; font-size: 1rem; }
.meal-type { font-size: 0.85rem; color: #666; margin-bottom: 8px; font-style: italic; }
.meal-description { font-size: 0.9rem; color: #555; margin-bottom: 8px; line-height: 1.3; }
.meal-calories { font-size: 0.8rem; color: #888; margin-bottom: 8px; }
.meal-price { font-weight: 700; color: #FF579A; font-size: 1.1rem; margin-top: auto; }
.meal-allergens { font-size: 0.75rem; color: #FF4081; margin-top: 8px; padding-top: 8px; border-top: 1px dashed #eee; }

/* Assistance Grid Styles */
.assistance-options-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 15px; }
.assistance-card { border: 2px solid #e0e0e0; padding: 15px; border-radius: 8px; cursor: pointer; transition: all 0.2s; background: white; display: flex; flex-direction: column; min-height: 200px; }
.assistance-card.selected { border-color: #FF579A; background: #FFF0F7; }
.assistance-card.free { border-color: #28a745; }
.assistance-card.free.selected { background: #e8f5e9; }
.assistance-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
.assistance-icon { font-size: 2rem; text-align: center; margin-bottom: 10px; }
.assistance-details { flex: 1; }
.assistance-name { font-weight: 700; color: #FF579A; margin-bottom: 5px; font-size: 1rem; }
.assistance-type { font-size: 0.85rem; color: #666; margin-bottom: 8px; font-style: italic; }
.assistance-description { font-size: 0.9rem; color: #555; margin-bottom: 8px; line-height: 1.3; }
.assistance-notice { font-size: 0.8rem; color: #888; margin-bottom: 8px; }
.assistance-requirements { font-size: 0.75rem; color: #666; margin-bottom: 8px; }
.assistance-price { font-weight: 700; color: #FF579A; font-size: 1.1rem; margin-top: auto; }
.assistance-card.free .assistance-price { color: #28a745; }

/* Common Styles */
.p-addon-row { margin-bottom: 30px; padding-bottom: 25px; border-bottom: 1px solid #eee; }
.p-info { margin-bottom: 15px; font-size: 1rem; }

.footer-nav { display: flex; justify-content: space-between; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eaeaea; }
.btn-back { padding: 15px 30px; background: #666; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }
.btn-continue { padding: 15px 40px; background: #FF579A; color: white; border: none; border-radius: 6px; font-weight: 700; cursor: pointer; }

.summary-card { background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid #eaeaea; }
.sticky { position: sticky; top: 20px; }
.summary-header { background: #FF579A; color: white; padding: 20px; text-align: center; font-weight: 700; border-radius: 12px 12px 0 0; }
.summary-body { padding: 25px; }
.price-line { display: flex; justify-content: space-between; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px dashed #eee; font-size: 0.95rem; }
.total-row { display: flex; justify-content: space-between; margin-top: 15px; padding-top: 15px; border-top: 2px solid #eee; font-size: 1.2rem; font-weight: 700; }
.final-amt { color: #FF579A; font-size: 1.5rem; font-weight: 900; }

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
  background: #FF579A;
  color: white;
  border-radius: 12px 12px 0 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: white;
  cursor: pointer;
  line-height: 1;
}

.modal-body {
  padding: 25px;
}

.modal-body p {
  margin: 10px 0;
  line-height: 1.6;
}

.modal-note {
  font-size: 0.9rem;
  color: #666;
  font-style: italic;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 6px;
  margin-top: 15px !important;
}

.modal-note.warning {
  color: #FF4081;
  background: #FFE6F1;
  border-left: 4px solid #FF4081;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.modal-cancel {
  padding: 10px 20px;
  background: #666;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.modal-confirm {
  padding: 10px 20px;
  background: #FF579A;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 700;
}

/* Add new styles for trip type header */
.trip-type-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.trip-type-badge {
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.trip-type-badge.round-trip {
  background: #FFE6F1;
  color: #FF579A;
  border: 2px solid #FF579A;
}

.trip-type-badge.one-way {
  background: #FCE4EC;
  color: #E91E63;
  border: 2px solid #E91E63;
}

/* Flight summary card styles */
.flight-summary-card {
  background: white;
  border-radius: 12px;
  margin-bottom: 25px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  border: 1px solid #eaeaea;
}

.flight-summary-header {
  background: #f8f9fa;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  border-radius: 12px 12px 0 0;
}

.flight-summary-header h3 {
  margin: 0;
  color: #FF579A;
  font-size: 1.2rem;
}

.flight-summary-body {
  padding: 20px;
}

.flight-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px dashed #eee;
}

.flight-item:last-child {
  border-bottom: none;
}

.flight-type {
  font-weight: bold;
  color: #FF579A;
  min-width: 80px;
}

.flight-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.flight-number {
  font-weight: bold;
  color: #333;
}

.flight-route {
  color: #666;
  font-size: 0.9rem;
}

.flight-price {
  font-weight: bold;
  color: #FF579A;
  min-width: 100px;
  text-align: right;
}

/* Update summary card styles */
.flight-line {
  font-size: 0.9rem;
  padding: 5px 0;
}

.passenger-line {
  color: #666;
  font-style: italic;
  padding: 5px 0 10px 0;
  border-bottom: 1px dashed #eee;
  margin-bottom: 10px;
}

/* Add new styles for flight segment tabs */
.flight-segment-tabs {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  background: white;
  padding: 15px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.segment-tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 15px;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.segment-tab.active {
  background: linear-gradient(135deg, #FF579A 0%, #FF4081 100%);
  border-color: #FF579A;
  color: white;
}

.segment-icon {
  font-size: 1.8rem;
  margin-bottom: 8px;
}

.segment-label {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 5px;
}

.segment-flight {
  font-size: 0.85rem;
  opacity: 0.8;
  font-family: monospace;
}

.segment-notice {
  background: #FFE6F1;
  padding: 12px 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-left: 4px solid #FF579A;
}

.notice-icon {
  font-size: 1.2rem;
}

/* Visual Roadmap Styles */
.visual-roadmap {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  border: 1px solid #eaeaea;
}

.roadmap-item {
  flex: 1;
  display: flex;
  align-items: center;
  position: relative;
}

.roadmap-dot {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: #888;
  border: 2px solid #e0e0e0;
  z-index: 2;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.roadmap-dot.active {
  background: white;
  border-color: #FF579A;
  color: #FF579A;
  box-shadow: 0 0 0 4px rgba(255, 87, 154, 0.1);
}

.roadmap-dot.done {
  background: #FF579A;
  border-color: #FF579A;
  color: white;
}

.roadmap-info {
  margin-left: 12px;
  display: flex;
  flex-direction: column;
}

.roadmap-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #333;
  white-space: nowrap;
}

.roadmap-status {
  display: flex;
  gap: 4px;
  margin-top: 2px;
}

.roadmap-status span {
  font-size: 0.75rem;
  opacity: 0.3;
  filter: grayscale(1);
}

.roadmap-status span.check-done {
  opacity: 1;
  filter: grayscale(0);
}

.roadmap-connector {
  flex: 1;
  height: 2px;
  background: #e0e0e0;
  margin: 0 15px;
  z-index: 1;
}

/* Copy Addon Button Styles */
.copy-addon-btn {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  background: #f0f7ff;
  color: #007bff;
  border: 1px solid #cce5ff;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-left: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  vertical-align: middle;
}

.copy-addon-btn:hover {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.copy-addon-btn span {
  display: inline-block;
}

.p-info {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .trip-type-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .flight-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .flight-price {
    text-align: left;
    min-width: auto;
  }
}

@media (max-width: 992px) {
  .pal-layout { grid-template-columns: 1fr; }
  .square-tabs-grid { grid-template-columns: repeat(2, 1fr); }
  .active-tab-indicator { width: 50%; }
  
  .option-grid,
  .meal-options-grid,
  .assistance-options-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    margin: 10px;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .modal-cancel, .modal-confirm {
    width: 100%;
  }
  
  .flight-segment-tabs {
    flex-direction: column;
  }
  
  .segment-tab {
    flex-direction: row;
    gap: 15px;
    text-align: left;
    justify-content: flex-start;
  }
  
  .segment-icon {
    margin-bottom: 0;
  }
}

@media (max-width: 1200px) {
  .pal-layout { 
    grid-template-columns: 1fr 350px; 
  }
}

@media (max-width: 768px) {
  .segment-tab {
    padding: 15px 10px;
  }
  
  .segment-label {
    font-size: 0.9rem;
  }
  
  .segment-flight {
    font-size: 0.8rem;
  }
}
</style>