import pyxel
from constants import *
from utils import *
from gameObjects import *


class App:
    SCREEN_WIDTH = BASE_BLOCK * BLOCK_WIDTH
    SCREEN_HEIGHT = BASE_BLOCK * BLOCK_HEIGHT
    WORLD_WIDTH = BASE_BLOCK * BLOCK_WIDTH * WORLD_MULTIPLIER
    WORLD_HEIGHT = BASE_BLOCK * BLOCK_HEIGHT * WORLD_MULTIPLIER

    def __init__(self):
        pyxel.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, title="Survival Game")
        pyxel.load(resource_path("assets.pyxres"))
        #pyxel.sound(1).set("a3a2c1a1", "p", "7", "s", 5)
        #pyxel.sound(2).set("a3a2c2c2", "n", "7742", "s", 10)
        self.scene = SCENE_TITLE
        self.score = 0
        self.gameObjects = GameObjectContainer(self)
        self.persistentGameObjects = []
        self.background = Background(BLOCK_WIDTH, BLOCK_HEIGHT)
        self.player = Player(pyxel.width / 2, pyxel.height - 20, self.gameObjects, self)
        self.cursor = Cursor(0, 0, self)
        self.gameObjects.append(self.player)
        self.persistentGameObjects.append(self.cursor)
        self.maxEnemies = 100
        self.numEnemies = 0
        self.numBricks = 0


        # config
        self.sceneUpdateDict = {SCENE_TITLE: self.update_title_scene,
                                SCENE_PLAY: self.update_play_scene,
                                SCENE_GAMEOVER: self.update_gameover_scene}

        self.sceneDrawDict = {SCENE_TITLE: self.draw_title_scene,
                              SCENE_PLAY: self.draw_play_scene,
                              SCENE_GAMEOVER: self.draw_gameover_scene}
        self.collisionList = [(Enemy, Bullet), (Enemy, Player), (Player, Ammo), (Player, Health), (Enemy, Enemy), (Enemy, Brick), (Player, Brick)]  # todo: store game objects in 2d array with modulo of location to only do collision detection close to player
        pyxel.run(self.update, self.draw)

    def createObject(self, T):
        tmp = T(pyxel.rndi(0, self.WORLD_WIDTH - T.w), pyxel.rndi(0, self.WORLD_HEIGHT - T.h), self.player, self)
        if distance(self.player, tmp) > BASE_BLOCK * 4:
            self.gameObjects.append(tmp)

    def initWorld(self):
        for _ in range(100):
            self.createObject(Enemy)

        for _ in range(100):
            self.createObject(Ammo)

        for _ in range(100):
            self.createObject(Brick)

    def update(self):
        if pyxel.btn(pyxel.KEY_Q):
            pyxel.quit()
        self.background.update()
        self.sceneUpdateDict[self.scene]()

    def collisionDetection(self):
        for each in self.collisionList:
            aList = [x for x in self.gameObjects if isinstance(x, each[0])]
            for a in aList:
                bList = [x for x in self.gameObjects.getNearbyElements(a) if isinstance(x, each[1])]
                for b in bList:
                    if a != b and collision(a, b):
                        a.collide(b)
                        b.collide(a)

    def numType(self, t):
        return len([x for x in self.gameObjects if isinstance(x, t)])

    # todo: generalize this spawn function
    def spawnEnemies(self):
        if pyxel.frame_count % 60 == 0:
            self.numEnemies += 1
            tmp = Enemy(pyxel.rndi(0, self.WORLD_WIDTH - ENEMY_WIDTH), pyxel.rndi(0, self.WORLD_HEIGHT - ENEMY_HEIGHT), self.player, self)
            if distance(self.player, tmp) > BASE_BLOCK*4:
                self.gameObjects.append(tmp)
            pass

    def spawnAmmo(self):
        if pyxel.frame_count % 60 == 0:
            tmp = Ammo(pyxel.rndi(0, self.WORLD_WIDTH - Ammo.w), pyxel.rndi(0, self.WORLD_HEIGHT - Ammo.h))
            if distance(self.player, tmp) > BASE_BLOCK * 4:
                self.gameObjects.append(tmp)

    def spawnHealth(self):
        if pyxel.frame_count % 120 == 0:
            tmp = Health(pyxel.rndi(0, self.WORLD_WIDTH - Health.w), pyxel.rndi(0, self.WORLD_HEIGHT - Health.h))
            if distance(self.player, tmp) > BASE_BLOCK * 4:
                self.gameObjects.append(tmp)

    def spawnBricks(self):
        if pyxel.frame_count % 120 == 0:
            tmp = Brick(pyxel.rndi(0, self.WORLD_WIDTH - Brick.w), pyxel.rndi(0, self.WORLD_HEIGHT - Brick.h), self.gameObjects, self)
            if distance(self.player, tmp) > BASE_BLOCK * 4:
                self.gameObjects.append(tmp)
                self.numBricks += 1

    def getRelativeXY(self):
        return self.player.x - self.SCREEN_WIDTH/2, self.player.y - self.SCREEN_HEIGHT/2

    def update_title_scene(self):
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.initWorld()
            self.scene = SCENE_PLAY

    def update_play_scene(self):
        pyxel.camera(self.player.x-self.SCREEN_WIDTH/2, self.player.y - self.SCREEN_HEIGHT/2)
        self.spawnEnemies()
        self.spawnAmmo()
        self.spawnHealth()
        self.spawnBricks()
        self.collisionDetection()
        update_list(self.persistentGameObjects)
        update_list(self.gameObjects)
        cleanup_list(self.persistentGameObjects)
        cleanup_list(self.gameObjects)

    def update_gameover_scene(self):
        update_list(self.gameObjects)
        cleanup_list(self.gameObjects)

        if pyxel.btnp(pyxel.KEY_RETURN):
            self.scene = SCENE_PLAY
            self.player.x = pyxel.width / 2
            self.player.y = pyxel.height / 2
            self.score = 0
            self.gameObjects.clear()
            self.gameObjects.append(self.player)

    def draw(self):
        relx, rely = self.getRelativeXY()
        pyxel.cls(0)
        self.background.draw()
        self.sceneDrawDict[self.scene]()
        pyxel.text(relx+39, rely+4, f"Ammo: {self.player.ammo}", 7)
        pyxel.text(relx+39, rely+16, f"Health: {self.player.health}", 7)
        pyxel.text(relx + 39, rely+28, f"enemies: {self.numEnemies}", 7)
        pyxel.text(relx + 39, rely+36, f"bricks: {self.player.bricks}", 7)

    def draw_title_scene(self):
        pyxel.text(35, 66, "Survival game", pyxel.frame_count % 16)

    def draw_play_scene(self):
        draw_list(self.gameObjects)
        draw_list(self.persistentGameObjects)

    def draw_gameover_scene(self):
        draw_list(self.gameObjects)
        draw_list(self.persistentGameObjects)
        pyxel.text(43, 66, "GAME OVER", 8)


App()