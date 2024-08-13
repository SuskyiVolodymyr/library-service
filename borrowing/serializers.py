from django.db import transaction
from rest_framework import serializers

from book.serializers import BookReadSerializer
from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookReadSerializer(read_only=True)
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field="email")

    class Meta:
        model = Borrowing
        fields = ["id", "borrow_date", "expected_return_date", "actual_return_date", "book", "user"]
        read_only_fields = ["id", "borrow_date", "book", "user"]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["expected_return_date", "book"]

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data.get("book")
            if book.inventory <= 0:
                raise serializers.ValidationError("Book is out of stock.")
            book.inventory -= 1
            book.save()

            borrowing = Borrowing.objects.create(
                user=self.context['request'].user,
                **validated_data
            )

            return borrowing
