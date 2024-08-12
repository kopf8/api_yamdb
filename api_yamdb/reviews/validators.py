import re

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    now = timezone.now().year
    if value > now:
        raise ValidationError(
            f"{value} can't be later than {now}"
        )


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            "Username can't be <me>.",
            params={'value': value},
        )
    if re.search(r'^[a-zA-Z][a-zA-Z0-9-_.]{1,20}$', value) is None:
        raise ValidationError(
            f'Invalid characters <{value}> used in username.',
            params={'value': value},
        )
