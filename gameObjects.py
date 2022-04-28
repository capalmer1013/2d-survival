import random
import pyxel
from constants import *
from utils import *

class BaseGameObject:
    pass


class Background:
    U = 32
    V = 0

    def __init__(self, width, height):
        self.tiles = []  # [[(int, int)]]
        self.width = width
        self.height = height
        opts = (1, -1)

        for _ in range(width):
            tmp = []
            for _ in range(height):
                tmp.append((random.choice(opts), random.choice(opts)))
            self.tiles.append(tmp)

    def update(self):
        pass

    def draw(self):
        for x in range(self.width):
            for y in range(self.height):
                # todo: refactor this to not be a steaming pile of garbage
                pyxel.blt(x*BASE_BLOCK, y*BASE_BLOCK, 0, self.U, self.V, BASE_BLOCK * self.tiles[x][y][0], BASE_BLOCK * self.tiles[x][y][1])


class Player:
    U = 16
    V = 0

    def __init__(self, x, y, gameObjects):
        self.x = x
        self.y = y
        self.w = PLAYER_WIDTH
        self.h = PLAYER_HEIGHT
        self.is_alive = True
        self.gameObjects = gameObjects
        self.ammo = 100

    def update(self):
        # move player
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_UP):
            self.y -= PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y += PLAYER_SPEED

        # check for player boundary collision
        self.x = max(self.x, 0)
        self.x = min(self.x, pyxel.width - self.w)
        self.y = max(self.y, 0)
        self.y = min(self.y, pyxel.height - self.h)

        # shoot
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.gameObjects.append(Bullet(
                self.x + (PLAYER_WIDTH - BULLET_WIDTH) / 2, self.y - BULLET_HEIGHT / 2, UP
            ))
            pyxel.play(0, 0)
        if pyxel.btnp(pyxel.KEY_W):
            self.gameObjects.append(Bullet(
                self.x + (PLAYER_WIDTH - BULLET_WIDTH) / 2, self.y + (PLAYER_WIDTH - BULLET_HEIGHT) / 2, UP
            ))
            pyxel.play(0, 0)
        if pyxel.btnp(pyxel.KEY_A):
            self.gameObjects.append(Bullet(
                self.x + (PLAYER_WIDTH - BULLET_WIDTH) / 2, self.y + (PLAYER_WIDTH - BULLET_HEIGHT) / 2, LEFT
            ))
            pyxel.play(0, 0)
        if pyxel.btnp(pyxel.KEY_S):
            self.gameObjects.append(Bullet(
                self.x + (PLAYER_WIDTH - BULLET_WIDTH) / 2, self.y + (PLAYER_WIDTH - BULLET_HEIGHT) / 2, DOWN
            ))
            pyxel.play(0, 0)
        if pyxel.btnp(pyxel.KEY_D):
            self.gameObjects.append(Bullet(
                self.x + (PLAYER_WIDTH - BULLET_WIDTH) / 2, self.y + (PLAYER_WIDTH - BULLET_HEIGHT) / 2, RIGHT
            ))
            pyxel.play(0, 0)

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.U, self.V, self.w , self.h, 14)
        #pyxel.blt(self.x, self.y, 0, 0, 0, self.w, self.h, 0)


class Bullet:
    def __init__(self, x, y, dir):
        self.dirDict = {UP: (0, -1), DOWN: (0, 1), LEFT: (-1, 0), RIGHT: (1, 0)}
        self.x = x
        self.y = y
        self.w = BULLET_WIDTH
        self.h = BULLET_HEIGHT
        self.is_alive = True
        self.dir = dir
        self.maxDistance = 60
        self.distance = 0

    def update(self):
        self.x, self.y = self.x + BULLET_SPEED*self.dirDict[self.dir][0], self.y + BULLET_SPEED*self.dirDict[self.dir][1]
        self.distance += 1
        if self.distance > self.maxDistance:
            self.is_alive = False

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, BULLET_COLOR)


class Enemy:
    U = 0
    V = 16

    def __init__(self, x, y, player):
        self.x = x
        self.y = y
        self.w = ENEMY_WIDTH
        self.h = ENEMY_HEIGHT
        self.dir = [1, 1]
        self.timer_offset = pyxel.rndi(0, 59)
        self.is_alive = True
        self.player = player
        self.stepCount = 0
        self.state = self.stateInit

    def stateInit(self):
        if self.stepCount > 30:
            self.stepCount = 0
            return self.stateAttack
        return self.stateInit

    def stateAttack(self):
        self.x, self.y, self.dir[0], self.dir[1] = stepToward(self.player, self, ENEMY_SPEED)
        if self.stepCount > 30:
            self.stepCount = 0
            return random.choice([self.stateAttack, self.stateInit])

        return self.stateAttack

    def update(self):
        self.state = self.state()
        self.stepCount += 1

        pass

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.U, self.V, self.w * self.dir[0], self.h, 14)


class Blast:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = BLAST_START_RADIUS
        self.is_alive = True

    def update(self):
        self.radius += 1
        if self.radius > BLAST_END_RADIUS:
            self.is_alive = False

    def draw(self):
        pyxel.circ(self.x, self.y, self.radius, BLAST_COLOR_IN)
        pyxel.circb(self.x, self.y, self.radius, BLAST_COLOR_OUT)

