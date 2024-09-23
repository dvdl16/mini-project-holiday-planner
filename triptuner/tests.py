import json

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from triptuner.models import Destination, Itinerary


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
            name="Nurnenharad", description="A volcanic wasteland south of Mordor, where slaves toil near the Sea of Núrnen.", type="poi", latitude=-38.0, longitude=63.5
        )
        self.destination1 = Destination.objects.create(
            name="Galadorn", description="An ancient Elven stronghold hidden deep within the Ered Luin mountains.", type="city", latitude=-33.2, longitude=-23.1
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
        data = {"name": "Lothurien", "description": "A mystical forest land where time flows differently.", "type": "country", "latitude": -15.4, "longitude": 45.6}
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
        self.destination1 = Destination.objects.create(name="Kijani Plains", description="A vast savanna rich in biodiversity.", type="ecosystem", latitude=-2.515, longitude=37.761)

        self.destination2 = Destination.objects.create(
            name="Mara Wetlands",
            description="A critical wetland system supporting sustainable agriculture and protecting local communities from flooding.",
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
            "destinations": [{"destination": self.destination1.id, "visit_order": 1}, {"destination": self.destination2.id, "visit_order": 2}],
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
