from rest_framework import serializers
from .models import TelegramUser, Payment, Message


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ["telegram_id", "first_name", "phone", "username", "date"]

    def validate(self, data):
        # Ensure the first name is present
        if not data.get("first_name"):
            raise serializers.ValidationError({"first_name": "This field is required."})
        return data


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["user", "chek", "is_confirmed"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["user", "text", "image", "video", "date"]
