from rest_framework import permissions

class IsInstructor(permissions.BasePermission):
    """
    Custom permission to only allow instructors to access specific views.
    Checks both UserProfile role and current valid Session role.
    """

    def has_permission(self, request, view):
        # 1. Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Check UserProfile role
        try:
            if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'instructor':
                return False
        except Exception:
            return False

        # 3. Check Session role (if using MultiSessionTokenAuthentication)
        if hasattr(request, 'session_obj'):
            if request.session_obj.role != 'instructor':
                return False

        return True
