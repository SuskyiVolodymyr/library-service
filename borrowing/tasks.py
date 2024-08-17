from celery import shared_task
from datetime import date

from borrowing.models import Borrowing
from borrowing.telegram_helper import send_message


@shared_task
def check_overdue_borrowings() -> None:
    today = date.today()
    all_borrowings = Borrowing.objects.filter(actual_return_date__isnull=True)

    if all_borrowings.exists():
        for borrowing in all_borrowings:
            books_title = ", ".join(
                borrowing.book.values_list("title", flat=True)
            )
            status = (
                "Overdue"
                if borrowing.expected_return_date <= today
                else "Not overdue"
            )
            message = (
                f"Overdue borrowing: {books_title} by {borrowing.user.email}\n"
                f"Status: {status}"
            )
            send_message(message)
    else:
        send_message("No active borrowings today!")
