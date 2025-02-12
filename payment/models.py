from django.db import models
from django_enum import EnumField

from borrowing.models import Borrowing


class Payment(models.Model):
    class StatusEnum(models.TextChoices):
        pending = "1", "Pending"
        paid = "2", "Paid"
        canceled = "3", "Canceled"

    class TypeEnum(models.TextChoices):
        payment = "1", "Payment"
        fine = "2", "Fine"

    status = EnumField(StatusEnum)
    payment_type = EnumField(TypeEnum)
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=100)
    money_to_pay = models.DecimalField(decimal_places=2, max_digits=10)

    class Meta:
        unique_together = ("borrowing", "payment_type")
