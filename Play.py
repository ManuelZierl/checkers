from keras.models import load_model

from Game import Game
from Human_Player import Human_Player
from KI_Player import KI_Player

player_1 = Human_Player(12, 0)
player_2 = KI_Player(12, 1, model=load_model("models/1000_20.h5"))

game = Game(player_1=player_1, player_2=player_2)
print(game.play(show=True))
player_2.train(game.history_board, game.history_reward_WHITE)
player_1.save("1000_20_besser.h5")