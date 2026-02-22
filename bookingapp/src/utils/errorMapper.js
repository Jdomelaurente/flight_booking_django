/**
 * Utility to map technical API errors to user-friendly messages.
 * Handles string errors, nested validation objects (DRF style), and specific endpoint context.
 */

const fieldLabels = {
    firstName: 'First Name',
    lastName: 'Last Name',
    middleName: 'Middle Name',
    dateOfBirth: 'Date of Birth',
    passport_number: 'Passport Number',
    email: 'Email',
    phone: 'Phone Number',
    nationality: 'Nationality',
    title: 'Title',
    gender: 'Gender',
    travel_doc_type: 'Document Type',
    non_field_errors: 'Validation Error'
};

/**
 * Recursively flattens nested error objects into readable strings
 */
const flattenErrors = (obj) => {
    const messages = [];

    const extract = (data) => {
        if (typeof data === 'string') {
            messages.push(data);
        } else if (Array.isArray(data)) {
            data.forEach(item => extract(item));
        } else if (typeof data === 'object' && data !== null) {
            Object.entries(data).forEach(([key, value]) => {
                const label = fieldLabels[key] || key;

                if (Array.isArray(value) && typeof value[0] === 'string') {
                    messages.push(`${label}: ${value[0]}`);
                } else if (typeof value === 'object') {
                    extract(value);
                } else {
                    messages.push(`${label}: ${value}`);
                }
            });
        }
    };

    extract(obj);
    return messages.length > 0 ? messages.join('\n') : null;
};

export const getFriendlyErrorMessage = (error) => {
    if (!error.response) {
        return 'Network connection lost. Please check your internet or if the server is running.';
    }

    const { status, data, config } = error.response;
    const url = config?.url || '';

    // Context-specific overrides
    if (url.includes('seats') && status === 400) {
        return "We couldn't verify your seat selection. The seat map might have changed. Refreshing layout...";
    }

    if (url.includes('create-booking') && status === 400) {
        return "We couldn't finalize your booking. Please review your passenger details for any missing or invalid information.";
    }

    // Handle common status codes
    switch (status) {
        case 400:
            const flattened = flattenErrors(data);
            return flattened || data.error || data.message || 'Invalid request. Please check your input.';

        case 401:
            return 'Your session has expired. For your security, please log in again.';

        case 403:
            return 'Access denied. You do not have permission for this action.';

        case 404:
            return 'The requested information could not be found.';

        case 500:
            return 'Philippine Airlines servers are temporarily busy. Please try again in a few moments.';

        default:
            return data.error || data.message || `An unexpected error occurred (Status ${status}).`;
    }
};
