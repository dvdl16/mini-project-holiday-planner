from django.contrib.auth.models import User
from rest_framework import serializers

from triptuner.models import Destination, Itinerary, ItineraryDestination


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "is_staff"]


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ["id", "name", "description", "type", "latitude", "longitude"]


class ItineraryDestinationSerializer(serializers.ModelSerializer):
    destination = serializers.PrimaryKeyRelatedField(queryset=Destination.objects.all())

    class Meta:
        model = ItineraryDestination
        fields = ["id", "destination", "visit_order"]


class ItinerarySerializer(serializers.ModelSerializer):
    destinations = ItineraryDestinationSerializer(many=True, source="itinerarydestination_set")

    class Meta:
        model = Itinerary
        fields = ["id", "name", "description", "start_date", "end_date", "destinations"]

    def create(self, validated_data):
        destinations = validated_data.pop("itinerarydestination_set", [])
        itinerary = Itinerary.objects.create(**validated_data)

        for destination in destinations:
            ItineraryDestination.objects.create(
                itinerary=itinerary, destination=destination["destination"], visit_order=len(destinations)
            )

        return itinerary
