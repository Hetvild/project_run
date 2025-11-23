import logging

from django.db.models import Avg, Count, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.filters import OrderingFilter

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from app_run.models import Run, Position, Challenge
from app_run.serializers import RunSerializer
from app_run.services import calculate_route_distance, calculate_run_time_seconds

logger = logging.getLogger(__name__)


class ViewPagination(PageNumberPagination):
    page_size_query_param = "size"
    max_page_size = 5


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related("athlete").all()
    serializer_class = RunSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "athlete"]
    ordering_fields = ["created_at"]
    pagination_class = ViewPagination


class StartRunAPIView(APIView):
    def post(self, request, *args, **kwargs) -> Response:
        run_id = kwargs.get("run_id")
        run = get_object_or_404(Run, pk=run_id)

        if run.status != "init":
            return Response(
                {"Ошибка": "Забег уже запущен или закончен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        run.status = "in_progress"
        run.save()

        serializer = RunSerializer(run)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StopRunAPIView(APIView):
    def post(self, request, run_id) -> Response:
        run = get_object_or_404(Run, pk=run_id)

        # Проверяем, что статус бега не "завершен"
        if run.status != "in_progress":
            return Response(
                {"Ошибка": "Забег еще не запущен"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Если забег завершен — обновляем статус на "finished"
        run.status = "finished"
        run.save()

        # Получаем спортсмена, который завершил забег
        athlete = run.athlete

        # Получаем список позиций из модели Position для текущего забега по полю run в виде словаря
        positions_list = Position.objects.filter(run=run).values()

        # Рассчитываем расстояние по полученным координатам
        try:
            distance = calculate_route_distance(positions_list)
        except ValueError as e:
            # Если точек меньше 2 — считаем расстояние = 0
            distance = 0.0
            logger.warning(f"Расчёт расстояния невозможен для забега {run.id}: {e}")

        # Рассчитываем время по пройденным координатам
        run_time_seconds = calculate_run_time_seconds(run)
        logger.warning(f"run_time_seconds: {run_time_seconds}")

        # Получаем среднюю скорость всех позиций
        if positions_list:
            speed = sum([position["speed"] for position in positions_list]) / len(
                positions_list
            )
            run.speed = speed
            run.save()
        logger.warning(f"positions_list: {positions_list}")

        if run_time_seconds:
            run.run_time_seconds = run_time_seconds
            run.save()

        # Обновляем поле distance в модели Run
        if distance:
            run.distance = distance
            run.save()

        average_speed = Position.objects.filter(run=run).aggregate(Avg("speed"))[
            "speed__avg"
        ]
        print(f"average_speed: {average_speed}")

        count = Run.objects.filter(athlete=athlete, status="finished").aggregate(
            Count("athlete")
        )

        distance_sum = Run.objects.filter(athlete=athlete, status="finished").aggregate(
            Sum("distance")
        )

        # Если это 10-й завершённый забег — создаём челлендж (если ещё не создан)
        if count["athlete__count"] == 10:
            Challenge.objects.get_or_create(
                athlete=athlete,
                full_name="Сделай 10 Забегов!",
            )

        # Если сумма завершенных забегов больше или равна 50 км — создаём челлендж (если ещё не создан)
        if distance_sum["distance__sum"] >= 50:
            Challenge.objects.get_or_create(
                athlete=athlete,
                full_name="Пробеги 50 километров!",
            )

        # Если атлет пробежал за 10 минут или быстрее и дистанция была 2 км или больше -
        # создаем челлендж "Челлендж 2 км за 10 минут"
        if run_time_seconds <= 600 and distance >= 2 and run.status == "finished":
            Challenge.objects.get_or_create(
                athlete=athlete,
                full_name="2 километра за 10 минут!",
            )

        serializer = RunSerializer(run)
        return Response(serializer.data, status=status.HTTP_200_OK)
