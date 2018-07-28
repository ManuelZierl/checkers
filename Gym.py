import sys
from random import randint

from Game import Game
from KI_Player import KI_Player
from Random_Player import Random_Player


class Gym():
    def __init__(self):
        self.players = []

    def add_players(self, type, amount=1):
        for i in range(amount):
            if type == "KI":
                self.players.append(KI_Player(12, 0))
            if type == "RA":
                self.players.append(Random_Player(12, 0))

    def last_man_standing(self, amount_games=100):
        winners = []
        while len(winners) != 1:
            print("TO_GO", len(self.players))
            while len(self.players) > 1:
                player_1 = self.players.pop(randint(0, len(self.players) - 1))
                player_2 = self.players.pop(randint(0, len(self.players) - 1))
                winners.append(self.play_games(player_1, player_2, amount_games))

            self.players = winners
        return winners[0]

    def play_games(self, player_1, player_2, amount, console=True, train=True, output="winner"):
        if console is True:
            print("INIT NEW COMPETITION")
            print("")
        out = []

        for i in range(amount):
            if console is True:
                progress = int((i / amount) * 15)
                sys.stdout.write("\r" + "|" + "=" * progress + ">" + "_" * (15 - progress) + "|" + str(
                    (out.count(0), out.count(1), out.count(-1))))

            game = Game(player_1=player_1, player_2=player_2)
            out.append(game.play(train=train))

        if console is True:
            print("")
            print("RESULT")
            print((out.count(0), out.count(1), out.count(-1)))

        winner = player_1
        if out.count(1) > out.count(0):
            winner = player_2

        if output == "winner":
            return winner

        if output == "result":
            return out.count(0), out.count(1), out.count(-1)


gym = Gym()
gym.add_players("KI", 2)
gym.last_man_standing(10).save("winner")
