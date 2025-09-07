from typing import Any

from django.db.models import QuerySet
from geopy.distance import geodesic

from app_run.models import Position


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
