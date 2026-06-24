<template>
  <div class="p-6 poppins">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-2">
        <button 
          @click="openAddModal" 
          class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[14px] rounded-[1px]"
        >
          <i class="ph ph-plus"></i> Add Booking Tax
        </button>
        <button 
          @click="exportTaxes" 
          class="border border-gray-300 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px] rounded-[1px]"
        >
          <i class="ph ph-export"></i> Export
        </button>
        <button 
          @click="refreshData" 
          class="border border-gray-300 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px] rounded-[1px]"
        >
          <i class="ph ph-arrows-clockwise"></i> Refresh
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Total Tax Records</p>
            <p class="text-3xl font-bold text-[#002D1E]">{{ stats.total }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-blue-50 flex items-center justify-center border border-blue-100">
            <i class="ph ph-receipt text-blue-500 text-2xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Total Tax Amount</p>
            <p class="text-3xl font-bold text-[#fe3787]">₱{{ formatNumber(stats.totalAmount) }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-pink-50 flex items-center justify-center border border-pink-100">
            <i class="ph ph-currency-circle-dollar text-[#fe3787] text-2xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Avg per Booking</p>
            <p class="text-3xl font-bold text-green-600">₱{{ formatNumber(stats.averagePerBooking) }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-green-50 flex items-center justify-center border border-green-100">
            <i class="ph ph-chart-bar text-green-500 text-2xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Unique Bookings</p>
            <p class="text-3xl font-bold text-purple-600">{{ stats.uniqueBookings }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-purple-50 flex items-center justify-center border border-purple-100">
            <i class="ph ph-ticket text-purple-600 text-2xl"></i>
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
            placeholder="Search by booking ID, tax type..." 
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-[1px] w-full focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
            @input="debounceSearch"
          />
        </div>
        
        <select 
          v-model="selectedBooking" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px] min-w-[150px]"
          @change="filterTaxes"
        >
          <option value="">All Bookings</option>
          <option v-for="booking in bookings" :key="booking.id" :value="booking.id">
            #{{ booking.id }}
          </option>
        </select>

        <select 
          v-model="selectedTaxType" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px] min-w-[150px]"
          @change="filterTaxes"
        >
          <option value="">All Tax Types</option>
          <option v-for="tax in taxTypes" :key="tax.id" :value="tax.id">
            {{ tax.name }}
          </option>
        </select>

        <select 
          v-model="selectedPassengerType" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px] min-w-[150px]"
          @change="filterTaxes"
        >
          <option value="">All Types</option>
          <option value="adult">Adult</option>
          <option value="child">Child</option>
          <option value="infant">Infant</option>
        </select>

        <button 
          @click="clearFilters" 
          class="text-white px-4 py-2 border bg-[#fe3787] rounded-[1px] hover:bg-[#fb1873] font-medium poppins text-[14px]"
        >
          Clear
        </button>
      </div>
    </div>

    <!-- Taxes Table -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Booking</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Tax Type</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Passenger Type</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Amount</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Date</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr 
            v-for="tax in paginatedTaxes" 
            :key="tax.id" 
            :id="`bookingtax-row-${tax.id}`"
            :class="{'highlight-active': highlightedId === tax.id}"
            class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium"
          >
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                  <i class="ph ph-ticket text-blue-600 text-lg"></i>
                </div>
                <div>
                  <span class="font-semibold text-[#002D1E] block poppins">Booking #{{ tax.booking?.id }}</span>
                  <span class="text-gray-400 poppins text-xs">{{ formatDate(tax.booking?.created_at) }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <span class="font-semibold text-[#002D1E] block poppins">{{ tax.tax_type?.name }}</span>
              <span class="text-gray-400 poppins text-xs">{{ tax.tax_type?.code }}</span>
            </td>
            <td class="px-6 py-4">
              <span :class="passengerTypeClass(tax.passenger_type)" class="px-3 py-1 rounded-full font-semibold uppercase text-xs poppins">
                {{ formatPassengerType(tax.passenger_type) }}
              </span>
            </td>
            <td class="px-6 py-4">
              <span class="text-lg font-bold text-[#fe3787] poppins">₱{{ formatNumber(tax.amount) }}</span>
            </td>
            <td class="px-6 py-4">
              <span class="text-gray-600 poppins">{{ formatDate(tax.created_at) }}</span>
            </td>
            <td class="px-6 py-4 text-right">
              <button @click="viewDetails(tax)" class="text-blue-600 hover:text-blue-400 p-2" title="View Details">
                <i class="ph ph-eye text-lg"></i>
              </button>
              <button @click="editTax(tax)" class="text-green-600 hover:text-green-400 p-2" title="Edit">
                <i class="ph ph-pencil-simple text-lg"></i>
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
        <h3 class="text-lg font-semibold text-gray-900 mb-2 poppins">No booking taxes found</h3>
        <p class="text-gray-500 poppins">Tax records will appear when bookings are made</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="p-12 text-center">
        <i class="ph ph-spinner animate-spin text-4xl text-[#fe3787]"></i>
        <p class="mt-2 text-gray-500 poppins">Loading booking taxes...</p>
      </div>

      <!-- Pagination -->
      <div v-if="filteredTaxes.length > itemsPerPage" class="px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-600 poppins">
            Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ filteredTaxes.length }} taxes
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

    <!-- Tax Summary by Type -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
        <h3 class="text-sm font-black uppercase text-[#002D1E] tracking-[2px] mb-6">Tax Summary by Type</h3>
        <div class="space-y-3">
          <div 
            v-for="(item, index) in taxTypeSummary" 
            :key="index"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-[1px]"
          >
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-[#fe3787]/10 flex items-center justify-center">
                <i class="ph ph-receipt text-[#fe3787]"></i>
              </div>
              <span class="font-medium text-[#002D1E] poppins">{{ item.tax_type__name }}</span>
            </div>
            <div class="text-right">
              <span class="block font-bold text-[#fe3787] poppins">₱{{ formatNumber(item.total) }}</span>
              <span class="text-xs text-gray-500 poppins">{{ item.count }} records</span>
            </div>
          </div>
          <div v-if="taxTypeSummary.length === 0" class="text-center text-gray-500 py-4">
            No data available
          </div>
        </div>
      </div>

      <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
        <h3 class="text-sm font-black uppercase text-[#002D1E] tracking-[2px] mb-6">Tax by Passenger Type</h3>
        <div class="space-y-4">
          <div v-for="(item, type) in passengerTypeSummary" :key="type" class="flex items-center justify-between p-4 bg-gray-50 rounded-[1px]">
            <div class="flex items-center gap-3">
              <div :class="['w-12 h-12 rounded-full flex items-center justify-center', passengerTypeIconBg(type)]">
                <i :class="['text-xl', passengerTypeIcon(type)]"></i>
              </div>
              <span class="font-semibold text-[#002D1E] block poppins capitalize">{{ formatPassengerType(type) }}</span>
            </div>
            <div class="text-right">
              <span class="block text-2xl font-bold text-[#fe3787] poppins">₱{{ formatNumber(item.total) }}</span>
              <span class="text-xs text-gray-500 poppins">{{ item.count }} records</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-[#002D1E]/60 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-md rounded-[1px] shadow-2xl overflow-hidden">
        <div class="bg-[#002D1E] p-4 text-white flex justify-between items-center">
          <h2 class="text-sm font-black uppercase tracking-[2px]">{{ isEditing ? 'Revise Booking Tax' : 'Register Booking Tax' }}</h2>
          <button @click="closeModal" class="text-white/70 hover:text-white transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveTax" class="p-6 space-y-5">
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Booking *</label>
            <select 
              v-model="form.booking" 
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
              required
            >
              <option value="">Select Booking</option>
              <option v-for="booking in bookings" :key="booking.id" :value="booking.id">
                #{{ booking.id }} - {{ booking.user_name }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Tax Type *</label>
            <select 
              v-model="form.tax_type" 
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
              required
            >
              <option value="">Select Tax Type</option>
              <option v-for="tax in taxTypes" :key="tax.id" :value="tax.id">
                {{ tax.name }} ({{ tax.code }})
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Passenger Type *</label>
            <select 
              v-model="form.passenger_type" 
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
              required
            >
              <option value="">Select Passenger Type</option>
              <option value="adult">Adult</option>
              <option value="child">Child</option>
              <option value="infant">Infant</option>
            </select>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Amount (₱) *</label>
            <input 
              v-model="form.amount" 
              type="number" 
              step="0.01"
              min="0"
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
              required
            >
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
              {{ isEditing ? 'Update Tax' : 'Save Tax' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- View Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 z-50 flex items-center justify-center bg-[#002D1E]/60 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-lg rounded-[1px] shadow-2xl overflow-hidden">
        <div class="bg-[#002D1E] p-4 text-white flex justify-between items-center">
          <h2 class="text-sm font-black uppercase tracking-[2px]">Booking Tax Record</h2>
          <button @click="showDetailsModal = false" class="text-white/70 hover:text-white transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <div v-if="selectedTax" class="p-8 space-y-6">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
              <i class="ph ph-ticket text-3xl text-blue-600"></i>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-[#002D1E] poppins">Booking #{{ selectedTax.booking?.id }}</h3>
              <p class="text-sm text-gray-500 poppins">{{ formatDate(selectedTax.booking?.created_at) }}</p>
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Tax Type</label>
              <div class="p-2 border border-gray-200 rounded-[1px] poppins">{{ selectedTax.tax_type?.name }}</div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Code</label>
              <div class="p-2 border border-gray-200 rounded-[1px] poppins font-mono">{{ selectedTax.tax_type?.code }}</div>
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Passenger Type</label>
            <div class="p-2 border border-gray-200 rounded-[1px]">
              <span :class="passengerTypeClass(selectedTax.passenger_type)" class="px-3 py-1 rounded-full text-xs font-semibold uppercase poppins">
                {{ formatPassengerType(selectedTax.passenger_type) }}
              </span>
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Tax Amount</label>
            <div class="p-2 border border-gray-200 rounded-[1px] text-2xl font-bold text-[#fe3787] poppins">
              ₱{{ formatNumber(selectedTax.amount) }}
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Recorded At</label>
            <div class="p-2 border border-gray-200 rounded-[1px] poppins">
              {{ formatDateTime(selectedTax.created_at) }}
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
import { useRoute } from 'vue-router'
import api from '@/services/admin/api'
import { useModalStore } from '@/stores/modal'

const modalStore = useModalStore()
const route = useRoute()

// State
const taxes = ref([])
const bookings = ref([])
const taxTypes = ref([])
const loading = ref(false)
const showModal = ref(false)
const showDetailsModal = ref(false)
const selectedTax = ref(null)
const isEditing = ref(false)
const currentId = ref(null)
const highlightedId = ref(null)

// Filters
const searchQuery = ref('')
const selectedBooking = ref('')
const selectedTaxType = ref('')
const selectedPassengerType = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Stats
const stats = ref({
  total: 0,
  totalAmount: 0,
  averagePerBooking: 0,
  uniqueBookings: 0
})

const taxTypeSummary = ref([])

// Form
const form = ref({
  booking: '',
  tax_type: '',
  passenger_type: '',
  amount: 0
})

// Computed
const filteredTaxes = computed(() => {
  let filtered = taxes.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(tax => 
      tax.booking?.id?.toString().includes(query) ||
      tax.tax_type?.name?.toLowerCase().includes(query) ||
      tax.tax_type?.code?.toLowerCase().includes(query)
    )
  }
  
  if (selectedBooking.value) {
    filtered = filtered.filter(tax => tax.booking?.id === parseInt(selectedBooking.value))
  }
  
  if (selectedTaxType.value) {
    filtered = filtered.filter(tax => tax.tax_type?.id === parseInt(selectedTaxType.value))
  }
  
  if (selectedPassengerType.value) {
    filtered = filtered.filter(tax => tax.passenger_type === selectedPassengerType.value)
  }
  
  return filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
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

const passengerTypeSummary = computed(() => {
  const summary = {
    adult: { total: 0, count: 0 },
    child: { total: 0, count: 0 },
    infant: { total: 0, count: 0 }
  }
  
  taxes.value.forEach(tax => {
    const type = tax.passenger_type
    if (summary[type]) {
      summary[type].total += parseFloat(tax.amount || 0)
      summary[type].count++
    }
  })
  
  return summary
})

// Methods
const fetchData = async () => {
  loading.value = true
  try {
    const [taxesRes, bookingsRes, taxTypesRes] = await Promise.all([
      api.get('/booking-taxes/'),
      api.get('/bookings/'),
      api.get('/tax-types/')
    ])
    
    taxes.value = taxesRes.data.results || taxesRes.data
    bookings.value = bookingsRes.data.results || bookingsRes.data
    taxTypes.value = taxTypesRes.data.results || taxTypesRes.data
    
    calculateStats()
    calculateSummaries()

    if (route.query.page) {
        currentPage.value = parseInt(route.query.page);
    }

    if (route.query.highlight) {
        const hId = parseInt(route.query.highlight);
        highlightedId.value = hId;

        // Auto-navigate to the correct page for this ID
        const index = taxes.value.findIndex(t => t.id === hId);
        if (index !== -1) {
            currentPage.value = Math.floor(index / itemsPerPage) + 1;
        }

        setTimeout(() => {
            const el = document.getElementById(`bookingtax-row-${hId}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => { highlightedId.value = null; }, 3000);
        }, 500);
    }
  } catch (err) {
    console.error('Fetch error:', err)
    alert('Failed to load data')
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  const total = taxes.value.length
  const totalAmount = taxes.value.reduce((sum, t) => sum + parseFloat(t.amount || 0), 0)
  const uniqueBookingIds = new Set(taxes.value.map(t => t.booking?.id)).size
  const averagePerBooking = uniqueBookingIds > 0 ? totalAmount / uniqueBookingIds : 0
  
  stats.value = {
    total,
    totalAmount,
    averagePerBooking,
    uniqueBookings: uniqueBookingIds
  }
}

const calculateSummaries = () => {
  // Tax type summary
  const typeMap = {}
  taxes.value.forEach(tax => {
    const id = tax.tax_type?.id
    if (!typeMap[id]) {
      typeMap[id] = {
        tax_type__name: tax.tax_type?.name,
        total: 0,
        count: 0
      }
    }
    typeMap[id].total += parseFloat(tax.amount || 0)
    typeMap[id].count++
  })
  taxTypeSummary.value = Object.values(typeMap).sort((a, b) => b.total - a.total)
}

const openAddModal = () => {
  isEditing.value = false
  currentId.value = null
  form.value = { booking: '', tax_type: '', passenger_type: '', amount: 0 }
  showModal.value = true
}

const editTax = (tax) => {
  isEditing.value = true
  currentId.value = tax.id
  form.value = {
    booking: tax.booking?.id,
    tax_type: tax.tax_type?.id,
    passenger_type: tax.passenger_type,
    amount: tax.amount
  }
  showModal.value = true
}

const viewDetails = (tax) => {
  selectedTax.value = tax
  showDetailsModal.value = true
}

const saveTax = async () => {
  try {
    const payload = {
      booking_id: form.value.booking,
      tax_type_id: form.value.tax_type,
      passenger_type: form.value.passenger_type,
      amount: parseFloat(form.value.amount)
    }
    
    if (isEditing.value) {
      await api.put(`/booking-taxes/${currentId.value}/`, payload)
      alert('Booking tax updated successfully!')
    } else {
      await api.post('/booking-taxes/', payload)
      alert('Booking tax added successfully!')
    }
    
    await fetchData()
    closeModal()
  } catch (err) {
    console.error('Save error:', err)
    console.error('Error response:', err.response?.data)
    alert('Error: ' + JSON.stringify(err.response?.data || err.message))
  }
}

const deleteTax = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Delete Booking Tax?',
    message: 'Are you sure you want to delete this booking tax record?',
    variant: 'danger',
    confirmText: 'Delete',
    loadingText: 'Deleting...'
  });

  if (!confirmed) return;
  
  modalStore.setLoader(true);
  try {
    await api.delete(`/booking-taxes/${id}/`)
    taxes.value = taxes.value.filter(t => t.id !== id)
    calculateStats()
    calculateSummaries()
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
  form.value = { booking: '', tax_type: '', passenger_type: '', amount: 0 }
}

const exportTaxes = async () => {
  try {
    const response = await api.get('/booking-taxes/export/', {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `booking_taxes_${new Date().toISOString().split('T')[0]}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    console.error('Export error:', err)
    alert('Failed to export booking taxes')
  }
}

const refreshData = () => {
  fetchData()
}

const formatNumber = (num) => {
  return parseFloat(num || 0).toLocaleString('en-PH', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatPassengerType = (type) => {
  const map = {
    'adult': 'Adult',
    'child': 'Child',
    'infant': 'Infant'
  }
  return map[type] || type
}

const passengerTypeClass = (type) => {
  switch(type) {
    case 'adult': return 'bg-blue-100 text-blue-700'
    case 'child': return 'bg-yellow-100 text-yellow-700'
    case 'infant': return 'bg-purple-100 text-purple-700'
    default: return 'bg-gray-100 text-gray-600'
  }
}

const passengerTypeIcon = (type) => {
  switch(type) {
    case 'adult': return 'ph-user text-blue-600'
    case 'child': return 'ph-baby text-yellow-600'
    case 'infant': return 'ph-infant text-purple-600'
    default: return 'ph-user text-gray-600'
  }
}

const passengerTypeIconBg = (type) => {
  switch(type) {
    case 'adult': return 'bg-blue-100'
    case 'child': return 'bg-yellow-100'
    case 'infant': return 'bg-purple-100'
    default: return 'bg-gray-100'
  }
}

const filterTaxes = () => {
  currentPage.value = 1
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedBooking.value = ''
  selectedTaxType.value = ''
  selectedPassengerType.value = ''
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
onMounted(fetchData)
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