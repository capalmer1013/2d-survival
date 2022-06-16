import math
import pickle
import time
from pygase import GameState, Backend
import main
import eventlet
import socketio

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

positions = {}
@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def my_message(sid, data):
    print('message ', data)
    sio.emit('my_message', {"server": "server response"})

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

@sio.event
def move(sid, data):
    print("move command received")
    print(sid, data)
    positions[sid] = data
    print(positions)

@sio.event
def ping(sid, data):
    print("ping received")
    sio.emit('ping', time.time())

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

