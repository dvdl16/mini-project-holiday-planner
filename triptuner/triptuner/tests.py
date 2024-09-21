from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class UserListTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="ellie", password="loxodonto")
        self.user2 = User.objects.create_user(username="simba", password="panthera")

    def test_get_users_list(self):
        """
        Ensure we can list users
        """
        # url = reverse('users-list')
        response = self.client.get("/api/users/")

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the number of users and contents
        users = response.json()
        self.assertEqual(len(users), 2)
        usernames = [user["username"] for user in users]
        self.assertIn("ellie", usernames)
        self.assertIn("simba", usernames)
