from rest_framework import permissions
from workouts.models import Workout


class IsCommentVisibleToUser(permissions.BasePermission):
    """
    Custom permission to only allow a comment to be viewed
    if one of the following holds:
    - The comment is on a public visibility workout
    - The comment was written by the user
    - The comment is on a coach visibility workout and the user is the workout owner's coach
    - The comment is on a workout owned by the user
    """

    def has_object_permission(self, request, view, obj):
        # Write permissions are only allowed to the owner.
        return (
            obj.workout.visibility == "PU"
            or obj.owner == request.user
            or (obj.workout.visibility == "CO" and obj.owner.coach == request.user)
            or obj.workout.owner == request.user
        )

class CanUserCommentOnWorkout(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            if request.data.get("workout"):
                workout_id = request.data["workout"].split("/")[-2]
                workout = Workout.objects.get(pk=workout_id)
                if workout:
                    return (
                        workout.visibility == "PU"
                        or (workout.visibility == "CO" and workout.owner.coach == request.user)
                        or workout.owner == request.user
                    )
            return False
        return True
