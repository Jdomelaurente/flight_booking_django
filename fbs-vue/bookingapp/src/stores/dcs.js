import { defineStore } from 'pinia';
import { dcsService } from '@/services/api/dcsService';

export const useDcsStore = defineStore('dcs', {
    state: () => ({
        flights: [],
        selectedSchedule: null,
        manifest: [],
        isLoading: false,
        error: null,
        activeAirline: null, // Track which airline the DCS agent is currently operating under
    }),

    getters: {
        totalPassengers: (state) => state.manifest.length,
        checkedInPassengers: (state) => state.manifest.filter(p => p.status === 'checkin' || p.status === 'boarding').length,
        pendingPassengers: (state) => state.manifest.filter(p => p.status === 'confirmed' || p.status === 'pending').length,
    },

    actions: {
        async fetchFlights() {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await dcsService.getFlights();
                // Bug fix: defensively handle both array response and {flights:[]} shaped response
                this.flights = Array.isArray(response.data) ? response.data : (response.data?.flights || []);
            } catch (err) {
                this.error = 'Failed to fetch departing flights';
                console.error(err);
            } finally {
                this.isLoading = false;
            }
        },

        async fetchManifest(scheduleId) {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await dcsService.getManifest(scheduleId);
                this.manifest = response.data.manifest;
                this.selectedSchedule = response.data.flight;
            } catch (err) {
                this.error = 'Failed to fetch passenger manifest';
                console.error(err);
            } finally {
                this.isLoading = false;
            }
        },

        async processCheckin(passengers) {
            this.isLoading = true;
            this.error = null;
            try {
                await dcsService.processCheckin(passengers);

                // Update local manifest state for each checked-in passenger
                passengers.forEach(pData => {
                    const passenger = this.manifest.find(p => p.booking_detail_id === pData.booking_detail_id);
                    if (passenger) {
                        passenger.status = 'checkin';
                        if (pData.seat_number) passenger.seat = pData.seat_number;
                    }
                });

                return true;
            } catch (err) {
                this.error = 'Failed to process check-in';
                console.error(err);
                // Bug fix: re-throw so calling code's catch block is reached
                throw err;
            } finally {
                this.isLoading = false;
            }
        },

        clearSelection() {
            this.selectedSchedule = null;
            this.manifest = [];
        },

        setActiveAirline(airline) {
            this.activeAirline = airline;
        }
    }
});
