from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

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
    filter_backends = [SearchFilter]
    search_fields = ["first_name", "last_name"]

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get("type", None)

        if type == "coach":
            return qs.filter(is_staff=True)

        elif type == "athlete":
            return qs.filter(is_staff=False)

        else:
            return qs


class StartRunAPIView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, pk=run_id)

        if run.status != "init":
            return Response(
                {"Ошибка": "Забег уже запущен или закончен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        run.status = "in_progress"
        run.save()

        serializer = RunSerializer(run)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StopRunAPIView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, pk=run_id)

        # Проверяем, что статус бега не "завершен"
        if run.status != "in_progress":
            return Response(
                {"Ошибка": "Забег еще не запущен"}, status=status.HTTP_400_BAD_REQUEST
            )

        run.status = "finished"
        run.save()

        serializer = RunSerializer(run)
        return Response(serializer.data, status=status.HTTP_200_OK)
