from django.contrib.auth.models import User
from rest_framework import serializers

from app_run.models import Run


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = "__all__"


class CouchAthleteSerializer(serializers.ModelSerializer):
    # Определяем вычисляемое поле для вывода типа пользователя
    type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_superuser",
            "type",
        )

    def get_type(self, obj):
        if obj.is_staff:
            return "coach"
        else:
            return "athlete"
