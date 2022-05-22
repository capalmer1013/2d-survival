from pygase import Client
import time

client = Client()
client.connect_in_thread(port=8080, hostname="localhost")


while True:
    with client.access_game_state() as game_state:
        for each in game_state.__dict__:
            print(each)
            print(type(each))
            print(game_state.__dict__[each])
    time.sleep(1)