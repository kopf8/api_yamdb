from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import ConfirmationCode, CustomUser
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
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role')


class SignupSerializer(serializers.ModelSerializer):
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
        fields = ('username', 'email')


class ConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    class Meta:
        model = ConfirmationCode
