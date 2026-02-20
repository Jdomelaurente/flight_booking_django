<template>
  <div class="pal-bg">
    <div class="container seat-layout-wrapper">
      <main class="seat-main">
        <div class="seat-header">
          <button @click="$router.back()" class="back-link">❮ Back to Add-ons</button>
          <h2>Select Your Seats</h2>
          
          <!-- Flight Segment Tabs for Round Trips -->
          <div v-if="bookingStore.isRoundTrip" class="flight-segment-tabs seat-segment">
            <div 
              v-for="segment in flightSegments" 
              :key="segment.key"
              @click="switchFlightSegment(segment.key)"
              :class="['segment-tab', { active: activeFlightSegment === segment.key }]"
            >
              <div class="segment-icon">
                <span v-if="segment.key === 'depart'">✈️</span>
                <span v-else>🔄</span>
              </div>
              <div class="segment-info">
                <div class="segment-label">{{ segment.label }}</div>
                <div class="segment-details">
                  {{ segment.flight }} • {{ segment.route }}
                  <span v-if="getSeatsForSegment(segment.key).length > 0" class="seat-count">
                    ({{ getSeatsForSegment(segment.key).length }}/{{ bookingStore.passengers.length }} selected)
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <p v-else class="flight-info">
            {{ bookingStore.selectedOutbound?.origin }} to {{ bookingStore.selectedOutbound?.destination }}
          </p>
        </div>

        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading seat map for {{ activeFlightSegmentLabel }}...</p>
        </div>

        <div v-else-if="aircraftModel && AircraftLayout" class="seat-selection-grid">
          <aside class="seat-passenger-list">
            <h3>Passengers</h3>
            <div 
              v-for="(p, index) in bookingStore.passengers" 
              :key="p.key"
              :class="['p-seat-card', { 
                active: activePIndex === index,
                'has-seat': assignedSeats[p.key]
              }]"
              @click="activePIndex = index"
            >
              <div class="p-info">
                <span class="p-number">{{ index + 1 }}</span>
                <div>
                  <span class="p-name">{{ p.firstName }} {{ p.lastName }}</span>
                  <span class="p-type">{{ p.type }}</span>
                </div>
              </div>
              <div class="seat-action">
                <span class="p-assigned-seat">
                  {{ assignedSeats[p.key]?.seat_code || 'Not Selected' }}
                </span>
                <button 
                  v-if="assignedSeats[p.key]"
                  @click.stop="changeSeat(p.key)"
                  class="change-seat-btn"
                  title="Change seat"
                >
                  ↻
                </button>
              </div>
            </div>

            <!-- Quick Actions for Round Trips -->
            <div v-if="bookingStore.isRoundTrip" class="quick-actions">
              <h4>Quick Actions</h4>
              <button 
                @click="copySeatsToReturn"
                class="quick-action-btn"
                :disabled="!hasDepartSeats"
                :class="{ disabled: !hasDepartSeats }"
              >
                📋 Copy Depart Seats to Return
              </button>
              <button 
                @click="clearSegmentSeats"
                class="quick-action-btn secondary"
              >
                🗑️ Clear {{ activeFlightSegmentLabel }} Seats
              </button>
            </div>

            <div class="seat-class-info">
              <h4>Seat Classes</h4>
              <div v-for="sc in seatClasses" :key="sc.id" class="class-item">
                <span class="class-color" :style="{ backgroundColor: getClassColor(sc.name) }"></span>
                <div>
                  <div class="class-name">{{ sc.name }}</div>
                  <div class="class-price">Multiplier: {{ sc.price_multiplier }}x</div>
                </div>
              </div>
            </div>
          </aside>

          <section class="aircraft-layout-container">
            <div class="aircraft-header">
              <h3>{{ aircraftModel }}</h3>
              <div class="flight-segment-info">
                <span class="aircraft-subtitle">{{ activeFlightSegmentLabel }} Flight</span>
                <span class="flight-number-badge">{{ currentFlight?.flight_number || 'N/A' }}</span>
              </div>
              <div class="aircraft-capacity">
                <span class="capacity-badge">Capacity: {{ aircraftCapacity }} seats</span>
                <span class="selected-badge">Selected: {{ Object.keys(assignedSeats).length }}/{{ bookingStore.passengers.length }}</span>
              </div>
            </div>
            
            <!-- Dynamically load the aircraft layout component -->
            <component
              :is="AircraftLayout"
              :seats="rawSeats"
              :selectedSeats="assignedSeats"
              :activePassenger="activePassenger"
              :onSeatSelect="assignSeat"
              :onSeatHover="hoverSeat"
            />
            
            <div class="aircraft-footer">
              <div class="cabin-legend">
                <span class="legend-item">
                  <span class="legend-color first"></span>
                  <span>First Class</span>
                </span>
                <span class="legend-item">
                  <span class="legend-color business"></span>
                  <span>Business</span>
                </span>
                <span class="legend-item">
                  <span class="legend-color economy"></span>
                  <span>Economy</span>
                </span>
              </div>
            </div>
          </section>

          <aside class="map-legend">
            <div class="legend-card">
              <h4>Legend</h4>
              <div class="legend-grid">
                <div class="legend-item"><span class="box available"></span><span>Available</span></div>
                <div class="legend-item"><span class="box selected"></span><span>Selected</span></div>
                <div class="legend-item"><span class="box occupied"></span><span>Occupied</span></div>
                <div class="legend-item"><span class="box premium"></span><span>Extra Space</span></div>
              </div>

              <div v-if="hasSelections" class="selected-summary">
                <div class="summary-divider"></div>
                <h4>Your Selection ({{ activeFlightSegmentLabel }})</h4>
                
                <div v-for="(seat, pKey) in assignedSeats" :key="pKey" class="selected-item">
                  <div class="selected-info">
                    <span class="passenger-name">{{ getPassengerName(pKey) }}</span>
                    <div class="seat-badge-row">
                      <span class="seat-mini-pill">{{ seat.seat_code }}</span>
                      <span class="seat-class-label">{{ seat.seat_class?.name }}</span>
                    </div>
                  </div>
                  <div class="selected-price">
                    ₱{{ (seat.seat_price || 0).toLocaleString() }}
                    <button @click="removeSeat(pKey)" class="remove-btn">×</button>
                  </div>
                </div>

                <div class="price-summary-box">
                  <div class="price-line">
                    <span>Seat Fees ({{ activeFlightSegmentLabel }}):</span>
                    <span>₱{{ segmentSeatTotal.toLocaleString() }}</span>
                  </div>
                  
                  <!-- Show total for both segments if round trip -->
                  <div v-if="bookingStore.isRoundTrip" class="price-line total">
                    <span>Total Seat Fees (Both Flights):</span>
                    <span>₱{{ totalSeats.toLocaleString() }}</span>
                  </div>
                  
                  <p class="summary-note">*Base flight fare not included in this total</p>
                </div>
              </div>

              <div class="selection-progress" v-if="bookingStore.isRoundTrip">
                <div class="progress-label">Selection Progress</div>
                <div class="progress-bars">
                  <div class="progress-bar">
                    <div class="progress-text">Depart</div>
                    <div class="progress-track">
                      <div class="progress-fill" :style="{ width: departProgress + '%' }"></div>
                    </div>
                    <div class="progress-count">{{ departSeatCount }}/{{ bookingStore.passengers.length }}</div>
                  </div>
                  <div class="progress-bar">
                    <div class="progress-text">Return</div>
                    <div class="progress-track">
                      <div class="progress-fill" :style="{ width: returnProgress + '%' }"></div>
                    </div>
                    <div class="progress-count">{{ returnSeatCount }}/{{ bookingStore.passengers.length }}</div>
                  </div>
                </div>
              </div>

              <button 
                class="btn-confirm-seats" 
                @click="confirmSeats"
                :disabled="!allPassengersHaveSeats"
                :class="{ disabled: !allPassengersHaveSeats }"
              >
                {{ confirmButtonText }}
              </button>
              
              <button 
                v-if="bookingStore.isRoundTrip && activeFlightSegment === 'depart' && allPassengersHaveSeats"
                @click="switchToReturnSegment"
                class="btn-next-segment"
              >
                Continue to Return Flight Seats →
              </button>
            </div>
          </aside>
        </div>

        <div v-else-if="!isLoading" class="error-state">
          <div class="error-icon">✈️</div>
          <h3>Unable to Load Seat Map</h3>
          <p v-if="aircraftModel">The aircraft layout for "{{ aircraftModel }}" is not available.</p>
          <p v-else>Unable to determine aircraft type.</p>
          <button @click="$router.back()" class="back-btn">Go Back</button>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineAsyncComponent, watch, shallowRef } from 'vue';
import { useRouter } from 'vue-router';
import { useBookingStore } from '@/stores/booking';
import { seatService } from '@/services/booking/seatService';
import { useModalStore } from '@/stores/modal';

const router = useRouter();
const bookingStore = useBookingStore();
const notificationStore = useNotificationStore();
const modalStore = useModalStore();

const activePIndex = ref(0);
const activeFlightSegment = ref('depart'); // 'depart' or 'return'
const hoveredSeat = ref(null);
const rawSeats = ref([]);
const isLoading = ref(true);
const baseFlightPrice = ref(0);
const aircraftModel = ref('');
const aircraftCapacity = ref(0);
const AircraftLayout = shallowRef(null);

// Computed properties
const currentFlight = computed(() => {
  return activeFlightSegment.value === 'depart' 
    ? bookingStore.selectedOutbound 
    : bookingStore.selectedReturn;
});

const activeFlightSegmentLabel = computed(() => {
  return activeFlightSegment.value === 'depart' ? 'Depart' : 'Return';
});

const flightSegments = computed(() => {
  const segments = [
    {
      key: 'depart',
      label: 'Depart Flight',
      flight: bookingStore.selectedOutbound?.flight_number || 'N/A',
      route: bookingStore.selectedOutbound 
        ? `${bookingStore.selectedOutbound.origin} → ${bookingStore.selectedOutbound.destination}`
        : 'N/A'
    }
  ];
  
  if (bookingStore.isRoundTrip && bookingStore.selectedReturn) {
    segments.push({
      key: 'return',
      label: 'Return Flight',
      flight: bookingStore.selectedReturn.flight_number || 'N/A',
      route: `${bookingStore.selectedReturn.origin} → ${bookingStore.selectedReturn.destination}`
    });
  }
  
  return segments;
});

// Get assigned seats for current segment
const assignedSeats = computed(() => {
  return bookingStore.getSeatsBySegment(activeFlightSegment.value);
});

// Get seats count for each segment
const departSeatCount = computed(() => {
  return Object.keys(bookingStore.getSeatsBySegment('depart')).length;
});

const returnSeatCount = computed(() => {
  return Object.keys(bookingStore.getSeatsBySegment('return')).length;
});

// Progress percentages
const departProgress = computed(() => {
  return (departSeatCount.value / bookingStore.passengers.length) * 100;
});

const returnProgress = computed(() => {
  return (returnSeatCount.value / bookingStore.passengers.length) * 100;
});

// Check if depart segment has seats
const hasDepartSeats = computed(() => {
  return departSeatCount.value > 0;
});

// Seat selection progress
const allPassengersHaveSeats = computed(() => {
  return bookingStore.allPassengersHaveSeatsForSegment(activeFlightSegment.value);
});

const allPassengersHaveAllSeats = computed(() => {
  return bookingStore.allPassengersHaveAllSeats;
});

const confirmButtonText = computed(() => {
  if (bookingStore.isRoundTrip) {
    if (activeFlightSegment.value === 'depart') {
      return allPassengersHaveSeats.value 
        ? 'Continue to Return Seats' 
        : `Assign All ${activeFlightSegmentLabel.value} Seats`;
    } else {
      return allPassengersHaveSeats.value 
        ? 'Confirm All Seat Selections' 
        : `Assign All ${activeFlightSegmentLabel.value} Seats`;
    }
  } else {
    return allPassengersHaveSeats.value 
      ? 'Confirm Seat Selection' 
      : 'Assign All Seats';
  }
});

// Seat total for current segment
const segmentSeatTotal = computed(() => {
  const seats = Object.values(assignedSeats.value || {});
  
  return seats.reduce((total, seat) => {
    const seatPrice = parseFloat(seat.seat_price) || 0;
    return total + seatPrice;
  }, 0);
});

// Total seats for both segments
const totalSeats = computed(() => {
  let total = 0;
  
  // Add depart seats
  Object.values(bookingStore.getSeatsBySegment('depart')).forEach(seat => {
    total += parseFloat(seat.seat_price) || 0;
  });
  
  // Add return seats if round trip
  if (bookingStore.isRoundTrip) {
    Object.values(bookingStore.getSeatsBySegment('return')).forEach(seat => {
      total += parseFloat(seat.seat_price) || 0;
    });
  }
  
  return total;
});

const hasSelections = computed(() => Object.keys(assignedSeats.value).length > 0);

// Get active passenger
const activePassenger = computed(() => {
  return bookingStore.passengers[activePIndex.value] || bookingStore.passengers[0];
});

// Get seats for a specific segment
const getSeatsForSegment = (segment) => {
  return Object.values(bookingStore.getSeatsBySegment(segment));
};

// Fetch seat data based on active segment
const fetchSeatData = async () => {
  const scheduleId = currentFlight.value?.id;
  if (!scheduleId) { 
    console.error('No schedule ID for', activeFlightSegment.value);
    return;
  }

  try {
    isLoading.value = true;
    
    console.log(`🚀 Fetching seat data for ${activeFlightSegmentLabel.value} flight:`, scheduleId);
    
    const response = await seatService.getSeatsBySchedule(scheduleId);
    
    if (response.success) {
      // Handle paginated response (response.seats.results) or flat array (response.seats)
      const seatsData = response.seats?.results || response.seats || [];
      rawSeats.value = Array.isArray(seatsData) ? seatsData : [];
      
      baseFlightPrice.value = response.schedule_price || 0;
      aircraftModel.value = response.aircraft_model || 'Airbus A321';
      aircraftCapacity.value = response.aircraft_capacity || 220;
      
      console.log(`✅ Seat data loaded for ${activeFlightSegmentLabel.value}:`, {
        scheduleId,
        schedulePrice: baseFlightPrice.value,
        aircraftModel: aircraftModel.value,
        aircraftCapacity: aircraftCapacity.value,
        seatsCount: rawSeats.value.length
      });
      
      // Load the appropriate aircraft layout component
      await loadAircraftLayout(aircraftModel.value);
      
      if (rawSeats.value.length === 0) {
        console.error(`❌ No seats found for ${activeFlightSegmentLabel.value} flight`, scheduleId);
      }
    } else {
      console.error(`❌ Failed to load seat data for ${activeFlightSegmentLabel.value}:`, response.error);
    }
    
  } catch (err) {
    console.error(`❌ Failed to load seat map for ${activeFlightSegmentLabel.value}`, err);
  } finally {
    isLoading.value = false;
  }
};

// Load aircraft layout component
const loadAircraftLayout = async (model) => {
  try {
    const normalizedModel = normalizeAircraftModel(model);
    
    console.log(`🛩️ Loading layout for aircraft: ${model} (normalized: ${normalizedModel})`);
    
    try {
      AircraftLayout.value = defineAsyncComponent(() => 
        import(`@/components/seatmaps/${normalizedModel}Layout.vue`)
      );
      
      await new Promise(resolve => setTimeout(resolve, 100));
      
      console.log(`✅ Loaded specific layout for ${model}`);
    } catch (error) {
      console.log(`⚠️ Specific layout for ${model} not found, trying default...`, error);
      
      try {
        AircraftLayout.value = defineAsyncComponent(() => 
          import('@/components/seatmaps/AirbusA321Layout.vue')
        );
        console.log(`✅ Loaded default Airbus A321 layout`);
      } catch (fallbackError) {
        console.error('❌ Failed to load default layout:', fallbackError);
        AircraftLayout.value = null;
      }
    }
    
  } catch (error) {
    console.error('❌ Error loading aircraft layout:', error);
    AircraftLayout.value = null;
  }
};

// Helper function to normalize aircraft model names
const normalizeAircraftModel = (model) => {
  if (!model) return 'AirbusA321';
  
  const modelMappings = {
    'Airbus A321': 'AirbusA321',
    'Airbus A320': 'AirbusA320',
    'Airbus A319': 'AirbusA319',
    'Boeing 737': 'Boeing737',
    'Boeing 747': 'Boeing747',
    'Boeing 777': 'Boeing777',
    'Boeing 787': 'Boeing787',
    'ATR 72': 'ATR72',
    'ATR 42': 'ATR42'
  };
  
  if (modelMappings[model]) {
    return modelMappings[model];
  }
  
  for (const [key, value] of Object.entries(modelMappings)) {
    if (model.toLowerCase().includes(key.toLowerCase())) {
      return value;
    }
  }
  
  return model
    .replace(/\s+/g, '')
    .replace(/[^a-zA-Z0-9]/g, '')
    .replace(/\d+$/, '') + model.match(/\d+$/)?.[0] || '';
};

// Layout Logic
const seatMapRows = computed(() => {
  const rows = {};
  rawSeats.value.forEach(s => {
    if (!rows[s.row]) rows[s.row] = { number: s.row, seats: [] };
    rows[s.row].seats.push(s);
  });
  return Object.values(rows).sort((a, b) => a.number - b.number);
});

const seatClasses = computed(() => {
  const unique = [];
  rawSeats.value.forEach(s => {
    if (s.seat_class && !unique.find(c => c.id === s.seat_class.id)) unique.push(s.seat_class);
  });
  return unique;
});

const exitRows = computed(() => [...new Set(rawSeats.value.filter(s => s.is_exit_row).map(s => s.row))]);

// Helpers
const getSeatStatus = (seat) => {
  const currentPKey = bookingStore.passengers[activePIndex.value]?.key;
  if (assignedSeats.value[currentPKey]?.id === seat.id) return 'selected';
  if (!seat.is_available) return 'occupied';
  const isTaken = Object.values(assignedSeats.value).some(s => s.id === seat.id);
  return isTaken ? 'taken-by-other' : 'available';
};

const getClassColor = (name) => {
  const colors = { 
    'First Class': '#8B4513', 
    'Business': '#4169E1', 
    'Premium Economy': '#228B22', 
    'Economy': '#666' 
  };
  return colors[name] || '#666';
};

const getPassengerName = (key) => {
  const p = bookingStore.passengers.find(p => p.key === key);
  return p ? `${p.firstName} ${p.lastName.charAt(0)}.` : '';
};

// Seat hover handler
const hoverSeat = (seat) => {
  hoveredSeat.value = seat;
};

// Actions
const assignSeat = (seat) => {
  if (!seat.is_available) return;
  
  const currentP = bookingStore.passengers[activePIndex.value];
  const occupantKey = Object.keys(assignedSeats.value).find(k => assignedSeats.value[k]?.id === seat.id);
  
  if (occupantKey && occupantKey !== currentP.key) {
    console.warn("Seat already taken by another passenger in this booking");
    return;
  }

  // Toggle Logic
  if (assignedSeats.value[currentP.key]?.id === seat.id) {
    bookingStore.removeSeat(currentP.key, activeFlightSegment.value);
    console.log(`❌ Removed seat ${seat.seat_code} from ${currentP.firstName} for ${activeFlightSegmentLabel.value}`);
  } else {
    // Calculate seat price ONLY (not base flight fare)
    const baseFlightPrice = currentFlight.value?.price || 0;
    const seatTotalPrice = parseFloat(seat.final_price) || 0;
    const seatPrice = Math.max(0, seatTotalPrice - baseFlightPrice);
    
    const seatPriceData = {
      id: seat.id,
      seat_code: seat.seat_code,
      seat_price: seatPrice,
      seat_total_price: seatTotalPrice,
      seat_class_name: seat.seat_class?.name,
      seat_class: {
        name: seat.seat_class?.name
      }
    };
    
    bookingStore.assignSeat(currentP.key, seatPriceData, activeFlightSegment.value);
    
    console.group(`💺 SEAT SELECTED: ${seat.seat_code}`);
    console.log(`Passenger: ${currentP.firstName} ${currentP.lastName}`);
    console.log(`Flight: ${activeFlightSegmentLabel.value}`);
    console.log(`Class: ${seat.seat_class?.name}`);
    console.log(`Base Flight Price: ₱${baseFlightPrice.toLocaleString()}`);
    console.log(`Total Seat Price (inc. flight): ₱${seatTotalPrice.toLocaleString()}`);
    console.log(`Extra Seat Fee Only: ₱${seatPrice.toLocaleString()}`);
    console.groupEnd();
  }

  // Auto-advance logic
  setTimeout(() => {
    const nextIdx = findNextPassengerWithoutSeat();
    if (nextIdx !== -1) activePIndex.value = nextIdx;
  }, 200);
};

const findNextPassengerWithoutSeat = () => {
  let next = bookingStore.passengers.findIndex((p, i) => 
    i > activePIndex.value && !assignedSeats.value[p.key]
  );
  
  if (next === -1) {
    next = bookingStore.passengers.findIndex(p => !assignedSeats.value[p.key]);
  }
  
  return next;
};

const changeSeat = (key) => {
  const idx = bookingStore.passengers.findIndex(p => p.key === key);
  if (idx !== -1) activePIndex.value = idx;
};

const removeSeat = (key) => {
  bookingStore.removeSeat(key, activeFlightSegment.value);
};

const switchFlightSegment = (segment) => {
  if (segment === activeFlightSegment.value) return;
  
  activeFlightSegment.value = segment;
  activePIndex.value = 0;
  fetchSeatData();
};

const switchToReturnSegment = () => {
  if (bookingStore.isRoundTrip && activeFlightSegment.value === 'depart') {
    switchFlightSegment('return');
  }
};

const copySeatsToReturn = () => {
  if (!bookingStore.isRoundTrip) return;
  
  bookingStore.copySeatsToReturn();
  notificationStore.success('Seats copied from depart to return flight!');
  
  // Switch to return segment to show copied seats
  if (activeFlightSegment.value === 'depart') {
    switchFlightSegment('return');
  }
};

const clearSegmentSeats = async () => {
  const confirmed = await modalStore.confirm({
    title: 'Clear Seats?',
    message: `Clear all seat selections for ${activeFlightSegmentLabel.value} flight?`,
    confirmText: 'Clear All',
    cancelText: 'Cancel'
  })

  if (confirmed) {
    bookingStore.clearSeatsForSegment(activeFlightSegment.value);
    console.log(`🧹 Cleared all seats for ${activeFlightSegmentLabel.value} flight`);
  }
};

const confirmSeats = () => {
  if (!allPassengersHaveSeats.value) {
    notificationStore.warn(`Please assign seats to all passengers for the ${activeFlightSegmentLabel.value} flight.`);
    return;
  }
  
  if (bookingStore.isRoundTrip) {
    if (activeFlightSegment.value === 'depart') {
      // Move to return seat selection
      switchFlightSegment('return');
    } else {
      // Both segments are complete, go back to add-ons
      router.back();
    }
  } else {
    // One-way trip is complete
    router.back();
  }
};

// Watch for active segment changes
watch(activeFlightSegment, () => {
  fetchSeatData();
});

// Initialize
onMounted(async () => {
  // First, migrate store to new format
  bookingStore.migrateAddonsToNewFormat();
  
  // Fetch seat data for initial segment
  await fetchSeatData();
  
  // If return flight doesn't exist for round trip, show warning
  if (bookingStore.isRoundTrip && !bookingStore.selectedReturn) {
    console.warn('Round trip selected but return flight is missing');
  }
});
</script>

<style scoped>
/* Core Layout */
.seat-layout-wrapper { 
  max-width: 1400px; 
  margin: 0 auto; 
  padding: 20px; 
  font-family: 'Segoe UI', sans-serif; 
}

.seat-selection-grid { 
  display: grid; 
  grid-template-columns: 250px 1fr 250px; 
  gap: 10px; 
  align-items: start;
}

/* Aircraft Layout Container */
.aircraft-layout-container {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border: 1px solid #eaeaea;
  max-height: 85vh;
  overflow-y: auto;
}

.aircraft-header {
  text-align: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.aircraft-header h3 {
  color: #003870;
  font-size: 1.5rem;
  margin: 0 0 8px 0;
  font-weight: 700;
}

.flight-segment-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 10px;
}

.aircraft-subtitle {
  color: #FF579A;
  font-size: 1rem;
  font-weight: 600;
  background: #FFF0F7;
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid #FF579A;
}

.flight-number-badge {
  background: #003870;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.aircraft-capacity {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 10px;
}

.capacity-badge,
.selected-badge {
  background: #f0f7ff;
  color: #0066cc;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  border: 1px solid #b3d9ff;
}

.selected-badge {
  background: #FFF0F7;
  color: #FF579A;
  border-color: #FFB6D9;
}

/* Flight Segment Tabs */
.flight-segment-tabs.seat-segment {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.segment-tab {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  gap: 10px;
}

.segment-tab.active {
  background: linear-gradient(135deg, #FF579A 0%, #FF4081 100%);
  border-color: #FF579A;
  color: white;
}

.segment-icon {
  font-size: 1.8rem;
  flex-shrink: 0;
}

.segment-info {
  flex: 1;
}

.segment-label {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 3px;
}

.segment-details {
  font-size: 0.85rem;
  opacity: 0.9;
  line-height: 1.3;
}

.seat-count {
  color: #FF579A;
  font-weight: 600;
}

/* Quick Actions */
.quick-actions {
  margin-top: 25px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #eaeaea;
}

.quick-actions h4 {
  color: #003870;
  font-size: 1rem;
  margin-bottom: 12px;
}

.quick-action-btn {
  width: 100%;
  padding: 10px;
  background: #003870;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-bottom: 8px;
  transition: 0.3s;
  text-align: center;
}

.quick-action-btn:hover:not(.disabled) {
  background: #002a54;
  transform: translateY(-1px);
}

.quick-action-btn.disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.quick-action-btn.secondary {
  background: #666;
}

.quick-action-btn.secondary:hover {
  background: #555;
}

/* Selection Progress */
.selection-progress {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #eaeaea;
}

.progress-label {
  font-weight: 600;
  color: #003870;
  margin-bottom: 10px;
  font-size: 0.95rem;
}

.progress-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.progress-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-text {
  width: 60px;
  font-size: 0.85rem;
  font-weight: 500;
  color: #333;
}

.progress-track {
  flex: 1;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #FF579A;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-count {
  width: 40px;
  text-align: right;
  font-size: 0.85rem;
  color: #666;
}

/* Next Segment Button */
.btn-next-segment {
  width: 100%;
  padding: 12px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 10px;
  transition: 0.3s;
  font-size: 0.95rem;
}

.btn-next-segment:hover {
  background: #218838;
  transform: translateY(-1px);
}

/* Update price summary for segments */
.price-line {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 0.9rem;
}

.price-line.total {
  font-weight: 800;
  color: #333;
  font-size: 1rem;
  padding-top: 10px;
  border-top: 1px dashed #ddd;
  margin-top: 10px;
}

/* Responsive */
@media (max-width: 1200px) {
  .seat-selection-grid {
    grid-template-columns: 250px 1fr 280px;
  }
}

@media (max-width: 992px) {
  .seat-selection-grid {
    grid-template-columns: 1fr;
    gap: 25px;
  }
  
  .seat-main {
    padding: 15px;
  }
  
  .aircraft-layout-container {
    order: 1;
  }
  
  .seat-passenger-list {
    order: 2; 
  }
  
  .map-legend {
    order: 3;
  }
  
  .flight-segment-tabs.seat-segment {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .seat-layout-wrapper {
    padding: 10px;
  }
  
  .aircraft-layout-container {
    padding: 15px;
  }
  
  .aircraft-capacity {
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
  
  .flight-segment-info {
    flex-direction: column;
    gap: 8px;
  }
}

/* Keep existing styles for other elements (p-seat-card, legend-card, etc.) */
/* Add these to your existing styles */

.p-seat-card { 
  padding: 15px; 
  border: 1px solid #eee; 
  border-radius: 10px; 
  margin-bottom: 10px; 
  cursor: pointer; 
  background: white; 
  transition: 0.3s;
}

.p-seat-card.active { 
  border-color: #d11241; 
  box-shadow: 0 4px 12px rgba(209, 18, 65, 0.1); 
}

.p-seat-card.has-seat { 
  border-left: 4px solid #28a745; 
}

.p-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.p-number {
  background: #003870;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
}

.p-name {
  font-weight: 600;
  color: #333;
  display: block;
}

.p-type {
  font-size: 0.75rem;
  color: #666;
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 10px;
  margin-top: 3px;
  display: inline-block;
}

.seat-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}

.p-assigned-seat {
  font-weight: 700;
  color: #003870;
  font-size: 0.95rem;
}

.change-seat-btn {
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1rem;
  transition: 0.2s;
  color: #666;
}

.change-seat-btn:hover {
  background: #e9ecef;
  border-color: #003870;
  color: #003870;
}

.seat-class-info {
  margin-top: 25px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #eaeaea;
}

.seat-class-info h4 {
  margin-top: 0;
  color: #003870;
  font-size: 1rem;
  margin-bottom: 12px;
}

.class-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  padding: 8px;
  background: white;
  border-radius: 6px;
  border: 1px solid #eee;
}

.class-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  flex-shrink: 0;
}

.class-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: #333;
}

.class-price {
  font-size: 0.8rem;
  color: #666;
}

.legend-card {
  background: white;
  padding: 20px;
  border-radius: 5px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.05);
  border: 1px solid #eee;
}

.legend-card h4 {
  color: #003870;
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.legend-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 20px;
}

.box {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid #ddd;
  flex-shrink: 0;
}

.box.available { 
  background: #fff; 
  border-color: #91d5ff;
}

.box.selected { 
  background: #d11241; 
  border-color: #a50d32;
}

.box.occupied { 
  background: #e0e0e0; 
  border-color: #bdbdbd;
}

.box.premium { 
  background: #ffd700; 
  border-color: #b8860b;
}

.selected-summary {
  margin-top: 20px;
}

.summary-divider {
  border-top: 1px solid #eee;
  margin: 15px 0;
}

.selected-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f9f9f9;
}

.selected-info {
  flex: 1;
}

.passenger-name {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
  display: block;
}

.seat-badge-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 3px;
}

.seat-mini-pill {
  background: #003870;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: bold;
}

.seat-class-label { 
  font-size: 0.65rem; 
  color: #666; 
}

.selected-price { 
  font-size: 0.85rem; 
  font-weight: 600; 
  color: #d11241; 
  display: flex; 
  align-items: center; 
  gap: 5px; 
}

.remove-btn {
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1rem;
  transition: 0.2s;
  color: #666;
}

.remove-btn:hover {
  background: #e9ecef;
  color: #d11241;
  border-color: #d11241;
}

.price-summary-box {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  margin-top: 15px;
  border: 1px solid #eee;
}

.summary-note {
  font-size: 0.65rem;
  color: #999;
  margin: 5px 0 0;
  font-style: italic;
  text-align: center;
}

.btn-confirm-seats { 
  width: 100%; 
  padding: 15px; 
  background: #003870; 
  color: white; 
  border: none; 
  border-radius: 8px; 
  font-weight: bold; 
  cursor: pointer; 
  margin-top: 20px;
  transition: 0.3s;
  font-size: 1rem;
}

.btn-confirm-seats:hover:not(.disabled) {
  background: #002a54;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 56, 112, 0.2);
}

.btn-confirm-seats.disabled { 
  background: #ccc; 
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #666;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #003870;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.seat-header {
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.back-link {
  background: none;
  border: none;
  color: #003870;
  cursor: pointer;
  font-size: 0.9rem;
  margin-bottom: 10px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 0;
}

.back-link:hover {
  color: #d11241;
  text-decoration: underline;
}

.seat-header h2 {
  color: #003870;
  font-size: 1.8rem;
  margin: 0 0 8px 0;
}

.flight-info {
  color: #555;
  font-size: 1rem;
  margin: 0;
  font-weight: 500;
  line-height: 1.4;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 500px;
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  margin: 20px auto;
  max-width: 600px;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.7;
}

.error-state h3 {
  color: #d11241;
  margin-bottom: 10px;
  font-size: 1.5rem;
}

.error-state p {
  color: #666;
  margin-bottom: 20px;
  max-width: 400px;
  line-height: 1.5;
}

.back-btn {
  background: #003870;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.3s;
  font-size: 1rem;
  margin-top: 10px;
}

.back-btn:hover {
  background: #002a54;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 56, 112, 0.2);
}

.aircraft-footer {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #eee;
  text-align: center;
}

.cabin-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #555;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  display: inline-block;
}

.legend-color.first { background-color: #8B4513; }
.legend-color.business { background-color: #4169E1; }
.legend-color.economy { background-color: #666; }
</style>