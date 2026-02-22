# ============================================================================
# CREATE THIS FILE: authentication.py in your fbs_instructor app
# ============================================================================

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from .models import UserSession

class MultiSessionTokenAuthentication(BaseAuthentication):
    """
    Custom authentication class that supports multiple simultaneous sessions
    Each session has its own unique token
    """
    
    keyword = 'Token'
    
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        try:
            # Expected format: "Token <session_token>"
            parts = auth_header.split()
            
            if len(parts) != 2 or parts[0].lower() != 'token':
                return None
            
            token = parts[1]
            
            # Find the session
            try:
                session = UserSession.objects.select_related('user').get(
                    session_token=token,
                    is_active=True
                )
            except UserSession.DoesNotExist:
                # Not a MultiSession token; allow other authentication backends to try
                return None
            
            # Check if session is expired
            if session.is_expired():
                session.deactivate()
                raise AuthenticationFailed('Session has expired. Please login again.')
            
            # Refresh the session activity timestamp
            session.refresh()
            
            # Store session info in request for later use
            request.session_obj = session
            request.user_role = session.role
            
            return (session.user, session)
            
        except Exception as e:
            # If anything goes wrong here, fall back to other authenticators
            return None
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response.
        """
        return self.keyword
