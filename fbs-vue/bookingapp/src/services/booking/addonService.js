import api from './api';

export const addonService = {
  // Pass airlineId to filter results on the server
  async getBaggageOptions(airlineId) {
    try {
      const response = await api.get('flightapp/api/baggage-options/', { params: { airline: airlineId } });
      const data = response.data?.results || response.data || [];

      // If we get an empty array or just want to enforce PH realism:
      if (data.length === 0) {
        return {
          data: [
            { id: 901, weight: 20, formatted_weight: "20kg Baggage", price: 850.00 },
            { id: 902, weight: 32, formatted_weight: "32kg Baggage", price: 1400.00 },
            { id: 903, weight: 40, formatted_weight: "40kg Baggage", price: 2100.00 }
          ]
        };
      }
      return response;
    } catch (e) {
      // Fallback for realistic PH tiers if the API fails
      return {
        data: [
          { id: 901, weight: 20, formatted_weight: "20kg Baggage", price: 850.00 },
          { id: 902, weight: 32, formatted_weight: "32kg Baggage", price: 1400.00 },
          { id: 903, weight: 40, formatted_weight: "40kg Baggage", price: 2100.00 }
        ]
      };
    }
  },
  getMealOptions(airlineId) {
    return api.get('flightapp/api/meal-options/', { params: { airline: airlineId } });
  },
  getAssistanceServices(airlineId) {
    return api.get('flightapp/api/assistance-services/', { params: { airline: airlineId } });
  }
};