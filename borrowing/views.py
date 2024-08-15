import datetime

from django.http import JsonResponse
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
    queryset = Borrowing.objects.select_related("user").prefetch_related("book")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return BorrowingSerializer
        return BorrowingCreateSerializer

    def get_queryset(self):
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
        permission_classes=[IsAuthenticated],
    )
    def return_book(self, request: Request, pk=None) -> Response | JsonResponse:
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
