# Импортируем функции из пакетов
from .challenge import ChallengeSerializer, ChallengeSummarySerializer
from .collectible import CollectibleItemSerializer
from .position import PositionSerializer
from .run import RunSerializer
from .user import (
    UserSerializer,
    CoachAthleteSerializer,
    CoachAthleteItemsSerializer,
    AthleteInfoSerializer,
    AthleteWithCoachSerializer,
    CoachWithAthletesSerializer,
)

# Указываем какие имена импортируем
__all__ = [
    "UserSerializer",
    "CoachAthleteSerializer",
    "CoachAthleteItemsSerializer",
    "AthleteInfoSerializer",
    "RunSerializer",
    "CollectibleItemSerializer",
    "ChallengeSerializer",
    "PositionSerializer",
    "AthleteWithCoachSerializer",
    "CoachWithAthletesSerializer",
    "ChallengeSummarySerializer",
]
