import random

import pyxel

from .attributes import HasInventoryMixin, Inventory
from .basegameobject import BaseGameObject
from .gui import InventoryUI
from .misc import Blast
from .projectiles import Bullet
from ..constants import ENEMY_WIDTH, ENEMY_HEIGHT


class Item(BaseGameObject):
    def collide(self, other):
        raise NotImplementedError

    def __init__(self, x, y, parent, app, amount=10, placed=False):
        super().__init__(x, y, parent, app)
        self.ttl = 9000  # 5 minnutes if update gets called 30x/s
        self.amount = amount
        self.placed = placed

    def update(self):
        self.ttl -= 1
        if self.ttl <= 0:
            self.is_alive = False


class Ammo(Item):
    U = 16
    V = 32
    w = 8
    h = 8

    def __init__(self, x, y, parent, app, **kwargs):
        super().__init__(x, y, parent, app, **kwargs)

    def collide(self, other):
        pass


class BuildingMaterial(Item):
    def __init__(self, x, y, parent, app, placed=False, **kwargs):
        super().__init__(x, y, parent, app, **kwargs)
        self.app = app
        self.placed = placed
        self.amount = 10
        self.health = 100

    def collide(self, other):
        if isinstance(other, Bullet):
            self.takeDamage(other.damage)

    def takeDamage(self, amount):
        if self.placed:
            self.health -= amount
            if self.health <= 0:
                self.die(True)
            if self in self.app.model.gameObjects.getNearbyElements(
                self.app.model.player
            ):
                pyxel.play(0, 8)

    def update(self):
        self.ttl -= 1
        if self.ttl <= 0 and not self.placed:
            self.is_alive = False

    def draw(self):
        if self.placed:
            super().draw()
        else:
            if pyxel.frame_count % 3 != 0:
                super().draw()

    def die(self, sound=False, score=0):
        self.is_alive = False
        self.app.model.gameObjects.append(
            Blast(self.x + ENEMY_WIDTH / 2, self.y + ENEMY_HEIGHT / 2, self, self.app)
        )
        if sound:
            pyxel.play(1, 2)
        self.app.model.score += score


class StorageChest(BuildingMaterial, HasInventoryMixin):
    U = 0
    V = 24
    w = 16
    h = 8

    def __init__(self, x, y, parent, app, placed=False, amount=1):
        super().__init__(x, y, parent, app)
        self.placed = placed
        self.amount = amount
        self.inventory = Inventory()
        self.ui = InventoryUI(self.x, self.y, self, self.app)

    def collide(self, other):
        if isinstance(other, Bullet):
            self.takeDamage(other.damage)

        if isinstance(other, Item) and not isinstance(other, StorageChest):
            if other.placed:
                self.inventory.append(other)
                self.app.model.gameObjects.remove(other)

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.U, self.V, self.w, self.h, 14)
        self.ui.draw()


class Brick(BuildingMaterial):
    U = 24
    V = 40
    w = 8
    h = 8

    def __init__(self, x, y, parent, app, placed=False, amount=10):
        super().__init__(x, y, parent, app, placed=placed, amount=amount)
        self.amount = amount


class Door(BuildingMaterial):
    U = 32
    V = 64
    w = 16
    h = 16

    def __init__(self, x, y, parent, app, placed=False, **kwargs):
        super().__init__(x, y, parent, app, **kwargs)
        self.placed = placed
        self.amount = 1


class Bones(Item):
    U = 0
    V = 64

    def __init__(self, x, y, parent, app, **kwargs):
        super().__init__(x, y, parent, app, **kwargs)
        self.w = 16
        self.h = 16

    def collide(self, other):
        self.is_alive = False


class Barrel(Item, HasInventoryMixin):
    U = 8
    V = 48
    w = 8
    h = 16

    def __init__(self, x, y, parent, app):
        super().__init__(x, y, self, app)
        self.health = 100
        # self.contents = [random.choice([Door]) for _ in range(random.randint(1, 6))]

        self.inventory = Inventory(
            [
                random.choice([Ammo, Health, Brick, Door, StorageChest])(
                    0, 0, self, self.app
                )
                for _ in range(random.randint(1, 6))
            ]
        )

    def collide(self, other):
        if isinstance(other, Bullet):
            self.takeDamage(other.damage)


class Food(Item):
    U = 16
    V = 40
    w = 8
    h = 8

    def __init__(self, x, y, parent, app, **kwargs):
        super().__init__(x, y, parent, app, **kwargs)
        self.amount = 50

    def collide(self, other):
        if other != self.parent:
            self.is_alive = False


class Health(Item):
    U = 24
    V = 32
    w = 8
    h = 8

    def __init__(self, x, y, player, app, amount=10):
        super().__init__(x, y, player, app, amount=amount)
        self.amount = amount

    def collide(self, other):
        if isinstance(other, Player):
            if other.health != other.maxHealth:
                self.is_alive = False
