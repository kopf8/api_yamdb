from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet

from api.filters import TitleFilter
from reviews.models import Category, Genre, Review, Title

from .mixins import ModelMixinViewSet
from .permissions import (IsAdmin, IsAuthenticated, IsModerator, IsOwner,
                          IsReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer)


class CategoryViewSet(ModelMixinViewSet):
    queryset = Category.objects.all()
    permission_classes = (
        IsAdmin | IsReadOnly,
    )
    serializer_class = CategorySerializer
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(ModelMixinViewSet):
    queryset = Genre.objects.all()
    permission_classes = (
        IsAdmin | IsReadOnly,
    )
    serializer_class = GenreSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (
        IsAdmin | IsReadOnly,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAdmin | IsModerator | IsOwner | IsAuthenticated | IsReadOnly,
    )
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        author = self.request.user
        serializer.save(title=title, author=author)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        IsAdmin | IsModerator | IsOwner | IsAuthenticated | IsReadOnly,
    )
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs['review_id'],
            title_id=self.kwargs['title_id']
        )

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
