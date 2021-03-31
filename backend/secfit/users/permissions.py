from rest_framework import permissions
from django.contrib.auth import get_user_model


class IsCurrentUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user

class IsPostOrIsAuthenticated(permissions.BasePermission):        
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        
        return request.user and request.user.is_authenticated


class IsAthlete(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            if request.data.get("athlete"):
                athlete_id = request.data["athlete"].split("/")[-2]
                return athlete_id == request.user.id
            return False

        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.athlete


class IsCoach(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            if request.data.get("athlete"):
                athlete_id = request.data["athlete"].split("/")[-2]
                athlete = get_user_model().objects.get(pk=athlete_id)
                return athlete.coach == request.user
            return False

        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.athlete.coach


class IsOfferOwnerOrRecipient(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.user == obj.recipient


class IsOfferRecipient(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.recipient


class IsOfferOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner


class TwoFactorNotEnabled(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return true
