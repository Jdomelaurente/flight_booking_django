<template>
  <div class="min-h-screen bg-cover bg-center bg-no-repeat flex flex-col font-sans" :style="backgroundStyle">
    <div class="min-h-screen bg-black/40 flex flex-col backdrop-blur-[2px]">
      <main class="flex-grow flex items-center justify-center p-4">
        <div class="w-full max-w-md bg-white/95 backdrop-blur-md p-8 rounded-sm shadow-2xl transition-all duration-500 overflow-hidden relative">
          
          <!-- Progress Indicator -->
          <div class="flex justify-center gap-2 mb-8">
            <div v-for="i in 3" :key="i" 
                 :class="[step >= i ? 'bg-pink-500 w-8' : 'bg-gray-200 w-2']" 
                 class="h-1 rounded-full transition-all duration-500">
            </div>
          </div>

          <!-- STEP 1: Enter Email -->
          <div v-if="step === 1" class="animate-slide-in">
            <div class="text-center mb-8">
              <h3 class="text-2xl font-black text-gray-900 mb-2 uppercase tracking-tighter">Find Account</h3>
              <p class="text-gray-500 text-[11px] font-bold uppercase tracking-wider">Step 1: Enter your registered email</p>
            </div>

            <form @submit.prevent="handleRequestOTP" class="space-y-6">
              <div class="space-y-2">
                <label class="block text-gray-800 font-bold text-[10px] uppercase tracking-widest ml-1">Email Address</label>
                <div class="relative">
                  <i class="ph ph-envelope absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"></i>
                  <input 
                    v-model="email" 
                    type="email" 
                    required
                    class="w-full pl-11 pr-5 py-3 bg-gray-50 border border-gray-200 rounded-md focus:outline-none focus:border-pink-400 focus:bg-white transition-all duration-300 font-medium text-sm"
                    placeholder="example@fbs.com"
                  />
                </div>
              </div>

              <button 
                type="submit" 
                :disabled="loading"
                class="w-full font-bold py-3.5 rounded-md text-white bg-pink-500 hover:bg-pink-600 cursor-pointer transition-all duration-300 active:scale-[0.98] disabled:opacity-70 shadow-lg shadow-pink-500/20"
              >
                {{ loading ? 'SEARCHING...' : 'CONTINUE' }}
              </button>
            </form>
          </div>

          <!-- STEP 2: Enter OTP -->
          <div v-if="step === 2" class="animate-slide-in">
            <div class="text-center mb-8">
              <div class="w-16 h-16 bg-pink-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <i class="ph ph-shield-check text-pink-500 text-3xl"></i>
              </div>
              <h3 class="text-2xl font-black text-gray-900 mb-2 uppercase tracking-tighter">Security Check</h3>
              <p class="text-gray-500 text-[11px] font-bold uppercase tracking-wider">Step 2: Enter the 6-digit code sent to</p>
              <p class="text-pink-500 text-[12px] font-black">{{ email }}</p>
            </div>

            <form @submit.prevent="verifyCode" class="space-y-6">
              <div class="flex justify-center gap-2 py-4">
                <input 
                  v-model="otp" 
                  type="text" 
                  maxlength="6"
                  required
                  autofocus
                  class="w-full max-w-[240px] text-center text-4xl tracking-[0.3em] font-black px-4 py-4 bg-gray-50 border-2 border-dashed border-gray-200 rounded-xl focus:outline-none focus:border-pink-500 focus:bg-white transition-all text-pink-600"
                  placeholder="000000"
                />
              </div>

              <button 
                type="submit" 
                class="w-full font-bold py-3.5 rounded-md text-white bg-pink-500 hover:bg-pink-600 cursor-pointer transition-all duration-300 active:scale-[0.98] shadow-lg shadow-pink-500/20"
              >
                VERIFY CODE
              </button>

              <p @click="step = 1" class="text-center text-[10px] text-gray-400 font-bold uppercase cursor-pointer hover:text-pink-500 transition-colors tracking-widest">
                Wrong email? Back to start
              </p>
            </form>
          </div>

          <!-- STEP 3: New Password -->
          <div v-if="step === 3" class="animate-slide-in">
            <div class="text-center mb-8">
              <h3 class="text-2xl font-black text-gray-900 mb-2 uppercase tracking-tighter">Secure Account</h3>
              <p class="text-gray-500 text-[11px] font-bold uppercase tracking-wider">Step 3: Create your new password</p>
            </div>

            <form @submit.prevent="handleResetPassword" class="space-y-5">
              <div class="space-y-4">
                <div class="space-y-1.5">
                  <label class="block text-gray-800 font-bold text-[10px] uppercase tracking-widest ml-1 text-gray-400">New Password</label>
                  <input v-model="newPassword" type="password" required class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-md focus:outline-none focus:border-pink-400 text-sm font-bold">
                </div>
                <div class="space-y-1.5">
                  <label class="block text-gray-800 font-bold text-[10px] uppercase tracking-widest ml-1 text-gray-400">Confirm Password</label>
                  <input v-model="rePassword" type="password" required class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-md focus:outline-none focus:border-pink-400 text-sm font-bold">
                </div>
              </div>

              <button 
                type="submit" 
                :disabled="loading"
                class="w-full font-bold py-3.5 rounded-md text-white bg-pink-500 hover:bg-pink-600 cursor-pointer transition-all duration-300 active:scale-[0.98] disabled:opacity-70 shadow-lg shadow-pink-500/20"
              >
                {{ loading ? 'SAVING...' : 'UPDATE PASSWORD' }}
              </button>
            </form>
          </div>

          <div class="text-center mt-10 pt-6 border-t border-gray-50">
             <router-link to="/login" class="text-[10px] font-bold text-gray-400 hover:text-pink-500 transition-colors uppercase tracking-[0.2em]">
               Return to Login
             </router-link>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api/axios'
import bgImage from '@/assets/image/bg-cthm.svg'
import { useNotificationStore } from '@/stores/notification'

const router = useRouter()
const notificationStore = useNotificationStore()

const step = ref(1)
const email = ref('')
const otp = ref('')
const newPassword = ref('')
const rePassword = ref('')
const loading = ref(false)

const backgroundStyle = {
  backgroundImage: `url(${bgImage})`
}

const handleRequestOTP = async () => {
  loading.value = true
  try {
    await api.post('api/auth/otp/request/', { email: email.value })
    notificationStore.success('A 6-digit code has been sent to your email.')
    step.value = 2
  } catch (err) {
    notificationStore.error(err.response?.data?.error || 'Account not found or error sending code.')
  } finally {
    loading.value = false
  }
}

const verifyCode = () => {
  if (otp.value.length !== 6) {
    notificationStore.warn('Please enter the full 6-digit code.')
    return
  }
  // We proceed to step 3. The actual server verification happens on the final save.
  step.value = 3
}

const handleResetPassword = async () => {
  if (newPassword.value !== rePassword.value) {
    notificationStore.error("Passwords do not match")
    return
  }
  if (newPassword.value.length < 8) {
    notificationStore.warn("Password must be at least 8 characters.")
    return
  }

  loading.value = true
  try {
    await api.post('api/auth/otp/reset/', {
      email: email.value,
      otp: otp.value,
      new_password: newPassword.value
    })
    notificationStore.success('Success! Your password has been updated.')
    setTimeout(() => router.push('/login'), 2000)
  } catch (err) {
    notificationStore.error(err.response?.data?.error || 'Invalid code or session expired. Please try again.')
    if (err.response?.status === 400) {
        step.value = 2 // Go back to OTP if it failed
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.animate-slide-in {
  animation: slideIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes slideIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

/* Glassmorphism focus */
input:focus {
  box-shadow: 0 0 20px rgba(236, 72, 153, 0.1);
}
</style>
