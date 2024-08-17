from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.viewsets import GenericViewSet


class ModelMixinViewSet(CreateModelMixin, ListModelMixin,
                        DestroyModelMixin, GenericViewSet):
    """Custom viewset for genres and categories"""
    pass
