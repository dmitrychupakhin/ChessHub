from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *

class GameListView(LoginRequiredMixin, TemplateView):
    template_name = 'game/game-list.html'

class GameHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'game/game-home.html'

class GameView(LoginRequiredMixin, TemplateView):
    template_name = 'game/game.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('game_id')
        
        get_object_or_404(ChessGame, id=game_id)
        
        context['game_id'] = game_id
        return context

class GameComputerView(LoginRequiredMixin, TemplateView):
    template_name = 'game/game-computer.html'
    
class GameConnectView(LoginRequiredMixin, TemplateView):
    template_name = 'game/game-connect.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        link = self.kwargs.get('link')
        
        get_object_or_404(ChessGame, unique_link=link)
        
        context['link'] = link
        return context