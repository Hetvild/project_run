from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from app_run.models import AthleteInfo
from app_run.serializers import (
    CouchAthleteSerializer,
    CouchAthleteItemsSerializer,
    AthleteInfoSerializer,
)
from app_run.views.run_views import ViewPagination


class CouchAthleteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = CouchAthleteSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["date_joined"]
    search_fields = ["first_name", "last_name"]
    ordering_fields = ["date_joined"]
    pagination_class = ViewPagination

    def get_serializer_class(self):
        if self.action == "retrieve":  # для /api/users/{id}/
            return CouchAthleteItemsSerializer
        else:
            return CouchAthleteSerializer  # для /api/users/

    def get_queryset(self):
        qs = User.objects.filter(is_superuser=False).annotate(
            runs_finished=Count(
                "run",  # обратная связь: User → Run (related_name="run")
                filter=models.Q(run__status="finished"),  # фильтр по статусу
            )
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
