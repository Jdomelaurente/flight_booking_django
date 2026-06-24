import api from '../api/axios';

export const activityService = {
    createActivity: (sectionId, formData) => {
        return api.post(
            `api/instructor/sections/${sectionId}/activities/create/`,
            formData
        );
    },
    updateActivity: (sectionId, activityId, formData) => {
        return api.put(
            `api/instructor/sections/${sectionId}/activities/${activityId}/update/`,
            formData
        );
    }
};
