import time
import cProfile
import pyxel
from pygase import GameState, Backend, Client as PygaseClient
from constants import *
from utils import *
import event_types
from gameObjects import *

class Client:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Survival Game")
        pyxel.load(resource_path("assets.pyxres"))
        self.scene = SCENE_TITLE
        self.score = 0
        self.cursor = Cursor(0, 0, self.player, self)
        self.persistentGameObjects = []
        self.persistentGameObjects.append(self.cursor)
        #self.uiObjects = [UI(-200, 80, self, self)]
        self.uiObjects = []
        self.background = Background(BLOCK_WIDTH, BLOCK_HEIGHT)
        # self.player = Player(*getRandomSpawnCoords(Player), self, self)
        self.player_object_id = None

        # config
        self.sceneUpdateDict = {SCENE_TITLE: self.update_title_scene,
                                SCENE_PLAY: self.update_play_scene,
                                SCENE_GAMEOVER: self.update_gameover_scene}

        self.sceneDrawDict = {SCENE_TITLE: self.draw_title_scene,
                              SCENE_PLAY: self.draw_play_scene,
                              SCENE_GAMEOVER: self.draw_gameover_scene}

        # Networking
        self.event_container = ClientEventContainer(self.create_player)
        self.event_container.connect()
        self.gameObjects = GameObjectContainer(event_container=self.event_container)
        # TODO: this is super messy and needs cleaned up - does this even pass by reference?
        self.event_container.game_objects = self.gameObjects

        # Join game
        self.event_container.dispatch(event_types.JOIN)

        pyxel.run(self.update, self.draw)

    @property
    def player(self):
        try:
            player = self.gameObjects[self.player_object_id]
        except KeyError:
            player = None
        return player

    # @player.setter
    # def player(self, p):
    #     self.gameObjects[self.player_object_id] = p

    def create_player(self, player_object_id, position):
        # Does not use append because the player is not placed on the grid
        if not self.player:
            player = Player(*position, self, self, object_id=player_object_id)
            self.player_object_id = player_object_id
            self.gameObjects[player_object_id] = player

    def update(self):
        self.background.update()
        self.sceneUpdateDict[self.scene]()

    def getRelativeXY(self):
        return self.player.x - SCREEN_WIDTH/2, self.player.y - SCREEN_HEIGHT/2

    def update_title_scene(self):
        if pyxel.btnp(pyxel.KEY_RETURN):
            # self.initWorld()
            self.scene = SCENE_PLAY

    def update_play_scene(self):
        if self.player:
            pyxel.camera(self.player.x-SCREEN_WIDTH/2, self.player.y - SCREEN_HEIGHT/2)
            # TODO: access game state and register updates
            # TODO: send key presses to server
        # if pyxel.frame_count % 240 == 0: self.spawnInstance(Enemy)
        # if pyxel.frame_count % 240 == 0: self.spawnInstance(Ammo)
        # if pyxel.frame_count % 240 == 0: self.spawnInstance(Health)
        # if pyxel.frame_count % 240 == 0: self.spawnInstance(Brick)
        # if pyxel.frame_count % 240 == 0: self.spawnInstance(Bear)
        # if pyxel.frame_count % 240 == 0: self.spawnInstance(Barrel)
        # self.collisionDetection()
        # update_list(self.persistentGameObjects)
        # update_list(self.gameObjects)
        # cleanup_list(self.persistentGameObjects)
        # cleanup_list(self.gameObjects)

    def update_gameover_scene(self):
        # TODO: respawn player somewhere on grid
        self.player.x, self.player.y = getRandomSpawnCoords()
        pass
        # update_list(self.gameObjects)
        # cleanup_list(self.gameObjects)

        # if pyxel.btnp(pyxel.KEY_RETURN):
        #     self.scene = SCENE_PLAY
        #     self.player.x = pyxel.width / 2
        #     self.player.y = pyxel.height / 2
        #     self.score = 0
        #     self.gameObjects.clear()
        #     self.gameObjects.append(self.player)

    def draw(self):
        relx, rely = self.getRelativeXY()
        pyxel.cls(0)
        self.background.draw()
        self.sceneDrawDict[self.scene]()
        pyxel.text(relx+39, rely+4, f"Health: {self.player.health}", 7)
        pyxel.text(relx+39, rely+16, f"Hunger: {self.player.hunger}", 7)
        pyxel.text(relx + 39, rely+24, f"Ammo: {self.player.ammo}", 7)
        y = 24 + 8
        inv_dict = self.player.inventory.dict()
        count = 1
        for each in inv_dict:
            pyxel.text(relx+39, rely+y, f"[{count}] {each.__name__}(s): {inv_dict[each]}", 7)
            y += 8
            count += 1
            # pyxel.text(relx + 39, rely+36, f"Bones: {self.player.bones}", 7)
            # pyxel.text(relx + 39, rely+42, f"bricks: {self.player.bricks}", 7)

    def draw_title_scene(self):
        pyxel.text(35, 66, "A Survival Running Man", pyxel.frame_count % 16)

    def draw_play_scene(self):
        draw_list(self.gameObjects)
        draw_list(self.persistentGameObjects)
        draw_list(self.uiObjects)

    def draw_gameover_scene(self):
        draw_list(self.gameObjects)
        draw_list(self.persistentGameObjects)
        pyxel.text(43, 66, "GAME OVER", 8)


# TODO: rename to server?
class App:
    def __init__(self):
        self.collisionList = [(Enemy, Bullet), (Enemy, Player),
                              (Player, Ammo), (Player, Health),
                              (Enemy, Enemy), (Enemy, Brick),
                              (Player, Brick), (Player, Food),
                              (Enemy, Food), (Player, Bones),
                              (Bullet, Brick), (Bullet, Barrel),
                              (Player, Barrel), (Creature, Door),
                              (Player, StorageChest), (StorageChest, Item)]

        self.event_container = ServerEventContainer(self.time_step)
        self.event_container.listen()
        self.gameObjects = GameObjectContainer(event_container=self.event_container)

    def time_step(self, game_state, dt):
        # TODO: spawn things here
        return {}
        # new_game_state = {}
        # if not game_state.gameObjectDicts:
        #     self.initWorld()
        # if game_state.gameStartTimestamp:
        #     lastSpawnMonotonicTime = game_state.lastSpawnMonotonicTime
        #     currentMonotonicTime = int(time.monotonic())
        #     if (currentMonotonicTime - lastSpawnMonotonicTime) >= 8:
        #         # TODO: change to use getRandomGridCoords to instantiate object, maybe re-implement spawn method to add to gameObjects - also dispatch create event?
        #         self.spawnInstance(Enemy)
        #         self.spawnInstance(Ammo)
        #         self.spawnInstance(Health)
        #         self.spawnInstance(Brick)
        #         new_game_state['lastSpawnMonotonicTime'] = currentMonotonicTime
        #     self.collisionDetection()
        #     # update_list(self.persistentGameObjects)
        #     update_list(self.gameObjects)
        #     # cleanup_list(self.persistentGameObjects)
        #     cleanup_list(self.gameObjects)
        # return new_game_state

    # TODO: check distance from all players
    # def spawnInstance(self, T):
    #     tmp = T(pyxel.rndi(0, WORLD_WIDTH - T.w), pyxel.rndi(0, WORLD_HEIGHT - T.h), self, self)
    #     if distance(self.player, tmp) > BASE_BLOCK * 4:
    #         self.gameObjects.append(tmp)

    # def initWorld(self):
    #     # TODO: change to return objects
    #     for _ in range(15):
    #         self.spawnInstance(Enemy)
    #
    #     for _ in range(25):
    #         self.spawnInstance(Bear)
    #
    #     for _ in range(50):
    #         self.spawnInstance(Ammo)
    #
    #     for _ in range(20):
    #         self.spawnInstance(Brick)
    #
    #     for _ in range(25):
    #         self.spawnInstance(Barrel)

    # TODO: maybe move this to GameObjectContainer
    def collisionDetection(self):
        for each in self.collisionList:
            aList = [x for x in self.gameObjects.values() if isinstance(x, each[0])]
            for a in aList:
                bList = [x for x in self.gameObjects.getNearbyElements(a) if isinstance(x, each[1])]
                for b in bList:
                    if a != b and collision(a, b):
                        b.collide(a)
                        a.collide(b)

App()
print('after')
