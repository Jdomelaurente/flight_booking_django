import api from '../api/axios';
import AuthStorage from '@/utils/authStorage';

export const authService = {
    /**
     * Login user and store token
     * @param {string} username 
     * @param {string} password 
     * @returns {Promise<{token: string, user: object, role: string, dashboard_route: string}>}
     */
    async login(username, password) {
        try {
            // 1. Get Token and User Data from Custom Login Endpoint
            const response = await api.post('api/auth/login/', { username, password });
            const data = response.data;
            const token = data.token;
            const session_id = data.session_id;

            if (!token) {
                throw new Error('No token received from server');
            }

            const user = data.user;
            const role = data.role;
            const dashboard_route = data.dashboard_route || '/';

            // 2. Clear old state and Initialize New Session using AuthStorage
            AuthStorage.clearCurrentSession();
            AuthStorage.initializeSession({
                token,
                session_id,
                role,
                user,
                dashboard_route
            });

            // Fallback for legacy components reading from localStorage directly without AuthStorage
            localStorage.setItem('token', token);
            localStorage.setItem('auth_token', token);
            localStorage.setItem('user', JSON.stringify(user));
            localStorage.setItem('role', role);

            return { token, user, role, dashboard_route };
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    },

    /**
     * Register a new user
     * @param {object} formData 
     * @returns {Promise}
     */
    register(formData) {
        return api.post('api/auth/register/', formData);
    },

    /**
     * Get current user profile (re-fetch data)
     * @returns {Promise<object>}
     */
    async getUserProfile() {
        return api.get('api/auth/users/me/');
    },

    /**
     * Logout user and clear local storage
     */
    logout() {
        localStorage.clear();
        // Redirect logic should stay in components or a dedicated router guard
    }
};
