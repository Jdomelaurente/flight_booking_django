// src/router/admin.js
const adminRoutes = [
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('@/views/admin/login.vue'),
    meta: { title: 'Admin Login' }
  },
  {
    path: '/admin',
    component: () => import('@/views/admin/adminlayout.vue'),
    meta: { requiresAuth: true, role: ['admin', 'lms_admin', 'flight_admin', 'superadmin'] },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/admindashboard.vue'),
        meta: { title: 'Dashboard' }
      },

      // --- Manage Flight ---
      {
        path: 'manage-flight/routes',
        name: 'ManageRoutes',
        component: () => import('@/views/admin/manage_flight/routes.vue'),
        meta: { title: 'Flight Routes', role: ['superadmin', 'flight_admin', 'admin'] }
      },
      {
        path: 'manage-flight/flights',
        name: 'ManageFlights',
        component: () => import('@/views/admin/manage_flight/flights.vue'),
        meta: { title: 'Flight Profiles', role: ['superadmin', 'flight_admin', 'admin'] }
      },
      {
        path: 'manage-flight/schedules',
        name: 'ManageSchedules',
        component: () => import('@/views/admin/manage_flight/schedules.vue'),
        meta: { title: 'Flight Schedules', role: ['superadmin', 'flight_admin', 'admin'] }
      },
      {
        path: 'manage-flight/seats',
        name: 'ManageSeats',
        component: () => import('@/views/admin/manage_flight/seats.vue'),
        meta: { title: 'Seat Maps', role: ['superadmin', 'flight_admin', 'admin'] }
      },
      {
        path: 'manage-flight/live-monitor',
        name: 'LiveMonitor',
        component: () => import('@/views/admin/manage_flight/live_monitor.vue'),
        meta: { title: 'Live Operations', role: ['superadmin', 'flight_admin', 'admin'] }
      },

      // --- Assets ---
      {
        path: 'assets/airports',
        name: 'AdminAirports',
        component: () => import('@/views/admin/assets/airports.vue'),
        meta: { title: 'Airports', role: ['superadmin', 'flight_admin', 'admin'] }
      },
      {
        path: 'assets/add-ons',
        name: 'AdminAddOns',
        component: () => import('@/views/admin/assets/addons.vue'),
        meta: { title: 'Add-ons', role: ['superadmin', 'flight_admin', 'admin'] }
      },
      {
        path: 'assets/seat-classes',
        name: 'AdminSeatClasses',
        component: () => import('@/views/admin/assets/seat_classes.vue'),
        meta: { title: 'Seat Classes', role: ['superadmin', 'flight_admin', 'admin'] }
      },
      {
        path: 'assets/airlines',
        name: 'AdminAirlines',
        component: () => import('@/views/admin/assets/airlines.vue'),
        meta: { title: 'Airlines' }
      },
      {
        path: 'assets/aircraft',
        name: 'AdminAircraft',
        component: () => import('@/views/admin/assets/aircraft.vue'),
        meta: { title: 'Aircraft' }
      },
      {
        path: 'assets/seat-requirements',
        name: 'AdminSeatRequirements',
        component: () => import('@/views/admin/assets/seat_requirements.vue'),
        meta: { title: 'Seat Requirements' }
      },

      // --- Booking ---
      {
        path: 'booking/details',
        name: 'AdminBookingDetails',
        component: () => import('@/views/admin/booking/details.vue'),
        meta: { title: 'Booking Details' }
      },
      {
        path: 'booking/list',
        name: 'AdminBookingsList',
        component: () => import('@/views/admin/booking/list.vue'),
        meta: { title: 'Bookings' }
      },
      {
        path: 'booking/payments',
        name: 'AdminPayments',
        component: () => import('@/views/admin/booking/payments.vue'),
        meta: { title: 'Payments', role: ['superadmin', 'flight_admin', 'admin'] }
      },

      // --- Passenger ---
      {
        path: 'passenger/list',
        name: 'AdminPassengerList',
        component: () => import('@/views/admin/passenger/list.vue'),
        meta: { title: 'Passengers' }
      },
      {
        path: 'passenger/check-ins',
        name: 'AdminCheckIns',
        component: () => import('@/views/admin/passenger/check_ins.vue'),
        meta: { title: 'Check-ins' }
      },

      // --- Student Info ---
      {
        path: 'student-info/list',
        name: 'AdminStudentList',
        component: () => import('@/views/admin/student_info/list.vue'),
        meta: { title: 'Students', role: ['superadmin', 'lms_admin', 'admin'] }
      },
      {
        path: 'student-info/track-log',
        name: 'AdminTrackLog',
        component: () => import('@/views/admin/student_info/track_log.vue'),
        meta: { title: 'Audit Logs', role: ['superadmin', 'lms_admin', 'admin'] }
      },
      {
        path: 'student-info/lms-overview',
        name: 'AdminLmsOverview',
        component: () => import('@/views/admin/student_info/lms_overview.vue'),
        meta: { title: 'LMS Overview', role: ['superadmin', 'lms_admin', 'admin'] }
      },

      // --- Instructor Info ---
      {
        path: 'instructor-info/list',
        name: 'AdminInstructorList',
        component: () => import('@/views/admin/instructor_info/list.vue'),
        meta: { title: 'Instructors', role: ['superadmin', 'lms_admin', 'admin'] }
      },

      // --- Manage Tax ---
      {
        path: 'manage-tax/airport-fee',
        name: 'AdminTaxAirportFee',
        component: () => import('@/views/admin/manage_tax/airport_fee.vue'),
        meta: { title: 'Airport Fee' }
      },
      {
        path: 'manage-tax/tax-type',
        name: 'AdminTaxType',
        component: () => import('@/views/admin/manage_tax/tax_type.vue'),
        meta: { title: 'Tax Types' }
      },
      {
        path: 'manage-tax/airline-tax',
        name: 'AdminAirlineTax',
        component: () => import('@/views/admin/manage_tax/airline_tax.vue'),
        meta: { title: 'Airline Tax' }
      },
      {
        path: 'manage-tax/travel-tax',
        name: 'AdminTravelTax',
        component: () => import('@/views/admin/manage_tax/travel_tax.vue'),
        meta: { title: 'Travel Tax', role: ['superadmin', 'flight_admin', 'admin'] }
      },
      {
        path: 'manage-tax/booking-tax',
        name: 'AdminBookingTax',
        component: () => import('@/views/admin/manage_tax/booking_tax.vue'),
        meta: { title: 'Booking Tax' }
      },

      // --- Countries ---
      {
        path: 'assets/countries',
        name: 'AdminCountries',
        component: () => import('@/views/admin/assets/countries.vue'),
        meta: { title: 'Countries' }
      },

      // --- Insurance ---
      {
        path: 'insurance/providers',
        name: 'AdminInsuranceProviders',
        component: () => import('@/views/admin/insurance/providers.vue'),
        meta: { title: 'Insurance Providers' }
      },
      {
        path: 'insurance/plans',
        name: 'AdminInsurancePlans',
        component: () => import('@/views/admin/insurance/plans.vue'),
        meta: { title: 'Insurance Plans' }
      },

      // --- Add-on Details ---
      {
        path: 'addons/meal-options',
        name: 'AdminMealOptions',
        component: () => import('@/views/admin/addons/meal_options.vue'),
        meta: { title: 'Meal Options' }
      },
      {
        path: 'addons/assistance',
        name: 'AdminAssistanceServices',
        component: () => import('@/views/admin/addons/assistance_services.vue'),
        meta: { title: 'Assistance Services' }
      },
      {
        path: 'addons/baggage',
        name: 'AdminBaggageOptions',
        component: () => import('@/views/admin/addons/baggage_options.vue'),
        meta: { title: 'Baggage Options' }
      },

      // --- Pricing Config ---
      {
        path: 'pricing-config',
        name: 'AdminPricingConfig',
        component: () => import('@/views/admin/pricing_config.vue'),
        meta: { title: 'Pricing Configuration', role: ['superadmin', 'flight_admin', 'admin'] }
      },
      {
        path: 'bulk-import',
        name: 'AdminBulkImport',
        component: () => import('@/views/admin/bulk_import.vue'),
        meta: { title: 'Bulk Data Import', role: ['superadmin', 'flight_admin', 'lms_admin', 'admin'] }
      }
    ]
  }
];

export default adminRoutes;
