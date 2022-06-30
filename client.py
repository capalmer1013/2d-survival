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

@sio.on('*')
def catch_all(event, data):
    print("==============")
    print("event: ", event)
    print("data: ", data)

@sio.event
def ping(data):
    print("============")
    print("data: ", data)
    print("ping (ms)", (time.time()-data['time']) * 1000)

@sio.event
def game_state_update(data):
    print("==========")
    print("gamestate data:", data)
    print("gamestate len: ", len(data))

@sio.event
def move(data):
    print("move received")
    print(data)

@sio.event
def connect():
    print('connection established')

@sio.event
def connect_error(data):
    print("The connection failed!")
    print("data: ", data)

@sio.event
def disconnect():
    print('disconnected from server')


# ===========================

def openConnection():
    sio.connect('http://localhost:5000', wait_timeout = 10)
    #sio.wait()


def sendMove():
    while True:
        print("sending move")
        sio.emit("move", {'x': random.randint(0, 100), 'y': random.randint(0, 100)})
        time.sleep(5)

def queryGameState():
    sio.emit("game_state", {'x': 1, 'y': 2})

def sendPing():
    global pingTime
    print("pinging")
    pingTime = time.time()
    sio.emit("ping", {'time': time.time()})


#openConnection_t = threading.Thread(target=openConnection)
#move_t = threading.Thread(target=sendMove)
#openConnection_t.start()
loop = True
openConnection()
# while loop:
#     choice = input("q: quit, p: ping, s: sid, g: game state")
#     if choice.lower() == "p":
#         sendPing()
#     elif choice.lower() == "g":
#         queryGameState()
#     elif choice.lower() == "s":
#         print(sio.sid)
#     elif choice.lower() == "q":
#         loop = False


#move_t.start()

game = main.App()
