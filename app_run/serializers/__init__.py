# Импортируем функции из пакетов
from .user import (
    UserSerializer,
    CouchAthleteSerializer,
    CouchAthleteItemsSerializer,
    AthleteInfoSerializer,
    AthleteWithCoachSerializer,
    CoachWithAthletesSerializer,
)
from .run import RunSerializer
from .collectible import CollectibleItemSerializer
from .challenge import ChallengeSerializer
from .position import PositionSerializer

# Указываем какие имена импортируем
__all__ = [
    "UserSerializer",
    "CouchAthleteSerializer",
    "CouchAthleteItemsSerializer",
    "AthleteInfoSerializer",
    "RunSerializer",
    "CollectibleItemSerializer",
    "ChallengeSerializer",
    "PositionSerializer",
    "AthleteWithCoachSerializer",
    "CoachWithAthletesSerializer",
]
