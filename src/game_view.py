from threading import Thread

import pyxel

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCENE_PLAY
from gameObjects import (
    BASE_BLOCK,

)
from game_controller import GameController
from game_model import GameModel
from savethread import save_game_periodically
from utils import (
    cleanup_list,
    draw_list,
    resource_path,
    update_list,
)


class GameView:
    def __init__(self):
        self.pyxel = pyxel
        self.scene = SCENE_PLAY
        self.uiObjects = []
        self.pyxel_init()
        self.model = GameModel()
        self.controller = GameController()

        # config
        self.sceneUpdateDict = {SCENE_PLAY: self.update_play_scene}
        self.sceneDrawDict = {SCENE_PLAY: self.draw_play_scene}
        self.controller.init_world()
        self.start()

    def pyxel_init(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Rust[2D]ust")
        pyxel.load(resource_path("assets.pyxres"))
        self.pyxel = pyxel

    def resume(self):
        raise NotImplementedError

    def start(self):
        save_thread = Thread(target=save_game_periodically, args=(self,))
        save_thread.start()
        self.pyxel.run(self.update, self.draw)

    def update(self):
        self.model.background.update()
        self.sceneUpdateDict[self.scene]()

    def num_type(self, t):
        return len([x for x in self.model.gameObjects if isinstance(x, t)])

    def get_relative_xy(self):
        return (
            self.model.player.x - SCREEN_WIDTH / 2,
            self.model.player.y - SCREEN_HEIGHT / 2,
        )

    def update_play_scene(self):  # todo (this goes in the controller)
        self.controller.collision_detection(self.model.gameObjects)
        update_list(self.model.persistentGameObjects)
        update_list([x for x in self.model.gameObjects if x.nearPlayer(self.model.gameObjects, self.model.player)])
        cleanup_list(self.model.persistentGameObjects)
        cleanup_list(self.model.gameObjects)

    def draw(self):
        relx, rely = self.get_relative_xy()
        self.pyxel.cls(0)
        self.pyxel.camera(
            self.model.player.x - SCREEN_WIDTH / 2,
            self.model.player.y - SCREEN_HEIGHT / 2,
        )
        self.model.background.draw(
            (self.model.player.x - SCREEN_WIDTH / 2) / BASE_BLOCK,
            (self.model.player.y - SCREEN_HEIGHT / 2) / BASE_BLOCK,
        )
        self.sceneDrawDict[self.scene]()
        self.pyxel.text(relx + 39, rely + 4, f"Health: {self.model.player.health}", 7)
        self.pyxel.text(relx + 39, rely + 16, f"Hunger: {self.model.player.hunger}", 7)
        self.pyxel.text(relx + 39, rely + 24, f"Ammo: {self.model.player.ammo}", 7)
        # todo: why the heck is player.x and y a float?
        self.pyxel.text(
            relx + 39,
            rely + 32,
            f"Coord: {int(self.model.player.x)}, {int(self.model.player.y)}",
            7,
        )
        y = 32 + 8
        inv_dict = self.model.player.inventory.dict()
        count = 1
        for each in inv_dict:
            self.pyxel.text(
                relx + 39,
                rely + y,
                f"[{count}] {each.__name__}(s): {inv_dict[each]}",
                7,
            )
            y += 8
            count += 1
            # pyxel.text(relx + 39, rely+36, f"Bones: {self.model.player.bones}", 7)
            # pyxel.text(relx + 39, rely+42, f"bricks: {self.model.player.bricks}", 7)

    def draw_play_scene(self):
        draw_list([x for x in self.model.gameObjects if x.nearPlayer(self.model.gameObjects, self.model.player)])
        draw_list(self.model.persistentGameObjects)
        draw_list(self.uiObjects)
