import re

from rest_framework import serializers
from .models import CustomUser


def validate_username(value, instance=None):
    if value.lower() == 'me':
        raise serializers.ValidationError("Using 'me' as a username is not allowed.")

    if re.search(r'^[a-zA-Z][a-zA-Z0-9-_.]{1,30}$', value) is None:
        raise serializers.ValidationError(f'Unaccepted symbols <{value}> in nickname.')

    if CustomUser.objects.filter(username=value).exists():
        raise serializers.ValidationError("This username is already taken.")
    return value


def validate_email(value, instance=None):
    if CustomUser.objects.filter(email=value).exists():
        raise serializers.ValidationError("This email is already in use.")
    return value
