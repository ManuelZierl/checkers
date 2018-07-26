from Player import Player


class Human_Player(Player):

    def move(self, game):
        x = int(input())
        return game.get_move_pool()[x]

