from collections import defaultdict

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app_run.models import Challenge
from app_run.serializers import ChallengeSerializer
from app_run.serializers.user import AthleteSummarySerializer


class ChallengeViewSet(APIView):
    def get(self, request):
        athlete_id = request.query_params.get("athlete")

        # Если передан athlete — фильтруем по нему
        if athlete_id:
            try:
                athlete_id = int(athlete_id)
            except ValueError:
                return Response(
                    {"error": "Параметр 'athlete' должен быть числом"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            challenges = Challenge.objects.select_related("athlete").filter(
                athlete_id=athlete_id
            )
        else:
            # Иначе — все челленджи
            challenges = Challenge.objects.select_related("athlete").all()

        serializer = ChallengeSerializer(challenges, many=True)
        return Response(serializer.data)


class ChallengeSummaryViewSet(APIView):
    def get(self, request):
        # Получаем все челленджи с жадной загрузкой athlete (User)
        challenges = Challenge.objects.select_related("athlete").all()

        # Группируем по full_name
        grouped = defaultdict(list)
        for ch in challenges:
            grouped[ch.full_name].append(ch.athlete)

        # Формируем результат
        result = []
        for full_name, athletes in grouped.items():
            # Убираем дубликаты пользователей (на всякий случай)
            unique_athletes = list({a.id: a for a in athletes}.values())
            # Сериализуем бегунов
            athletes_data = AthleteSummarySerializer(unique_athletes, many=True).data
            result.append({"name_to_display": full_name, "athletes": athletes_data})

        return Response(result)
