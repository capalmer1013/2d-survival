import pyxel

from .basegameobject import BaseGameObject
from .misc import Blast
from ..constants import BASE_BLOCK
from ..utils import distance


class Creature(BaseGameObject):
    U = 16
    V = 0

    def __init__(self, x, y, parent, app, damage=10, maxHunger=100):
        super().__init__(x, y, parent, app)
        self.w = BASE_BLOCK
        self.h = BASE_BLOCK
        self.HUNGER_MULTIPLIER = -0.1
        self.dir = [1, 1]
        self.dirtime = 0
        self.health, self.maxHealth = (100, 100)
        self.is_alive = True
        self.damage = damage
        self.deathClass = Blast
        self.hunger, self.maxHunger = (maxHunger, maxHunger)
        self.hungerCount = 0
        self.app = app
        self.targetPoint = None
        self.dieSound, self.damageSound = False, False
        self.bones = 0
        self.aggressiveness = 0.5
        self.inventory = []

    def debounceDir(self, w, h):
        if self.dir[0] != w or self.dir[1] != h and self.dirtime > 10:
            self.dir[0] = w
            self.dir[1] = h
            self.dirtime = 0
        self.dirtime += 1

    def takeDamage(self, amount):
        if self.damageSound and self in self.app.model.gameObjects.getNearbyElements(
            self.app.model.player
        ):
            pyxel.play(0, 6)
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        self.is_alive = False
        self.app.model.gameObjects.append(
            self.deathClass(self.x + self.w / 2, self.y + self.h / 2, self, self.app)
        )
        if self.dieSound:
            pyxel.play(1, 2)  # todo: distance from player affect volume level

    def eat(self, amount):
        self.hungerCount = 0
        self.targetPoint = None
        self.hunger = (
            self.hunger + amount
            if self.hunger + amount <= self.maxHunger
            else self.maxHunger
        )
        self.heal(amount // 2, False)

    def heal(self, amount, sound=False):
        self.health = (
            self.health + amount
            if self.health + amount <= self.maxHealth
            else self.maxHealth
        )
        if sound:
            pyxel.play(0, 7)

    def hungerUpdate(self):
        self.hungerCount += 1
        if self.hungerCount > 3600:
            if self.hungerCount % 240 == 0:
                self.hunger -= 1
                if self.hunger <= 0:
                    self.takeDamage(1)

    def melee(self):
        hit = False
        for nearby in [
            x
            for x in self.app.model.gameObjects.getNearbyElements(self)
            if distance(x, self) < BASE_BLOCK * 2
            and isinstance(x, Creature)
            and x is not self
        ]:
            self.bounceBack(nearby)
            nearby.takeDamage(self.damage + self.bones)
            hit = True

        if hit:
            pyxel.play(0, 6)

        if self.bones:
            self.bones = max(self.bones - 1, 0)

    def collide(self, other):
        self.takeDamage(other.damage)
