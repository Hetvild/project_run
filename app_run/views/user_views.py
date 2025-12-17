from django.contrib.auth.models import User
from django.db import models
from django.db.models.aggregates import Avg, Count, Max, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from app_run.models import AthleteInfo, Subscribe, Run
from app_run.serializers import (
    CoachAthleteSerializer,
    CoachAthleteItemsSerializer,
    AthleteInfoSerializer,
    AthleteWithCoachSerializer,
    CoachWithAthletesSerializer,
)
from app_run.views.run_views import ViewPagination


class CouchAthleteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = CoachAthleteSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["date_joined"]
    search_fields = ["first_name", "last_name"]
    ordering_fields = ["date_joined"]
    pagination_class = ViewPagination

    def get_serializer_class(self):
        if self.action == "retrieve":  # для /api/users/{id}/
            # Для retrieve — сначала получаем объект
            user_being_viewed = self.get_object()

            if user_being_viewed.is_staff:
                # Это тренер → возвращаем сериализатор с athletes
                return CoachWithAthletesSerializer
            else:
                # Это атлет → возвращаем сериализатор с coach
                return AthleteWithCoachSerializer

            return CoachAthleteItemsSerializer
        else:
            return CoachAthleteSerializer  # для /api/users/

    def get_queryset(self):
        qs = User.objects.filter(is_superuser=False).annotate(
            runs_finished=Count("run", filter=models.Q(run__status="finished")),
            rating=Avg("received_ratings__rating"),
        )

        type_param = self.request.query_params.get("type", None)

        if type_param == "coach":
            qs = qs.filter(is_staff=True)
        elif type_param == "athlete":
            qs = qs.filter(is_staff=False)

        return qs


class AthleteInfoAPIView(APIView):
    # Получение информации о целях, весе и id пользователя
    def get(self, request: Request, user_id: int) -> Response:
        """
        Метод get возвращает информацию о целях, весе и id пользователя
        """
        # Ищем пользователя по id, если его нет, то возвращаем ошибку 404
        user = get_object_or_404(User, pk=user_id)

        # Ищем запись в таблице AthleteInfo по user_id, если нет, то создаем новую пустую запись
        athlete_info, created = AthleteInfo.objects.get_or_create(
            user_id=user,  # ← ищем по user_id
            defaults={
                "goals": "",
                "weight": None,
            },
        )

        # Сериализуем данные
        serializer = AthleteInfoSerializer(athlete_info)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, user_id: int):
        """
        Метод put обновляет информацию о целях и весе по id пользователя
        """
        # Получаем переданные данные из запроса в формате JSON
        data = request.data

        # Ищем пользователя по id, если его нет, то возвращаем ошибку 404
        user = get_object_or_404(User, pk=user_id)

        # Сериализуем данные, чтобы проверить их на валидность до записи в базу данных
        serializer = AthleteInfoSerializer(data=request.data, partial=True)

        # Если данные не валидны (проверяем значение "weight"), то возвращаем ошибку 400
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        # Ищем запись в таблице AthleteInfo по user_id, если нет, то обновляем данными из запроса
        athlete_info, created = AthleteInfo.objects.update_or_create(
            user_id=user,
            defaults={
                "goals": data.get("goals"),
                "weight": data.get("weight"),
            },
        )

        # Сериализуем данные
        serializer = AthleteInfoSerializer(athlete_info, data=request.data)

        # Если данные валидны, то обновляем данные в базе данных
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class AnalyticsForCoachAPIView(APIView):
    """
    Представление, которое возвращает аналитику для тренера по атлетам
    {
    'longest_run_user': ...  # Id Бегуна который сделал самый длинный забег у этого Тренера
    'longest_run_value': ... # Дистанция самого длинного забега
    'total_run_user': ...    # Id Бегуна который пробежал в сумме больше всех у этого Тренера
    'total_run_value': ...   # Дистанция которую в сумме пробежал этот Бегун
    'speed_avg_user': ...    # Id Бегуна который в среднем бежал быстрее всех
    'speed_avg_value': ...   # Средняя скорость этого Бегуна
    }
    """

    def get(self, request: Request, coach_id: int):

        # Проверка - существует ли тренер и он ли это
        try:
            coach = User.objects.get(id=coach_id, is_staff=True)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Получаем подписчиков тренера
        subscribed_athletes = Subscribe.objects.filter(coach=coach).values_list(
            "athlete_id", flat=True
        )

        # Создаем QuerySet для забегов атлетов, подписанных на тренера
        runs = Run.objects.filter(athlete_id__in=subscribed_athletes, status="finished")

        # Самый длинный забег (по одному забегу)
        longest_run = (
            runs.values("athlete_id")
            .annotate(max_distance=Max("distance"))
            .order_by("-max_distance")
        ).first()

        # Суммарная дистанция по атлетам
        total_run = (
            runs.values("athlete_id")
            .annotate(total_distance=Sum("distance"))
            .order_by("-total_distance")
            .first()
        )

        # Средняя скорость по атлетам
        speed_avg = (
            runs.values("athlete_id")
            .annotate(avg_speed=Avg("speed"))
            .order_by("-avg_speed")
            .first()
        )

        # Формируем ответ
        result = {
            "longest_run_user": longest_run["athlete_id"] if longest_run else None,
            "longest_run_value": (
                float(longest_run["max_distance"]) if longest_run else None
            ),
            "total_run_user": total_run["athlete_id"] if total_run else None,
            "total_run_value": (
                float(total_run["total_distance"]) if total_run else None
            ),
            "speed_avg_user": speed_avg["athlete_id"] if speed_avg else None,
            "speed_avg_value": float(speed_avg["avg_speed"]) if speed_avg else None,
        }

        return Response(result, status=status.HTTP_200_OK)
