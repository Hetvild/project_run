from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app_run.models import Subscribe, CoachRating


class RateCoachApiView(APIView):
    """
    Представление для передачи рейтинга Тренера от Атлета
    """

    def post(self, request, coach_id):
        # Получаем данные из тела запроса и проверяем что они не None
        # Получаем athlete_id из тела запроса
        athlete_id = request.data.get("athlete")
        # Получаем рейтинг из тела запроса
        rating = request.data.get("rating")

        # Проверяем что полученные элементы не None
        if athlete_id is None or rating is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Проверяем что rating это целое число в диапазоне от 1 до 5
        if not (isinstance(rating, int) and 1 <= rating <= 5):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Получаем атлета из базы
        try:
            athlete = User.objects.get(id=athlete_id, is_staff=False)
        except User.DoesNotExist as ex:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Получаем тренера из базы
        try:
            coach = User.objects.get(id=coach_id, is_staff=True)
        except User.DoesNotExist as ex:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Проверяет, что атлет подписан на этого тренера (через модель Subscribe)
        if not Subscribe.objects.filter(coach=coach, athlete=athlete).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        CoachRating.objects.update_or_create(
            coach=coach, athlete=athlete, defaults={"rating": rating}
        )

        return Response({"message": "Rating saved"}, status=status.HTTP_200_OK)
