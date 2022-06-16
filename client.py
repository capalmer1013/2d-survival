import time
import threading
import random

import main
import gameObjects

import socketio

sio = socketio.Client()

# move    <->
# spawn   <->


pingTime = 0

@sio.event
def ping(data):
    global pingTime
    tmp = pingTime
    print("ping (ms)", (time.time() - tmp) * 1000)
    if tmp:
        pingTime = 0

@sio.event
def move(data):
    print(data)

@sio.event
def connect():
    print('connection established')

@sio.event
def disconnect():
    print('disconnected from server')


# ===========================

def openConnection():
    sio.connect('http://localhost:5000', wait_timeout = 10)
    sio.wait()

def sendMove():
    while True:
        sio.emit("move", {'x': random.randint(0, 100), 'y': random.randint(0, 100)})
        time.sleep(5)

def sendPing():
    global pingTime
    pingTime = time.time()
    sio.emit("ping", time.time())
    time.sleep(5)
    if pingTime:
        print("ping timeout")
        pingTime = 0


openConnection_t = threading.Thread(target=openConnection)
move_t = threading.Thread(target=sendMove)

openConnection_t.start()
time.sleep(10)
move_t.start()
sendPing()