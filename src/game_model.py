import pyxel

from gameObjects import (
    BASE_BLOCK,
    BLOCK_WIDTH,
    BLOCK_HEIGHT,
    WORLD_MULTIPLIER,
    Background,
    GameObjectContainer,
    Player,
    Cursor
)


class GameModel:
    WORLD_WIDTH = BASE_BLOCK * BLOCK_WIDTH * WORLD_MULTIPLIER
    WORLD_HEIGHT = BASE_BLOCK * BLOCK_HEIGHT * WORLD_MULTIPLIER

    def __init__(self):
        self.background = Background(BLOCK_WIDTH, BLOCK_HEIGHT, self)
        self.maxEnemies = 100
        self.numEnemies = 0
        self.numBricks = 0
        self.persistentGameObjects = []
        self.score = 0
        self.gameObjects = GameObjectContainer(self)
        self.player = Player(pyxel.width / 2, pyxel.height - 20, self, self)
        self.gameObjects.append(self.player)
        self.cursor = Cursor(0, 0, self.player, self)
        self.persistentGameObjects.append(self.cursor)
