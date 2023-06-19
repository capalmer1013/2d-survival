import pyxel

from .basegameobject import BaseGameObject
from .creature import Creature
from ..constants import (
    BULLET_SPEED,
    BULLET_WIDTH,
    BULLET_HEIGHT,
    BULLET_COLOR,
    UP,
    DOWN,
    LEFT,
    RIGHT,
)
from ..utils import collision, stepToward


class Bullet(BaseGameObject):
    w = BULLET_WIDTH
    h = BULLET_HEIGHT

    def __init__(self, x, y, player, app, direction=None, point=None, *args, **kwargs):
        super().__init__(x, y, player, app)
        global BULLETS_FIRED  # generalize this to count all instances
        BULLETS_FIRED += 1
        if direction is None and point is None:
            raise Exception("both dir and point undefined. todo: fix this")
        if direction and point:
            raise Exception("both dir and point are defined. cmon, now")

        self.dirDict = {UP: (0, -1), DOWN: (0, 1), LEFT: (-1, 0), RIGHT: (1, 0)}
        self.x = x
        self.y = y
        self.w = BULLET_WIDTH
        self.h = BULLET_HEIGHT
        self.is_alive = True
        self.dir = direction
        self.point = point
        self.maxDistance = 40
        self.distance = 0
        self.current_speed = BULLET_SPEED
        self.minSpeed = 5
        self.damage = 25

    def update(self):
        self.moved = True
        if self.dir is not None:
            self.x, self.y = (
                self.x + self.current_speed * self.dirDict[self.dir][0],
                self.y + self.current_speed * self.dirDict[self.dir][1],
            )
        if self.point is not None:
            self.x, self.y, _, _ = stepToward(self.point, self, self.current_speed)
            if collision(self, self.point):
                self.is_alive = False
        self.distance += 1
        if self.distance > self.maxDistance:
            self.is_alive = False
        if self.current_speed > self.minSpeed:
            self.current_speed -= 1

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, BULLET_COLOR)

    def collide(self, other):
        self.is_alive = False
        if isinstance(other, Creature):
            pyxel.play(0, 6)
