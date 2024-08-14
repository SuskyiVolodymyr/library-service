from datetime import date

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from book.serializers import BookReadSerializer
from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookReadSerializer(read_only=True, many=True)
    user = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="email"
    )

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user"
        ]
        read_only_fields = [
            "id",
            "borrow_date",
            "book",
            "user"
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["expected_return_date", "book"]

    def validate(self, attrs):
        borrow_date = timezone.now().date()
        expected_return_date = attrs.get("expected_return_date")

        if expected_return_date < borrow_date:
            raise serializers.ValidationError(
                "The expected return date cannot be earlier than the borrowing date."
            )
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            books = validated_data.pop("book")
            for book in books:
                if book.inventory <= 0:
                    raise serializers.ValidationError("Book is out of stock.")
                book.inventory -= 1
                book.save()

                borrowing = Borrowing.objects.create(
                    user=self.context["request"].user,
                    **validated_data
                )
            borrowing.book.add(*books)

            return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    actual_return_date = serializers.DateField()

    class Meta:
        model = Borrowing
        fields = ["actual_return_date"]

    def validate_actual_return_date(self, value):
        if value > date.today():
            raise serializers.ValidationError(
                "The actual return date cannot be in the future."
            )
        return value

    def validate(self, data):
        borrowing = self.instance

        if borrowing.actual_return_date is not None:
            raise serializers.ValidationError(
                "This book has already been returned."
            )

        return data

    def update(self, instance, validated_data):
        instance.actual_return_date = validated_data["actual_return_date"]
        for book in instance.book.all():
            book.inventory += 1
            book.save()
        instance.save()
        return instance
