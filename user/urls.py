from django.urls import path

from user.views import CreateUserAPIView, ProgressAPIView

urlpatterns = [
    path('', CreateUserAPIView.as_view(), name='user-create'),
    path('<str:username>/progress', ProgressAPIView.as_view(), name='user-progress'),
]
