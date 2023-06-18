from game_view import GameView
from savethread import load_most_recent_game

if __name__ == "__main__":
    if loaded_game := load_most_recent_game():
        loaded_game.resume()
    else:
        GameView()
