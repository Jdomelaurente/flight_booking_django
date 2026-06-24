// Booking API - scoped to flightapp endpoints
// Re-exports the centralized axios instance from services/api/axios.js
// All booking services should prefix their URLs with 'flightapp/' when calling the API.
//
// Example: api.get('flightapp/schedules/')
//
// This module exists for backward compatibility with existing service imports.
import api from '@/services/api/axios';

export default api;