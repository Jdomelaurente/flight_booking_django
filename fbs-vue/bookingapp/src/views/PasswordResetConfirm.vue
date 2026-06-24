<template>
  <div class="min-h-screen bg-cover bg-center bg-no-repeat flex flex-col font-sans" :style="backgroundStyle">
    <div class="min-h-screen bg-black/40 flex flex-col backdrop-blur-[2px]">
      <main class="flex-grow flex items-center justify-center p-4">
        <div class="w-full max-w-md bg-white/95 backdrop-blur-md p-8 rounded-sm shadow-2xl animate-fade-in-up">
          <div class="text-center mb-8">
            <h3 class="text-2xl font-black text-gray-900 mb-2">Create New Password</h3>
            <p class="text-gray-500 text-xs font-medium">Please enter and confirm your new password below.</p>
          </div>

          <form @submit.prevent="handleResetConfirm" class="space-y-6">
            <div class="space-y-4">
              <div class="space-y-1.5">
                <label class="block text-gray-800 font-bold text-xs uppercase tracking-widest ml-1">New Password</label>
                <input 
                  v-model="newPassword" 
                  type="password" 
                  required
                  class="w-full px-5 py-2.5 bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:border-rose-400 focus:bg-white transition-all duration-300 font-medium"
                  placeholder="••••••••"
                />
              </div>

              <div class="space-y-1.5">
                <label class="block text-gray-800 font-bold text-xs uppercase tracking-widest ml-1">Confirm Password</label>
                <input 
                  v-model="reNewPassword" 
                  type="password" 
                  required
                  class="w-full px-5 py-2.5 bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:border-rose-400 focus:bg-white transition-all duration-300 font-medium"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button 
              type="submit" 
              :disabled="loading"
              class="w-full font-bold py-3 rounded-md text-white bg-pink-500 hover:bg-pink-600 cursor-pointer transition-all duration-300 active:scale-[0.98] disabled:opacity-70"
            >
              {{ loading ? 'UPDATING...' : 'RESET PASSWORD' }}
            </button>
          </form>

          <div class="text-center mt-8">
            <p v-if="error" class="text-red-500 text-[10px] font-bold uppercase mb-4">{{ error }}</p>
            <router-link to="/login" class="text-xs font-bold text-rose-500 hover:text-rose-600 transition-colors uppercase tracking-widest">
              ← Back to Login
            </router-link>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api/axios'
import bgImage from '@/assets/image/bg-cthm.svg'
import { useNotificationStore } from '@/stores/notification'

const route = useRoute()
const router = useRouter()
const notificationStore = useNotificationStore()

const newPassword = ref('')
const reNewPassword = ref('')
const loading = ref(false)
const error = ref('')

const backgroundStyle = {
  backgroundImage: `url(${bgImage})`
}

const handleResetConfirm = async () => {
  if (newPassword.value !== reNewPassword.value) {
    error.value = "Passwords do not match"
    return
  }

  loading.value = true
  error.value = ""

  try {
    await api.post('api/auth/users/reset_password_confirm/', {
      uid: route.params.uid,
      token: route.params.token,
      new_password: newPassword.value,
      re_new_password: reNewPassword.value
    })

    notificationStore.success('Password reset successful! You can now login.')
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    console.error(err)
    error.value = "Invalid or expired link. Please request a new one."
    notificationStore.error('Reset failed. The link may have expired.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
