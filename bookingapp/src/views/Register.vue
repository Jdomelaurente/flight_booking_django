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
                <div>
                  <label class="block text-gray-700 font-semibold mb-1">I am a:</label>
                  <select v-model="form.role" class="w-full px-4 py-2 border rounded-lg focus:outline-none bg-white">
                    <option value="student">Student</option>
                    <option value="instructor">Instructor</option>
                  </select>
                </div>

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

                <div>
                  <label class="block text-gray-700 font-semibold mb-1">Email</label>
                  <input v-model="form.email" type="email" class="w-full px-4 py-2 border rounded-lg" placeholder="email@example.com" />
                </div>

                <div>
                  <label class="block text-gray-700 font-semibold mb-1">Password</label>
                  <input v-model="form.password" type="password" class="w-full px-4 py-2 border rounded-lg" placeholder="••••••••" />
                </div>

                <button @click="handleRegister" :disabled="loading" class="w-full font-bold py-3 rounded-lg mt-4 transition-all hover:opacity-90" style="background-color: #FF579A; color: #F9FAFB;">
                  <span v-if="loading">Processing Registration...</span>
                  <span v-else>Register as {{ form.role.charAt(0).toUpperCase() + form.role.slice(1) }}</span>
                </button>

                <p v-if="error" class="text-red-500 text-sm text-center mt-4 font-medium">{{ error }}</p>
                
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
      // Basic validation
      if (!this.form.username || !this.form.password || !this.form.id_number) {
        this.notificationStore.warn("Please fill in all required fields.");
        return;
      }

      this.loading = true;
      this.error = null;

      try {
        // This hits your fbs_instructor/views.py register_view
        await authService.register(this.form);
        
        this.notificationStore.success("Account Created Successfully! Redirecting to login...");
        setTimeout(() => {
             this.$router.push('/login');
        }, 1500);
       
      } catch (err) {
        // Capture the error from Django (e.g., "Username already taken")
        const msg = err.response?.data?.error || "Registration failed. Try a different username/ID.";
        this.notificationStore.error(msg);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>