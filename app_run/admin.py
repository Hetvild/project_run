from django.contrib import admin

from app_run.models import Run, AthleteInfo


# Register your models here.
@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ("id", "comment", "athlete", "status")


@admin.register(AthleteInfo)
class AthleteInfoAdmin(admin.ModelAdmin):
    list_display = ("id", "goals", "weight", "user_id")
