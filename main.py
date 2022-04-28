import pyxel
from constants import *
from utils import *
from gameObjects import *

gameObjects = []


class App:
    SCREEN_WIDTH = BASE_BLOCK * BLOCK_WIDTH
    SCREEN_HEIGHT = BASE_BLOCK * BLOCK_HEIGHT

    def __init__(self):
        pyxel.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, title="Survival Game")
        pyxel.load(resource_path("assets.pyxres"))
        pyxel.sound(0).set("a3a2c1a1", "p", "7", "s", 5)
        pyxel.sound(1).set("a3a2c2c2", "n", "7742", "s", 10)
        self.scene = SCENE_TITLE
        self.score = 0
        self.background = Background(BLOCK_WIDTH, BLOCK_HEIGHT)
        self.player = Player(pyxel.width / 2, pyxel.height - 20, gameObjects)
        self.sceneUpdateDict = {SCENE_TITLE: self.update_title_scene,
                                SCENE_PLAY: self.update_play_scene,
                                SCENE_GAMEOVER: self.update_gameover_scene}

        self.sceneDrawDict = {SCENE_TITLE: self.draw_title_scene,
                              SCENE_PLAY: self.draw_play_scene,
                              SCENE_GAMEOVER: self.draw_gameover_scene}
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.KEY_Q):
            pyxel.quit()
        self.background.update()
        self.sceneUpdateDict[self.scene]()

    def update_title_scene(self):
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.scene = SCENE_PLAY

    def collision(self, a, b):
        return a.x + a.w > b.x and b.x + b.w > a.x and a.y + a.h > b.y and b.y + b.h > a.y

    def collisionDetection(self):
        # todo: generalize collision detection
        enemies = [x for x in gameObjects if type(x) == Enemy]
        bullets = [x for x in gameObjects if type(x) == Bullet]
        for enemy in enemies:
            for bullet in bullets:
                if self.collision(enemy, bullet):
                    enemy.is_alive = False
                    bullet.is_alive = False
                    gameObjects.append(
                        Blast(enemy.x + ENEMY_WIDTH / 2, enemy.y + ENEMY_HEIGHT / 2)
                    )
                    pyxel.play(1, 1)
                    self.score += 10

        for enemy in enemies:
            if self.collision(self.player, enemy):
                enemy.is_alive = False
                gameObjects.append(
                    Blast(
                        self.player.x + PLAYER_WIDTH / 2,
                        self.player.y + PLAYER_HEIGHT / 2,
                    )
                )
                pyxel.play(1, 1)
                self.scene = SCENE_GAMEOVER

    def spawnEnemies(self):
        if pyxel.frame_count % 12 == 0:
            tmp = Enemy(pyxel.rndi(0, pyxel.width - ENEMY_WIDTH), pyxel.rndi(0, pyxel.height - ENEMY_HEIGHT), self.player)
            if distance(self.player, tmp) > 32:
                gameObjects.append(tmp)
            pass

    def update_play_scene(self):
        self.spawnEnemies()
        self.collisionDetection()
        self.player.update()
        update_list(gameObjects)
        cleanup_list(gameObjects)

    def update_gameover_scene(self):
        update_list(gameObjects)
        cleanup_list(gameObjects)

        if pyxel.btnp(pyxel.KEY_RETURN):
            self.scene = SCENE_PLAY
            self.player.x = pyxel.width / 2
            self.player.y = pyxel.height / 2
            self.score = 0
            gameObjects.clear()

    def draw(self):
        pyxel.cls(0)
        self.background.draw()
        self.sceneDrawDict[self.scene]()
        pyxel.text(39, 4, f"SCORE {self.score:5}", 7)

    def draw_title_scene(self):
        pyxel.text(35, 66, "AirStrike Revolved Movement", pyxel.frame_count % 16)
        pyxel.text(31, 126, "- PRESS ENTER -", 13)

    def draw_play_scene(self):
        self.player.draw()
        draw_list(gameObjects)

    def draw_gameover_scene(self):
        draw_list(gameObjects)
        pyxel.text(43, 66, "GAME OVER", 8)
        pyxel.text(31, 126, "- PRESS ENTER -", 13)


App()