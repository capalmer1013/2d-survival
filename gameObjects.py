import random
import pyxel
from constants import *
from utils import *


BULLETS_FIRED = 0


class BaseGameObject:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.is_alive = True

    def collide(self, other):
        raise NotImplementedError

    def bounceBack(self, other, bounceFactor=0.5):
        self.x += (self.x - other.x) * bounceFactor
        self.y += (self.y - other.y) * bounceFactor

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.U, self.V, self.w, self.h, 14)


class Point(BaseGameObject):
    def __init__(self, x, y):
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

    def __init__(self, width, height):
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

    def draw(self):
        for x in range(self.width):
            for y in range(self.height):
                #pyxel.pset(x, y, int(pyxel.noise(x, y))%16)
                pyxel.blt(x*BASE_BLOCK, y*BASE_BLOCK, 0, self.U, self.V, BASE_BLOCK * self.tiles[x][y][0], BASE_BLOCK * self.tiles[x][y][1])

        pass


class Ammo(BaseGameObject):
    U = 16
    V = 32
    w = 8
    h = 8

    def __init__(self, x, y):
        super().__init__(x, y)
        self.ammoAmmount = 10

    def collide(self, other):
        if isinstance(other, Player):
            self.is_alive = False
            other.ammo += self.ammoAmmount

    def update(self):
        pass


class Health(BaseGameObject):
    U = 24
    V = 32
    w = 8
    h = 8

    def __init__(self, x, y, healthAmount=25):
        super().__init__(x, y)
        self.healthAmount = healthAmount

    def collide(self, other):
        if isinstance(other, Player):
            self.is_alive = False
            other.heal(self.healthAmount)

    def update(self):
        pass


class Player(BaseGameObject):
    U = 32
    V = 16
    MOVE_LEFT_KEY = pyxel.KEY_A
    MOVE_RIGHT_KEY = pyxel.KEY_D
    MOVE_UP_KEY = pyxel.KEY_W
    MOVE_DOWN_KEY = pyxel.KEY_S
    # MOVE_LEFT_KEY = pyxel.KEY_LEFT
    # MOVE_RIGHT_KEY = pyxel.KEY_RIGHT
    # MOVE_UP_KEY = pyxel.KEY_UP
    # MOVE_DOWN_KEY = pyxel.KEY_DOWN

    def __init__(self, x, y, gameObjects, app):
        self.app = app
        self.x = x
        self.y = y
        self.w = PLAYER_WIDTH
        self.h = PLAYER_HEIGHT
        self.is_alive = True
        self.gameObjects = gameObjects
        self.maxHealth = 100
        self.ammo = 100
        self.health = self.maxHealth
        self.damageCount = 0

    def moveControls(self):
        if pyxel.btn(self.MOVE_LEFT_KEY):
            self.x -= PLAYER_SPEED
        if pyxel.btn(self.MOVE_RIGHT_KEY):
            self.x += PLAYER_SPEED
        if pyxel.btn(self.MOVE_UP_KEY):
            self.y -= PLAYER_SPEED
        if pyxel.btn(self.MOVE_DOWN_KEY):
            self.y += PLAYER_SPEED

    def shootControls(self):
        # shoot
        if self.ammo > 0:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.gameObjects.append(Bullet(
                    self.x + (PLAYER_WIDTH - BULLET_WIDTH) / 2, self.y - BULLET_HEIGHT / 2, point=Point(self.app.cursor.x, self.app.cursor.y)
                ))
                pyxel.play(0, 1)
                self.ammo -= 1
        pass

    def update(self):
        # check for player boundary collision
        self.x = max(self.x, 0)
        self.x = min(self.x, WORLD_MULTIPLIER * pyxel.width - self.w)
        self.y = max(self.y, 0)
        self.y = min(self.y, WORLD_MULTIPLIER * pyxel.height - self.h)

        # move player
        if self.app.scene == SCENE_PLAY:
            self.moveControls()
            self.shootControls()

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.U, self.V, self.w, self.h, 14)

    def takeDamage(self, amount):
        self.health -= amount
        pyxel.play(0, 6)
        if self.health <= 0:
            # self.is_alive = False
            pyxel.play(0, 0)
            self.app.gameObjects.append(Blast(self.x + PLAYER_WIDTH / 2, self.y + PLAYER_HEIGHT / 2, ))
            self.app.scene = SCENE_GAMEOVER
            self.health = 100

    def heal(self, amount):
        self.health = self.health + amount if self.health + amount <= self.maxHealth else self.maxHealth
        pyxel.play(0, 7)



    def collide(self, other):
        if isinstance(other, Enemy):
            self.takeDamage(other.damage)
            self.bounceBack(other)


class Bullet:
    def __init__(self, x, y, dir=None, point=None):
        global BULLETS_FIRED # generalize this to count all instances
        BULLETS_FIRED += 1
        if not dir and not point:
            raise Exception("both dir and point undefined. todo: fix this")
        if dir and point:
            raise Exception("both dir and point are defined. cmon, now")

        self.dirDict = {UP: (0, -1), DOWN: (0, 1), LEFT: (-1, 0), RIGHT: (1, 0)}
        self.x = x
        self.y = y
        self.w = BULLET_WIDTH
        self.h = BULLET_HEIGHT
        self.is_alive = True
        self.dir = dir
        self.point = point
        self.maxDistance = 40
        self.distance = 0
        self.current_speed = BULLET_SPEED
        self.minSpeed = 5

    def update(self):
        if self.dir:
            self.x, self.y = self.x + self.current_speed*self.dirDict[self.dir][0], self.y + self.current_speed *self.dirDict[self.dir][1]
        if self.point:
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


class Enemy(BaseGameObject):
    # U = 0
    # V = 16

    def __init__(self, x, y, player, app):
        self.U, self.V = (random.choice([(32, 16), (48, 16), (48, 32), (48, 48)]))
        self.x = x
        self.y = y
        self.w = ENEMY_WIDTH
        self.h = ENEMY_HEIGHT
        self.dir = [1, 1]
        self.timer_offset = pyxel.rndi(0, 59)
        self.is_alive = True
        self.player = player
        self.app = app
        self.stepCount = 0
        self.state = self.stateInit
        self.dirtime = 0
        self.damage = 5
        self.randomPoint = BaseGameObject(random.randint(0, BASE_BLOCK*BLOCK_WIDTH), random.randint(0, BASE_BLOCK+BLOCK_HEIGHT))
        self.attackDistance = BASE_BLOCK * 5
    def die(self):
        self.is_alive = False
        self.app.gameObjects.append(Blast(self.x + ENEMY_WIDTH / 2, self.y + ENEMY_HEIGHT / 2))
        pyxel.play(1, 2)  # todo: distance from player affect volume level
        self.app.score += 10

    def collide(self, other):
        if isinstance(other, Bullet):
            self.die()
        if isinstance(other, Player):
            self.bounceBack(other)

    def debounceDir(self, w, h):
        if self.dir[0] != w or self.dir[1] != h and self.dirtime > 10:
            self.dir[0] = w
            self.dir[1] = h
            self.dirtime = 0
        self.dirtime += 1

        pass

    def stateInit(self):
        if self.stepCount > 30:
            self.stepCount = 0
            return random.choice([self.stateAttack, self.stateRandomWalk])
        return self.stateInit

    def stateRandomWalk(self):
        if self.stepCount == 0:
            self.randomPoint = Point(random.randint(0, self.app.WORLD_WIDTH), random.randint(0, self.app.WORLD_HEIGHT))
        elif self.stepCount > 120:
            self.stepCount = 0
            return random.choice([self.stateRandomWalk, self.stateInit])

        if distance(self, self.player) < self.attackDistance:
            return self.stateAttack

        self.x, self.y, _, _ = stepToward(self.randomPoint, self, ENEMY_SPEED)
        return self.stateRandomWalk

    def stateAttack(self):
        self.x, self.y, h, w = stepToward(self.player, self, ENEMY_SPEED)
        if self.stepCount > 240:
            self.stepCount = 0
            return random.choice([self.stateAttack, self.stateInit, self.stateRandomWalk])

        if distance(self, self.player) > self.attackDistance:
            return self.stateRandomWalk

        return self.stateAttack

    def update(self):
        self.state = self.state()
        self.stepCount += 1

        pass

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.U, self.V, self.w * self.dir[0], self.h, 14)


class Cursor(BaseGameObject):
    def __init__(self, x, y, app):
        super().__init__()
        self.x = x
        self.y = y
        self.U = 48
        self.V = 0
        self.W = 16
        self.H = 16
        self.app = app

    def update(self):
        self.x = pyxel.mouse_x + (self.app.player.x - self.app.SCREEN_WIDTH/2)
        self.y = pyxel.mouse_y + (self.app.player.y - self.app.SCREEN_HEIGHT/2)

    def draw(self):
        pyxel.blt(self.x-8, self.y-8, 0, self.U, self.V, self.W, self.H, 14)

    def collide(self, other):
        pass


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

