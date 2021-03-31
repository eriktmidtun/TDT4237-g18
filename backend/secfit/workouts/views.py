"""Contains views for the workouts application. These are mostly class-based views.
"""
from rest_framework import generics, mixins, views
from rest_framework import permissions

from rest_framework.parsers import (
    JSONParser,
)
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from django.db.models import Q
from rest_framework import filters
from workouts.parsers import MultipartJsonParser
from workouts.permissions import (
    IsOwner,
    IsCoachAndVisibleToCoach,
    IsOwnerOfWorkout,
    IsCoachOfWorkoutAndVisibleToCoach,
    IsReadOnly,
    IsPublic,
    IsWorkoutPublic,
    IsUserAllowedToViewWorkoutFile
)
from workouts.mixins import CreateListModelMixin
from workouts.models import Workout, Exercise, ExerciseInstance, WorkoutFile
from workouts.serializers import WorkoutSerializer, ExerciseSerializer
from workouts.serializers import ExerciseInstanceSerializer, WorkoutFileSerializer
from django.core.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
import json
from django.http import FileResponse, Http404
from django.conf import settings

@api_view(["GET"])
def api_root(request, format=None):
    return Response(
        {
            "users": reverse("user-list", request=request, format=format),
            "workouts": reverse("workout-list", request=request, format=format),
            "exercises": reverse("exercise-list", request=request, format=format),
            "exercise-instances": reverse(
                "exercise-instance-list", request=request, format=format
            ),
            "workout-files": reverse(
                "workout-file-list", request=request, format=format
            ),
            "comments": reverse("comment-list", request=request, format=format),
            "likes": reverse("like-list", request=request, format=format),
        }
    )

class WorkoutList(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    """Class defining the web response for the creation of a Workout, or displaying a list
    of Workouts

    HTTP methods: GET, POST
    """

    serializer_class = WorkoutSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]  # User must be authenticated to create/view workouts
    parser_classes = [
        MultipartJsonParser,
        JSONParser,
    ]  # For parsing JSON and Multi-part requests
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["name", "date", "owner__username"]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = Workout.objects.none()
        if self.request.user:
            # A workout should be visible to the requesting user if any of the following hold:
            # - The workout has public visibility
            # - The owner of the workout is the requesting user
            # - The workout has coach visibility and the requesting user is the owner's coach
            qs = Workout.objects.filter(
                Q(visibility="PU")
                | Q(owner=self.request.user)
                | (Q(visibility="CO") & Q(owner__coach=self.request.user))
            ).distinct()

        return qs


class WorkoutDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    """Class defining the web response for the details of an individual Workout.

    HTTP methods: GET, PUT, DELETE
    """

    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [
        permissions.IsAuthenticated
        & (IsOwner | (IsReadOnly & (IsCoachAndVisibleToCoach | IsPublic)))
    ]
    parser_classes = [MultipartJsonParser, JSONParser]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class WorkoutFileResponse(
    views.APIView
):
    permission_classes = [
        permissions.IsAuthenticated & IsUserAllowedToViewWorkoutFile
    ]

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        
        path = f'{settings.MEDIA_ROOT}/{obj.file}'
        return FileResponse(open(path, 'rb'))

    
    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        try:
            obj = WorkoutFile.objects.get(
                Q(workout=self.kwargs['workout_id']) & Q(file=f'workouts/{self.kwargs["workout_id"]}/{self.kwargs["filename"]}')
            )
        except:
            raise Http404("Media does not exist")

        self.check_object_permissions(self.request, obj)

        return obj

class ExerciseList(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    """Class defining the web response for the creation of an Exercise, or
    a list of Exercises.

    HTTP methods: GET, POST
    """

    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ExerciseDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    """Class defining the web response for the details of an individual Exercise.

    HTTP methods: GET, PUT, PATCH, DELETE
    """

    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ExerciseInstanceList(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    CreateListModelMixin,
    generics.GenericAPIView,
):
    """Class defining the web response for the creation"""

    serializer_class = ExerciseInstanceSerializer
    permission_classes = [permissions.IsAuthenticated & IsOwnerOfWorkout]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        qs = ExerciseInstance.objects.none()
        if self.request.user:
            qs = ExerciseInstance.objects.filter(
                Q(workout__owner=self.request.user)
                | (
                    (Q(workout__visibility="CO") | Q(workout__visibility="PU"))
                    & Q(workout__owner__coach=self.request.user)
                )
            ).distinct()

        return qs


class ExerciseInstanceDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    serializer_class = ExerciseInstanceSerializer
    permission_classes = [
        permissions.IsAuthenticated
        & (
            IsOwnerOfWorkout
            | (IsReadOnly & (IsCoachOfWorkoutAndVisibleToCoach | IsWorkoutPublic))
        )
    ]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class WorkoutFileList(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    CreateListModelMixin,
    generics.GenericAPIView,
):

    queryset = WorkoutFile.objects.all()
    serializer_class = WorkoutFileSerializer
    permission_classes = [permissions.IsAuthenticated & IsOwnerOfWorkout]
    parser_classes = [MultipartJsonParser, JSONParser]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = WorkoutFile.objects.none()
        if self.request.user:
            qs = WorkoutFile.objects.filter(
                Q(owner=self.request.user)
                | Q(workout__owner=self.request.user)
                | (
                    Q(workout__visibility="CO")
                    & Q(workout__owner__coach=self.request.user)
                )
            ).distinct()

        return qs


class WorkoutFileDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):

    queryset = WorkoutFile.objects.all()
    serializer_class = WorkoutFileSerializer
    permission_classes = [
        permissions.IsAuthenticated
        & (
            IsOwner
            | IsOwnerOfWorkout
            | (IsReadOnly & (IsCoachOfWorkoutAndVisibleToCoach | IsWorkoutPublic))
        )
    ]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
