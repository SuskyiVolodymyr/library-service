import datetime

from django.http import JsonResponse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from book.permissions import IsAdminOrReadOnly
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingCreateSerializer,
    BorrowingSerializer,
)
from payment.payment_helper import payment_create_borrowing, fine_payment


class BorrowingViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing borrowing instances.
    - List and retrieve actions use the `BorrowingSerializer`.
    - Create action uses the `BorrowingCreateSerializer`.
    - The queryset is filtered based on the authenticated user.
    """

    queryset = Borrowing.objects.select_related("user").prefetch_related("book")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Return the appropriate serializer class depending on the action.
        """
        if self.action in ["list", "retrieve"]:
            return BorrowingSerializer
        return BorrowingCreateSerializer

    def get_queryset(self):
        """
        Return a filtered queryset depending on the user's permissions and query parameters.
        """
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if user.is_staff and user_id:
            queryset = queryset.filter(user__id=user_id)

        if is_active is not None:
            is_active = is_active.lower() == "true"
            queryset = queryset.filter(actual_return_date__isnull=is_active)

        return queryset

    def create(self, request: Request, *args, **kwargs) -> JsonResponse:
        """
        Create a new borrowing instance and initiate the payment process.
        """
        serializer = BorrowingCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return payment_create_borrowing(
            borrowing_id=serializer["id"],
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="return",
        permission_classes=[IsAdminOrReadOnly],
    )
    def return_book(self, request: Request, pk=None) -> Response | JsonResponse:
        """
        Return a borrowed book. If the book is returned late, a fine payment is processed.
        """
        borrowing = self.get_object()
        if borrowing.actual_return_date:
            raise ValidationError("You already returned book")
        borrowing.actual_return_date = datetime.date.today()
        borrowing.save()
        for book in borrowing.book.all():
            book.inventory += 1
            book.save()
        if borrowing.expected_return_date < borrowing.actual_return_date:
            return fine_payment(borrowing=borrowing)

        serializer = BorrowingSerializer(borrowing)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                description="Filter borrowings by user ID.",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="is_active",
                description="Filter borrowings by whether they are active or not.",
                required=False,
                type=str,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
