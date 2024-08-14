from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters import TitleFilter
from reviews.models import Category, Genre, Review, Title

from .mixins import ModelMixinViewSet
from .permissions import IsOwnerOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer)
from .validators import validate_review_unique


class CategoryViewSet(ModelMixinViewSet):
    """Viewset for categories"""
    queryset = Category.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = CategorySerializer
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(ModelMixinViewSet):
    """Viewset for genres"""
    queryset = Genre.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = GenreSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(ModelViewSet):
    """Viewset for titles"""
    queryset = Title.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method 'PUT' not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        title_to_update = self.get_object()
        if request.user.role == 'user':
            return Response(
                {"detail": "You do not have permission to modify this title."},
                status=status.HTTP_403_FORBIDDEN
            )
        if (request.user.role == 'moderator' and request.title !=
                title_to_update):
            return Response(
                {"detail": "Moderators cannot modify other users' titles."},
                status=status.HTTP_403_FORBIDDEN
            )
        if request.user.is_admin:
            serializer = self.get_serializer(
                title_to_update, data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": "You do not have permission to modify this title."},
            status=status.HTTP_403_FORBIDDEN
        )


class ReviewViewSet(ModelViewSet):
    """Viewset for reviews"""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        author = self.request.user
        validate_review_unique(title, author)
        serializer.save(title=title, author=author)

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method 'PUT' not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        review_to_update = self.get_object()

        if request.user.role == 'user':
            serializer = self.get_serializer(
                review_to_update, data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if (request.user.role == 'moderator' and request.review !=
                review_to_update):
            serializer = self.get_serializer(
                review_to_update, data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.user.is_admin:
            serializer = self.get_serializer(
                review_to_update, data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": "You do not have permission to modify this review."},
            status=status.HTTP_403_FORBIDDEN
        )


class CommentViewSet(ModelViewSet):
    """Viewset for comments"""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

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

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method 'PUT' not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        comment_to_update = self.get_object()

        if request.user.role == 'user':
            serializer = self.get_serializer(
                comment_to_update, data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if (request.user.role == 'moderator' and request.comment !=
                comment_to_update):
            return Response(
                {"detail": "Moderators cannot modify other users' comments."},
                status=status.HTTP_403_FORBIDDEN
            )

        if request.user.is_admin:
            serializer = self.get_serializer(
                comment_to_update, data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": "You do not have permission to modify this comment."},
            status=status.HTTP_403_FORBIDDEN
        )
