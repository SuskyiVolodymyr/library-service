from datetime import date, timedelta
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from book.models import Book
from borrowing.models import Borrowing

User = get_user_model()


class BorrowingUserTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            first_name="User",
            last_name="Example",
            is_staff=False,
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover="Soft",
            inventory=5,
            daily_fee=1.50,
        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date=(date.today() + timedelta(days=10)), user=self.user
        )
        self.borrowing.book.set([self.book])
        self.borrowing_url = reverse("borrowings:borrowing-list")
        self.client.force_authenticate(user=self.user)

    @patch("borrowing.serializers.send_message")
    def test_create_borrowing_authenticated(self, mock_send_message):
        data = {
            "expected_return_date": (date.today() + timedelta(days=10)),
            "book": [self.book.id],
        }
        response = self.client.post(self.borrowing_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 4)
        mock_send_message.assert_called_once()

    def test_create_borrowing_out_of_stock(self):
        self.book.inventory = 0
        self.book.save()
        data = {
            "expected_return_date": (date.today() + timedelta(days=10)),
            "book": [self.book.id],
        }
        response = self.client.post(self.borrowing_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Book is out of stock.", str(response.data))

    def test_create_borrowing_invalid_return_date(self):
        data = {"expected_return_date": "2024-08-01", "book": [self.book.id]}
        response = self.client.post(self.borrowing_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "The expected return date cannot be earlier than the borrowing date.",
            str(response.data),
        )

    def test_return_book(self):
        self.borrowing.book.add(self.book)
        return_url = reverse(
            "borrowings:borrowing-return-book", args=[self.borrowing.id]
        )
        response = self.client.get(return_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 6)

    def test_return_book_already_returned(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            expected_return_date=(date.today() + timedelta(days=10)),
            actual_return_date=(date.today() + timedelta(days=9)),
        )
        borrowing.book.add(self.book)
        return_url = reverse("borrowings:borrowing-return-book", args=[borrowing.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(return_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You already returned book", str(response.data))

    def test_user_sees_only_their_borrowings(self):
        response = self.client.get(self.borrowing_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.borrowing.id)


class BorrowingAdminTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password="password123",
            first_name="Admin",
            last_name="Example",
            is_staff=True,
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover="Soft",
            inventory=5,
            daily_fee=1.50,
        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date=(date.today() + timedelta(days=10)),
            user=self.admin_user,
        )
        self.borrowing.book.set([self.book])
        self.borrowing_url = reverse("borrowings:borrowing-list")
        self.client.force_authenticate(user=self.admin_user)

    def test_list_borrowings_admin_user(self):
        response = self.client.get(self.borrowing_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_user_can_filter_by_user_id(self):
        another_user = User.objects.create_user(
            email="another_user@example.com",
            password="password123",
            first_name="Another",
            last_name="User",
        )
        another_borrowing = Borrowing.objects.create(
            expected_return_date=(date.today() + timedelta(days=5)), user=another_user
        )
        another_borrowing.book.set([self.book])

        response = self.client.get(self.borrowing_url, {"user_id": another_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], another_borrowing.id)

    def test_admin_user_can_filter_by_is_active(self):
        response = self.client.get(self.borrowing_url, {"is_active": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.borrowing.id)


class BorrowingUnauthorizedTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.borrowing_url = reverse("borrowings:borrowing-list")

    def test_unauthenticated_access(self):
        response = self.client.get(self.borrowing_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
