from rest_framework import serializers
from rest_framework.serializers import HyperlinkedRelatedField
from comments.models import Comment, Like
from workouts.models import Workout


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    workout = HyperlinkedRelatedField(
        queryset=Workout.objects.all(), view_name="workout-detail"
    )

    class Meta:
        model = Comment
        fields = ["url", "id", "owner", "workout", "content", "timestamp"]


class LikeSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    comment = HyperlinkedRelatedField(
        queryset=Comment.objects.all(), view_name="comment-detail"
    )

    class Meta:
        model = Like
        fields = ["url", "id", "owner", "comment", "timestamp"]
