from .views import *
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('game-list/', GameListView.as_view(), name='game-list'),
    path('game/<int:game_id>/', GameView.as_view(), name='game'),
    path('game/', GameHomeView.as_view(), name='game-home')
]
