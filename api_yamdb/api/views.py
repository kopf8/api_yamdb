from django.core.mail import send_mail
from django.contrib.auth import get_user_model

import random

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import (MethodNotAllowed,
                                       PermissionDenied, ValidationError)
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilter
from reviews.models import Category, Genre, Review, Title

from users.models import CustomUser, ConfirmationCode

from .mixins import ModelMixinViewSet
from .permissions import (IsAdminModeratorOwnerOrReadOnly,
                          IsAdminUserOrReadOnly,
                          IsSuperuser, IsAdmin)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          UserSerializer, SignupSerializer,
                          ConfirmationCodeSerializer)
from .validators import validate_review_unique


User = get_user_model()


class CategoryViewSet(ModelMixinViewSet):
    """Viewset for categories"""
    queryset = Category.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = CategorySerializer
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(ModelMixinViewSet):
    """Viewset for genres"""
    queryset = Genre.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    serializer_class = GenreSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(ModelViewSet):
    """Viewset for titles"""
    queryset = Title.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
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
        if (request.user.role == 'moderator' and request.title
                != title_to_update):
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
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAdminModeratorOwnerOrReadOnly
    )

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
        if request.method == 'PUT':
            raise MethodNotAllowed('PUT')
        return super().update(request, *args, **kwargs)


class CommentViewSet(ModelViewSet):
    """Viewset for comments"""
    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAdminModeratorOwnerOrReadOnly
    )

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
        if request.method == 'PUT':
            raise MethodNotAllowed('PUT')
        return super().update(request, *args, **kwargs)


class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = (SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            url_name='me')
    def me(self, request):
        # Получение данных своей учетной записи
        if request.method == "GET":
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        elif request.method == "PATCH":
            data = request.data.copy()
            data.pop('role', None)
            serializer = UserSerializer(request.user, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        self.permission_classes = (IsAdmin | IsSuperuser,)
        self.check_permissions(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        if 'role' not in serializer.validated_data:
            serializer.save(role='user')
        else:
            serializer.save()

    def list(self, request, *args, **kwargs):
        self.permission_classes = (IsAdmin | IsSuperuser,)
        self.check_permissions(request)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.permission_classes = (IsAdmin | IsSuperuser,)
        self.check_permissions(request)
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method 'PUT' not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        if request.user.role == 'user':
            raise PermissionDenied(
                "You do not have permission to update this user.")
        user_to_update = self.get_object()
        if request.user.role == 'moderator' and request.user != user_to_update:
            raise PermissionDenied(
                "Moderators cannot update other users' profiles.")
        self.permission_classes = (IsAdmin | IsSuperuser,)
        self.check_object_permissions(request, user_to_update)

        serializer = self.get_serializer(
            user_to_update, data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user_to_delete = self.get_object()

        if request.user.is_superuser:
            # Суперпользователь может удалять любого
            user_to_delete.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # Проверка прав администратора
        if request.user.is_admin and not user_to_delete.is_admin:
            # Администратор может удалять только неадминистраторов
            user_to_delete.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # Обычные пользователи не имеют прав на удаление
        raise PermissionDenied(
            "You do not have permission to delete this user.")


class SignupView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

    def send_confirmation_code(self, user, email):
        confirmation_code = str(random.randint(100000, 999999))
        ConfirmationCode.objects.update_or_create(
            user=user,
            defaults={'code': confirmation_code}
        )

        send_mail(
            'Your confirmation code',
            f'Your confirmation code is {confirmation_code}',
            'from@example.com',
            [email],
            fail_silently=False,
        )

    def create(self, request, *args, **kwargs):
        # Поиск пользователя с этим email и username.
        username = request.data.get('username', None)
        email = request.data.get('email', None)
        user = CustomUser.objects.filter(
            email=email,
            username=username
        ).first()

        if user:
            self.send_confirmation_code(user, email)
            return Response(request.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']

        # Проверка на случай, если email и username заняты разными
        # пользователями.
        existing_email = CustomUser.objects.filter(email=email).first()
        existing_username = CustomUser.objects.filter(
            username=username
        ).first()

        if existing_email:
            raise ValidationError(
                {'email': ['This email is already in use by another user.']}
            )
        if existing_username:
            raise ValidationError(
                {'username': [
                    'This username is already in use by another user.'
                ]}
            )

        # Если ни email, ни username не заняты, создаем нового пользователя.
        user = serializer.save()
        self.send_confirmation_code(user, email)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ConfirmationCodeSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            confirmation_code = serializer.validated_data['confirmation_code']
            try:
                user = CustomUser.objects.get(username=username)
                code = ConfirmationCode.objects.get(user=user)
                if code.code == confirmation_code:
                    refresh = RefreshToken.for_user(user)
                    return Response(
                        {'token': str(refresh.access_token)},
                        status=status.HTTP_200_OK
                    )
                return Response(
                    {'error': 'Invalid confirmation code'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except CustomUser.DoesNotExist:
                return Response(
                    {'error': 'User does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except ConfirmationCode.DoesNotExist:
                return Response(
                    {'error': 'Confirmation code does not exist'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
