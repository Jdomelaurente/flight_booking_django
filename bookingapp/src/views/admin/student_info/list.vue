<template>
  <div class="p-6 poppins">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-2">
        <button 
          @click="exportStudents" 
          class="bg-white border border-gray-200 text-gray-700 px-4 py-2 flex items-center gap-2 hover:bg-gray-50 font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all"
        >
          <i class="ph ph-export"></i> Export CSV
        </button>
        <button 
          @click="openAddModal" 
          class="bg-[#fe3787] text-white px-4 py-2 flex items-center gap-2 hover:bg-[#fb1873] font-semibold poppins text-[14px] rounded-[1px] shadow-sm transition-all"
        >
          <i class="ph ph-plus"></i> Add Student
        </button>
      </div>
    </div>

    <!-- Student Stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div 
        v-for="(stat, label) in statsItems" 
        :key="label" 
        class="bg-white p-4 border border-gray-200 rounded-[1px] shadow-sm"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-semibold text-gray-500 tracking-widest poppins leading-none mb-2">{{ label }}</p>
            <p class="text-2xl font-bold text-[#002D1E] poppins">{{ stat.value }}</p>
          </div>
          <div :class="stat.iconBg" class="w-12 h-12 rounded-full flex items-center justify-center">
            <i :class="[stat.icon, stat.iconColor, 'text-xl']"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm p-4 mb-6">
      <div class="flex flex-col md:flex-row md:items-center gap-4">
        <div class="relative flex-1">
          <i class="ph ph-magnifying-glass absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search by name, student ID, email..." 
            class="pl-10 pr-4 py-2 border border-gray-200 rounded-[1px] w-full outline-none focus:border-[#fe3787] transition-all poppins text-sm"
            @input="debounceSearch"
          />
        </div>
        
        <select 
          v-model="selectedType" 
          class="border border-gray-200 px-3 py-2 rounded-[1px] outline-none focus:border-[#fe3787] transition-all poppins text-sm bg-white min-w-[150px]"
          @change="fetchStudents"
        >
          <option value="">All Genders</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
        </select>

        <button 
          @click="clearFilters" 
          class="bg-gray-100 text-gray-600 px-6 py-2 rounded-[1px] hover:bg-gray-200 font-bold poppins text-sm transition-all"
        >
          Reset
        </button>
      </div>
    </div>

    <!-- Students Table -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Student Profile</th>
            <th class="px-6 py-4 poppins">Contact Details</th>
            <th class="px-6 py-4 poppins text-center">Gender</th>
            <th class="px-6 py-4 poppins">Enrollment Date</th>
            <th class="px-6 py-4 text-right poppins">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="student in paginatedStudents" :key="student.id" class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium">
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                  <i class="ph ph-student text-blue-600 text-xl"></i>
                </div>
                <div>
                  <span class="font-bold text-[#002D1E] block poppins">{{ student.full_name }}</span>
                  <span class="text-[10px] text-gray-400 poppins uppercase tracking-wider">SN #{{ student.student_number }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex items-center gap-2 mb-1">
                <i class="ph ph-envelope text-gray-400"></i>
                <span class="font-bold text-[#002D1E] poppins">{{ student.email || 'N/A' }}</span>
              </div>
              <div class="text-[10px] text-gray-400 poppins uppercase">{{ student.phone_number || 'No Phone' }}</div>
            </td>
            <td class="px-6 py-4 text-center">
              <span :class="genderClass(student.gender)" class="px-3 py-1 rounded-full text-[10px] font-bold uppercase poppins">
                {{ student.gender || 'Unknown' }}
              </span>
            </td>
            <td class="px-6 py-4">
              <div class="font-bold text-[#002D1E] poppins">{{ formatDate(student.date_enrolled) || '—' }}</div>
              <div class="text-[10px] text-gray-400 poppins uppercase text-xs">Joined System</div>
            </td>
            <td class="px-6 py-4 text-right">
              <div class="flex justify-end gap-2">
                <button @click="viewDetails(student)" class="text-blue-600 hover:text-blue-400 p-2 transition-colors">
                  <i class="ph ph-eye text-lg"></i>
                </button>
                <button @click="editStudent(student)" class="text-green-600 hover:text-green-400 p-2 transition-colors">
                  <i class="ph ph-pencil-simple text-lg"></i>
                </button>
                <button @click="deleteStudent(student.id)" class="text-red-600 hover:text-red-400 p-2 transition-colors">
                  <i class="ph ph-trash text-lg"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="students.length === 0 && !loading" class="p-12 text-center poppins">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-50 border border-gray-100 rounded-full flex items-center justify-center">
          <i class="ph ph-users text-2xl text-gray-300"></i>
        </div>
        <h3 class="text-lg font-bold text-[#002D1E] mb-2 poppins">No Students Found</h3>
        <p class="text-sm text-gray-400 poppins">Register new students to manage their academic records.</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="p-12 text-center">
        <i class="ph ph-circle-notch animate-spin text-4xl text-[#fe3787]"></i>
        <p class="mt-4 text-sm font-bold text-gray-400 uppercase tracking-widest poppins">Syncing Database...</p>
      </div>

      <!-- Pagination -->
      <div v-if="filteredStudents.length > itemsPerPage" class="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
        <div class="flex items-center justify-between">
          <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
            Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ filteredStudents.length }}
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

    <!-- Add/Edit Student Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-lg p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">{{ isEditing ? 'Update Student' : 'Register Student' }}</h2>
          <button @click="closeModal" class="text-gray-400 hover:text-black transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="saveStudent" class="space-y-4">
          <!-- Account credentials (only shown when adding) -->
          <template v-if="!isEditing">
            <div class="bg-blue-50 border border-blue-100 rounded-[1px] p-3">
              <p class="text-[10px] font-bold text-blue-600 uppercase tracking-widest poppins">Account Credentials</p>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Username *</label>
                <input v-model="form.username" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required placeholder="e.g. jdoe">
              </div>
              <div>
                <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Password *</label>
                <input v-model="form.password" type="password" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required placeholder="••••••••">
              </div>
            </div>
          </template>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">First Name *</label>
              <input v-model="form.first_name" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Last Name *</label>
              <input v-model="form.last_name" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
            </div>
          </div>

          <div>
            <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Middle Initial (Optional)</label>
            <input v-model="form.mi" type="text" maxlength="1" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" placeholder="M">
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Student Number *</label>
              <input v-model="form.id_number" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required placeholder="2024-XXXX">
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Gender</label>
              <select v-model="form.gender" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px] bg-white">
                <option value="">Select Gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Email Address *</label>
              <input v-model="form.email" type="email" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold uppercase text-gray-400 mb-1 poppins">Phone Number</label>
              <input v-model="form.phone_number" type="text" class="w-full border p-2 text-sm outline-none focus:border-[#fe3787] transition-all rounded-[1px]">
            </div>
          </div>

          <p v-if="formError" class="text-red-500 text-xs poppins font-semibold">{{ formError }}</p>
          
          <div class="flex justify-end gap-3 pt-4 border-t">
            <button type="button" @click="closeModal" class="text-sm text-gray-500 font-medium poppins">Cancel</button>
            <button type="submit" :disabled="saving" class="bg-[#fe3787] text-white px-6 py-2 text-sm font-bold shadow-md hover:bg-[#e6327a] transition-all rounded-[1px] poppins disabled:opacity-60">
              {{ saving ? 'Saving...' : (isEditing ? 'Apply Changes' : 'Register Student') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- View Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 poppins">
      <div class="bg-white w-full max-w-lg p-6 rounded-[1px] shadow-2xl animate-in fade-in zoom-in duration-200">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-[#002D1E] poppins">Full Profile</h2>
          <button @click="showDetailsModal = false" class="text-gray-400 hover:text-black transition-colors">
            <i class="ph ph-x text-xl"></i>
          </button>
        </div>
        
        <div v-if="selectedStudent" class="space-y-6">
          <div class="flex items-center gap-4 border-b pb-4">
            <div class="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
              <i class="ph ph-student text-3xl text-blue-600"></i>
            </div>
            <div>
              <h3 class="text-xl font-bold text-[#002D1E] poppins">{{ selectedStudent.full_name }}</h3>
              <p class="text-xs font-bold text-gray-400 uppercase tracking-widest poppins">ID: STUDENT-{{ selectedStudent.id }}</p>
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-6">
            <div>
              <p class="text-[10px] uppercase font-bold text-gray-400 mb-1 poppins">Gender</p>
              <span :class="genderClass(selectedStudent.gender)" class="px-3 py-1 rounded-full text-[10px] font-bold uppercase poppins">
                {{ selectedStudent.gender || 'Unknown' }}
              </span>
            </div>
            <div>
              <p class="text-[10px] uppercase font-bold text-gray-400 mb-1 poppins">Enrollment Date</p>
              <p class="text-sm font-bold text-[#002D1E] poppins">{{ formatDate(selectedStudent.date_enrolled) || '—' }}</p>
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-6">
            <div>
              <p class="text-[10px] uppercase font-bold text-gray-400 mb-1 poppins">Email Address</p>
              <p class="text-sm font-bold text-[#002D1E] poppins">{{ selectedStudent.email || 'N/A' }}</p>
            </div>
            <div>
              <p class="text-[10px] uppercase font-bold text-gray-400 mb-1 poppins">Phone Number</p>
              <p class="text-sm font-bold text-[#002D1E] poppins">{{ selectedStudent.phone_number || 'N/A' }}</p>
            </div>
          </div>
          
          <div class="bg-gray-50 p-4 border border-gray-100 rounded-[1px]">
            <p class="text-[10px] uppercase font-bold text-gray-400 mb-2 poppins">Activity Summary</p>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <i class="ph ph-ticket text-[#fe3787] text-xl"></i>
                <span class="font-bold text-[#002D1E] poppins">{{ selectedStudent.booking_count }} Total Bookings</span>
              </div>
              <p v-if="selectedStudent.last_booking" class="text-[10px] text-gray-400 poppins">LAST: {{ formatDate(selectedStudent.last_booking) }}</p>
            </div>
          </div>
        </div>
        
        <div class="flex justify-end pt-6">
          <button 
            type="button" 
            @click="showDetailsModal = false" 
            class="bg-gray-100 text-[#002D1E] px-6 py-2 text-sm font-bold rounded-[1px] hover:bg-gray-200 transition-all poppins"
          >
            Close Profile
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

// Reactive state
const students = ref([])
const loading = ref(false)
const showModal = ref(false)
const showDetailsModal = ref(false)
const selectedStudent = ref(null)
const isEditing = ref(false)
const currentId = ref(null)

// Filters and pagination
const searchQuery = ref('')
const selectedType = ref('')
const bookingFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Form data
const form = ref({
  username: '',
  password: '',
  student_number: '',
  id_number: '',
  first_name: '',
  last_name: '',
  mi: '',
  email: '',
  phone_number: '',
  gender: ''
})
const formError = ref('')
const saving = ref(false)

// Stats
const stats = ref({ total: 0, male: 0, female: 0, other: 0 })

const statsItems = computed(() => ({
  'Total Students': { value: stats.value.total, icon: 'ph ph-users-three', iconBg: 'bg-blue-100', iconColor: 'text-blue-600' },
  'Male Students': { value: stats.value.male, icon: 'ph ph-gender-male', iconBg: 'bg-blue-100', iconColor: 'text-blue-600' },
  'Female Students': { value: stats.value.female, icon: 'ph ph-gender-female', iconBg: 'bg-pink-100', iconColor: 'text-pink-600' },
  'Other/Unset': { value: stats.value.other, icon: 'ph ph-user-circle', iconBg: 'bg-gray-100', iconColor: 'text-gray-600' }
}))

// Computed properties
const filteredStudents = computed(() => {
  let filtered = students.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    filtered = filtered.filter(s => 
      s.first_name?.toLowerCase().includes(q) || 
      s.last_name?.toLowerCase().includes(q) || 
      s.student_number?.toLowerCase().includes(q) ||
      s.email?.toLowerCase().includes(q)
    )
  }
  if (selectedType.value) filtered = filtered.filter(s => s.gender === selectedType.value)
  return filtered
})

const totalPages = computed(() => Math.ceil(filteredStudents.value.length / itemsPerPage))
const paginatedStudents = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredStudents.value.slice(start, start + itemsPerPage)
})
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredStudents.value.length))

const visiblePages = computed(() => {
  const pages = []
  const t = totalPages.value; const c = currentPage.value;
  if (t <= 5) for (let i = 1; i <= t; i++) pages.push(i)
  else {
    if (c <= 3) { for (let i = 1; i <= 4; i++) pages.push(i); pages.push('...', t) }
    else if (c >= t - 2) { pages.push(1, '...'); for (let i = t - 3; i <= t; i++) pages.push(i) }
    else pages.push(1, '...', c - 1, c, c + 1, '...', t)
  }
  return pages
})

// Methods
const fetchStudents = async () => {
  loading.value = true
  try {
    const params = {}
    if (selectedType.value) params.gender = selectedType.value
    if (searchQuery.value) params.search = searchQuery.value
    
    const response = await api.get('/students/', { params })
    students.value = (response.data.results || response.data)
    calculateStats()
  } catch (err) { console.error(err) } finally { loading.value = false }
}

const calculateStats = () => {
  const total = students.value.length
  const male = students.value.filter(s => s.gender === 'male').length
  const female = students.value.filter(s => s.gender === 'female').length
  const other = total - (male + female)
  stats.value = { total, male, female, other }
}

const openAddModal = () => {
  isEditing.value = false; currentId.value = null;
  form.value = { username: '', password: '', student_number: '', id_number: '', first_name: '', last_name: '', mi: '', email: '', phone_number: '', gender: '' }
  formError.value = ''
  showModal.value = true
}

const editStudent = (s) => {
  isEditing.value = true; currentId.value = s.id;
  form.value = { username: '', password: '', student_number: s.student_number || '', id_number: s.student_number || '', first_name: s.first_name || '', last_name: s.last_name || '', mi: s.mi || '', email: s.email || '', phone_number: s.phone_number || '', gender: s.gender || '' }
  formError.value = ''
  showModal.value = true
}

const viewDetails = (s) => { selectedStudent.value = s; showDetailsModal.value = true }

const saveStudent = async () => {
  saving.value = true
  formError.value = ''
  try {
    if (isEditing.value) {
      await api.put(`/students/${currentId.value}/`, {
        first_name: form.value.first_name,
        last_name: form.value.last_name,
        mi: form.value.mi,
        student_number: form.value.student_number,
        email: form.value.email,
        phone_number: form.value.phone_number,
        gender: form.value.gender
      })
      alert('Student updated successfully!')
    } else {
      // Use the same registration endpoint as Register.vue
      await api.post('auth/register/', {
        role: 'student',
        username: form.value.username,
        password: form.value.password,
        first_name: form.value.first_name,
        last_name: form.value.last_name,
        mi: form.value.mi,
        id_number: form.value.id_number,
        email: form.value.email,
        gender: form.value.gender
      })
      alert('Student account created successfully!')
    }
    await fetchStudents()
    closeModal()
  } catch (err) {
    console.error('Save error:', err)
    formError.value = err.response?.data?.error || 'Failed to save. Please check the details and try again.'
  } finally {
    saving.value = false
  }
}

const deleteStudent = async (id) => {
  const confirmed = await modalStore.confirm({
    title: 'Purge Personnel Record?',
    message: 'Are you sure you want to permanently delete this student record? This action cannot be undone.',
    variant: 'danger',
    confirmText: 'Delete',
    loadingText: 'Purging...'
  });

  if (confirmed) {
    modalStore.setLoader(true);
    try {
      await api.delete(`/students/${id}/`)
      students.value = students.value.filter(s => s.id !== id);
      calculateStats()
      modalStore.close(true);
    } catch (err) {
      console.error(err);
      modalStore.setLoader(false);
    }
  }
}

const closeModal = () => { showModal.value = false; isEditing.value = false; currentId.value = null; formError.value = ''; saving.value = false }

const exportStudents = async () => {
  try {
    const response = await api.get('/students/export/', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `students_${new Date().toISOString().split('T')[0]}.csv`)
    document.body.appendChild(link)
    link.click(); link.remove()
  } catch (err) { console.error(err) }
}

const genderClass = (gender) => {
  switch(gender?.toLowerCase()) {
    case 'male': return 'bg-blue-100 text-blue-700'
    case 'female': return 'bg-pink-100 text-pink-700'
    default: return 'bg-gray-100 text-gray-500'
  }
}

const bookingClass = (count) => {
  if (count === 0) return 'bg-gray-100 text-gray-400'
  if (count === 1) return 'bg-blue-100 text-blue-700'
  return 'bg-[#fe3787]/10 text-[#fe3787]'
}

const formatDate = (d) => d ? new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : ''
const clearFilters = () => { searchQuery.value = ''; selectedType.value = ''; bookingFilter.value = ''; currentPage.value = 1; fetchStudents() }

let searchTimeout = null
const debounceSearch = () => { clearTimeout(searchTimeout); searchTimeout = setTimeout(() => fetchStudents(), 500) }

const prevPage = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const goToPage = (p) => { if (p !== '...') currentPage.value = p }

watch([searchQuery, selectedType, bookingFilter], () => currentPage.value = 1)
onMounted(fetchStudents)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
.poppins { font-family: 'Poppins', sans-serif; }
</style>
