<template>
<div
  class="min-h-screen flex flex-col bg-no-repeat bg-center"
  :style="{
    backgroundImage: `url(${bgImage})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat',
    backgroundAttachment: 'fixed'
  }"
>

    <!-- Header -->
    <header class="bg-[#F9FAFB]  p-4 shadow-md relative flex items-center space-x-3">
      <img :src="headerLogo" alt="CSU Logo" class="ml-4 h-15 w-15">
      <div>
        <h1 class="poppins font-bold text-[#FF579A] text-[15px]">Caraga State University</h1>
        <p class="poppins-none text-[#FF579A] text-[10px]">Cabadbaran City</p>
        <p class="font-extralight text-black poppins-none text-[10px] mb-1">
          T. Curato St., Cabadbaran City, Agusan del Norte, 8604
        </p>
      </div>
      <div class="absolute bottom-0 left-0 w-full h-1 first-color"></div>
    </header>

    <!-- Main Content -->
    <main class="flex flex-grow">

      <!-- Left Side -->
      <div class="w-1/2 flex flex-col justify-center pl-20 pr-10 relative overflow-hidden">
        <div class="relative z-10 flex flex-col items-center justify-center text-center">
          <h2 class="text-5xl font-bold mb-3 text-white unbounded-none">
            Welcome back,<br>Administrators.
          </h2>
          <p class="text-white poppins max-w-md">
            Please login to access the admin dashboard.
          </p>

          <div class="flex justify-center items-center space-x-6 mt-4">
            <img :src="logo1" class="h-16 w-16 object-contain">
            <img :src="logo2" class="h-20 w-16 object-contain">
            <img :src="logo3" class="h-16 w-16 object-contain">
            <img :src="logo4" class="h-16 w-16 object-contain">
          </div>
        </div>
      </div>

      <!-- Right Side (Login Form) -->
      <div class="w-1/2 flex items-center justify-center">
        <div class="bg-white p-6 rounded shadow-md w-full max-w-sm">
          <h2 class="text-xl font-bold mb-4 text-center poppins">Login</h2>
          <p class="poppins-small text-[#FF579A] text-center mb-3">Please enter your information</p>

          <form @submit.prevent="login" class="space-y-3">
            <label class="block poppins text-sm">Username</label>
            <div class="flex items-center bg-gray-100 border rounded shadow-inner p-2">
              <input
                v-model="username"
                type="text"
                placeholder="Enter username"
                class="w-full bg-gray-100 outline-none text-sm"
                required
              >
            </div>

            <label class="block poppins text-sm mt-2">Password</label>
            <div class="flex items-center bg-gray-100 border rounded shadow-inner p-2">
              <input
                v-model="password"
                type="password"
                placeholder="Enter password"
                class="w-full bg-gray-100 outline-none text-sm"
                required
              >
            </div>

            <button
              type="submit"
              class="w-full mt-3 bg-[#FF579A] text-white p-2 font-semibold poppins text-sm"
            >
              Login
            </button>
          </form>
        </div>
      </div>

    </main>

    <!-- Footer -->
    <footer class="bg-[#F9FAFB] text-black flex items-center justify-center p-2 poppins-small h-14">
      © 2025 All rights reserved.
    </footer>
  </div>
</template>

<script>
import { adminLogin } from '@/services/admin/login'
import AuthStorage from '@/utils/authStorage'
import { useUserStore } from '@/stores/user'

import bgImage from '@/assets/admin/bg-cthm.svg'
import headerLogo from '@/assets/admin/cthm-logo.png'
import logo1 from '@/assets/admin/logo-1.png'
import logo2 from '@/assets/admin/logo-2.png'
import logo3 from '@/assets/admin/logo-3.png'
import logo4 from '@/assets/admin/logo-4.png'

export default {
  name: 'AdminLogin',

  setup() {
    const userStore = useUserStore()
    return { userStore }
  },

  data() {
    return {
      username: '',
      password: '',
      bgImage,
      headerLogo,
      logo1,
      logo2,
      logo3,
      logo4
    }
  },

  methods: {
    async login() {
      try {
        const result = await adminLogin(this.username, this.password)

        if (result.success) {
          // 1. Initialize session using AuthStorage (Required by new Router Guard)
          AuthStorage.clearCurrentSession()
          AuthStorage.initializeSession({
            token: result.token,
            session_id: result.session_id,
            role: result.role,
            user: result.user,
            dashboard_route: result.dashboard_route
          })

          // 2. Legacy support for components reading from localStorage directly
          localStorage.setItem('adminLoggedIn', 'true')
          localStorage.setItem('adminUsername', this.username)
          localStorage.setItem('token', result.token)
          localStorage.setItem('role', result.role)

          // Update user store
          this.userStore.setAuth({
            token: result.token,
            user: result.user,
            role: result.role
          })

          // Redirect to admin dashboard
          this.$router.push('/admin/dashboard')
        } else {
          alert(result.message || 'Invalid credentials or not an admin.')
        }
      } catch (error) {
        console.error('Admin Login Error:', error)
        const msg = error.response?.data?.message || error.message || 'Login failed. Please try again.'
        alert(`Login failed: ${msg}`)
      }
    }
  }
}
</script>


<style scoped>
.first-color { background-color: #FF579A; }
.second-color { background-color: #FFC83D; }
.unbounded { font-family: 'Unbounded', sans-serif; }
.unbounded-none { font-family: 'Unbounded', sans-serif; }
.poppins { font-family: 'Poppins', sans-serif; }
.poppins-none { font-family: 'Poppins', sans-serif; }
.poppins-small { font-family: 'Poppins', sans-serif; font-size: 10px; }
</style>
