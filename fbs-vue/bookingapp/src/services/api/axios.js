import axios from 'axios';
import { useNotificationStore } from '@/stores/notification';
import AuthStorage from '@/utils/authStorage';
import { getFriendlyErrorMessage } from '@/utils/errorMapper';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/', // Use env variable with fallback
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

// Request Interceptor: Attach Auth Token
api.interceptors.request.use(
    (config) => {
        // Do not attach token for authentication endpoints
        if (config.url && (config.url.includes('auth/login') || config.url.includes('admin/login') || config.url.includes('auth/register') || config.url.includes('auth/otp') || config.url.includes('auth/set-password'))) {
            return config;
        }

        const token = AuthStorage.getToken();
        if (token) {
            config.headers.Authorization = `Token ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response Interceptor: Global Error Handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Skip global error handling for authentication and specific data endpoints
        // because those components handle their own error feedback.
        if (error.config && error.config.url && (
            error.config.url.includes('auth/login') ||
            error.config.url.includes('admin/login') ||
            error.config.url.includes('auth/register') ||
            error.config.url.includes('auth/otp') ||
            error.config.url.includes('auth/set-password') ||
            error.config.url.includes('student/dashboard')
        )) {
            return Promise.reject(error);
        }

        const notificationStore = useNotificationStore();

        // Use utility to get a friendly message
        const message = getFriendlyErrorMessage(error);
        const type = 'error';

        // Check if the request wants to skip the global toast
        if (!error.config.skipGlobalToast) {
            notificationStore.addNotification({ message, type });
        }

        // Special handling for 401: clear session
        if (error.response && error.response.status === 401) {
            AuthStorage.clearCurrentSession();
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }

        return Promise.reject(error);
    }
);

export default api;
