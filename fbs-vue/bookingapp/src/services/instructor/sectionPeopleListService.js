import api from '../api/axios';

export const sectionPeopleListService = {
    async getEnrolledStudents(sectionId) {
        const response = await api.get(`api/instructor/sections/${sectionId}/students/`);
        return response.data;
    },
    async unenrollStudent(sectionId, studentId) {
        const response = await api.delete(`api/instructor/sections/${sectionId}/enroll/${studentId}/`);
        return response.data;
    },
    async bulkEnrollStudents(sectionId, file) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post(`api/instructor/sections/${sectionId}/bulk-enroll/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    },
    async clearEnrolledStudents(sectionId) {
        const response = await api.delete(`api/instructor/sections/${sectionId}/clear-enrollments/`);
        return response.data;
    }
};
