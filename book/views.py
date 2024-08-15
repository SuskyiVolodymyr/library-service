from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from book.models import Book
from book.permissions import IsAdminOrReadOnly
from book.serializers import BookSerializer


class BookPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


class BookViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing book instances.
    - List and retrieve actions use the `BookSerializer`.
    - Create action uses the `BookSerializer`.
    - The queryset is filtered based on the authenticated user.
    """

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = BookPagination
