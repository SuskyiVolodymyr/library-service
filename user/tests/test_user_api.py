from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


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

    def test_update_user(self):
        url = reverse("user:manage")
        data = {"first_name": "Updated", "last_name": "User"}
        response = self.client.patch(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "User")

    def test_user_password_update(self):
        url = reverse("user:manage")
        data = {"password": "newpassword123"}
        self.client.patch(url, data, format="json")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))

    def test_retrieve_user(self):
        url = reverse("user:manage")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_obtain_token(self):
        url = reverse("user:token_obtain_pair")
        data = {"email": "testuser@example.com", "password": "password123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)





