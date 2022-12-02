from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions




class IsAdminOrReadOnly(permissions.BasePermission):
    """
    The request is admin as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and
            request.user.is_staff
        )


class IsPostWriterOrReadOnly(permissions.BasePermission):
    """
    The request is writer as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_staff:
            return True
        elif (request.user != AnonymousUser()) and (request.user.member.is_writer):
            return True    
        return False


    def has_object_permission(self, request, view, obj):
        if obj.writer.user_id == request.user.id:
            return True
        else:
            return False

class IsWriterOrReadOnly(permissions.BasePermission):
    """
    The request is writer as a user, or is a read-only request.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif (request.user != AnonymousUser()) and (request.user.member.is_writer):
            return True    
        return False


