<template>
  <div class="p-6 poppins">
    <!-- Header & Tools Section -->
    <AdminTableTool 
      v-model="searchQuery" 
      placeholder="Search trainee name or passport..."
      @update:modelValue="debounceSearch"
    >
      <template #filters>
        <div class="flex items-center gap-2">
          <select 
            v-model="selectedType" 
            class="text-[11px] font-bold border border-gray-200 px-3 py-2 bg-white rounded-[1px] outline-none focus:border-[#fe3787] poppins cursor-pointer"
            @change="fetchPassengers"
          >
            <option value="">Any Type</option>
            <option value="Adult">Adult</option>
            <option value="Child">Child</option>
            <option value="Infant">Infant</option>
          </select>
        </div>
      </template>

      <template #actions>
        <div class="flex items-center gap-2">
          <button @click="exportPassengers" class="bg-white border border-gray-200 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[12px] rounded-[1px] shadow-sm transition-all">
            <i class="ph ph-export text-[14px]"></i> Export
          </button>
          <button @click="openAddModal" class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#e6327a] font-bold poppins text-[12px] rounded-[1px] shadow-md transition-all">
            <i class="ph ph-plus-circle text-[14px]"></i> Enroll
          </button>
        </div>
      </template>
    </AdminTableTool>

    <!-- Passenger Stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
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



    <!-- Main Table -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Trainee Name</th>
            <th class="px-6 py-4 poppins">Identification</th>
            <th class="px-6 py-4 poppins text-center">Type</th>
            <th class="px-6 py-4 poppins">Birth Date</th>
            <th class="px-6 py-4 poppins">Loyalty</th>
            <th class="px-6 py-4 text-right poppins">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr 
            v-for="passenger in paginatedPassengers" 
            :key="passenger.id" 
            :id="`passenger-row-${passenger.id}`"
            :class="{'highlight-active': highlightedId === passenger.id}"
            class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium"
          >
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <i :class="getPassengerIcon(passenger.passenger_type), 'text-blue-600'"></i>
                </div>
                <div>
                  <span class="font-bold text-[#002D1E] block poppins">{{ passenger.first_name }} {{ passenger.last_name }}</span>
                  <span class="text-[10px] text-gray-400 poppins uppercase tracking-wider">Trainee ID #{{ passenger.id }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-2 mb-1">
                <i class="ph ph-passport text-gray-400"></i>
                <span class="font-bold text-[#002D1E] poppins">{{ passenger.passport_number || 'N/A' }}</span>
              </div>
              <div class="text-[10px] text-gray-400 poppins uppercase">{{ passenger.nationality || 'Unspecified' }}</div>
            </td>
            <td class="px-6 py-4 text-center">
              <span :class="typeClass(passenger.passenger_type)" class="px-3 py-1 rounded-full text-[10px] font-bold uppercase poppins">
                {{ passenger.passenger_type }}
              </span>
            </td>
            <td class="px-6 py-4">
              <div class="font-bold text-[#002D1E] poppins">{{ formatDate(passenger.date_of_birth) || '—' }}</div>
              <div class="text-[10px] text-gray-400 poppins uppercase">Age: {{ passenger.age || '—' }}</div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-2">
                <span :class="bookingClass(passenger.booking_count)" class="px-3 py-1 rounded-[1px] text-[10px] font-bold uppercase poppins">
                  {{ passenger.booking_count }} Bookings
                </span>
              </div>
              <div v-if="passenger.last_booking" class="text-[10px] text-gray-400 mt-1 poppins uppercase">
                Recent: {{ formatDate(passenger.last_booking) }}
              </div>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="editPassenger(passenger)" class="text-green-600 hover:text-green-400 p-2 transition-colors">
                  <i class="ph ph-pencil-simple text-lg"></i>
                </button>
                <button @click="deletePassenger(passenger.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors">
                  <i class="ph ph-trash text-lg"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="passengers.length === 0 && !loading" class="p-12 text-center poppins">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-50 border border-gray-100 rounded-full flex items-center justify-center">
          <i class="ph ph-users text-2xl text-gray-300"></i>
        </div>
        <h3 class="text-lg font-bold text-[#002D1E] mb-2 poppins">No Data Found</h3>
        <p class="text-sm text-gray-400 poppins">Passenger records will appear here once bookings are created.</p>
      </div>

      <!-- Pagination -->
      <div v-if="filteredPassengers.length > itemsPerPage" class="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
        <div class="flex items-center justify-between">
          <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
            Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ filteredPassengers.length }}
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

    <!-- Add/Edit Passenger Modal -->
    <div v-if="showAddModal || showEditModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-lg p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">{{ isEditing ? 'Edit Profile' : 'New Passenger' }}</h2>
          <button @click="closeModal" class="text-gray-400 hover:text-black transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="savePassenger" class="space-y-6">
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Title</label>
              <select v-model="form.title" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px] bg-white" required>
                <option value="MR">Mr.</option>
                <option value="MRS">Mrs.</option>
                <option value="MS">Ms.</option>
              </select>
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">First Name</label>
              <input v-model="form.first_name" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="e.g. JUAN" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Middle Name (Optional)</label>
              <input v-model="form.middle_name" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="e.g. DELA">
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Last Name</label>
              <input v-model="form.last_name" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="e.g. CRUZ" required>
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Type</label>
              <select v-model="form.passenger_type" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px] bg-white" required>
                <option value="">Select Type</option>
                <option value="Adult">Adult</option>
                <option value="Child">Child</option>
                <option value="Infant">Infant</option>
              </select>
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Date of Birth</label>
              <input v-model="form.date_of_birth" type="date" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]">
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Passport Number</label>
              <input v-model="form.passport_number" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]">
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Nationality</label>
              <input v-model="form.nationality" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]">
            </div>
          </div>
          
          <div class="flex justify-end gap-3 pt-6 border-t mt-4">
            <button type="button" @click="closeModal" class="text-sm text-gray-500 font-medium hover:text-gray-700 poppins">Cancel</button>
            <button type="submit" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins">
              {{ isEditing ? 'Update Profile' : 'Save Profile' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/admin/api'
import { useModalStore } from '@/stores/modal'
import AdminTableTool from '@/components/admin/AdminTableTool.vue';

const modalStore = useModalStore()
const route = useRoute()

// Reactive state
const passengers = ref([])
const loading = ref(false)
const showDetailsModal = ref(false)
const showAddModal = ref(false)
const showEditModal = ref(false)
const selectedPassenger = ref(null)
const isEditing = ref(false)
const currentId = ref(null)
const highlightedId = ref(null);

// Filters and pagination
const searchQuery = ref('')
const selectedType = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Form data
const form = ref({
  first_name: '',
  middle_name: '',
  last_name: '',
  passenger_type: 'Adult',
  date_of_birth: '',
  passport_number: '',
  nationality: '',
  title: 'MR',
  linked_adult: null
})

// Computed properties
const statsItems = computed(() => {
  const total = passengers.value.length
  const adults = passengers.value.filter(p => p.passenger_type === 'Adult').length
  const children = passengers.value.filter(p => p.passenger_type === 'Child').length
  const infants = passengers.value.filter(p => p.passenger_type === 'Infant').length
  
  return {
    'Total Passengers': total,
    'Adult Group': adults,
    'Children Group': children,
    'Infant Group': infants,
  }
})

const statIcon = (label) => {
  if (label === 'Total Passengers') return 'ph ph-users-three';
  if (label === 'Adult Group') return 'ph ph-user';
  if (label === 'Children Group') return 'ph ph-baby';
  return 'ph ph-infant';
};

const statIconClass = (label) => {
  if (label === 'Total Passengers') return 'bg-blue-100 text-blue-600';
  if (label === 'Adult Group') return 'bg-green-100 text-green-600';
  if (label === 'Children Group') return 'bg-purple-100 text-purple-600';
  return 'bg-pink-100 text-pink-600';
};

const adultPassengers = computed(() => {
  return passengers.value.filter(p => p.passenger_type === 'Adult')
})

const filteredPassengers = computed(() => {
  let filtered = passengers.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(passenger => 
      passenger.first_name?.toLowerCase().includes(query) ||
      passenger.last_name?.toLowerCase().includes(query) ||
      (passenger.passport_number && passenger.passport_number.toLowerCase().includes(query))
    )
  }
  
  if (selectedType.value) {
    filtered = filtered.filter(passenger => passenger.passenger_type === selectedType.value)
  }
  
  return filtered
})

const totalPages = computed(() => {
  return Math.ceil(filteredPassengers.value.length / itemsPerPage)
})

const paginatedPassengers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredPassengers.value.slice(start, end)
})

const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredPassengers.value.length))

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
const openAddModal = () => {
  isEditing.value = false
  currentId.value = null
  form.value = {
    first_name: '', 
    middle_name: '',
    last_name: '', 
    passenger_type: 'Adult', 
    date_of_birth: '', 
    passport_number: '', 
    nationality: '', 
    title: 'MR', 
    linked_adult: null
  }
  showAddModal.value = true
}

const fetchPassengers = async () => {
  loading.value = true
  try {
    const params = {}
    if (selectedType.value) params.type = selectedType.value
    if (searchQuery.value) params.search = searchQuery.value
    
    const response = await api.get('/passengers/', { params })
    passengers.value = (response.data.results || response.data).map(p => ({
      ...p,
      age: calculateAge(p.date_of_birth)
    }))

    if (route.query.page) {
        currentPage.value = parseInt(route.query.page);
    }

    if (route.query.highlight) {
        const hId = parseInt(route.query.highlight);
        highlightedId.value = hId;

        // Auto-navigate to the correct page for this ID
        const index = passengers.value.findIndex(p => p.id === hId);
        if (index !== -1) {
            currentPage.value = Math.floor(index / itemsPerPage) + 1;
        }

        setTimeout(() => {
            const el = document.getElementById(`passenger-row-${hId}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => { highlightedId.value = null; }, 3000);
        }, 500);
    }
  } catch (err) {
    console.error('Fetch error:', err)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  fetchPassengers()
}

const editPassenger = (passenger) => {
  isEditing.value = true
  currentId.value = passenger.id
  form.value = {
    first_name: passenger.first_name,
    last_name: passenger.last_name,
    passenger_type: passenger.passenger_type,
    date_of_birth: passenger.date_of_birth ? passenger.date_of_birth.split('T')[0] : '',
    passport_number: passenger.passport_number || '',
    nationality: passenger.nationality || '',
    title: passenger.title || '',
    linked_adult: passenger.linked_adult || null
  }
  showEditModal.value = true
}

const deletePassenger = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Expunge Passenger?',
    message: 'Are you sure you want to permanently delete this passenger data? This action cannot be undone.',
    variant: 'danger',
    confirmText: 'Expunge',
    loadingText: 'Expunging...'
  });

  if (confirmed) {
    modalStore.setLoader(true);
    try {
      await api.delete(`/passengers/${id}/`)
      passengers.value = passengers.value.filter(p => p.id !== id)
      modalStore.close(true);
    } catch (err) {
      console.error('Delete error:', err);
      modalStore.setLoader(false);
      alert('Deletion restricted: Passenger has active booking history.');
    }
  }
}

const savePassenger = async () => {
  try {
    // Basic cleanup of data
    const payload = { ...form.value };
    console.log('Sending Passenger Payload:', payload);
    
    // Convert empty strings to null for backend validation
    if (!payload.date_of_birth) payload.date_of_birth = null;
    if (!payload.passport_number) payload.passport_number = null;
    if (!payload.nationality) payload.nationality = null;
    if (!payload.middle_name) payload.middle_name = null;
    
    // Conventions: Uppercase names
    payload.first_name = payload.first_name?.toUpperCase();
    payload.last_name = payload.last_name?.toUpperCase();
    if (payload.middle_name) payload.middle_name = payload.middle_name.toUpperCase();

    if (isEditing.value) {
      await api.put(`/passengers/${currentId.value}/`, payload)
    } else {
      await api.post('/passengers/', payload)
    }
    await fetchPassengers()
    closeModal()
  } catch (err) {
    console.error('Save error:', err)
    const errorData = err.response?.data;
    let errorMsg = 'Failed to save passenger profile.';
    
    if (errorData) {
      if (typeof errorData === 'object') {
        errorMsg = Object.entries(errorData)
          .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`)
          .join('\n');
      } else {
        errorMsg = errorData;
      }
    }
    
    alert('Error Saving Passenger:\n\n' + errorMsg);
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  showDetailsModal.value = false
  isEditing.value = false
  currentId.value = null
  form.value = {
    first_name: '', last_name: '', passenger_type: '', 
    date_of_birth: '', passport_number: '', nationality: '', 
    title: 'MR', linked_adult: null
  }
}

const exportPassengers = async () => {
  try {
    const response = await api.get('/passengers/export/', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `passengers_${new Date().toISOString().split('T')[0]}.csv`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    console.error('Export error:', err)
  }
}

const getPassengerIcon = (type) => {
  switch(type) {
    case 'Adult': return 'ph ph-user'
    case 'Child': return 'ph ph-baby'
    case 'Infant': return 'ph ph-infant'
    default: return 'ph ph-user-circle'
  }
}

const typeClass = (type) => {
  switch(type) {
    case 'Adult': return 'bg-green-100 text-green-700'
    case 'Child': return 'bg-purple-100 text-purple-700'
    case 'Infant': return 'bg-pink-100 text-pink-700'
    default: return 'bg-gray-100 text-gray-500'
  }
}

const bookingClass = (count) => {
  if (count === 0) return 'bg-gray-100 text-gray-400'
  if (count === 1) return 'bg-blue-100 text-blue-700'
  return 'bg-[#fe3787]/10 text-[#fe3787]'
}

const calculateAge = (dateString) => {
  if (!dateString) return null
  const birthDate = new Date(dateString)
  const today = new Date()
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) age--
  return age
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric'
  })
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedType.value = ''
  currentPage.value = 1
  fetchPassengers()
}

let searchTimeout = null
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => { fetchPassengers() }, 500)
}

const prevPage = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const goToPage = (page) => { if (page !== '...') currentPage.value = page }

watch([searchQuery, selectedType], () => { currentPage.value = 1 })

onMounted(fetchPassengers)
</script>

<style scoped>
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

.poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
