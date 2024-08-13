from django.core.mail import send_mail
from django.contrib.auth import get_user_model

import random

from rest_framework import generics, status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ConfirmationCode, CustomUser
from .serializers import (
    SignupSerializer, ConfirmationCodeSerializer, UserSerializer
)
from .permissions import IsAdminOrReadOnly


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'

    def get_object(self):
        # Для обычных операций, требующих проверки администратора
        if not self.request.user.is_admin:
            raise PermissionDenied("You do not have permission to perform this action.")

        return super().get_object()

    @action(detail=False, methods=['get', 'patch'], url_path='me', url_name='me')
    def me(self, request):
        # Получение данных своей учетной записи
        if request.method == "GET":
            serializer = UserSerializer(request.user)
            return Response(serializer.data)

        # Изменение данных своей учетной записи
        elif request.method == "PATCH":
            serializer = UserSerializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class SignupView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        confirmation_code = str(random.randint(100000, 999999))
        ConfirmationCode.objects.update_or_create(
            user=user,
            defaults={'code': confirmation_code}
        )
        send_mail(
            'Your confirmation code',
            f'Your confirmation code is {confirmation_code}',
            'from@example.com',
            [serializer.validated_data['email']],
            fail_silently=False,
        )
        user, created = CustomUser.objects.get_or_create(
            email=serializer.validated_data['email'],
            username=serializer.validated_data['username'],
            defaults={'confirmation_code': confirmation_code}
        )

        if not created:
            # Update confirmation code if user exists
            user.confirmation_code = confirmation_code
            user.save()

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
                    return Response({'token': str(refresh.access_token)})
                return Response({'error': 'Invalid confirmation code'}, status=status.HTTP_400_BAD_REQUEST)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            except ConfirmationCode.DoesNotExist:
                return Response({'error': 'Confirmation code does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        if not self.request.user.is_admin:
            raise PermissionDenied("You do not have permission to perform this action.")
        queryset = super().get_queryset()
        search_param = self.request.query_params.get('search', None)
        if search_param:
            queryset = queryset.filter(username__icontains=search_param)
        return queryset
