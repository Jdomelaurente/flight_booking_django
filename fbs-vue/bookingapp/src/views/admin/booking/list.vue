<template>
  <div class="p-6 poppins">
    <!-- Header & Tools Section -->
    <AdminTableTool 
      v-model="searchQuery" 
      placeholder="Search booking ID or user name..."
    >
      <template #filters>
        <div class="flex items-center gap-2">
          <select 
            v-model="filterStatus"
            class="text-[11px] font-bold border border-gray-200 px-3 py-2 bg-white rounded-[1px] outline-none focus:border-[#fe3787] poppins cursor-pointer"
          >
            <option value="all">Any Status</option>
            <option value="confirmed">Confirmed</option>
            <option value="pending">Pending</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </template>
    </AdminTableTool>

    <!-- Stats Section -->
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

    <!-- Table Section -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Booking ID</th>
            <th class="px-6 py-4 poppins">User</th>
            <th class="px-6 py-4 poppins">Trip Type</th>
            <th class="px-6 py-4 poppins text-right">Total Amount</th>
            <th class="px-6 py-4 poppins text-center">Status</th>
            <th class="px-6 py-4 poppins text-right">Created</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="booking in paginatedBookings"
            :key="booking.id"
            :id="`booking-row-${booking.id}`"
            :class="{'highlight-active': highlightedId === booking.id}"
            class="hover:bg-gray-50/50 transition-all text-[12px] font-medium"
          >
            <td class="px-6 py-4">
              <span class="font-bold text-[#fe3787] poppins block">#{{ booking.id }}</span>
              <div class="flex items-center gap-1 mt-1">
                <span class="text-[9px] text-gray-400 font-bold uppercase poppins">Recorded</span>
                <div class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
              </div>
            </td>

            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center">
                  <i class="ph ph-user text-blue-600"></i>
                </div>
                <div class="font-bold text-[#002D1E] poppins">
                  {{ booking.user_name || '—' }}
                </div>
              </div>
            </td>

            <td class="px-6 py-4">
               <span class="bg-gray-100 text-gray-600 px-3 py-1 rounded-[1px] text-[10px] font-bold uppercase poppins tracking-tight">
                 {{ booking.trip_type.replace('_', ' ') }}
               </span>
            </td>

            <td class="px-6 py-4 text-right">
               <span class="font-bold text-[#002D1E] poppins">₱{{ parseFloat(booking.total_amount).toLocaleString() }}</span>
            </td>

            <td class="px-6 py-4 text-center">
              <span
                class="px-3 py-1 text-[10px] font-bold uppercase rounded-full poppins"
                :class="statusBadge(booking.status)"
              >
                {{ booking.status }}
              </span>
            </td>

            <td class="px-6 py-4 text-right text-gray-400 poppins">
              {{ formatDate(booking.created_at) }}
            </td>
          </tr>

          <tr v-if="bookings.length === 0">
            <td colspan="6" class="px-6 py-10 text-center text-gray-400 italic poppins">
              No bookings found.
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination Section -->
      <div v-if="bookings.length > itemsPerPage" class="px-6 py-4 border-t border-gray-100 bg-gray-50/50">
        <div class="flex items-center justify-between">
          <div class="text-[11px] font-bold text-gray-400 uppercase tracking-widest poppins">
            Showing {{ startIndex + 1 }} - {{ endIndex }} of {{ bookings.length }}
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import { useRoute } from "vue-router"
import api from "@/services/admin/api"
import AdminTableTool from '@/components/admin/AdminTableTool.vue';

const bookings = ref([])
const highlightedId = ref(null);
const route = useRoute();
const searchQuery = ref('');
const filterStatus = ref('all');

// Pagination State
const currentPage = ref(1);
const itemsPerPage = 10;

const statsItems = computed(() => {
  return {
    'Total Bookings': bookings.value.length,
    'Confirmed': bookings.value.filter(b => b.status?.toLowerCase() === 'confirmed').length,
    'Pending': bookings.value.filter(b => b.status?.toLowerCase() === 'pending').length,
    'Cancelled': bookings.value.filter(b => b.status?.toLowerCase() === 'cancelled').length,
  };
});

// Search & Filter Logic
const filteredBookings = computed(() => {
  let result = bookings.value;
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(b => 
      String(b.id).includes(q) || 
      (b.user_name && b.user_name.toLowerCase().includes(q))
    );
  }

  if (filterStatus.value !== 'all') {
    result = result.filter(b => b.status?.toLowerCase() === filterStatus.value.toLowerCase());
  }
  
  return result;
});

// Pagination Logic
const totalPages = computed(() => Math.ceil(filteredBookings.value.length / itemsPerPage));
const paginatedBookings = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return filteredBookings.value.slice(start, start + itemsPerPage);
});
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage);
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, filteredBookings.value.length));

const visiblePages = computed(() => {
  const pages = [];
  const t = totalPages.value;
  const c = currentPage.value;
  if (t <= 5) {
    for (let i = 1; i <= t; i++) pages.push(i);
  } else {
    if (c <= 3) {
      for (let i = 1; i <= 4; i++) pages.push(i);
      pages.push('...', t);
    } else if (c >= t - 2) {
      pages.push(1, '...');
      for (let i = t - 3; i <= t; i++) pages.push(i);
    } else {
      pages.push(1, '...', c - 1, c, c + 1, '...', t);
    }
  }
  return pages;
});

const statIcon = (label) => {
  if (label === 'Total Bookings') return 'ph ph-notebook';
  if (label === 'Confirmed') return 'ph ph-check-circle';
  if (label === 'Pending') return 'ph ph-clock';
  return 'ph ph-x-circle';
};

const statIconClass = (label) => {
  if (label === 'Total Bookings') return 'bg-blue-100 text-blue-600';
  if (label === 'Confirmed') return 'bg-green-100 text-green-600';
  if (label === 'Pending') return 'bg-purple-100 text-purple-600';
  return 'bg-pink-100 text-pink-600';
};

const fetchBookings = async () => {
  try {
    const res = await api.get("/bookings/")
    bookings.value = res.data.results || res.data

    if (route.query.page) {
        currentPage.value = parseInt(route.query.page);
    }

    if (route.query.highlight) {
        const hId = parseInt(route.query.highlight);
        highlightedId.value = hId;

        // Auto-navigate to the correct page for this ID
        const index = bookings.value.findIndex(b => b.id === hId);
        if (index !== -1) {
            currentPage.value = Math.floor(index / itemsPerPage) + 1;
        }

        setTimeout(() => {
            const el = document.getElementById(`booking-row-${hId}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => { highlightedId.value = null; }, 3000);
        }, 500);
    }
  } catch (err) {
    console.error("Fetch failed", err);
  }
}

const formatDate = (date) =>
  new Date(date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })

const statusBadge = (status) => {
  if (!status) return "bg-gray-100 text-gray-600";
  switch (status.toLowerCase()) {
    case "pending":
      return "bg-purple-100 text-purple-700"
    case "confirmed":
      return "bg-green-100 text-green-700"
    case "cancelled":
      return "bg-pink-100 text-pink-700"
    default:
      return "bg-gray-100 text-gray-600"
  }
}

const prevPage = () => { if (currentPage.value > 1) currentPage.value--; };
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++; };
const goToPage = (p) => { if (p !== '...') currentPage.value = p; };

onMounted(fetchBookings)
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

.poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
