from asgiref.sync import async_to_sync
from django.conf import settings
from django.db import models

from book.models import Book

from borrowing.telegram_bot import send_message


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ManyToManyField(Book, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    def __str__(self) -> str:
        return f"{self.book.title} borrowed by {self.user.email}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            message = (
                f"New borrowing created:\n"
                f"User: {self.user.email}\n"
                f"Books: "
                f"Borrow Date: {self.borrow_date}\n"
                f"Expected Return Date: {self.expected_return_date}"
            )
            async_to_sync(send_message)(message)

    @property
    def is_active(self) -> bool:
        return self.actual_return_date is None
