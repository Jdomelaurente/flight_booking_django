<template>
  <div class="min-h-screen bg-cover bg-center bg-no-repeat flex flex-col font-sans" :style="backgroundStyle">
    <div class="min-h-screen bg-black/40 flex flex-col backdrop-blur-[2px]">
      <main class="flex-grow flex items-center justify-center p-4">
        <div class="w-full max-w-md bg-white/95 backdrop-blur-md p-8 rounded-sm shadow-2xl transition-all duration-500 overflow-hidden relative">
          
          <div v-if="!token" class="text-center animate-slide-in">
            <div class="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="ph ph-warning-circle text-3xl text-red-500"></i>
            </div>
            <h3 class="text-2xl font-black text-gray-900 mb-2 uppercase tracking-tighter">Invalid Link</h3>
            <p class="text-gray-500 text-sm mb-6">This password setup link is invalid or expired.</p>
            <router-link to="/login" class="text-pink-500 font-bold hover:text-pink-600 text-sm">
              Go to Login
            </router-link>
          </div>

          <div v-else-if="success" class="text-center animate-slide-in">
            <div class="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="ph ph-check-circle text-3xl text-green-500"></i>
            </div>
            <h3 class="text-2xl font-black text-gray-900 mb-2 uppercase tracking-tighter">Password Set!</h3>
            <p class="text-gray-500 text-sm mb-6">Your password has been set up successfully. You can now log in.</p>
            <router-link to="/login" class="inline-block bg-pink-500 text-white px-8 py-3 rounded-md font-bold hover:bg-pink-600 transition-all">
              Go to Login
            </router-link>
          </div>

          <div v-else class="animate-slide-in">
            <div class="text-center mb-8">
              <div class="w-16 h-16 bg-pink-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <i class="ph ph-key text-3xl text-pink-500"></i>
              </div>
              <h3 class="text-2xl font-black text-gray-900 mb-2 uppercase tracking-tighter">Set Your Password</h3>
              <p class="text-gray-500 text-[11px] font-bold uppercase tracking-wider">Create a strong password for your account</p>
            </div>

            <form @submit.prevent="handleSetPassword" class="space-y-6">
              <div class="space-y-2">
                <label class="block text-gray-800 font-bold text-[10px] uppercase tracking-widest ml-1">New Password</label>
                <div class="relative">
                  <i class="ph ph-lock absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"></i>
                  <input 
                    v-model="newPassword" 
                    type="password" 
                    required
                    minlength="8"
                    class="w-full pl-11 pr-5 py-3 bg-gray-50 border border-gray-200 rounded-md focus:outline-none focus:border-pink-400 focus:bg-white transition-all duration-300 font-medium text-sm"
                    placeholder="At least 8 characters"
                  />
                </div>
              </div>

              <div class="space-y-2">
                <label class="block text-gray-800 font-bold text-[10px] uppercase tracking-widest ml-1">Confirm Password</label>
                <div class="relative">
                  <i class="ph ph-lock-simple absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"></i>
                  <input 
                    v-model="confirmPassword" 
                    type="password" 
                    required
                    minlength="8"
                    class="w-full pl-11 pr-5 py-3 bg-gray-50 border border-gray-200 rounded-md focus:outline-none focus:border-pink-400 focus:bg-white transition-all duration-300 font-medium text-sm"
                    placeholder="Repeat your password"
                  />
                </div>
              </div>

              <p v-if="errorMsg" class="text-red-500 text-xs font-bold text-center">{{ errorMsg }}</p>

              <button 
                type="submit" 
                :disabled="loading"
                class="w-full font-bold py-3.5 rounded-md text-white bg-pink-500 hover:bg-pink-600 cursor-pointer transition-all duration-300 active:scale-[0.98] disabled:opacity-70 shadow-lg shadow-pink-500/20"
              >
                {{ loading ? 'SETTING UP...' : 'SET PASSWORD' }}
              </button>
            </form>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api/axios'
import bgImage from '@/assets/image/bg-cthm.svg'
import { useNotificationStore } from '@/stores/notification'

const route = useRoute()
const router = useRouter()
const notificationStore = useNotificationStore()

const token = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const success = ref(false)
const errorMsg = ref('')

const backgroundStyle = {
  backgroundImage: `url(${bgImage})`
}

onMounted(() => {
  token.value = route.query.token || ''
})

const handleSetPassword = async () => {
  errorMsg.value = ''

  if (!token.value) {
    errorMsg.value = 'Invalid setup link.'
    return
  }

  if (newPassword.value.length < 8) {
    errorMsg.value = 'Password must be at least 8 characters.'
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    errorMsg.value = 'Passwords do not match.'
    return
  }

  loading.value = true
  try {
    await api.post('api/auth/set-password/', {
      token: token.value,
      new_password: newPassword.value
    })
    success.value = true
    notificationStore.success('Password set up successfully!')
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to set password. The link may have expired.'
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
input:focus {
  box-shadow: 0 0 20px rgba(236, 72, 153, 0.1);
}
</style>
