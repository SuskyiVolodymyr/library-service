from rest_framework import serializers

from borrowing.serializers import BorrowingSerializer
from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
	"""
	Serializer for the Payment model.
	Attributes:
	    borrowing (BorrowingSerializer):
	    The serializer for the related borrowing.
	    status (CharField): Human-readable status of the payment.
	    payment_type (CharField): Human-readable type of payment.
	"""

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
	"""
	Serializer for listing payments, with a reduced set of fields.
	"""

	class Meta:
		model = Payment
		fields = ("id", "status", "borrowing", "money_to_pay")
