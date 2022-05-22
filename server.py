import math
import pickle
import time
from pygase import GameState, Backend
import main

# todo: figure out how to make headless assignable on main import

game_cycle_time = 1/30

game = main.App()
game.initWorld(0.05)
game.scene = main.SCENE_PLAY

total_dt = 0.0

stale_game_state = {str(x.id): x.serialize() for x in game.gameObjects}

initial_game_state = GameState(**stale_game_state)

count = 0


def time_step(game_state, dt):
    global total_dt
    global stale_game_state

    global count
    count += 1
    total_dt += dt
    if total_dt > game_cycle_time:
        total_dt = 0.0
        game.update()
        stale_game_state.update({str(x.id): x.serialize() for x in game.gameObjects if x.moved})

    return stale_game_state


for each in initial_game_state.__dict__:
    print(each)
print(len(initial_game_state.__dict__))

backend = Backend(initial_game_state, time_step)
backend.run('localhost', 8080)
