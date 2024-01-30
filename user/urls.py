from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.views import UserCreate, UpdateProgress, UserRetrieveDestroy

urlpatterns = [
    path('', UserCreate.as_view(), name='user-create'),
    path('<str:username>', UserRetrieveDestroy.as_view(), name='user-detail'),
    path('<str:username>/progress', UpdateProgress.as_view(), name='user-progress'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
