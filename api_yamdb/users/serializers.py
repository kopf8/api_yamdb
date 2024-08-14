from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import CustomUser
from .validators import validate_username, validate_email

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[validate_username]
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[validate_email]
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150
    )
    email = serializers.EmailField(
        max_length=254
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

    def validate_username(self, value):
        # Get the instance if it exists
        instance = self.instance
        return validate_username(value, instance)

    def validate_email(self, value):
        # Get the instance if it exists
        instance = self.instance
        return validate_email(value, instance)


class ConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
