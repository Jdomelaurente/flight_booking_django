import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api', // Match your Django URL
  headers: {
    'Content-Type': 'application/json'
  }
});

// Automatically add the Token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('adminToken'); // Assuming you save it here on login
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export default api;