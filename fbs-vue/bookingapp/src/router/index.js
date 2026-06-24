import { createRouter, createWebHistory, RouterView } from 'vue-router';
import { useBookingStore } from '@/stores/booking';
import { useNotificationStore } from '@/stores/notification';
import { useUserStore } from '@/stores/user';
import AuthStorage from '@/utils/authStorage';

// 1. Import your new admin routes file
import adminRoutes from './admin';

// Booking Views
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
// import Base_login from '@/views/Login.vue';
// import Register from '@/views/Register.vue';

// Instructor Views
import InstructorDashboard from '@/views/Instructor/instructor_dashboard.vue';
import Activity_details from '@/views/Instructor/Activity/Activity_details.vue';
import InstructorStudentScore from '@/views/Instructor/Activity/instructor_students_score.vue';

// Student Views
import StudentLayout from '@/views/Student/StudentLayout.vue';
import StudentDashboard from '@/views/Student/Student_dashboard.vue';
import StudentActivityDetails from '@/views/Student/Activities/Student_activity_details.vue'

// DCS Views
import DcsLayout from '@/views/dcs/DcsLayout.vue';
import FlightDashboardView from '@/views/dcs/FlightDashboardView.vue';
import ManifestView from '@/views/dcs/ManifestView.vue';
import CheckinCounterView from '@/views/dcs/CheckinCounterView.vue';

const routes = [
  // 3. Use the Spread Operator (...) to include all admin routes
  ...adminRoutes,

  {
    path: '/login',
    name: 'instructor_login',
    component: () => import('@/views/Login.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/ForgotPassword.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/set-password',
    name: 'SetPassword',
    component: () => import('@/views/SetPassword.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/instructor',
    component: () => import('@/views/Instructor/InstructorLayout.vue'),
    meta: { requiresAuth: true, role: 'instructor' },
    children: [
      {
        path: 'dashboard',
        name: 'instructor_dashboard',
        component: InstructorDashboard
      },
      {
        path: 'section/:id',
        name: 'SectionDetails',
        component: () => import('@/views/Instructor/Section_details.vue')
      },
      {
        path: 'section/:id/student',
        name: 'SectionStudent',
        component: () => import('@/views/Instructor/Section_student_list.vue')
      },
      {
        path: 'section/:id/settings',
        name: 'CourseSettings',
        component: () => import('@/views/Instructor/Course_settings.vue')
      },
      {
        path: 'activity/:activityId',
        name: 'ActivityDetails',
        component: Activity_details
      },
      {
        path: 'activity/:activityId/student/:studentId/score',
        name: 'InstructorStudentScore',
        component: InstructorStudentScore
      },
      {
        path: 'activity/:activityId/toplist',
        name: 'ActivityToplist',
        component: () => import('@/views/Instructor/Activity/Activity_toplist.vue')
      },
      {
        path: 'logs',
        name: 'InstructorLogs',
        component: () => import('@/views/Instructor/Activity/instructor_logs.vue')
      },
      {
        path: 'sections',
        name: 'InstructorSectionList',
        component: () => import('@/views/Instructor/instructor_section_list.vue')
      },
      {
        path: 'activities',
        name: 'InstructorActivitiesList',
        component: () => import('@/views/Instructor/instructor_activities_list.vue')
      },
      {
        path: 'students',
        name: 'InstructorStudentList',
        component: () => import('@/views/Instructor/Instructor_student_list_sidebar.vue')
      },
      {
        path: 'reports',
        name: 'InstructorReports',
        component: () => import('@/views/Instructor/instructor_reports.vue')
      },
      {
        path: 'profile',
        name: 'InstructorProfile',
        component: ProfileView
      }
    ]
  },
  {
    path: '/profile',
    redirect: (to) => {
      const userRole = AuthStorage.getRole()
      if (userRole === 'instructor') return '/instructor/profile'
      return '/student/dashboard'
    }
  },
  {
    path: '/student',
    component: RouterView,
    meta: { requiresAuth: true, role: 'student', layout: 'StudentLayout' },
    children: [
      {
        path: 'dashboard',
        name: 'StudentDashboard',
        component: StudentDashboard
      },
      {
        path: 'home',
        name: 'StudentHome',
        component: () => import('@/views/Student/Home.vue')
      },
      {
        path: 'calendar',
        name: 'StudentCalendar',
        component: () => import('@/views/Student/Calendar.vue')
      },
      {
        path: 'activity/:id',
        name: 'StudentActivityDetails',
        component: StudentActivityDetails,
        props: true
      },
      {
        path: 'activity/:activityId/analysis',
        name: 'StudentAssessmentAnalysis',
        component: () => import('@/views/Student/Activities/Student_assessment_analysis.vue')
      },
      {
        path: 'booking-registry',
        name: 'StudentBookingRegistry',
        component: () => import('@/views/Student/Operations/BookingRegistry.vue'),
        meta: { title: 'DCS | Booking Registry' }
      },
      {
        path: 'checkin-registry',
        name: 'StudentCheckinRegistry',
        component: () => import('@/views/Student/Operations/CheckinRegistry.vue'),
        meta: { title: 'DCS | Check-in Registry' }
      },
      {
        path: 'leaderboard',
        name: 'StudentLeaderboard',
        component: () => import('@/views/Student/StudentLeaderboard.vue'),
        meta: { title: 'Section Leaderboard' }
      },
    ]
  },
  {
    path: '/airbus-321',
    name: 'Airbus321',
    component: AirbusA321Layout
  },
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: {
      layout: 'BookingLayout',
      title: 'Book a Flight | Philippine Airlines',
      requiresAuth: true,
      isBookingProtected: true // Needs activity code check
    }
  },
  {
    path: '/check-in',
    name: 'check-in',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true },
    component: () => import('../views/booking/CheckInView.vue')
  },
  {
    path: '/status',
    name: 'status',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true },
    component: () => import('../views/booking/FlightStatusView.vue')
  },
  {
    path: '/flights/search',
    name: 'SearchResults',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true },
    component: SearchResults
  },
  {
    path: '/booking/passengers',
    name: 'PassengerDetails',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true, requireActiveBookingSession: true },
    component: PassengerDetails
  },
  {
    path: '/addons',
    name: 'Addons',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true, requireActiveBookingSession: true },
    component: AddonsView
  },
  {
    path: '/addons/seats',
    name: 'SeatSelection',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true, requireActiveBookingSession: true },
    component: SeatSelection
  },
  {
    path: '/review/booking',
    name: 'ReviewBooking',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true, requireActiveBookingSession: true },
    component: ReviewBooking
  },
  {
    path: '/payment',
    name: 'Payment',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true, requireActiveBookingSession: true },
    component: Payment
  },
  {
    path: '/payment-callback',
    name: 'PaymentCallback',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true },
    component: () => import('../views/booking/PaymentCallbackView.vue')
  },
  {
    path: '/booking-success',
    name: 'BookingSuccess',
    meta: { layout: 'BookingLayout', requiresAuth: true, isBookingProtected: true },
    component: () => import('@/views/booking/BookingSuccessView.vue')
  },
  {
    path: '/dcs',
    component: DcsLayout,
    meta: { requiresAuth: true, role: 'student' },
    children: [
      {
        path: 'dashboard',
        name: 'DcsDashboard',
        component: FlightDashboardView,
        meta: { title: 'DCS | Flight Dashboard' }
      },
      {
        path: 'manifest/:schedule_id',
        name: 'DcsManifest',
        component: ManifestView,
        meta: { title: 'DCS | Passenger Manifest' },
        props: true
      },
      {
        path: 'checkin/:booking_detail_id',
        name: 'DcsCheckin',
        component: CheckinCounterView,
        meta: { title: 'DCS | Check-in Counter' },
        props: true
      },
      {
        path: 'airline-checkin',
        name: 'DcsAirlineCheckin',
        component: () => import('@/views/booking/CheckInView.vue'),
        meta: { title: 'DCS | Airline Check-in' }
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

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

  const token = AuthStorage.getToken();
  const userRole = AuthStorage.getRole();
  // Full check: requires token + sessionId + role to be a valid active session
  const isFullyAuthenticated = AuthStorage.isAuthenticated();

  console.log('🛡️ Router Guard:', to.path);
  console.log('🔑 Token exists:', !!token);
  console.log('✅ Fully authenticated:', isFullyAuthenticated);
  console.log('🔒 Requires Auth:', to.meta.requiresAuth);

  // 1. Guest Only Routes (Login/Register)
  if (to.matched.some(record => record.meta.guestOnly)) {
    // Only redirect if there's a REAL active session (token + sessionId + role)
    if (isFullyAuthenticated) {
      console.log('👤 Authenticated user attempting to visit guest route - Redirecting...');
      if (userRole === 'instructor') {
        return next('/instructor/dashboard');
      } else if (userRole === 'student') {
        return next('/student/dashboard');
      } else {
        // Admin or unknown roles: clear stale session and let them through
        AuthStorage.clearCurrentSession();
        return next();
      }
    }
    // No valid session — allow access to login/register
    return next();
  }


  // 2. Requires Authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      console.log('❌ No token - Redirecting to login');
      return next('/login');
    }

    // Role-based Route Protection
    if (to.meta.role && userRole) {
      const allowedRoles = Array.isArray(to.meta.role) ? to.meta.role : [to.meta.role];
      if (!allowedRoles.includes(userRole)) {
        console.warn(`⛔ User role '${userRole}' blocked from accessing '${to.meta.role}' route`);
        notificationStore.error('You do not have permission to access that page.');
        
        if (userRole === 'instructor') {
          return next('/instructor/dashboard');
        } else if (userRole === 'student') {
          return next('/student/dashboard');
        } else if (['lms_admin', 'flight_admin', 'superadmin'].includes(userRole)) {
          return next('/admin/dashboard');
        } else {
          return next('/login');
        }
      }
    }

    // Additional Check: Instructors cannot access booking flow
    if (to.meta.isBookingProtected && userRole === 'instructor') {
      console.warn('⛔ Instructor attempted to access booking flow:', to.path);
      return next('/instructor/dashboard');
    }

    // Additional Check: Non-enrolled students cannot access booking flow
    const userStore = useUserStore();
    if (to.meta.isBookingProtected && userRole === 'student' && !userStore.isEnrolled) {
      console.warn('⛔ Non-enrolled student attempted to access booking flow:', to.path);
      notificationStore.error('You are not enrolled in any section. Please contact your administrator.');
      return next('/student/dashboard');
    }
  }

  // 3. Booking Protection (Activity Code / Practice Mode)
  if (to.matched.some(record => record.meta.isBookingProtected)) {
    if (!bookingStore.hasActivityCodeValidation) {
      console.log('❌ Authenticated user without activity code in booking area');
      // Only students use the booking flow; redirect others appropriately
      if (userRole === 'instructor') {
        return next('/instructor/dashboard');
      } else if (userRole === 'student') {
        notificationStore.info('Please enter an activity code or select practice mode to start booking.');
        return next('/student/dashboard');
      } else {
        // Admin or unknown: no booking flow access
        return next('/login');
      }
    }
  }

  // 4. Strict Activity Mode Protection: Only allow booking-related pages
  if (bookingStore.hasActivityCodeValidation && !to.matched.some(record => record.meta.isBookingProtected)) {
    console.log('⚠️ Activity mode active - Blocking navigation to non-booking page:', to.path);
    notificationStore.warn('You are currently in an active activity session. Please complete or end your session before navigating elsewhere.');
    return next('/');
  }

  // 5. Active Booking Session Expiry Check
  if (to.matched.some(record => record.meta.requireActiveBookingSession)) {
    if (!bookingStore.sessionExpiry || Date.now() > bookingStore.sessionExpiry) {
      notificationStore.error("Your booking session has expired or hasn't started. Please start a new search.");
      bookingStore.resetBooking();
      return next('/');
    }
  }

  next();
});

export default router;
