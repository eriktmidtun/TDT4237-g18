from django.db import models


from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db import models
from django.contrib.auth import get_user_model
from workouts.models import Workout

# Create your models here.
class Comment(models.Model):
    """Django model for a comment left on a workout.

    Attributes:
        owner:       Who posted the comment
        workout:     The workout this comment was left on.
        content:     The content of the comment.
        timestamp:   When the comment was created.
    """
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="comments"
    )
    workout = models.ForeignKey(
        Workout, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]


class Like(models.Model):
    """Django model for a reaction to a comment.


    Attributes:
        owner:       Who liked the comment
        comment:     The comment that was liked
        timestamp:   When the like occurred.
    """
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="likes"
    )
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    timestamp = models.DateTimeField(auto_now_add=True)
