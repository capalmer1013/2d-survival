import time
import cProfile
import pyxel
from pygase import GameState, Backend
from constants import *
from utils import *
from gameObjects import *


class Client:
    def __init__(self):
        pyxel.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, title="Survival Game")
        pyxel.load(resource_path("assets.pyxres"))
        self.scene = SCENE_TITLE
        self.score = 0
        self.gameObjects = GameObjectContainer(self)
        self.persistentGameObjects = []
        self.persistentGameObjects.append(self.cursor)
        #self.uiObjects = [UI(-200, 80, self, self)]
        self.uiObjects = []
        self.background = Background(BLOCK_WIDTH, BLOCK_HEIGHT)
        # TODO: replace with self.gameObjects[player_object_id], make getter/setter for self.player
        self.player = Player(*getRandomSpawnCoords(Player), self, self)
        self.cursor = Cursor(0, 0, self.player, self)

        # config
        self.sceneUpdateDict = {SCENE_TITLE: self.update_title_scene,
                                SCENE_PLAY: self.update_play_scene,
                                SCENE_GAMEOVER: self.update_gameover_scene}

        self.sceneDrawDict = {SCENE_TITLE: self.draw_title_scene,
                              SCENE_PLAY: self.draw_play_scene,
                              SCENE_GAMEOVER: self.draw_gameover_scene}

        # TODO: dispatch join event, pass entire player object dict, while loop until player_object_id is set

        pyxel.run(self.update, self.draw)

    def update(self):
        self.background.update()
        self.sceneUpdateDict[self.scene]()

    def getRelativeXY(self):
        return self.player.x - self.SCREEN_WIDTH/2, self.player.y - self.SCREEN_HEIGHT/2

    def update_title_scene(self):
        if pyxel.btnp(pyxel.KEY_RETURN):
            # self.initWorld()
            self.scene = SCENE_PLAY

    def update_play_scene(self):
        pyxel.camera(self.player.x-self.SCREEN_WIDTH/2, self.player.y - self.SCREEN_HEIGHT/2)
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
        pyxel.text(relx+39, rely+4, f"Ammo: {self.player.ammo}", 7)
        pyxel.text(relx+39, rely+16, f"Health: {self.player.health}", 7)
        pyxel.text(relx+39, rely+28, f"Hunger: {self.player.hunger}", 7)
        pyxel.text(relx + 39, rely+36, f"Bones: {self.player.bones}", 7)
        pyxel.text(relx + 39, rely+42, f"bricks: {self.player.bricks}", 7)

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
                              (Player, Barrel), (Creature, Door)]  # todo: store game objects in 2d array with modulo of location to only do collision detection close to player
        initial_game_state = GameState(
            # players={},  # dict with `player_id: player_dict` entries
            # Needs to be a dict (not list) to delete objects from game state by key
            gameObjectDicts={},
            gameStartTimestamp=None,
            lastSpawnMonotonicTime=None # Should be cast to an integer i.e. seconds
        )
        # TODO: run pygase backend here
        self.backend = Backend(initial_game_state, self.timeStep, event_handlers={"MOVE": self.onMove, "JOIN": self.onJoin})
        self.backend.run(hostname="localhost", port=8000)

    def timeStep(self, game_state, dt):
        new_game_state = {}
        if not game_state.gameObjectDicts:
            # TODO: Store in new_game_state
            self.initWorld()
        if game_state.gameStartTimestamp:
            lastSpawnMonotonicTime = game_state.lastSpawnMonotonicTime
            currentMonotonicTime = int(time.monotonic())
            if (currentMonotonicTime - lastSpawnMonotonicTime) >= 8:
                # TODO: change to use getRandomGridCoords to instantiate object
                self.spawnInstance(Enemy)
                self.spawnInstance(Ammo)
                self.spawnInstance(Health)
                self.spawnInstance(Brick)
                new_game_state['lastSpawnMonotonicTime'] = currentMonotonicTime
            self.collisionDetection()
            # update_list(self.persistentGameObjects)
            update_list(self.gameObjects)
            # cleanup_list(self.persistentGameObjects)
            cleanup_list(self.gameObjects)
        # TODO: serialize all game objects and send that as update
        return new_game_state

    def onJoin(self, player_object_dict, game_state, client_address, **kwargs):
        print('new player joined')
        player_object_id = len(game_state.gameObjectDicts)
        new_game_state = {'gameObjectDicts': {player_object_id: { 'type': Player, 'data': player_object_dict}}}
        if not game_state.gameStartTimestamp:
            new_game_state['gameStartTimestamp'] = time.mktime(time.gmtime())
        self.backend.server.dispatch_event("PLAYER_CREATED", player_object_id, target_client=client_address, retries=1)
        return new_game_state


    def onMove(self, player_object_id, x, y, **kwargs):
        # TODO: verify that object is 1) a player 2) the player dispatching the event
        return {'gameObjectDicts': {player_object_id: {'data': {'x': x, 'y': y}}}}

    def initWorld(self):
        # TODO: change to return objects
        for _ in range(15):
            self.spawnInstance(Enemy)

        for _ in range(25):
            self.spawnInstance(Bear)

        for _ in range(50):
            self.spawnInstance(Ammo)

        for _ in range(20):
            self.spawnInstance(Brick)

        for _ in range(25):
            self.spawnInstance(Barrel)

    def collisionDetection(self):
        for each in self.collisionList:
            aList = [x for x in self.gameObjects if isinstance(x, each[0])]
            for a in aList:
                bList = [x for x in self.gameObjects.getNearbyElements(a) if isinstance(x, each[1])]
                for b in bList:
                    if a != b and collision(a, b):
                        b.collide(a)
                        a.collide(b)

    def numType(self, t):
        return len([x for x in self.gameObjects if isinstance(x, t)])

App()
print('after')
