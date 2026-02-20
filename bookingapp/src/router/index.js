import { createRouter, createWebHistory } from 'vue-router';
import { useBookingStore } from '@/stores/booking';
import { useNotificationStore } from '@/stores/notification';

<<<<<<< HEAD
// 1. Import your new admin routes file
import adminRoutes from './admin';

// 2. Booking Views (Keep these or move them to a booking.js later)
=======
// Booking Views
>>>>>>> origin/criss
import HomeView from '@/views/booking/HomeView.vue';
import SearchResults from '@/views/booking/SearchResultsView.vue';
import PassengerDetails from '@/views/booking/PassengerDetailsView.vue';
import AddonsView from '@/views/booking/AddonsView.vue';
import SeatSelection from '@/views/booking/SeatSelectionView.vue';
import ProfileView from '@/views/Profile/ProfileView.vue';
import ReviewBooking from '@/views/booking/ReviewBookingView.vue';
import Payment from '@/views/booking/PaymentView.vue';
import AirbusA321Layout from '@/components/seatmaps/AirbusA321Layout.vue';

// Authentication Views
import Base_login from '@/views/Login.vue';
import Register from '@/views/Register.vue';

// Instructor Views
import InstructorDashboard from '@/views/Instructor/instructor_dashboard.vue';
import Activity_details from '@/views/Instructor/Activity/Activity_details.vue';

// Student Views
import StudentDashboard from '@/views/Student/Student_dashboard.vue';
import StudentActivityDetails from '@/views/Student/Activities/Student_activity_details.vue'

const routes = [
<<<<<<< HEAD
  // 3. Use the Spread Operator (...) to include all admin routes
  ...adminRoutes,

  // --- Booking Routes (The main site) ---
=======
  {
    path: '/login',
    name: 'instructor_login',
    component: Base_login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/instructor/dashboard',
    name: 'instructor_dashboard',
    component: InstructorDashboard,
    meta: { requiresAuth: true, role: 'instructor' }
  },
  {
    path: '/instructor/section/:id',
    name: 'SectionDetails',
    component: () => import('@/views/Instructor/Section_details.vue'),
    meta: { requiresAuth: true, role: 'instructor' }
  },
  {
    path: '/instructor/section/:id/people',
    name: 'SectionPeople',
    component: () => import('@/views/Instructor/Section_student_list.vue'),
    meta: { requiresAuth: true, role: 'instructor' }
  },
  {
    path: '/instructor/activity/:activityId',
    name: 'ActivityDetails',
    component: Activity_details,
    meta: { requiresAuth: true, role: 'instructor' }
  },
  {
    path: '/student/dashboard',
    name: 'StudentDashboard',
    component: StudentDashboard,
    meta: { requiresAuth: true, role: 'student' }
  },
  // ✅ FIXED: Added /student/ prefix to match navigation in Student_dashboard.vue
  {
    path: '/student/activity/:id',
    name: 'StudentActivityDetails',
    component: StudentActivityDetails,
    meta: {
      requiresAuth: true,
      role: 'student'
    },
    props: true
  },
  {
    path: '/airbus-321',
    name: 'Airbus321',
    component: AirbusA321Layout
  },
>>>>>>> origin/criss
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: {
      layout: 'BookingLayout',
      title: 'Book a Flight | Philippine Airlines',
      requiresAuth: true
    }
  },
  {
    path: '/airbus-321',
    name: 'Airbus321',
    component: AirbusA321Layout
  },
  {
    path: '/check-in',
    name: 'check-in',
<<<<<<< HEAD
=======
    meta: { layout: 'BookingLayout' },
>>>>>>> origin/criss
    component: () => import('../views/booking/CheckInView.vue')
  },
  {
    path: '/status',
    name: 'status',
    meta: { layout: 'BookingLayout' },
    component: () => import('../views/booking/FlightStatusView.vue')
  },
  {
    path: '/flights/search',
    name: 'SearchResults',
    meta: { layout: 'BookingLayout' },
    component: SearchResults
  },
  {
    path: '/booking/passengers',
    name: 'PassengerDetails',
    meta: { layout: 'BookingLayout' },
    component: PassengerDetails
  },
  {
    path: '/addons',
    name: 'Addons',
    meta: { layout: 'BookingLayout' },
    component: AddonsView
  },
  {
    path: '/addons/seats',
    name: 'SeatSelection',
    meta: { layout: 'BookingLayout' },
    component: SeatSelection
  },
  {
    path: '/review/booking',
    name: 'ReviewBooking',
    meta: { layout: 'BookingLayout' },
    component: ReviewBooking
  },
  {
    path: '/payment',
    name: 'Payment',
    meta: { layout: 'BookingLayout' },
    component: Payment
  },
  {
    path: '/payment-callback',
    name: 'PaymentCallback',
<<<<<<< HEAD
    component: () => import('../views/booking/PaymentCallbackView.vue'),
    meta: { requiresAuth: false }
=======
    meta: { layout: 'BookingLayout' },
    component: () => import('../views/booking/PaymentCallbackView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/booking-success',
    name: 'BookingSuccess',
    meta: { layout: 'BookingLayout' },
    component: () => import('@/views/booking/BookingSuccessView.vue')
>>>>>>> origin/criss
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

<<<<<<< HEAD
// Keep your router.beforeEach logic here...
router.beforeEach((to, from, next) => {
  const bookingStore = useBookingStore();
  document.title = to.meta.title || 'Philippine Airlines';

  const bookingRoutes = ['PassengerDetails', 'Addons', 'SeatSelection', 'ReviewBooking', 'Payment'];
  if (bookingRoutes.includes(to.name)) {
    if (!bookingStore.sessionExpiry || Date.now() > bookingStore.sessionExpiry) {
      alert("Your booking session has expired. Please start a new search.");
      bookingStore.resetBooking();
      return next('/');
    }
  }

  if (to.meta.requiresAuth && to.meta.role === 'admin') {
    const isAdminLoggedIn = !!localStorage.getItem('adminLoggedIn');
    if (!isAdminLoggedIn) {
      return next('/admin/login'); // Matches the login path in admin.js
=======
// ==========================================
// NAVIGATION GUARD
// ==========================================
router.beforeEach((to, from, next) => {
  const bookingStore = useBookingStore();
  const notificationStore = useNotificationStore();

  // Set page title
  if (to.meta.title) {
    document.title = to.meta.title;
  }

  // Check for authentication token
  const token = localStorage.getItem('token') || localStorage.getItem('auth_token');

  console.log('🛡️ Router Guard:', to.path);
  console.log('🔑 Token exists:', !!token);
  console.log('🔒 Requires Auth:', to.meta.requiresAuth);

  // REDIRECT AUTHENTICATED USERS AWAY FROM LOGIN/REGISTER
  if ((to.name === 'instructor_login' || to.name === 'Register') && token) {
    console.log('👤 Authenticated user attempting to visit login/register - Redirecting...');
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'instructor') {
        return next('/instructor/dashboard');
      } else {
        return next('/student/dashboard');
      }
    } catch (e) {
      console.error('Error parsing user data for redirect:', e);
      return next('/'); // Fallback
    }
  }

  // Authentication Check
  if (to.meta.requiresAuth) {
    if (!token) {
      console.log('❌ No token - Redirecting to login');
      return next('/login');
    }

    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      console.log('👤 User role:', user.role);

      // STRICT INSTRUCTOR RESTRICTION
      if (user.role === 'instructor') {
        const allowedRoutes = ['instructor_dashboard', 'SectionDetails', 'SectionPeople', 'ActivityDetails'];
        const isAllowedPath = to.path.startsWith('/instructor/');

        if (!isAllowedPath && !allowedRoutes.includes(to.name)) {
          console.warn('⛔ Instructor attempted to access restricted page:', to.path);
          return next('/instructor/dashboard');
        }
      }

      // STRICT STUDENT RESTRICTION
      if (user.role === 'student') {
        // Prevent access to ANY instructor routes
        if (to.path.startsWith('/instructor/')) {
          console.warn('⛔ Student attempted to access instructor page:', to.path);
          return next('/student/dashboard');
        }
      }

      // Optional: Check role if specified
      if (to.meta.role && user.role && user.role !== to.meta.role) {
        console.log('⚠️ Role mismatch - but allowing (backend will block if needed)');
      }
    } catch (e) {
      console.error('Error parsing user data:', e);
    }
  }

  // Activity Code / Practice Mode Check
  // Protect ALL booking routes - require activity code or practice mode selection
  // Only login and register pages are unprotected
  const protectedBookingRoutes = [
    'Home',                 // Home page with flight search
    'check-in',            // Check-in page
    'status',              // Flight status page
    'SearchResults',       // Search results
    'PassengerDetails',    // Passenger details form
    'Addons',              // Add-ons selection
    'SeatSelection',       // Seat selection
    'ReviewBooking',       // Review booking
    'Payment',             // Payment page
    'PaymentCallback',     // Payment callback
    'BookingSuccess'       // Booking success page
  ];

  if (protectedBookingRoutes.includes(to.name)) {
    if (!bookingStore.hasActivityCodeValidation) {
      console.log('❌ No activity code validation - Checking authentication status');

      // Check if user is authenticated
      if (!token) {
        console.log('❌ User not authenticated - Redirecting to login');
        notificationStore.warn('Please log in to access the booking system.');
        return next('/login');
      }

      // User is authenticated but hasn't validated activity code or selected practice mode
      console.log('❌ Authenticated user without activity code - Redirecting to student dashboard');
      notificationStore.info('Please enter an activity code or select practice mode from your dashboard to start booking.');
      return next('/student/dashboard');
    }
  }

  // PREVENT ACCESS TO STUDENT PAGES DURING ACTIVE SESSION
  if (to.path.startsWith('/student/') && bookingStore.hasActivityCodeValidation) {
    // Exception: Allow access to activity details even during active session
    // This allows students to check instructions while booking
    if (to.name === 'StudentActivityDetails') {
      return next();
    }

    console.log('⚠️ Active session detected - Blocking student page access');
    notificationStore.warn('You have an active booking or practice session. Please end your activity session before returning to the dashboard.');
    return next('/');
  }

  // Booking flow session check
  const bookingRoutes = [
    'PassengerDetails',
    'Addons',
    'SeatSelection',
    'ReviewBooking',
    'Payment'
  ];

  if (bookingRoutes.includes(to.name)) {
    if (!bookingStore.sessionExpiry || Date.now() > bookingStore.sessionExpiry) {
      notificationStore.error("Your booking session has expired or hasn't started. Please start a new search.");
      bookingStore.resetBooking();
      return next('/');
>>>>>>> origin/criss
    }
  }

  next();
});

export default router;