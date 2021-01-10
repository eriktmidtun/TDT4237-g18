from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


# Create your models here.


class User(AbstractUser):
    """
    Standard Django User model with an added field for a user's coach.
    """

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
    file = models.FileField(upload_to=athlete_directory_path)


class Offer(models.Model):
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

    #ATHLETE = "a"
    #COACH = "c"
    #OFFER_TYPE_CHOICES = ((ATHLETE, "Athlete"), (COACH, "Coach"))

    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=PENDING)
    #offer_type = models.CharField(
    #    max_length=8, choices=OFFER_TYPE_CHOICES, default=ATHLETE
    #)
    #stale = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
