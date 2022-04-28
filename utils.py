import math
import sys
import os

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
    return math.sqrt(abs(a.x - b.x)**2 + abs(a.y - b.y)**2)


def stepToward(destObj, curObj, speed):
    deltax = destObj.x - curObj.x
    deltay = destObj.y - curObj.y
    if abs(deltax) > abs(deltay):
        deltax = stepFunction(deltax)*speed
        deltay = 0
    else:
        deltay = stepFunction(deltay)*speed
        deltax = 0
    return deltax+curObj.x, deltay+curObj.y, stepFunction(deltax)*-1, stepFunction(deltay) * -1


def stepFunction(x):
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
