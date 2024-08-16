import stripe
from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet
from django.http import JsonResponse
from rest_framework import status

from borrowing.models import Borrowing
from borrowing.telegram_helper import send_message
from payment.models import Payment


stripe.api_key = settings.STRIPE_SECRET_KEY

FINE_MULTIPLIER = 2


def payment_create_borrowing(borrowing_id) -> JsonResponse:
    """
    Create a payment session for a new borrowing.
    """
    borrowing = Borrowing.objects.get(id=borrowing_id.value)
    books = borrowing.book.all()
    borrowing_days = borrowing.expected_return_date - borrowing.borrow_date
    money_to_pay = (
        borrowing_days.days * int(sum(book.daily_fee for book in books)) * 100
    )
    return payment_helper(
        borrowing=borrowing, money_to_pay=money_to_pay, books=books, payment_type="1"
    )


def fine_payment(borrowing: Borrowing) -> JsonResponse:
    """
    Create a payment session for a late fee.
    """
    books = borrowing.book.all()
    overdue_days = borrowing.actual_return_date - borrowing.expected_return_date
    money_to_pay = (
        overdue_days.days
        * int(sum(book.daily_fee for book in books))
        * 100
        * FINE_MULTIPLIER
    )
    return payment_helper(
        borrowing=borrowing, money_to_pay=money_to_pay, books=books, payment_type="2"
    )


def payment_helper(
    borrowing: Borrowing, money_to_pay: int, books: QuerySet, payment_type: str
) -> JsonResponse:
    """
    Helper function to create a Stripe checkout session and save payment details.
    """
    domain = "http://127.0.0.1:8000"
    with transaction.atomic():
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": ", ".join([book.title for book in books]),
                            },
                            "unit_amount": money_to_pay,
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url=f"{domain}/api/payment/success/{borrowing.id}/?payment_type={payment_type}",
                cancel_url=f"{domain}/api/payment/cancel/{borrowing.id}/?payment_type={payment_type}",
            )
            Payment.objects.create(
                status="1",
                payment_type=payment_type,
                borrowing=borrowing,
                session_url=checkout_session.url,
                session_id=checkout_session.id,
                money_to_pay=round(money_to_pay / 100, 2),
            )
            return JsonResponse(
                {"checkout_url": checkout_session.url}, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


def telegram_payment_notification(
    payment: Payment, borrowing: Borrowing, payment_status: str, payment_type: str
) -> None:
    """
    Send Telegram message with payment details.
    """
    book_titles = ", ".join([book.title for book in borrowing.book.all()])
    message = (
        f"{payment_status}:\n"
        f"User: {borrowing.user.email}\n"
        f"Books: {book_titles}\n"
        f"Payment type: {payment_type}\n"
        f"Amount: {payment.money_to_pay}$"
    )
    send_message(message)
