from rest_framework import permissions


class IsPersonalAccountOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.username == view.kwargs.get('username')
