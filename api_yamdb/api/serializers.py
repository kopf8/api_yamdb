import re

from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from reviews.models import Category, Comment, CustomUser, Genre, Review, Title


User = get_user_model()


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for model Category"""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for model Genre"""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Serializer for model Title on GET requests"""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')


class TitleWriteSerializer(serializers.ModelSerializer):
    """Serializer for model Title on POST, PATCH, DELETE requests"""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    class Meta:
        model = Review
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('review',)


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
