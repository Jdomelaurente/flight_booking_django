import api from '@/services/api/axios';

class DcsService {
    /**
     * Get upcoming flights for the DCS Dashboard
     */
    async getFlights() {
        return await api.get('api/dcs/flights/');
    }

    /**
     * Get passenger manifest for a specific flight schedule
     * @param {number} scheduleId
     */
    async getManifest(scheduleId) {
        return await api.get(`api/dcs/manifest/${scheduleId}/`);
    }

    /**
     * Get details for a specific passenger
     * @param {number} bookingDetailId
     */
    async getPassengerDetails(bookingDetailId) {
        return await api.get(`api/dcs/passenger/${bookingDetailId}/`);
    }

    /**
     * Get all passengers on a PNR for a flight
     * @param {string} pnr 
     * @param {number} scheduleId 
     */
    async getPnrDetails(pnr, scheduleId) {
        return await api.get(`api/dcs/pnr/${pnr}/${scheduleId}/`);
    }

    /**
     * Process check-in for one or more passengers
     * @param {Array} passengers - Array of {booking_detail_id, actual_weight}
     */
    async processCheckin(passengers) {
        return await api.post('api/dcs/process-checkin/', {
            passengers: passengers
        });
    }

    /**
     * Scan a QR code value and look up the passenger on a given flight
     * @param {string} qrValue - The scanned QR code content (PNR or encoded string)
     * @param {number} scheduleId - The schedule/flight this counter is serving
     */
    async scanQr(qrValue, scheduleId) {
        return await api.post('api/dcs/scan-qr/', {
            qr_value: qrValue,
            schedule_id: scheduleId
        });
    }

    /**
     * Assign a seat to a passenger during DCS check-in
     * @param {number} bookingDetailId 
     * @param {number} seatId 
     */
    async assignSeat(bookingDetailId, seatId) {
        return await api.post('api/dcs/assign-seat/', {
            booking_detail_id: bookingDetailId,
            seat_id: seatId
        });
    }

    /**
     * Get available seats for a schedule
     * @param {number} scheduleId 
     */
    async getAvailableSeats(scheduleId) {
        return await api.get(`flightapp/api/seats/?schedule=${scheduleId}`);
    }
}

export const dcsService = new DcsService();

