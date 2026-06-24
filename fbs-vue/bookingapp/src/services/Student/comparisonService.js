import api from '../api/axios';
import { bookingService } from '../booking/bookingService';

export const comparisonService = {
    /**
     * Fetches full activity details and the confirmed booking associated with it.
     * @param {number} activityId 
     * @param {number|null} bookingId - Optional: direct ID of the confirmed booking to skip search
     * @returns {Promise<{activity: object, booking: object|null}>}
     */
    async getComparisonData(activityId, bookingId = null) {
        try {
            // 1. Fetch full activity details
            const activityRes = await api.get(`api/student/activities/${activityId}/details/`);
            const activity = activityRes.data?.activity || null;

            // 2. Get the confirmed booking
            let booking = null;
            let targetBookingId = bookingId;

            // If bookingId wasn't provided, we have to search for it
            if (!targetBookingId) {
                const bookingRes = await api.get(`flightapp/api/bookings/?activity=${activityId}&status=Confirmed`);
                const bookings = bookingRes.data?.results || bookingRes.data;
                if (bookings && bookings.length > 0) {
                    targetBookingId = bookings[0].id;
                }
            }

            // 3. Fetch full details for the booking if we have an ID
            if (targetBookingId) {
                const fullBooking = await bookingService.getBookingDetails(targetBookingId);
                booking = fullBooking.booking;
            }

            return {
                success: true,
                activity,
                booking
            };
        } catch (error) {
            console.error("Error in comparisonService.getComparisonData:", error);
            throw error;
        }
    }
};
