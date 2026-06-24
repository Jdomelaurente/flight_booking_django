import api from '@/services/api/axios'

export async function adminLogin(username, password) {
  try {
    const response = await api.post(
      'api/admin/login/',
      { username, password }
    )
    return response.data
  } catch (error) {
    if (error.response && error.response.data) {
      return error.response.data
    }
    throw error
  }
}
