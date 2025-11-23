from rest_framework import serializers

from app_run.models import CollectibleItem


class CollectibleItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели CollectibleItem, используемой для представления собирательных элементов в API.

    Основные функции:
    - Валидация и сериализация данных объекта CollectibleItem.
    - Преобразование данных между форматом Python и JSON при работе с API.
    - Обеспечение доступа к полям модели, необходимым для отображения и редактирования.

    Атрибуты:
        id (IntegerField): Уникальный идентификатор элемента.
        name (CharField): Название элемента. Максимальная длина — 255 символов.
        uid (UUIDField): Уникальный идентификатор элемента (UUID).
        latitude (FloatField): Широта местоположения элемента.
        longitude (FloatField): Долгота местоположения элемента.
        pictures (URLField): Список url ссылок на изображения, связанных с элементом.
        value (DecimalField): Значение элемента, например, стоимость или рейтинг.
    """

    # Проверяем что name не пустое и не длиннее 255 символов
    name = serializers.CharField()

    # Проверяем что uid является тестовым полем, не может быть пустым
    uid = serializers.CharField()

    # Проверяем что value является числом, значение не может быть отрицательным
    value = serializers.IntegerField()

    # Проверяем что поле pictures является url
    picture = serializers.URLField()

    # Проверяем что latitude и longitude в диапазоне от -90 до 90 и от -180 до 180
    latitude = serializers.FloatField(min_value=-90.0, max_value=90.0)
    longitude = serializers.FloatField(min_value=-180.0, max_value=180.0)

    class Meta:
        model = CollectibleItem
        fields = ("id", "name", "uid", "latitude", "longitude", "picture", "value")
