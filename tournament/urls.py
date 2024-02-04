from django.urls import path

from tournament.views import EnterTournament, ClaimTournamentReward, UserTournamentScoreDetails

urlpatterns = [
    path('enter', EnterTournament.as_view(), name='enter-tournament'),
    path('claim-reward', ClaimTournamentReward.as_view(), name='claim-tournament-reward'),
    path('<int:tournament>', UserTournamentScoreDetails.as_view(), name='user-tournament-score-details'),
]
