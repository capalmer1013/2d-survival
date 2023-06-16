import math
import pickle
import time
import threading
import main
import eventlet
import socketio

# game setup
game = main.App(headless=True, networked=True, client=False)
game.WORLD_HEIGHT = game.SCREEN_HEIGHT
game.WORLD_WIDTH = game.SCREEN_WIDTH
game.scene = main.SCENE_PLAY

# socketio setup
sio = socketio.Server()
app = socketio.WSGIApp(
    sio, static_files={"/": {"content_type": "text/html", "filename": "index.html"}}
)

positions = {}


@sio.event
def connect(sid, environ):
    print("connect ", sid)
    print("environ: ", environ)


@sio.event
def disconnect(sid):
    print("disconnect ", sid)


@sio.event
def move(sid, data):
    print("move command received")
    print(sid, data)
    positions[sid] = data
    print(positions)


@sio.event
def ping(sid, data):
    print("ping received")
    sio.emit("ping", data, room=sid)


@sio.event
def game_state(sid, data):
    sio.emit("game_state_update", game.gameObjects.GRID[data["x"]][data["y"]], room=sid)


# ===============================================


def gameLoop():
    loop_speed = 1 / 30
    while True:
        start_time = time.time()
        game.update()
        delta_time = time.time() - start_time
        if delta_time < loop_speed:
            time.sleep(loop_speed)


if __name__ == "__main__":
    gameLoop_t = threading.Thread(target=gameLoop)
    gameLoop_t.start()
    eventlet.wsgi.server(eventlet.listen(("", 5000)), app)
