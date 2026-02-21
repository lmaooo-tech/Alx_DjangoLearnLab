from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """
    Permission to allow authors to edit/delete their own posts and comments,
    while allowing all users to read.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author
        return obj.author == request.user


class IsAuthor(BasePermission):
    """
    Permission to allow only the author to perform any action on posts and comments.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
