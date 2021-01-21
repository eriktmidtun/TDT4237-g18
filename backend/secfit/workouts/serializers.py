"""Serializers for the workouts application
"""
from rest_framework import serializers
from rest_framework.serializers import HyperlinkedRelatedField
from workouts.models import Workout, Exercise, ExerciseInstance, WorkoutFile, RememberMe


class ExerciseInstanceSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for an ExerciseInstance. Hyperlinks are used for relationships by default.

    Serialized fields: url, id, exercise, sets, number, workout

    Attributes:
        workout:    The associated workout for this instance, represented by a hyperlink
    """

    workout = HyperlinkedRelatedField(
        queryset=Workout.objects.all(), view_name="workout-detail", required=False
    )

    class Meta:
        model = ExerciseInstance
        fields = ["url", "id", "exercise", "sets", "number", "workout"]


class WorkoutFileSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for a WorkoutFile. Hyperlinks are used for relationships by default.

    Serialized fields: url, id, owner, file, workout

    Attributes:
        owner:      The owner (User) of the WorkoutFile, represented by a username. ReadOnly
        workout:    The associate workout for this WorkoutFile, represented by a hyperlink
    """

    owner = serializers.ReadOnlyField(source="owner.username")
    workout = HyperlinkedRelatedField(
        queryset=Workout.objects.all(), view_name="workout-detail", required=False
    )

    class Meta:
        model = WorkoutFile
        fields = ["url", "id", "owner", "file", "workout"]

    def create(self, validated_data):
        return WorkoutFile.objects.create(**validated_data)


class WorkoutSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for a Workout. Hyperlinks are used for relationships by default.

    This serializer specifies nested serialization since a workout consists of WorkoutFiles
    and ExerciseInstances.

    Serialized fields: url, id, name, date, notes, owner, owner_username, visiblity,
                       exercise_instances, files

    Attributes:
        owner_username:     Username of the owning User
        exercise_instance:  Serializer for ExericseInstances
        files:              Serializer for WorkoutFiles
    """

    owner_username = serializers.SerializerMethodField()
    exercise_instances = ExerciseInstanceSerializer(many=True, required=True)
    files = WorkoutFileSerializer(many=True, required=False)

    class Meta:
        model = Workout
        fields = [
            "url",
            "id",
            "name",
            "date",
            "notes",
            "owner",
            "owner_username",
            "visibility",
            "exercise_instances",
            "files",
        ]
        extra_kwargs = {"owner": {"read_only": True}}

    def create(self, validated_data):
        """Custom logic for creating ExerciseInstances, WorkoutFiles, and a Workout.

        This is needed to iterate over the files and exercise instances, since this serializer is
        nested.

        Args:
            validated_data: Validated files and exercise_instances

        Returns:
            Workout: A newly created Workout
        """
        exercise_instances_data = validated_data.pop("exercise_instances")
        files_data = []
        if "files" in validated_data:
            files_data = validated_data.pop("files")

        workout = Workout.objects.create(**validated_data)

        for exercise_instance_data in exercise_instances_data:
            ExerciseInstance.objects.create(workout=workout, **exercise_instance_data)
        for file_data in files_data:
            WorkoutFile.objects.create(
                workout=workout, owner=workout.owner, file=file_data.get("file")
            )

        return workout

    def update(self, instance, validated_data):
        """Custom logic for updating a Workout with its ExerciseInstances and Workouts.

        This is needed because each object in both exercise_instances and files must be iterated
        over and handled individually.

        Args:
            instance (Workout): Current Workout object
            validated_data: Contains data for validated fields

        Returns:
            Workout: Updated Workout instance
        """
        exercise_instances_data = validated_data.pop("exercise_instances")
        exercise_instances = instance.exercise_instances

        instance.name = validated_data.get("name", instance.name)
        instance.notes = validated_data.get("notes", instance.notes)
        instance.visibility = validated_data.get("visibility", instance.visibility)
        instance.date = validated_data.get("date", instance.date)
        instance.save()

        # Handle ExerciseInstances

        # This updates existing exercise instances without adding or deleting object.
        # zip() will yield n 2-tuples, where n is
        # min(len(exercise_instance), len(exercise_instance_data))
        for exercise_instance, exercise_instance_data in zip(
            exercise_instances.all(), exercise_instances_data
        ):
            exercise_instance.exercise = exercise_instance_data.get(
                "exercise", exercise_instance.exercise
            )
            exercise_instance.number = exercise_instance_data.get(
                "number", exercise_instance.number
            )
            exercise_instance.sets = exercise_instance_data.get(
                "sets", exercise_instance.sets
            )
            exercise_instance.save()

        # If new exercise instances have been added to the workout, then create them
        if len(exercise_instances_data) > len(exercise_instances.all()):
            for i in range(len(exercise_instances.all()), len(exercise_instances_data)):
                exercise_instance_data = exercise_instances_data[i]
                ExerciseInstance.objects.create(
                    workout=instance, **exercise_instance_data
                )
        # Else if exercise instances have been removed from the workout, then delete them
        elif len(exercise_instances_data) < len(exercise_instances.all()):
            for i in range(len(exercise_instances_data), len(exercise_instances.all())):
                exercise_instances.all()[i].delete()

        # Handle WorkoutFiles

        if "files" in validated_data:
            files_data = validated_data.pop("files")
            files = instance.files

            for file, file_data in zip(files.all(), files_data):
                file.file = file_data.get("file", file.file)

            # If new files have been added, creating new WorkoutFiles
            if len(files_data) > len(files.all()):
                for i in range(len(files.all()), len(files_data)):
                    WorkoutFile.objects.create(
                        workout=instance,
                        owner=instance.owner,
                        file=files_data[i].get("file"),
                    )
            # Else if files have been removed, delete WorkoutFiles
            elif len(files_data) < len(files.all()):
                for i in range(len(files_data), len(files.all())):
                    files.all()[i].delete()

        return instance

    def get_owner_username(self, obj):
        """Returns the owning user's username

        Args:
            obj (Workout): Current Workout

        Returns:
            str: Username of owner
        """
        return obj.owner.username


class ExerciseSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for an Exercise. Hyperlinks are used for relationships by default.

    Serialized fields: url, id, name, description, unit, instances

    Attributes:
        instances:  Associated exercise instances with this Exercise type. Hyperlinks.
    """

    instances = serializers.HyperlinkedRelatedField(
        many=True, view_name="exerciseinstance-detail", read_only=True
    )

    class Meta:
        model = Exercise
        fields = ["url", "id", "name", "description", "unit", "instances"]


class RememberMeSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for an RememberMe. Hyperlinks are used for relationships by default.

    Serialized fields: remember_me

    Attributes:
        remember_me:    Value of cookie used for remember me functionality
    """

    class Meta:
        model = RememberMe
        fields = ["remember_me"]
