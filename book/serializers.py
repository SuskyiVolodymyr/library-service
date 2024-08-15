from django.db import transaction
from rest_framework import serializers

from book.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "author", "cover", "inventory", "daily_fee"]

    def create(self, validated_data):
        """Create and return a new book."""
        book = Book.objects.filter(
            title=validated_data["title"],
            author=validated_data["author"],
            cover=validated_data["cover"],
        )
        if book:
            book = book[0]
            book.inventory += validated_data["inventory"]
            book.save()
            return book
        return Book.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update and return an existing book."""
        book = Book.objects.filter(
            title=validated_data["title"],
            author=validated_data["author"],
            cover=validated_data["cover"],
        ).exclude(id=instance.id)
        if book:
            with transaction.atomic():
                book = book[0]
                book.inventory += validated_data["inventory"]
                book.save()
                instance.delete()
                return book
        return super().update(instance, validated_data)


class BookReadSerializer(serializers.ModelSerializer):
    """Serializer for reading books ."""

    class Meta:
        model = Book
        fields = ["title", "author", "inventory"]
