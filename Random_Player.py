from random import randint

from Player import Player


class Random_Player(Player):
    def move(self, game):
        move_pool = game.get_move_pool()
        return move_pool[randint(0, len(move_pool) - 1)]
