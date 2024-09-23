import json

import requests_mock
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from triptuner.models import Destination, Itinerary, ItineraryDestination


class UserTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="ellie", password="loxodonto")
        self.user2 = User.objects.create_user(username="simba", password="panthera")

    def test_get_users_list(self):
        """
        Ensure we can list users
        """
        response = self.client.get("/api/users/")

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the number of users and contents
        users = response.json()
        self.assertEqual(len(users), 2)
        usernames = [user["username"] for user in users]
        self.assertIn("ellie", usernames)
        self.assertIn("simba", usernames)


class DestinationTest(APITestCase):
    def setUp(self):
        # Create destinations. Dummy data provided by an LLM.
        self.destination1 = Destination.objects.create(
            name="Nurnenharad",
            description="A volcanic wasteland south of Mordor, where slaves toil near the Sea of Núrnen.",
            type="poi",
            latitude=-38.0,
            longitude=63.5,
        )
        self.destination1 = Destination.objects.create(
            name="Galadorn",
            description="An ancient Elven stronghold hidden deep within the Ered Luin mountains.",
            type="city",
            latitude=-33.2,
            longitude=-23.1,
        )
        self.user = User.objects.create_user(username="admin", is_staff=1, is_superuser=1)

    def test_get_destinations_list(self):
        """
        Ensure we can list destinations
        """
        response = self.client.get("/api/destinations/")

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the number of destinations and contents
        destinations = response.json()
        self.assertEqual(len(destinations), 2)
        names = [destination["name"] for destination in destinations]
        self.assertIn("Nurnenharad", names)
        self.assertIn("Galadorn", names)

    def test_get_destinations_list_with_filter(self):
        """
        Ensure we can filter for a destination, using types
        """
        query_params = {"type": "city"}
        response = self.client.get("/api/destinations/", query_params=query_params)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the number of destinations and contents
        destinations = response.json()
        self.assertEqual(len(destinations), 1)
        self.assertEquals(destinations[0]["name"], "Galadorn")

    def test_post_destination(self):
        """
        Ensure we can create a destination
        """
        data = {
            "name": "Lothurien",
            "description": "A mystical forest land where time flows differently.",
            "type": "country",
            "latitude": -15.4,
            "longitude": 45.6,
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/destinations/", data=data)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the response contents
        destination = response.json()
        self.assertEquals(destination["name"], "Lothurien")

        result = Destination.objects.get(name="Lothurien")

        self.assertEquals(result.description, "A mystical forest land where time flows differently.")


class ItineraryTest(APITestCase):
    def setUp(self):
        # Create destinations, dummy data provided by an LLM.
        self.destination1 = Destination.objects.create(
            name="Kijani Plains",
            description="A vast savanna rich in biodiversity.",
            type="ecosystem",
            latitude=-2.515,
            longitude=37.761,
        )

        self.destination2 = Destination.objects.create(
            name="Mara Wetlands",
            description="A critical wetland system supporting sustainable agriculture.",
            type="wetland",
            latitude=-1.317,
            longitude=34.763,
        )

        self.user = User.objects.create_user(username="admin", is_staff=1, is_superuser=1)

    def test_post_itinerary(self):
        """
        Ensure we can create an itinerary
        """
        data = {
            "name": "Trip 1",
            "description": "A field trip for some ground truthing.",
            "start_date": "2024-09-23",
            "end_date": "2024-09-25",
            "destinations": [
                {"destination": self.destination1.id, "visit_order": 1},
                {"destination": self.destination2.id, "visit_order": 2},
            ],
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/itineraries/", data=json.dumps(data), content_type="application/json")

        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the response contents
        itinerary = response.json()
        self.assertEquals(itinerary["name"], "Trip 1")

        result = Itinerary.objects.get(name="Trip 1")

        self.assertEquals(result.destinations.all()[0].description, "A vast savanna rich in biodiversity.")


class ItineraryDestinationWeatherViewTests(APITestCase):

    def setUp(self):
        # Set up some test data
        self.destination = Destination.objects.create(name="Test City", type="city", latitude=51.5074, longitude=-0.1278)

        self.itinerary = Itinerary.objects.create(
            name="Test Itinerary",
            description="Test itinerary description",
            start_date="2024-09-20",
            end_date="2024-09-25",
        )

        self.itinerary_destination = ItineraryDestination.objects.create(
            itinerary=self.itinerary, destination=self.destination, visit_order=1
        )

    @requests_mock.Mocker()
    def test_get_weather_success(self, mocker):
        # Mock the Open-Meteo API response
        mocker.get(
            "https://api.open-meteo.com/v1/forecast",
            json={"hourly": {"temperature_2m": [15.0, 16.0, 17.0]}},
            status_code=200,
        )

        # Make request to the view
        url = reverse(
            "get_itinerary_destination_weather",
            kwargs={
                "itinerary_id": self.itinerary.id,
                "itinerary_destination_order": self.itinerary_destination.visit_order,
            },
        )

        response = self.client.get(url)

        # Check that the response is successful and contains mocked weather data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("hourly", response.json())
        self.assertIn("temperature_2m", response.json()["hourly"])

    @requests_mock.Mocker()
    def test_get_weather_missing_coordinates(self, mocker):
        # Update destination to have no coordinates
        self.destination.latitude = None
        self.destination.longitude = None
        self.destination.save()

        # Make request to the view
        url = reverse(
            "get_itinerary_destination_weather",
            kwargs={
                "itinerary_id": self.itinerary.id,
                "itinerary_destination_order": self.itinerary_destination.visit_order,
            },
        )

        response = self.client.get(url)

        # Check for a 400 error due to missing coordinates
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Invalid coordinates for this destination"})
