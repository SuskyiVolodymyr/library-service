from django.urls import path

from payment.views import (
    CreateCheckoutSessionView,
    PaymentSuccessView,
    PaymentCancelView,
)

app_name = "payment"

urlpatterns = [
    path(
        "create-checkout-session/",
        CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path("success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]
