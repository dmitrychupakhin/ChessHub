import asyncio
import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder
from channels.generic.websocket import AsyncWebsocketConsumer
import chess
import chess.pgn
from django.utils import timezone
from channels.db import database_sync_to_async
from .models import *
from django.db.models import Q
import random
from io import StringIO
from datetime import timedelta

class GameConnectConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_white_user(self, game):
        return game.white_user
    @database_sync_to_async
    def start_game_random(self, chess_game):
        white_user = chess_game.white_user
        black_user = chess_game.black_user
        
        if random.choice([True, False]):
            chess_game.white_user = black_user
            chess_game.black_user = white_user
            chess_game.save()
            
    async def connect(self):
        self.room_group_name = self.scope['url_route']['kwargs']['link']
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        user = self.scope['user']
        
        game = await database_sync_to_async(ChessGame.objects.get)(unique_link=self.room_group_name, is_started=False)
        
        white_user = await self.get_white_user(game)
        
        if user != white_user:
            game.black_user = user
            game.is_started = True
            game.start_time=timezone.now()
            game.last_move_time = game.start_time
            game.white_user_end_time = game.start_time + game.total_game_time
            game.black_user_end_time = game.start_time + game.total_game_time
            await database_sync_to_async(game.save)()
            await self.start_game_random(game)
        
            await self.channel_layer.group_send(
                    self.room_group_name,
                        {
                            'type': 'start_game',
                            'game_id':  game.pk,
                        }
                )
              
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        game = await database_sync_to_async(ChessGame.objects.get)(unique_link=self.room_group_name, is_started=False)
        if game.is_started == False:
            await database_sync_to_async(game.delete)()
    
    async def start_game(self, event):
        event['type'] = 'start-game'
        await self.send(text_data=json.dumps(event))

def serialize_datetime(obj):
    if isinstance(obj, (timezone.datetime,)):
        return obj.isoformat()
    return None

def serialize_timedelta(obj):
    if isinstance(obj, (timedelta,)):
        return obj.total_seconds()
    return None

@database_sync_to_async
def time_over(game_id):
    game = ChessGame.objects.get(id=game_id)
    if game.is_white_move:
        if game.white_user_end_time < timezone.now():
            game.is_finished = True
            print('black win')
        elif game.black_user_end_time + (timezone.now() - game.last_move_time ) < timezone.now():
            game.is_finished = True
            print('white win')
        if game.is_finished:
            if game.white_user_remaining_time == None:
                game.white_user_remaining_time = game.white_user_end_time - timezone.now()
            if game.black_user_remaining_time == None:
                game.black_user_remaining_time = (game.black_user_end_time + (timezone.now() - game.last_move_time )) -  timezone.now()
    else:
        if game.white_user_end_time + (timezone.now() - game.last_move_time )  < timezone.now():
            game.is_finished = True
            print('black win')
        elif game.black_user_end_time < timezone.now():
            game.is_finished = True
            print('white win') 
        if game.is_finished:
            if game.white_user_remaining_time == None:
                game.white_user_remaining_time = game.white_user_end_time  + (timezone.now() - game.last_move_time ) - timezone.now() 
            if game.black_user_remaining_time == None:
                game.black_user_remaining_time = (game.black_user_end_time) - timezone.now()
        
    game.save()

class GameConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_white_black_user(self, chess_game):
        white_user = chess_game.white_user
        black_user = chess_game.black_user
        return white_user, black_user
    
    @database_sync_to_async
    def get_game_data(self, game_id):
        game = ChessGame.objects.get(id=game_id)
        
        game_data = {
            'is_finished': game.is_finished,
            'white_user_remaining_time': serialize_timedelta(game.white_user_remaining_time),
            'black_user_remaining_time': serialize_timedelta(game.black_user_remaining_time),
            'white_rematch': game.white_rematch,
            'black_rematch': game.black_rematch,
            'white_user': game.white_user.username,
            'black_user': game.black_user.username,
            'is_white_move': game.is_white_move,
            'game_pgn': game.pgn,
            'last_move_time': serialize_datetime(game.last_move_time),
            'white_user_end_time': serialize_datetime(game.white_user_end_time),
            'black_user_end_time': serialize_datetime(game.black_user_end_time),
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
        
        if type == 'game-data':
            game_id = self.scope['url_route']['kwargs']['game_id']
            game = await database_sync_to_async(ChessGame.objects.get)(id=game_id)

            await time_over(game_id)
        
            game_data = await self.get_game_data(game_id)
            await self.send(
                text_data=json.dumps({
                    'type': 'game-data', 
                    'game_data': game_data,
                })
            )
        elif type == 'resign':
            user = self.scope['user']
            game_id = self.scope['url_route']['kwargs']['game_id']
            game = await database_sync_to_async(ChessGame.objects.get)(id=game_id)
            
            game.is_finished = True
            await database_sync_to_async(game.save)()
            await time_over(game_id)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                    {
                        'type': 'rematch',
                        'white_rematch':  game.white_rematch,
                        'black_rematch':  game.black_rematch,
                    }
            )
            
        elif type == 'draw':
            user = self.scope['user']
            game_id = self.scope['url_route']['kwargs']['game_id']
            game = await database_sync_to_async(ChessGame.objects.get)(id=game_id)
            white_user, black_user = await self.get_white_black_user(game)
            if white_user == user:
                game.white_draw = timezone.now()
                message = 'Black player offers a draw'
            elif black_user == user:
                game.black_draw = timezone.now()
                message = 'White player offers a draw'
                    
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'game_message',
                        'message': message
                    }
                )
            
            if game.white_draw and game.black_draw:
                if abs((game.white_draw - game.black_draw).total_seconds()) < 10:
                    game.is_finished = True
                    await database_sync_to_async(game.save)()
                    await time_over(game_id)
                    await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'rematch',
                        'white_rematch':  game.white_rematch,
                        'black_rematch':  game.black_rematch,
                    }
                )
            
            await database_sync_to_async(game.save)()
            
        elif type == 'message':
            user = self.scope['user']
            message = data['message']
            
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'message',
                        'user': user.username,
                        'message': message
                    }
                )
            
        elif type == 'time-over':
            game_id = self.scope['url_route']['kwargs']['game_id']
            
            await time_over(game_id)
            
        elif type == 'rematch':
            game_id = self.scope['url_route']['kwargs']['game_id']
            self.room_group_name = game_id
            game = await database_sync_to_async(ChessGame.objects.get)(id=game_id)
            
            if game.white_rematch and game.black_rematch:
                return
    
            if game.is_finished:
                user = self.scope["user"]
                game_data = await self.get_game_data(game_id)
                if game_data['white_user'] == user.username:
                    game.white_rematch = True
                elif game_data['black_user'] == user.username:
                    game.black_rematch = True
            else:
                return      
            
            await database_sync_to_async(game.save)()
            
            if game.white_rematch and game.black_rematch:
                white_user = await database_sync_to_async(User.objects.get)(username=game_data['white_user'])
                black_user = await database_sync_to_async(User.objects.get)(username=game_data['black_user'])

                new_game = game
                new_game.pk = None
                new_game.pgn = ''
                new_game.fen = ''
                new_game.white_rematch = False
                new_game.black_rematch = False
                new_game.is_finished = False
                new_game.is_white_move = True
                new_game.start_time=timezone.now()
                new_game.last_move_time = new_game.start_time
                new_game.white_user_end_time = new_game.start_time + new_game.total_game_time
                new_game.black_user_end_time = new_game.start_time + new_game.total_game_time
                new_game.white_user = black_user
                new_game.black_user = white_user
                
                await database_sync_to_async(new_game.save)()
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'rematch',
                        'game_id': new_game.pk
                    }
                )
            else:    
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'rematch',
                        'white_rematch':  game.white_rematch,
                        'black_rematch':  game.black_rematch,
                    }
                )
                
        elif type == 'move':
            game_id = self.scope['url_route']['kwargs']['game_id']
            self.room_group_name = game_id
            game = await database_sync_to_async(ChessGame.objects.get)(id=game_id)
            
            game_data = await self.get_game_data(game_id)
            
            time_now = timezone.now() 
            
            await time_over(game_id)
            
            if game.is_finished:
                return
            
            if game.is_white_move:
                game.black_user_end_time += (time_now - game.last_move_time)
                game.white_user_end_time += game.move_increment
                user = game_data['white_user']
            else:
                game.black_user_end_time += game.move_increment
                game.white_user_end_time += (time_now - game.last_move_time)
                user = game_data['black_user']
            
            game.last_move_time = time_now
            
            board = chess.Board()
            if game.fen:
                board.set_fen(game.fen)
            board.push_san(data['move'])
            game.fen = board.fen()
            
            if board.is_game_over():
                game.is_finished = True
            
            if game.is_finished:
                if game.is_white_move:
                    game.white_user_remaining_time = game.white_user_end_time  + (timezone.now() - game.last_move_time ) -  timezone.now() 
                    game.black_user_remaining_time = game.black_user_end_time - timezone.now()
                else:
                    game.white_user_remaining_time = game.white_user_end_time  + (timezone.now() - game.last_move_time ) - timezone.now()
                    game.black_user_remaining_time = game.black_user_end_time - timezone.now()
            
            game.pgn = data['gamePGN']
            game.is_white_move = not game.is_white_move
            await database_sync_to_async(game.save)()
             
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_move',
                    'user': user,
                    'move': data['move'],
                    'white_user_end_time': serialize_datetime(game.white_user_end_time),
                    'black_user_end_time': serialize_datetime(game.black_user_end_time),
                    'last_move_time': serialize_datetime(game.last_move_time),
                    'is_white_move': game.is_white_move
                }
            )
            
    async def game_move(self, event):
        event['type'] = 'game-move'
        await self.send(text_data=json.dumps(event))
    
    async def rematch(self, event):
        event['type'] = 'rematch'
        await self.send(text_data=json.dumps(event))
    
    async def game_message(self, event):
        event['type'] = 'game-message'
        await self.send(text_data=json.dumps(event))    

    async def message(self, event):
        event['type'] = 'message'
        await self.send(text_data=json.dumps(event))
        

            

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
                is_public=True,
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
        for current_game in current_games:
            game = ChessGame.objects.get(id=current_game.pk)
            if game.is_started:
                if game.is_white_move:
                    if game.white_user_end_time < timezone.now():
                        game.is_finished = True
                        print('black win')
                    elif game.black_user_end_time + (timezone.now() - game.last_move_time ) < timezone.now():
                        game.is_finished = True
                        print('white win')
                    if game.is_finished:
                        if game.white_user_remaining_time == None:
                            game.white_user_remaining_time = game.white_user_end_time - timezone.now()
                        if game.black_user_remaining_time == None:
                            game.black_user_remaining_time = (game.black_user_end_time + (timezone.now() - game.last_move_time )) -  timezone.now()
                else:
                    if game.white_user_end_time + (timezone.now() - game.last_move_time )  < timezone.now():
                        game.is_finished = True
                        print('black win')
                    elif game.black_user_end_time < timezone.now():
                        game.is_finished = True
                        print('white win') 
                    if game.is_finished:
                        if game.white_user_remaining_time == None:
                            game.white_user_remaining_time = game.white_user_end_time  + (timezone.now() - game.last_move_time ) - timezone.now() 
                        if game.black_user_remaining_time == None:
                            game.black_user_remaining_time = (game.black_user_end_time) - timezone.now()
                    
            game.save()
        current_games = current_games.filter(
            is_finished=False, 
        )
        current_games_list = [
            {
                'game_id': current_game.pk,
                'is_started': current_game.is_started,
                'white_user': current_game.white_user.username if current_game.white_user else None,
                'black_user': current_game.black_user.username if current_game.black_user else None,
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
            chess_game = await database_sync_to_async(ChessGame.objects.create)(white_user=user,
                total_game_time=timedelta(minutes=int(data['game_time'])),
                move_increment=timedelta(seconds=int(data['step_time'])),
                is_public=data['is_public'])
            if data['is_public'] == 0:
                await self.send(
                    text_data=json.dumps({
                        'type': 'new-game',
                        'game_id': chess_game.pk,
                        'white_user': user.username,
                        'link': chess_game.unique_link,
                    }, cls=DjangoJSONEncoder)
                )
                return
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
            chess_game.start_time=timezone.now()
            chess_game.last_move_time = chess_game.start_time
            chess_game.white_user_end_time = chess_game.start_time + chess_game.total_game_time
            chess_game.black_user_end_time = chess_game.start_time + chess_game.total_game_time
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
        