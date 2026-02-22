<template>
  <div class="p-6 space-y-6 bg-gray-100 min-h-screen">
    <!-- Loading Overlay -->
    <div v-if="loading" class="fixed inset-0 bg-white/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <div class="flex flex-col items-center">
        <div class="w-12 h-12 border-4 border-[#fe3787] border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-4 text-gray-600 poppins">Loading dashboard...</p>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
      <strong class="font-bold">Error!</strong>
      <span class="block sm:inline">{{ error }}</span>
    </div>

    <!-- Glassmorphism Welcome Header -->
    <div class="relative overflow-hidden p-8 rounded-[1px] border border-white/20 shadow-2xl bg-gradient-to-br from-[#002D1E] to-[#013d29] mb-8 group">
      <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
      <div class="absolute -right-20 -top-20 w-64 h-64 bg-[#fe3787] rounded-full blur-[100px] opacity-20 group-hover:opacity-30 transition-opacity"></div>
      
      <div class="relative flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/10 mb-4">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span class="text-[10px] font-bold text-white uppercase tracking-[0.2em] poppins">System Live</span>
          </div>
          <h1 class="text-4xl font-black text-white poppins tracking-tight mb-2">
            {{ greeting }}, <span class="text-[#fe3787] drop-shadow-sm font-black italic">Admin</span>
          </h1>
          <p class="text-gray-300 poppins text-sm max-w-md">Welcome to your command center. Everything looks optimized for today's operations.</p>
        </div>
        
        <div class="flex items-center gap-4 bg-black/20 backdrop-blur-xl p-4 rounded-[1px] border border-white/10 shadow-inner">
          <div class="w-12 h-12 rounded-[1px] bg-[#fe3787] flex items-center justify-center shadow-lg">
            <i class="ph ph-calendar-check text-white text-2xl"></i>
          </div>
          <div>
            <p class="text-[10px] uppercase font-bold text-gray-400 tracking-widest poppins mb-1">Session Data</p>
            <p class="text-lg font-black text-white poppins leading-none">{{ currentDate }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Cards - Refined -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <!-- Passengers Card -->
      <div class="group bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-xl transition-all hover:-translate-y-1 duration-300 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-24 h-24 bg-blue-50/50 rounded-full -mr-12 -mt-12 transition-transform group-hover:scale-110"></div>
        <div class="relative flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-bold text-gray-500 tracking-[0.2em] poppins">Daily Traffic</p>
            <p class="text-4xl font-black text-[#002D1E] poppins mt-2 tracking-tighter">{{ stats.passengersToday }}</p>
          </div>
          <div class="w-14 h-14 rounded-[1px] bg-blue-50 flex items-center justify-center border border-blue-100 shadow-inner">
            <i class="ph ph-users-three text-blue-600 text-3xl transition-transform group-hover:rotate-12"></i>
          </div>
        </div>
        <div class="mt-6 flex items-center text-xs poppins">
          <div :class="stats.passengerGrowth >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'" class="flex items-center gap-1 px-2 py-1 rounded-full font-bold">
            <i class="ph" :class="stats.passengerGrowth >= 0 ? 'ph-trend-up' : 'ph-trend-down'"></i>
            {{ stats.passengerGrowth >= 0 ? '+' : '' }}{{ stats.passengerGrowth }}%
          </div>
          <span class="text-gray-400 ml-2 font-medium">vs yesterday</span>
        </div>
      </div>

      <!-- Revenue Card -->
      <div class="group bg-[#002D1E] p-6 border border-[#002D1E] rounded-[1px] shadow-sm hover:shadow-2xl transition-all hover:-translate-y-1 duration-300 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-24 h-24 bg-[#fe3787]/10 rounded-full -mr-12 -mt-12 transition-transform group-hover:scale-110"></div>
        <div class="relative flex items-center justify-between text-white">
          <div>
            <p class="text-[10px] uppercase font-bold text-gray-400 tracking-[0.2em] poppins">Total Revenue</p>
            <p class="text-4xl font-black text-[#fe3787] poppins mt-2 tracking-tighter">₱{{ formatNumber(stats.totalRevenue) }}</p>
          </div>
          <div class="w-14 h-14 rounded-[1px] bg-white/5 flex items-center justify-center border border-white/10 shadow-inner backdrop-blur-sm">
            <i class="ph ph-hand-coins text-[#fe3787] text-3xl transition-transform group-hover:rotate-12"></i>
          </div>
        </div>
        <div class="mt-6 flex items-center text-xs poppins">
          <div :class="stats.revenueGrowth >= 0 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'" class="flex items-center gap-1 px-2 py-1 rounded-full font-bold border border-white/10">
            <i class="ph" :class="stats.revenueGrowth >= 0 ? 'ph-trend-up' : 'ph-trend-down'"></i>
            {{ stats.revenueGrowth >= 0 ? '+' : '' }}{{ stats.revenueGrowth }}%
          </div>
          <span class="text-gray-400 ml-2 font-medium">vs last month</span>
        </div>
      </div>

      <!-- Bookings Card -->
      <div class="group bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-xl transition-all hover:-translate-y-1 duration-300 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-24 h-24 bg-green-50/50 rounded-full -mr-12 -mt-12 transition-transform group-hover:scale-110"></div>
        <div class="relative flex items-center justify-between text-[#002D1E]">
          <div>
            <p class="text-[10px] uppercase font-bold text-gray-500 tracking-[0.2em] poppins">Reservations</p>
            <p class="text-4xl font-black poppins mt-2 tracking-tighter">{{ stats.totalBookings }}</p>
          </div>
          <div class="w-14 h-14 rounded-[1px] bg-green-50 flex items-center justify-center border border-green-100 shadow-inner">
            <i class="ph ph-ticket text-green-600 text-3xl transition-transform group-hover:rotate-12"></i>
          </div>
        </div>
        <div class="mt-6 flex items-center text-xs poppins font-bold">
          <div v-if="loading" class="h-6 w-12 bg-gray-100 animate-pulse rounded-full"></div>
          <span v-else class="text-[#fe3787] bg-pink-50 px-2 py-1 rounded-full border border-pink-100">{{ stats.pendingBookings }}</span>
          <span class="text-gray-400 ml-2 font-medium uppercase tracking-wider text-[9px]">Awaiting Confirmation</span>
        </div>
      </div>

      <!-- Flights Card -->
      <div class="group bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-xl transition-all hover:-translate-y-1 duration-300 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-24 h-24 bg-purple-50/50 rounded-full -mr-12 -mt-12 transition-transform group-hover:scale-110"></div>
        <div class="relative flex items-center justify-between text-[#002D1E]">
          <div>
            <p class="text-[10px] uppercase font-bold text-gray-500 tracking-[0.2em] poppins">Active Ops</p>
            <p class="text-4xl font-black poppins mt-2 tracking-tighter">{{ stats.activeFlights }}</p>
          </div>
          <div class="w-14 h-14 rounded-[1px] bg-purple-50 flex items-center justify-center border border-purple-100 shadow-inner">
            <i class="ph ph-airplane text-purple-600 text-3xl transition-transform group-hover:rotate-12"></i>
          </div>
        </div>
        <div class="mt-6 flex items-center text-xs poppins font-bold">
          <div v-if="loading" class="h-6 w-12 bg-gray-100 animate-pulse rounded-full"></div>
          <span v-else class="text-purple-600 bg-purple-50 px-2 py-1 rounded-full border border-purple-100">{{ stats.scheduledFlights }}</span>
          <span class="text-gray-400 ml-2 font-medium uppercase tracking-wider text-[9px]">Schedules Today</span>
        </div>
      </div>
    </div>

    <!-- Active Flight Map (NEW) -->
    <div ref="mapCardRef" class="bg-white border border-gray-200 rounded-[1px] shadow-sm mb-8 overflow-hidden group relative" :class="{'h-screen w-screen !m-0 !fixed inset-0 z-[100]': isMapFullScreen}">
      <div class="absolute top-0 left-0 w-1 h-full bg-[#002D1E] opacity-0 group-hover:opacity-100 transition-opacity"></div>
      <div class="p-6 border-b border-gray-100 flex items-center justify-between">
        <div>
          <h3 class="text-lg font-black text-[#002D1E] poppins tracking-tight flex items-center gap-2">
            <i class="ph ph-map-pin-line text-[#fe3787]"></i>
            Live Global Operations
          </h3>
          <p class="text-[10px] text-gray-400 poppins uppercase tracking-wider font-bold">Real-time aircraft tracking & telemetry</p>
        </div>
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2 text-[10px] font-bold poppins text-gray-400">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            {{ activeFlights.length }} Flights Active
          </div>
          <button @click="fetchActiveFlights" class="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-400 hover:text-[#fe3787]" title="Refresh Map">
            <i class="ph ph-arrows-clockwise text-lg" :class="{'animate-spin': mapLoading}"></i>
          </button>
          <button @click="toggleFullScreen" class="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-400 hover:text-[#fe3787]" :title="isMapFullScreen ? 'Exit Full Screen' : 'Full Screen'">
            <i class="ph text-lg" :class="isMapFullScreen ? 'ph-corners-in' : 'ph-corners-out'"></i>
          </button>
        </div>
      </div>
      <div :class="isMapFullScreen ? 'h-[calc(100vh-80px)]' : 'h-[400px]'" class="relative transition-all duration-300">
        <div ref="mapContainer" class="absolute inset-0 z-0"></div>
        
        <!-- Map Overlay Stats -->
        <div class="absolute bottom-6 left-6 z-[400] flex flex-col gap-2">
          <div class="bg-black/80 backdrop-blur-md border border-white/10 p-4 rounded-[1px] shadow-2xl">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-8 h-8 rounded-[1px] bg-[#fe3787] flex items-center justify-center">
                <i class="ph ph-airplane-tilt text-white"></i>
              </div>
              <div>
                <p class="text-[8px] text-gray-400 uppercase font-bold tracking-widest leading-none">Global Coverage</p>
                <p class="text-xs text-white font-black poppins">Active Airspace</p>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-[10px] text-emerald-400 font-black">98.4%</p>
                <p class="text-[7px] text-gray-500 uppercase font-bold tracking-tighter">On-Time Perf</p>
              </div>
              <div>
                <p class="text-[10px] text-[#fe3787] font-black">12</p>
                <p class="text-[7px] text-gray-500 uppercase font-bold tracking-tighter">Planned (1h)</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Main Sales Chart -->
      <div class="lg:col-span-8 bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm relative overflow-hidden group">
        <div class="absolute top-0 left-0 w-1 h-full bg-[#fe3787] opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="flex items-center justify-between mb-8">
          <div>
            <h3 class="text-lg font-black text-[#002D1E] poppins tracking-tight">Revenue Stream</h3>
            <p class="text-xs text-gray-400 poppins uppercase tracking-wider font-bold">Ticket sales performance</p>
          </div>
          <div class="flex items-center gap-2">
            <select 
              v-model="chartPeriod" 
              @change="fetchTicketSales"
              class="bg-gray-50 border border-gray-200 rounded-[1px] px-4 py-2 text-xs font-bold uppercase tracking-widest poppins focus:outline-none focus:ring-2 focus:ring-[#fe3787] cursor-pointer"
            >
              <option value="1">Today</option>
              <option value="7">Week</option>
              <option value="30">Month</option>
              <option value="365">Year</option>
            </select>
          </div>
        </div>
        <div class="h-[340px] relative">
          <canvas ref="ticketChartRef"></canvas>
          <div v-if="!hasTicketData && !loading" class="absolute inset-0 flex flex-col items-center justify-center bg-white/90 backdrop-blur-sm">
             <div class="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
                <i class="ph ph-chart-line-up text-3xl text-gray-200"></i>
             </div>
             <p class="text-gray-400 text-xs font-bold uppercase tracking-[0.2em]">Gathering data...</p>
          </div>
        </div>
      </div>

      <!-- Composition Charts Column -->
      <div class="lg:col-span-4 space-y-6">
        <!-- Revenue Distribution -->
        <div class="bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm relative group overflow-hidden">
          <div class="absolute top-0 right-0 w-32 h-32 bg-purple-50 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-110"></div>
          <h3 class="text-sm font-black text-[#002D1E] poppins uppercase tracking-widest mb-6 relative">Budget Allocation</h3>
          <div class="h-48 relative">
            <canvas ref="revenueChartRef"></canvas>
          </div>
          <div class="mt-6 space-y-2 relative">
            <div v-for="(item, index) in revenueBreakdown" :key="index" class="flex items-center justify-between text-[11px] font-bold uppercase poppins">
              <span class="text-gray-400">{{ item.label }}</span>
              <span class="text-[#002D1E]">₱{{ formatNumber(item.value) }}</span>
            </div>
          </div>
        </div>

        <!-- Passenger Mix (NEW) -->
        <div class="bg-[#fe3787] p-6 rounded-[1px] shadow-lg relative group overflow-hidden">
           <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/brushed-alum.png')] opacity-10"></div>
           <h3 class="text-sm font-black text-white poppins uppercase tracking-widest mb-6 relative">Crowd Profile</h3>
           <div class="h-40 relative">
             <canvas ref="compositionChartRef"></canvas>
           </div>
           <div class="mt-4 flex justify-between gap-2 relative">
              <div v-for="(val, idx) in compositionData.data" :key="idx" class="flex flex-col items-center">
                 <span class="text-[14px] font-black text-white poppins">{{ val }}</span>
                 <span class="text-[8px] text-white/60 font-black uppercase tracking-widest poppins">{{ compositionData.labels[idx] }}</span>
              </div>
           </div>
        </div>
      </div>
    </div>

    <!-- Second Row: Routes & Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
       <!-- Popular Routes (NEW) -->
       <div class="lg:col-span-4 bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm">
          <div class="flex items-center justify-between mb-8">
             <h3 class="text-sm font-black text-[#002D1E] poppins uppercase tracking-widest">High Traffic Routes</h3>
             <i class="ph ph-map-trifold text-[#fe3787] text-xl"></i>
          </div>
          <div class="h-[300px]">
             <canvas ref="routesChartRef"></canvas>
          </div>
       </div>

       <!-- Recent Ledger -->
       <div class="lg:col-span-8 bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden flex flex-col">
         <div class="p-6 border-b border-gray-200 flex items-center justify-between">
           <h3 class="text-lg font-black text-[#002D1E] poppins flex items-center gap-2">
             <i class="ph ph-clock-counter-clockwise text-[#fe3787]"></i>
             Recent Activity
           </h3>
           <router-link to="/admin/booking/list" class="text-[#fe3787] hover:bg-pink-50 px-3 py-1 rounded-[1px] text-xs font-black uppercase tracking-widest poppins flex items-center gap-2 transition-all border border-transparent hover:border-pink-100">
             View Ledger <i class="ph ph-arrow-right"></i>
           </router-link>
         </div>
         
         <div class="overflow-x-auto flex-grow">
           <table class="w-full text-left" v-if="recentBookings.length > 0">
             <thead class="bg-gray-50 text-gray-600 text-[10px] uppercase font-bold tracking-[0.1em]">
               <tr>
                 <th class="px-6 py-4 poppins">Ref #</th>
                 <th class="px-6 py-4 poppins">Passenger</th>
                 <th class="px-6 py-4 poppins">Flight</th>
                 <th class="px-6 py-4 poppins">Status</th>
               </tr>
             </thead>
             <tbody class="divide-y divide-gray-100">
               <tr v-for="booking in recentBookings" :key="booking.id" class="hover:bg-gray-50/50 transition-colors group/row">
                 <td class="px-6 py-4">
                   <span class="font-mono text-xs font-bold text-[#fe3787]">#{{ booking.id }}</span>
                 </td>
                 <td class="px-6 py-4">
                   <span class="font-bold text-[#002D1E] poppins text-xs">{{ booking.passenger }}</span>
                 </td>
                 <td class="px-6 py-4">
                   <span class="text-xs text-gray-400 poppins font-mono">{{ booking.flight }}</span>
                 </td>
                 <td class="px-6 py-4">
                   <span :class="statusClass(booking.status)" class="px-2 py-0.5 rounded-[1px] text-[9px] font-black uppercase poppins border">
                     {{ booking.status }}
                   </span>
                 </td>
               </tr>
             </tbody>
           </table>
           <div v-else class="h-64 flex flex-col items-center justify-center text-gray-300">
              <i class="ph ph-scroll text-4xl mb-2"></i>
              <p class="text-[10px] uppercase font-black tracking-[0.2em] poppins">No activity found</p>
           </div>
         </div>
       </div>
    </div>
    <!-- Seat Class Distribution (NEW) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Doughnut Chart -->
      <div class="lg:col-span-5 bg-white border border-gray-200 rounded-[1px] shadow-sm p-6 group relative overflow-hidden">
        <div class="absolute top-0 left-0 w-1 h-full bg-[#fe3787] opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="flex items-center justify-between mb-6">
          <div>
            <h3 class="text-sm font-black text-[#002D1E] poppins uppercase tracking-widest flex items-center gap-2">
              <i class="ph ph-chart-donut text-[#fe3787]"></i>
              Seat Class Distribution
            </h3>
            <p class="text-[10px] text-gray-400 poppins mt-0.5">Bookings by cabin class</p>
          </div>
          <span class="text-[10px] bg-gray-50 border border-gray-100 px-2 py-1 rounded-[1px] poppins font-bold text-gray-400 uppercase tracking-widest">
            {{ seatclassDist.total }} total
          </span>
        </div>

        <div class="flex items-center justify-center">
          <div v-if="seatclassLoading" class="flex flex-col items-center justify-center h-48 gap-2 text-gray-200">
            <i class="ph ph-spinner-gap text-4xl animate-spin"></i>
            <p class="text-[10px] uppercase font-black tracking-widest poppins">Loading...</p>
          </div>
          <div v-else-if="seatclassDist.classes.length === 0" class="flex flex-col items-center justify-center h-48 gap-2 text-gray-200">
            <i class="ph ph-chart-donut text-4xl"></i>
            <p class="text-[10px] uppercase font-black tracking-widest poppins">No data available</p>
          </div>
          <div v-else class="relative h-52 w-52">
            <canvas ref="seatClassChartRef"></canvas>
            <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span class="text-2xl font-black text-[#002D1E] poppins">{{ seatclassDist.total }}</span>
              <span class="text-[8px] font-bold text-gray-400 uppercase tracking-widest poppins">Bookings</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Legend + Stats -->
      <div class="lg:col-span-7 bg-white border border-gray-200 rounded-[1px] shadow-sm p-6">
        <h3 class="text-sm font-black text-[#002D1E] poppins uppercase tracking-widest mb-6">Class Breakdown</h3>
        <div v-if="seatclassDist.classes.length === 0" class="flex flex-col items-center justify-center h-48 gap-2 text-gray-200">
          <i class="ph ph-list-dashes text-4xl"></i>
          <p class="text-[10px] uppercase font-black tracking-widest poppins">No bookings yet</p>
        </div>
        <div v-else class="space-y-4">
          <div v-for="cls in seatclassDist.classes" :key="cls.label" class="group/row">
            <div class="flex items-center justify-between mb-1">
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ background: cls.color }"></span>
                <span class="text-xs font-bold text-[#002D1E] poppins">{{ cls.label }}</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-[10px] text-gray-400 poppins font-bold">{{ cls.count }} pax</span>
                <span class="text-[10px] font-black poppins" :style="{ color: cls.color }">{{ cls.percentage }}%</span>
              </div>
            </div>
            <!-- Progress bar -->
            <div class="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-700"
                :style="{ width: cls.percentage + '%', background: cls.color }"
              ></div>
            </div>
            <div class="mt-1 text-[9px] text-gray-400 poppins font-medium">
              Revenue: <span class="font-black text-gray-600">₱{{ formatNumber(cls.revenue) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
       <!-- Action Cards (Combined from original quick actions) -->
       <div v-for="action in quickActions" :key="action.label" class="bg-white p-6 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-md transition-all group">
          <div class="flex items-start justify-between">
             <div :class="action.colorClass" class="w-12 h-12 rounded-[1px] flex items-center justify-center text-xl shadow-inner">
                <i :class="action.icon"></i>
             </div>
             <router-link :to="action.link" class="text-[#fe3787] opacity-0 group-hover:opacity-100 transition-opacity">
                <i class="ph ph-arrow-square-out text-xl"></i>
             </router-link>
          </div>
          <h4 class="mt-6 text-sm font-black text-[#002D1E] poppins uppercase tracking-wider">{{ action.label }}</h4>
          <p class="text-[10px] text-gray-400 poppins font-medium mt-1">{{ action.description }}</p>
       </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, onUnmounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import api from '@/services/admin/api'

Chart.register(...registerables)

// State
const loading = ref(false)
const error = ref(null)
const chartPeriod = ref('7')
const ticketChartRef = ref(null)
const revenueChartRef = ref(null)
const compositionChartRef = ref(null)
const routesChartRef = ref(null)
const seatClassChartRef = ref(null)
const mapContainer = ref(null)
const mapCardRef = ref(null)
const mapLoading = ref(false)
const isMapFullScreen = ref(false)
const seatclassLoading = ref(false)
const activeFlights = ref([])
const seatclassDist = ref({ total: 0, classes: [] })

// Stats
const stats = ref({
  passengersToday: 0,
  passengerGrowth: 0,
  totalRevenue: 0,
  revenueGrowth: 0,
  totalBookings: 0,
  pendingBookings: 0,
  activeFlights: 0,
  scheduledFlights: 0
})

const recentBookings = ref([])
const alerts = ref([])
const ticketSalesData = ref({
  labels: [],
  data: []
})

const revenueBreakdown = ref([
  { label: 'Airfare', value: 0, color: '#fe3787' },
  { label: 'Add-ons', value: 0, color: '#002D1E' },
  { label: 'Taxes', value: 0, color: '#3b82f6' }
])

const compositionData = ref({
  labels: [],
  data: []
})

const routesData = ref({
  labels: [],
  data: []
})

// Chart instances
let ticketChartInstance = null
let revenueChartInstance = null
let compositionChartInstance = null
let routesChartInstance = null
let seatClassChartInstance = null
let mapInstance = null
let flightMarkers = []
let flightPolylines = []
let animationInterval = null
let mapRefreshInterval = null

// Computed
const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-PH', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good Morning'
  if (hour < 18) return 'Good Afternoon'
  return 'Good Evening'
})

const revenueTotal = computed(() => {
  return revenueBreakdown.value.reduce((sum, item) => sum + item.value, 0)
})

const hasTicketData = computed(() => {
  return ticketSalesData.value.data.some(val => val > 0)
})

// Methods
const fetchDashboardData = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Fetch all dashboard data in parallel with proper error handling
    const responses = await Promise.allSettled([
      api.get('/dashboard/stats/').catch(err => ({ error: err, data: null })),
      api.get('/dashboard/revenue_breakdown/').catch(err => ({ error: err, data: null })),
      api.get('/dashboard/recent_bookings/').catch(err => ({ error: err, data: null })),
      api.get('/dashboard/alerts/').catch(err => ({ error: err, data: null })),
      api.get(`/dashboard/ticket_sales/?days=${chartPeriod.value}`).catch(err => ({ error: err, data: null }))
    ])

    // Handle stats response
    const statsRes = responses[0]
    if (statsRes.value && !statsRes.value.error && statsRes.value.data) {
      const data = statsRes.value.data
      stats.value = {
        passengersToday: data.passengersToday || 0,
        passengerGrowth: data.passengerGrowth || 0,
        totalRevenue: data.totalRevenue || 0,
        revenueGrowth: data.revenueGrowth || 0,
        totalBookings: data.totalBookings || 0,
        pendingBookings: data.pendingBookings || 0,
        activeFlights: data.activeFlights || 0,
        scheduledFlights: data.scheduledFlights || 0
      }
    } else if (statsRes.value?.error) {
      console.error('Stats API error:', statsRes.value.error)
    }

    // Handle revenue breakdown
    const revenueRes = responses[1]
    if (revenueRes.value && !revenueRes.value.error && revenueRes.value.data?.breakdown) {
      const breakdown = revenueRes.value.data.breakdown
      revenueBreakdown.value = [
        { label: 'Airfare', value: breakdown.tickets || 0, color: '#fe3787' },
        { label: 'Add-ons', value: breakdown.addons || 0, color: '#002D1E' },
        { label: 'Taxes', value: breakdown.taxes || 0, color: '#3b82f6' }
      ]
    }

    // Handle recent bookings
    const bookingsRes = responses[2]
    if (bookingsRes.value && !bookingsRes.value.error) {
      recentBookings.value = bookingsRes.value.data || []
    }

    // Handle alerts
    const alertsRes = responses[3]
    if (alertsRes.value && !alertsRes.value.error) {
      alerts.value = alertsRes.value.data || []
    }

    // Handle ticket sales
    const ticketSalesRes = responses[4]
    if (ticketSalesRes.value && !ticketSalesRes.value.error && ticketSalesRes.value.data) {
      ticketSalesData.value = {
        labels: ticketSalesRes.value.data.labels || [],
        data: ticketSalesRes.value.data.data || []
      }
    }

    // Fetch Extra Data in background
    fetchExtraStats()
    fetchActiveFlights()
    fetchSeatClassDistribution()

    // Wait for DOM to update then initialize charts
    await nextTick()
    initCharts()
    
  } catch (err) {
    console.error('Dashboard fetch error:', err)
    error.value = 'Failed to load dashboard data. Please try again.'
  } finally {
    loading.value = false
  }
}

const fetchTicketSales = async () => {
  try {
    const res = await api.get(`/dashboard/ticket_sales/?days=${chartPeriod.value}`)
    if (res.data) {
      ticketSalesData.value = {
        labels: res.data.labels || [],
        data: res.data.data || []
      }
      await nextTick()
      updateTicketChart()
    }
  } catch (err) {
    console.error('Ticket sales fetch error:', err)
  }
}

const fetchExtraStats = async () => {
    try {
        const [compositionRes, routesRes] = await Promise.all([
            api.get('/dashboard/passenger_composition/'),
            api.get('/dashboard/popular_routes/')
        ])
        
        if (compositionRes.data) compositionData.value = compositionRes.data
        if (routesRes.data) routesData.value = routesRes.data
        
        nextTick(() => {
            initCompositionChart()
            initRoutesChart()
        })
    } catch (err) {
        console.error('Extra stats error:', err)
    }
}

const initCharts = () => {
  // Delay slightly to ensure canvas elements are rendered
  setTimeout(() => {
    initTicketChart()
    initRevenueChart()
  }, 100)
}

const initTicketChart = () => {
  if (!ticketChartRef.value) {
    console.warn('Ticket chart canvas not found')
    return
  }
  
  if (ticketChartInstance) {
    ticketChartInstance.destroy()
    ticketChartInstance = null
  }

  const ctx = ticketChartRef.value.getContext('2d')
  if (!ctx) {
    console.warn('Could not get 2d context for ticket chart')
    return
  }

  const gradient = ctx.createLinearGradient(0, 0, 0, 400)
  gradient.addColorStop(0, 'rgba(254, 55, 135, 0.2)')
  gradient.addColorStop(1, 'rgba(254, 55, 135, 0)')

  const labels = ticketSalesData.value.labels.length > 0 ? ticketSalesData.value.labels : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const data = ticketSalesData.value.data.length > 0 ? ticketSalesData.value.data : [0, 0, 0, 0, 0, 0, 0]

  ticketChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Tickets Sold',
        data: data,
        borderColor: '#fe3787',
        borderWidth: 3,
        backgroundColor: gradient,
        tension: 0.45,
        fill: true,
        pointBackgroundColor: '#fe3787',
        pointBorderColor: '#fff',
        pointBorderWidth: 3,
        pointRadius: 0,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: '#fe3787',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        intersect: false,
        mode: 'index'
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#002D1E',
          titleColor: '#fff',
          bodyColor: '#fff',
          padding: 12,
          cornerRadius: 4,
          displayColors: false,
          callbacks: {
            label: function(context) {
              return ` ${context.parsed.y} Tickets`
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: '#f3f4f6' },
          ticks: {
            stepSize: 1,
            color: '#6b7280'
          }
        },
        x: {
          grid: { display: false },
          ticks: {
            color: '#6b7280'
          }
        }
      }
    }
  })
}

const updateTicketChart = () => {
  if (!ticketChartInstance) {
    initTicketChart()
    return
  }
  
  ticketChartInstance.data.labels = ticketSalesData.value.labels
  ticketChartInstance.data.datasets[0].data = ticketSalesData.value.data
  ticketChartInstance.update('active')
}

const initRevenueChart = () => {
  if (!revenueChartRef.value) {
    console.warn('Revenue chart canvas not found')
    return
  }
  
  if (revenueChartInstance) {
    revenueChartInstance.destroy()
    revenueChartInstance = null
  }

  const ctx = revenueChartRef.value.getContext('2d')
  if (!ctx) {
    console.warn('Could not get 2d context for revenue chart')
    return
  }

  const data = revenueBreakdown.value.map(item => item.value)
  const hasData = data.some(val => val > 0)

  revenueChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: revenueBreakdown.value.map(i => i.label),
      datasets: [{
        data: hasData ? data : [1, 1, 1],
        backgroundColor: hasData ? revenueBreakdown.value.map(i => i.color) : ['#e5e7eb', '#e5e7eb', '#e5e7eb'],
        borderWidth: 0,
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: { display: false },
        tooltip: {
          enabled: hasData,
          backgroundColor: '#002D1E',
          bodyColor: '#fff',
          padding: 12,
          cornerRadius: 4,
          callbacks: {
            label: function(context) {
              const value = context.parsed
              const total = context.dataset.data.reduce((a, b) => a + b, 0)
              const percentage = ((value / total) * 100).toFixed(1)
              return `₱${value.toLocaleString()} (${percentage}%)`
            }
          }
        }
      }
    }
  })
}

const initCompositionChart = () => {
  if (!compositionChartRef.value) return
  if (compositionChartInstance) compositionChartInstance.destroy()
  
  const ctx = compositionChartRef.value.getContext('2d')
  compositionChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: compositionData.value.labels,
      datasets: [{
        data: compositionData.value.data,
        backgroundColor: ['#fff', 'rgba(255,255,255,0.6)', 'rgba(255,255,255,0.3)'],
        borderWidth: 0,
        hoverOffset: 10
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '80%',
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#002D1E',
          titleColor: '#fff',
          bodyColor: '#fff',
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.raw}`
          }
        }
      }
    }
  })
}

const initRoutesChart = () => {
  if (!routesChartRef.value) return
  if (routesChartInstance) routesChartInstance.destroy()
  
  const ctx = routesChartRef.value.getContext('2d')
  routesChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: routesData.value.labels,
      datasets: [{
        label: 'Bookings',
        data: routesData.value.data,
        backgroundColor: '#002D1E',
        borderRadius: 2,
        barThickness: 12
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { grid: { display: false }, ticks: { display: false }, border: { display: false } },
        y: { 
          grid: { display: false }, 
          border: { display: false },
          ticks: { 
            font: { family: 'Poppins', size: 10, weight: 'bold' },
            color: '#9ca3af'
          }
        }
      }
    }
  })
}

const quickActions = [
  { label: 'Add Schedule', description: 'Create new flight schedule', icon: 'ph ph-calendar-plus', link: '/admin/manage-flight/schedules', colorClass: 'bg-blue-50 text-blue-600' },
  { label: 'Add Passenger', description: 'Register new passenger', icon: 'ph ph-user-plus', link: '/admin/passenger/list', colorClass: 'bg-green-50 text-green-600' },
  { label: 'View Bookings', description: 'Check all reservations', icon: 'ph ph-receipt', link: '/admin/booking/list', colorClass: 'bg-pink-50 text-[#fe3787]' }
]

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  return parseFloat(num).toLocaleString('en-PH', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  })
}

const calculateBearing = (startLat, startLng, endLat, endLng) => {
  const startLatRad = startLat * Math.PI / 180
  const startLngRad = startLng * Math.PI / 180
  const endLatRad = endLat * Math.PI / 180
  const endLngRad = endLng * Math.PI / 180

  const y = Math.sin(endLngRad - startLngRad) * Math.cos(endLatRad)
  const x = Math.cos(startLatRad) * Math.sin(endLatRad) -
    Math.sin(startLatRad) * Math.cos(endLatRad) * Math.cos(endLngRad - startLngRad)
  
  let brng = Math.atan2(y, x) * 180 / Math.PI
  return (brng + 360) % 360
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return ''
  return date.toLocaleDateString('en-PH', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return ''
  return date.toLocaleTimeString('en-PH', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

const statusClass = (status) => {
  const classes = {
    'Confirmed': 'bg-emerald-50 text-emerald-700 border border-emerald-100',
    'Pending': 'bg-amber-50 text-amber-700 border border-amber-100',
    'Cancelled': 'bg-rose-50 text-rose-700 border border-rose-100',
    'Completed': 'bg-blue-50 text-blue-700 border border-blue-100',
    'Paid': 'bg-purple-50 text-purple-700 border border-purple-100'
  }
  return classes[status] || 'bg-gray-50 text-gray-600 border border-gray-100'
}

const alertTypeClass = (type) => {
  const classes = {
    'warning': 'bg-yellow-50 border-yellow-400 text-yellow-800',
    'error': 'bg-red-50 border-red-400 text-red-800',
    'info': 'bg-blue-50 border-blue-400 text-blue-800',
    'success': 'bg-green-50 border-green-400 text-green-800'
  }
  return classes[type] || 'bg-gray-50 border-gray-400 text-gray-800'
}

const alertIconClass = (type) => {
  const classes = {
    'warning': 'ph-warning-circle text-yellow-600',
    'error': 'ph-x-circle text-red-600',
    'info': 'ph-info text-blue-600',
    'success': 'ph-check-circle text-green-600'
  }
  return classes[type] || 'ph-bell text-gray-600'
}

const initMap = () => {
  if (!mapContainer.value || mapInstance) return

  // Fix for default marker icons in Leaflet with Vite
  delete L.Icon.Default.prototype._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
    iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
    shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
  })

  mapInstance = L.map(mapContainer.value, {
    center: [12.8797, 121.7740], // Centered on Philippines
    zoom: 5,
    zoomControl: false,
    attributionControl: false
  })

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19
  }).addTo(mapInstance)

  L.control.zoom({ position: 'topright' }).addTo(mapInstance)
  
  updateMapMarkers()
}

const fetchActiveFlights = async () => {
  mapLoading.value = true
  try {
    const res = await api.get('/dashboard/active_flights_map/')
    activeFlights.value = res.data || []
    if (mapInstance) {
      updateMapMarkers()
    } else {
      await nextTick()
      initMap()
    }
    startFlightAnimation()
  } catch (err) {
    console.error('Map data fetch error:', err)
  } finally {
    mapLoading.value = false
  }
}

const toggleFullScreen = () => {
  if (!mapCardRef.value) return
  
  if (!document.fullscreenElement) {
    mapCardRef.value.requestFullscreen().catch(err => {
      console.error(`Error attempting to enable full-screen mode: ${err.message}`)
    })
  } else {
    document.exitFullscreen()
  }
}

const handleFullScreenChange = () => {
  isMapFullScreen.value = !!document.fullscreenElement
  if (mapInstance) {
    // Small delay to let the DOM settle before resizing Leaflet
    setTimeout(() => {
      mapInstance.invalidateSize()
      // If entering full screen, maybe zoom in or adjust center
      if (isMapFullScreen.value) {
        mapInstance.setZoom(mapInstance.getZoom() + 1)
      } else {
        mapInstance.setZoom(mapInstance.getZoom() - 1)
      }
    }, 100)
  }
}

const fetchSeatClassDistribution = async () => {
  seatclassLoading.value = true
  try {
    const res = await api.get('/dashboard/seat_class_distribution/')
    seatclassDist.value = res.data || { total: 0, classes: [] }
    await nextTick()
    initSeatClassChart()
  } catch (err) {
    console.error('Seat class distribution error:', err)
  } finally {
    seatclassLoading.value = false
  }
}

const initSeatClassChart = () => {
  if (!seatClassChartRef.value || seatclassDist.value.classes.length === 0) return
  if (seatClassChartInstance) {
    seatClassChartInstance.destroy()
    seatClassChartInstance = null
  }
  const ctx = seatClassChartRef.value.getContext('2d')
  const classes = seatclassDist.value.classes
  seatClassChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: classes.map(c => c.label),
      datasets: [{
        data: classes.map(c => c.count),
        backgroundColor: classes.map(c => c.color),
        borderWidth: 3,
        borderColor: '#fff',
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '72%',
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const cls = classes[ctx.dataIndex]
              return ` ${cls.label}: ${cls.count} pax (${cls.percentage}%)`
            }
          }
        }
      },
      animation: { animateRotate: true, duration: 800 }
    }
  })
}

const getFlightProgress = (flight) => {
  const now = Date.now()
  const dep = new Date(flight.departure_time).getTime()
  const arr = new Date(flight.arrival_time).getTime()
  
  if (now <= dep) return 0          // Not yet departed
  if (now >= arr) return 1          // Already landed
  return (now - dep) / (arr - dep)  // 0.0 - 1.0 progress
}

const updateMapMarkers = () => {
  if (!mapInstance) return

  // Clear existing
  flightMarkers.forEach(m => m.remove())
  flightPolylines.forEach(p => p.remove())
  flightMarkers = []
  flightPolylines = []

  activeFlights.value.forEach(flight => {
    const origin = [flight.origin.lat, flight.origin.lng]
    const dest = [flight.destination.lat, flight.destination.lng]

    // Draw Route Line
    const polyline = L.polyline([origin, dest], {
      color: '#fe3787',
      weight: 1,
      dashArray: '5, 10',
      opacity: 0.5
    }).addTo(mapInstance)
    flightPolylines.push(polyline)

    // Calculate actual position based on flight progress
    const t = getFlightProgress(flight)
    const aircraftPos = [
      origin[0] + (dest[0] - origin[0]) * t,
      origin[1] + (dest[1] - origin[1]) * t
    ]

    const bearing = calculateBearing(flight.origin.lat, flight.origin.lng, flight.destination.lat, flight.destination.lng)
    const progressPct = Math.round(t * 100)
    const isBoarding = flight.status === 'Closed'
    const statusColor = isBoarding ? '#f59e0b' : '#22c55e'
    const statusLabel = isBoarding ? 'Boarding' : 'In Flight'

    const planeIcon = L.divIcon({
      html: `<div class="relative" style="transform: rotate(${bearing - 45}deg)">
               <i class="ph ph-airplane-tilt text-[#fe3787] text-2xl drop-shadow-lg"></i>
               <div class="absolute -top-1 -right-1 w-2 h-2 rounded-full border border-white animate-pulse" style="background:${statusColor}"></div>
             </div>`,
      className: 'custom-plane-icon',
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    })

    // Show progress on popup
    const depStr = new Date(flight.departure_time).toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' })
    const arrStr = new Date(flight.arrival_time).toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' })

    const marker = L.marker(aircraftPos, { icon: planeIcon })
      .addTo(mapInstance)
      .bindPopup(`
        <div class="poppins p-1">
          <p class="font-black text-[#002D1E]">${flight.flight_number}</p>
          <p class="text-[10px] text-gray-500 uppercase font-bold">${flight.airline}</p>
          <span class="inline-block mt-1 px-2 py-0.5 text-[8px] font-bold uppercase rounded" style="background:${statusColor}22; color:${statusColor}">${statusLabel}</span>
          <div class="mt-2 border-t pt-2 flex items-center justify-between gap-4">
             <div>
                <p class="text-[8px] text-gray-400">FROM</p>
                <p class="text-[10px] font-bold">${flight.origin.code}</p>
                <p class="text-[8px] text-gray-400">${depStr}</p>
             </div>
             <div class="flex flex-col items-center gap-1">
               <i class="ph ph-arrow-right text-[#fe3787]"></i>
               <p class="text-[8px] font-black text-[#fe3787]">${progressPct}%</p>
             </div>
             <div>
                <p class="text-[8px] text-gray-400">TO</p>
                <p class="text-[10px] font-bold">${flight.destination.code}</p>
                <p class="text-[8px] text-gray-400">${arrStr}</p>
             </div>
          </div>
        </div>
      `, {
        className: 'custom-leaflet-popup'
      })
    flightMarkers.push(marker)
  })

  if (flightMarkers.length > 0 && flightPolylines.length > 0) {
    const allLayers = [...flightPolylines]
    const group = new L.featureGroup(allLayers)
    mapInstance.fitBounds(group.getBounds().pad(0.15))
  }
}

const startFlightAnimation = () => {
  // Clear existing intervals
  if (animationInterval) clearInterval(animationInterval)
  if (mapRefreshInterval) clearInterval(mapRefreshInterval)

  // Re-draw marker positions every 30 seconds (smooth movement)
  animationInterval = setInterval(() => {
    updateMapMarkers()
  }, 30000)

  // Re-fetch from API every 60 seconds to catch status changes
  mapRefreshInterval = setInterval(() => {
    fetchActiveFlights()
  }, 60000)
}

// Lifecycle
onMounted(() => {
  fetchDashboardData()
  document.addEventListener('fullscreenchange', handleFullScreenChange)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullScreenChange)
  // Clean up charts to prevent memory leaks
  if (ticketChartInstance) {
    ticketChartInstance.destroy()
    ticketChartInstance = null
  }
  if (revenueChartInstance) {
    revenueChartInstance.destroy()
    revenueChartInstance = null
  }
  if (mapInstance) {
    mapInstance.remove()
    mapInstance = null
  }
  if (animationInterval) {
    clearInterval(animationInterval)
    animationInterval = null
  }
  if (mapRefreshInterval) {
    clearInterval(mapRefreshInterval)
    mapRefreshInterval = null
  }
})
</script>

<style scoped>
.poppins {
  font-family: 'Poppins', sans-serif;
}

/* Custom scrollbar for tables */
.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}
.overflow-x-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}
.overflow-x-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

/* Smooth transitions */
.transition-shadow {
  transition: box-shadow 0.2s ease-in-out;
}

/* Loading animation */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>