from geopy.distance import geodesic
from rest_framework import serializers

from app_run.models import Position


class PositionSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(min_value=-90.0, max_value=90.0)
    longitude = serializers.FloatField(min_value=-180.0, max_value=180.0)
    date_time = serializers.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M:%S.%f"],
        format="%Y-%m-%dT%H:%M:%S.%f",
        required=True,
        allow_null=False,
    )

    class Meta:
        model = Position
        fields = (
            "id",
            "run",
            "latitude",
            "longitude",
            "date_time",
            "speed",
            "distance",
        )

    def validate(self, data):
        run = data["run"]
        if run.status != "in_progress":
            raise serializers.ValidationError("Run is not in progress.")
        return data

    def create(self, validated_data):
        run = validated_data["run"]

        # Получаем все позиции для этой пробежки, отсортированные по времени
        prev_positions = Position.objects.filter(run=run).order_by("date_time")

        total_distance = 0.0  # начальное расстояние

        # Если есть предыдущие позиции, считаем суммарное расстояние
        if prev_positions.exists():
            prev_pos = prev_positions.last()  # последняя из предыдущих
            current_point = (validated_data["latitude"], validated_data["longitude"])
            prev_point = (prev_pos.latitude, prev_pos.longitude)

            # Расстояние от предыдущей позиции до текущей
            segment_distance = geodesic(prev_point, current_point).kilometers

            # Суммируем с предыдущим расстоянием
            total_distance = prev_pos.distance + segment_distance

        # Записываем итоговое расстояние в validated_data
        validated_data["distance"] = round(total_distance, 2)

        # Вычисляем скорость (если есть предыдущая позиция)
        if prev_positions.exists():
            prev_pos = prev_positions.last()
            current_point = (validated_data["latitude"], validated_data["longitude"])
            prev_point = (prev_pos.latitude, prev_pos.longitude)

            distance_meters = geodesic(prev_point, current_point).meters
            time_diff = (
                validated_data["date_time"] - prev_pos.date_time
            ).total_seconds()

            if time_diff > 0:
                speed = distance_meters / time_diff
            else:
                speed = 0

            validated_data["speed"] = round(speed, 2)

        # Создаём позицию
        position = super().create(validated_data)

        # Проверяем предметы рядом
        self.check_collectible_items(position)

        return position

    def check_collectible_items(self, position):
        from app_run.models import CollectibleItem  # чтобы избежать circular import

        athlete = position.run.athlete
        current_point = (position.latitude, position.longitude)

        for item in CollectibleItem.objects.all():
            item_point = (item.latitude, item.longitude)
            distance = geodesic(current_point, item_point).meters

            if distance < 100:
                item.athlete.add(athlete)
