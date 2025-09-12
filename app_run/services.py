import io
from typing import Any

from django.db.models import QuerySet
from geopy.distance import geodesic
from openpyxl import load_workbook

from app_run.models import Position
from app_run.serializers import CollectibleItemSerializer


def calculate_route_distance(coordinates: QuerySet[Position, dict[str, Any]]) -> float:
    """
    Рассчитывает общее расстояние маршрута между географическими точками.

    Args:
        coordinates (list[dict]): Список координат в формате словарей,
                                  где каждый словарь содержит ключи "lat" и "lon".
                                  Пример: [{"lat": 55.7558, "lon": 37.6176}, ...]

    Returns:
        float: Общее расстояние маршрута в километрах.

    Raises:
        KeyError: Если в одном из элементов списка отсутствуют ключи "lat" или "lon".
        TypeError: Если значения "lat" или "lon" не являются числами.
        ValueError: Если список содержит менее двух точек.

    Пример:
        >>> coordinates = [
        ...     {"latitude": 55.7558, "longitude": 37.6176},
        ...     {"latitude": 48.8566, "longitude": 2.3522}
        ... ]
        >>> calculate_route_distance(coordinates)
        1698.7
    """
    if len(coordinates) < 2:
        raise ValueError(
            "Список должен содержать минимум две точки для расчета расстояния."
        )

    total_distance = 0.0

    for i in range(len(coordinates) - 1):
        point1 = (coordinates[i]["latitude"], coordinates[i]["longitude"])
        point2 = (coordinates[i + 1]["latitude"], coordinates[i + 1]["longitude"])
        distance = geodesic(point1, point2).kilometers
        total_distance += distance

    return total_distance


def read_excel_file(uploaded_file):
    # Читаем переданный файл
    file_content = uploaded_file.read()
    # Переводим файл в байтовый поток
    file_bytes = io.BytesIO(file_content)

    # Загружаем файл в экземпляр класса Workbook
    wb = load_workbook(file_bytes)
    # Получаем активный лист
    worksheet = wb.active
    # Получаем количество строк в листе
    max_row = worksheet.max_row

    # Создаем пустой список для хранения не валидных данных
    data_error = []

    # Получаем данные из листа
    for row in worksheet.iter_rows(values_only=True, min_row=1, max_row=max_row):
        # Присваиваем значения переменным
        name, uid, value, latitude, longitude, pictures = row

        # Формируем словарь для сериализации
        data = {
            "name": name,
            "uid": uid,
            "latitude": latitude,
            "longitude": longitude,
            "pictures": pictures,
            "value": value,
        }

        # Отправляем данные на сериализацию
        serializer = CollectibleItemSerializer(data=data)

        # Проверяем валидность данных, если данные валидны, сохраняем их в базе данных
        if serializer.is_valid():
            # Сохраняем данные в базе данных
            serializer.save()
        else:
            # Если данные не валидны, добавляем их в список ошибок
            data_error.append(list(data.values()))

    return data_error
