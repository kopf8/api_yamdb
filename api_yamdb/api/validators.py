from rest_framework.exceptions import ValidationError


def validate_review_unique(title, author):

    if title.reviews.filter(author=author).exists():
        raise ValidationError('You have already reviewed this title.')
