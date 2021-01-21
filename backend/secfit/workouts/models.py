"""Contains the models for the workouts Django application. Users
log workouts (Workout), which contain instances (ExerciseInstance) of various
type of exercises (Exercise). The user can also upload files (WorkoutFile) .
"""
import os
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth import get_user_model


class OverwriteStorage(FileSystemStorage):
    """Filesystem storage for overwriting files. Currently unused."""

    def get_available_name(self, name, max_length=None):
        """https://djangosnippets.org/snippets/976/
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.

        Args:
            name (str): Name of the file
            max_length (int, optional): Maximum length of a file name. Defaults to None.
        """
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))


# Create your models here.
class Workout(models.Model):
    """Django model for a workout that users can log.

    A workout has several attributes, and is associated with one or more exercises
    (instances) and, optionally, files uploaded by the user.

    Attributes:
        name:        Name of the workout
        date:        Date the workout was performed or is planned
        notes:       Notes about the workout
        owner:       User that logged the workout
        visibility:  The visibility level of the workout: Public, Coach, or Private
    """

    name = models.CharField(max_length=100)
    date = models.DateTimeField()
    notes = models.TextField()
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="workouts"
    )

    # Visibility levels
    PUBLIC = "PU"  # Visible to all authenticated users
    COACH = "CO"  # Visible only to owner and their coach
    PRIVATE = "PR"  # Visible only to owner
    VISIBILITY_CHOICES = [
        (PUBLIC, "Public"),
        (COACH, "Coach"),
        (PRIVATE, "Private"),
    ]  # Choices for visibility level

    visibility = models.CharField(
        max_length=2, choices=VISIBILITY_CHOICES, default=COACH
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.name


class Exercise(models.Model):
    """Django model for an exercise type that users can create.

    Each exercise instance must have an exercise type, e.g., Pushups, Crunches, or Lunges.

    Attributes:
        name:        Name of the exercise type
        description: Description of the exercise type
        unit:        Name of the unit for the exercise type (e.g., reps, seconds)
    """

    name = models.CharField(max_length=100)
    description = models.TextField()
    unit = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ExerciseInstance(models.Model):
    """Django model for an instance of an exercise.

    Each workout has one or more exercise instances, each of a given type. For example,
    Kyle's workout on 15.06.2029 had one exercise instance: 3 (sets) reps (unit) of
    10 (number) pushups (exercise type)

    Attributes:
        workout:    The workout associated with this exercise instance
        exercise:   The exercise type of this instance
        sets:       The number of sets the owner will perform/performed
        number:     The number of repetitions in each set the owner will perform/performed
    """

    workout = models.ForeignKey(
        Workout, on_delete=models.CASCADE, related_name="exercise_instances"
    )
    exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, related_name="instances"
    )
    sets = models.IntegerField()
    number = models.IntegerField()


def workout_directory_path(instance, filename):
    """Return path for which workout files should be uploaded on the web server

    Args:
        instance (WorkoutFile): WorkoutFile instance
        filename (str): Name of the file

    Returns:
        str: Path where workout file is stored
    """
    return f"workouts/{instance.workout.id}/{filename}"


class WorkoutFile(models.Model):
    """Django model for file associated with a workout. Basically a wrapper.

    Attributes:
        workout: The workout for which this file has been uploaded
        owner:   The user who uploaded the file
        file:    The actual file that's being uploaded
    """

    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="files")
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="workout_files"
    )
    file = models.FileField(upload_to=workout_directory_path)


class RememberMe(models.Model):
    """Django model for an remember_me cookie used for remember me functionality.

    Attributes:
        remember_me:        Value of cookie used for remember me
    """

    remember_me = models.CharField(max_length=500)

    def __str__(self):
        return self.remember_me
