from rest_framework import serializers

from app_run.models import Challenge


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = "__all__"


class ChallengeSummarySerializer(serializers.ModelSerializer):
    """
    Собираем список челленджей и готовим структуру
    """

    class Meta:
        model = Challenge
        fields = "__all__"
