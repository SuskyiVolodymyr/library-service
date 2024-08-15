from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from book.serializers import BookReadSerializer
from borrowing.models import Borrowing
from borrowing.telegram_helper import send_message


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookReadSerializer(read_only=True, many=True)
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field="email")

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]
        read_only_fields = ["id", "borrow_date", "book", "user"]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["id", "expected_return_date", "book"]

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
                user=self.context["request"].user, **validated_data
            )
            borrowing.book.add(*books)

            book_titles = ", ".join([book.title for book in books])
            message = (
                f"New borrowing created:\n"
                f"User: {borrowing.user.email}\n"
                f"Book: {book_titles}\n"
                f"Borrow Date: {borrowing.borrow_date}\n"
                f"Expected return date: {borrowing.expected_return_date}"
            )
            send_message(message)

            return borrowing
