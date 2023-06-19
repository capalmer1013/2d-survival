import random

import pyxel

from .creature import Creature
from .items import Bones, BuildingMaterial, Food
from .misc import Point
from .projectiles import Bullet
from ..constants import (
    ENEMY_WIDTH,
    ENEMY_SPEED,
    ENEMY_HEIGHT,
    BASE_BLOCK,
    BLOCK_WIDTH,
    BLOCK_HEIGHT,
)
from ..utils import distance, stepToward


class Enemy(Creature):
    w = ENEMY_WIDTH
    h = ENEMY_HEIGHT

    def __init__(self, x, y, parent, app, *args, **kwargs):
        super().__init__(x, y, parent, app, *args, **kwargs)
        self.U, self.V = random.choice([(32, 16), (48, 16), (48, 32), (48, 48)])
        self.deathClass = Bones
        self.timer_offset = pyxel.rndi(0, 59)
        self.stepCount = 0
        self.state = self.stateInit
        self.targetPoint = Point(
            random.randint(0, BASE_BLOCK * BLOCK_WIDTH),
            random.randint(0, BASE_BLOCK + BLOCK_HEIGHT),
            self,
            self.app,
        )
        self.hungerStateLevel = 3
        self.speed = ENEMY_SPEED
        self.aggressiveness = random.uniform(0.0, 1.0)
        self.attackDistance = BASE_BLOCK * 10 * self.aggressiveness

    def collide(self, other):
        if isinstance(other, Bullet):
            self.takeDamage(other.damage)
        if isinstance(other, Enemy):
            self.bounceBack(other)
        if isinstance(other, BuildingMaterial):
            if other.placed:
                other.takeDamage(1)
                self.bounceBack(other)
        if isinstance(other, Food):
            self.eat(other.amount)
            self.targetPoint = None

    def stateInit(self):
        self.moved = False
        if self.stepCount > 30:
            self.stepCount = 0
            return random.choice([self.stateAttack, self.stateRandomWalk])
        return self.stateInit

    def stateLookForFood(self):
        if self.hunger > self.hungerStateLevel:
            if self.hunger >= self.maxHunger:
                return self.stateInit
            else:
                return random.choice([self.stateRandomWalk, self.stateLookForFood])
        nearbyFood = sorted(
            [
                x
                for x in self.app.model.gameObjects.getNearbyElements(self)
                if isinstance(x, Food)
            ],
            key=lambda x: distance(self, x),
        )
        if nearbyFood:
            self.step_toward_point(nearbyFood[0])
        else:
            self.stateRandomWalk()
        return self.stateLookForFood

    # use this method in other places when stepping toward random point
    def step_toward_point(self, pnt=None):
        if not pnt or not self.targetPoint:
            randx, randy = random.randint(
                0, self.app.model.WORLD_WIDTH
            ), random.randint(0, self.app.model.WORLD_HEIGHT)
            self.targetPoint = Point(randx, randy, self, self.app)
        else:
            self.targetPoint = pnt
        self.x, self.y, _, _ = stepToward(self.targetPoint, self, ENEMY_SPEED)

    def stateRandomWalk(self):
        self.moved = True
        if not self.targetPoint:
            randx, randy = random.randint(
                0, self.app.model.WORLD_WIDTH
            ), random.randint(0, self.app.model.WORLD_HEIGHT)
            self.targetPoint = Point(randx, randy, self, self.app)
        if self.stepCount % 120 == 0:
            self.stepCount = 0
            self.targetPoint = None
            return random.choice(
                [self.stateRandomWalk, self.stateInit, self.stateLookForFood]
            )

        self.x, self.y, _, _ = stepToward(self.targetPoint, self, ENEMY_SPEED)
        self.app.model.gameObjects.updateObject(self)
        if self.app.model.player in self.app.model.gameObjects.getNearbyElements(self):
            if (
                    distance(self, self.app.model.player) < self.attackDistance
                    and self.app.model.player.is_alive
            ):
                self.stepCount = 0
                return self.stateAttack
        return self.stateRandomWalk

    def stateAttack(self):
        self.moved = True
        self.hunger -= 0.1
        enemy_target = self.app.model.get_closest_creature(self.x, self.y)
        self.x, self.y, h, w = stepToward(enemy_target, self, self.speed * 3)
        self.app.model.gameObjects.updateObject(self)
        if self.stepCount > 240:
            self.stepCount = 0
            return random.choice(
                [self.stateAttack, self.stateInit, self.stateRandomWalk]
            )

        if distance(self, self.app.model.player) > self.attackDistance:
            self.stepCount = 0
            return self.stateRandomWalk

        return self.stateAttack

    def update(self):
        self.hungerUpdate()
        self.moved = False
        if self.hunger < self.hungerStateLevel:
            self.state = self.stateLookForFood()
        else:
            self.state = self.state()
        self.stepCount += 1


class Bear(Enemy):
    w = ENEMY_WIDTH
    h = ENEMY_HEIGHT

    def __init__(self, x, y, player, app):
        super().__init__(x, y, player, app)
        self.U, self.V = (0, 32)
        self.speed = ENEMY_SPEED * 1.5
        self.damage = 15
        self.deathClass = Food
        self.aggressiveness = random.uniform(0.5, 1.0)
        self.attackDistance = BASE_BLOCK * 10 * self.aggressiveness
        self.health, self.maxHealth = (200, 200)
