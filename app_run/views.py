import io

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem
from app_run.serializers import (
    RunSerializer,
    CouchAthleteSerializer,
    AthleteInfoSerializer,
    ChallengeSerializer,
    PositionSerializer,
    CollectibleItemSerializer,
)
from app_run.services import calculate_route_distance, read_excel_file


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

        # Если забег завершен — обновляем статус на "finished"
        run.status = "finished"
        run.save()

        athlete = run.athlete

        # Получаем список позиций из модели Position для текущего забега по полю run в виде словаря
        positions_list = Position.objects.filter(run=run).values()
        distance = calculate_route_distance(positions_list)

        # Обновляем поле distance в модели Run
        if distance:
            run.distance = distance
            run.save()

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


class PositionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для просмотра и редактирования объектов Position.

    Этот ViewSet предоставляет стандартные действия: получение, создание,
    обновление и удаление позиций. Также доступна фильтрация по полю 'run'
    с использованием DjangoFilterBackend.

    Атрибуты:
        queryset (QuerySet): Базовый набор запросов для всех объектов Position.
        serializer_class (Serializer): Класс сериализатора для данных Position.
        filter_backends (List): Список бэкендов фильтрации, используемых в этом ViewSet.
        filterset_fields (List[str]): Поля, по которым можно производить фильтрацию.
    """

    queryset = Position.objects.all()
    serializer_class = PositionSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["run"]


class CollectibleItemViewSet(viewsets.ModelViewSet):
    queryset = CollectibleItem.objects.all()
    serializer_class = CollectibleItemSerializer


class UploadFileAPIView(APIView):
    def post(self, request):
        # Если файл не передан, то возвращаем ошибку 400
        if not request.FILES:
            return Response(
                {"error": "Файл не был загружен"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Получаем переданный файл из запроса
        uploaded_file = request.FILES.get("upload_example", None)

        # Проверяем, что файл не пустой и имеет расширение .xlsx
        if uploaded_file.name.endswith(".xlsx"):

            # Отправляем полученный файл на чтение
            read_excel_file(uploaded_file)

        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return HttpResponse("ok", status=status.HTTP_201_CREATED)
