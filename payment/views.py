from django.http import JsonResponse
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from borrowing.models import Borrowing
from payment.models import Payment
from payment.payment_helper import telegram_payment_notification
from payment.serializers import PaymentSerializer, PaymentListSerializer


class PaymentSuccessView(APIView):
    def get(self, request, *args, **kwargs):
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
            payment_type="Payment",
        )
        return JsonResponse({"message": "Payment was successful."})


class PaymentCancelView(APIView):
    def get(self, request: Request, *args, **kwargs):
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
            payment_type="Fine",
        )
        return JsonResponse({"message": "Payment was canceled or failed."})


class PaymentViewSet(GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Payment.objects.select_related("borrowing")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        return PaymentSerializer

    def get_queryset(self):
        queryset = self.queryset.all()
        status = self.request.query_params.get("status")
        if status == "canceled":
            queryset = queryset.filter(status="3")
        if status == "paid":
            queryset = queryset.filter(status="2")
        if status == "pending":
            queryset = queryset.filter(status="1")
        if not self.request.user.is_staff:
            return queryset.filter(borrowing__user_id=self.request.user.id)
        return queryset
