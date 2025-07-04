from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permission check for admin role.
    Admins have full access to everything.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_admin()


class IsMaintainer(permissions.BasePermission):
    """
    Permission check for maintainer role.
    Maintainers have access to manage issues but not users.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_maintainer()


class IsReporter(permissions.BasePermission):
    """
    Permission check for reporter role.
    Reporters can only create and view issues.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_reporter()


class IsOwnerOrMaintainer(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object or maintainers to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if user is maintainer or admin (they can edit anything)
        if hasattr(request.user, 'profile') and request.user.profile.is_maintainer():
            return True
            
        # Check if object has a user field that matches the request user
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        # Check if object has a created_by field that matches the request user
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
            
        return False
