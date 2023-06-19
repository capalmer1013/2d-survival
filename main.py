from src.game_controller import GameController
from src.game_model import GameModel
from src.game_view import GameView

if __name__ == "__main__":
    # if loaded_game := load_most_recent_game():
    #     loaded_game.resume()
    # else:
    #     GameView()
    model = GameModel()
    controller = GameController(model)
    controller.init_world()
    GameView(model, controller)
