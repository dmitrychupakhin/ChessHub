import json
from channels.generic.websocket import AsyncWebsocketConsumer
from chess import Board
from channels.db import database_sync_to_async
from .models import *
from django.db.models import Q
import random

class GameConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_game_data(self, game_id):
        game = ChessGame.objects.get(id=game_id)
        game_data = {
            'white_user': game.white_user.username,
            'black_user': game.black_user.username,
        }
        return game_data
    async def connect(self):
        self.room_group_name = self.scope['url_route']['kwargs']['game_id']
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        type = data['type']
        print(data)
        
        if type == 'game-data':
            game_id = self.scope['url_route']['kwargs']['game_id']
            game_data = await self.get_game_data(game_id)
            await self.send(
                text_data=json.dumps({
                    'type': 'game-data',
                    'game_data': game_data,
                })
            )
            
            

class HomeConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_white_black_user(self, chess_game):
        white_user = chess_game.white_user
        black_user = chess_game.black_user
        return white_user, black_user

    @database_sync_to_async
    def start_game_random(self, chess_game):
        white_user = chess_game.white_user
        black_user = chess_game.black_user
        
        if random.choice([True, False]):
            chess_game.white_user = black_user
            chess_game.black_user = white_user
            chess_game.save()

    @database_sync_to_async
    def get_open_games(self, user):
        open_games = ChessGame.objects.exclude(
            Q(white_user=user) | Q(black_user=user)).filter(
                is_started=False, 
                is_finished=False, 
            )
        open_games_list = [
            {
                'game_id': open_game.pk,
                'is_started': open_game.is_started,
                'white_user': open_game.white_user.username if open_game.white_user else None,
                'black_user': open_game.black_user.username if open_game.black_user else None
            }
            for open_game in open_games
        ]
        return open_games_list

    @database_sync_to_async
    def get_current_games(self, user):
        current_games = ChessGame.objects.filter(
            Q(white_user=user) | Q(black_user=user),
            is_finished=False, 
        )
        current_games_list = [
            {
                'game_id': current_game.pk,
                'is_started': current_game.is_started,
                'white_user': current_game.white_user.username if current_game.white_user else None,
                'black_user': current_game.black_user.username if current_game.black_user else None
            }
            for current_game in current_games
        ]
        return current_games_list

    async def connect(self):
        self.room_group_name = "home"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        type = data['type']
        print(data)
        if type == 'new-game':
            user = self.scope["user"]
            chess_game = await database_sync_to_async(ChessGame.objects.create)(white_user=user)
            await self.channel_layer.group_send(
                'home',
                {
                    'type': 'new_game',
                    'game_id': chess_game.pk,
                    'white_user': user.username,
                }
            )
        elif type == 'game-list':
            user = self.scope["user"]
            current_games = await self.get_current_games(user)
            open_games = await self.get_open_games(user)
            
            await self.send(
                text_data=json.dumps({
                    'type': 'game-list',
                    'current_games': current_games,
                    'open_games': open_games,
                })
            )
        elif type == 'join-game':
            user = self.scope["user"]
            game_id = data.get('game_id')
            chess_game = await database_sync_to_async(ChessGame.objects.get)(id=game_id)
            chess_game.black_user = user
            chess_game.is_started = True
            await database_sync_to_async(chess_game.save)()
            await self.start_game_random(chess_game)
            white_user, black_user = await self.get_white_black_user(chess_game)
            
            await self.channel_layer.group_send(
                'home',
                {
                    'type': 'start_game',
                    'game_id': chess_game.pk,
                    'white_user': white_user.username,
                    'black_user': black_user.username,
                }
            )

        elif type == 'leave-game':
            user = self.scope["user"]
            game_id = data.get('game_id')
            chess_game = await database_sync_to_async(ChessGame.objects.get)(id=game_id, white_user = user)
            await database_sync_to_async(chess_game.delete)()
            await self.channel_layer.group_send(
                'home',
                {
                    'type': 'remove_game',
                    'game_id': game_id,
                    'white_user': user.username,
                }
            )
            
    async def game_list(self, event):
        event['type'] = 'game-list'
        await self.send(text_data=json.dumps(event))

    async def remove_game(self, event):
        event['type'] = 'remove-game'
        await self.send(text_data=json.dumps(event))
    
    async def new_game(self, event):
        event['type'] = 'new-game'
        await self.send(text_data=json.dumps(event))
        
    async def start_game(self, event):
        event['type'] = 'start-game'
        await self.send(text_data=json.dumps(event))
        