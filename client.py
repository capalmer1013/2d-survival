import time
import main
import gameObjects
import asyncio
import socketio

sio = socketio.AsyncClient()


# game = main.App(headless=False, networked=True)
# game.scene = main.SCENE_PLAY
# game.WORLD_HEIGHT = game.SCREEN_HEIGHT
# game.WORLD_WIDTH = game.SCREEN_WIDTH
#
# def update_play_scene(self):
#     for each in game_state.__dict__:
#         print(each)
#         print(type(each))
#         print(game_state.__dict__[each])
#         tmpObj = gameObjects.BaseGameObject.deserialize(each, game.player, game)
#         if tmpObj not in game.gameObjects:
#             game.gameObjects.append(tmpObj)
#
# game.start()


import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('connection established')

@sio.event
def my_message(data):
    print('message received with ', data)
    sio.emit('my response', {'response': 'my response'})

@sio.event
def disconnect():
    print('disconnected from server')

sio.connect('http://localhost:5000')
sio.wait()


