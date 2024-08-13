from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient


class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            password="password123",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_user(self):
        url = reverse("user:create")
        data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "newpassword123",
            "is_staff": False,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_user_model().objects.count(), 2)
        self.assertEqual(
            get_user_model().objects.get(email="newuser@example.com").email,
            "newuser@example.com",
        )

