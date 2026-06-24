<template>
  <div
    class="min-h-screen bg-cover bg-center bg-no-repeat flex flex-col font-sans"
    :style="backgroundStyle"
  >
    <!-- Dark overlay for better contrast & backdrop blur -->
    <div class="min-h-screen bg-black/40 flex flex-col backdrop-blur-[2px]">
      
      <!-- Responsive Header -->
      <header class="w-full px-4 md:px-8 py-2 md:py-2 flex flex-col sm:flex-row items-center justify-between gap-4 md:gap-0 transition-all duration-300" 
              style="background-color: rgba(245, 245, 245, 0.95); backdrop-filter: blur(8px); box-shadow: 0 2px 15px rgba(0,0,0,0.1);">
        
        <div class="flex items-center gap-3 sm:gap-4 group">
          <div class="w-8 h-8 md:w-12 md:h-12 rounded-full flex items-center justify-center bg-white shadow-sm overflow-hidden transition-transform duration-300">
            <img :src="CTHM" alt="CTHM Logo" class="w-full h-full object-contain p-0.5">
          </div>
          <div class="text-center sm:text-left">
            <h1 class="font-bold text-xs md:text-sm lg:text-base text-gray-800 leading-tight">
              College of Tourism and Hospitality Management
            </h1>
            <p class="text-[10px] md:text-xs text-gray-600 font-medium tracking-wide uppercase">
              CARAGA STATE UNIVERSITY - CABADBARAN CITY
            </p>
          </div>
        </div>

        <div class="flex items-center gap-3 w-full sm:w-auto justify-center sm:justify-end">
          <!-- <router-link to="/register" class="w-full sm:w-auto">
            <button class="w-full sm:w-auto font-bold text-white bg-pink-500 px-4 md:px-8 py-2 md:py-2.5 rounded-sm text-xs md:text-sm cursor-pointer hover:bg-pink-500/80" 
                    >
              Register
            </button>
          </router-link> -->

          <button class="hidden sm:block border-2 font-bold bg-white text-pink-500 hover:bg-pink-600/80 hover:text-white cursor-pointer px-4 md:px-8 py-2 md:py-2.5 rounded-sm text-xs md:text-sm transition-all duration-300 active:scale-95" 
                 >
            Contact Us
          </button>
        </div>
      </header>

      <!-- Main Responsive Content -->
      <main class="flex-grow flex items-center justify-center p-2 md:p-4">
        <div class="container mx-auto max-w-7xl">
          <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-16  ">
            
            <!-- Left Info Content -->
            <div class="lg:col-span-7 space-y-4 md:space-y-8 text-center mt-5 lg:text-left animate-fade-in-up">
              <div style="color: #F9FAFB;">
                <h2 class="text-xl md:text-2xl lg:text-3xl font-extrabold mb-2 md:mb-4 leading-[1.1] drop-shadow-lg tracking-tight">
                  <span class="block text-rose-300 text-4xl">TourSim :</span>
                  Flight Booking and Tourism Training Platform
                </h2>
                <div class="h-1.5 w-24 bg-rose-400 rounded-full mb-6 mx-auto lg:mx-0 shadow-sm"></div>
                <p class="leading-relaxed text-sm md:text-base font-medium opacity-90 max-w-2xl mx-auto lg:mx-0 drop-shadow-sm">
                  Experience flight booking simulation and comprehensive tourism training. Standardizing tourism education through digital innovation and hands-on simulation tools.
                </p>
              </div>
              
              <!-- Features/Indicators -->
              <div class="hidden sm:flex flex-wrap justify-center lg:justify-start gap-4 md:gap-8 pt-4">
                 <div class="flex items-center gap-2 text-white/90">
                    <div class="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.5)]"></div>
                    <span class="text-sm font-semibold tracking-wide uppercase opacity-80">Live Simulation</span>
                 </div>
               
              </div>
            </div>

            <!-- Login Card -->
            <div class="lg:col-span-5 w-full max-w-md mx-auto animate-fade-in-right">
              <div class="rounded-sm shadow-2xl p-4 md:p-6 transition-all duration-300 hover:shadow-[0_20px_50px_rgba(0,0,0,0.3)] bg-white/95 backdrop-blur-md">
                <div class="text-center mb-8">
                  <h3 class="text-2xl md:text-xl font-black text-gray-900 mb-2">Welcome Back</h3>
                  <p class="text-gray-500 text-xs font-medium">
                    Sign in to your training workspace
                  </p>
                </div>

                <div class="space-y-5">
                  <div class="space-y-1.5">
                    <label class="block text-gray-800 font-bold text-xs uppercase tracking-widest ml-1">Username</label>
                    <div class="relative group">
                       <input
                        v-model="username"
                        type="text"
                        class="w-full px-5 py-1.5 md:py-2 bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:border-rose-400 focus:bg-white transition-all duration-300 font-medium"
                        placeholder="Enter your username"
                      />
                    </div>
                  </div>

                  <div class="space-y-1.5">
                    <label class="block text-gray-800 font-bold text-xs uppercase tracking-widest ml-1">Password</label>
                    <div class="relative group">
                      <input
                        v-model="password"
                        type="password"
                        class="w-full px-5 py-1.5 md:py-2 bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:border-rose-400 focus:bg-white transition-all duration-300 font-medium"
                        placeholder="••••••••"
                        @keyup.enter="handleLogin"
                      />
                    </div>
                  </div>

                  <div class="flex items-center justify-between px-1">
                    <label class="flex items-center gap-2 cursor-pointer group">
                      <input type="checkbox" class="accent-rose-500 w-4 h-4 rounded">
                      <span class="text-xs text-gray-600 font-medium group-hover:text-gray-900 transition-colors">Remember me</span>
                    </label>
                    <router-link to="/forgot-password" class="text-xs font-bold text-rose-500 hover:text-rose-600 transition-colors">
                      Forgot password?
                    </router-link>
                  </div>

                  <button
                    @click="handleLogin"
                    :disabled="loading"
                    class="w-full font-bold py-1.5 md:py-2.5 rounded-md text-white  bg-pink-500 hover:bg-pink-500/80 cursor-pointer transition-all duration-300 active:scale-[0.98] disabled:opacity-70 disabled:scale-100 disabled:cursor-not-allowed group relative overflow-hidden"
                  >
                    <div class="flex items-center justify-center gap-2">
                       <span v-if="loading" class="animate-pulse">Authenticating...</span>
                       <span v-else class="flex items-center gap-2">
                         LOGIN 
                         <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                         </svg>
                       </span>
                    </div>
                  </button>

                  <div class="text-center pt-2 sm:hidden">
                    <p class="text-sm text-gray-500">
                      Need help? <a href="#" class="text-rose-500 font-bold">Contact Support</a>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- Footer / Version -->
      <footer class="p-6 text-center">
         <p class="text-white/60 text-[10px] font-bold tracking-[0.2em] uppercase">
            © 2025 CSUCC College of Tourism and Hospitality Management • v1.2.0
         </p>
      </footer>
    </div>
  </div>
</template>


<script>
import bgImage from '@/assets/image/bg-cthm.svg'
import { authService } from '@/services/auth/authService'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'
import { useRouter } from 'vue-router'
import CTHM from '@/assets/image/cthm-logos.png'

export default {
  name: 'LoginView',
  setup() {
    const userStore = useUserStore()
    const notificationStore = useNotificationStore()
    const router = useRouter() // Get router instance
    return { userStore, notificationStore, router, CTHM } // Expose router + logo
  },
  data() {
    return {
      username: '',
      password: '',
      loading: false
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
      
      this.loading = true

      try {
        console.log('🔐 Attempting login for:', this.username);
        
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
        console.error('❌ LOGIN ERROR:', err);
        if (err.response) {
          const data = err.response.data;
          if (err.response?.status === 401 || err.response?.status === 400) {
            const errorMsg = data.non_field_errors?.[0] || data.error || data.detail || 'Invalid username or password';
            this.notificationStore.error(errorMsg);
          } else {
            const msg = data.error || data.detail || data.message || 'An error occurred during login.';
            this.notificationStore.error(msg);
          }
        } else if (err.message === 'NOT_ENROLLED') {
          this.notificationStore.error('You are not enrolled. Please contact your instructor or administrator.');
        } else {
          this.notificationStore.error('Login failed. Please check your internet connection.');
        }
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.8s ease-out forwards;
}

.animate-fade-in-right {
  animation: fadeInRight 0.8s ease-out forwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Custom transitions for inputs */
input::placeholder {
  color: #9ca3af;
  font-weight: 400;
  opacity: 0.6;
}

/* Mobile adjustments for header text */
@media (max-width: 640px) {
  header {
    background-color: white !important;
  }
}

/* Smooth glassmorphism enhancements */
.backdrop-blur-md {
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
</style>
