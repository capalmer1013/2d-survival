import itertools

import pyxel

from .constants import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SCENE_PLAY,
    MOVE_UP_KEY,
    MOVE_DOWN_KEY,
    MOVE_LEFT_KEY,
    MOVE_RIGHT_KEY,
    PLAYER_SPEED,
    PLAYER_WIDTH,
    BULLET_WIDTH,
    BULLET_HEIGHT,
)
from .game_objects import (
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
    Door,
    StorageChest,
    Item,
    Point,
    Creature
)
from .utils import collision, update_list, cleanup_list


class GameController:
    def __init__(self, model):
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
        self.model = model

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
        return player

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


class InputController:
    def __init__(self, model):
        self.model = model

    def move_controls(self, player):
        if pyxel.btn(MOVE_LEFT_KEY):
            player.x -= PLAYER_SPEED
        if pyxel.btn(MOVE_RIGHT_KEY):
            player.x += PLAYER_SPEED
        if pyxel.btn(MOVE_UP_KEY):
            player.y -= PLAYER_SPEED
        if pyxel.btn(MOVE_DOWN_KEY):
            player.y += PLAYER_SPEED
        self.model.gameObjects.updateObject(player)

    def shoot_controls(self, player, cursor):
        # shoot
        if player.ammo > 0:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.model.gameObjects.append(
                    Bullet(
                        player.x + (PLAYER_WIDTH - BULLET_WIDTH) / 2,
                        player.y - BULLET_HEIGHT / 2,
                        player,
                        player.app,
                        point=Point(cursor.x, cursor.y, player, player.app),
                    )
                )
                pyxel.play(0, 1)
                player.ammo -= 1

        if pyxel.btnp(pyxel.KEY_SPACE):
            player.melee()

        inventory_index = None
        if pyxel.btnp(pyxel.KEY_1):
            inventory_index = 0
        if pyxel.btn(pyxel.KEY_2):
            inventory_index = 1
        if pyxel.btnp(pyxel.KEY_3):
            inventory_index = 2
        if pyxel.btn(pyxel.KEY_4):
            inventory_index = 3
        if pyxel.btnp(pyxel.KEY_5):
            inventory_index = 4
        try:
            if player.getInventory:
                player.inventory.append(
                    player.getInventory.inventory.getItem(inventory_index)(
                        0, 0, player, player.app, amount=1
                    )
                )
            else:
                self.model.gameObjects.append(
                    player.inventory.getItem(inventory_index)(
                        int(self.parent.cursor.x / 8) * 8,
                        int(self.parent.cursor.y / 8) * 8,
                        self,
                        player.app,
                        placed=True,
                        amount=1,
                    )
                )
        except TypeError as e:
            # print(e)
            pass
        except IndexError as e:
            # print(e)
            pass
            # inventory should probably be its own class
