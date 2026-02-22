<template>
  <div class="p-6 poppins">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <button 
        @click="openAddModal" 
        class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[14px] rounded-[1px]"
      >
        <i class="ph ph-plus"></i> Add Airport Fee
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Total Fees</p>
            <p class="text-3xl font-bold text-[#002D1E]">{{ stats.total }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-green-50 flex items-center justify-center border border-green-100">
            <i class="ph ph-airplane-landing text-green-500 text-2xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Active Fees</p>
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
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Total Revenue</p>
            <p class="text-3xl font-bold text-[#fe3787]">₱{{ formatNumber(stats.totalRevenue) }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-pink-50 flex items-center justify-center border border-pink-100">
            <i class="ph ph-currency-circle-dollar text-[#fe3787] text-2xl"></i>
          </div>
        </div>
      </div>
      <div class="bg-white p-5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1">Avg Fee</p>
            <p class="text-3xl font-bold text-purple-600">₱{{ formatNumber(stats.averageFee) }}</p>
          </div>
          <div class="w-14 h-14 rounded-full bg-purple-50 flex items-center justify-center border border-purple-100">
            <i class="ph ph-chart-bar text-purple-500 text-2xl"></i>
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
            placeholder="Search by airport, fee type..." 
            class="pl-10 pr-4 py-2 border border-gray-300 rounded-[1px] w-full focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins"
            @input="debounceSearch"
          />
        </div>
        
        <select 
          v-model="selectedAirport" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px] min-w-[150px]"
          @change="filterFees"
        >
          <option value="">All Airports</option>
          <option v-for="airport in airports" :key="airport.id" :value="airport.id">
            {{ airport.code }} - {{ airport.name }}
          </option>
        </select>

        <select 
          v-model="selectedTaxType" 
          class="border border-gray-300 px-3 py-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins text-[14px] min-w-[150px]"
          @change="filterFees"
        >
          <option value="">All Fee Types</option>
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

    <!-- Fees Table -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Airport</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Fee Type</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Category</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Amount</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest">Status</th>
            <th class="px-6 py-4 text-[11px] uppercase font-black text-[#002D1E] tracking-widest text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="fee in paginatedFees" :key="fee.id" class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium">
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-[#fe3787] flex items-center justify-center">
                  <i class="ph ph-airplane-tilt text-white text-lg"></i>
                </div>
                <div>
                  <span class="font-semibold text-[#002D1E] block poppins">{{ fee.airport?.name }}</span>
                  <span class="text-gray-400 poppins text-xs">{{ fee.airport?.code }} • {{ fee.airport?.city }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <span class="font-semibold text-[#002D1E] block poppins">{{ fee.tax_type?.name }}</span>
              <span class="font-mono text-xs bg-gray-100 px-2 py-0.5 rounded poppins">{{ fee.tax_type?.code }}</span>
            </td>
            <td class="px-6 py-4">
              <span :class="categoryClass(fee.tax_type?.category)" class="px-3 py-1 rounded-full font-semibold uppercase text-xs poppins">
                {{ formatCategory(fee.tax_type?.category) }}
              </span>
            </td>
            <td class="px-6 py-4">
              <span class="text-lg font-bold text-[#002D1E] poppins">₱{{ formatNumber(fee.amount) }}</span>
            </td>
            <td class="px-6 py-4">
              <span :class="statusClass(fee.tax_type?.is_active)" class="px-3 py-1 rounded-full font-semibold uppercase text-xs poppins">
                {{ fee.tax_type?.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="px-6 py-4 text-right">
              <button @click="viewDetails(fee)" class="text-blue-600 hover:text-blue-400 p-2" title="View Details">
                <i class="ph ph-eye text-lg"></i>
              </button>
              <button @click="editFee(fee)" class="text-green-600 hover:text-green-400 p-2" title="Edit">
                <i class="ph ph-pencil-simple text-lg"></i>
              </button>
              <button @click="deleteFee(fee.id)" class="text-red-600 hover:text-red-400 p-2" title="Delete">
                <i class="ph ph-trash text-lg"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="filteredFees.length === 0 && !loading" class="p-12 text-center">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <i class="ph ph-airplane-landing text-2xl text-gray-400"></i>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2 poppins">No airport fees found</h3>
        <p class="text-gray-500 poppins">Add airport fees to manage terminal charges</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="p-12 text-center">
        <i class="ph ph-spinner animate-spin text-4xl text-[#fe3787]"></i>
        <p class="mt-2 text-gray-500 poppins">Loading airport fees...</p>
      </div>

      <!-- Pagination -->
      <div v-if="filteredFees.length > itemsPerPage" class="px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-600 poppins">
            Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ filteredFees.length }} fees
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
          <h2 class="text-sm font-black uppercase tracking-[2px]">{{ isEditing ? 'Revise Airport Fee' : 'Register Airport Fee' }}</h2>
          <button @click="closeModal" class="text-white/70 hover:text-white transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveFee" class="p-6 space-y-5">
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Airport *</label>
            <select 
              v-model="form.airport" 
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
              required
            >
              <option value="">Select Airport</option>
              <option v-for="airport in airports" :key="airport.id" :value="airport.id">
                {{ airport.code }} - {{ airport.name }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-600 uppercase mb-1 poppins">Fee Type *</label>
            <select 
              v-model="form.tax_type" 
              class="w-full border border-gray-300 p-2 rounded-[1px] focus:outline-none focus:ring-1 focus:ring-[#fe3787] focus:border-[#fe3787] poppins" 
              required
            >
              <option value="">Select Fee Type</option>
              <option v-for="tax in taxTypes" :key="tax.id" :value="tax.id">
                {{ tax.name }} ({{ tax.code }})
              </option>
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
              {{ isEditing ? 'Update Fee' : 'Save Fee' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- View Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 z-50 flex items-center justify-center bg-[#002D1E]/60 backdrop-blur-sm p-4">
      <div class="bg-white w-full max-w-lg rounded-[1px] shadow-2xl overflow-hidden">
        <div class="bg-[#002D1E] p-4 text-white flex justify-between items-center">
          <h2 class="text-sm font-black uppercase tracking-[2px]">Airport Fee Information</h2>
          <button @click="showDetailsModal = false" class="text-white/70 hover:text-white transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <div v-if="selectedFee" class="p-8 space-y-6">
          <div class="flex items-center gap-4 mb-4">
            <div class="w-16 h-16 rounded-full bg-[#fe3787]/10 flex items-center justify-center">
              <i class="ph ph-airplane-tilt text-3xl text-[#fe3787]"></i>
            </div>
            <div>
              <h3 class="text-xl font-semibold text-[#002D1E] poppins">{{ selectedFee.airport?.name }}</h3>
              <p class="text-sm text-gray-500 poppins">{{ selectedFee.airport?.code }} • {{ selectedFee.airport?.city }}</p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1 poppins">Fee Type</label>
              <div class="p-3 border border-gray-200 rounded-[1px] poppins text-sm font-medium">{{ selectedFee.tax_type?.name }}</div>
            </div>
            <div>
              <label class="block text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1 poppins">Code</label>
              <div class="p-3 border border-gray-200 rounded-[1px] font-mono text-sm">{{ selectedFee.tax_type?.code }}</div>
            </div>
          </div>

          <div>
            <label class="block text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1 poppins">Category</label>
            <div class="p-3 border border-gray-200 rounded-[1px]">
              <span :class="categoryClass(selectedFee.tax_type?.category)" class="px-3 py-1 rounded-full text-xs font-semibold uppercase poppins">
                {{ formatCategory(selectedFee.tax_type?.category) }}
              </span>
            </div>
          </div>

          <div>
            <label class="block text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1 poppins">Amount</label>
            <div class="p-3 border border-gray-200 rounded-[1px] text-2xl font-bold text-[#fe3787] poppins">
              ₱{{ formatNumber(selectedFee.amount) }}
            </div>
          </div>

          <div>
            <label class="block text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1 poppins">Status</label>
            <div class="p-3 border border-gray-200 rounded-[1px]">
              <span :class="statusClass(selectedFee.tax_type?.is_active)" class="px-3 py-1 rounded-full text-xs font-semibold uppercase poppins">
                {{ selectedFee.tax_type?.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>

          <div v-if="selectedFee.tax_type?.description">
            <label class="block text-[10px] uppercase font-black text-gray-400 tracking-[2px] mb-1 poppins">Description</label>
            <div class="p-3 border border-gray-200 rounded-[1px] text-sm text-gray-600 poppins">
              {{ selectedFee.tax_type?.description }}
            </div>
          </div>
        </div>
        
        <div class="flex justify-end gap-2 p-6 pt-0 border-t">
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
const fees = ref([])
const airports = ref([])
const taxTypes = ref([])
const loading = ref(false)
const showModal = ref(false)
const showDetailsModal = ref(false)
const selectedFee = ref(null)
const isEditing = ref(false)
const currentId = ref(null)

// Filters
const searchQuery = ref('')
const selectedAirport = ref('')
const selectedTaxType = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Stats
const stats = ref({
  total: 0,
  active: 0,
  totalRevenue: 0,
  averageFee: 0
})

// Form
const form = ref({
  airport: '',
  tax_type: '',
  amount: 0
})

// Computed
const filteredFees = computed(() => {
  let filtered = fees.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(fee => 
      fee.airport?.name?.toLowerCase().includes(query) ||
      fee.airport?.code?.toLowerCase().includes(query) ||
      fee.tax_type?.name?.toLowerCase().includes(query) ||
      fee.tax_type?.code?.toLowerCase().includes(query)
    )
  }
  
  if (selectedAirport.value) {
    filtered = filtered.filter(fee => fee.airport?.id === parseInt(selectedAirport.value))
  }
  
  if (selectedTaxType.value) {
    filtered = filtered.filter(fee => fee.tax_type?.id === parseInt(selectedTaxType.value))
  }
  
  return filtered
})

const totalPages = computed(() => Math.ceil(filteredFees.value.length / itemsPerPage))

const paginatedFees = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredFees.value.slice(start, end)
})

const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredFees.value.length))

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
    const [feesRes, airportsRes, taxTypesRes] = await Promise.all([
      api.get('/airport-fees/'),
      api.get('/airports/'),
      api.get('/tax-types/')
    ])
    
    fees.value = feesRes.data.results || feesRes.data
    airports.value = airportsRes.data.results || airportsRes.data
    const allTaxTypes = taxTypesRes.data.results || taxTypesRes.data
    taxTypes.value = allTaxTypes.filter(t => t.category === 'airport')
    
    calculateStats()
  } catch (err) {
    console.error('Fetch error:', err)
    alert('Failed to load data')
  } finally {
    loading.value = false
  }
}

const calculateStats = () => {
  const total = fees.value.length
  const active = fees.value.filter(f => f.tax_type?.is_active).length
  const totalRevenue = fees.value.reduce((sum, f) => sum + parseFloat(f.amount || 0), 0)
  const averageFee = total > 0 ? totalRevenue / total : 0
  
  stats.value = { total, active, totalRevenue, averageFee }
}

const openAddModal = () => {
  isEditing.value = false
  currentId.value = null
  form.value = { airport: '', tax_type: '', amount: 0 }
  showModal.value = true
}

const editFee = (fee) => {
  isEditing.value = true
  currentId.value = fee.id
  form.value = {
    airport: fee.airport?.id,
    tax_type: fee.tax_type?.id,
    amount: fee.amount
  }
  showModal.value = true
}

const viewDetails = (fee) => {
  selectedFee.value = fee
  showDetailsModal.value = true
}

const saveFee = async () => {
  try {
    const payload = {
      airport_id: form.value.airport,
      tax_type_id: form.value.tax_type,
      amount: parseFloat(form.value.amount)
    }
    
    if (isEditing.value) {
      await api.put(`/airport-fees/${currentId.value}/`, payload)
      alert('Airport fee updated successfully!')
    } else {
      await api.post('/airport-fees/', payload)
      alert('Airport fee added successfully!')
    }
    
    await fetchData()
    closeModal()
  } catch (err) {
    console.error('Full error:', err)
    console.error('Error response:', err.response?.data)
    alert('Error: ' + JSON.stringify(err.response?.data || err.message))
  }
}

const deleteFee = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Purge Airport Fee?',
    message: 'Are you sure you want to permanently delete this airport fee record?',
    variant: 'danger',
    confirmText: 'Purge',
    loadingText: 'Purging...'
  });

  if (!confirmed) return;
  
  modalStore.setLoader(true);
  try {
    await api.delete(`/airport-fees/${id}/`)
    fees.value = fees.value.filter(f => f.id !== id)
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
  form.value = { airport: '', tax_type: '', amount: 0 }
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
  return map[category] || category || 'N/A'
}

const categoryClass = (category) => {
  switch(category) {
    case 'government': return 'bg-red-200 text-red-700'
    case 'airport': return 'bg-blue-200 text-blue-700'
    case 'airline': return 'bg-purple-200 text-purple-700'
    default: return 'bg-gray-200 text-gray-600'
  }
}

const statusClass = (isActive) => {
  return isActive ? 'bg-green-200 text-green-700' : 'bg-gray-200 text-gray-500'
}

const filterFees = () => {
  currentPage.value = 1
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedAirport.value = ''
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