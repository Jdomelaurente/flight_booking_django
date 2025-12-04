# bookingapp/middleware.py - Even safer version
from django.utils import timezone
from datetime import timedelta

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check session if user is authenticated
        # Use getattr with default to avoid AttributeError
        user = getattr(request, 'user', None)
        
        if user and user.is_authenticated:
            last_activity_str = request.session.get('last_activity')
            
            if last_activity_str:
                try:
                    last_activity = timezone.datetime.fromisoformat(last_activity_str)
                    timeout_duration = timedelta(hours=24)
                    
                    if timezone.now() - last_activity > timeout_duration:
                        from django.contrib.auth import logout
                        logout(request)
                        request.session.flush()
                except (ValueError, TypeError):
                    pass
            
            request.session['last_activity'] = str(timezone.now())
        
        response = self.get_response(request)
        return response


class StudentProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Safely get user attribute
        user = getattr(request, 'user', None)
        
        if user and user.is_authenticated:
            try:
                # Check if user has role attribute
                if hasattr(user, 'role') and user.role == 'student':
                    # Try to get student profile
                    if hasattr(user, 'student_profile'):
                        request.student = user.student_profile
                    else:
                        request.student = None
                else:
                    request.student = None
            except Exception:
                request.student = None
        else:
            request.student = None
        
        response = self.get_response(request)
        return response