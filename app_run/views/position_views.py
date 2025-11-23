from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from app_run.models import Position
from app_run.serializers import PositionSerializer


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
