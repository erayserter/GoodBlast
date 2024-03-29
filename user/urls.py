from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.views import UserCreate, UserRetrieveDestroy, UserUpdateProgress

urlpatterns = [
    path('', UserCreate.as_view(), name='user-create'),

    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    path('<str:username>', UserRetrieveDestroy.as_view(), name='user-detail'),
    path('<str:username>/progress', UserUpdateProgress.as_view(), name='user-progress'),
]
