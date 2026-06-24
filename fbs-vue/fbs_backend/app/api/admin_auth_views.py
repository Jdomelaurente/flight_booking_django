from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from ..models import UserProfile

class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            user = authenticate(username=username, password=password)
            
            if user and user.is_staff:
                # Log the action
                from ..models import TrackLog
                TrackLog.objects.create(
                    user=user,
                    action=f"Admin Login: {user.username} successfully logged in to the dashboard."
                )

                # 1. Get or create DRF token (for legacy support)
                token, _ = Token.objects.get_or_create(user=user)
                
                # 2. Get UserProfile for role
                try:
                    profile = UserProfile.objects.get(user=user)
                    role = profile.role
                except UserProfile.DoesNotExist:
                    role = 'admin' # Fallback
                    
                # 3. Create a UserSession (Multi-session support)
                # from fbs_instructor.models import UserSession
                # from fbs_instructor.views import get_client_ip
                
                # session = UserSession.objects.create(
                #     user=user,
                #     session_token=UserSession.generate_token(),
                #     role=role,
                #     ip_address=get_client_ip(request),
                #     user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                #     is_active=True
                # )
                
                return Response({
                    'success': True,
                    'token': token.key, # Fallback to DRF token
                    'session_id': None,
                    'role': role,
                    'dashboard_route': '/admin/dashboard',
                    'user': {
                        'username': user.username,
                        'email': user.email
                    }
                }, status=status.HTTP_200_OK)
                
            return Response({
                'success': False, 
                'message': 'Invalid admin credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'message': f'Server Error: {str(e)}',
                'traceback': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
