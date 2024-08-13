from django.core.exceptions import ValidationError
from django.db import models


class Book(models.Model):
    COVER_CHOICES = [
        ("HARD", "Hard"),
        ("SOFT", "Soft"),
    ]

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.CharField(max_length=100, choices=COVER_CHOICES)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["title", "author", "cover"], name="unique_book_constraint"
            )
        ]

    def save(self, *args, **kwargs):
        if (
            not self.pk
            and Book.objects.filter(
                title=self.title, author=self.author, cover=self.cover
            ).exists()
        ):
            raise ValidationError(
                "A book with this title, author, and cover already exists."
            )

        if self.inventory is None:
            self.inventory = 1

        super(Book, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.author}"
