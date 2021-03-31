from django.urls import path, include
from workouts import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# This is a bit messy and will need to change
urlpatterns = format_suffix_patterns(
    [
        path("", views.api_root),
        path("api/workouts/", views.WorkoutList.as_view(), name="workout-list"),
        path(
            "api/workouts/<int:pk>/",
            views.WorkoutDetail.as_view(),
            name="workout-detail",
        ),
        path("api/exercises/", views.ExerciseList.as_view(), name="exercise-list"),
        path(
            "api/exercises/<int:pk>/",
            views.ExerciseDetail.as_view(),
            name="exercise-detail",
        ),
        path(
            "api/exercise-instances/",
            views.ExerciseInstanceList.as_view(),
            name="exercise-instance-list",
        ),
        path(
            "api/exercise-instances/<int:pk>/",
            views.ExerciseInstanceDetail.as_view(),
            name="exerciseinstance-detail",
        ),
        path(
            "api/workout-files/",
            views.WorkoutFileList.as_view(),
            name="workout-file-list",
        ),
        path(
            "api/workout-files/<int:pk>/",
            views.WorkoutFileDetail.as_view(),
            name="workoutfile-detail",
        ),
        path("api/auth/", include("rest_framework.urls")),
        path("media/workouts/<int:workout_id>/<str:filename>", views.WorkoutFileResponse.as_view(), name="media_workout_file")
    ]
)
