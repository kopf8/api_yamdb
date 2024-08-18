import re

from rest_framework import serializers

from .models import CustomUser


def validate_username(value, instance=None):
    if value.lower() == 'me':
        raise serializers.ValidationError(
            "Using 'me' as a username is not allowed."
        )

    if re.search(r'^[a-zA-Z][a-zA-Z0-9-_.]{1,30}$', value) is None:
        raise serializers.ValidationError(
            f'Unaccepted symbols <{value}> in nickname.'
        )

    user_queryset = CustomUser.objects.filter(username=value)
    if instance is not None:
        user_queryset = user_queryset.exclude(pk=instance.pk)

    if re.search(r'^[a-zA-Z][a-zA-Z0-9-_.@]{1,20}$', value) is None:
        raise serializers.ValidationError(
            f'Unaccepted symbols <{value}> in nickname.',
        )

    if user_queryset.exists():
        raise serializers.ValidationError("This username is already taken.")

    return value


def validate_email(value, instance=None):
    # Проверка уникальности с учетом instance
    email_queryset = CustomUser.objects.filter(email=value)
    if instance is not None:
        email_queryset = email_queryset.exclude(pk=instance.pk)

    if email_queryset.exists():
        raise serializers.ValidationError("This email is already in use.")

    return value
