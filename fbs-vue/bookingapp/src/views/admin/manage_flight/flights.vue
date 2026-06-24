<template>
  <div class="p-6 poppins">
    <!-- Header & Tools Section -->
    <AdminTableTool 
      v-model="searchQuery" 
      placeholder="Search flight number..."
    >
      <template #filters>
        <div class="flex items-center gap-2">
          <select 
            v-model="filterAirline"
            class="text-[11px] font-bold border border-gray-200 px-3 py-2 bg-white rounded-[1px] outline-none focus:border-[#fe3787] poppins cursor-pointer min-w-[150px]"
          >
            <option value="all">Any Airline</option>
            <option v-for="airline in airlines" :key="airline.id" :value="airline.id">
              {{ airline.name }}
            </option>
          </select>
        </div>
      </template>

      <template #actions>
        <div class="flex items-center gap-2">
          <button 
            @click="showImportModal = true" 
            class="bg-[#002D1E] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#014d33] font-semibold poppins text-[12px] rounded-[1px] shadow-sm transition-all"
          >
            <i class="ph ph-file-csv text-[14px]"></i> Import
          </button>
          <button 
            @click="openModal()" 
            class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[12px] rounded-[1px] shadow-sm transition-all"
          >
            <i class="ph ph-plus text-[14px]"></i> Add
          </button>
        </div>
      </template>
    </AdminTableTool>

    <!-- Import Modal -->
    <ImportModal 
      :show="showImportModal" 
      title="Flights" 
      model-type="flights" 
      @close="showImportModal = false"
      @refresh="fetchData"
    />

    <!-- Stats Section -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div 
        v-for="(count, label) in statsItems" 
        :key="label" 
        class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins leading-none mb-2">{{ label }}</p>
            <p class="text-2xl font-bold text-[#002D1E] poppins">{{ count }}</p>
          </div>
          <div :class="statIconClass(label)" class="w-12 h-12 rounded-full flex items-center justify-center">
            <i :class="[statIcon(label), 'text-xl']"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Table Section -->
    <div class="bg-white border border-gray-200 rounded-[1px] overflow-hidden shadow-sm">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins uppercase">Flight #</th>
            <th class="px-6 py-4 poppins uppercase">Airline</th>
            <th class="px-6 py-4 poppins uppercase">Aircraft</th>
            <th class="px-6 py-4 poppins uppercase">Route</th>
            <th class="px-6 py-4 poppins uppercase text-center">Total Stops</th>
            <th class="px-6 py-4 poppins uppercase">Layovers</th>
            <th class="px-6 py-4 poppins uppercase text-center">Profile Status</th>
            <th class="px-6 py-4 poppins text-right uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr 
            v-for="f in flights" 
            :key="f.id" 
            :id="`flight-row-${f.id}`"
            :class="{'highlight-active': highlightedId === f.id}"
            class="hover:bg-gray-50/50 transition-all text-[12px] font-medium"
          >
            <td class="px-6 py-4">
              <div class="flex flex-col gap-1">
                <router-link 
                  :to="{ name: 'ManageRoutes', query: { highlight: f.route } }" 
                  class="font-bold text-[#fe3787] poppins text-sm hover:underline hover:text-[#fb1873] transition-all flex items-center gap-1 group"
                  title="View Route Connection"
                >
                  {{ f.flight_number }}
                  <i class="ph ph-link-simple text-[10px] opacity-0 group-hover:opacity-100 transition-opacity"></i>
                </router-link>
                <div class="flex items-center gap-1 mt-1">
                  <span class="text-[9px] text-gray-400 font-bold uppercase tracking-tighter poppins">Internal ID: {{ f.id }}</span>
                  <div class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" title="Connected to Backend"></div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center">
                  <i class="ph ph-buildings text-blue-600"></i>
                </div>
                <router-link 
                  :to="{ name: 'AdminAirlines', query: { highlight: f.airline } }"
                  class="font-bold text-[#002D1E] poppins hover:text-[#fe3787] transition-all"
                  title="View Airline Connection"
                >
                  {{ f.airline_display }}
                </router-link>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-2">
                <i class="ph ph-airplane-tilt text-purple-600"></i>
                <router-link 
                  :to="{ name: 'AdminAircraft', query: { highlight: f.aircraft } }"
                  class="text-gray-700 poppins hover:text-[#fe3787] transition-all font-medium"
                  title="View Aircraft Connection"
                >
                  {{ f.aircraft_display }}
                </router-link>
              </div>
            </td>
            <td class="px-6 py-4">
              <router-link 
                :to="{ name: 'ManageRoutes', query: { highlight: f.route } }"
                class="bg-purple-100 text-purple-700 px-3 py-1 rounded-[1px] text-[10px] font-bold uppercase poppins tracking-tight hover:bg-[#fe3787] hover:text-white transition-all inline-block"
                title="View Route Details"
              >
                {{ f.route_display || 'No Route' }}
              </router-link>
            </td>
            <td class="px-6 py-4 text-center">
              <span 
                :class="f.total_stops > 0 ? 'bg-orange-50 text-orange-600 border border-orange-100' : 'bg-gray-50 text-gray-400 border border-gray-100'"
                class="px-2.5 py-1 rounded-[1px] text-[10px] font-bold uppercase poppins"
              >
                {{ f.total_stops === 0 ? 'Direct' : `${f.total_stops} Stop${f.total_stops > 1 ? 's' : ''}` }}
              </span>
            </td>
            <td class="px-6 py-4">
              <div class="flex flex-wrap gap-1 max-w-[200px]">
                <span 
                  v-for="(layover, lIdx) in getLayoversList(f.layovers_data)" 
                  :key="lIdx"
                  class="bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded-[1px] text-[9px] font-semibold poppins border border-gray-200/50"
                  :title="`Layover at ${layover.city || layover.airport}`"
                >
                  {{ layover.airport }} <span class="text-gray-400 font-medium">({{ layover.duration || 'no time' }})</span>
                </span>
                <span v-if="!f.total_stops" class="text-gray-300 italic text-[11px]">None</span>
              </div>
            </td>
            <td class="px-6 py-4 text-center">
              <span 
                :class="f.is_active !== false ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500'"
                class="px-3 py-1 rounded-[1px] text-[9px] font-black uppercase poppins border"
              >
                {{ f.is_active !== false ? 'Active Profile' : 'Inactive' }}
              </span>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="openModal(f)" class="text-green-600 hover:text-green-400 p-2 transition-colors">
                  <i class="ph ph-pencil-simple text-lg"></i>
                </button>
                <button @click="deleteFlight(f.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors">
                  <i class="ph ph-trash text-lg"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="flights.length === 0">
            <td colspan="5" class="px-6 py-10 text-center text-gray-400 italic poppins">No flights found. Please add one.</td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination Section -->
      <div v-if="totalRecords > itemsPerPage" class="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
        <div class="flex items-center justify-between">
          <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
            Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ totalRecords }}
          </div>
          <div class="flex gap-1">
            <button 
              @click="prevPage" 
              :disabled="currentPage === 1"
              class="px-4 py-2 bg-white border border-gray-200 rounded-[1px] text-xs font-bold uppercase hover:bg-gray-50 disabled:opacity-50 poppins transition-all shadow-sm"
            >
              Prev
            </button>
            <button 
              v-for="page in visiblePages" 
              :key="page"
              @click="goToPage(page)"
              :disabled="page === '...'"
              :class="[
                'px-4 py-2 border rounded-[1px] text-xs font-bold uppercase poppins transition-all shadow-sm',
                page === '...' ? 'bg-white border-gray-200 text-gray-400' : 
                currentPage === page ? 'bg-[#fe3787] text-white border-[#fe3787]' : 'bg-white border-gray-200 text-[#002D1E] hover:bg-gray-50'
              ]"
            >
              {{ page }}
            </button>
            <button 
              @click="nextPage" 
              :disabled="currentPage === totalPages"
              class="px-4 py-2 bg-white border border-gray-200 rounded-[1px] text-xs font-bold uppercase hover:bg-gray-50 disabled:opacity-50 poppins transition-all shadow-sm"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===================== 2-Step Wizard Modal ===================== -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-5xl h-[88vh] flex flex-col shadow-2xl rounded-[1px] overflow-hidden border border-gray-100 animate-modal-in">

        <!-- Wizard Step Progress Bar -->
        <div class="bg-white border-b border-gray-100 px-8 pt-6 pb-0 flex-shrink-0">
          <div class="flex items-center gap-0 mb-0">
            <!-- Step 1 -->
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-black transition-all duration-300"
                   :class="wizardStep >= 1 ? 'bg-[#fe3787] text-white shadow-md' : 'bg-gray-100 text-gray-400'">
                <i v-if="wizardStep > 1" class="ph ph-check text-sm"></i>
                <span v-else>1</span>
              </div>
              <div>
                <p class="text-[10px] font-black uppercase tracking-widest" :class="wizardStep === 1 ? 'text-[#fe3787]' : 'text-gray-400'">Step 1</p>
                <p class="text-[11px] font-bold text-[#002D1E] leading-none">Flight Details</p>
              </div>
            </div>

            <!-- Connector -->
            <div class="flex-1 mx-4 h-[2px] rounded-full transition-all duration-500" :class="wizardStep >= 2 ? 'bg-[#fe3787]' : 'bg-gray-100'"></div>

            <!-- Step 2 -->
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-black transition-all duration-300"
                   :class="wizardStep >= 2 ? 'bg-[#fe3787] text-white shadow-md' : 'bg-gray-100 text-gray-400'">
                2
              </div>
              <div>
                <p class="text-[10px] font-black uppercase tracking-widest" :class="wizardStep === 2 ? 'text-[#fe3787]' : 'text-gray-400'">Step 2</p>
                <p class="text-[11px] font-bold text-[#002D1E] leading-none">Route & Stops</p>
              </div>
            </div>
          </div>

          <!-- Wizard title row -->
          <div class="flex justify-between items-center pb-4 pt-4 border-t border-gray-50 mt-4">
            <h2 class="font-black text-xl text-[#002D1E] tracking-tight uppercase">
              {{ isEditing ? 'Edit Flight' : 'New Flight' }}
              <span class="text-[#fe3787]"> · {{ wizardStep === 1 ? 'Flight Details' : 'Route & Stops' }}</span>
            </h2>
            <button @click="isModalOpen = false" class="text-gray-300 hover:text-gray-600 transition-colors p-1">
              <i class="ph ph-x text-xl"></i>
            </button>
          </div>
        </div>

        <!-- =========== STEP 1: Flight Number, Airline, Aircraft =========== -->
        <div v-if="wizardStep === 1" class="flex-1 overflow-y-auto">
          <div class="p-8 max-w-xl mx-auto space-y-7">

            <!-- Flight Number -->
            <div>
              <label class="block text-[10px] font-black uppercase text-gray-400 mb-2 tracking-widest">
                <i class="ph ph-tag text-[#fe3787]"></i> Flight Number
              </label>
              <input 
                v-model="form.flight_number" 
                type="text" 
                class="w-full border border-gray-200 p-3 text-sm outline-none focus:border-[#fe3787] font-bold text-[#002D1E] tracking-widest uppercase bg-gray-50 focus:bg-white transition-all rounded-[1px]" 
                placeholder="e.g. PR101" 
                required
              >
            </div>

            <!-- Airline -->
            <div>
              <label class="block text-[10px] font-black uppercase text-gray-400 mb-2 tracking-widest">
                <i class="ph ph-buildings text-blue-500"></i> Airline
              </label>
              <SearchableSelect
                v-model="form.airline"
                :options="airlineOptions"
                placeholder="Search and select airline..."
                label="Airline"
              />
            </div>

            <!-- Aircraft Model -->
            <div>
              <label class="block text-[10px] font-black uppercase text-gray-400 mb-2 tracking-widest">
                <i class="ph ph-airplane-tilt text-purple-500"></i> Aircraft Model
              </label>
              <SearchableSelect
                v-model="form.aircraft"
                :options="aircraftOptions"
                :disabled="!form.airline"
                :placeholder="form.airline ? 'Search and select aircraft...' : 'Select an airline first'"
                label="Aircraft"
              />
              <p v-if="!form.airline" class="text-[9px] text-amber-500 font-bold mt-1.5 uppercase tracking-widest">
                <i class="ph ph-warning-circle"></i> Select an airline to filter available aircraft
              </p>
            </div>

          </div>
        </div>

        <!-- =========== STEP 2: Route, Total Stops, Layovers =========== -->
        <div v-if="wizardStep === 2" class="flex-1 flex overflow-hidden">

          <!-- Left: Route & Layover form -->
          <div class="w-5/12 flex flex-col border-r border-gray-100 overflow-y-auto">
            <div class="p-8 space-y-6 flex-1">

              <!-- Route Selection -->
              <div>
                <label class="block text-[10px] font-black uppercase text-gray-400 mb-2 tracking-widest">
                  <i class="ph ph-map-trifold text-[#fe3787]"></i> Flight Route
                </label>
                <SearchableSelect
                  v-model="form.route"
                  :options="routeOptions"
                  placeholder="Search by airport or city..."
                  label="Route"
                />
                <p class="text-[9px] text-gray-400 font-bold mt-1.5 uppercase tracking-widest">Or click a route on the map →</p>
              </div>

              <!-- Total Stops -->
              <div>
                <label class="block text-[10px] font-black uppercase text-gray-400 mb-2 tracking-widest">
                  <i class="ph ph-path text-orange-500"></i> Total Stops
                </label>
                <div class="flex gap-2">
                  <button 
                    v-for="n in [0,1,2,3]" :key="n"
                    type="button"
                    @click="setTotalStops(n)"
                    :class="form.total_stops === n ? 'bg-[#fe3787] text-white border-[#fe3787]' : 'bg-white text-gray-500 border-gray-200 hover:border-[#fe3787]'"
                    class="flex-1 py-2.5 border rounded-[1px] text-xs font-black uppercase tracking-widest transition-all"
                  >
                    {{ n === 0 ? 'Direct' : `${n} Stop${n > 1 ? 's' : ''}` }}
                  </button>
                </div>
              </div>

              <!-- Layovers Data Builder -->
              <div v-if="form.total_stops > 0">
                <label class="block text-[10px] font-black uppercase text-gray-400 mb-2 tracking-widest">
                  <i class="ph ph-git-branch text-indigo-500"></i> Layover Stops
                  <span class="text-[8px] ml-1 normal-case font-bold text-gray-300">({{ layovers.length }}/{{ form.total_stops }})</span>
                </label>

                <!-- Existing Layovers -->
                <div class="space-y-2 mb-3">
                  <div 
                    v-for="(stop, idx) in layovers" :key="idx"
                    class="flex items-center gap-2 bg-gray-50 border border-gray-100 rounded-[1px] p-2.5 group"
                  >
                    <div class="w-6 h-6 rounded-full bg-[#fe3787] flex items-center justify-center text-[8px] font-black text-white flex-shrink-0">{{ idx + 1 }}</div>
                    <div class="flex-1 min-w-0">
                      <p class="text-[11px] font-black text-[#002D1E] truncate">{{ stop.airport }} <span class="text-gray-400 font-medium">{{ stop.city ? `· ${stop.city}` : '' }}</span></p>
                      <p class="text-[9px] text-gray-400 font-bold">{{ stop.duration || 'No duration set' }}</p>
                    </div>
                    <button 
                      type="button" 
                      @click="removeLayover(idx)"
                      class="text-gray-300 hover:text-red-400 transition-colors flex-shrink-0 opacity-0 group-hover:opacity-100"
                    >
                      <i class="ph ph-x text-xs"></i>
                    </button>
                  </div>
                </div>

                <!-- Add Layover Form -->
                <div v-if="layovers.length < form.total_stops" class="border border-dashed border-[#fe3787]/30 rounded-[1px] p-4 bg-pink-50/20 space-y-3">
                  <p class="text-[9px] font-black text-[#fe3787] uppercase tracking-widest">+ Add Layover Stop {{ layovers.length + 1 }}</p>
                  <div>
                    <label class="text-[8px] font-black uppercase text-gray-400 tracking-widest block mb-1">Airport</label>
                    <SearchableSelect
                      v-model="newLayover.airport"
                      :options="airportOptions"
                      placeholder="Search and select airport..."
                      label="Airport"
                    />
                  </div>
                  <div v-if="newLayover.city" class="bg-gray-50 border border-gray-100 p-2 rounded-[1px] flex justify-between items-center">
                    <span class="text-[8px] font-black uppercase text-gray-400 tracking-widest">City</span>
                    <span class="text-xs font-bold text-[#002D1E]">{{ newLayover.city }}</span>
                  </div>
                  <div>
                    <label class="text-[8px] font-black uppercase text-gray-400 tracking-widest block mb-1">Stopover Duration</label>
                    <input 
                      v-model="newLayover.duration" 
                      type="text"
                      class="w-full border border-gray-200 p-2 text-xs outline-none focus:border-[#fe3787] font-bold text-[#002D1E] bg-white rounded-[1px]"
                      placeholder="e.g. 1h 30m"
                    />
                  </div>
                  <button 
                    type="button" 
                    @click="addLayover"
                    :disabled="!newLayover.airport"
                    class="w-full py-2 bg-[#002D1E] text-white text-[10px] font-black uppercase tracking-widest rounded-[1px] hover:bg-black transition-all disabled:opacity-40"
                  >
                    <i class="ph ph-plus mr-1"></i> Add Stop
                  </button>
                </div>
              </div>

            </div>
          </div>

          <!-- Right: Leaflet Route Map -->
          <div class="hidden md:block w-7/12 relative bg-gray-50 flex-shrink-0">
            <div id="flight-modal-map" class="w-full h-full z-0"></div>

            <!-- Floating legend -->
            <div class="absolute top-4 right-4 z-[400] bg-white/90 backdrop-blur-md border border-gray-200/80 px-4 py-3 rounded-[1px] shadow-lg max-w-[220px]">
              <p class="text-[10px] font-black text-[#002D1E] uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
                <i class="ph ph-map-trifold text-[#fe3787] text-xs"></i> Route Map
              </p>
              <p class="text-[9px] text-gray-500 font-bold leading-normal">
                Click a route line or airport pin to select a route.
              </p>
              <div class="mt-3 pt-2 border-t border-gray-100 space-y-1">
                <div class="flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                  <span class="text-[8px] font-bold text-gray-400 uppercase">International</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-[#10b981]"></span>
                  <span class="text-[8px] font-bold text-gray-400 uppercase">Domestic</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <div class="w-4 h-[2px] bg-[#fe3787] rounded-full" style="border-top: 2px dashed #fe3787; height: 0;"></div>
                  <span class="text-[8px] font-bold text-gray-400 uppercase">Available Route</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <div class="w-4 rounded-full" style="border-top: 2px solid #002D1E; height: 0;"></div>
                  <span class="text-[8px] font-bold text-gray-400 uppercase">Selected Route</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer Buttons -->
        <div class="bg-white border-t border-gray-100 px-8 py-5 flex justify-between items-center flex-shrink-0">
          <button 
            type="button" 
            @click="isModalOpen = false" 
            class="text-xs font-black uppercase tracking-widest text-gray-400 hover:text-gray-600 transition-colors"
          >
            Cancel
          </button>
          <div class="flex gap-3">
            <button 
              v-if="wizardStep === 2"
              type="button" 
              @click="wizardStep = 1" 
              class="border border-gray-200 text-gray-500 px-6 py-2.5 text-xs font-black uppercase tracking-widest hover:bg-gray-50 transition-all rounded-[1px] flex items-center gap-2"
            >
              <i class="ph ph-arrow-left"></i> Back
            </button>
            <button 
              v-if="wizardStep === 1"
              type="button" 
              @click="goToStep2"
              class="bg-[#fe3787] text-white px-8 py-2.5 text-xs font-black uppercase tracking-widest shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] flex items-center gap-2"
            >
              Next <i class="ph ph-arrow-right"></i>
            </button>
            <button 
              v-if="wizardStep === 2"
              type="button"
              @click="saveFlight"
              class="bg-[#002D1E] text-white px-8 py-2.5 text-xs font-black uppercase tracking-widest shadow-md hover:bg-black transition-all rounded-[1px] flex items-center gap-2"
            >
              <i class="ph ph-airplane-takeoff"></i>
              {{ isEditing ? 'Update Flight' : 'Confirm Flight' }}
            </button>
          </div>
        </div>

      </div>
    </div>
    <!-- ==================== End Modal ==================== -->

  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import api from '@/services/admin/api';
import { useModalStore } from '@/stores/modal';
import ImportModal from '@/components/admin/ImportModal.vue';
import SearchableSelect from '@/components/admin/SearchableSelect.vue';
import AdminTableTool from '@/components/admin/AdminTableTool.vue';

// Leaflet icon fix
if (L && L.Icon && L.Icon.Default) {
  delete L.Icon.Default.prototype._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
    iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
    shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
  });
}

const modalStore = useModalStore();

// Data
const flights = ref([]);
const allFilteredFlights = ref([]);
const airlines = ref([]);
const allAircrafts = ref([]);
const filteredAircrafts = ref([]);
const routes = ref([]);
const airports = ref([]);

// Wizard state
const wizardStep = ref(1);
const isModalOpen = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const showImportModal = ref(false);

// Layover state
const layovers = ref([]);
const newLayover = ref({ airport: '', city: '', duration: '' });

// Map state
let mapInstance = null;
let mapAirportMarkers = [];
let mapRouteLines = [];

// Form
const form = ref({
  flight_number: '',
  airline: '',
  aircraft: '',
  route: '',
  total_stops: 0,
  is_active: true
});

const searchQuery = ref('');
const filterAirline = ref('all');
const currentPage = ref(1);
const itemsPerPage = 10;
const totalRecords = ref(0);
const highlightedId = ref(null);
const route = useRoute();

// Computed Options
const airlineOptions = computed(() =>
  airlines.value.map(a => ({ value: a.id, label: a.name, sublabel: `Code: ${a.code}` }))
);
const aircraftOptions = computed(() =>
  filteredAircrafts.value.map(ac => ({ value: ac.id, label: ac.model, sublabel: `${ac.capacity} seats` }))
);
const routeOptions = computed(() =>
  routes.value.map(r => ({ value: r.id, label: `${r.origin_info} → ${r.destination_info}` }))
);
const airportOptions = computed(() =>
  airports.value.map(ap => ({ value: ap.code, label: `${ap.code} - ${ap.name}`, sublabel: ap.city || '' }))
);

// Stats
const statsItems = computed(() => ({
  'Total Flights': totalRecords.value,
  'Active Airlines': new Set(allFilteredFlights.value.map(f => f.airline)).size,
  'Operational Aircraft': new Set(allFilteredFlights.value.map(f => f.aircraft)).size,
}));

// Pagination
const totalPages = computed(() => Math.ceil(totalRecords.value / itemsPerPage));
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage);
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, totalRecords.value));
const visiblePages = computed(() => {
  const pages = [];
  const t = totalPages.value;
  const c = currentPage.value;
  if (t <= 5) { for (let i = 1; i <= t; i++) pages.push(i); }
  else {
    if (c <= 3) { for (let i = 1; i <= 4; i++) pages.push(i); pages.push('...', t); }
    else if (c >= t - 2) { pages.push(1, '...'); for (let i = t - 3; i <= t; i++) pages.push(i); }
    else { pages.push(1, '...', c - 1, c, c + 1, '...', t); }
  }
  return pages;
});

const statIcon = (label) => {
  if (label === 'Total Flights') return 'ph ph-airplane';
  if (label === 'Active Airlines') return 'ph ph-buildings';
  return 'ph ph-airplane-tilt';
};
const statIconClass = (label) => {
  if (label === 'Total Flights') return 'bg-blue-100 text-blue-600';
  if (label === 'Active Airlines') return 'bg-green-100 text-green-600';
  return 'bg-purple-100 text-purple-600';
};

// Fetch data
const fetchData = async () => {
  try {
    const params = { page: currentPage.value, page_size: itemsPerPage };
    if (searchQuery.value) params.search = searchQuery.value;
    if (filterAirline.value !== 'all') params.airline = filterAirline.value;

    const statsParams = { ...params, pagination: 'false' };
    delete statsParams.page;
    delete statsParams.page_size;

    const [resF, resA, resAc, resR, resAp, resAllF] = await Promise.all([
      api.get('/flights/', { params }),
      api.get('/airlines/', { params: { pagination: 'false' } }),
      api.get('/aircraft/', { params: { pagination: 'false' } }),
      api.get('/routes/', { params: { pagination: 'false' } }),
      api.get('/airports/'),
      api.get('/flights/', { params: statsParams })
    ]);

    flights.value = resF.data.results || resF.data;
    totalRecords.value = resF.data.count || flights.value.length;
    airlines.value = resA.data.results || resA.data;
    allAircrafts.value = resAc.data.results || resAc.data;
    routes.value = resR.data.results || resR.data;
    airports.value = resAp.data.results || resAp.data;
    allFilteredFlights.value = resAllF.data.results || resAllF.data;

    if (route.query.page) currentPage.value = parseInt(route.query.page);
    if (route.query.highlight) {
      const hId = parseInt(route.query.highlight);
      highlightedId.value = hId;
      setTimeout(() => {
        const el = document.getElementById(`flight-row-${hId}`);
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(() => { highlightedId.value = null; }, 3000);
      }, 500);
    }
  } catch (err) {
    console.error('Data fetch failed:', err.response?.data || err.message);
  }
};

// Watch airline filter on form to filter aircrafts
watch(() => form.value.airline, (newAirlineId) => {
  if (newAirlineId) {
    filteredAircrafts.value = allAircrafts.value.filter(ac => ac.airline === newAirlineId);
    if (!filteredAircrafts.value.find(ac => ac.id === form.value.aircraft)) {
      form.value.aircraft = '';
    }
  } else {
    filteredAircrafts.value = [];
  }
});

// Watch route changes to update map
watch(() => form.value.route, () => {
  if (mapInstance) updateFlightRouteOnMap();
});

// Watch new layover airport to auto-populate city
watch(() => newLayover.value.airport, (newVal) => {
  if (newVal) {
    const selectedAp = airports.value.find(ap => ap.code === newVal);
    if (selectedAp) {
      newLayover.value.city = selectedAp.city || '';
    }
  } else {
    newLayover.value.city = '';
  }
});

// Layover helpers
const getLayoversList = (layoversData) => {
  if (!layoversData) return [];
  try {
    return typeof layoversData === 'string' ? JSON.parse(layoversData) : layoversData;
  } catch {
    return [];
  }
};

const setTotalStops = (n) => {
  form.value.total_stops = n;
  // Trim layovers if reduced
  if (layovers.value.length > n) {
    layovers.value = layovers.value.slice(0, n);
  }
  if (n === 0) layovers.value = [];
};

const addLayover = () => {
  if (!newLayover.value.airport) return;
  layovers.value.push({
    airport: newLayover.value.airport.toUpperCase().trim(),
    city: newLayover.value.city.trim(),
    duration: newLayover.value.duration.trim()
  });
  newLayover.value = { airport: '', city: '', duration: '' };
};

const removeLayover = (idx) => {
  layovers.value.splice(idx, 1);
};

// Step navigation
const goToStep2 = async () => {
  if (!form.value.flight_number || !form.value.airline || !form.value.aircraft) {
    alert('Please fill in Flight Number, Airline and Aircraft before continuing.');
    return;
  }
  wizardStep.value = 2;
  await nextTick();
  setTimeout(initRouteMap, 250);
};

// Map operations
const initRouteMap = () => {
  const container = document.getElementById('flight-modal-map');
  if (!container || mapInstance) return;

  mapInstance = L.map(container, {
    center: [12.8797, 121.7740],
    zoom: 6,
    zoomControl: true,
    attributionControl: false
  });

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { maxZoom: 19 }).addTo(mapInstance);

  renderMapAirportsAndRoutes();
};

const destroyMap = () => {
  if (mapInstance) { mapInstance.remove(); mapInstance = null; }
  mapAirportMarkers = [];
  mapRouteLines = [];
};

const getAirportCoords = (ap) => {
  const lat = ap.latitude !== undefined && ap.latitude !== null ? parseFloat(ap.latitude) : parseFloat(ap.lat);
  const lng = ap.longitude !== undefined && ap.longitude !== null ? parseFloat(ap.longitude) : parseFloat(ap.lng);
  return isNaN(lat) || isNaN(lng) ? null : [lat, lng];
};

const renderMapAirportsAndRoutes = () => {
  if (!mapInstance) return;

  // Clear old layers
  mapAirportMarkers.forEach(m => m.remove()); mapAirportMarkers = [];
  mapRouteLines.forEach(l => l.remove()); mapRouteLines = [];

  const selectedRouteId = form.value.route;

  // Draw route lines
  routes.value.forEach(r => {
    const originAp = airports.value.find(a => a.id === r.origin_airport);
    const destAp = airports.value.find(a => a.id === r.destination_airport);
    if (!originAp || !destAp) return;

    const originCoords = getAirportCoords(originAp);
    const destCoords = getAirportCoords(destAp);
    if (!originCoords || !destCoords) return;

    const isSelected = Number(r.id) === Number(selectedRouteId);

    const line = L.polyline([originCoords, destCoords], {
      color: isSelected ? '#002D1E' : '#fe3787',
      weight: isSelected ? 4 : 1.5,
      opacity: isSelected ? 0.95 : 0.25,
      dashArray: isSelected ? null : '6, 8'
    })
      .addTo(mapInstance)
      .bindTooltip(
        `<div style="font-family:'Poppins',sans-serif; font-size:10px; font-weight:900; color:#002D1E">
          ${r.origin_info || ''} → ${r.destination_info || ''}
         </div>`,
        { direction: 'top', className: 'airport-tooltip' }
      );

    line.on('click', () => {
      form.value.route = r.id;
      renderMapAirportsAndRoutes();
    });

    mapRouteLines.push(line);
  });

  // Draw airport markers (only for airports referenced in active routes)
  const activeAirportIds = new Set();
  routes.value.forEach(r => {
    if (r.origin_airport) activeAirportIds.add(Number(r.origin_airport));
    if (r.destination_airport) activeAirportIds.add(Number(r.destination_airport));
  });

  airports.value.forEach(ap => {
    if (!activeAirportIds.has(Number(ap.id))) return;
    const coords = getAirportCoords(ap);
    if (!coords) return;

    const isIntl = ap.airport_type === 'international' || ap.type === 'international';
    const color = isIntl ? '#3b82f6' : '#10b981';
    const shadow = isIntl ? 'rgba(59,130,246,0.35)' : 'rgba(16,185,129,0.35)';

    const apIcon = L.divIcon({
      html: `<div style="width:8px;height:8px;background:${color};border:1.5px solid white;border-radius:50%;box-shadow:0 0 6px ${shadow};cursor:pointer;"></div>`,
      className: 'airport-dot-icon',
      iconSize: [8, 8],
      iconAnchor: [4, 4]
    });

    const marker = L.marker(coords, { icon: apIcon })
      .addTo(mapInstance)
      .bindTooltip(
        `<div style="font-family:'Poppins',sans-serif;min-width:120px">
          <span style="font-size:10px;font-weight:900;color:#002D1E;display:block">${ap.code} – ${ap.name}</span>
          <span style="font-size:8px;color:#888;font-weight:700;text-transform:uppercase">${ap.city || ''}</span>
         </div>`,
        { direction: 'top', className: 'airport-tooltip', offset: [0, -5] }
      );

    mapAirportMarkers.push(marker);
  });
};

const updateFlightRouteOnMap = () => {
  renderMapAirportsAndRoutes();

  const selectedRouteId = form.value.route;
  if (!selectedRouteId) return;

  const selectedRoute = routes.value.find(r => Number(r.id) === Number(selectedRouteId));
  if (!selectedRoute) return;

  const originAp = airports.value.find(a => a.id === selectedRoute.origin_airport);
  const destAp = airports.value.find(a => a.id === selectedRoute.destination_airport);
  if (!originAp || !destAp) return;

  const oc = getAirportCoords(originAp);
  const dc = getAirportCoords(destAp);
  if (oc && dc) {
    const bounds = L.latLngBounds([oc, dc]);
    mapInstance.fitBounds(bounds, { padding: [60, 60] });
  }
};

// Modal control
const openModal = (flight = null) => {
  isEditing.value = !!flight;
  currentId.value = flight?.id || null;
  wizardStep.value = 1;
  layovers.value = [];
  newLayover.value = { airport: '', city: '', duration: '' };

  if (flight) {
    form.value = {
      flight_number: flight.flight_number,
      airline: flight.airline,
      aircraft: flight.aircraft,
      route: flight.route,
      total_stops: flight.total_stops || 0,
      is_active: flight.is_active !== false
    };
    // Parse existing layovers_data if available
    if (flight.layovers_data) {
      try {
        const parsed = typeof flight.layovers_data === 'string' 
          ? JSON.parse(flight.layovers_data) 
          : flight.layovers_data;
        if (Array.isArray(parsed)) layovers.value = parsed;
      } catch {}
    }
  } else {
    form.value = { flight_number: '', airline: '', aircraft: '', route: '', total_stops: 0, is_active: true };
  }
  isModalOpen.value = true;
};

// Save
const saveFlight = async () => {
  try {
    const payload = { ...form.value };
    payload.flight_number = payload.flight_number.toUpperCase().trim();
    payload.layovers_data = layovers.value.length > 0 ? JSON.stringify(layovers.value) : '[]';

    if (isEditing.value) {
      await api.put(`/flights/${currentId.value}/`, payload);
    } else {
      await api.post('/flights/', payload);
    }

    await fetchData();
    isModalOpen.value = false;
  } catch (err) {
    console.error('Save error:', err.response?.data);
    alert('Error saving flight. Please check all fields.');
  }
};

// Delete
const deleteFlight = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Delete Flight?',
    message: 'Are you sure you want to delete this flight record?',
    variant: 'danger',
    confirmText: 'Delete',
    loadingText: 'Deleting...'
  });

  if (confirmed) {
    modalStore.setLoader(true);
    try {
      await api.delete(`/flights/${id}/`);
      await fetchData();
      modalStore.close(true);
    } catch (err) {
      console.error('Delete Error:', err);
      modalStore.setLoader(false);
    }
  }
};

// Watch modal close to destroy map
watch(isModalOpen, (newVal) => {
  if (!newVal) destroyMap();
});

// Watch wizard step back to step 1 also destroy map
watch(wizardStep, (val) => {
  if (val === 1) destroyMap();
});

// Debounce search
let searchTimeout = null;
const debounceSearch = () => { clearTimeout(searchTimeout); searchTimeout = setTimeout(() => fetchData(), 500); };
watch([searchQuery, filterAirline], () => { currentPage.value = 1; debounceSearch(); });

const prevPage = () => { if (currentPage.value > 1) { currentPage.value--; fetchData(); } };
const nextPage = () => { if (currentPage.value < totalPages.value) { currentPage.value++; fetchData(); } };
const goToPage = (p) => { if (p !== '...') { currentPage.value = p; fetchData(); } };

onMounted(fetchData);
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

@keyframes pulse-highlight {
  0% { background-color: rgba(254, 55, 135, 0.05); }
  50% { background-color: rgba(254, 55, 135, 0.2); }
  100% { background-color: rgba(254, 55, 135, 0.05); }
}

.highlight-active {
  animation: pulse-highlight 1.5s ease-in-out infinite;
  border-left: 4px solid #fe3787 !important;
  box-shadow: inset 0 0 20px rgba(254, 55, 135, 0.1);
}

.poppins { font-family: 'Poppins', sans-serif; }

@keyframes modal-in {
  from { opacity: 0; transform: scale(0.98) translateY(8px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.animate-modal-in {
  animation: modal-in 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

:deep(.airport-tooltip) {
  background: white !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
  border-radius: 2px !important;
  padding: 6px 10px !important;
  opacity: 1 !important;
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: 2px !important;
  box-shadow: 0 10px 35px rgba(0,0,0,0.12) !important;
  border: 1px solid #e2e8f0 !important;
  padding: 0 !important;
}

:deep(.leaflet-popup-content) { margin: 0 !important; }
:deep(.leaflet-popup-tip-container) { display: none !important; }
</style>
