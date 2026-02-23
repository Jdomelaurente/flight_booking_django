import api from '../api/axios';

export const studentDashboardService = {
    /**
     * Get student dashboard data
     * URL: GET /api/student/dashboard/data/
     */
    getStudentDashboard() {
        return api.get('api/student/dashboard/data/');
    },

    /**
     * Get specific section details
     * URL: GET /api/student/section/{id}/
     */
    getSectionDetails(sectionId) {
        return api.get(`api/student/section/${sectionId}/`);
    },

    /**
     * Get specific activity details
     * URL: GET /api/student/activity/{id}/
     */
    getActivityDetails(activityId) {
        return api.get(`api/student/activity/${activityId}/`);
    },

    /**
     * Get practice bookings for the student
     * URL: GET /api/student/practice-bookings/
     */
    getPracticeBookings() {
        return api.get('api/student/practice-bookings/');
    },

    /**
     * Submit activity work
     * URL: POST /api/student/activity/{id}/submit/
     */
    submitActivity(activityId, data) {
        return api.post(`api/student/activity/${activityId}/submit/`, data);
    }
};
