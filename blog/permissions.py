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


class IsAdminOrOwnUserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool( (request.method == "POST") or (request.user and request.user.is_authenticated) )
    
    def has_object_permission(self, request, view, obj):
        return bool( (request.user.is_staff) or (obj == request.user) ) 


class IsUserOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):       
        return obj == request.user


class IsMemberOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):       
        return obj.user_id == request.user.id


class NotAllowAny(permissions.BasePermission):
    def has_permission(self, request, view):
        return False
            

class IsAdminOrOwnMemberOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        return bool( (request.user.is_staff) or (obj == request.user.member) ) 
  

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


