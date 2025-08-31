from django.contrib import admin

from app_run.models import Run

# Register your models here.
# admin.site.register(Run)
@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'athlete', 'status')