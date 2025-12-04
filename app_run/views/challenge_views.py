from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from app_run.models import Challenge
from app_run.serializers import ChallengeSerializer, ChallengeSummarySerializer


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


class ChallengeSummaryViewSet(generics.ListAPIView):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSummarySerializer
