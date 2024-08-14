import stripe
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentSuccessView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "Payment was successful."})


class PaymentCancelView(APIView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "Payment was canceled or failed."})


class CreateCheckoutSessionView(APIView):
    def post(self, request, *args, **kwargs):
        DOMAIN = "http://127.0.0.1:8000"

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": "Book Borrowing Fee",
                            },
                            "unit_amount": 2000,  # e.g., $20.00
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url=f"{DOMAIN}/api/payment/success/",
                cancel_url=f"{DOMAIN}/api/payment/cancel/",
            )
            return JsonResponse({"checkout_url": checkout_session.url})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
