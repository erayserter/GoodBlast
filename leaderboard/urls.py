from django.urls import path

from leaderboard.views import (
    GlobalLeaderboard,
    CountryLeaderboard,
    GroupLeaderboard,
    UserGroupRank
)

urlpatterns = [
    path('global', GlobalLeaderboard.as_view(), name='global-leaderboard'),
    path('country', CountryLeaderboard.as_view(), name='country-leaderboard'),
    path('group', GroupLeaderboard.as_view(), name='group-leaderboard'),
    path('rank', UserGroupRank.as_view(), name='user-rank'),
]
