from rest_framework import serializers

from app_run.models import Run
from app_run.serializers import UserSerializer


class RunSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Run, который позволяет переводить объекты Run в JSON и обратно.
    """

    athlete_data = UserSerializer(source="athlete", read_only=True)

    class Meta:
        model = Run
        fields = (
            "id",
            "created_at",
            "comment",
            "athlete",
            "status",
            "distance",
            "run_time_seconds",
            "speed",
            "athlete_data",
        )
