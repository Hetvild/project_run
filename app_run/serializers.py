from django.contrib.auth.models import User
from rest_framework import serializers

from app_run.models import Run, AthleteInfo


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

    def get_type(self, obj) -> str:
        if obj.is_staff:
            return "coach"
        else:
            return "athlete"

    def get_runs_finished(self, obj) -> int:
        count = obj.run_set.filter(status="finished").count()
        return count


class AthleteInfoSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user_id.id", read_only=True)

    weight = serializers.IntegerField(
        min_value=0.1,
        max_value=899.9,
        allow_null=True,
        error_messages={
            "min_value": "Вес должен быть больше 0",
            "max_value": "Вес должен быть меньше 900",
        },
    )

    class Meta:
        model = AthleteInfo
        fields = ("weight", "goals", "user_id")
