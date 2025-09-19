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
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name="run")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="init")
    distance = models.FloatField(default=0, blank=True)
    run_time_seconds = models.IntegerField(default=0, blank=True)

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
    date_time = models.DateTimeField(null=True, blank=True)
    # date_time = models.DateTimeField(default="")


class CollectibleItem(models.Model):
    """
    Модель хранит коллекции предметов для награждения спортсменов, связанный с пользователем (спортсменом).

    Attributes:
        name (str): Название предмета. Обязательное поле.
        uid (str): Уникальный идентификатор предмета. Обязательное поле.
        latitude (float): Географическая широта местоположения предмета. Индексировано для ускорения поиска.
        longitude (float): Географическая долгота местоположения предмета. Индексировано для ускорения поиска.
        picture (str): URL изображения предмета. Максимальная длина — 500 символов.
        value (int): Числовое значение или цена предмета.
        items (ManyToManyField): Связь "многие ко многим" с моделью пользователя (User),
                                   указывает, какие спортсмены имеют данный предмет.
                                   related_name позволяет обращаться к предметам через пользователя как `collectible_items`.
    """

    name = models.CharField(max_length=100, blank=False)
    uid = models.CharField(max_length=100, blank=False)
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)
    picture = models.URLField(max_length=500)
    value = models.IntegerField()
    athlete = models.ManyToManyField(User, related_name="items")
