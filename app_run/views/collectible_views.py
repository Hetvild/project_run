from rest_framework import viewsets

from app_run.models import CollectibleItem
from app_run.serializers import CollectibleItemSerializer


class CollectibleItemViewSet(viewsets.ModelViewSet):
    queryset = CollectibleItem.objects.all()
    serializer_class = CollectibleItemSerializer
