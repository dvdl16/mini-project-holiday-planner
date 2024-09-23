from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from triptuner.models import Destination


class UserListTest(APITestCase):
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


class DestinationListTest(APITestCase):
    def setUp(self):
        """
        Create destinations. Dummy data provided by an LLM.
        """
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
