from django.contrib.auth.models import User
from geopy.distance import geodesic
from rest_framework import serializers

from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "last_name", "first_name")


class RunSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Run, который позволяет переводить объекты Run в JSON и обратно.
    """

    athlete_data = UserSerializer(source="athlete", read_only=True)

    class Meta:
        model = Run
        fields = (
            "id",
            "created_at",
            "comment",
            "athlete",
            "status",
            "distance",
            "run_time_seconds",
        )


class CouchAthleteSerializer(serializers.ModelSerializer):
    # Определяем вычисляемое поле для вывода типа пользователя
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "date_joined",
            "username",
            "last_name",
            "first_name",
            "type",
            "runs_finished",
        )

    def get_type(self, obj) -> str:
        if obj.is_staff:
            return "coach"
        else:
            return "athlete"

    def get_runs_finished(self, obj) -> int:
        count = obj.run_set.filter(status="finished").count()
        return count


class AthleteInfoSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user_id.id", read_only=True)

    weight = serializers.IntegerField(
        min_value=0.1,
        max_value=899.9,
        allow_null=True,
        error_messages={
            "min_value": "Вес должен быть больше 0",
            "max_value": "Вес должен быть меньше 900",
        },
    )

    class Meta:
        model = AthleteInfo
        fields = ("weight", "goals", "user_id")


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = "__all__"


class PositionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Position, используемой для представления географических координат пробежки.

    Основные функции:
    - Валидация и сериализация данных широты и долготы.
    - Обеспечение соответствия входных данных требованиям географических координат.
    - Преобразование данных между форматом Python и JSON при работе с API.

    Атрибуты:
        latitude (FloatField): Поле широты. Значение должно находиться в диапазоне от -90 до 90.
        longitude (FloatField): Поле долготы. Значение должно находиться в диапазоне от -180 до 180.
    """

    latitude = serializers.FloatField(
        min_value=-90.0,
        max_value=90.0,
    )
    longitude = serializers.FloatField(
        min_value=-180.0,
        max_value=180.0,
    )

    date_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f")

    class Meta:
        """
        Вложенный класс Meta, задающий параметры сериализатора.

        Атрибуты:
            model (Model): Модель Django, к которой относится этот сериализатор — Position.
            fields (tuple): Поля модели, которые будут включены в сериализацию.
                Содержит:
                - id: Уникальный идентификатор позиции.
                - run: Идентификатор пробежки, к которой относится данная позиция.
                - latitude: Широта.
                - longitude: Долгота.
        """

        model = Position
        fields = ("id", "run", "latitude", "longitude", "date_time")

    def validate(self, data):
        run = data["run"]

        if run.status != "in_progress":
            raise serializers.ValidationError()
        return data

    def create(self, validated_data):
        # Создаём позицию
        position = super().create(validated_data)

        # Проверяем предметы рядом
        self.check_collectible_items(position)

        return position

    def check_collectible_items(self, position):
        from app_run.models import CollectibleItem  # чтобы избежать circular import

        athlete = position.run.athlete
        current_point = (position.latitude, position.longitude)

        # Ищем все предметы
        for item in CollectibleItem.objects.all():
            item_point = (item.latitude, item.longitude)
            distance = geodesic(current_point, item_point).meters

            if distance < 100:
                # Добавляем атлета к предмету (ManyToMany)
                item.athlete.add(athlete)


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


class CouchAthleteItemsSerializer(CouchAthleteSerializer):
    """
    Сериалайзер, который возвращает пользователя и его предметы из модели User и CollectibleItem
    из связи many-to-many athlete = models.ManyToManyField(User, related_name="collectible_items")
    """

    # Переопределяем метод для получения списка предметов
    items = CollectibleItemSerializer(many=True, read_only=True)

    class Meta:
        # Переопределяем модель для CouchAthleteSerializer
        model = User
        # Добавляем поле items к полям CouchAthleteSerializer
        fields = CouchAthleteSerializer.Meta.fields + ("items",)
