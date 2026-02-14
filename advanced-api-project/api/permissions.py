from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        # This assumes the model has an 'owner' field
        return obj.owner == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    Read-only access is granted to everyone.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff


class CanManageBooks(permissions.BasePermission):
    """
    Custom permission specifically for managing books.
    Allows authenticated users to create books,
    but only staff members can update or delete.
    """
    
    def has_permission(self, request, view):
        # Allow read access to everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow authenticated users to create books
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
        
        # Require staff status for updates and deletes
        return request.user and request.user.is_staff
