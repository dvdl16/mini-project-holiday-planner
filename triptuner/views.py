from django.contrib.auth.models import User
from rest_framework import viewsets

from triptuner.models import Destination
from triptuner.serializers import DestinationSerializer, UserSerializer

# ViewSets define the view behavior.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_fields = ["is_staff", "is_active"]


class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    filterset_fields = ["type", "latitude", "longitude"]
