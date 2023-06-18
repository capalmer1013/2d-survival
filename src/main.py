import itertools
from threading import Thread

import pyxel

from gameObjects import (BASE_BLOCK, BLOCK_HEIGHT, BLOCK_WIDTH, SCENE_GAMEOVER,
                         SCENE_PLAY, SCENE_TITLE, WORLD_MULTIPLIER, Ammo,
                         Background, Barrel, Bear, Bones, Brick, Bullet,
                         Creature, Cursor, Door, Enemy, Food,
                         GameObjectContainer, Health, Item, Player,
                         StorageChest, cleanup_list, collision, distance,
                         draw_list, resource_path, update_list)
from savethread import save_game_periodically, load_most_recent_game


class Game:
    SCREEN_WIDTH = BASE_BLOCK * BLOCK_WIDTH
    SCREEN_HEIGHT = BASE_BLOCK * BLOCK_HEIGHT
    WORLD_WIDTH = BASE_BLOCK * BLOCK_WIDTH * WORLD_MULTIPLIER
    WORLD_HEIGHT = BASE_BLOCK * BLOCK_HEIGHT * WORLD_MULTIPLIER

    def __init__(
            self, client=False, game_state_query=None
    ):
        self.gameStateQuery = game_state_query
        self.pyxel = pyxel
        self.client = client
        self.scene = SCENE_TITLE
        self.score = 0
        self.gameObjects = GameObjectContainer(self)
        self.persistentGameObjects = []
        self.uiObjects = []
        self.background = Background(BLOCK_WIDTH, BLOCK_HEIGHT, self)
        self.maxEnemies = 100
        self.numEnemies = 0
        self.numBricks = 0

        self.pyxel_init()

        self.player = Player(
            self.pyxel.width / 2, self.pyxel.height - 20, self, self
        )
        self.cursor = Cursor(0, 0, self.player, self)
        self.gameObjects.append(self.player)
        self.persistentGameObjects.append(self.cursor)

        # config
        self.sceneUpdateDict = {
            SCENE_TITLE: self.update_title_scene,
            SCENE_PLAY: self.update_play_scene,
            SCENE_GAMEOVER: self.update_gameover_scene,
        }

        self.sceneDrawDict = {
            SCENE_TITLE: self.draw_title_scene,
            SCENE_PLAY: self.draw_play_scene,
            SCENE_GAMEOVER: self.draw_gameover_scene,
        }
        self.collisionList = [
            (Enemy, Bullet),
            (Enemy, Player),
            (Player, Ammo),
            (Player, Health),
            (Enemy, Enemy),
            (Enemy, Brick),
            (Player, Brick),
            (Player, Food),
            (Enemy, Food),
            (Player, Bones),
            (Bullet, Brick),
            (Bullet, Barrel),
            (Player, Barrel),
            (Creature, Door),
            (Player, StorageChest),
            (StorageChest, Item),
        ]
        self.init_world()
        self.start()

    def pyxel_init(self):
        pyxel.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, title="Rust2Dust")
        pyxel.load(resource_path("assets.pyxres"))
        self.pyxel = pyxel

    def resume(self):
        self.pyxel_init()
        self.start()

    def start(self):
        save_thread = Thread(target=save_game_periodically, args=(self,))
        save_thread.start()
        self.pyxel.run(self.update, self.draw)

    def spawn_instance(self, T):
        tmp = T(
            self.pyxel.rndi(0, self.WORLD_WIDTH - T.w),
            self.pyxel.rndi(0, self.WORLD_HEIGHT - T.h),
            self,
            self,
        )
        if distance(self.player, tmp) > BASE_BLOCK * 4:
            self.gameObjects.append(tmp)

    def init_world(self, multiplier=10):
        for _ in range(int(15 * multiplier)):
            self.spawn_instance(Enemy)

        for _ in range(int(25 * multiplier)):
            self.spawn_instance(Bear)

        for _ in range(int(50 * multiplier)):
            self.spawn_instance(Ammo)

        for _ in range(int(20 * multiplier)):
            self.spawn_instance(Brick)

        for _ in range(int(50 * multiplier)):
            self.spawn_instance(Barrel)

    def update(self):
        self.background.update()
        self.sceneUpdateDict[self.scene]()

    def collision_detection(self):
        current_view_game_objects = [x for x in self.gameObjects if x.nearPlayer()]
        for each in self.collisionList:
            collidable_objects = [
                x
                for x in current_view_game_objects
                if isinstance(x, each[0]) or isinstance(x, each[1])
            ]
            collide_tuple = itertools.combinations(collidable_objects, 2)
            for a, b in collide_tuple:
                if collision(a, b):
                    b.collide(a)
                    a.collide(b)

    def num_type(self, t):
        return len([x for x in self.gameObjects if isinstance(x, t)])

    def get_relative_xy(self):
        return (
            self.player.x - self.SCREEN_WIDTH / 2,
            self.player.y - self.SCREEN_HEIGHT / 2,
        )

    def update_title_scene(self):
        if pyxel.btnp(pyxel.KEY_RETURN):
            # self.initWorld()
            self.scene = SCENE_PLAY

    def update_play_scene(self):
        if self.gameStateQuery:
            self.gameStateQuery(self)
        self.collision_detection()
        update_list(self.persistentGameObjects)
        update_list([x for x in self.gameObjects if x.nearPlayer()])
        cleanup_list(self.persistentGameObjects)
        cleanup_list(self.gameObjects)

    def update_gameover_scene(self):
        update_list(self.gameObjects)
        cleanup_list(self.gameObjects)

        if self.pyxel.btnp(self.pyxel.KEY_RETURN):
            self.scene = SCENE_PLAY
            self.player.x = self.pyxel.width / 2
            self.player.y = self.pyxel.height / 2
            self.score = 0
            self.gameObjects.clear()
            self.gameObjects.append(self.player)

    def draw(self):
        relx, rely = self.get_relative_xy()
        self.pyxel.cls(0)
        self.pyxel.camera(
            self.player.x - self.SCREEN_WIDTH / 2,
            self.player.y - self.SCREEN_HEIGHT / 2,
        )
        self.background.draw(
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

    def draw_title_scene(self):
        self.pyxel.text(35, 66, "Rust2Dust", self.pyxel.frame_count % 16)

    def draw_play_scene(self):
        draw_list([x for x in self.gameObjects if x.nearPlayer()])
        draw_list(self.persistentGameObjects)
        draw_list(self.uiObjects)

    def draw_gameover_scene(self):
        draw_list(self.gameObjects)
        draw_list(self.persistentGameObjects)
        pyxel.text(43, 66, "GAME OVER", 8)


if __name__ == "__main__":
    if loaded_game := load_most_recent_game():
        loaded_game.resume()
    else:
        Game()
