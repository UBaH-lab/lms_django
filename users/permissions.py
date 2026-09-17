from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """Проверяет, состоит ли пользователь в группе модераторов."""
    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(BasePermission):
    """Проверяет, является ли пользователь владельцем объекта."""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsNotModerator(BasePermission):
    """Проверяет, что пользователь НЕ модератор."""
    def has_permission(self, request, view):
        return not request.user.groups.filter(name='moderators').exists()


class IsModeratorOrOwner(BasePermission):
    """Модератор ИЛИ владелец объекта."""
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='moderators').exists():
            return True
        return obj.owner == request.user
