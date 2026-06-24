<template>
  <div class="p-6 poppins">
    <!-- Header -->
    <div class="mb-6 flex justify-between items-center">
    </div>

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
            <p class="text-2xl font-bold text-[#002D1E] poppins">
              {{ label.includes('Amount') ? '₱' + count.toLocaleString() : count }}
            </p>
          </div>
          <div :class="statIconClass(label)" class="w-12 h-12 rounded-full flex items-center justify-center">
            <i :class="[statIcon(label), 'text-xl']"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Payment ID</th>
            <th class="px-6 py-4 poppins">Booking</th>
            <th class="px-6 py-4 poppins text-right">Amount</th>
            <th class="px-6 py-4 poppins text-center">Method</th>
            <th class="px-6 py-4 poppins">Transaction</th>
            <th class="px-6 py-4 poppins text-center">Status</th>
            <th class="px-6 py-4 poppins text-right">Date</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="payment in paginatedPayments"
            :key="payment.id"
            :id="`payment-row-${payment.id}`"
            :class="[{'highlight-active': highlightedId === payment.id}, 'hover:bg-gray-50/50 transition-colors text-[12px] font-medium']"
          >
            <!-- Payment ID -->
            <td class="px-6 py-4 font-bold text-[#fe3787] poppins">
              #{{ payment.id }}
            </td>

            <!-- Booking -->
            <td class="px-6 py-4">
              <span class="font-bold text-[#002D1E] poppins uppercase">BK-{{ payment.booking }}</span>
            </td>

            <!-- Amount -->
            <td class="px-6 py-4 text-right font-bold text-[#002D1E] poppins">
              ₱{{ parseFloat(payment.amount).toLocaleString() }}
            </td>

            <!-- Method -->
            <td class="px-6 py-4 text-center">
              <span
                class="px-3 py-1 text-[10px] font-bold uppercase rounded-[1px] bg-blue-50 text-blue-600 poppins"
              >
                {{ payment.method }}
              </span>
            </td>

            <!-- Transaction -->
            <td class="px-6 py-4 text-gray-400 poppins italic">
              {{ payment.transaction_id || '—' }}
            </td>

            <!-- Status -->
            <td class="px-6 py-4 text-center">
              <span
                class="px-3 py-1 text-[10px] font-bold uppercase rounded-full poppins"
                :class="statusBadge(payment.status)"
              >
                {{ payment.status }}
              </span>
            </td>

            <!-- Date -->
            <td class="px-6 py-4 text-right text-gray-400 poppins">
              {{ formatDate(payment.payment_date) }}
            </td>
          </tr>

          <tr v-if="payments.length === 0">
            <td colspan="7" class="px-6 py-10 text-center text-gray-400 italic poppins">
              No financial records found.
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div v-if="payments.length > itemsPerPage" class="px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-[12px] text-gray-500 poppins">
            Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ payments.length }} payments
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import { useRoute } from 'vue-router'
import api from "@/services/admin/api"

const route = useRoute()

const payments = ref([])
const highlightedId = ref(null)

// Pagination State
const currentPage = ref(1)
const itemsPerPage = 10

const statsItems = computed(() => {
  const completed = payments.value.filter(p => p.status === 'Completed');
  return {
    'Total Collected Amount': completed.reduce((acc, p) => acc + parseFloat(p.amount), 0),
    'Success Transactions': completed.length,
    'Pending Approvals': payments.value.filter(p => p.status === 'Pending').length,
  };
});

const statIcon = (label) => {
  if (label === 'Total Collected Amount') return 'ph ph-currency-circle-dollar';
  if (label === 'Success Transactions') return 'ph ph-chart-line-up';
  return 'ph ph-hourglass-medium';
};

const statIconClass = (label) => {
  if (label === 'Total Collected Amount') return 'bg-green-100 text-green-600';
  if (label === 'Success Transactions') return 'bg-blue-100 text-blue-600';
  return 'bg-purple-100 text-purple-600';
};

const fetchPayments = async () => {
  try {
    const res = await api.get("/payments/")
    payments.value = res.data.results || res.data

    if (route.query.page) {
        currentPage.value = parseInt(route.query.page);
    }

    if (route.query.highlight) {
        const hId = parseInt(route.query.highlight);
        highlightedId.value = hId;

        // Auto-navigate to the correct page for this ID
        const index = payments.value.findIndex(p => p.id === hId);
        if (index !== -1) {
            currentPage.value = Math.floor(index / itemsPerPage) + 1;
        }

        setTimeout(() => {
            const el = document.getElementById(`payment-row-${hId}`);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => { highlightedId.value = null; }, 3000);
        }, 500);
    }
  } catch (err) {
    console.error("Failed to load payments", err)
  }
}

// Pagination Computed
const totalPages = computed(() => Math.ceil(payments.value.length / itemsPerPage))
const paginatedPayments = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return payments.value.slice(start, start + itemsPerPage)
})
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => Math.min(currentPage.value * itemsPerPage, payments.value.length))

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

const prevPage = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }
const goToPage = (p) => { if (p !== '...') currentPage.value = p }

const formatDate = (date) =>
  new Date(date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })

const statusBadge = (status) => {
  switch (status) {
    case "Completed":
      return "bg-green-100 text-green-700"
    case "Pending":
      return "bg-purple-100 text-purple-700"
    case "Failed":
      return "bg-pink-100 text-pink-700"
    default:
      return "bg-gray-100 text-gray-600"
  }
}

onMounted(fetchPayments)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

.poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
