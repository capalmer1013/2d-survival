import pyxel

from .attributes import Inventory
from .creature import Creature
from .items import Brick, Food, Bones, Door, Health, Barrel, StorageChest, Ammo
from .npc import Enemy
from ..constants import PLAYER_WIDTH, PLAYER_HEIGHT, WORLD_MULTIPLIER


class Player(Creature):
    U = 32
    V = 16
    w = PLAYER_WIDTH
    h = PLAYER_HEIGHT

    def __init__(self, x, y, parent, app):
        super().__init__(x, y, parent, app)
        self.maxHealth = 100
        self.ammo = 10
        self.health = self.maxHealth
        self.hunger, self.maxHunger = (100, 100)
        self.damageCount = 0
        self.hungerCount = 0
        self.dieSound, self.damageSound = True, True
        self.bones = 0
        self.inventory = Inventory()
        self.getInventory = None

    def update(self):
        self.hungerUpdate()
        if self.health <= 0:
            self.die()
        self.moved = False
        # check for player boundary collision
        self.x = max(self.x, 0)
        self.x = min(self.x, WORLD_MULTIPLIER * pyxel.width - self.w)
        self.y = max(self.y, 0)
        self.y = min(self.y, WORLD_MULTIPLIER * pyxel.height - self.h)

        # move player
        self.getInventory = None

    def die(self):
        self.is_alive = False
        self.app.model.gameObjects.append(
            self.deathClass(self.x + self.w / 2, self.y + self.h / 2, self, self.app)
        )
        pyxel.play(0, 0)
        self.health = 100

    def collide(self, other):
        if isinstance(other, Enemy):
            self.takeDamage(other.damage)
            other.bounceBack(self)
            self.bounceBack(other)

        if isinstance(other, Brick):
            if not other.placed:
                self.inventory.append(other)
                other.is_alive = False
            else:
                self.bounceBack(other)

        if isinstance(other, Food):
            self.eat(other.amount)

        if isinstance(other, Health):
            if self.health != self.maxHealth:
                self.heal(other.amount, True)

        if isinstance(other, Bones):
            self.bones += 1

        if isinstance(other, Barrel):
            self.bounceBack(other)

        if isinstance(other, Door):
            if not other.placed:
                self.inventory.append(other)
                self.app.model.gameObjects.remove(other)
            else:
                if other.parent is not self:
                    self.bounceBack(other)

        if isinstance(other, StorageChest):
            if not other.placed:
                self.inventory.append(other)
                self.app.model.gameObjects.remove(other)
            else:
                if other.parent is not self:
                    self.bounceBack(other)
                else:
                    self.getInventory = other

        if isinstance(other, Ammo):
            other.is_alive = False
            self.ammo += other.amount
