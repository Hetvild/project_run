from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app_run.models import Run
from app_run.serializers import RunSerializer, CouchAthleteSerializer


# Create your views here.
@api_view(["GET"])
def company_details(request) -> Response:
    """
    Возвращает информацию о компании, данные берутся из settings.py
    """
    details = {
        "company_name": settings.COMPANY_NAME,
        "slogan": settings.SLOGAN,
        "contacts": settings.CONTACTS,
    }
    return Response(details)


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related("athlete").all()
    serializer_class = RunSerializer


class CouchAthleteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = CouchAthleteSerializer

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get("type", None)
        if type == "coach":
            print("type coach")
            return qs.filter(is_staff=True)
        elif type == "athlete":
            return qs.filter(is_staff=False)
        else:
            return qs
