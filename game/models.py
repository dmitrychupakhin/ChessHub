from django.db import models
from account.models import User

class ChessGame(models.Model):
    fen = models.TextField(default='')
    pgn = models.TextField(default='')

    white_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='white_games', null=True, blank=True)
    black_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='black_games', null=True, blank=True)
    
    white_rematch = models.BooleanField(default=False)
    black_rematch = models.BooleanField(default=False)
    
    is_white_move = models.BooleanField(default=True)
    
    is_public = models.BooleanField(default=True)
    is_started = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    
    start_time = models.DateTimeField(null=True, blank=True)  # Время начала игры
    total_game_time = models.DurationField(null=True, blank=True)  # Общее время на игру
    move_increment = models.DurationField(null=True, blank=True)  # Время прибавки к каждому ходу