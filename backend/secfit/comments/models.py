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
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="likes"
    )
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    timestamp = models.DateTimeField(auto_now_add=True)
