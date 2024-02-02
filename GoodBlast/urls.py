from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/users/', include('user.urls')),
    path('api/tournament/', include('tournament.urls')),
    path('api/leaderboard/', include('leaderboard.urls')),
]
