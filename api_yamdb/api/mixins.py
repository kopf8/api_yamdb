from rest_framework import serializers
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.viewsets import GenericViewSet


class CreateListDestroyViewSet(CreateModelMixin, ListModelMixin,
                               DestroyModelMixin, GenericViewSet):
    """Custom viewset for genres and categories"""
    pass


class AuthorMixin(metaclass=serializers.SerializerMetaclass):
    """Mixin for field Author in ReviewSerializer and CommentSerializer"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
