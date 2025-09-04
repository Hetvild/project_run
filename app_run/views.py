from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from app_run.models import Run, AthleteInfo, Challenge
from app_run.serializers import (
    RunSerializer,
    CouchAthleteSerializer,
    AthleteInfoSerializer,
    ChallengeSerializer,
)


class ViewPagination(PageNumberPagination):
    page_size_query_param = "size"
    max_page_size = 5


@api_view(["GET"])
def company_details(request) -> Response:
    """
    Возвращает информацию о компании, данные берутся из settings.py
    """
    details = {
        "company_name": settings.COMPANY_NAME,
        "slogan": settings.SLOGAN,
        "contacts": settings.CONTACTS,
    }
    return Response(details)


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related("athlete").all()
    serializer_class = RunSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "athlete"]
    ordering_fields = ["created_at"]
    pagination_class = ViewPagination


class CouchAthleteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = CouchAthleteSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["date_joined"]
    search_fields = ["first_name", "last_name"]
    ordering_fields = ["date_joined"]
    pagination_class = ViewPagination

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get("type", None)

        if type == "coach":
            return qs.filter(is_staff=True)

        elif type == "athlete":
            return qs.filter(is_staff=False)

        else:
            return qs


class StartRunAPIView(APIView):
    def post(self, request, run_id: int) -> Response:
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

        run.status = "finished"
        run.save()

        # Если забег закончен и id равен 10, то создаем запись в таблице Challenge
        if run_id == 10:
            full_name = "Сделай 10 Забегов!"
            if run.status == "finished":
                Challenge.objects.create(full_name=full_name, athlete=run.athlete)

        serializer = RunSerializer(run)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class ChallengeViewSet(APIView):
    def get(self, request):
        # Проверяем, что в запросе есть параметр athlete
        athlete_id = request.query_params.get("athlete", None)

        # Получаем количество завершенных забегов
        runs = Run.objects.filter(
            athlete=athlete_id, status="finished"
        ).count()  # ← считаем количество завершенных забегов
        print(runs)
        # Проверяем, по athlete_id что у пользователя есть 10 завершенных забегов
        # if athlete_id:
        #     runs = Run.objects.filter(
        #         athlete=athlete_id, status="finished"
        #     ).count()  # ← считаем количество завершенных забегов
        #
        #     # Если количество завершенных забегов равно 10, то возвращаем 200 статус
        #     if runs == 10:

        if athlete_id:
            challenges = Challenge.objects.select_related("athlete").filter(
                athlete=athlete_id
            )
            serializer = ChallengeSerializer(challenges, many=True)
            return Response(serializer.data)

        else:
            challenges = Challenge.objects.all()
            serializer = ChallengeSerializer(challenges, many=True)
            return Response(serializer.data)
