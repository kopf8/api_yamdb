from django.core.mail import send_mail
from django.contrib.auth import get_user_model

import random

from rest_framework import generics, status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ConfirmationCode, CustomUser
from .serializers import (
    SignupSerializer, ConfirmationCodeSerializer, UserSerializer)


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = (SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)

    def get_object(self):
        return super().get_object()

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            url_name='me')
    def me(self, request):
        # Получение данных своей учетной записи
        if request.method == "GET":
            serializer = UserSerializer(request.user)
            return Response(serializer.data)

        # Изменение данных своей учетной записи
        elif request.method == "PATCH":
            data = request.data.copy()
            if 'role' in data:
                data.pop('role')
            serializer = UserSerializer(
                request.user,
                data=data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        # Проверка, что пользователь является администратором
        if not request.user.is_admin and not request.user.is_superuser:
            return Response(
                {"detail": "You do not have permission to view this list."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(
                {"detail": "You do not have permission to view this user."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method 'PUT' not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        user_to_update = self.get_object()
        # Проверка роли пользователя
        if request.user.role == 'user':
            return Response(
                {"detail": "You do not have permission to modify this user."},
                status=status.HTTP_403_FORBIDDEN
            )
        if request.user.role == 'moderator' and request.user != user_to_update:
            return Response(
                {"detail": "Moderators cannot modify other users' profiles."},
                status=status.HTTP_403_FORBIDDEN
            )
        if request.user.is_admin:
            serializer = self.get_serializer(
                user_to_update, data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Возвращаем ответ с обновленными данными и статусом 200
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": "You do not have permission to modify this user."},
            status=status.HTTP_403_FORBIDDEN
        )

    def destroy(self, request, *args, **kwargs):
        user_to_delete = self.get_object()

        # Проверка прав суперпользователя
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
        user = CustomUser.objects.filter(email=email, username=username).first()

        if user:
            self.send_confirmation_code(user, email)
            return Response(request.data, status=status.HTTP_200_OK)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        # Проверка на случай, если email и username заняты разными пользователями.
        existing_user = CustomUser.objects.filter(email=email).first()
        existing_username = CustomUser.objects.filter(username=username).first()
        if existing_user and existing_username and existing_user != existing_username:
            raise ValidationError({
                'email': ['This email is already in use by another user.'],
                'username': ['This username is already in use by another user.']
            })
        if existing_user:
            raise ValidationError({'email': ['This email is already in use by another user.']})
        if existing_username:
            raise ValidationError({'username': ['This username is already in use by another user.']})
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
