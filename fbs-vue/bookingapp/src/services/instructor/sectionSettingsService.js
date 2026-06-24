import api from '@/services/api/axios';

export const sectionSettingsService = {
    updateSectionSettings(sectionId, data) {
        return api.patch(`api/instructor/sections/${sectionId}/update/`, data);
    }
};
