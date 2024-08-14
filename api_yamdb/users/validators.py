import re
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from .models import CustomUser


def validate_username(value, instance=None):
    if value.lower() == 'me':
        raise serializers.ValidationError("Using 'me' as a username is not allowed.")

    if re.search(r'^[a-zA-Z][a-zA-Z0-9-_.]{1,20}$', value) is None:
        raise serializers.ValidationError(f'Unaccepted symbols <{value}> in nickname.')

    try:
        user = CustomUser.objects.get(username=value)
        if instance is None or user.id != instance.id:
            raise serializers.ValidationError("This username is already taken.")
    except ObjectDoesNotExist:
        pass

    return value


def validate_email(value, instance=None):
    try:
        user = CustomUser.objects.get(email=value)
        if instance is None or user.id != instance.id:
            raise serializers.ValidationError("This email is already in use.")
    except ObjectDoesNotExist:
        pass

    return value
