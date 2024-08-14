from django.conf import settings
from django.db import models

from book.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ManyToManyField(Book, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    def __str__(self) -> str:
        return f"{self.book.title} borrowed by {self.user.email}"

    @property
    def is_active(self) -> bool:
        return self.actual_return_date is None
