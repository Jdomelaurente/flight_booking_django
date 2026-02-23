<template>
  <div class="p-6 poppins">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <button 
        @click="openAddModal" 
        class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[14px] rounded-[1px]"
      >
        <i class="ph ph-plus"></i> Add Tax Type
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Total Tax Types</p>
            <p class="text-3xl font-bold text-[#002D1E]">{{ stats.total }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-green-50 flex items-center justify-center border border-green-100">
            <i class="ph ph-receipt text-green-500 text-2xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Active</p>
            <p class="text-3xl font-bold text-blue-600">{{ stats.active }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-blue-50 flex items-center justify-center border border-blue-100">
            <i class="ph ph-check-circle text-blue-500 text-2xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Government</p>
            <p class="text-3xl font-bold text-red-600">{{ stats.government }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-red-50 flex items-center justify-center border border-red-100">
            <i class="ph ph-buildings text-red-500 text-2xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Airline</p>
            <p class="text-3xl font-bold text-purple-600">{{ stats.airline }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-purple-50 flex items-center justify-center border border-purple-100">
            <i class="ph ph-airplane-tilt text-purple-500 text-2xl"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-4 mb-6 text-[14px]">
      <div class="flex flex-col md:flex-row md:items-center gap-4">
        <div class="relative flex-1">
          <i class="ph ph-magnifying-glass absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search by name, code..." 
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-[1px] w-full focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
            @input="debounceSearch"
          />
        </div>
        
        <select 
          v-model="selectedCategory" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px] min-w-[150px]"
          @change="filterTaxes"
        >
          <option value="">All Categories</option>
          <option value="government">Government Tax</option>
          <option value="airport">Airport Fee</option>
          <option value="airline">Airline Surcharge</option>
        </select>

        <select 
          v-model="selectedStatus" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px] min-w-[150px]"
          @change="filterTaxes"
        >
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>

        <button 
          @click="clearFilters" 
          class="text-white px-4 py-2 border bg-[#fe3787] rounded-[1px] hover:bg-[#fb1873] font-medium poppins text-[14px]"
        >
          Clear
        </button>
      </div>
    </div>

    <!-- Tax Types Table -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Tax Type</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Code</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Category</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Base Amount</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Rules</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Status</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="tax in paginatedTaxes" :key="tax.id" class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium">
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-[#fe3787] flex items-center justify-center">
                  <i class="ph ph-receipt text-white text-lg"></i>
                </div>
                <div>
                  <span class="font-semibold text-[#002D1E] block poppins">{{ tax.name }}</span>
                  <span v-if="tax.description" class="text-gray-400 poppins text-xs truncate max-w-[200px] block">{{ tax.description }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <span class="font-mono text-sm bg-gray-100 px-2 py-1 rounded poppins">{{ tax.code }}</span>
            </td>
            <td class="px-6 py-4">
              <span :class="categoryClass(tax.category)" class="px-3 py-1 rounded-full font-semibold uppercase text-xs poppins">
                {{ formatCategory(tax.category) }}
              </span>
            </td>
            <td class="px-6 py-4">
              <span class="text-lg font-bold text-[#002D1E] poppins">₱{{ formatNumber(tax.base_amount) }}</span>
            </td>
            <td class="px-6 py-4">
              <div class="flex flex-col gap-1">
                <span v-if="tax.per_passenger" class="text-xs text-gray-600 poppins flex items-center gap-1">
                  <i class="ph ph-user"></i> Per passenger
                </span>
                <span v-if="tax.adult_only" class="text-xs text-gray-600 poppins flex items-center gap-1">
                  <i class="ph ph-user-circle"></i> Adults only
                </span>
                <span v-if="!tax.applies_domestic" class="text-xs text-red-500 poppins flex items-center gap-1">
                  <i class="ph ph-x-circle"></i> No domestic
                </span>
                <span v-if="!tax.applies_international" class="text-xs text-red-500 poppins flex items-center gap-1">
                  <i class="ph ph-x-circle"></i> No international
                </span>
              </div>
            </td>
            <td class="px-6 py-4">
              <span :class="statusClass(tax.is_active)" class="px-3 py-1 rounded-full font-semibold uppercase text-xs poppins">
                {{ tax.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="px-6 py-4 text-right">
              <button @click="viewDetails(tax)" class="text-blue-600 hover:text-blue-400 p-2" title="View Details">
                <i class="ph ph-eye text-lg"></i>
              </button>
              <button @click="editTax(tax)" class="text-green-600 hover:text-green-400 p-2" title="Edit">
                <i class="ph ph-pencil-simple text-lg"></i>
              </button>
              <button @click="toggleStatus(tax)" class="text-yellow-600 hover:text-yellow-400 p-2" :title="tax.is_active ? 'Deactivate' : 'Activate'">
                <i :class="tax.is_active ? 'ph-pause-circle' : 'ph-play-circle'" class="ph text-lg"></i>
              </button>
              <button @click="deleteTax(tax.id)" class="text-red-600 hover:text-red-400 p-2" title="Delete">
                <i class="ph ph-trash text-lg"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="filteredTaxes.length === 0 && !loading" class="p-12 text-center">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <i class="ph ph-receipt text-2xl text-gray-400"></i>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2 poppins">No tax types found</h3>
        <p class="text-gray-500 poppins">Add tax types to manage booking calculations</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="p-12 text-center">
        <i class="ph ph-spinner animate-spin text-4xl text-[#fe3787]"></i>
        <p class="mt-2 text-gray-500 poppins">Loading tax types...</p>
      </div>

      <!-- Pagination -->
      <div v-if="filteredTaxes.length > itemsPerPage" class="px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-600 poppins">
            Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ filteredTaxes.length }} tax types
          </div>
          <div class="flex gap-1">
            <button 
              @click="prevPage" 
              :disabled="currentPage === 1"
              class="px-3 py-1 border border-gray-300 rounded-[1px] text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed poppins"
            >
              Prev
            </button>
            <button 
              v-for="page in visiblePages" 
              :key="page"
              @click="goToPage(page)"
              :disabled="page === '...'"
              :class="[
                'px-3 py-1 border rounded-[1px] text-sm poppins',
                page === '...' ? 'border-gray-300 cursor-default' : '',
                currentPage === page ? 'bg-[#fe3787] text-white border-[#fe3787]' : 'border-gray-300 hover:bg-gray-50'
              ]"
            >
              {{ page }}
            </button>
            <button 
              @click="nextPage" 
              :disabled="currentPage === totalPages"
              class="px-3 py-1 border border-gray-300 rounded-[1px] text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed poppins"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-[#002D1E]/60 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-lg rounded-[1px] shadow-2xl overflow-hidden">
        <div class="bg-[#002D1E] p-4 text-white flex justify-between items-center">
          <h2 class="text-sm font-black uppercase tracking-[2px]">{{ isEditing ? 'Revise Tax Type' : 'Register Tax Type' }}</h2>
          <button @click="closeModal" class="text-white/70 hover:text-white transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveTax" class="p-6 space-y-5">
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Name *</label>
            <input 
              v-model="form.name" 
              type="text" 
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
              required
              placeholder="e.g., Travel Tax"
            >
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Code *</label>
            <input 
              v-model="form.code" 
              type="text" 
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
              required
              placeholder="e.g., PH_TRAVEL_TAX"
            >
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Category *</label>
            <select 
              v-model="form.category" 
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
              required
            >
              <option value="">Select Category</option>
              <option value="government">Government Tax</option>
              <option value="airport">Airport Fee</option>
              <option value="airline">Airline Surcharge</option>
            </select>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Description</label>
            <textarea 
              v-model="form.description" 
              rows="3"
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
              placeholder="Brief description of this tax type..."
            ></textarea>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Base Amount (₱) *</label>
            <input 
              v-model="form.base_amount" 
              type="number" 
              step="0.01"
              min="0"
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
              required
            >
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div class="flex items-center gap-2 p-3 border border-gray-200 rounded-[1px]">
              <input 
                v-model="form.per_passenger" 
                type="checkbox" 
                id="per_passenger"
                class="w-4 h-4 text-[#fe3787] rounded focus:ring-[#fe3787]"
              >
              <label for="per_passenger" class="text-sm text-gray-700 poppins cursor-pointer">Per Passenger</label>
            </div>
            <div class="flex items-center gap-2 p-3 border border-gray-200 rounded-[1px]">
              <input 
                v-model="form.adult_only" 
                type="checkbox" 
                id="adult_only"
                class="w-4 h-4 text-[#fe3787] rounded focus:ring-[#fe3787]"
              >
              <label for="adult_only" class="text-sm text-gray-700 poppins cursor-pointer">Adults Only</label>
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div class="flex items-center gap-2 p-3 border border-gray-200 rounded-[1px]">
              <input 
                v-model="form.applies_domestic" 
                type="checkbox" 
                id="applies_domestic"
                class="w-4 h-4 text-[#fe3787] rounded focus:ring-[#fe3787]"
              >
              <label for="applies_domestic" class="text-sm text-gray-700 poppins cursor-pointer">Applies Domestic</label>
            </div>
            <div class="flex items-center gap-2 p-3 border border-gray-200 rounded-[1px]">
              <input 
                v-model="form.applies_international" 
                type="checkbox" 
                id="applies_international"
                class="w-4 h-4 text-[#fe3787] rounded focus:ring-[#fe3787]"
              >
              <label for="applies_international" class="text-sm text-gray-700 poppins cursor-pointer">Applies International</label>
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Departure Country Code (Optional)</label>
            <input 
              v-model="form.applies_departure_country" 
              type="text" 
              maxlength="2"
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins uppercase" 
              placeholder="e.g., PH (leave blank for all)"
            >
          </div>
          
          <div class="flex items-center gap-2 p-3 border border-gray-200 rounded-[1px]">
            <input 
              v-model="form.is_active" 
              type="checkbox" 
              id="is_active"
              class="w-4 h-4 text-[#fe3787] rounded focus:ring-[#fe3787]"
            >
            <label for="is_active" class="text-sm text-gray-700 poppins cursor-pointer font-medium">Active</label>
          </div>
          
          <div class="flex justify-end gap-2 pt-4 border-t">
            <button 
              type="button" 
              @click="closeModal" 
              class="px-4 py-2 text-gray-600 font-medium poppins hover:bg-gray-100 rounded-[1px]"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              class="px-4 py-2 bg-[#fe3787] text-white rounded-[1px] font-medium hover:bg-[#e6327a] transition-colors poppins"
            >
              {{ isEditing ? 'Update Tax Type' : 'Save Tax Type' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- View Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 z-50 flex items-center justify-center bg-[#002D1E]/60 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-lg rounded-[1px] shadow-2xl overflow-hidden">
        <div class="bg-[#002D1E] p-4 text-white flex justify-between items-center">
          <h2 class="text-sm font-black uppercase tracking-[2px]">Tax Type Information</h2>
          <button @click="showDetailsModal = false" class="text-white/70 hover:text-white transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <div v-if="selectedTax" class="p-8 space-y-6">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-16 h-16 rounded-full bg-[#fe3787]/10 flex items-center justify-center">
              <i class="ph ph-receipt text-3xl text-[#fe3787]"></i>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-[#002D1E] poppins">{{ selectedTax.name }}</h3>
              <span class="font-mono text-sm bg-gray-100 px-2 py-1 rounded poppins">{{ selectedTax.code }}</span>
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Category</label>
              <div class="p-2 border border-gray-200 rounded-[1px]">
                <span :class="categoryClass(selectedTax.category)" class="px-3 py-1 rounded-full text-xs font-semibold uppercase poppins">
                  {{ formatCategory(selectedTax.category) }}
                </span>
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Status</label>
              <div class="p-2 border border-gray-200 rounded-[1px]">
                <span :class="statusClass(selectedTax.is_active)" class="px-3 py-1 rounded-full text-xs font-semibold uppercase poppins">
                  {{ selectedTax.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Base Amount</label>
            <div class="p-2 border border-gray-200 rounded-[1px] text-2xl font-bold text-[#fe3787] poppins">
              ₱{{ formatNumber(selectedTax.base_amount) }}
            </div>
          </div>
          
          <div v-if="selectedTax.description">
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Description</label>
            <div class="p-2 border border-gray-200 rounded-[1px] text-sm text-gray-600 poppins">
              {{ selectedTax.description }}
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Application Rules</label>
            <div class="p-3 border border-gray-200 rounded-[1px] space-y-2">
              <div class="flex items-center gap-2">
                <i :class="selectedTax.per_passenger ? 'ph-check-circle text-green-500' : 'ph-x-circle text-red-500'" class="ph"></i>
                <span class="text-sm poppins">Per passenger</span>
              </div>
              <div class="flex items-center gap-2">
                <i :class="selectedTax.adult_only ? 'ph-check-circle text-green-500' : 'ph-x-circle text-red-500'" class="ph"></i>
                <span class="text-sm poppins">Adults only</span>
              </div>
              <div class="flex items-center gap-2">
                <i :class="selectedTax.applies_domestic ? 'ph-check-circle text-green-500' : 'ph-x-circle text-red-500'" class="ph"></i>
                <span class="text-sm poppins">Applies to domestic flights</span>
              </div>
              <div class="flex items-center gap-2">
                <i :class="selectedTax.applies_international ? 'ph-check-circle text-green-500' : 'ph-x-circle text-red-500'" class="ph"></i>
                <span class="text-sm poppins">Applies to international flights</span>
              </div>
            </div>
          </div>
          
          <div v-if="selectedTax.applies_departure_country">
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Departure Country</label>
            <div class="p-2 border border-gray-200 rounded-[1px] poppins font-mono">
              {{ selectedTax.applies_departure_country }}
            </div>
          </div>
        </div>
        
        <div class="flex justify-end gap-2 pt-4 border-t mt-6">
          <button 
            type="button" 
            @click="showDetailsModal = false" 
            class="px-4 py-2 text-gray-600 font-medium poppins hover:bg-gray-100 rounded-[1px]"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import api from '@/services/admin/api'
import { useModalStore } from '@/stores/modal'

const modalStore = useModalStore()

// State
const taxes = ref([])
const loading = ref(false)
const showModal = ref(false)
const showDetailsModal = ref(false)
const selectedTax = ref(null)
const isEditing = ref(false)
const currentId = ref(null)

// Filters
const searchQuery = ref('')
const selectedCategory = ref('')
const selectedStatus = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Stats
const stats = ref({
  total: 0,
  active: 0,
  government: 0,
  airport: 0,
  airline: 0
})

// Form
const form = ref({
  name: '',
  code: '',
  description: '',
  category: '',
  base_amount: 0,
  per_passenger: true,
  adult_only: false,
  applies_domestic: true,
  applies_international: true,
  applies_departure_country: '',
  is_active: true
})

// Computed
const filteredTaxes = computed(() => {
  let filtered = taxes.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(tax => 
      tax.name?.toLowerCase().includes(query) ||
      tax.code?.toLowerCase().includes(query) ||
      tax.description?.toLowerCase().includes(query)
    )
  }
  
  if (selectedCategory.value) {
    filtered = filtered.filter(tax => tax.category === selectedCategory.value)
  }
  
  if (selectedStatus.value) {
    const isActive = selectedStatus.value === 'active'
    filtered = filtered.filter(tax => tax.is_active === isActive)
  }
  
  return filtered
})

const totalPages = computed(() => Math.ceil(filteredTaxes.value.length / itemsPerPage))

const paginatedTaxes = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredTaxes.value.slice(start, end)
})

const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredTaxes.value.length))

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 5) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    if (current <= 3) {
      for (let i = 1; i <= 4; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 2) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 3; i <= total; i++) pages.push(i)
    } else {
      pages.push(1)
      pages.push('...')
      pages.push(current - 1)
      pages.push(current)
      pages.push(current + 1)
      pages.push('...')
      pages.push(total)
    }
  }
  
  return pages
})

// Methods
const fetchTaxes = async () => {
  loading.value = true
  try {
    const response = await api.get('/tax-types/')
    taxes.value = response.data.results || response.data
    calculateStats()
  } catch (err) {
    console.error('Fetch error:', err)
    alert('Failed to load tax types')
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  stats.value.total = taxes.value.length
  stats.value.active = taxes.value.filter(t => t.is_active).length
  stats.value.government = taxes.value.filter(t => t.category === 'government').length
  stats.value.airport = taxes.value.filter(t => t.category === 'airport').length
  stats.value.airline = taxes.value.filter(t => t.category === 'airline').length
}

const openAddModal = () => {
  isEditing.value = false
  currentId.value = null
  form.value = {
    name: '',
    code: '',
    description: '',
    category: '',
    base_amount: 0,
    per_passenger: true,
    adult_only: false,
    applies_domestic: true,
    applies_international: true,
    applies_departure_country: '',
    is_active: true
  }
  showModal.value = true
}

const editTax = (tax) => {
  isEditing.value = true
  currentId.value = tax.id
  form.value = { ...tax }
  showModal.value = true
}

const viewDetails = (tax) => {
  selectedTax.value = tax
  showDetailsModal.value = true
}

const saveTax = async () => {
  try {
    const payload = {
      ...form.value,
      base_amount: parseFloat(form.value.base_amount),
      applies_departure_country: form.value.applies_departure_country?.toUpperCase() || null
    }
    
    if (isEditing.value) {
      await api.put(`/tax-types/${currentId.value}/`, payload)
      alert('Tax type updated successfully!')
    } else {
      await api.post('/tax-types/', payload)
      alert('Tax type added successfully!')
    }
    
    await fetchTaxes()
    closeModal()
  } catch (err) {
    console.error('Save error:', err)
    alert('Error saving tax type. Please check your input.')
  }
}

const toggleStatus = async (tax) => {
  try {
    await api.patch(`/tax-types/${tax.id}/`, {
      is_active: !tax.is_active
    })
    tax.is_active = !tax.is_active
    calculateStats()
    alert(`Tax type ${tax.is_active ? 'activated' : 'deactivated'} successfully!`)
  } catch (err) {
    console.error('Toggle error:', err)
    alert('Failed to update status')
  }
}

const deleteTax = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Delete Tax Type?',
    message: 'Are you sure you want to delete this tax type? This may affect existing bookings and calculations.',
    variant: 'danger',
    confirmText: 'Delete',
    loadingText: 'Deleting...'
  });

  if (!confirmed) return;
  
  modalStore.setLoader(true);
  try {
    await api.delete(`/tax-types/${id}//`)
    taxes.value = taxes.value.filter(t => t.id !== id)
    calculateStats()
    modalStore.close(confirmed);
  } catch (err) {
    console.error('Delete error:', err)
    modalStore.setLoader(false);
  }
}

const closeModal = () => {
  showModal.value = false
  showDetailsModal.value = false
  isEditing.value = false
  currentId.value = null
}

const formatNumber = (num) => {
  return parseFloat(num || 0).toLocaleString('en-PH', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const formatCategory = (category) => {
  const map = {
    'government': 'Government',
    'airport': 'Airport',
    'airline': 'Airline'
  }
  return map[category] || category
}

const categoryClass = (category) => {
  switch(category) {
    case 'government': return 'bg-red-200 '
    case 'airport': return 'bg-blue-200 '
    case 'airline': return 'bg-purple-200 '
    default: return 'bg-gray-200 text-gray-600'
  }
}

const statusClass = (isActive) => {
  return isActive ? 'bg-green-200 ' : 'bg-gray-200 '
}

const filterTaxes = () => {
  currentPage.value = 1
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedCategory.value = ''
  selectedStatus.value = ''
  currentPage.value = 1
}

// Debounce
let searchTimeout = null
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
  }, 500)
}

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const goToPage = (page) => {
  if (page !== '...') currentPage.value = page
}

// Watch
watch([searchQuery], () => {
  currentPage.value = 1
})

// Lifecycle
onMounted(fetchTaxes)
</script>

<style scoped>
.poppins {
  font-family: 'Poppins', sans-serif;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>