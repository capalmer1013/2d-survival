import uuid

import pyxel

from .sound import Sound


class BaseGameObject(dict):
    U = 16
    V = 0

    def __init__(self, x, y, parent, app):
        self.id = uuid.uuid4()
        self.x = x
        self.y = y
        self.parent = parent
        self.app = app
        self.is_alive = True
        self.moved = False
        self.gridCoord = (0, 0)
        self.sound = Sound()
        dict.__init__(self, **self.serialize())

    def serialize(self):
        return {
            "x": self.x,
            "y": self.y,
            "id": str(self.id),
            "type": type(self).__name__,
        }

    @staticmethod
    def deserialize(d, parent, app):
        # expects the dict provided by serialize
        tmp = eval(d["type"])(d["x"], d["y"], parent, app)
        tmp.id = d["id"]
        return tmp

    # todo: generalize to not just be for players
    def nearPlayer(self, game_objects, player, *args, **kwargs):
        return self in game_objects.getNearbyElements(player, *args, **kwargs)

    def collide(self, other):
        raise NotImplementedError

    def bounceBack(self, other, bounceFactor=0.5):
        self.x += int((self.x - other.x) * bounceFactor)
        self.y += int((self.y - other.y) * bounceFactor)

    def update(self):
        pass

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.U, self.V, self.w, self.h, 14)
