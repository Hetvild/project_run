from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from app_run.models import Subscribe
from app_run.views.run_views import logger


class SubscribeAPIView(APIView):
    """
    class обрабатывает данные с url: api/subscribe_to_coach/<int:id>/
    В url должен передаваться id Тренера
    В теле запроса передается id Атлета в виде: {'athlete': 123}
    """

    def post(self, request: Request, id: int):
        # Проверяем что получили данные по тренеру или возвращаем 404
        # Если юзер есть но он не коуч, то ответ 400
        # Если подписывыемся на несуществующего коуча, то код ответа 404
        try:
            coach = User.objects.get(id=id, is_superuser=False)
            logger.warning(
                f"Данные по запрашиваемому тренеру: ID: {coach.id}, UserName: {coach.username}, Тренер: {coach.is_staff}"
            )
            if coach.is_staff:
                logger.warning(
                    f"Данные по запрашиваемому тренеру найдены: ID: {coach.id}, UserName: {coach.username}, Тренер: {coach.is_staff}"
                )
            else:
                logger.warning(
                    f"Получен пользователь который не является тренером: ID: {coach.id}, UserName: {coach.username}"
                )
                return Response(status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist as ex:
            logger.warning(
                f"Попытка подписаться на не существующего тренера: {id}. Ошибка: {ex}"
            )
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Получаем данные по athlete через get, чтобы поймать исключение, если athlete не найден, то возвращаем код 400
        try:
            athlete = User.objects.get(
                id=int(request.data.get("athlete")), is_staff=False, is_superuser=False
            )
            logger.warning(f"athlete_data: {athlete.id}")

        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        logger.warning(f"Запрос на подписку на тренера: {id}")
        logger.warning(f"Тело запроса: {request.data}")

        if coach.coach_subscriptions.filter(
            athlete_id=athlete, coach_id=coach
        ).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Делаем запись в модель Subscribe
        Subscribe.objects.create(
            coach_id=coach.id,
            athlete_id=athlete.id,
        )

        return Response({"message": "Подписка оформлена"}, status=status.HTTP_200_OK)
