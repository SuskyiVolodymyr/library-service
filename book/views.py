import django_filters
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from book.models import Book
from book.permissions import IsAdminOrReadOnly
from book.serializers import BookSerializer


class BookPagination(PageNumberPagination):
	page_size = 5
	max_page_size = 100


class BookFilters(django_filters.FilterSet):
	title = django_filters.CharFilter(lookup_expr="icontains")
	author = django_filters.CharFilter(lookup_expr="icontains")

	class Meta:
		model = Book
		fields = ["title", "author"]


class BookViewSet(viewsets.ModelViewSet):
	"""
	A viewset for viewing and editing book instances.
	- List and retrieve actions use the "BookSerializer".
	- Create action uses the "BookSerializer".
	- The queryset is filtered based on the authenticated user.
	"""

	queryset = Book.objects.all()
	serializer_class = BookSerializer
	permission_classes = [IsAdminOrReadOnly]
	pagination_class = BookPagination
	filterset_class = BookFilters
