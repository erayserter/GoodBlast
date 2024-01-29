from django.urls import path

from user.views import UserCreate, UpdateProgress

urlpatterns = [
    path('', UserCreate.as_view(), name='user-create'),
    path('<str:username>/progress', UpdateProgress.as_view(), name='user-progress'),
]
