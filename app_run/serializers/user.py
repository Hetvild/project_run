from django.contrib.auth.models import User
from rest_framework import serializers

from app_run.models import AthleteInfo, Subscribe
from app_run.serializers.collectible import CollectibleItemSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "last_name", "first_name")


class CoachAthleteSerializer(serializers.ModelSerializer):
    # Определяем вычисляемое поле для вывода типа пользователя
    type = serializers.SerializerMethodField()
    runs_finished = serializers.ReadOnlyField()
    rating = serializers.FloatField(read_only=True)

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
            "rating",
        )

    def get_type(self, obj) -> str:
        if obj.is_staff:
            return "coach"
        else:
            return "athlete"


class CoachAthleteItemsSerializer(CoachAthleteSerializer):
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
        fields = CoachAthleteSerializer.Meta.fields + ("items",)


class CoachWithAthletesSerializer(CoachAthleteSerializer):
    """
    Для ТРЕНЕРА: добавляет поле athletes — список ID атлетов
    """

    athletes = serializers.SerializerMethodField()

    class Meta(CoachAthleteSerializer.Meta):
        fields = CoachAthleteSerializer.Meta.fields + ("athletes",)

    def get_athletes(self, obj):
        # Получаем список ID атлетов, подписанных на этого тренера
        return list(
            Subscribe.objects.filter(coach=obj).values_list("athlete_id", flat=True)
        )


class AthleteWithCoachSerializer(CoachAthleteSerializer):
    """
    Сериалайзер, который добавляет поле coach со списком его Атлетов
    """

    coach = serializers.SerializerMethodField()
    rating = serializers.FloatField(read_only=True)

    class Meta(CoachAthleteSerializer.Meta):
        fields = CoachAthleteSerializer.Meta.fields + ("coach",)

    def get_coach(self, obj):
        # Ищем первую подписку атлета на тренера
        subscription = Subscribe.objects.filter(athlete=obj).first()
        if subscription:
            return subscription.coach_id  # возвращаем только ID
        return None


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


class AthleteSummarySerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "full_name", "username"]

    def get_full_name(self, obj):
        # Используем first_name и last_name из User
        return f"{obj.first_name} {obj.last_name}".strip()
