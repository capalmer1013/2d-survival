from threading import Thread

import pyxel

from gameObjects import (
    BASE_BLOCK,
    BLOCK_HEIGHT,
    BLOCK_WIDTH,
    SCENE_PLAY,
    Cursor,
    Player,
    cleanup_list,
    draw_list,
    resource_path,
    update_list,
)
from game_controller import GameController
from game_model import GameModel
from savethread import save_game_periodically


class GameView:
    SCREEN_WIDTH = BASE_BLOCK * BLOCK_WIDTH
    SCREEN_HEIGHT = BASE_BLOCK * BLOCK_HEIGHT

    def __init__(self, game_state_query=None):
        self.gameStateQuery = game_state_query
        self.pyxel = pyxel
        self.scene = SCENE_PLAY
        self.uiObjects = []
        self.pyxel_init()
        self.player = Player(self.pyxel.width / 2, self.pyxel.height - 20, self, self)
        self.cursor = Cursor(0, 0, self.player, self)
        self.model = GameModel()
        self.controller = GameController()
        self.model.gameObjects.append(self.player)
        self.model.persistentGameObjects.append(self.cursor)

        # config
        self.sceneUpdateDict = {SCENE_PLAY: self.update_play_scene}
        self.sceneDrawDict = {SCENE_PLAY: self.draw_play_scene}
        self.controller.init_world()
        self.start()

    def pyxel_init(self):
        pyxel.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, title="Rust2Dust")
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
            self.player.x - self.SCREEN_WIDTH / 2,
            self.player.y - self.SCREEN_HEIGHT / 2,
        )

    def update_play_scene(self):
        if self.gameStateQuery:
            self.gameStateQuery(self)
        self.controller.collision_detection()
        update_list(self.model.persistentGameObjects)
        update_list([x for x in self.model.gameObjects if x.nearPlayer()])
        cleanup_list(self.model.persistentGameObjects)
        cleanup_list(self.model.gameObjects)

    def draw(self):
        relx, rely = self.get_relative_xy()
        self.pyxel.cls(0)
        self.pyxel.camera(
            self.player.x - self.SCREEN_WIDTH / 2,
            self.player.y - self.SCREEN_HEIGHT / 2,
        )
        self.model.background.draw(
            (self.player.x - self.SCREEN_WIDTH / 2) / BASE_BLOCK,
            (self.player.y - self.SCREEN_HEIGHT / 2) / BASE_BLOCK,
        )
        self.sceneDrawDict[self.scene]()
        self.pyxel.text(relx + 39, rely + 4, f"Health: {self.player.health}", 7)
        self.pyxel.text(relx + 39, rely + 16, f"Hunger: {self.player.hunger}", 7)
        self.pyxel.text(relx + 39, rely + 24, f"Ammo: {self.player.ammo}", 7)
        # todo: why the heck is player.x and y a float?
        self.pyxel.text(
            relx + 39,
            rely + 32,
            f"Coord: {int(self.player.x)}, {int(self.player.y)}",
            7,
        )
        y = 32 + 8
        inv_dict = self.player.inventory.dict()
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
            # pyxel.text(relx + 39, rely+36, f"Bones: {self.player.bones}", 7)
            # pyxel.text(relx + 39, rely+42, f"bricks: {self.player.bricks}", 7)

    def draw_play_scene(self):
        draw_list([x for x in self.model.gameObjects if x.nearPlayer()])
        draw_list(self.model.persistentGameObjects)
        draw_list(self.uiObjects)
