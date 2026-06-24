import apiClient from '@/services/booking/api';

export default {
    // fetch all airports
    getAirports() {
        return apiClient.get('flightapp/api/airports/');
    },

    // fetch a single airport by id
    getAirport(id) {
        return apiClient.get(`flightapp/api/airports/${id}`);
    },

    searchAirports(query) {
        // This matches the search filter we set up in Django
        return apiClient.get(`flightapp/api/airports/?search=${query}`);
    }


}