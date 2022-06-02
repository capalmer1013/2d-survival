from pygase import Client
import time
import main
import gameObjects

client = Client()
client.connect_in_thread(port=8080, hostname="localhost")
game = main.App(headless=False, networked=True)
game.scene = main.SCENE_PLAY
game.WORLD_HEIGHT = game.SCREEN_HEIGHT
game.WORLD_WIDTH = game.SCREEN_WIDTH

def update_play_scene(self):
    with client.access_game_state() as game_state:
        for each in game_state.__dict__:
            print(each)
            print(type(each))
            print(game_state.__dict__[each])
            tmpObj = gameObjects.BaseGameObject.deserialize(each, game.player, game)
            if tmpObj not in game.gameObjects:
                game.gameObjects.append(tmpObj)

game.start()