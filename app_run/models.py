from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Run(models.Model):
    STATUS_CHOICES = [
        ('init', 'init'),
        ('in_progress', 'in_progress'),
        ('finished', 'finished'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='init')

    def __str__(self):
        return self.athlete.username + " - " + self.comment
