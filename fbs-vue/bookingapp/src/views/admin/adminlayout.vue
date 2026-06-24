<template>
  <div class="h-screen bg-gray-100 flex ">
    <nav
      :class="[
        'sidebar text-white bg-[#fe3787] flex flex-col items-start transition-all duration-300 fixed h-screen z-50 no-print',
        collapsed ? 'w-16' : 'w-48'
      ]"
    >
    <button
      @click="toggleSidebar"
      class="absolute -right-3 top-1/2 -translate-y-1/2
            bg-white text-black rounded-full p-1 shadow-md z-50
            flex items-center justify-center border border-gray-200"
    >
      <i :class="collapsed ? 'ph ph-caret-right' : 'ph ph-caret-left'" class="text-xs"></i>
    </button>

      <div id="sidebar-content" class="w-full h-full overflow-y-auto flex flex-col py-2">
      <div class="mt-2 mb-4 flex items-center w-full px-4">
        <img src="@/assets/admin/cthm-logos.png" class="w-8 h-8 flex-shrink-0" />
        <span v-if="!collapsed" class="ml-3 font-bold leading-tight text-white text-[13px] poppins">
          Caraga State University <br/>
          <span class="font-semibold opacity-90">Cabadbaran Campus</span>
        </span>
      </div>

      <div class="w-full space-y-1 flex-1">
        <hr class="border-white/15 my-4 mx-4" />

        <div class="px-4 py-2 mt-4" v-if="!collapsed">
          <p class="text-[10px] uppercase font-black tracking-[0.2em] text-white/40 poppins">Main</p>
        </div>
        <router-link 
          to="/admin/dashboard" 
          class="flex items-center px-4 py-1.5 text-white hover:bg-white/10 transition-colors group"
          active-class="bg-white/10 border-l-4 border-white"
        >
          <i class="ph ph-squares-four text-lg"></i>
          <span v-if="!collapsed" class="ml-3 text-[12px] font-medium">Flight & LMS Dashboard</span>
        </router-link>

        <router-link 
          to="/admin/bulk-import" 
          class="flex items-center px-4 py-1.5 text-white hover:bg-white/10 transition-colors group"
          active-class="bg-white/10 border-l-4 border-white"
        >
          <i class="ph ph-database text-lg"></i>
          <span v-if="!collapsed" class="ml-3 text-[12px] font-medium">Bulk Import</span>
        </router-link>

        <router-link 
          to="/admin/manage-flight/live-monitor" 
          class="flex items-center px-4 py-1.5 text-white hover:bg-white/10 transition-colors group"
          active-class="bg-white/10 border-l-4 border-white"
        >
          <i class="ph ph-broadcast text-lg"></i>
          <span v-if="!collapsed" class="ml-3 text-[12px] font-medium">Live Monitoring</span>
        </router-link>

        <!-- LMS ADMIN PRIVILEGES: Users (Flat List) -->
        <template v-if="userRole === 'lms_admin'">
          <div class="px-4 py-2 mt-4" v-if="!collapsed">
            <p class="text-[10px] uppercase font-black tracking-[0.2em] text-white/40 poppins">User Management</p>
          </div>
          
          <router-link to="/admin/instructor-info/list" class="flex items-center px-4 py-1.5 text-white hover:bg-white/10 transition-colors group" active-class="bg-white/10 border-l-4 border-white">
            <i class="ph ph-chalkboard-teacher text-lg"></i>
            <span v-if="!collapsed" class="ml-3 text-[12px] font-medium">Instructors</span>
          </router-link>

          <router-link to="/admin/student-info/list" class="flex items-center px-4 py-1.5 text-white hover:bg-white/10 transition-colors group" active-class="bg-white/10 border-l-4 border-white">
            <i class="ph ph-student text-lg"></i>
            <span v-if="!collapsed" class="ml-3 text-[12px] font-medium">Students</span>
          </router-link>

          <router-link to="/admin/student-info/track-log" class="flex items-center px-4 py-1.5 text-white hover:bg-white/10 transition-colors group" active-class="bg-white/10 border-l-4 border-white">
            <i class="ph ph-clipboard-text text-lg"></i>
            <span v-if="!collapsed" class="ml-3 text-[12px] font-medium">Audit Logs</span>
          </router-link>
        </template>

        <!-- SUPERADMIN, FLIGHT_ADMIN, & ADMIN PRIVILEGES (Core Ops) -->
        <template v-if="['superadmin', 'flight_admin', 'admin'].includes(userRole)">
          <div class="px-4 py-2 mt-4" v-if="!collapsed">
            <p class="text-[10px] uppercase font-black tracking-[0.2em] text-white/40 poppins">Users</p>
          </div>
          <SidebarGroup title="Users" icon="ph-chalkboard-teacher">
            <SidebarSubLink label="Instructors" to="/admin/instructor-info/list" />
            <SidebarSubLink label="Students" to="/admin/student-info/list" />
            <SidebarSubLink label="Audit Logs" to="/admin/student-info/track-log" />
          </SidebarGroup>

          <div class="px-4 py-2 mt-4" v-if="!collapsed">
            <p class="text-[10px] uppercase font-black tracking-[0.2em] text-white/40 poppins">Flights</p>
          </div>
          <SidebarGroup title="Manage Flight" icon="ph-airplane">
            <SidebarSubLink label="Schedules" to="/admin/manage-flight/schedules" />
            <SidebarSubLink label="Profiles" to="/admin/manage-flight/flights" /> 
            <SidebarSubLink label="Routes" to="/admin/manage-flight/routes" />
            <SidebarSubLink label="Seat Maps" to="/admin/manage-flight/seats" />
          </SidebarGroup>

          <div class="px-4 py-2 mt-4" v-if="!collapsed">
            <p class="text-[10px] uppercase font-black tracking-[0.2em] text-white/40 poppins">Bookings</p>
          </div>
          <SidebarGroup title="Records" icon="ph-identification-card">
            <SidebarSubLink label="Passengers" to="/admin/passenger/list" />
            <SidebarSubLink label="Check-ins" to="/admin/passenger/check-ins" />
            <SidebarSubLink label="Details" to="/admin/booking/details" />
            <SidebarSubLink label="Bookings" to="/admin/booking/list" />
            <SidebarSubLink label="Payments" to="/admin/booking/payments" />
          </SidebarGroup>

          <div class="px-4 py-2 mt-4" v-if="!collapsed">
            <p class="text-[10px] uppercase font-black tracking-[0.2em] text-white/40 poppins">Assets</p>
          </div>
          <SidebarGroup title="Resources" icon="ph-database">
            <SidebarSubLink label="Countries" to="/admin/assets/countries" />
            <SidebarSubLink label="Airports" to="/admin/assets/airports" />
            <SidebarSubLink label="Aircraft" to="/admin/assets/aircraft" />
            <SidebarSubLink label="Airlines" to="/admin/assets/airlines" />
            <SidebarSubLink label="Seat Classes" to="/admin/assets/seat-classes" />
            <SidebarSubLink label="Seat Requirements" to="/admin/assets/seat-requirements" />
            <SidebarSubLink label="Add-on Types" to="/admin/assets/add-ons" />
          </SidebarGroup>

          <div class="px-4 py-2 mt-4" v-if="!collapsed">
            <p class="text-[10px] uppercase font-black tracking-[0.2em] text-white/40 poppins">Meal & Baggage</p>
          </div>
          <SidebarGroup title="Extra Services" icon="ph-package">
            <SidebarSubLink label="Meal Options" to="/admin/addons/meal-options" />
            <SidebarSubLink label="Assistance" to="/admin/addons/assistance" />
            <SidebarSubLink label="Baggage" to="/admin/addons/baggage" />
          </SidebarGroup>

          <div class="px-4 py-2 mt-4" v-if="!collapsed">
            <p class="text-[10px] uppercase font-black tracking-[0.2em] text-white/40 poppins">Insurance & Tax</p>
          </div>
          <SidebarGroup title="Insurance" icon="ph-shield-check">
            <SidebarSubLink label="Providers" to="/admin/insurance/providers" />
            <SidebarSubLink label="Plans" to="/admin/insurance/plans" />
          </SidebarGroup>

          <SidebarGroup title="Taxation" icon="ph-bank">
            <SidebarSubLink label="Airport Fees" to="/admin/manage-tax/airport-fee" />
            <SidebarSubLink label="Tax Types" to="/admin/manage-tax/tax-type" />
            <SidebarSubLink label="Airline Taxes" to="/admin/manage-tax/airline-tax" />
            <SidebarSubLink label="Travel Taxes" to="/admin/manage-tax/travel-tax" />
            <SidebarSubLink label="Booking Taxes" to="/admin/manage-tax/booking-tax" />
          </SidebarGroup>
        </template>
      </div>
      </div>
    </nav>

    <main 
      :class="['flex-1 flex flex-col min-h-screen transition-all duration-300', collapsed ? 'ml-16' : 'ml-48']"
      class="print:ml-0 relative"
    >
      <header class="h-12 flex items-center justify-between px-4 sticky top-0 z-40 
               bg-white/30 backdrop-blur-md border-b border-transparent no-print">
        <div>
          <h1 class="text-lg font-bold text-[#002D1E] poppins leading-none">
          {{ pageTitle }}
          </h1>
          <p class="text-xs text-gray-500">Welcome back! All systems are online.</p>
        </div>

        <div class="flex items-center space-x-4">
          <div class="relative">
            <div 
              @click.stop="isProfileOpen = !isProfileOpen"
              class="bg-[#fe3787] text-white px-4 py-2 rounded-[1px] flex items-center cursor-pointer font-medium text-sm gap-2 hover:bg-[#fa1571] transition-all shadow-sm"
            >
              <i class="ph ph-user-circle text-xl"></i>
              <span>{{ adminName }}</span>
              <span class="text-[10px] px-2 py-0.5 bg-white/20 rounded uppercase font-bold">{{ userRole }}</span>
              <i :class="isProfileOpen ? 'ph-caret-up' : 'ph-caret-down'" class="ph text-xs transition-transform duration-200"></i>
            </div>

            <transition 
              enter-active-class="transition duration-100 ease-out"
              enter-from-class="transform scale-95 opacity-0"
              enter-to-class="transform scale-100 opacity-100"
              leave-active-class="transition duration-75 ease-in"
              leave-from-class="transform scale-100 opacity-100"
              leave-to-class="transform scale-95 opacity-0"
            >
              <div 
                v-if="isProfileOpen" 
                class="absolute right-0 mt-2 w-48 bg-white shadow-xl  rounded-[1px] border border-gray-100 py-1 z-50 overflow-hidden"
              >
                <button   
                  @click="handleLogout"
                  class="flex items-center w-full px-4 py-3 text-sm text-gray-700 hover:bg-red-50 hover:text-red-600 transition-colors gap-3"
                >
                  <i class="ph ph-sign-out text-lg"></i>
                  <span class="font-medium">Logout</span>
                </button>
              </div>
            </transition>
          </div>
        </div>
      </header>

      <div class="p-1 bg-gray-100 flex-1 relative">
        <!-- Global Loading Overlay -->
        <div v-if="isNavigating" class="absolute inset-0 bg-gray-100/80 backdrop-blur-sm z-50 flex flex-col items-center justify-center animate-in fade-in duration-300">
          <i class="ph ph-circle-notch animate-spin text-5xl text-[#fe3787]"></i>
          <p class="mt-4 text-sm font-bold text-gray-500 uppercase tracking-widest poppins">Loading Module...</p>
        </div>

        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, provide, onMounted, onUnmounted, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import AuthStorage from '@/utils/authStorage';
import { useUserStore } from '@/stores/user';

// Import child components
import SidebarGroup from '@/components/admin/SidebarGroup.vue';
import SidebarSubLink from '@/components/admin/SidebarSubLink.vue';

const collapsed = ref(false);
const isProfileOpen = ref(false);
const isNavigating = ref(false);

const userStore = useUserStore();
const router = useRouter();
const route = useRoute();

// Setup router navigation guards for loading screen
router.beforeEach((to, from, next) => {
  if (to.path !== from.path) {
    isNavigating.value = true;
  }
  next();
});

router.afterEach(() => {
  // Add a slight delay to allow component mounting
  setTimeout(() => {
    isNavigating.value = false;
  }, 300);
});

const adminName = computed(() => {
  if (userStore.user?.username) return userStore.user.username;
  return localStorage.getItem('adminUsername') || 'Admin';
});

const userRole = computed(() => {
  return AuthStorage.getRole() || 'admin';
});

/* -------------------------
   Sidebar
-------------------------- */
const toggleSidebar = () => {
  collapsed.value = !collapsed.value;
};

/* -------------------------
   Logout
-------------------------- */
const handleLogout = () => {
  // Clear modern session
  AuthStorage.clearCurrentSession();
  userStore.logout();

  // Clear legacy admin flags
  localStorage.removeItem('adminLoggedIn');
  localStorage.removeItem('adminUsername');
  localStorage.removeItem('adminName');

  router.push('/admin/login');
};

/* -------------------------
   Profile dropdown
-------------------------- */
const closeDropdown = (e) => {
  if (!e.target.closest('.relative')) {
    isProfileOpen.value = false;
  }
};

/* -------------------------
   🔥 Dynamic Page Title
-------------------------- */
const pageTitle = computed(() => {
  return route.meta.title || 'Dashboard';
});

// Optional: update browser tab title
watch(
  () => route.meta.title,
  (title) => {
    document.title = title ? `${title} | Admin Panel` : 'Admin Panel';
  },
  { immediate: true }
);

/* -------------------------
   Lifecycle
-------------------------- */
onMounted(() => {
  window.addEventListener('click', closeDropdown);
});

onUnmounted(() => {
  window.removeEventListener('click', closeDropdown);
});

/* -------------------------
   Provide sidebar state
-------------------------- */
provide('isSidebarCollapsed', collapsed);
</script>


<style>
@media print {
  /* Aggressive global hiding */
  .no-print, 
  .sidebar, 
  nav, 
  header,
  .sticky,
  aside,
  button,
  .sidebar-content,
  #sidebar-content {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    position: absolute !important;
    left: -9999px !important;
  }
  
  /* FORCE ZERO SPACING - FIXES THE GAP */
  body, html, #app, .h-screen, main, .flex-1 {
    margin-left: 0 !important;
    margin-right: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    width: 100% !important;
    position: static !important;
    display: block !important;
    left: 0 !important;
    background: white !important;
  }

  .ml-16, .ml-48, .ml-64 {
    margin-left: 0 !important;
  }
  
  body {
    overflow: visible !important;
    height: auto !important;
  }
}
</style>

<style scoped>
.poppins {
  font-family: 'Poppins', sans-serif;
}

#sidebar-content::-webkit-scrollbar {
  width: 4px;
}
#sidebar-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
</style>