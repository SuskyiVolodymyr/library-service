from django.db.models import QuerySet
from django.http import JsonResponse
from rest_framework import mixins, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from borrowing.models import Borrowing
from payment.models import Payment
from payment.payment_helper import telegram_payment_notification
from payment.serializers import PaymentSerializer, PaymentListSerializer


class PaymentSuccessView(APIView):
    def get(self, request: Request, *args, **kwargs) -> JsonResponse:
        """
        Handles successful payments.
        Retrieves the payment using the borrowing ID ("borrowing")
        and payment type ("payment_type") from the request.
        Updates the payment status to successful
        and sends a notification via Telegram.
        Returns a JSON response indicating success.
        """
        borrowing = Borrowing.objects.get(id=kwargs["pk"])
        payment_type = request.query_params["payment_type"]
        payment = Payment.objects.get(
            borrowing_id=borrowing.id, payment_type=payment_type
        )
        payment.status = "2"
        payment.save()
        telegram_payment_notification(
            payment=payment,
            borrowing=borrowing,
            payment_status="Success payment",
            payment_type=payment_type,
        )
        return JsonResponse({"message": "Payment was successful."})


class PaymentCancelView(APIView):
    def get(self, request: Request, *args, **kwargs) -> JsonResponse:
        """
        Handles canceled or failed payments.

        Retrieves the payment using the borrowing ID ("borrowing")
        and payment type ("payment_type") from the request.
        Updates the payment status to canceled/failed
        and sends a notification via Telegram.
        Returns a JSON response indicating success.
        """
        borrowing = Borrowing.objects.get(id=kwargs["pk"])
        payment_type = request.query_params["payment_type"]
        payment = Payment.objects.get(
            borrowing_id=borrowing.id, payment_type=payment_type
        )
        payment.status = "3"
        payment.save()
        telegram_payment_notification(
            payment=payment,
            borrowing=borrowing,
            payment_status="Canceled payment",
            payment_type=payment_type,
        )
        return JsonResponse({"message": "Payment was canceled or failed."})


class PaymentViewSet(
    GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    """
    ViewSet for managing payments.

    Allows retrieving a list of payments and individual payments.
    Supports filtering by payment status.
    """

    queryset = Payment.objects.select_related("borrowing")
    permission_classes = [IsAuthenticated]
    filterset_fields = ("status",)

    def get_serializer_class(self) -> serializers.SerializerMetaclass:
        """
        Return the appropriate serializer class based on the action.
        """
        if self.action == "list":
            return PaymentListSerializer
        return PaymentSerializer

    def get_queryset(self) -> QuerySet:
        """
        Returns the filtered queryset based on query parameters
        and user permissions.
        Filters payments by status (canceled/paid/pending) and user.
        Returns the filtered queryset.
        """
        queryset = self.queryset.select_related(
            "borrowing__user"
        ).prefetch_related("borrowing__book")
        if not self.request.user.is_staff:
            return queryset.filter(borrowing__user_id=self.request.user.id)
        return queryset
