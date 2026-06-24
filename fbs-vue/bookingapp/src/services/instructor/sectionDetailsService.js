import api from '../api/axios';

export const sectionDetailsService = {
    /**
     * GET: Fetch data for a specific section
     * URL format: /api/instructor/sections/5/
     */
    async getSectionDetails(sectionId) {
        try {
            const response = await api.get(`api/instructor/sections/${sectionId}/`);
            return response.data;
        } catch (error) {
            throw error;
        }
    }
};
