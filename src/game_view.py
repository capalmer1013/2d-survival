from threading import Thread

import pyxel

from .constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCENE_PLAY,
    BLOCK_HEIGHT,
    BLOCK_WIDTH,
    BASE_BLOCK,
)
from .game_controller import GameController
from .game_model import GameModel
from .game_objects import Background, Cursor
from .savethread import save_game_periodically
from .utils import (
    draw_list,
    resource_path,
)


class GameView:
    def __init__(self, model: GameModel, controller: GameController):
        self.scene = SCENE_PLAY
        self.pyxel_init()
        self.model = model
        self.controller = controller
        self.viewGameObjects = []
        self.player = self.controller.create_player_character()
        self.viewGameObjects.append(Cursor(0, 0, self.player, self))
        self.background = Background(BLOCK_WIDTH, BLOCK_HEIGHT, self)
        self.sceneDrawDict = {SCENE_PLAY: self.draw_play_scene}
        self.start()

    @staticmethod
    def pyxel_init():
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Rust[2D]ust")
        pyxel.load(resource_path("assets.pyxres"))

    def resume(self):
        raise NotImplementedError

    def start(self):
        save_thread = Thread(target=save_game_periodically, args=(self,))
        save_thread.start()
        pyxel.run(self.update, self.draw)

    def update(self):
        self.background.update()
        self.controller.update(self.scene)

    def get_relative_xy(self):
        return (
            self.player.x - SCREEN_WIDTH / 2,
            self.player.y - SCREEN_HEIGHT / 2,
        )

    def draw(self):
        # query model for what to draw
        relx, rely = self.get_relative_xy()
        pyxel.cls(0)
        pyxel.camera(
            self.player.x - SCREEN_WIDTH / 2,
            self.player.y - SCREEN_HEIGHT / 2,
        )
        self.background.draw(
            (self.player.x - SCREEN_WIDTH / 2) / BASE_BLOCK,
            (self.player.y - SCREEN_HEIGHT / 2) / BASE_BLOCK,
        )
        self.sceneDrawDict[self.scene]()
        pyxel.text(relx + 39, rely + 4, f"Health: {self.player.health}", 7)
        pyxel.text(relx + 39, rely + 16, f"Hunger: {self.player.hunger}", 7)
        pyxel.text(relx + 39, rely + 24, f"Ammo: {self.player.ammo}", 7)
        # todo: why the heck is player.x and y a float?
        pyxel.text(
            relx + 39,
            rely + 32,
            f"Coord: {int(self.player.x)}, {int(self.player.y)}",
            7,
        )
        y = 32 + 8
        inv_dict = self.player.inventory.dict()
        count = 1
        for each in inv_dict:
            pyxel.text(
                relx + 39,
                rely + y,
                f"[{count}] {each.__name__}(s): {inv_dict[each]}",
                7,
            )
            y += 8
            count += 1
            # pyxel.text(relx + 39, rely+36, f"Bones: {self.player.bones}", 7)
            # pyxel.text(relx + 39, rely+42, f"bricks: {self.player.bricks}", 7)

    def draw_play_scene(self, game_objects, player):
        draw_list([x for x in game_objects if x.nearPlayer(game_objects, player)])
        draw_list(self.model.persistentGameObjects)
        draw_list(self.viewGameObjects)
