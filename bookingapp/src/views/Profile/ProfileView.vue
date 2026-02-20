<template>
  <div class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-3xl mx-auto space-y-8">
      
      <!-- Header -->
      <div>
        <h2 class="text-3xl font-extrabold text-gray-900">Profile Settings</h2>
        <p class="mt-2 text-sm text-gray-600">
          Manage your account information and preferences.
        </p>
      </div>

      <div class="bg-white shadow rounded-lg overflow-hidden">
        <!-- Tabs -->
        <div class="border-b border-gray-200">
          <nav class="-mb-px flex">
            <button
              v-for="tab in currentTabs"
              :key="tab.name"
              @click="activeTab = tab.name"
              :class="[
                activeTab === tab.name
                  ? 'border-pink-500 text-pink-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                'w-1/2 py-4 px-1 text-center border-b-2 font-medium text-sm transition-colors'
              ]"
            >
              {{ tab.label }}
            </button>
          </nav>
        </div>

        <!-- Personal Details Tab -->
        <div v-if="activeTab === 'details'" class="p-6 space-y-6">
          
          <!-- Avatar Section -->
          <div class="flex items-center space-x-6">
            <div class="relative group">
              <div class="w-24 h-24 rounded-full overflow-hidden bg-gray-100 border-2 border-dashed border-gray-300 flex items-center justify-center">
                <img 
                  v-if="previewAvatar || form.avatar" 
                  :src="previewAvatar || form.avatar" 
                  alt="Avatar" 
                  class="w-full h-full object-cover"
                />
                <span v-else class="text-gray-400 text-2xl font-bold">
                  {{ initials }}
                </span>
                
                <!-- Upload Overlay -->
                <div 
                    class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                    @click="$refs.fileInput.click()"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                </div>
              </div>
              <input 
                type="file" 
                ref="fileInput" 
                class="hidden" 
                accept="image/*"
                @change="handleFileChange"
              />
            </div>
            <div>
              <h3 class="text-lg font-medium text-gray-900">Profile Photo</h3>
              <p class="text-sm text-gray-500">
                Click the image to upload a new one. JPG, GIF or PNG.
              </p>
            </div>
          </div>

          <!-- Form Fields -->
          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div class="sm:col-span-3">
              <label class="block text-sm font-medium text-gray-700">First name</label>
              <input 
                v-model="form.first_name" 
                type="text" 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-pink-500 focus:border-pink-500 sm:text-sm"
              />
            </div>

            <div class="sm:col-span-3">
              <label class="block text-sm font-medium text-gray-700">Last name</label>
              <input 
                v-model="form.last_name" 
                type="text" 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-pink-500 focus:border-pink-500 sm:text-sm"
              />
            </div>

            <div class="sm:col-span-6">
              <label class="block text-sm font-medium text-gray-700">Email address</label>
              <input 
                v-model="form.email" 
                type="email" 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-pink-500 focus:border-pink-500 sm:text-sm"
              />
            </div>

             <div class="sm:col-span-6">
              <label class="block text-sm font-medium text-gray-700">Username (Read Only)</label>
               <input 
                v-model="form.username" 
                type="text" 
                readonly
                class="mt-1 block w-full bg-gray-50 border border-gray-300 rounded-md shadow-sm py-2 px-3 text-gray-500 sm:text-sm cursor-not-allowed"
              />
            </div>
          </div>
          
           <div class="flex justify-end pt-4">
            <button
              @click="saveProfile"
              :disabled="loading"
              class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-pink-600 hover:bg-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-pink-500 disabled:opacity-50 transition-colors"
            >
              <span v-if="loading">Saving...</span>
              <span v-else>Save Changes</span>
            </button>
          </div>

        </div>

        <!-- Security Tab -->
        <div v-if="activeTab === 'security'" class="p-6 space-y-6">
            <div class="flex items-center space-x-3 mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-pink-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <h3 class="text-lg font-medium text-gray-900">Change Password</h3>
            </div>

            <div class="space-y-4 max-w-md">
                <div>
                    <label class="block text-sm font-medium text-gray-700">New Password</label>
                    <input 
                        v-model="passwordForm.newPassword" 
                        type="password" 
                        placeholder="••••••••"
                        class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-pink-500 focus:border-pink-500 sm:text-sm"
                    />
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700">Confirm New Password</label>
                    <input 
                        v-model="passwordForm.confirmPassword" 
                        type="password" 
                        placeholder="••••••••"
                        class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-pink-500 focus:border-pink-500 sm:text-sm"
                    />
                </div>

                <div class="bg-blue-50 p-4 rounded-md">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                            </svg>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm text-blue-700">
                                Changing your password will not log you out of your current session.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="flex justify-end pt-4">
                <button
                    @click="updatePassword"
                    :disabled="loading || !passwordForm.newPassword || !passwordForm.confirmPassword"
                    class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-pink-600 hover:bg-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-pink-500 disabled:opacity-50 transition-colors"
                >
                    <span v-if="loading">Updating...</span>
                    <span v-else>Update Password</span>
                </button>
            </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useNotificationStore } from '@/stores/notification'
import api from '@/services/api/axios' // Assuming you have an axios instance configuration
import axios from 'axios'

const notificationStore = useNotificationStore()

const activeTab = ref('details')
const loading = ref(false)
const previewAvatar = ref(null)
const selectedFile = ref(null)

const currentTabs = [
  { name: 'details', label: 'Personal Details' },
  { name: 'security', label: 'Security' },
]

const form = ref({
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  avatar: null
})

const passwordForm = ref({
    newPassword: '',
    confirmPassword: ''
})

const initials = computed(() => {
    const f = form.value.first_name?.charAt(0) || '';
    const l = form.value.last_name?.charAt(0) || '';
    return (f + l).toUpperCase();
})

const fetchProfile = async () => {
    loading.value = true
    try {
        // Fetch to our new endpoint
        const response = await api.get('api/profile/update/')
        const data = response.data
        
        form.value = {
            username: data.username,
            first_name: data.first_name,
            last_name: data.last_name,
            email: data.email,
            avatar: data.avatar
        }
    } catch (error) {
        console.error('Failed to load profile:', error)
        notificationStore.error('Failed to load profile data.')
    } finally {
        loading.value = false
    }
}

const handleFileChange = (event) => {
    const file = event.target.files[0]
    if (!file) return

    // Validation (Size < 2MB, Type Image)
    if (file.size > 2 * 1024 * 1024) {
        notificationStore.warn('Image size should be less than 2MB.')
        return
    }
    
    selectedFile.value = file
    
    // Create preview
    const reader = new FileReader()
    reader.onload = (e) => {
        previewAvatar.value = e.target.result
    }
    reader.readAsDataURL(file)
}

const saveProfile = async () => {
    loading.value = true
    try {
        const formData = new FormData()
        formData.append('first_name', form.value.first_name)
        formData.append('last_name', form.value.last_name)
        formData.append('email', form.value.email)
        
        if (selectedFile.value) {
            formData.append('avatar', selectedFile.value)
        }

        const response = await api.patch('api/profile/update/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
        
        // Update local state with response
        const data = response.data
         form.value = {
            username: data.username,
            first_name: data.first_name,
            last_name: data.last_name,
            email: data.email,
            avatar: data.avatar
        }
        
        // Reset file selection
        selectedFile.value = null
        previewAvatar.value = null
        
        notificationStore.success('Profile updated successfully!')
        
    } catch (error) {
        console.error('Update failed:', error)
        notificationStore.error('Failed to update profile. Please try again.')
    } finally {
        loading.value = false
    }
}

const updatePassword = async () => {
    if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
        notificationStore.error('Passwords do not match.')
        return
    }

    if (passwordForm.value.newPassword.length < 8) {
        notificationStore.warn('Password must be at least 8 characters long.')
        return
    }

    loading.value = true
    try {
        await api.patch('api/profile/update/', {
            new_password: passwordForm.value.newPassword
        })
        
        notificationStore.success('Password updated successfully!')
        passwordForm.value.newPassword = ''
        passwordForm.value.confirmPassword = ''
    } catch (error) {
        console.error('Password update failed:', error)
        notificationStore.error(error.response?.data?.error || 'Failed to update password.')
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchProfile()
})
</script>
