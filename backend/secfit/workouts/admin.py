"""Module for registering models from workouts app to admin page so that they appear
"""
from django.contrib import admin

# Register your models here.
from .models import Exercise, ExerciseInstance, Workout, WorkoutFile

admin.site.register(Exercise)
admin.site.register(ExerciseInstance)
admin.site.register(Workout)
admin.site.register(WorkoutFile)
