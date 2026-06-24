<template>
  <div class="bg-[#F9F9F9] text-gray-800 px-4 py-2.5 flex items-center shadow-sm justify-between ">
    <div class="flex items-center gap-3">
      <button 
        @click="$emit('toggle-sidebar')" 
        class="p-1.5 hover:bg-gray-500/20  cursor-pointer rounded transition-colors focus:outline-none"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </button>
      
      <div class="flex items-center gap-2">
        <div class="w-10 h-10 rounded-full flex items-center justify-center overflow-hidden">
          <img :src="CTHM" alt="CTHM Logo" class="w-full h-full object-contain">
        </div>
        <div class="font-sans">
          <div class="text-[10px] sm:text-xs font-bold leading-tight text-gray-900">College of Tourism and Hospitality Management</div>
          <div class="text-[8px] sm:text-[9px] text-green-800 font-medium opacity-90 leading-tight">CARAGA STATE UNIVERSITY - CABADBARAN CITY</div>
        </div>
      </div>
    </div>

    <div class="flex items-center gap-4 relative">
      <!-- Notification Bell -->
      <div class="relative">
        <button 
          @click="toggleNotificationDropdown"
          class="p-1.5 text-gray-400 hover:text-pink-600 hover:bg-pink-50 rounded-full transition-colors focus:outline-none relative"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <span 
            v-if="unreadCount > 0" 
            class="absolute top-0 right-0 inline-flex items-center justify-center min-w-[18px] h-[18px] text-[10px] font-bold text-white bg-red-500 rounded-full border-2 border-white px-1"
          >
            {{ unreadCount > 99 ? '99+' : unreadCount }}
          </span>
        </button>

        <!-- Notification Dropdown -->
        <div 
          v-if="notificationOpen" 
          class="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-lg shadow-xl py-1 z-50 border border-gray-100"
        >
          <div class="px-4 py-3 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
            <h3 class="text-sm font-bold text-gray-800">Notifications</h3>
            <button 
              v-if="unreadCount > 0"
              @click.stop="markAllAsRead"
              class="text-xs font-semibold text-pink-600 hover:text-pink-800 transition-colors"
            >
              Mark all as read
            </button>
          </div>
          
          <div class="max-h-[60vh] overflow-y-auto">
            <div v-if="loadingNotifications && notifications.length === 0" class="p-4 text-center">
              <svg class="animate-spin h-5 w-5 text-pink-500 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>

            <div v-else-if="notifications.length === 0" class="p-6 text-center text-gray-500">
              <div class="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </div>
              <p class="text-sm">You're all caught up!</p>
              <p class="text-xs text-gray-400 mt-1">No new notifications</p>
            </div>

            <div v-else class="divide-y divide-gray-50">
              <div 
                v-for="notif in notifications" 
                :key="notif.id"
                @click="handleNotificationClick(notif)"
                class="px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors flex gap-3 group"
                :class="{ 'bg-pink-50/30': !notif.is_read }"
              >
                <div class="flex-shrink-0 mt-1">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center shadow-sm"
                    :class="!notif.is_read ? 'bg-pink-100 text-pink-600' : 'bg-gray-100 text-gray-500'"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                  </div>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex justify-between items-start mb-1">
                    <p class="text-sm font-semibold text-gray-900 truncate pr-2" :class="{'text-pink-700': !notif.is_read}">
                      {{ notif.title }}
                    </p>
                    <span class="text-[10px] font-medium text-gray-400 whitespace-nowrap">
                      {{ formatTimeAgo(notif.created_at) }}
                    </span>
                  </div>
                  <p class="text-xs text-gray-600 line-clamp-2 leading-relaxed">
                    {{ notif.message }}
                  </p>
                  <div v-if="!notif.is_read" class="mt-2">
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-pink-100 text-pink-700">
                      New
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="px-4 py-2 border-t border-gray-100 bg-gray-50/50 text-center">
            <button 
              @click="$router.push('/student/dashboard'); notificationOpen = false;"
              class="text-xs font-semibold text-gray-500 hover:text-gray-800 transition-colors"
            >
              View Dashboard
            </button>
          </div>
        </div>
      </div>

      <!-- Profile Dropdown -->
      <div class="relative">
        <button 
          @click="toggleProfileDropdown" 
          class="flex items-center gap-2 hover:bg-pink-600/10 px-1 py-1 rounded-full transition-colors focus:outline-none"
        >
          <div class="w-7 h-7 bg-[#F9F9F9] rounded-full flex items-center justify-center overflow-hidden border-2 border-white shadow-sm">
            <div class="w-full h-full bg-pink-200 flex items-center justify-center text-pink-700 font-bold text-xs">
              {{ initials }}
            </div>
          </div>
        </button>

        <div v-if="dropdownOpen" class="absolute right-0 mt-2 w-48 bg-[#F9F9F9] rounded-lg shadow-xl py-1 z-50 border border-gray-100">
          <div class="px-4 py-3 border-b border-gray-100">
            <p class="text-sm font-semibold text-gray-800">{{ fullName }}</p>
            <p class="text-xs text-gray-500">{{ student?.email }}</p>
          </div>
          <button 
            @click="$router.push('/profile')" 
            class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
          >
            My Profile
          </button>
          <button 
            @click="$emit('logout')" 
            class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import notificationService from '@/services/Student/notificationService';
import CTHM from '@/assets/image/cthm-logos.png';

export default {
  name: 'DashboardHeader',
  props: {
    student: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      dropdownOpen: false,
      notificationOpen: false,
      notifications: [],
      unreadCount: 0,
      loadingNotifications: false,
      pollingInterval: null,
      CTHM
    }
  },
  computed: {
    fullName() {
      if (!this.student) return 'Student';
      return `${this.student.first_name || ''} ${this.student.last_name || ''}`.trim() || 'Student';
    },
    initials() {
      if (!this.student) return 'ST';
      const first = this.student.first_name?.charAt(0) || '';
      const last = this.student.last_name?.charAt(0) || '';
      return (first + last).toUpperCase() || 'ST';
    }
  },
  methods: {
    toggleProfileDropdown() {
      this.dropdownOpen = !this.dropdownOpen;
      if (this.dropdownOpen) this.notificationOpen = false;
    },
    toggleNotificationDropdown() {
      this.notificationOpen = !this.notificationOpen;
      if (this.notificationOpen) this.dropdownOpen = false;
    },
    async fetchNotifications(showLoading = false) {
      if (showLoading) this.loadingNotifications = true;
      try {
        const data = await notificationService.getNotifications();
        this.notifications = data.notifications;
        this.unreadCount = data.unread_count;
      } catch (error) {
        console.error('Failed to poll notifications:', error);
      } finally {
        this.loadingNotifications = false;
      }
    },
    async markAllAsRead() {
      try {
        await notificationService.markAsRead();
        this.notifications.forEach(n => n.is_read = true);
        this.unreadCount = 0;
      } catch (error) {
        console.error('Failed to mark all as read');
      }
    },
    async handleNotificationClick(notif) {
      this.notificationOpen = false;
      if (!notif.is_read) {
        try {
          await notificationService.markAsRead([notif.id]);
          notif.is_read = true;
          this.unreadCount = Math.max(0, this.unreadCount - 1);
        } catch (error) {
          console.error('Failed to mark as read');
        }
      }
      if (this.$route.path !== '/student/dashboard') {
        this.$router.push('/student/dashboard');
      }
    },
    formatTimeAgo(dateString) {
      const date = new Date(dateString);
      const now = new Date();
      const diffInSeconds = Math.floor((now - date) / 1000);
      
      if (diffInSeconds < 60) return 'Just now';
      if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
      if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
      return `${Math.floor(diffInSeconds / 86400)}d ago`;
    }
  },
  mounted() {
    // Initial fetch
    this.fetchNotifications(true);
    
    // Start polling every 60 seconds
    this.pollingInterval = setInterval(() => {
      this.fetchNotifications();
    }, 60000);

    document.addEventListener('click', (e) => {
      // Close profile dropdown
      if (this.dropdownOpen && !e.target.closest('.relative')) {
        this.dropdownOpen = false;
      }
      // Close notification dropdown
      if (this.notificationOpen && !e.target.closest('.relative')) {
        this.notificationOpen = false;
      }
    });
  },
  beforeUnmount() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
  }
}
</script>
