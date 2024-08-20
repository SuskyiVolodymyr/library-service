import datetime

from django.db import transaction
from django.db.models import QuerySet
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

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

    queryset = Borrowing.objects.select_related("user").prefetch_related(
        "book"
    )
    permission_classes = [IsAuthenticated]
    filterset_fields = ("user_id",)

    def get_serializer_class(self) -> serializers.SerializerMetaclass:
        """
        Return the appropriate serializer class depending on the action.
        """
        if self.action in ["list", "retrieve"]:
            return BorrowingSerializer
        return BorrowingCreateSerializer

    def get_queryset(self) -> QuerySet:
        """
        Return a filtered queryset depending
        on the user's permissions and query parameters.
        """
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        is_active = self.request.query_params.get("is_active")

        if is_active is not None:
            is_active = is_active.lower() == "true"
            queryset = queryset.filter(actual_return_date__isnull=is_active)

        return queryset

    def create(self, request: Request, *args, **kwargs) -> JsonResponse:
        """
        Create a new borrowing instance and initiate the payment process.
        """
        serializer = self.get_serializer_class()(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return payment_create_borrowing(
            borrowing_id=serializer.data["id"],
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="return",
        permission_classes=[IsAuthenticated],
    )
    def return_book(
        self, request: Request, pk: int = None
    ) -> Response | JsonResponse:
        """
        Return a borrowed book. If the book is returned late,
        a fine payment is processed.
        """
        borrowing = get_object_or_404(Borrowing, pk=pk)
        if borrowing.actual_return_date:
            raise ValidationError("You already returned book")
        with transaction.atomic():
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
                name="is_active",
                description="Filter borrowings "
                "by whether they are active or not.",
                required=False,
                type=str,
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)
