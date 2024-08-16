from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book


def sample_book(**params):
    defaults = {
        "title": "Sample Book",
        "author": "Author Name",
        "cover": "HARD",
        "inventory": 10,
        "daily_fee": 5.99,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


class AdminBookTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@test.com",
            password="password123",
            first_name="Admin",
            last_name="User",
        )
        self.client.force_authenticate(self.admin_user)

    def test_create_new_book_increases_inventory_if_exists(self):
        sample_book(title="Sample Book", author="Author Name", cover="HARD")

        payload = {
            "title": "Sample Book",
            "author": "Author Name",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": 5.99,
        }

        url = reverse("book:books-list")
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(title="Sample Book", author="Author Name", cover="HARD")
        self.assertEqual(book.inventory, 15)

    def test_update_existing_book_merges_inventory(self):
        book1 = sample_book(title="Sample Book", author="Author Name", cover="HARD")
        book2 = sample_book(title="Another Book", author="Another Author", cover="SOFT")

        payload = {
            "title": "Sample Book",
            "author": "Author Name",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": 7.99,
        }

        url = reverse("books:books-detail", args=[book2.id])
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book1.refresh_from_db()
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(book1.inventory, 15)

    def test_partial_update_existing_book_merges_inventory(self):
        book1 = sample_book(title="Sample Book", author="Author Name", cover="HARD")
        book2 = sample_book(title="Another Book", author="Another Author", cover="SOFT")

        payload = {
            "title": "Sample Book",
            "author": "Author Name",
            "cover": "HARD",
            "inventory": 5,
        }

        url = reverse("books:books-detail", args=[book2.id])
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book1.refresh_from_db()
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(book1.inventory, 15)

    def test_create_new_book(self):
        payload = {
            "title": "New Book",
            "author": "New Author",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": 6.99,
        }

        url = reverse("books:books-list")
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(title="New Book", author="New Author", cover="SOFT")
        self.assertEqual(book.inventory, 5)

    def test_read_book_inventory(self):
        book = sample_book()
        url = reverse("books:books-detail", args=[book.id])

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["inventory"], book.inventory)


class UserBookTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.common_user = get_user_model().objects.create_user(
            email="user@test.com",
            password="password123",
            first_name="Common",
            last_name="User",
        )
        self.client.force_authenticate(self.common_user)

    def test_common_user_cannot_create_book(self):
        self.client.force_authenticate(self.common_user)
        payload = {
            "title": "Unauthorized Book",
            "author": "Unauthorized Author",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": 5.99,
        }

        url = reverse("books:books-list")
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_common_user_cannot_update_book(self):
        self.client.force_authenticate(self.common_user)
        book = sample_book()

        payload = {
            "title": "Updated Title",
            "author": "Updated Author",
        }

        url = reverse("books:books-detail", args=[book.id])
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_can_get_books_list(self):
        self.client.force_authenticate(user=None)
        url = reverse("books:books-list")

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
