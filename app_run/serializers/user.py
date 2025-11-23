from django.contrib.auth.models import User
from rest_framework import serializers

from app_run.models import AthleteInfo
from app_run.serializers.collectible import CollectibleItemSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "last_name", "first_name")


class CouchAthleteSerializer(serializers.ModelSerializer):
    # Определяем вычисляемое поле для вывода типа пользователя
    type = serializers.SerializerMethodField()
    runs_finished = serializers.ReadOnlyField()

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
