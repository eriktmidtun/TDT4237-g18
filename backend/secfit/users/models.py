from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from .validators import PDFValidator


# Create your models here.


class User(AbstractUser):
    """
    Standard Django User model with an added field for a user's coach.
    """
    email = models.EmailField(blank=False, null=False, unique=True, max_length=254, verbose_name="email address")
    is_verified=models.BooleanField(default=False)
    coach = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="athletes", blank=True, null=True
    )


def athlete_directory_path(instance, filename):
    """
    Return the path for an athlete's file
    :param instance: Current instance containing an athlete
    :param filename: Name of the file
    :return: Path of file as a string
    """
    return f"users/{instance.athlete.id}/{filename}"


class AthleteFile(models.Model):
    """
    Model for an athlete's file. Contains fields for the athlete for whom this file was uploaded,
    the coach owner, and the file itself.
    """

    athlete = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="coach_files"
    )
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="athlete_files"
    )
    file = models.FileField(upload_to=athlete_directory_path, validators=[PDFValidator])


class Offer(models.Model):
    """Django model for a coaching offer that one user sends to another.

    Each offer has an owner, a recipient, a status, and a timestamp.

    Attributes:
        owner:       Who sent the offer
        recipient:   Who received the offer
        status:      The current status of the offer (accept, declined, or pending)
        timestamp:   When the offer was sent.
    """
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="sent_offers"
    )
    recipient = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="received_offers"
    )

    ACCEPTED = "a"
    PENDING = "p"
    DECLINED = "d"
    STATUS_CHOICES = (
        (ACCEPTED, "Accepted"),
        (PENDING, "Pending"),
        (DECLINED, "Declined"),
    )

    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=PENDING)
    timestamp = models.DateTimeField(auto_now_add=True)

class RememberMe(models.Model):
    """Django model for an remember_me cookie used for remember me functionality.

    Attributes:
        remember_me:        Value of cookie used for remember me
    """

    remember_me = models.CharField(max_length=500)

    def __str__(self):
        return self.remember_me
