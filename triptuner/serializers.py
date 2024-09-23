from django.contrib.auth.models import User
from rest_framework import serializers

from triptuner.models import Destination


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "is_staff"]


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ["id", "name", "description", "type", "latitude", "longitude"]
