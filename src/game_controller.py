import itertools

import pyxel

from constants import SCREEN_HEIGHT, SCREEN_WIDTH, SCENE_PLAY
from gameObjects import (
    Ammo,
    Barrel,
    Brick,
    Bear,
    Enemy,
    Player,
    Bullet,
    Health,
    Food,
    Bones,
    Creature,
    Door,
    StorageChest,
    Item,
    Cursor
)
from game_model import GameModel
from utils import collision, update_list, cleanup_list


class GameController:
    def __init__(self):
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
        self.sceneUpdateDict = {SCENE_PLAY: self.update_play_scene}
        self.model = GameModel()

    def spawn_instance(
            self,
            TypeClass,
            min_xy: tuple = (0, SCREEN_WIDTH),
            max_xy: tuple = (0, SCREEN_HEIGHT),
    ):
        self.model.gameObjects.append(
            TypeClass(
                pyxel.rndi(min_xy[0], max_xy[0] - TypeClass.w),
                pyxel.rndi(min_xy[1], max_xy[1] - TypeClass.h),
                self,
                self,
            )
        )
        # todo: generalize so we don't depend on only 1 player character existing
        # if distance(player, tmp) > BASE_BLOCK * 4:
        #     game_objects.append(tmp)

    def create_player_character(self):
        """
        return: player uuid, cursor uuid
        """
        player = Player(pyxel.width / 2, pyxel.height - 20, self, self)
        self.model.gameObjects.append(player)
        cursor = Cursor(0, 0, player, self)
        self.model.persistentGameObjects.append(cursor)  # todo: cursor object should probably only be stored in view
        return player, cursor

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

    def collision_detection(self, game_objects):  # todo: reimplement with quadtree
        for each in self.collisionList:
            collidable_objects = [
                x
                for x in game_objects
                if isinstance(x, each[0]) or isinstance(x, each[1])
            ]
            collide_tuple = itertools.combinations(collidable_objects, 2)
            for a, b in collide_tuple:
                if collision(a, b):
                    b.collide(a)
                    a.collide(b)

    def update(self, scene):
        self.sceneUpdateDict[scene]()

    def update_play_scene(self):  # todo (this goes in the controller)
        self.collision_detection(self.model.gameObjects)
        update_list(self.model.persistentGameObjects)
        update_list(self.model.gameObjects)
        cleanup_list(self.model.persistentGameObjects)
        cleanup_list(self.model.gameObjects)
