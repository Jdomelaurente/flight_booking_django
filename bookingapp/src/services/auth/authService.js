import api from '../api/axios';

export const authService = {
    /**
     * Login user and store token
     * @param {string} username 
     * @param {string} password 
     * @returns {Promise<{token: string, user: object}>}
     */
    async login(username, password) {
        try {
            const response = await api.post('api/auth/login/', { username, password });
            const { token, user, role, dashboard_route } = response.data;

            localStorage.setItem('auth_token', token);
            localStorage.setItem('token', token); // For compatibility
            localStorage.setItem('user', JSON.stringify(user));
            localStorage.setItem('role', role);

            return { token, user, role, dashboard_route };
        } catch (error) {
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
        return api.get('api/me/');
    },

    /**
     * Logout user and clear local storage
     */
    logout() {
        localStorage.clear();
        // Redirect logic should stay in components or a dedicated router guard
    }
};
