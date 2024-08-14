from rest_framework import serializers

from borrowing.serializers import BorrowingSerializer
from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    borrowing = BorrowingSerializer(read_only=True)
    status = serializers.CharField(source="get_status_display", read_only=True)
    payment_type = serializers.CharField(
        source="get_payment_type_display", read_only=True
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "payment_type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        )


class PaymentListSerializer(PaymentSerializer):
    class Meta:
        model = Payment
        fields = ("id", "status", "borrowing", "money_to_pay")
