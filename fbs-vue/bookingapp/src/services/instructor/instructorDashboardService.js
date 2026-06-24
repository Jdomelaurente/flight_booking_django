import api from '../api/axios';

const BASE_URL = 'api/instructor/dashboard/';

export const instructorDashboardService = {
    // GET: Fetch all sections and instructor profile details
    async getDashboard() {
        try {
            const response = await api.get(BASE_URL);
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    // POST: Create a new academic section
    async createSection(payload) {
        try {
            const response = await api.post(BASE_URL, payload);
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    // DELETE: Remove a section by ID
    async deleteSection(id) {
        try {
            const response = await api.delete(`api/instructor/sections/${id}/update/`);
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    // GET: Fetch all instructor logs
    async getLogs() {
        try {
            const response = await api.get('api/instructor/logs/');
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    // POST: Log a report print action
    async logPrintReport(payload) {
        try {
            const response = await api.post('api/instructor/logs/print-report/', payload);
            return response.data;
        } catch (error) {
            // Silently fail logging if it fails, don't break main app
            console.warn('Logging failed:', error);
            return null;
        }
    },

    // GET: Fetch read notification IDs
    async getReadStatuses() {
        const response = await api.get('api/instructor/notifications/read-status/');
        return response.data;
    },

    // POST: Mark notifications as read in DB
    async markNotificationsRead(ids) {
        const response = await api.post('api/instructor/notifications/mark-read/', { notification_ids: ids });
        return response.data;
    }
};

