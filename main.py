import pyxel
from constants import *
from utils import *
from gameObjects import *


class App:
    SCREEN_WIDTH = BASE_BLOCK * BLOCK_WIDTH
    SCREEN_HEIGHT = BASE_BLOCK * BLOCK_HEIGHT

    def __init__(self):
        pyxel.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, title="Survival Game")
        pyxel.load(resource_path("assets.pyxres"))
        #pyxel.sound(1).set("a3a2c1a1", "p", "7", "s", 5)
        #pyxel.sound(2).set("a3a2c2c2", "n", "7742", "s", 10)
        self.scene = SCENE_TITLE
        self.score = 0
        self.gameObjects = []
        self.persistentGameObjects = []
        self.background = Background(BLOCK_WIDTH, BLOCK_HEIGHT)
        self.player = Player(pyxel.width / 2, pyxel.height - 20, self.gameObjects, self)
        self.cursor = Cursor(0, 0)
        self.gameObjects.append(self.player)
        self.persistentGameObjects.append(self.cursor)

        # config
        self.sceneUpdateDict = {SCENE_TITLE: self.update_title_scene,
                                SCENE_PLAY: self.update_play_scene,
                                SCENE_GAMEOVER: self.update_gameover_scene}

        self.sceneDrawDict = {SCENE_TITLE: self.draw_title_scene,
                              SCENE_PLAY: self.draw_play_scene,
                              SCENE_GAMEOVER: self.draw_gameover_scene}
        self.collisionList = [(Enemy, Bullet), (Enemy, Player), (Player, Ammo)]

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.KEY_Q):
            pyxel.quit()
        self.background.update()
        self.sceneUpdateDict[self.scene]()

    def update_title_scene(self):
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.scene = SCENE_PLAY

    def collisionDetection(self):
        for each in self.collisionList:
            aList = [x for x in self.gameObjects if isinstance(x, each[0])]
            bList = [x for x in self.gameObjects if isinstance(x, each[1])]
            for a in aList:
                for b in bList:
                    if collision(a, b):
                        a.collide(b)
                        b.collide(a)

    def spawnEnemies(self):
        if pyxel.frame_count % 12 == 0:
            tmp = Enemy(pyxel.rndi(0, pyxel.width - ENEMY_WIDTH), pyxel.rndi(0, pyxel.height - ENEMY_HEIGHT), self.player, self)
            if distance(self.player, tmp) > BASE_BLOCK*4:
                self.gameObjects.append(tmp)
            pass

    def spawnAmmo(self):
        if pyxel.frame_count % 120 == 0:
            tmp = Ammo(pyxel.rndi(0, pyxel.width - Ammo.w), pyxel.rndi(0, pyxel.height - Ammo.h))
            if distance(self.player, tmp) > BASE_BLOCK * 4:
                self.gameObjects.append(tmp)

    def update_play_scene(self):
        self.spawnEnemies()
        self.spawnAmmo()
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
        pyxel.cls(0)
        self.background.draw()
        self.sceneDrawDict[self.scene]()
        pyxel.text(39, 4, f"Ammo: {self.player.ammo}", 7)
        pyxel.text(39, 16, f"Health: {self.player.health}", 7)
        # pyxel.text(39, 28, f"damage count {self.player.damageCount}", 7)
        # pyxel.text(39, 36, f"cursor x: {self.cursor.x} y: {self.cursor.y}", 7)

    def draw_title_scene(self):
        pyxel.text(35, 66, "Survival game", pyxel.frame_count % 16)
        pyxel.text(31, 126, "- PRESS ENTER -", 13)

    def draw_play_scene(self):
        draw_list(self.gameObjects)
        draw_list(self.persistentGameObjects)

    def draw_gameover_scene(self):
        draw_list(self.gameObjects)
        draw_list(self.persistentGameObjects)
        pyxel.text(43, 66, "GAME OVER", 8)
        pyxel.text(31, 126, "- PRESS ENTER -", 13)


App()