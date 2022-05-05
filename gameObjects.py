import random
from constants import *
from utils import *

BULLETS_FIRED = 0


class GameObjectContainer:
    def __init__(self, app):
        self.app = app
        self.gameList = []
        self.gridw, self.gridh = self.app.SCREEN_WIDTH//2, self.app.SCREEN_HEIGHT//2
        self.GRID = [[[] for _ in range(self.gridh)] for _ in range(self.gridw)]
        self.n = 0

    def append(self, elem):
        x, y = self.gridCoord(elem)
        elem.gridCoord = (x, y)
        self.GRID[x][y].append(elem)
        self.gameList.append(elem)

    def getNearbyElements(self, elem):  # todo: rename to more general ie. getCollisionCandidates
        x, y = self.gridCoord(elem)
        lenx, leny = len(self.GRID), len(self.GRID[x])
        # currently checks up and down adjacent. not diagonal todo: maybe add that... maybe
        return self.GRID[x][y] + self.GRID[x-1][y] + self.GRID[x+1%lenx][y] + self.GRID[x][y-1] + self.GRID[x][y+1%leny]

    def gridCoord(self, elem):
        return int(elem.x/self.gridw), int(elem.y/self.gridh)

    def updateObject(self, elem):
        x, y = self.gridCoord(elem)
        if elem not in self.GRID[x][y]:
            self.GRID[x][y].append(elem)
            oldx, oldy = elem.gridCoord
            self.GRID[oldx][oldy].remove(elem)
            elem.gridCoord = (x, y)

    def pop(self, i=None):
        x, y = self.gameList[i].gridCoord
        self.GRID[x][y].remove(self.gameList[i])
        return self.gameList.pop(i)

    def __len__(self):
        return len(self.gameList)

    def __getitem__(self, item):
        return self.gameList[item]

    def __iter__(self):
        self.n = 0
        return iter(self.gameList)

    def __next__(self):
        result = self.gameList[self.n]
        return result

    def clear(self):
        self.gameList.clear()

    def remove(self, elem):
        x, y = self.gridCoord(elem)
        self.gameList.remove(elem)
        self.GRID[x][y].remove(elem)


class Inventory:
    def __init__(self, l=None):
        self.items = {}
        if l:
            for each in l:
                self.append(each)

    def getItem(self, index):
        item = self.items[list(self.items.keys())[index]]
        if item.amount > 0:
            item.amount -= 1
            if item.amount == 0:
                self.items.pop(list(self.items.keys())[index], None)
            return item.__class__
        return None

    def append(self, item):
        if type(item) in self.items:
            self.items[type(item)].amount += item.amount
        else:
            self.items[type(item)] = item
        # if hte list is full just drop it
        pass

    def dict(self):
        return {x:self.items[x].amount for x in self.items}

    def get_all(self):
        return list(self.items.keys())


class BaseGameObject:
    U = 16
    V = 0
    def __init__(self, x, y, parent, app):
        self.x = x
        self.y = y
        self.parent = parent
        self.app = app
        self.is_alive = True
        self.moved = False
        self.gridCoord = (0, 0)

    def nearPlayer(self):
        return self in self.app.gameObjects.getNearbyElements(self.app.player)

    def collide(self, other):
        raise NotImplementedError

    def bounceBack(self, other, bounceFactor=0.5):
        self.x += (self.x - other.x) * bounceFactor
        self.y += (self.y - other.y) * bounceFactor

    def update(self):
        pass

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.U, self.V, self.w, self.h, 14)


class Item(BaseGameObject):
    def __init__(self, x, y, parent, app, amount=10):
        super().__init__(x, y, parent, app)
        self.ttl = 9000  # 5 minnutes if update gets called 30x/s
        self.amount = amount

    def update(self):
        self.ttl -= 1
        if self.ttl <= 0:
            self.is_alive = False


# make abstract class probably
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
        if self.damageSound and self in self.app.gameObjects.getNearbyElements(self.app.player):
            pyxel.play(0, 6)
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        self.is_alive = False
        self.app.gameObjects.append(self.deathClass(self.x + self.w / 2, self.y + self.h / 2, self, self.app))
        if self.dieSound:
            pyxel.play(1, 2)  # todo: distance from player affect volume level

    def eat(self, amount):
        self.hungerCount = 0
        self.targetPoint = None
        self.hunger = self.hunger + amount if self.hunger + amount <= self.maxHunger else self.maxHunger
        self.heal(amount // 2, False)

    def heal(self, amount, sound=False):
        self.health = self.health + amount if self.health + amount <= self.maxHealth else self.maxHealth
        if sound: pyxel.play(0, 7)

    def hungerUpdate(self):
        self.hungerCount += 1
        if self.hungerCount > 3600:
            if self.hungerCount % 240 == 0:
                self.hunger -= 1
                if self.hunger <= 0:
                    self.takeDamage(1)

    def melee(self):
        hit = False
        for nearby in [x for x in self.app.gameObjects.getNearbyElements(self) if distance(x, self) < BASE_BLOCK*2 and isinstance(x, Creature) and x is not self]:
            self.bounceBack(nearby)
            nearby.takeDamage(self.damage + self.bones)
            hit = True

        if hit:
            pyxel.play(0, 6)

        if self.bones:
            self.bones = max(self.bones-1, 0)

    def collide(self, other):
        self.takeDamage(other.damage)


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


class UI:
    def __init__(self, relx, rely, parent, app):
        self.relx, self.rely = relx, rely
        self.parent = parent
        self.app = app
        self.h = 16
        self.w = 128

    def update(self):
        pass

    def draw(self):
        pyxel.rect(self.app.player.x + self.relx, self.app.player.y + self.rely, self.w, self.h, 13)
        # pyxel.blt(self.relx, self.rely, 0, self.U, self.V, self.w, self.h, 14)


class Ammo(Item):
    U = 16
    V = 32
    w = 8
    h = 8

    def __init__(self, x, y, player, app, amount=10):
        super().__init__(x, y, player, app, amount=amount)
        self.amount = amount

    def collide(self, other):
        if isinstance(other, Player):
            self.is_alive = False
            other.ammo += self.amount


class BuildingMaterial(Item):
    def __init__(self, x, y, parent, app, placed=False):
        super().__init__(x, y, parent, app)
        self.app = app
        self.placed = placed
        self.amount = 10
        self.health = 100
        self.damageSound, self.dieSound = True, True

    def collide(self, other):
        if isinstance(other, Bullet):
            self.takeDamage(other.damage)

    def takeDamage(self, amount):
        if self.placed:
            self.health -= amount
            if self.health <= 0:
                self.die(True)
            if self.damageSound and self in self.app.gameObjects.getNearbyElements(self.app.player):
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
        self.app.gameObjects.append(Blast(self.x + ENEMY_WIDTH / 2, self.y + ENEMY_HEIGHT / 2, self, self.app))
        if sound:
            pyxel.play(1, 2)
        self.app.score += score


class HasInventoryMixin:
    def scatterInventory(self):
        for each in self.inventory.get_all():
            randx, randy = random.randint(-8, 8), random.randint(-8, 8)
            self.app.gameObjects.append(each(self.x + randx, self.y + randy, self, self.app))

    def takeDamage(self, amount):
        self.health -= amount
        if self.health <= 0:  # todo: move this into die function
            self.is_alive = False
            self.scatterInventory()


class StorageChest(BuildingMaterial, HasInventoryMixin):
    U = 0
    V = 24
    w = 16
    h = 8

    def __init__(self, x, y, parent, app, placed=False, amount=1):
        super().__init__(x, y, parent, app)
        self.placed = placed
        self.amount = amount

    def collide(self, other):
        if isinstance(other, Bullet):
            self.takeDamage(other.damage)


class Brick(BuildingMaterial):
    U = 24
    V = 40
    w = 8
    h = 8


class Door(BuildingMaterial):
    U = 32
    V = 64
    w = 16
    h = 16

    def __init__(self, x, y, parent, app, placed=False):
        super().__init__(x, y, parent, app)
        self.placed = placed
        self.amount = 1


class Bones(Item):
    U = 16
    V = 48

    def __init__(self, x, y, parent, app):
        super().__init__(x, y, parent, app)
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
        #self.contents = [random.choice([Door]) for _ in range(random.randint(1, 6))]

        self.inventory = Inventory([random.choice([Ammo, Health, Brick, Door, StorageChest])(0, 0, self, self.app) for _ in range(random.randint(1, 6))])

    def collide(self, other):
        if isinstance(other, Bullet):
            self.takeDamage(other.damage)


class Food(Item):
    U = 16
    V = 40
    w = 8
    h = 8

    def __init__(self, x, y, parent, app):
        super().__init__(x, y, parent, app)
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


class Player(Creature):
    U = 32
    V = 16
    w = PLAYER_WIDTH
    h = PLAYER_HEIGHT
    MOVE_LEFT_KEY = pyxel.KEY_A
    MOVE_RIGHT_KEY = pyxel.KEY_D
    MOVE_UP_KEY = pyxel.KEY_W
    MOVE_DOWN_KEY = pyxel.KEY_S

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

    def moveControls(self):
        if pyxel.btn(self.MOVE_LEFT_KEY):
            self.x -= PLAYER_SPEED
        if pyxel.btn(self.MOVE_RIGHT_KEY):
            self.x += PLAYER_SPEED
        if pyxel.btn(self.MOVE_UP_KEY):
            self.y -= PLAYER_SPEED
        if pyxel.btn(self.MOVE_DOWN_KEY):
            self.y += PLAYER_SPEED
        self.app.gameObjects.updateObject(self)

    def shootControls(self):
        # shoot
        if self.ammo > 0:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.app.gameObjects.append(Bullet(
                    self.x + (PLAYER_WIDTH - BULLET_WIDTH) / 2, self.y - BULLET_HEIGHT / 2, self, self.app, point=Point(self.app.cursor.x, self.app.cursor.y)
                ))
                pyxel.play(0, 1)
                self.ammo -= 1
        # if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
        ## todo: might use this for current selected inventory item on right mouse trigger
        #     if self.bricks > 0:
        #         self.app.gameObjects.append(Brick(int(self.app.cursor.x/8)*8, int(self.app.cursor.y/8)*8, self, self.app, placed=True))
        #         self.bricks -= 1

        if pyxel.btnp(pyxel.KEY_SPACE):
            self.melee()

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
            self.app.gameObjects.append(
                self.inventory.getItem(inventory_index)(int(self.app.cursor.x / 8) * 8,
                                                        int(self.app.cursor.y / 8) * 8,
                                                        self,
                                                        self.app,
                                                        placed=True))
        except TypeError as e:
            # print(e)
            pass
        except IndexError as e:
            # print(e)
            pass
            # inventory should probably be its own class

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
        if self.app.scene == SCENE_PLAY:
            self.moveControls()
            self.shootControls()

    def die(self):
        self.is_alive = False
        self.app.gameObjects.append(self.deathClass(self.x + self.w / 2, self.y + self.h / 2, self, self.app))
        pyxel.play(0, 0)
        self.app.scene = SCENE_GAMEOVER
        self.health = 100

    def collide(self, other):
        if isinstance(other, Enemy):
            self.takeDamage(other.damage)
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
                self.heal(other.healthAmount, True)

        if isinstance(other, Bones):
            self.bones += 1

        if isinstance(other, Barrel):
            self.bounceBack(other)

        if isinstance(other, Door):
            if not other.placed:
                self.inventory.append(other)
                self.app.gameObjects.remove(other)
            else:
                if other.parent is not self:
                    self.bounceBack(other)

        if isinstance(other, StorageChest):
            if not other.placed:
                self.inventory.append(other)
                self.app.gameObjects.remove(other)
            else:
                if other.parent is not self:
                    self.bounceBack(other)


class Bullet(BaseGameObject):
    w = BULLET_WIDTH
    h = BULLET_HEIGHT

    def __init__(self, x, y, player, app, dir=None, point=None, *args, **kwargs):
        super().__init__(x, y, player, app)
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
        self.damage = 25

    def update(self):
        self.moved = True
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
        if isinstance(other, Creature):
            pyxel.play(0, 6)


class Enemy(Creature):
    w = ENEMY_WIDTH
    h = ENEMY_HEIGHT

    def __init__(self, x, y, parent, app, *args, **kwargs):
        super().__init__(x, y, parent, app, *args, **kwargs)
        self.U, self.V = (random.choice([(32, 16), (48, 16), (48, 32), (48, 48)]))
        self.deathClass = Bones
        self.timer_offset = pyxel.rndi(0, 59)
        self.stepCount = 0
        self.state = self.stateInit
        self.targetPoint = Point(random.randint(0, BASE_BLOCK*BLOCK_WIDTH), random.randint(0, BASE_BLOCK+BLOCK_HEIGHT))
        self.hungerStateLevel = 3
        self.speed = ENEMY_SPEED
        self.aggressiveness = random.uniform(0.0, 1.0)
        self.attackDistance = BASE_BLOCK * 10 * self.aggressiveness

    def collide(self, other):
        if isinstance(other, Bullet):
            self.takeDamage(other.damage)
        if isinstance(other, Player):
            self.bounceBack(other)
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
        nearbyFood = sorted([x for x in self.app.gameObjects.getNearbyElements(self) if isinstance(x, Food)], key=lambda x: distance(self, x))
        if nearbyFood:
            self.stepTowardPoint(nearbyFood[0])
        else:
            self.stateRandomWalk()
        return self.stateLookForFood

    # use this method in other places when stepping toward random point
    def stepTowardPoint(self, pnt=None):
        if not pnt or not self.targetPoint:
            randx, randy = random.randint(0, self.app.WORLD_WIDTH), random.randint(0, self.app.WORLD_HEIGHT)
            self.targetPoint = Point(randx, randy)
        else:
            self.targetPoint = pnt
        self.x, self.y, _, _ = stepToward(self.targetPoint, self, ENEMY_SPEED)

    def stateRandomWalk(self):
        self.moved = True
        if not self.targetPoint:
            randx, randy = random.randint(0, self.app.WORLD_WIDTH), random.randint(0, self.app.WORLD_HEIGHT)
            self.targetPoint = Point(randx, randy)
        if self.stepCount % 120 == 0:
            self.stepCount = 0
            self.targetPoint = None
            return random.choice([self.stateRandomWalk, self.stateInit, self.stateLookForFood])

        self.x, self.y, _, _ = stepToward(self.targetPoint, self, ENEMY_SPEED)
        self.app.gameObjects.updateObject(self)
        if self.app.player in self.app.gameObjects.getNearbyElements(self):
            if distance(self, self.app.player) < self.attackDistance and self.app.player.is_alive:
                self.stepCount = 0
                return self.stateAttack
        return self.stateRandomWalk

    def stateAttack(self):
        self.moved = True
        self.hunger -= 0.1
        if not self.app.player.is_alive:
            return self.stateRandomWalk
        self.x, self.y, h, w = stepToward(self.app.player, self, self.speed*3)
        self.app.gameObjects.updateObject(self)
        if self.stepCount > 240:
            self.stepCount = 0
            return random.choice([self.stateAttack, self.stateInit, self.stateRandomWalk])

        if distance(self, self.app.player) > self.attackDistance:
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


class Cursor(BaseGameObject):
    def __init__(self, x, y, player, app):
        super().__init__(x, y, player, app)
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
    def __init__(self, x, y, player, app):
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

