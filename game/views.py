from django.shortcuts import render
from django.views.generic import TemplateView

class GameListView(TemplateView):
    template_name = 'game/game-list.html'

class GameHomeView(TemplateView):
    template_name = 'game/game-home.html'

class GameView(TemplateView):
    template_name = 'game/game.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs.get('game_id')
        context['game_id'] = game_id
        return context

class GameComputerView(TemplateView):
    template_name = 'game/game-computer.html'
    
class GameConnectView(TemplateView):
    template_name = 'game/game-connect.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        link = self.kwargs.get('link')
        context['link'] = link
        return context