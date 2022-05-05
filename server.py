"""Example game backend"""

# import random
# import time
# from pygase import GameState, Backend
# from utils import *
# from gameObjects import *

# def spawnInstance(T):
#     return T(pyxel.rndi(0, WORLD_WIDTH - T.w), pyxel.rndi(0, WORLD_HEIGHT - T.h), None, self)
#     # TODO: re-implement this by looking for all players
#     # if distance(self.player, tmp) > BASE_BLOCK * 4:
#     #     self.gameObjects.append(tmp)


### SETUP ###

"""
game state will be centralized here
server will spawn objects automatically
when player joins, game state will be retrieved and stored locally on client
server will handle `update_list` call, which will update all game objects
at end of `time_step` call, game objects will be serialized via json.dumps(obj.__dict__) and game_state.gameObjects will be updated
updates are sent out to clients
while client_update_loop:
    client will access new game state and compare it to local game state copy
    client will check if new gameObjects state is different from local gameObjects state
        if so, client will loop through all serializedGameObjects from new state with key = object_id
            # TODO: we don't need json, just use a dict cause pygase uses msgpack under the hood
            gameObjectDict = convertJsonToDict(serializedGameObject) (use walrus syntax in if statement)
            if object_id not in localGameState.serializedGameObjects:
                create new object from serializedGameObject and store in GameObjectsContainer with object ID
                # TODO: need to figure out how to pass object type. Maybe {object_id: (objectType, data)}
            elif gameObjectDict != client.gameObjects[object_id].__dict__:
                localGameState.gameObjects[object_id].__dict__ = gameObjectDict

client will handle drawing based on object updates
"""

# Initialize the game state.
# initial_game_state = GameState(
#     # players={},  # dict with `player_id: player_dict` entries
#     # Needs to be a dict (not list) to delete objects from game state by key
#     serializedGameObjects={},
#     numPlayers=0,
#     gameStartTimestamp=None,
#     lastSpawnMonotonicTime=None # Should be cast to an integer i.e. seconds
# )

# # Define the game loop iteration function.
# def example_time_step(game_state, dt):
#     # Before a player joins, updating the game state is unnecessary.
#     if game_state.chaser_id is None:
#         return {}
#     # If protection mode is on, all players are safe from the chaser.
#     if game_state.protection:
#         new_countdown = game_state.countdown - dt
#         return {"countdown": new_countdown, "protection": True if new_countdown >= 0.0 else False}
#     # Check if the chaser got someone.
#     chaser = game_state.players[game_state.chaser_id]
#     for player_id, player in game_state.players.items():
#         if not player_id == game_state.chaser_id:
#             # Calculate their distance to the chaser.
#             dx = player["position"][0] - chaser["position"][0]
#             dy = player["position"][1] - chaser["position"][1]
#             distance_squared = dx * dx + dy * dy
#             # Whoever the chaser touches becomes the new chaser and the protection countdown starts.
#             if distance_squared < 15:
#                 print(f"{player['name']} has been caught")
#                 return {"chaser_id": player_id, "protection": True, "countdown": 5.0}
#     return {}

# def time_step(game_state, dt):
#     # Do not update game state if there are no players
#     # if game_state.players:
#     #     return {}
#     if not game_state.gameObjects:
#         initWorld()

#     if game_state.gameStartTime:
#         lastSpawnMonotonicTime = game_state.lastSpawnMonotonicTime
#         currentMonotonicTime = int(time.monotonic())
#         if (currentMonotonicTime - lastSpawnMonotonicTime) >= 8:
#             spawnInstance(Enemy)
#             spawnInstance(Ammo)
#             spawnInstance(Health)
#             spawnInstance(Brick)
#         self.collisionDetection()
#         # update_list(self.persistentGameObjects)
#         update_list(self.gameObjects)
#         # cleanup_list(self.persistentGameObjects)
#         cleanup_list(self.gameObjects)
#     # TODO: serialize all game objects and send that as update

# "MOVE" event handler
# def on_move(player_id, new_position, **kwargs):
#     return {"players": {player_id: {"position": new_position}}}

# "JOIN" event handler
def on_join(player, game_state, client_address, **kwargs):
    print(f"{player_name} joined.")
    game_object_id = len(game_state.gameObjects)
    new_game_state = {}
    # TODO: add player object
    # new_game_state = {
    #     'gameObjects': {game_object_id:  }
    # }
    # Notify client that the player successfully joined the game.
    backend.server.dispatch_event("PLAYER_CREATED", game_object_id, target_client=client_address, retries=1)
    if game_state.gameStartTimestamp:
        new_game_state['gameStartTimestamp'] = time.mktime(time.gmtime())
    # return {
    #     # Add a new entry to the players dict
    #     "players": {player_id: {"name": player_name, "position": (random.random() * 640, random.random() * 420)}},
    #     # If this is the first player to join, make it the chaser.
    #     "chaser_id": player_id if game_state.chaser_id is None else game_state.chaser_id,
    # }
    return new_game_state

# Create the backend.
backend = Backend(initial_game_state, time_step, event_handlers={"MOVE": on_move, "JOIN": on_join})


# Register the "JOIN" handler.
# backend.game_state_machine.register_event_handler("JOIN", on_join)

### MAIN PROCESS ###

if __name__ == "__main__":
    backend.run(hostname="localhost", port=8080)