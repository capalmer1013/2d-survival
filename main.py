import cProfile
import itertools
import pyxel

from gameObjects import *


class App:
    SCREEN_WIDTH = BASE_BLOCK * BLOCK_WIDTH
    SCREEN_HEIGHT = BASE_BLOCK * BLOCK_HEIGHT
    WORLD_WIDTH = BASE_BLOCK * BLOCK_WIDTH * WORLD_MULTIPLIER
    WORLD_HEIGHT = BASE_BLOCK * BLOCK_HEIGHT * WORLD_MULTIPLIER

    def __init__(self, headless=False, networked=False, client=False, gameStateQuery=None):
        self.gameStateQuery = gameStateQuery
        self.pyxel = pyxel if not headless else FakePyxel()
        self.headless = headless
        self.networked = networked
        self.client = client
        if not headless:
            pyxel.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, title="Rust2Dust")
            pyxel.load(resource_path("assets.pyxres"))
        #pyxel.sound(1).set("a3a2c1a1", "p", "7", "s", 5)
        #pyxel.sound(2).set("a3a2c2c2", "n", "7742", "s", 10)
        self.scene = SCENE_TITLE
        self.score = 0
        self.gameObjects = GameObjectContainer(self)
        self.persistentGameObjects = []
        #self.uiObjects = [UI(-200, 80, self, self)]
        self.uiObjects = []
        self.background = Background(BLOCK_WIDTH, BLOCK_HEIGHT, self)
        if not self.headless:
            self.player = Player(self.pyxel.width / 2, self.pyxel.height - 20, self, self)
            self.cursor = Cursor(0, 0, self.player, self)
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
        self.collisionList = [(Enemy, Bullet), (Enemy, Player),
                              (Player, Ammo), (Player, Health),
                              (Enemy, Enemy), (Enemy, Brick),
                              (Player, Brick), (Player, Food),
                              (Enemy, Food), (Player, Bones),
                              (Bullet, Brick), (Bullet, Barrel),
                              (Player, Barrel), (Creature, Door),
                              (Player, StorageChest), (StorageChest, Item)]
        if headless:
            self.initWorld()
        else:
            self.start()
        print("end of __init__ ")

    def start(self):
        try:
            self.pyxel.run(self.update, self.draw)
        except:
            pass

    def spawnInstance(self, T):
        tmp = T(self.pyxel.rndi(0, self.WORLD_WIDTH - T.w), self.pyxel.rndi(0, self.WORLD_HEIGHT - T.h), self, self)
        if not self.headless:
            if distance(self.player, tmp) > BASE_BLOCK * 4:
                self.gameObjects.append(tmp)
        else:
            self.gameObjects.append(tmp)

    def initWorld(self, multiplier=10):
        for _ in range(int(15*multiplier)):
            self.spawnInstance(Enemy)

        for _ in range(int(25*multiplier)):
            self.spawnInstance(Bear)

        for _ in range(int(50*multiplier)):
            self.spawnInstance(Ammo)

        for _ in range(int(20*multiplier)):
            self.spawnInstance(Brick)

        for _ in range(int(50*multiplier)):
            self.spawnInstance(Barrel)

    def update(self):
        self.background.update()
        self.sceneUpdateDict[self.scene]()

    def collisionDetection(self):
        if self.networked and self.headless:
            currentViewGameObjects = self.gameObjects
        elif self.client:
            currentViewGameObjects = [x for x in self.gameObjects if x.nearPlayer()]
        else:
            return
        for each in self.collisionList:
            collidable_objects = [x for x in currentViewGameObjects if isinstance(x, each[0]) or isinstance(x, each[1])]
            collide_tuple = itertools.combinations(collidable_objects, 2)
            for a, b in collide_tuple:
                if collision(a, b):
                    b.collide(a)
                    a.collide(b)

    def numType(self, t):
        return len([x for x in self.gameObjects if isinstance(x, t)])

    def getRelativeXY(self):
        return self.player.x - self.SCREEN_WIDTH/2, self.player.y - self.SCREEN_HEIGHT/2

    def update_title_scene(self):
        if pyxel.btnp(pyxel.KEY_RETURN):
            # self.initWorld()
            self.scene = SCENE_PLAY

    def update_play_scene(self):
        if self.gameStateQuery:
            self.gameStateQuery(self)
        if self.networked and self.headless and not self.client:
            if self.pyxel.frame_count % 240 == 0: self.spawnInstance(Enemy)
            if self.pyxel.frame_count % 240 == 0: self.spawnInstance(Ammo)
            if self.pyxel.frame_count % 240 == 0: self.spawnInstance(Health)
            if self.pyxel.frame_count % 240 == 0: self.spawnInstance(Brick)
            if self.pyxel.frame_count % 240 == 0: self.spawnInstance(Bear)
            if self.pyxel.frame_count % 240 == 0: self.spawnInstance(Barrel)
        self.collisionDetection()
        update_list(self.persistentGameObjects)
        if self.networked:
            update_list(self.gameObjects)
        else:
            update_list([x for x in self.gameObjects if x.nearPlayer()])
        cleanup_list(self.persistentGameObjects)
        cleanup_list(self.gameObjects)
        if self.networked:
            self.scene = SCENE_PLAY

    def update_gameover_scene(self):
        update_list(self.gameObjects)
        cleanup_list(self.gameObjects)

        if self.pyxel.btnp(self.pyxel.KEY_RETURN):
            self.scene = SCENE_PLAY
            self.player.x = self.pyxel.width / 2
            self.player.y = self.pyxel.height / 2
            self.score = 0
            self.gameObjects.clear()
            self.gameObjects.append(self.player)

    def draw(self):
        relx, rely = self.getRelativeXY()
        self.pyxel.cls(0)
        self.pyxel.camera(self.player.x-self.SCREEN_WIDTH/2, self.player.y - self.SCREEN_HEIGHT/2)
        self.background.draw((self.player.x-self.SCREEN_WIDTH/2)/BASE_BLOCK, (self.player.y - self.SCREEN_HEIGHT/2)/BASE_BLOCK)
        self.sceneDrawDict[self.scene]()
        self.pyxel.text(relx+39, rely+4, f"Health: {self.player.health}", 7)
        self.pyxel.text(relx+39, rely+16, f"Hunger: {self.player.hunger}", 7)
        self.pyxel.text(relx + 39, rely+24, f"Ammo: {self.player.ammo}", 7)
        # todo: why the heck is player.x and y a float?
        self.pyxel.text(relx + 39, rely + 32, f"Coord: {int(self.player.x)}, {int(self.player.y)}", 7)
        y = 32 + 8
        inv_dict = self.player.inventory.dict()
        count = 1
        for each in inv_dict:
            self.pyxel.text(relx+39, rely+y, f"[{count}] {each.__name__}(s): {inv_dict[each]}", 7)
            y += 8
            count += 1
            # pyxel.text(relx + 39, rely+36, f"Bones: {self.player.bones}", 7)
            # pyxel.text(relx + 39, rely+42, f"bricks: {self.player.bricks}", 7)

    def draw_title_scene(self):
        self.pyxel.text(35, 66, "Rust2Dust", self.pyxel.frame_count % 16)

    def draw_play_scene(self):
        draw_list([x for x in self.gameObjects if x.nearPlayer()])
        draw_list(self.persistentGameObjects)
        draw_list(self.uiObjects)

    def draw_gameover_scene(self):
        draw_list(self.gameObjects)
        draw_list(self.persistentGameObjects)
        pyxel.text(43, 66, "GAME OVER", 8)


if __name__ == "__main__":
    App(headless=True)
    print('after')
