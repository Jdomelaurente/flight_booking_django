<template>
  <div class="p-6 poppins">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <button 
        @click="openAddModal" 
        class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[14px] rounded-[1px]"
      >
        <i class="ph ph-plus"></i> Add Travel Tax Rate
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Total Rates</p>
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
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Adult Rate</p>
            <p class="text-3xl font-bold text-blue-600">₱{{ formatNumber(adultRate) }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-blue-50 flex items-center justify-center border border-blue-100">
            <i class="ph ph-user text-blue-500 text-2xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Child Rate</p>
            <p class="text-3xl font-bold text-yellow-600">₱{{ formatNumber(childRate) }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-yellow-50 flex items-center justify-center border border-yellow-100">
            <i class="ph ph-baby text-yellow-500 text-2xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Infant Rate</p>
            <p class="text-3xl font-bold text-purple-600">₱{{ formatNumber(infantRate) }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-purple-50 flex items-center justify-center border border-purple-100">
            <i class="ph ph-baby-carriage text-purple-500 text-2xl"></i>
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
            placeholder="Search by tax type, passenger type..." 
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-[1px] w-full focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
            @input="debounceSearch"
          />
        </div>
        
        <select 
          v-model="selectedTaxType" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px] min-w-[150px]"
          @change="filterRates"
        >
          <option value="">All Tax Types</option>
          <option v-for="tax in taxTypes" :key="tax.id" :value="tax.id">
            {{ tax.name }}
          </option>
        </select>

        <select 
          v-model="selectedPassengerType" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px] min-w-[150px]"
          @change="filterRates"
        >
          <option value="">All Passenger Types</option>
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

    <!-- Rates Table -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Tax Type</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Passenger Type</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Amount</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Status</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="rate in paginatedRates" :key="rate.id" class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium">
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-[#fe3787] flex items-center justify-center">
                  <i class="ph ph-receipt text-white text-lg"></i>
                </div>
                <div>
                  <span class="font-semibold text-[#002D1E] block poppins">{{ rate.tax_type?.name }}</span>
                  <span class="text-gray-400 poppins text-xs">{{ rate.tax_type?.code }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <span :class="passengerTypeClass(rate.passenger_type)" class="px-3 py-1 rounded-full font-semibold uppercase text-xs poppins">
                {{ formatPassengerType(rate.passenger_type) }}
              </span>
            </td>
            <td class="px-6 py-4">
              <span class="text-lg font-bold poppins">₱{{ formatNumber(rate.amount) }}</span>
            </td>
            <td class="px-6 py-4">
              <span :class="statusClass(rate.tax_type?.is_active)" class="px-3 py-1 rounded-full font-semibold uppercase text-xs poppins">
                {{ rate.tax_type?.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="px-6 py-4 text-right">
              <button @click="viewDetails(rate)" class="text-blue-600 hover:text-blue-400 p-2" title="View Details">
                <i class="ph ph-eye text-lg"></i>
              </button>
              <button @click="editRate(rate)" class="text-green-600 hover:text-green-400 p-2" title="Edit">
                <i class="ph ph-pencil-simple text-lg"></i>
              </button>
              <button @click="deleteRate(rate.id)" class="text-red-600 hover:text-red-400 p-2" title="Delete">
                <i class="ph ph-trash text-lg"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="filteredRates.length === 0 && !loading" class="p-12 text-center">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <i class="ph ph-receipt text-2xl text-gray-400"></i>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2 poppins">No travel tax rates found</h3>
        <p class="text-gray-500 poppins">Add passenger-type specific tax rates</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="p-12 text-center">
        <i class="ph ph-spinner animate-spin text-4xl text-[#fe3787]"></i>
        <p class="mt-2 text-gray-500 poppins">Loading travel tax rates...</p>
      </div>

      <!-- Pagination -->
      <div v-if="filteredRates.length > itemsPerPage" class="px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-600 poppins">
            Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ filteredRates.length }} rates
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

    <!-- Passenger Type Summary -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
        <h3 class="text-sm font-black uppercase text-[#002D1E] tracking-[2px] mb-6">Rates by Passenger Type</h3>
        <div class="space-y-4">
          <div v-for="(rate, type) in passengerTypeSummary" :key="type" class="flex items-center justify-between p-4 bg-gray-50 rounded-[1px]">
            <div class="flex items-center gap-3">
            <div :class="['w-12 h-12 rounded-full flex items-center justify-center', passengerTypeIconBg(type)]">
              <i :class="['ph', 'text-xl', passengerTypeIcon(type)]"></i>
            </div>
              <div>
                <span class="font-semibold block poppins capitalize">{{ formatPassengerType(type) }}</span>
                <span class="text-xs text-gray-500 poppins">{{ rate.count }} tax type(s)</span>
              </div>
            </div>
            <div class="text-right">
              <span class="block text-2xl font-bold poppins">₱{{ formatNumber(rate.total) }}</span>
              <span class="text-xs text-gray-400 poppins">avg: ₱{{ formatNumber(rate.average) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
        <h3 class="text-sm font-black uppercase text-[#002D1E] tracking-[2px] mb-6">Tax Type Distribution</h3>
        <div class="space-y-3">
          <div 
            v-for="(item, index) in taxTypeBreakdown" 
            :key="index"
            class="flex items-center justify-between"
          >
            <div class="flex items-center gap-3 flex-1">
              <div class="w-3 h-3 rounded-full bg-[#fe3787]"></div>
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
          <h2 class="text-sm font-black uppercase tracking-[2px]">{{ isEditing ? 'Revise Travel Tax' : 'Register Travel Tax' }}</h2>
          <button @click="closeModal" class="text-white/70 hover:text-white transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveRate" class="p-6 space-y-5">
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
              {{ isEditing ? 'Update Rate' : 'Save Rate' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- View Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 z-50 flex items-center justify-center bg-[#002D1E]/60 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-lg rounded-[1px] shadow-2xl overflow-hidden">
        <div class="bg-[#002D1E] p-4 text-white flex justify-between items-center">
          <h2 class="text-sm font-black uppercase tracking-[2px]">Travel Tax Information</h2>
          <button @click="showDetailsModal = false" class="text-white/70 hover:text-white transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <div v-if="selectedRate" class="p-8 space-y-6">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-16 h-16 rounded-full bg-[#fe3787]/10 flex items-center justify-center">
              <i class="ph ph-receipt text-3xl text-[#fe3787]"></i>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-[#002D1E] poppins">{{ selectedRate.tax_type?.name }}</h3>
              <span class="font-mono text-sm bg-gray-100 px-2 py-1 rounded poppins">{{ selectedRate.tax_type?.code }}</span>
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Passenger Type</label>
              <div class="p-2 border border-gray-200 rounded-[1px]">
                <span :class="passengerTypeClass(selectedRate.passenger_type)" class="px-3 py-1 rounded-full text-xs font-semibold uppercase poppins">
                  {{ formatPassengerType(selectedRate.passenger_type) }}
                </span>
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Amount</label>
              <div class="p-2 border border-gray-200 rounded-[1px] text-2xl font-bold text-[#fe3787] poppins">
                ₱{{ formatNumber(selectedRate.amount) }}
              </div>
            </div>
          </div>
          
          <div v-if="selectedRate.tax_type?.description">
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Description</label>
            <div class="p-2 border border-gray-200 rounded-[1px] text-sm text-gray-600 poppins">
              {{ selectedRate.tax_type?.description }}
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
const rates = ref([])
const taxTypes = ref([])
const loading = ref(false)
const showModal = ref(false)
const showDetailsModal = ref(false)
const selectedRate = ref(null)
const isEditing = ref(false)
const currentId = ref(null)

// Filters
const searchQuery = ref('')
const selectedTaxType = ref('')
const selectedPassengerType = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Stats
const stats = ref({
  total: 0
})

const taxTypeBreakdown = ref([])

// Form
const form = ref({
  tax_type: '',
  passenger_type: '',
  amount: 0
})

// Computed
const adultRate = computed(() => {
  const rate = rates.value.find(r => r.passenger_type === 'adult')
  return rate ? rate.amount : 0
})

const childRate = computed(() => {
  const rate = rates.value.find(r => r.passenger_type === 'child')
  return rate ? rate.amount : 0
})

const infantRate = computed(() => {
  const rate = rates.value.find(r => r.passenger_type === 'infant')
  return rate ? rate.amount : 0
})

const filteredRates = computed(() => {
  let filtered = rates.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(rate => 
      rate.tax_type?.name?.toLowerCase().includes(query) ||
      rate.tax_type?.code?.toLowerCase().includes(query) ||
      rate.passenger_type?.toLowerCase().includes(query)
    )
  }
  
  if (selectedTaxType.value) {
    filtered = filtered.filter(rate => rate.tax_type?.id === parseInt(selectedTaxType.value))
  }
  
  if (selectedPassengerType.value) {
    filtered = filtered.filter(rate => rate.passenger_type === selectedPassengerType.value)
  }
  
  return filtered
})

const totalPages = computed(() => Math.ceil(filteredRates.value.length / itemsPerPage))

const paginatedRates = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredRates.value.slice(start, end)
})

const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredRates.value.length))

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
    adult: { total: 0, count: 0, average: 0 },
    child: { total: 0, count: 0, average: 0 },
    infant: { total: 0, count: 0, average: 0 }
  }
  
  rates.value.forEach(rate => {
    const type = rate.passenger_type
    if (summary[type]) {
      summary[type].total += parseFloat(rate.amount || 0)
      summary[type].count++
    }
  })
  
  Object.keys(summary).forEach(key => {
    if (summary[key].count > 0) {
      summary[key].average = summary[key].total / summary[key].count
    }
  })
  
  return summary
})

// Methods
const fetchData = async () => {
  loading.value = true
  try {
    const [ratesRes, taxTypesRes] = await Promise.all([
      api.get('/passenger-tax-rates/'),
      api.get('/tax-types/')
    ])
    
    rates.value = ratesRes.data.results || ratesRes.data
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
  stats.value.total = rates.value.length
}

const calculateBreakdowns = () => {
  // Tax type breakdown
  const typeMap = {}
  rates.value.forEach(rate => {
    const id = rate.tax_type?.id
    if (!typeMap[id]) {
      typeMap[id] = {
        tax_type__name: rate.tax_type?.name,
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
  form.value = { tax_type: '', passenger_type: '', amount: 0 }
  showModal.value = true
}

const editRate = (rate) => {
  isEditing.value = true
  currentId.value = rate.id
  form.value = {
    tax_type: rate.tax_type?.id,
    passenger_type: rate.passenger_type,
    amount: rate.amount
  }
  showModal.value = true
}

const viewDetails = (rate) => {
  selectedRate.value = rate
  showDetailsModal.value = true
}

const saveRate = async () => {
  try {
    const payload = {
      tax_type: form.value.tax_type,
      passenger_type: form.value.passenger_type,
      amount: parseFloat(form.value.amount)
    }
    
    if (isEditing.value) {
      await api.put(`/passenger-tax-rates/${currentId.value}/`, payload)
      alert('Travel tax rate updated successfully!')
    } else {
      await api.post('/passenger-tax-rates/', payload)
      alert('Travel tax rate added successfully!')
    }
    
    await fetchData()
    closeModal()
  } catch (err) {
    console.error('Save error:', err)
    console.error('Error response:', err.response?.data)
    alert('Error: ' + JSON.stringify(err.response?.data || err.message))
  }
}

const deleteRate = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Delete Travel Tax Rate?',
    message: 'Are you sure you want to permanently delete this travel tax rate record?',
    variant: 'danger',
    confirmText: 'Delete',
    loadingText: 'Deleting...'
  });

  if (!confirmed) return;
  
  modalStore.setLoader(true);
  try {
    await api.delete(`/passenger-tax-rates/${id}/`)
    rates.value = rates.value.filter(r => r.id !== id)
    calculateStats()
    calculateBreakdowns()
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
  form.value = { tax_type: '', passenger_type: '', amount: 0 }
}

const formatNumber = (num) => {
  return parseFloat(num || 0).toLocaleString('en-PH', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
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
    case 'adult': return 'bg-blue-200'
    case 'child': return 'bg-yellow-200'
    case 'infant': return 'bg-purple-200'
    default: return 'bg-gray-100 text-gray-600'
  }
}

const passengerTypeIcon = (type) => {
  switch(type) {
    case 'adult': return 'ph-user'
    case 'child': return 'ph-baby '
    case 'infant': return 'ph-baby-carriage '
    default: return 'ph-user text-gray-600'
  }
}

const passengerTypeIconBg = (type) => {
  switch(type) {
    case 'adult': return 'bg-blue-200'
    case 'child': return 'bg-yellow-200'
    case 'infant': return 'bg-purple-200'
    default: return 'bg-gray-100'
  }
}

const statusClass = (isActive) => {
  return isActive ? 'bg-green-200' : 'bg-gray-200'
}

const filterRates = () => {
  currentPage.value = 1
}

const clearFilters = () => {
  searchQuery.value = ''
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