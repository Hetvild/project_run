from django.contrib import admin

from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem


# Register your models here.
@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ("id", "comment", "athlete", "status", "distance")


@admin.register(AthleteInfo)
class AthleteInfoAdmin(admin.ModelAdmin):
    list_display = ("id", "goals", "weight", "user_id")


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "athlete")


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("id", "run", "latitude", "longitude")


@admin.register(CollectibleItem)
class CollectibleItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "uid", "latitude", "longitude", "pictures", "value")
