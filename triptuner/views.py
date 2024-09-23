import requests
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from triptuner.models import Destination, Itinerary, ItineraryDestination
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


class ItineraryDestinationWeatherView(RetrieveAPIView):
    queryset = ItineraryDestination.objects.all()
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]

    def retrieve(self, request, *args, **kwargs):
        itinerary_id = kwargs.get("itinerary_id")
        itinerary_destination_order = kwargs.get("itinerary_destination_order")

        try:
            itinerary_destination = ItineraryDestination.objects.get(
                itinerary_id=itinerary_id, visit_order=itinerary_destination_order
            )
        except ItineraryDestination.DoesNotExist:
            return JsonResponse({"error": "Itinerary destination not found"}, status=404)

        destination = itinerary_destination.destination
        latitude = destination.latitude
        longitude = destination.longitude

        if not latitude or not longitude:
            return JsonResponse({"error": "Invalid coordinates for this destination"}, status=400)

        # Open-Meteo API call
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m",
            "start": request.GET.get("start"),  # optionally pass start time
            "end": request.GET.get("end"),  # optionally pass end time
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
        except requests.RequestException as e:
            return JsonResponse({"error": "Failed to fetch weather data", "details": str(e)}, status=500)

        return JsonResponse(response.json())
