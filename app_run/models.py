from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Run(models.Model):
    STATUS_CHOICES = [
        ("init", "init"),
        ("in_progress", "in_progress"),
        ("finished", "finished"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="init")
    distance = models.FloatField(default=0, blank=True)

    def __str__(self):
        return self.athlete.username + " - " + self.comment


class AthleteInfo(models.Model):
    goals = models.CharField(max_length=200, blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user_id.username + " - " + self.goals


class Challenge(models.Model):
    full_name = models.CharField(max_length=50, default="Сделай 10 Забегов!")
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)


class Position(models.Model):
    """
    Модель, представляющая географическую позицию пробежки.

    Attributes:
        run (IntegerField): Идентификатор пробежки, к которой относится данная позиция.
        latitude (FloatField): Широта местоположения в десятичном формате.
        longitude (FloatField): Долгота местоположения в десятичном формате.
    """

    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="positions")
    latitude = models.FloatField()
    longitude = models.FloatField()
