import random

import pyxel

from .basegameobject import BaseGameObject
from ..constants import (
    BASE_BLOCK,
    WORLD_MULTIPLIER,
    BLOCK_WIDTH,
    BLOCK_HEIGHT,
    BLAST_START_RADIUS,
    BLAST_END_RADIUS,
    BLAST_COLOR_IN,
    BLAST_COLOR_OUT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)

BULLETS_FIRED = 0


# make abstract class probably


class Point(BaseGameObject):
    def __init__(self, x, y, parent, app):
        super(Point, self).__init__(x, y, self, app)
        self.x, self.y = x, y
        self.w, self.h = (10, 10)

    def collide(self, other):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class Background:
    U = 32
    V = 32

    def __init__(self, width, height, app):
        self.app = app
        self.tiles = []  # [[(int, int)]]
        self.width = width * WORLD_MULTIPLIER
        self.height = height * WORLD_MULTIPLIER

        opts = (1, -1)

        for _ in range(width * WORLD_MULTIPLIER):
            tmp = []
            for _ in range(height * WORLD_MULTIPLIER):
                tmp.append((random.choice(opts), random.choice(opts)))
            self.tiles.append(tmp)

    def update(self):
        pass

    def draw(self, viewx, viewy):
        viewx = int(viewx)
        viewy = int(viewy)
        for x in range(viewx - 4, viewx + BLOCK_WIDTH + 8):
            for y in range(viewy - 4, viewy + BLOCK_HEIGHT + 8):
                # pyxel.pset(x, y, int(pyxel.noise(x, y))%16)
                pyxel.blt(
                    x * BASE_BLOCK,
                    y * BASE_BLOCK,
                    0,
                    self.U,
                    self.V,
                    BASE_BLOCK * self.tiles[x][y][0],
                    BASE_BLOCK * self.tiles[x][y][1],
                )


class Cursor(BaseGameObject):
    def __init__(self, x, y, parent, app):
        super().__init__(x, y, parent, app)
        self.x = x
        self.y = y
        self.U = 48
        self.V = 0
        self.W = 16
        self.H = 16
        self.app = app

    def update(self):
        self.x = pyxel.mouse_x + (self.parent.x - SCREEN_WIDTH / 2)
        self.y = pyxel.mouse_y + (self.parent.y - SCREEN_HEIGHT / 2)

    def draw(self):
        pyxel.blt(self.x - 8, self.y - 8, 0, self.U, self.V, self.W, self.H, 14)

    def collide(self, other):
        pass


class Blast(BaseGameObject):
    def __init__(self, x, y, player, app):
        self.x = x
        self.y = y
        self.radius = BLAST_START_RADIUS
        self.is_alive = True
        self.player = player
        self.app = app

    def collide(self, other):
        pass

    def update(self):
        self.radius += 1
        if self.radius > BLAST_END_RADIUS:
            self.is_alive = False

    def draw(self):
        pyxel.circ(self.x, self.y, self.radius, BLAST_COLOR_IN)
        pyxel.circb(self.x, self.y, self.radius, BLAST_COLOR_OUT)
