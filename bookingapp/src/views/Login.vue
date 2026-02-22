<template>
  <div
    class="min-h-screen bg-cover bg-center bg-no-repeat"
    :style="backgroundStyle"
  >
    <div class="min-h-screen bg-black/20">
      <header class="px-6 py-4 flex items-center justify-between" style="background-color:whitesmoke ;">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-full flex items-center justify-center" style="background-color: #FF579A;">
            <span class="font-bold text-xl" style="color: #F9FAFB ;">CS</span>
          </div>
          <div style="color: #0E8028;">
            <div class="font-bold text-lg">CARAGA STATE UNIVERSITY</div>
            <div class="text-xs">CABADBARAN CITY</div>
          </div>
        </div>
        <div class="flex gap-3">
        <router-link to="/register">
          <button class="font-semibold px-6 py-2 rounded" style="background-color: #FF579A; color: #F9FAFB;">
            Register
          </button>
        </router-link>

        <button class="border-2 font-semibold px-6 py-2 rounded" style="border-color: #FF579A; background-color: transparent; color: #0E8028 ;">
          Contact Us
        </button>
      </div>
      </header>

      <div class="container mx-auto px-6 py-12">
        <div class="grid lg:grid-cols-3 gap-8 items-start">
          <div class="lg:col-span-2 space-y-8">
            <div style="color: #F9FAFB;">
              <h1 class="text-4xl lg:text-5xl font-bold mb-4 leading-tight">
                TourEd Academy: Flight Booking and Tourism Training Platform
              </h1>
              <p class="leading-relaxed">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
              </p>
            </div>
          </div>

          <div class="lg:col-span-1">
            <div class="rounded-lg shadow-2xl p-8" style="background-color: #F9FAFB;">
              <h2 class="text-2xl font-bold text-gray-800 mb-2 text-center">Login Here!</h2>
              <p class="text-gray-500 text-sm text-center mb-8">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit.
              </p>

              <div class="space-y-6">
                <div>
                  <label class="block text-gray-700 font-semibold mb-2">Username</label>
                  <input
                    v-model="username"
                    type="text"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none"
                    placeholder="Enter username"
                  />
                </div>

                <div>
                  <label class="block text-gray-700 font-semibold mb-2">Password</label>
                  <input
                    v-model="password"
                    type="password"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none"
                    placeholder="Enter password"
                    @keyup.enter="handleLogin"
                  />
                </div>

                <button
                  @click="handleLogin"
                  :disabled="loading"
                  class="w-full font-bold py-3 rounded-lg transition-opacity"
                  :class="loading ? 'opacity-50 cursor-not-allowed' : 'hover:opacity-90'"
                  style="background-color: #FF579A; color: #F9FAFB;"
                >
                  <span v-if="loading">Logging in...</span>
                  <span v-else>Login</span>
                </button>

                <div class="text-center">
                  <a href="#" class="text-sm" style="color: #FF579A;">
                    forgot password?
                  </a>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import bgImage from '@/assets/image/bg-cthm.svg'
import { authService } from '@/services/auth/authService'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'
import { useRouter } from 'vue-router'

export default {
  name: 'LoginView',
  setup() {
    const userStore = useUserStore()
    const notificationStore = useNotificationStore()
    const router = useRouter() // Get router instance
    return { userStore, notificationStore, router } // Expose router
  },
  data() {
    return {
      username: '',
      password: '',
      isLoading: false
    }
  },
  computed: {
    backgroundStyle() {
      return {
        backgroundImage: `url(${bgImage})`
      }
    }
  },
  methods: {
    async handleLogin() {
      if (!this.username || !this.password) {
        this.notificationStore.warn('Please enter both username and password')
        return
      }
      
      this.isLoading = true

      try {
        console.log('🔐 Attempting login for:', this.username)
        
        // 1. Send Login Request
        const { token, user, role, dashboard_route } = await authService.login(this.username, this.password);
        
        // 2. Update Central Store
        this.userStore.setAuth({ token, user, role });
        
        console.log('✅ Login successful - User Store Updated');
        this.notificationStore.success('Login successful! Redirecting...')
        console.log('DEBUG: dashboard_route:', dashboard_route);
        console.log('DEBUG: router instance:', this.router);
        
        // 3. Move to appropriate dashboard
        setTimeout(() => {
          if (dashboard_route && this.router) {
            this.router.push(dashboard_route).catch(err => {
              console.error('Router push failed:', err);
              // Fallback to window location if router fails
              window.location.href = dashboard_route;
            });
          } else {
             console.error('Dashboard route or router missing');
             this.notificationStore.error('Navigation failed');
          }
        }, 500)
        
      } catch (err) {
        console.error('❌ LOGIN ERROR:', err)
        if (err.response) {
          const data = err.response.data
          if (err.response?.status === 401) {
            this.notificationStore.error('Invalid username or password')
          } else {
            const msg = data.error || data.detail || data.message || 'An error occurred during login.'
            this.notificationStore.error(msg)
          }
        } else {
          this.notificationStore.error('Login failed. Please check your internet connection.')
        }
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>