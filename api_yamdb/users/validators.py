from rest_framework import serializers
from .models import CustomUser


def validate_username(value):
    if value.lower() == 'me':
        raise serializers.ValidationError("Using 'me' as a username is not allowed.")
    if CustomUser.objects.filter(username=value).exists():
        raise serializers.ValidationError("This username is already taken.")
    return value


def validate_email(value):
    if CustomUser.objects.filter(email=value).exists():
        raise serializers.ValidationError("This email is already in use.")
    return value
