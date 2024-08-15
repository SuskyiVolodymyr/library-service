from rest_framework import viewsets

from book.models import Book
from book.permissions import IsAdminOrReadOnly
from book.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    """List all books. If the user is an admin, all books are listed.
    If the user is staff, all books are listed.
    If the user is not admin or staff, only books belonging to the user are listed.
    """

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
