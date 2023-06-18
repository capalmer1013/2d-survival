import itertools

import pyxel

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
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
)
from game_model import GameModel
from utils import collision


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
        current_view_game_objects = [x for x in game_objects if x.nearPlayer()]
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
