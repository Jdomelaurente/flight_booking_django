import { defineStore } from 'pinia';

export const useModalStore = defineStore('modal', {
    state: () => ({
        isOpen: false,
        type: 'confirm', // 'confirm', 'alert', 'custom'
        title: '',
        message: '',
        confirmText: 'Confirm',
        cancelText: 'Cancel',
        variant: 'standard', // 'standard', 'danger'
        isLoading: false,
        loadingText: '',
        resolvePromise: null,
    }),

    actions: {
        /**
         * Show a confirmation modal
         * @param {Object} options - { title, message, confirmText, cancelText }
         * @returns {Promise<boolean>}
         */
        confirm(options = {}) {
            this.isOpen = true;
            this.type = 'confirm';
            this.title = options.title || 'Confirm Action';
            this.message = options.message || 'Are you sure you want to proceed?';
            this.confirmText = options.confirmText || 'Confirm';
            this.cancelText = options.cancelText || 'Cancel';
            this.variant = options.variant || 'standard';
            this.isLoading = false;
            this.loadingText = options.loadingText || '';

            return new Promise((resolve) => {
                this.resolvePromise = resolve;
            });
        },

        setLoader(status, text = '') {
            this.isLoading = status;
            if (text) this.loadingText = text;
        },

        /**
         * Close the modal and resolve with a value
         * @param {any} value 
         */
        close(value = false) {
            this.isOpen = false;
            if (this.resolvePromise) {
                this.resolvePromise(value);
                this.resolvePromise = null;
            }
        }
    }
});
