from django.contrib.auth.models import User
from rest_framework import serializers

from app_run.models import Run


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "last_name", "first_name")


class RunSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Run, который позволяет переводить объекты Run в JSON и обратно.
    """

    athlete_data = UserSerializer(source="athlete", read_only=True)

    class Meta:
        model = Run
        fields = "__all__"


class CouchAthleteSerializer(serializers.ModelSerializer):
    # Определяем вычисляемое поле для вывода типа пользователя
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "date_joined",
            "username",
            "last_name",
            "first_name",
            "type",
            "runs_finished",
        )

    def get_type(self, obj):
        if obj.is_staff:
            return "coach"
        else:
            return "athlete"

    def get_runs_finished(self, obj):
        count = obj.run_set.filter(status="finished").count()
        return count
