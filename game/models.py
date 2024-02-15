from django.db import models
from account.models import User

class ChessGame(models.Model):
    fen = models.CharField(max_length=255, blank=True, null=True)
    move_history = models.TextField(blank=True, null=True)

    white_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='white_games', null=True, blank=True)
    black_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='black_games', null=True, blank=True)
    
    is_public = models.BooleanField(default=True)
    is_started = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)