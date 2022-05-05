import math
import sys
import os
import random

import pyxel

from constants import *


class FakePyxel:
    KEY_A = 0
    KEY_W = 0
    KEY_S = 0
    KEY_D = 0
    KEY_RETURN = 0
    MOUSE_BUTTON_LEFT = 0
    MOUSE_BUTTON_RIGHT = 0
    width, height = (100, 100)
    mouse_x, mouse_y = (50 ,50)

    def __init__(self):
        self.frameCount = 0

    def rndi(self, a, b):
        return random.randint(a, b)

    def blt(self, *args, **kwargs):
        pass

    def play(self, *args, **kwargs):
        pass

    def get_frame_count(self):
        self.frameCount += 1
        return self.frameCount

    def set_frame_count(self, n):
        self.frameCount = n

    def btn(self, *args, **kwargs):
        return random.choice([True, False])

    def btnp(self, *args, **kwargs):
        return random.choice([True, False])

    def camera(self, *args, **kwargs):
        pass
    def sgn(self, *args, **kwargs):
        return random.choice([-1, 0, 1])

    def run(self, update, draw):
        for _ in range(10000):
            update()
    frame_count = property(get_frame_count, set_frame_count)


if HEADLESS:
    pyxel = FakePyxel()

def update_list(list):
    for elem in list:
        elem.update()


def draw_list(list):
    for elem in list:
        elem.draw()


def cleanup_list(list):
    i = 0
    while i < len(list):
        elem = list[i]
        if not elem.is_alive:
            list.pop(i)
        else:
            i += 1


def distance(a, b):
    return math.sqrt(abs(a.x+(a.w/2) - b.x+(b.w/2))**2 + abs(a.y+(a.h/2) - b.y+(b.h/2))**2)


def stepToward(destObj, curObj, speed):
    deltax = pyxel.sgn(destObj.x - curObj.x)*speed
    deltay = pyxel.sgn(destObj.y - curObj.y)*speed
    # if abs(deltax) > abs(deltay):
    #     deltax = deltax
    #     deltay = 0
    # else:
    #     deltay = deltay
    #     deltax = 0
    return deltax+curObj.x, deltay+curObj.y, stepFunction(deltax)*-1, stepFunction(deltay) * -1


def stepFunction(x):  # todo: remove and refactor uses to use the pyxel sgn(x) func
    if x > 0:
        return 1
    else:
        return -1


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def collision(a, b):
    return a.x + a.w > b.x and b.x + b.w > a.x and a.y + a.h > b.y and b.y + b.h > a.y


def getRandomSpawnCoords(T):
    return pyxel.rndi(0, WORLD_WIDTH - T.w), pyxel.rndi(0, WORLD_HEIGHT - T.h)
