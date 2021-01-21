"""Contains custom DRF permissions classes for the workouts app
"""
from rest_framework import permissions
from workouts.models import Workout


class IsOwner(permissions.BasePermission):
    """Checks whether the requesting user is also the owner of the existing object"""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsOwnerOfWorkout(permissions.BasePermission):
    """Checks whether the requesting user is also the owner of the new or existing object"""

    def has_permission(self, request, view):
        if request.method == "POST":
            if request.data.get("workout"):
                workout_id = request.data["workout"].split("/")[-2]
                workout = Workout.objects.get(pk=workout_id)
                if workout:
                    return workout.owner == request.user
            return False

        return True

    def has_object_permission(self, request, view, obj):
        return obj.workout.owner == request.user


class IsCoachAndVisibleToCoach(permissions.BasePermission):
    """Checks whether the requesting user is the existing object's owner's coach
    and whether the object (workout) has a visibility of Public or Coach.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner.coach == request.user and (
            obj.visibility == "PU" or obj.visibility == "CO"
        )


class IsCoachOfWorkoutAndVisibleToCoach(permissions.BasePermission):
    """Checks whether the requesting user is the existing workout's owner's coach
    and whether the object has a visibility of Public or Coach.
    """

    def has_object_permission(self, request, view, obj):
        return obj.workout.owner.coach == request.user and (
            obj.workout.visibility == "PU" or obj.workout.visibility == "CO"
        )


class IsPublic(permissions.BasePermission):
    """Checks whether the object (workout) has visibility of Public."""

    def has_object_permission(self, request, view, obj):
        return obj.visibility == "PU"


class IsWorkoutPublic(permissions.BasePermission):
    """Checks whether the object's workout has visibility of Public."""

    def has_object_permission(self, request, view, obj):
        return obj.workout.visibility == "PU"


class IsReadOnly(permissions.BasePermission):
    """Checks whether the HTTP request verb is only for retrieving data (GET, HEAD, OPTIONS)"""

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS
