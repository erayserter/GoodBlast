from django.urls import path

from tournament.views import EnterTournament, ClaimTournamentReward

urlpatterns = [
    path('enter', EnterTournament.as_view(), name='enter-tournament'),
    path('claim-reward', ClaimTournamentReward.as_view(), name='claim-tournament-reward'),
]
