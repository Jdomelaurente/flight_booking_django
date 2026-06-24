<template>
  <div class="p-6 poppins">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
    </div>

    <!-- Table -->
    <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden">
      <table class="w-full text-left">
        <thead class="bg-gray-50 text-gray-600 text-[14px] uppercase font-semibold border-b border-gray-200">
          <tr>
            <th class="px-6 py-4 poppins">Passenger</th>
            <th class="px-6 py-4 poppins">Flight / Airline</th>
            <th class="px-6 py-4 poppins text-center">Seat</th>
            <th class="px-6 py-4 poppins">Class</th>
            <th class="px-6 py-4 poppins text-right">Price</th>
            <th class="px-6 py-4 poppins text-center">Status</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="detail in bookingDetails"
            :key="detail.id"
            class="hover:bg-gray-50/50 transition-colors text-[12px] font-medium"
          >
            <!-- Passenger -->
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-pink-100 flex items-center justify-center">
                  <i class="ph ph-user-circle text-pink-600"></i>
                </div>
                <div>
                  <div class="font-bold text-[#002D1E] poppins">
                    {{ detail.passenger_name }}
                  </div>
                  <div class="text-[10px] text-gray-400 poppins uppercase">
                    {{ detail.passenger_type }}
                  </div>
                </div>
              </div>
            </td>

            <!-- Flight -->
            <td class="px-6 py-4">
              <div class="font-bold text-[#002D1E] poppins uppercase">{{ detail.flight_number }}</div>
              <div class="text-[10px] text-gray-400 poppins">
                {{ detail.airline_name }} • {{ detail.route_display }}
              </div>
            </td>

            <!-- Seat -->
            <td class="px-6 py-4 text-center">
              <span
                v-if="detail.seat_number"
                class="px-3 py-1 text-[10px] font-bold rounded-[1px] bg-blue-100 text-blue-700 poppins"
              >
                {{ detail.seat_number }}
              </span>
              <span v-else class="text-gray-400 italic poppins">
                —
              </span>
            </td>

            <!-- Class -->
            <td class="px-6 py-4">
               <span class="bg-gray-100 text-gray-600 px-3 py-1 rounded-[1px] text-[10px] font-bold uppercase poppins tracking-tight">
                 {{ detail.seat_class_name || 'Standard' }}
               </span>
            </td>

            <!-- Price -->
            <td class="px-6 py-4 text-right font-bold text-[#002D1E] poppins">
              ₱{{ parseFloat(detail.price).toLocaleString() }}
            </td>

            <!-- Status -->
            <td class="px-6 py-4 text-center">
              <span
                :class="statusBadge(detail.status)"
                class="px-3 py-1 text-[10px] font-bold uppercase rounded-full poppins"
              >
                {{ detail.status }}
              </span>
            </td>
          </tr>

          <tr v-if="bookingDetails.length === 0">
            <td colspan="6" class="px-6 py-10 text-center text-gray-400 italic poppins">
              No manifest data found.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import api from "@/services/admin/api"

const bookingDetails = ref([])

const fetchBookingDetails = async () => {
  try {
    const res = await api.get("/booking-details/")
    bookingDetails.value = res.data.results || res.data
  } catch (err) {
    console.error("Failed to load booking details", err)
  }
}

const statusBadge = (status) => {
  const s = status?.toLowerCase();
  switch (s) {
    case "pending":
      return "bg-purple-100 text-purple-700"
    case "confirmed":
      return "bg-green-100 text-green-700"
    case "checkin":
    case "check-in":
      return "bg-blue-100 text-blue-700"
    case "boarding":
      return "bg-pink-100 text-pink-700"
    case "completed":
      return "bg-gray-200 text-gray-700"
    case "cancelled":
      return "bg-red-100 text-red-700"
    default:
      return "bg-gray-100 text-gray-500"
  }
}

onMounted(fetchBookingDetails)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

.poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
