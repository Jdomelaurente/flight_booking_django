<template>
  <div class="flex flex-col lg:flex-row items-start justify-center bg-gray-100 min-h-screen py-10 px-4 lg:px-10 gap-8">
    
    <!-- Seat Legend (Left Side on Desktop) -->
    <div class="w-full lg:w-70 order-2 lg:order-1">
      <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-200 sticky top-10">
        <div class="text-center mb-6">
          <h2 class="font-bold text-gray-700 text-lg mb-1">Seat Legend</h2>
          <p class="text-xs text-gray-500">Understanding the seat map</p>
        </div>

        <!-- Seat Status -->
        <div class="mb-6">
          <h3 class="text-sm font-semibold text-gray-700 mb-3 pb-2 border-b">Seat Status</h3>
          <div class="space-y-3">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 bg-gray-100 border-2 border-gray-300 rounded-lg flex-shrink-0"></div>
              <div>
                <div class="text-xs font-medium text-gray-700">Occupied</div>
                <div class="text-[10px] text-gray-500">Already booked</div>
              </div>
            </div>
            
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 bg-amber-500 border-2 border-amber-600 rounded-lg flex-shrink-0"></div>
              <div>
                <div class="text-xs font-medium text-gray-700">Selected (Business)</div>
                <div class="text-[10px] text-gray-500">Your current selection</div>
              </div>
            </div>
            
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 bg-emerald-500 border-2 border-emerald-600 rounded-lg flex-shrink-0"></div>
              <div>
                <div class="text-xs font-medium text-gray-700">Selected (Comfort)</div>
                <div class="text-[10px] text-gray-500">Your current selection</div>
              </div>
            </div>
            
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 bg-blue-600 border-2 border-blue-700 rounded-lg flex-shrink-0"></div>
              <div>
                <div class="text-xs font-medium text-gray-700">Selected (Economy)</div>
                <div class="text-[10px] text-gray-500">Your current selection</div>
              </div>
            </div>
            
            <div class="grid grid-cols-3 gap-2 mt-4">
              <div class="text-center">
                <div class="w-6 h-6 mx-auto bg-white border-2 border-amber-200 rounded-lg mb-1"></div>
                <div class="text-[10px] text-gray-600">Available<br>Business</div>
              </div>
              <div class="text-center">
                <div class="w-6 h-6 mx-auto bg-white border-2 border-emerald-200 rounded-lg mb-1"></div>
                <div class="text-[10px] text-gray-600">Available<br>Comfort</div>
              </div>
              <div class="text-center">
                <div class="w-6 h-6 mx-auto bg-white border-2 border-blue-100 rounded-lg mb-1"></div>
                <div class="text-[10px] text-gray-600">Available<br>Economy</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Seat Attributes -->
        <div class="mb-6">
          <h3 class="text-sm font-semibold text-gray-700 mb-3 pb-2 border-b">Special Seats</h3>
          <div class="space-y-3">
            <div v-for="(attr, key) in seatAttributeLegend" :key="key" 
                 class="flex items-center gap-3">
              <div :class="attr.color" class="w-6 h-6 rounded-lg flex items-center justify-center text-xs text-white flex-shrink-0">
                <span v-html="attr.icon"></span>
              </div>
              <div>
                <div class="text-xs font-medium text-gray-700">{{ attr.label }}</div>
                <div class="text-[10px] text-gray-500">{{ attr.description }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Position Types -->
        <div>
          <h3 class="text-sm font-semibold text-gray-700 mb-3 pb-2 border-b">Position Types</h3>
          <div class="grid grid-cols-2 gap-2">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-blue-500"></div>
              <span class="text-xs text-gray-700">Window</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-green-500"></div>
              <span class="text-xs text-gray-700">Aisle</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-yellow-500"></div>
              <span class="text-xs text-gray-700">Middle</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-purple-500"></div>
              <span class="text-xs text-gray-700">Bulkhead</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-red-500"></div>
              <span class="text-xs text-gray-700">Exit Row</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-emerald-500"></div>
              <span class="text-xs text-gray-700">Extra Legroom</span>
            </div>
          </div>
        </div>

        <!-- Class Summary -->
        <div class="mt-6 pt-6 border-t">
          <h3 class="text-sm font-semibold text-gray-700 mb-3">Cabin Summary</h3>
          <div class="space-y-3">
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-amber-500"></div>
                <span class="text-xs text-gray-700">Business Class</span>
              </div>
              <span class="text-xs font-medium">{{ businessClassSeatsCount }}</span>
            </div>
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-emerald-500"></div>
                <span class="text-xs text-gray-700">Comfort Class</span>
              </div>
              <span class="text-xs font-medium">{{ comfortClassSeatsCount }}</span>
            </div>
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-blue-500"></div>
                <span class="text-xs text-gray-700">Economy Class</span>
              </div>
              <span class="text-xs font-medium">{{ economyClassSeatsCount }}</span>
            </div>
            <div class="pt-3 border-t mt-3">
              <div class="flex justify-between">
                <span class="text-sm font-bold text-gray-700">Total Seats:</span>
                <span class="text-sm font-bold text-gray-900">{{ totalSeats }}</span>
              </div>
              <div class="flex justify-between mt-1">
                <span class="text-xs text-gray-600">Available:</span>
                <span class="text-xs font-medium text-green-600">{{ availableSeatsCount }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Seat Map (Right Side on Desktop) -->
    <div class="max-w-lg lg:flex-1 order-1 lg:order-2">
      <div class="bg-white border-x-8 border-t-[60px] border-gray-300 rounded-t-[120px] w-full max-w-md lg:max-w-none px-6 py-8 shadow-2xl">
        
        <div class="text-center mb-8">
          <h1 class="font-bold text-gray-700 tracking-widest uppercase text-xl">Airbus A321</h1>
          <p class="text-xs text-gray-500 mt-1">FLIGHT MAP - Seat Selection</p>
          <div class="mt-4 flex justify-center gap-4">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-amber-500"></div>
              <span class="text-xs text-gray-600">Business</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-emerald-500"></div>
              <span class="text-xs text-gray-600">Comfort</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-blue-500"></div>
              <span class="text-xs text-gray-600">Economy</span>
            </div>
          </div>
          <div class="mt-2 text-sm text-gray-600" v-if="scheduleInfo">
            Flight: {{ scheduleInfo.flightNumber }} | {{ scheduleInfo.origin }} → {{ scheduleInfo.destination }}
          </div>
        </div>

        <div class="space-y-8">
          
          <!-- Business Class -->
          <section >
            <div class="text-center mb-3">
              <span class="text-xs font-bold text-amber-600 bg-amber-50 px-4 py-2 rounded-full border border-amber-200">BUSINESS CLASS</span>
            </div>
            <div class="grid grid-cols-5 gap-5 items-center px-4 mx-auto">
              <template v-for="row in 4" :key="'biz-'+row">
                <button 
                  v-for="col in ['A', 'C']" 
                  :key="col" 
                  @click="toggleSeat(row, col, 'business')"
                  :class="getSeatClass(row, col, 'business')"
                  class="h-12 w-12 rounded-sm border-2 flex items-center justify-center font-bold transition-all group relative"
                  :disabled="isSeatOccupied(row, col)"
                >
                  {{ col }}
                  <div v-if="getSeatAttributes(row, col).tags.length > 0" 
                    :class="getAttributeBadgeColor(row, col)"
                    class="absolute -top-1 -right-1 w-4 h-4 rounded-full text-[10px] text-white flex items-center justify-center">
                    <span v-html="getAttributeIcon(row, col)"></span>
                  </div>
                </button>

                <div class="text-center text-sm font-bold text-gray-700">{{ row }}</div>

                <button 
                  v-for="col in ['D', 'F']" 
                  :key="col" 
                  @click="toggleSeat(row, col, 'business')"
                  :class="getSeatClass(row, col, 'business')"
                  class="h-12 w-12 rounded-sm border-2 flex items-center justify-center font-bold transition-all group relative"
                  :disabled="isSeatOccupied(row, col)"
                >
                  {{ col }}
                  <div v-if="getSeatAttributes(row, col).tags.length > 0" 
                    :class="getAttributeBadgeColor(row, col)"
                    class="absolute -top-1 -right-1 w-4 h-4 rounded-full text-[10px] text-white flex items-center justify-center">
                    <span v-html="getAttributeIcon(row, col)"></span>
                  </div>
                </button>
              </template>
            </div>
            <div class="text-center mt-2 text-xs text-gray-500">
              Rows 1-4 • 34" Pitch • Full Recline
            </div>
          </section>

          <hr class="border-dashed border-gray-300" />

          <!-- Comfort Class -->
          <section>
            <div class="text-center mb-3">
              <span class="text-xs font-bold text-emerald-600 bg-emerald-50 px-4 py-2 rounded-full border border-emerald-200">COMFORT CLASS</span>
            </div>
            <div class="grid grid-cols-7 gap-4 items-center px-2">
              <template v-for="row in 5" :key="'comfort-'+row">
                <button 
                  v-for="col in ['A', 'B', 'C']" 
                  :key="col" 
                  @click="toggleSeat(row + 4, col, 'comfort')"
                  :class="getSeatClass(row + 4, col, 'comfort')"
                  class="h-10 w-10 rounded-sm border flex items-center justify-center text-sm transition-all group relative"
                  :disabled="isSeatOccupied(row + 4, col)"
                >
                  {{ col }}
                  <div v-if="getSeatAttributes(row + 4, col).tags.length > 0" 
                    :class="getAttributeBadgeColor(row + 4, col)"
                    class="absolute -top-1 -right-1 w-2 h-2 rounded-full text-[8px] text-white flex items-center justify-center">
                    <span v-html="getAttributeIcon(row + 4, col)"></span>
                  </div>
                </button>

                <div class="text-center text-sm font-bold text-gray-700">{{ row + 4 }}</div>

                <button 
                  v-for="col in ['D', 'E', 'F']" 
                  :key="col" 
                  @click="toggleSeat(row + 4, col, 'comfort')"
                  :class="getSeatClass(row + 4, col, 'comfort')"
                  class="h-10 w-10 rounded-sm border flex items-center justify-center text-sm transition-all group relative"
                  :disabled="isSeatOccupied(row + 4, col)"
                >
                  {{ col }}
                  <div v-if="getSeatAttributes(row + 4, col).tags.length > 0" 
                    :class="getAttributeBadgeColor(row + 4, col)"
                    class="absolute -top-1 -right-1 w-2 h-2 rounded-full text-[8px] text-white flex items-center justify-center">
                    <span v-html="getAttributeIcon(row + 4, col)"></span>
                  </div>
                </button>
              </template>
            </div>
            <div class="text-center mt-2 text-xs text-gray-500">
              Rows 5-9 • 34" Pitch • Priority Boarding
            </div>
          </section>

          <hr class="border-dashed border-gray-300" />

          <!-- Economy Class -->
          <section>
            <div class="text-center mb-3">
              <span class="text-xs font-bold text-blue-600 bg-blue-50 px-4 py-2 rounded-full border border-blue-200">ECONOMY CLASS</span>
            </div>
            <div class="grid grid-cols-7 gap-3 items-center">
              <template v-for="row in 28" :key="'econ-'+row">
                <button 
                  v-for="col in ['A', 'B', 'C']" 
                  :key="col" 
                  @click="toggleSeat(row + 9, col, 'economy')"
                  :class="getSeatClass(row + 9, col, 'economy')"
                  class="h-9 w-9 rounded-sm border flex items-center justify-center text-xs transition-all group relative"
                  :disabled="isSeatOccupied(row + 9, col)"
                >
                  {{ col }}
                  <div v-if="getSeatAttributes(row + 9, col).tags.length > 0" 
                    :class="getAttributeBadgeColor(row + 9, col)"
                    class="absolute -top-1 -right-1 w-2 h-2 rounded-full text-[8px] text-white flex items-center justify-center">
                    <span v-html="getAttributeIcon(row + 9, col)"></span>
                  </div>
                </button>

                <div class="text-center text-xs font-bold text-gray-700">{{ row + 9 }}</div>

                <button 
                  v-for="col in ['D', 'E', 'F']" 
                  :key="col" 
                  @click="toggleSeat(row + 9, col, 'economy')"
                  :class="getSeatClass(row + 9, col, 'economy')"
                  class="h-9 w-9 rounded-sm border flex items-center justify-center text-xs transition-all group relative"
                  :disabled="isSeatOccupied(row + 9, col)"
                >
                  {{ col }}
                  <div v-if="getSeatAttributes(row + 9, col).tags.length > 0" 
                    :class="getAttributeBadgeColor(row + 9, col)"
                    class="absolute -top-1 -right-1 w-2 h-2 rounded-full text-[8px] text-white flex items-center justify-center">
                    <span v-html="getAttributeIcon(row + 9, col)"></span>
                  </div>
                </button>
              </template>
              <div class="col-span-7 text-center py-4 text-xs text-gray-500">
                Rows 10-37 • 31" Pitch • Standard Service
                <div class="mt-1 text-[10px] text-gray-400">Exit Rows: 11 & 26 • Limited Recline: 10, 25, 37</div>
              </div>
            </div>
          </section>

        </div>

        <!-- Seat Selection Summary -->
        <div class="mt-8 p-6 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl border border-gray-200">
          <div class="text-sm font-bold text-gray-700 mb-3">CURRENT SELECTION</div>
          <div v-if="selectedSeatCode" class="space-y-6">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-4">
                <div :class="getSeatClassColor(selectedSeatCode)" class="w-12 h-12 rounded-lg border-2 flex items-center justify-center font-bold text-lg">
                  {{ getSeatColumn(selectedSeatCode) }}
                </div>
                <div>
                  <div class="font-bold text-xl">{{ selectedSeatCode }}</div>
                  <div class="text-xs text-gray-500">{{ getSeatClassLabel(selectedSeatCode) }}</div>
                  <div v-if="selectedSeatPassenger" class="text-xs text-gray-600 mt-1">
                    For: {{ selectedSeatPassenger }}
                  </div>
                </div>
              </div>
              <button @click="deselectSeat" class="text-xs text-red-500 hover:text-red-700 px-3 py-1 hover:bg-red-50 rounded-lg">
                Change Seat
              </button>
            </div>
            
            <div v-if="selectedSeatAttributes" class="border-t pt-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <div class="text-xs font-semibold text-gray-500 mb-2">POSITION</div>
                  <div class="flex flex-wrap gap-2">
                    <span v-for="tag in selectedSeatAttributes.tags" :key="tag"
                      :class="getTagClass(tag)"
                      class="text-xs px-3 py-1 rounded-full font-medium">
                      {{ tag }}
                    </span>
                  </div>
                </div>
                
                <div>
                  <div class="text-xs font-semibold text-gray-500 mb-2">PRICE</div>
                  <div class="text-lg font-bold" :class="getPriceClass(selectedSeatAttributes.price)">
                    {{ selectedSeatAttributes.price }}
                    <div class="text-xs font-normal text-gray-500 mt-1">
                      {{ selectedSeatAttributes.price.includes('+') ? 'Premium' : selectedSeatAttributes.price.includes('-') ? 'Discount' : 'Standard' }} fare
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-if="selectedSeatAttributes.features.length > 0" class="mt-4">
                <div class="text-xs font-semibold text-gray-500 mb-2">FEATURES</div>
                <div class="grid grid-cols-2 gap-2">
                  <div v-for="feature in selectedSeatAttributes.features" :key="feature" 
                       class="flex items-center text-xs text-gray-600">
                    <span class="w-1.5 h-1.5 bg-gray-400 rounded-full mr-2"></span>
                    {{ feature }}
                  </div>
                </div>
              </div>
              
              <div class="mt-6 pt-4 border-t">
                <button @click="confirmSelection" class="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white py-3 rounded-xl text-sm font-semibold hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg hover:shadow-xl">
                  Confirm Seat {{ selectedSeatCode }}
                </button>
                <div class="text-center mt-3 text-xs text-gray-500">
                  Free cancellation up to 24 hours before departure
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8">
            <div class="text-gray-400 mb-3">
              <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/>
              </svg>
            </div>
            <div class="text-gray-600 font-medium">No seat selected</div>
            <div class="text-xs text-gray-400 mt-1">Click on an available seat above to select</div>
            <div class="text-xs text-gray-500 mt-2" v-if="activePassenger">
              Currently selecting for: {{ activePassenger.firstName }} {{ activePassenger.lastName }}
            </div>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="mt-6 grid grid-cols-3 gap-3 text-center">
          <div class="p-3 bg-amber-50 rounded-lg border border-amber-100">
            <div class="text-xs font-bold text-amber-700">Business</div>
            <div class="text-[10px] text-amber-600">{{ businessClassSeatsCount }} seats</div>
            <div class="text-[9px] text-amber-500">{{ businessClassAvailableCount }} available</div>
          </div>
          <div class="p-3 bg-emerald-50 rounded-lg border border-emerald-100">
            <div class="text-xs font-bold text-emerald-700">Comfort</div>
            <div class="text-[10px] text-emerald-600">{{ comfortClassSeatsCount }} seats</div>
            <div class="text-[9px] text-emerald-500">{{ comfortClassAvailableCount }} available</div>
          </div>
          <div class="p-3 bg-blue-50 rounded-lg border border-blue-100">
            <div class="text-xs font-bold text-blue-700">Economy</div>
            <div class="text-[10px] text-blue-600">{{ economyClassSeatsCount }} seats</div>
            <div class="text-[9px] text-blue-500">{{ economyClassAvailableCount }} available</div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, defineProps, onMounted } from 'vue';
import { useNotificationStore } from '@/stores/notification';

const props = defineProps({
  seats: {
    type: Array,
    default: () => []
  },
  selectedSeats: {
    type: Object,
    default: () => ({})
  },
  activePassenger: {
    type: Object,
    default: null
  },
  onSeatSelect: {
    type: Function,
    default: () => {}
  },
  onSeatHover: {
    type: Function,
    default: () => {}
  },
  occupiedSeats: {
    type: Array,
    default: () => []
  },
  passengerList: {
    type: Array,
    default: () => []
  },
  scheduleInfo: {
    type: Object,
    default: () => ({})
  }
});

const notificationStore = useNotificationStore();
const selectedSeatCode = ref(null);
const seatAttributeLegend = ref({
  'bulkhead': { 
    color: 'bg-purple-500', 
    label: 'Bulkhead Seat', 
    description: 'No seat in front, extra legroom',
    icon: 'W'
  },
  'exitRow': { 
    color: 'bg-red-500', 
    label: 'Exit Row', 
    description: 'Maximum legroom, emergency access',
    icon: 'E'
  },
  'limitedRecline': { 
    color: 'bg-orange-500', 
    label: 'Limited Recline', 
    description: 'Limited or no recline',
    icon: 'R'
  },
  'extraLegroom': { 
    color: 'bg-emerald-500', 
    label: 'Extra Legroom', 
    description: 'Additional legroom seat',
    icon: 'L'
  },
});

// Debug function to log seat data
const debugSeatData = () => {
  console.log('🔍 DEBUG: Total seats from props:', props.seats.length);
  if (props.seats.length > 0) {
    console.log('First 3 seats:', props.seats.slice(0, 3).map(s => ({
      id: s.id,
      seat_code: s.seat_code,
      row: s.row,
      column: s.column,
      is_available: s.is_available
    })));
  }
};

// Helper function to get default attributes for a seat
const getDefaultAttributes = (row, col) => {
  const tags = [];
  const features = [];
  let legendKey = null;
  
  // Lateral position
  if (col === 'A' || col === 'F') tags.push("Window");
  else if (col === 'B' || col === 'E') tags.push("Middle");
  else if (col === 'C' || col === 'D') tags.push("Aisle");
  
  // Row-specific attributes (A321 specific)
  if (row === 1) {
    tags.push("Bulkhead");
    features.push("No seat in front");
    legendKey = 'bulkhead';
  }
  
  if (row === 11 || row === 26) {
    tags.push("Exit Row");
    features.push("Maximum legroom");
    legendKey = 'exitRow';
  }
  
  if (row === 10 || row === 25 || row === 37) {
    tags.push("Limited Recline");
    features.push("Limited recline");
    legendKey = 'limitedRecline';
  }
  
  if (row >= 5 && row <= 9) {
    features.push("Extra legroom (34\" pitch)");
    if (row === 5) legendKey = 'extraLegroom';
  }
  
  // Price based on class
  let price = "";
  if (row <= 4) price = "+₱1500";
  else if (row <= 9) price = "+₱800";
  else price = "Standard";
  
  return { tags, price, features, legendKey };
};

// Get seat from database by row and column
const getSeatFromDB = (row, col) => {
  const seatCode = `${row}${col}`;
  
  // Try to find the seat
  const seat = props.seats.find(seat => {
    // Check seat_code first
    if (seat.seat_code === seatCode) {
      return true;
    }
    
    // Check row and column
    if (seat.row === row && seat.column === col) {
      return true;
    }
    
    // Check seat_number
    if (seat.seat_number === seatCode) {
      return true;
    }
    
    return false;
  });
  
  return seat || null;
};

// Check if seat is occupied
const isSeatOccupied = (row, col) => {
  const seat = getSeatFromDB(row, col);
  if (!seat) return true; // Seat doesn't exist in database
  
  // Check if seat is already occupied in database
  if (!seat.is_available) return true;
  
  // Check if seat is occupied in our occupied list
  const seatCode = `${row}${col}`;
  return props.occupiedSeats.includes(seatCode);
};

// Get seat attributes from database or defaults
const getSeatAttributes = (row, col) => {
  const seat = getSeatFromDB(row, col);
  
  if (seat) {
    // Get attributes from database
    const attributes = {
      tags: [],
      price: "",
      features: [],
      legendKey: null
    };
    
    // Add position tags
    if (seat.is_window) attributes.tags.push("Window");
    if (seat.is_aisle) attributes.tags.push("Aisle");
    if (!seat.is_window && !seat.is_aisle) attributes.tags.push("Middle");
    
    // Add special features
    if (seat.has_extra_legroom) {
      attributes.tags.push("Extra Legroom");
      attributes.features.push("Extra legroom");
      attributes.legendKey = 'extraLegroom';
    }
    
    if (seat.is_exit_row) {
      attributes.tags.push("Exit Row");
      attributes.features.push("Maximum legroom");
      attributes.legendKey = 'exitRow';
    }
    
    if (seat.is_bulkhead) {
      attributes.tags.push("Bulkhead");
      attributes.features.push("No seat in front");
      attributes.legendKey = 'bulkhead';
    }
    
    // Add price adjustment
    const priceAdj = parseFloat(seat.price_adjustment) || 0;
    const basePrice = parseFloat(seat.final_price) || 0;
    
    if (priceAdj > 0) {
      attributes.price = `+₱${priceAdj.toLocaleString()}`;
    } else if (priceAdj < 0) {
      attributes.price = `-₱${Math.abs(priceAdj).toLocaleString()}`;
    } else if (basePrice > 0) {
      attributes.price = `₱${basePrice.toLocaleString()}`;
    } else {
      attributes.price = "Standard";
    }
    
    return attributes;
  }
  
  // Fallback to default attributes if seat not found in database
  return getDefaultAttributes(row, col);
};

const getAttributeBadgeColor = (row, col) => {
  const attributes = getSeatAttributes(row, col);
  if (!attributes.legendKey) return 'bg-gray-400';
  
  switch(attributes.legendKey) {
    case 'bulkhead': return 'bg-purple-500';
    case 'exitRow': return 'bg-red-500';
    case 'limitedRecline': return 'bg-orange-500';
    case 'extraLegroom': return 'bg-emerald-500';
    default: return 'bg-gray-400';
  }
};

const getAttributeIcon = (row, col) => {
  const attributes = getSeatAttributes(row, col);
  if (!attributes.legendKey) return 'i';
  
  switch(attributes.legendKey) {
    case 'bulkhead': return 'W';
    case 'exitRow': return 'E';
    case 'limitedRecline': return 'R';
    case 'extraLegroom': return 'L';
    default: return 'i';
  }
};

const getSeatClass = (row, col, seatType) => {
  const seatCode = `${row}${col}`;
  const seat = getSeatFromDB(row, col);
  
  if (!seat) {
    console.log(`Seat ${seatCode} not found in database`);
    return 'bg-gray-100 border-gray-300 text-gray-400 cursor-not-allowed';
  }
  
  const isOccupied = isSeatOccupied(row, col);
  
  if (isOccupied) {
    return 'bg-gray-100 border-gray-300 text-gray-400 cursor-not-allowed';
  }

  const isSelected = selectedSeatCode.value === seatCode;
  
  if (isSelected) {
    switch(seatType) {
      case 'business':
        return 'bg-amber-500 border-amber-600 text-white shadow-lg scale-105';
      case 'comfort':
        return 'bg-emerald-500 border-emerald-600 text-white shadow-lg scale-105';
      case 'economy':
        return 'bg-blue-600 border-blue-700 text-white shadow-md scale-105';
      default:
        return 'bg-gray-500 border-gray-600 text-white';
    }
  }

  return seatType === 'business'
    ? 'bg-white border-amber-300 text-amber-700 hover:bg-amber-50 hover:border-amber-400'
    : seatType === 'comfort'
    ? 'bg-white border-emerald-300 text-emerald-700 hover:bg-emerald-50 hover:border-emerald-400'
    : 'bg-white border-blue-200 text-blue-600 hover:bg-blue-50 hover:border-blue-300';
};

const getSeatClassColor = (seatId) => {
  if (!seatId) return 'bg-gray-100 border-gray-300 text-gray-400';
  
  const row = getSeatRowFromCode(seatId);
  const col = getSeatColumnFromCode(seatId);
  const seat = getSeatFromDB(row, col);
  
  if (!seat || !seat.is_available) return 'bg-gray-100 border-gray-300 text-gray-400';
  
  if (row <= 4) return 'bg-amber-500 border-amber-600 text-white';
  if (row <= 9) return 'bg-emerald-500 border-emerald-600 text-white';
  return 'bg-blue-600 border-blue-700 text-white';
};

// Helper functions to extract row and column from seat code
const getSeatRowFromCode = (seatCode) => {
  if (!seatCode) return 0;
  const match = seatCode.match(/\d+/);
  return match ? parseInt(match[0]) : 0;
};

const getSeatColumnFromCode = (seatCode) => {
  if (!seatCode) return '';
  const match = seatCode.match(/[A-F]/);
  return match ? match[0] : '';
};

const getSeatColumn = (seatCode) => {
  return getSeatColumnFromCode(seatCode);
};

const toggleSeat = (row, col, seatType) => {
  const seatCode = `${row}${col}`;
  
  if (isSeatOccupied(row, col)) {
    console.log(`Seat ${seatCode} is occupied`);
    return;
  }
  
  const seat = getSeatFromDB(row, col);
  if (!seat) {
    console.error(`Seat ${seatCode} not found in database`);
    return;
  }
  
  if (selectedSeatCode.value === seatCode) {
    selectedSeatCode.value = null;
  } else {
    selectedSeatCode.value = seatCode;
    if (props.onSeatSelect) {
      props.onSeatSelect(seat);
    }
  }
};

const getSeatClassLabel = (seatId) => {
  if (!seatId) return 'No seat selected';
  const row = getSeatRowFromCode(seatId);
  if (row <= 4) return 'Business Class • Priority Service';
  if (row <= 9) return 'Comfort Class • Extra Legroom';
  return 'Economy Class • Standard Service';
};

const getTagClass = (tag) => {
  const classes = {
    'Window': 'bg-blue-100 text-blue-700 border border-blue-200',
    'Aisle': 'bg-green-100 text-green-700 border border-green-200',
    'Middle': 'bg-yellow-100 text-yellow-700 border border-yellow-200',
    'Bulkhead': 'bg-purple-100 text-purple-700 border border-purple-200',
    'Exit Row': 'bg-red-100 text-red-700 border border-red-200',
    'Extra Legroom': 'bg-emerald-100 text-emerald-700 border border-emerald-200',
    'Limited Recline': 'bg-orange-100 text-orange-700 border border-orange-200'
  };
  return classes[tag] || 'bg-gray-100 text-gray-700 border border-gray-200';
};

const getPriceClass = (price) => {
  if (!price) return 'text-gray-600';
  if (price.includes('+')) return 'text-green-600';
  if (price.includes('-')) return 'text-red-600';
  return 'text-gray-600';
};

const confirmSelection = () => {
  if (selectedSeatCode.value && props.onSeatSelect) {
    const row = getSeatRowFromCode(selectedSeatCode.value);
    const col = getSeatColumnFromCode(selectedSeatCode.value);
    const seat = getSeatFromDB(row, col);
    
    if (seat) {
      props.onSeatSelect(seat);
      
      // Show confirmation message
      const seatInfo = getSeatAttributes(row, col);
      const message = `✅ Seat ${selectedSeatCode.value} confirmed!\n\n` +
                     `Class: ${getSeatClassLabel(selectedSeatCode.value)}\n` +
                     `Price Adjustment: ${seatInfo.price}\n` +
                     `Features: ${seatInfo.features.join(', ')}`;
      
      notificationStore.success(message);
    }
  }
};

const deselectSeat = () => {
  selectedSeatCode.value = null;
};

// Computed properties for statistics
const totalSeats = computed(() => props.seats.length);
const availableSeatsCount = computed(() => 
  props.seats.filter(seat => seat.is_available).length
);

const businessClassSeats = computed(() => 
  props.seats.filter(seat => {
    const row = seat.row || 0;
    return row <= 4;
  })
);

const comfortClassSeats = computed(() => 
  props.seats.filter(seat => {
    const row = seat.row || 0;
    return row >= 5 && row <= 9;
  })
);

const economyClassSeats = computed(() => 
  props.seats.filter(seat => {
    const row = seat.row || 0;
    return row >= 10;
  })
);

const businessClassSeatsCount = computed(() => businessClassSeats.value.length);
const comfortClassSeatsCount = computed(() => comfortClassSeats.value.length);
const economyClassSeatsCount = computed(() => economyClassSeats.value.length);

const businessClassAvailableCount = computed(() => 
  businessClassSeats.value.filter(seat => seat.is_available).length
);

const comfortClassAvailableCount = computed(() => 
  comfortClassSeats.value.filter(seat => seat.is_available).length
);

const economyClassAvailableCount = computed(() => 
  economyClassSeats.value.filter(seat => seat.is_available).length
);

// Selected seat attributes
const selectedSeatAttributes = computed(() => {
  if (!selectedSeatCode.value) return null;
  
  const row = getSeatRowFromCode(selectedSeatCode.value);
  const col = getSeatColumnFromCode(selectedSeatCode.value);
  return getSeatAttributes(row, col);
});

// Selected seat passenger
const selectedSeatPassenger = computed(() => {
  if (!selectedSeatCode.value) return null;
  
  for (const [passengerKey, seat] of Object.entries(props.selectedSeats)) {
    if (seat && seat.seat_code === selectedSeatCode.value) {
      const passenger = props.passengerList.find(p => p.key === passengerKey);
      return passenger ? `${passenger.firstName} ${passenger.lastName}` : null;
    }
  }
  return null;
});

// Watch for active passenger changes to clear selection
watch(() => props.activePassenger, () => {
  selectedSeatCode.value = null;
});

// Watch for seat selection from parent
watch(() => props.selectedSeats, (newSelectedSeats) => {
  // Find if current passenger has a seat
  if (props.activePassenger && newSelectedSeats[props.activePassenger.key]) {
    selectedSeatCode.value = newSelectedSeats[props.activePassenger.key].seat_code;
  }
}, { deep: true });

// Debug on mount
onMounted(() => {
  debugSeatData();
  console.log('🔍 Airbus component mounted');
  console.log('Active passenger:', props.activePassenger);
  console.log('Selected seats:', props.selectedSeats);
});
</script>