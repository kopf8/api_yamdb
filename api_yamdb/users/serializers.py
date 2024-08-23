import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers

from .models import CustomUser

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150
    )
    email = serializers.EmailField(
        max_length=254
    )
    role = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                "Using 'me' as a username is not allowed.")

        if re.search(r'^[a-zA-Z][a-zA-Z0-9-_.]{1,20}$', value) is None:
            raise serializers.ValidationError(
                f'Unaccepted symbols <{value}> in nickname.')

        try:
            user = CustomUser.objects.get(username=value)
            if self.instance is None or user.id != self.instance.id:
                raise serializers.ValidationError(
                    "This username is already taken.")
        except ObjectDoesNotExist:
            pass

        return value

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
            if self.instance is None or user.id != self.instance.id:
                raise serializers.ValidationError(
                    "This email is already in use.")
        except ObjectDoesNotExist:
            pass

        return value

    def validate_role(self, value):
        if value not in ['user', 'superuser', 'admin', 'moderator']:
            raise serializers.ValidationError(
                f"Role '{value}' is not a valid choice."
            )
        return value


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
        return UserSerializer.validate_username(self, value)

    def validate_email(self, value):
        return UserSerializer.validate_email(self, value)


class ConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
