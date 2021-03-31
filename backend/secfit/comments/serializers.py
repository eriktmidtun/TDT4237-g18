from rest_framework import serializers
from rest_framework.serializers import HyperlinkedRelatedField
from comments.models import Comment, Like
from workouts.models import Workout
from django.utils.html import escape


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    workout = HyperlinkedRelatedField(
        queryset=Workout.objects.all(), view_name="workout-detail"
    )
    
    def validate_content(self,value):
        return escape(value)

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
