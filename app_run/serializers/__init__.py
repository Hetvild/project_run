# Импортируем функции из пакетов
from .challenge import ChallengeSerializer, ChallengeSummarySerializer
from .collectible import CollectibleItemSerializer
from .position import PositionSerializer
from .run import RunSerializer
from .user import (
    UserSerializer,
    CouchAthleteSerializer,
    CouchAthleteItemsSerializer,
    AthleteInfoSerializer,
    AthleteWithCoachSerializer,
    CoachWithAthletesSerializer,
)

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
    "ChallengeSummarySerializer",
]
