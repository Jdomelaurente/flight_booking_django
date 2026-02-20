<template>
  <div class="p-6 poppins">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <button 
        @click="openAddModal" 
        class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[14px] rounded-[1px]"
      >
        <i class="ph ph-plus"></i> Add Airline Tax
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Total Taxes</p>
            <p class="text-3xl font-bold text-[#002D1E]">{{ stats.total }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-blue-50 flex items-center justify-center border border-blue-100">
            <i class="ph ph-airplane-tilt text-blue-500 text-2xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Active Airlines</p>
            <p class="text-3xl font-bold text-green-600">{{ stats.activeAirlines }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-green-50 flex items-center justify-center border border-green-100">
            <i class="ph ph-check-circle text-green-500 text-2xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Total Surcharge</p>
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
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Avg per Airline</p>
            <p class="text-3xl font-bold text-purple-600">₱{{ formatNumber(stats.averagePerAirline) }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-purple-50 flex items-center justify-center border border-purple-100">
            <i class="ph ph-chart-bar text-purple-600 text-2xl"></i>
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
            placeholder="Search by airline, tax type..." 
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-[1px] w-full focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
            @input="debounceSearch"
          />
        </div>
        
        <select 
          v-model="selectedAirline" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px] min-w-[150px]"
          @change="filterTaxes"
        >
          <option value="">All Airlines</option>
          <option v-for="airline in airlines" :key="airline.id" :value="airline.id">
            {{ airline.code }} - {{ airline.name }}
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
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Airline</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Tax Type</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Category</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Amount</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Status</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="tax in paginatedTaxes" :key="tax.id" class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium">
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                  <i class="ph ph-airplane-tilt text-blue-600 text-lg"></i>
                </div>
                <div>
                  <span class="font-semibold text-[#002D1E] block poppins">{{ tax.airline?.name }}</span>
                  <span class="text-gray-400 poppins">{{ tax.airline?.code }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <span class="font-semibold text-[#002D1E] block poppins">{{ tax.tax_type?.name }}</span>
              <span class="text-gray-400 poppins text-xs">{{ tax.tax_type?.code }}</span>
            </td>
            <td class="px-6 py-4">
              <span :class="categoryClass(tax.tax_type?.category)" class="px-3 py-1 rounded-full font-semibold uppercase text-xs poppins">
                {{ formatCategory(tax.tax_type?.category) }}
              </span>
            </td>
            <td class="px-6 py-4">
              <span class="text-lg font-bold text-[#fe3787] poppins">₱{{ formatNumber(tax.amount) }}</span>
            </td>
            <td class="px-6 py-4">
              <span :class="statusClass(tax.tax_type?.is_active)" class="px-3 py-1 rounded-full font-semibold uppercase text-xs poppins">
                {{ tax.tax_type?.is_active ? 'Active' : 'Inactive' }}
              </span>
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
          <i class="ph ph-airplane-tilt text-2xl text-gray-400"></i>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2 poppins">No airline taxes found</h3>
        <p class="text-gray-500 poppins">Add airline-specific taxes and surcharges</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="p-12 text-center">
        <i class="ph ph-spinner animate-spin text-4xl text-[#fe3787]"></i>
        <p class="mt-2 text-gray-500 poppins">Loading airline taxes...</p>
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

    <!-- Airline Breakdown -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
        <h3 class="text-lg font-semibold text-[#002D1E] poppins mb-4">Taxes by Airline</h3>
        <div class="space-y-3">
          <div 
            v-for="(item, index) in airlineBreakdown" 
            :key="index"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-[1px]"
          >
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                <i class="ph ph-airplane-tilt text-blue-600"></i>
              </div>
              <span class="font-medium text-[#002D1E] poppins">{{ item.airline__name }}</span>
            </div>
            <div class="text-right">
              <span class="block font-bold text-[#fe3787] poppins">₱{{ formatNumber(item.total) }}</span>
              <span class="text-xs text-gray-500 poppins">{{ item.count }} taxes</span>
            </div>
          </div>
          <div v-if="airlineBreakdown.length === 0" class="text-center text-gray-500 py-4">
            No data available
          </div>
        </div>
      </div>

      <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
        <h3 class="text-lg font-semibold text-[#002D1E] poppins mb-4">Tax Type Distribution</h3>
        <div class="space-y-3">
          <div 
            v-for="(item, index) in taxTypeBreakdown" 
            :key="index"
            class="flex items-center justify-between"
          >
            <div class="flex items-center gap-3 flex-1">
              <div :class="['w-3 h-3 rounded-full', categoryClass(item.tax_type__category)]"></div>
              <span class="text-sm text-gray-600 poppins truncate">{{ item.tax_type__name }}</span>
            </div>
            <div class="flex items-center gap-3">
              <div class="w-32 bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-[#fe3787] h-2 rounded-full transition-all duration-300"
                  :style="{ width: (item.count / stats.total * 100) + '%' }"
                ></div>
              </div>
              <span class="text-sm font-semibold text-[#002D1E] poppins w-8 text-right">{{ item.count }}</span>
            </div>
          </div>
          <div v-if="taxTypeBreakdown.length === 0" class="text-center text-gray-500 py-4">
            No data available
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-[#002D1E]/60 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-md rounded-[1px] shadow-2xl overflow-hidden">
        <div class="bg-[#002D1E] p-4 text-white flex justify-between items-center">
          <h2 class="text-sm font-black uppercase tracking-[2px]">{{ isEditing ? 'Revise Airline Tax' : 'Register Airline Tax' }}</h2>
          <button @click="closeModal" class="text-white/70 hover:text-white transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveTax" class="p-6 space-y-5">
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Airline *</label>
            <select 
              v-model="form.airline" 
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
              required
            >
              <option value="">Select Airline</option>
              <option v-for="airline in airlines" :key="airline.id" :value="airline.id">
                {{ airline.code }} - {{ airline.name }}
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
                {{ tax.name }} ({{ tax.code }}) - {{ formatCategory(tax.category) }}
              </option>
            </select>
            <p v-if="taxTypes.length === 0" class="text-xs text-red-500 mt-1">
              No tax types loaded. Please check API connection.
            </p>
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
          <h2 class="text-sm font-black uppercase tracking-[2px]">Airline Tax Record</h2>
          <button @click="showDetailsModal = false" class="text-white/70 hover:text-white transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <div v-if="selectedTax" class="p-8 space-y-6">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
              <i class="ph ph-airplane-tilt text-3xl text-blue-600"></i>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-[#002D1E] poppins">{{ selectedTax.airline?.name }}</h3>
              <p class="text-sm text-gray-500 poppins">{{ selectedTax.airline?.code }}</p>
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
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Category</label>
            <div class="p-2 border border-gray-200 rounded-[1px]">
              <span :class="categoryClass(selectedTax.tax_type?.category)" class="px-3 py-1 rounded-full text-xs font-semibold uppercase poppins">
                {{ formatCategory(selectedTax.tax_type?.category) }}
              </span>
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Amount</label>
            <div class="p-2 border border-gray-200 rounded-[1px] text-2xl font-bold text-[#fe3787] poppins">
              ₱{{ formatNumber(selectedTax.amount) }}
            </div>
          </div>
          
          <div v-if="selectedTax.tax_type?.description">
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Description</label>
            <div class="p-2 border border-gray-200 rounded-[1px] text-sm text-gray-600 poppins">
              {{ selectedTax.tax_type?.description }}
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

// State
const taxes = ref([])
const airlines = ref([])
const taxTypes = ref([])
const loading = ref(false)
const showModal = ref(false)
const showDetailsModal = ref(false)
const selectedTax = ref(null)
const isEditing = ref(false)
const currentId = ref(null)

// Filters
const searchQuery = ref('')
const selectedAirline = ref('')
const selectedTaxType = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Stats
const stats = ref({
  total: 0,
  activeAirlines: 0,
  totalAmount: 0,
  averagePerAirline: 0
})

const airlineBreakdown = ref([])
const taxTypeBreakdown = ref([])

// Form
const form = ref({
  airline: '',
  tax_type: '',
  amount: 0
})

// Computed
const filteredTaxes = computed(() => {
  let filtered = taxes.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(tax => 
      tax.airline?.name?.toLowerCase().includes(query) ||
      tax.airline?.code?.toLowerCase().includes(query) ||
      tax.tax_type?.name?.toLowerCase().includes(query) ||
      tax.tax_type?.code?.toLowerCase().includes(query)
    )
  }
  
  if (selectedAirline.value) {
    filtered = filtered.filter(tax => tax.airline?.id === parseInt(selectedAirline.value))
  }
  
  if (selectedTaxType.value) {
    filtered = filtered.filter(tax => tax.tax_type?.id === parseInt(selectedTaxType.value))
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
const fetchData = async () => {
  loading.value = true
  try {
    const [taxesRes, airlinesRes, taxTypesRes] = await Promise.all([
      api.get('/airline-taxes/'),
      api.get('/airlines/'),
      api.get('/tax-types/')
    ])
    
    taxes.value = taxesRes.data.results || taxesRes.data
    airlines.value = airlinesRes.data.results || airlinesRes.data
    taxTypes.value = taxTypesRes.data.results || taxTypesRes.data
    
    calculateStats()
    calculateBreakdowns()
  } catch (err) {
    console.error('Fetch error:', err)
    alert('Failed to load data')
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  const total = taxes.value.length
  const uniqueAirlines = new Set(taxes.value.map(t => t.airline?.id)).size
  const totalAmount = taxes.value.reduce((sum, t) => sum + parseFloat(t.amount || 0), 0)
  const averagePerAirline = uniqueAirlines > 0 ? totalAmount / uniqueAirlines : 0
  
  stats.value = {
    total,
    activeAirlines: uniqueAirlines,
    totalAmount,
    averagePerAirline
  }
}

const calculateBreakdowns = () => {
  // Airline breakdown
  const airlineMap = {}
  taxes.value.forEach(tax => {
    const id = tax.airline?.id
    if (!airlineMap[id]) {
      airlineMap[id] = {
        airline__name: tax.airline?.name,
        total: 0,
        count: 0
      }
    }
    airlineMap[id].total += parseFloat(tax.amount || 0)
    airlineMap[id].count++
  })
  airlineBreakdown.value = Object.values(airlineMap).sort((a, b) => b.total - a.total)
  
  // Tax type breakdown
  const typeMap = {}
  taxes.value.forEach(tax => {
    const id = tax.tax_type?.id
    if (!typeMap[id]) {
      typeMap[id] = {
        tax_type__name: tax.tax_type?.name,
        tax_type__category: tax.tax_type?.category,
        count: 0
      }
    }
    typeMap[id].count++
  })
  taxTypeBreakdown.value = Object.values(typeMap).sort((a, b) => b.count - a.count)
}

const openAddModal = () => {
  isEditing.value = false
  currentId.value = null
  form.value = { airline: '', tax_type: '', amount: 0 }
  showModal.value = true
}

const editTax = (tax) => {
  isEditing.value = true
  currentId.value = tax.id
  form.value = {
    airline: tax.airline?.id,
    tax_type: tax.tax_type?.id,
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
      airline: form.value.airline,
      tax_type: form.value.tax_type,
      amount: parseFloat(form.value.amount)
    }
    
    if (isEditing.value) {
      await api.put(`/airline-taxes/${currentId.value}/`, payload)
      alert('Airline tax updated successfully!')
    } else {
      await api.post('/airline-taxes/', payload)
      alert('Airline tax added successfully!')
    }
    
    await fetchData()
    closeModal()
  } catch (err) {
    console.error('Save error:', err)
    alert('Error saving airline tax. Please check your input.')
  }
}

const deleteTax = async (id) => {
  if (!confirm('Are you sure you want to delete this airline tax?')) return
  
  try {
    await api.delete(`/airline-taxes/${id}/`)
    taxes.value = taxes.value.filter(t => t.id !== id)
    calculateStats()
    calculateBreakdowns()
    alert('Airline tax deleted successfully!')
  } catch (err) {
    console.error('Delete error:', err)
    alert('Failed to delete airline tax')
  }
}

const closeModal = () => {
  showModal.value = false
  showDetailsModal.value = false
  isEditing.value = false
  currentId.value = null
  form.value = { airline: '', tax_type: '', amount: 0 }
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
    case 'government': return 'bg-red-100 text-red-700'
    case 'airport': return 'bg-blue-100 text-blue-700'
    case 'airline': return 'bg-purple-100 text-purple-700'
    default: return 'bg-gray-100 text-gray-600'
  }
}

const statusClass = (isActive) => {
  return isActive ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
}

const filterTaxes = () => {
  currentPage.value = 1
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedAirline.value = ''
  selectedTaxType.value = ''
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