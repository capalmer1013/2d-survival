import random

from .constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BASE_BLOCK,
    BLOCK_WIDTH,
    BLOCK_HEIGHT,
    WORLD_MULTIPLIER,
)
from .game_objects import Point


class GameModel:
    WORLD_WIDTH = BASE_BLOCK * BLOCK_WIDTH * WORLD_MULTIPLIER
    WORLD_HEIGHT = BASE_BLOCK * BLOCK_HEIGHT * WORLD_MULTIPLIER

    def __init__(self):
        self.maxEnemies = 100
        self.numEnemies = 0
        self.numBricks = 0
        self.persistentGameObjects = []
        self.score = 0
        self.gameObjects = []
        self.gameList = []
        self.gridw, self.gridh = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.GRID = [[[] for _ in range(self.gridh)] for _ in range(self.gridw)]
        self.n = 0

    def append(self, elem):
        x, y = self.gridCoord(elem)
        elem.gridCoord = (x, y)
        self.GRID[x][y].append(elem)
        self.gameList.append(elem)

    def getNearbyElements(
            self, elem, dist=1
    ):  # todo: rename to more general ie. getCollisionCandidates maybe don't do that since this is being used for occlusion culling too
        x, y = self.gridCoord(elem)
        relx, rely = int(x - dist), int(y - dist)
        lenx, leny = len(self.GRID), len(self.GRID[x])
        # currently checks up and down adjacent. not diagonal todo: maybe add that... maybe
        nearbyElements = []
        # *2+1 is for making the box a square around the player
        for i in range(dist * 2 + 1):
            for j in range(dist * 2 + 1):
                nearbyElements.extend(self.GRID[(relx + i) % lenx][(rely + j) % leny])

        return nearbyElements

    def gridCoord(self, elem):
        return int(elem.x / self.gridw), int(elem.y / self.gridh)

    def updateObject(self, elem):
        x, y = self.gridCoord(elem)
        if elem not in self.GRID[x][y]:
            self.GRID[x][y].append(elem)
            oldx, oldy = elem.gridCoord
            self.GRID[oldx][oldy].remove(elem)
            elem.gridCoord = (x, y)

    def pop(self, i=None):
        x, y = self.gameList[i].gridCoord
        element_id_to_remove = self.gameList[i].id
        try:
            self.GRID[x][y].remove(
                next(x for x in self.GRID[x][y] if x.id == element_id_to_remove)
            )
            return self.gameList.pop(i)
        except StopIteration:
            return None

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

    def __contains__(self, item):
        return item.id in [x.id for x in self.gameList]

    def clear(self):
        self.gameList.clear()

    def remove(self, elem):
        x, y = self.gridCoord(elem)
        self.gameList.remove(elem)
        self.GRID[x][y].remove(elem)

    def get_closest_creature(self, x, y):
        dist = 1
        elem = Point(x, y, self, self)
        x, y = self.gridCoord(elem)
        relx, rely = int(x - dist), int(y - dist)
        lenx, leny = len(self.GRID), len(self.GRID[x])
        nearbyElements = []
        for i in range(dist * 2 + 1):
            for j in range(dist * 2 + 1):
                nearbyElements.extend(self.GRID[(relx + i) % lenx][(rely + j) % leny])

        return random.choice(nearbyElements)
