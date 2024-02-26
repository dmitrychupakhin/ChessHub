from django.db import models
from account.models import User
import uuid

class ChessGame(models.Model):
    fen = models.TextField(default='')
    pgn = models.TextField(default='')

    white_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='white_games', null=True, blank=True)
    black_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='black_games', null=True, blank=True)
    
    white_rematch = models.BooleanField(default=False)
    black_rematch = models.BooleanField(default=False)
    
    white_draw = models.DateTimeField(null=True, blank=True) 
    black_draw = models.DateTimeField(null=True, blank=True) 
    
    is_white_move = models.BooleanField(default=True)
    
    is_public = models.BooleanField(default=True)
    
    is_started = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    
    start_time = models.DateTimeField(null=True, blank=True) 
    total_game_time = models.DurationField(null=True, blank=True) 
    move_increment = models.DurationField(null=True, blank=True)  
    
    last_move_time = models.DateTimeField(null=True,blank=True)
    
    white_user_end_time = models.DateTimeField(null=True, blank=True)
    black_user_end_time = models.DateTimeField(null=True, blank=True)

    white_user_remaining_time = models.DurationField(null=True, blank=True)  
    black_user_remaining_time = models.DurationField(null=True, blank=True)  
    
    unique_link = models.CharField(max_length=36, default=uuid.uuid4, unique=True, editable=False)