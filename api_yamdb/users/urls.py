from django.urls import path
from .views import SignupView, TokenView, UserProfileView, UserCreateView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('token/', TokenView.as_view(), name='token'),
    path('me/', UserProfileView.as_view(), name='profile'),
    path('users/', UserCreateView.as_view(), name='create_user'),
]