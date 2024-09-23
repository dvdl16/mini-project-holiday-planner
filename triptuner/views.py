from django.contrib.auth.models import User
from rest_framework import viewsets

from triptuner.models import Destination, Itinerary
from triptuner.serializers import DestinationSerializer, ItinerarySerializer, UserSerializer

# ViewSets define the view behavior.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_fields = ["is_staff", "is_active"]


class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    filterset_fields = ["type", "latitude", "longitude"]


class ItineraryViewSet(viewsets.ModelViewSet):
    queryset = Itinerary.objects.all()
    serializer_class = ItinerarySerializer
    filterset_fields = ["name", "start_date", "end_date"]

    # Restrict allowed HTTP methods
    http_method_names = ["get", "post", "delete"]
