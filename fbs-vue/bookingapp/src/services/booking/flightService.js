import api from './api';

export default {
  getSchedules(params) {
    return api.get('flightapp/api/schedules/', { params });
  },

  getSeatClassFeatures() {
    return api.get('flightapp/seat-class-features/');
  },
  getPricePrediction(flightData) {
    return api.post('flightapp/api/predict-price/', flightData);
  }
};