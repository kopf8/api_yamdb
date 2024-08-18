from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SignupView, TokenView, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/token/', TokenView.as_view(), name='token'),
    path('', include(router.urls)),
]
