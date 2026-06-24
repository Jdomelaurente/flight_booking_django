<template>
  <div class="min-h-screen bg-cover bg-center bg-no-repeat" :style="backgroundStyle">
    <div class="min-h-screen bg-black/20">
      <header class="px-6 py-4 flex items-center justify-between" style="background-color:whitesmoke;">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-full flex items-center justify-center" style="background-color: #FF579A;">
            <span class="font-bold text-xl" style="color: #F9FAFB;">CS</span>
          </div>
          <div style="color: #0E8028;">
            <div class="font-bold text-lg">CARAGA STATE UNIVERSITY</div>
            <div class="text-xs">CABADBARAN CITY</div>
          </div>
        </div>
      </header>

      <div class="container mx-auto px-6 py-12">
        <div class="grid lg:grid-cols-3 gap-8 items-start">
          <div class="lg:col-span-1"></div>

          <div class="lg:col-span-1">
            <div class="rounded-lg shadow-2xl p-8" style="background-color: #F9FAFB;">
              <h2 class="text-2xl font-bold text-gray-800 mb-2 text-center">Create Account</h2>
              <p class="text-gray-500 text-sm text-center mb-6">Register to access the platform.</p>

              <div class="space-y-4">
                <!-- Role Selector -->
                <div>
                  <label class="block text-gray-700 font-semibold mb-1">I am a:</label>
                  <select v-model="form.role" class="w-full px-4 py-2 border rounded-lg focus:outline-none bg-white">
                    <option value="student">Student</option>
                    <option value="instructor">Instructor</option>
                  </select>
                </div>

                <!-- Username + ID -->
                <div class="grid grid-cols-2 gap-2">
                  <div>
                    <label class="block text-gray-700 font-semibold mb-1">Username</label>
                    <input v-model="form.username" type="text" class="w-full px-4 py-2 border rounded-lg" placeholder="User123" />
                  </div>
                  <div>
                    <label class="block text-gray-700 font-semibold mb-1">
                      {{ form.role === 'student' ? 'Student ID' : 'Instructor ID' }}
                    </label>
                    <input v-model="form.id_number" type="text" class="w-full px-4 py-2 border border-pink-300 rounded-lg" placeholder="2024-XXXX" />
                  </div>
                </div>

                <!-- Name Fields -->
                <div class="grid grid-cols-3 gap-2">
                  <div class="col-span-1">
                    <label class="block text-gray-700 font-semibold mb-1">First Name</label>
                    <input v-model="form.first_name" type="text" class="w-full px-4 py-2 border rounded-lg" />
                  </div>
                  <div class="col-span-1">
                    <label class="block text-gray-700 font-semibold mb-1">M.I.</label>
                    <input v-model="form.mi" type="text" maxlength="1" class="w-full px-4 py-2 border rounded-lg text-center" />
                  </div>
                  <div class="col-span-1">
                    <label class="block text-gray-700 font-semibold mb-1">Last Name</label>
                    <input v-model="form.last_name" type="text" class="w-full px-4 py-2 border rounded-lg" />
                  </div>
                </div>

                <!-- Email + Gender -->
                <div class="grid grid-cols-2 gap-2">
                  <div>
                    <label class="block text-gray-700 font-semibold mb-1">Email</label>
                    <input v-model="form.email" type="email" class="w-full px-4 py-2 border rounded-lg" placeholder="email@example.com" />
                  </div>
                  <div>
                    <label class="block text-gray-700 font-semibold mb-1">Gender</label>
                    <select v-model="form.gender" class="w-full px-4 py-2 border rounded-lg focus:outline-none bg-white">
                      <option value="" disabled>Select</option>
                      <option value="mr">Mr.</option>
                      <option value="mrs">Mrs.</option>
                    </select>
                  </div>
                </div>

                <!-- Password -->
                <div>
                  <label class="block text-gray-700 font-semibold mb-1">Password</label>
                  <input v-model="form.password" type="password" class="w-full px-4 py-2 border rounded-lg" placeholder="••••••••" />
                </div>

                <!-- Inline Error -->
                <p v-if="error" class="text-red-600 text-sm text-center font-medium bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                  {{ error }}
                </p>

                <!-- Submit Button -->
                <button
                  @click="handleRegister"
                  :disabled="loading"
                  class="w-full font-bold py-3 rounded-lg mt-2 transition-all hover:opacity-90 disabled:opacity-60"
                  style="background-color: #FF579A; color: #F9FAFB;"
                >
                  <span v-if="loading">Processing Registration...</span>
                  <span v-else>Register as {{ form.role.charAt(0).toUpperCase() + form.role.slice(1) }}</span>
                </button>

                <div class="text-center mt-4">
                  <router-link to="/login" class="text-sm font-semibold" style="color: #0E8028;">
                    Already have an account? Login here
                  </router-link>
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
import { useNotificationStore } from '@/stores/notification'

export default {
  name: 'UnifiedRegister',
  setup() {
    const notificationStore = useNotificationStore()
    return { notificationStore }
  },
  data() {
    return {
      form: {
        role: 'student',
        username: '',
        id_number: '',
        first_name: '',
        mi: '',
        last_name: '',
        email: '',
        gender: '',
        password: ''
      },
      loading: false,
      error: null
    }
  },
  computed: {
    backgroundStyle() {
      return { backgroundImage: `url(${bgImage})` }
    }
  },
  methods: {
    async handleRegister() {
      // Clear previous error
      this.error = null

      // ---- Validate all required fields ----
      if (!this.form.username.trim()) {
        this.error = 'Username is required.'
        return
      }
      if (!this.form.id_number.trim()) {
        this.error = `${this.form.role === 'student' ? 'Student' : 'Instructor'} ID is required.`
        return
      }
      if (!this.form.first_name.trim() || !this.form.last_name.trim()) {
        this.error = 'First name and last name are required.'
        return
      }
      if (!this.form.email.trim()) {
        this.error = 'Email is required.'
        return
      }
      if (!this.form.password.trim()) {
        this.error = 'Password is required.'
        return
      }

      this.loading = true

      try {
        await authService.register(this.form)

        this.notificationStore.success('Account created successfully! Redirecting to login...')
        setTimeout(() => {
          this.$router.push('/login')
        }, 1500)

      } catch (err) {
        console.error('Registration error:', err)
        console.error('Response data:', err.response?.data)
        console.error('Response status:', err.response?.status)

        let msg
        if (!err.response) {
          // Network error - backend not running or CORS issue
          msg = 'Cannot connect to server. Please make sure the server is running.'
        } else {
          // Try multiple error formats from Django/DRF
          const data = err.response.data
          msg = data?.error
            || data?.detail
            || data?.non_field_errors?.[0]
            || data?.username?.[0]
            || data?.email?.[0]
            || data?.id_number?.[0]
            || (typeof data === 'string' ? data : null)
            || `Registration failed (${err.response.status}). Please try again.`
        }

        this.error = msg
        this.notificationStore.error(msg)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>