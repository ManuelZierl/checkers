import sys
from copy import deepcopy

from Human_Player import Human_Player
from KI_Player import KI_Player
from Random_Player import Random_Player

import numpy as np


FREE, BLACK, WHITE = -1, 0, 1
D_BLACK, D_WHITE = 2, 3
X = 4

D_DIR = (-1, -1), (-1, +1), (+1, +1), (+1, -1)
GUI = ["●", "○", "♥", "♡", " "]

DRAW_AFTER_ROUNDS = 200

ALPHABET = "ABCDEFGH"

class Tree:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def deep_print(self, d=0):
        if self == None:
            return
        print("   " * d, self.value)
        for child in self.children:
            child.deep_print(d + 1)

    def paths(self):
        if not self.children:
            return [[self.value]]
        paths = []
        for child in self.children:
            for path in child.paths():
                paths.append([self.value] + path)
        return paths

def isBlack(x):
    if x == 0 or x == 2:
        return True
    return False

def isWhite(x):
    if x == 1 or x == 3:
        return True
    return False

def tween(x_1, y_1, x_2, y_2):
    v = [x_2 - x_1, y_2 - y_1]
    if v[0] > 0:
        v[0] = 1
    else:
        v[0] = -1
    if v[1] > 0:
        v[1] = 1
    else:
        v[1] = -1

    tween = []
    start = [x_1, y_1]

    while start[0] != x_2 or start[1] != y_2:
        start[0] += v[0]
        start[1] += v[1]
        tween.append((start[0], start[1]))

    tween = tween[0: len(tween) - 1]
    return tween
    pass

def longest(x):
    if isinstance(x, list):
        yield len(x)
        for y in x:
            yield from longest(y)

class Game:
    def __init__(self, player_1=KI_Player(12, 0), player_2=Random_Player(12, 1)):

        self.turn = BLACK
        self.player_1 = player_1
        self.player_2 = player_2
        self.players = [player_1, player_2]
        self.round = 0

        self.history_board = [] # todo
        self.history_reward_WHITE = [] # todo
        self.history_reward_BLACK = [] # todo

        # reinforcement statics
        self.REMEMBER_FACTOR = 0.99
        self.reward_CAPTURE = 0.1

        self.board = [[X, BLACK, X, BLACK, X, BLACK, X, BLACK],
                      [BLACK, X, BLACK, X, BLACK, X, BLACK, X],
                      [X, BLACK, X, BLACK, X, BLACK, X, BLACK],
                      [FREE, X, FREE, X, FREE, X, FREE, X],
                      [X, FREE, X, FREE, X, FREE, X, FREE],
                      [WHITE, X, WHITE, X, WHITE, X, WHITE, X],
                      [X, WHITE, X, WHITE, X, WHITE, X, WHITE],
                      [WHITE, X, WHITE, X, WHITE, X, WHITE, X]]

    def show(self, show_move_pool=True):
        sys.stdout.write("  | A | B | C | D | E | F | G | H |\n")
        count = 1
        for row in self.board:
            sys.stdout.write("- + - + - + - + - + - + - + - + - +\n")
            sys.stdout.write(str(count) + " ")
            for v in row:
                sys.stdout.write("| " + GUI[v] + " ")
            sys.stdout.write("|\n")
            count += 1
        sys.stdout.write("- + - + - + - + - + - + - + - + - +\n")
        sys.stdout.write("\n")

        if show_move_pool == True:
            sys.stdout.write("Possible Moves: \n")
            move_pool = self.get_move_pool()
            count = 0
            for move in move_pool:
                sys.stdout.write(str(count) + ": ")
                for tuple in move:
                    sys.stdout.write(ALPHABET[tuple[1]] + str(tuple[0] + 1) + " => ")
                sys.stdout.write("\x08\b\b\n")
                count += 1

    def copy_board(self, board=None):
        if board == None:
            board = self.board

        return deepcopy(board)

    def get_board_reduced(self, board = None):
        board_copy = self.copy_board()
        if not board is None:
            board_copy = board

        for r in range(len(board_copy)):
            board_copy[r] = list(filter(lambda a: a != X, board_copy[r]))

        return board_copy

    def is_turn(self,x):
        if self.turn is BLACK:
            if x == BLACK or x == D_BLACK:
                return True
            return False
        if self.turn is WHITE:
            if x == WHITE or x == D_WHITE:
                return True
            return False
        return False

    def is_D(self, x):
        if x == D_BLACK or x == D_WHITE:
            return True
        return False


    def move(self, move, board = None, silent = False):
        if board is None:
            board = self.board

        if isinstance(move, str):
            move = self.get_move_pool()[int(move)]

        capture_normal = 0
        capture_dame = 0
        new_dame = 0

        start = move.pop(0)
        temp_color = board[start[0]][start[1]]
        board[start[0]][start[1]] = FREE
        while len(move) != 0:
            for tw in tween(start[0], start[1], move[0][0], move[0][1]):
                if not self.is_turn(board[tw[0]][tw[1]]):

                    if self.is_D(board[tw[0]][tw[1]]):
                        capture_dame += 1
                    else:
                        capture_normal += 1

                    board[tw[0]][tw[1]] = FREE
                    break

            start = move.pop(0)

        board[start[0]][start[1]] = temp_color

        if temp_color < 2 and (start[0] == 0 or start[0] == 7):
            board[start[0]][start[1]] += 2
            new_dame += 0

        if silent == False:
            self.round += 1
            self.turn = not self.turn

        return capture_normal, capture_dame, new_dame

    def get_move_pool(self):
        move_pool = []
        if self.turn == BLACK:
            for x in range(len(self.board)):
                for y in range(len(self.board[0])):
                    if self.board[x][y] == BLACK:
                        move_pool += self.get_move_tree_BLACK(x, y).paths()

                    if self.board[x][y] == D_BLACK:
                        move_pool += self.get_move_tree_D_BLACK(x,y, self.board).paths()

        if self.turn == WHITE:
            for x in range(len(self.board)):
                for y in range(len(self.board[0])):
                    if self.board[x][y] == WHITE:
                        move_pool += self.get_move_tree_WHITE(x, y).paths()

                    if self.board[x][y] == D_WHITE:
                        move_pool += self.get_move_tree_D_WHITE(x, y, self.board).paths()

        if len(move_pool) == 0:
            return []

        maxima = len(max(move_pool, key=len))

        move_pool = [item for item in move_pool if len(item) == maxima]
        if maxima > 2:
            for m in move_pool:
                del m[len(m) - 1]
                pass
        return move_pool

    def get_move_tree_BLACK(self, x, y, tree=None, d=0, prior=False):
        if tree is None:
            tree = Tree((x, y))

        if not (x + 1 > 7 or y + 1 > 7):
            if isWhite(self.board[x + 1][y + 1]):
                if x + 2 < 8 and y + 2 < 8:
                    if self.board[x + 2][y + 2] == FREE:
                        child = Tree((x + 2, y + 2))
                        tree.add_child(child)
                        self.get_move_tree_BLACK(x + 2, y + 2, child, d + 1)
                        prior = True

        if not (x + 1 > 7 or y - 1 < 0):
            if isWhite(self.board[x + 1][y - 1]):
                if x + 2 < 8 and y - 2 < 8:
                    if self.board[x + 2][y - 2] == FREE:
                        child = Tree((x + 2, y - 2))
                        tree.add_child(child)
                        self.get_move_tree_BLACK(x + 2, y - 2, child, d + 1)
                        prior = True

        if d == 0 and len(tree.children) == 0:
            if not (x + 1 > 7 or y + 1 > 7):
                if self.board[x + 1][y + 1] == FREE:
                    tree.add_child(Tree((x + 1, y + 1)))
            if not (x + 1 > 7 or y - 1 < 0):
                if self.board[x + 1][y - 1] == FREE:
                    tree.add_child(Tree((x + 1, y - 1)))

        if prior is True:
            for child in tree.children:
                child.add_child(Tree((-1, -1)))

        return tree

    def get_move_tree_WHITE(self, x, y, tree=None, d=0, prior=False):
        if tree is None:
            tree = Tree((x, y))

        if not (x - 1 < 0 or y + 1 > 7):
            if isBlack(self.board[x - 1][y + 1]):
                if x - 2 > -1 and y + 2 < 8:
                    if self.board[x - 2][y + 2] == FREE:
                        child = Tree((x - 2, y + 2))
                        tree.add_child(child)
                        self.get_move_tree_WHITE(x - 2, y + 2, child, d + 1)
                        prior = True

        if not (x - 1 < 0 or y - 1 < 0):
            if isBlack(self.board[x - 1][y - 1]):
                if x - 2 > -1 and y - 2 < 8:
                    if self.board[x - 2][y - 2] == FREE:
                        child = Tree((x - 2, y - 2))
                        tree.add_child(child)
                        self.get_move_tree_WHITE(x - 2, y - 2, child, d + 1)
                        prior = True

        if d == 0 and len(tree.children) == 0:
            if not (x - 1 < 0 or y + 1 > 7):
                if self.board[x - 1][y + 1] == FREE:
                    tree.add_child(Tree((x - 1, y + 1)))
            if not (x - 1 < 0 or y - 1 < 0):
                if self.board[x - 1][y - 1] == FREE:
                    tree.add_child(Tree((x - 1, y - 1)))

        if prior is True:
            for child in tree.children:
                child.add_child(Tree((-1, -1)))

        return tree

    def get_move_tree_D_BLACK(self, x, y, board, tree=None, d=0, prior=False):
        if tree is None:
            tree = Tree((x, y))
        if not (x + 1 > 7 or y + 1 > 7):
            if isWhite(board[x + 1][y + 1]):
                if x + 2 < 8 and y + 2 < 8:
                    if board[x + 2][y + 2] == FREE:
                        child = Tree((x + 2, y + 2))
                        tree.add_child(child)
                        board_copy = self.copy_board(board)
                        board_copy[x + 1][y + 1] = FREE
                        self.get_move_tree_D_BLACK(x + 2, y + 2,board_copy, child, d + 1)
                        prior = True

        if not (x + 1 > 7 or y - 1 < 0):
            if isWhite(board[x + 1][y - 1]):
                if x + 2 < 8 and y - 2 < 8:
                    if board[x + 2][y - 2] == FREE:
                        child = Tree((x + 2, y - 2))
                        tree.add_child(child)
                        board_copy = self.copy_board(board)
                        board_copy[x + 1][y - 1] = FREE
                        self.get_move_tree_D_BLACK(x + 2, y - 2,board_copy, child, d + 1)
                        prior = True

        if not (x - 1 < 0 or y + 1 > 7):
            if isWhite(board[x - 1][y + 1]):
                if x - 2 > -1 and y + 2 < 8:
                    if board[x - 2][y + 2] == FREE:
                        child = Tree((x - 2, y + 2))
                        tree.add_child(child)
                        board_copy = self.copy_board(board)
                        board_copy[x - 1][y + 1] = FREE
                        self.get_move_tree_D_BLACK(x - 2, y + 2,board_copy, child, d + 1)
                        prior = True

        if not (x - 1 < 0 or y - 1 < 0):
            if isWhite(board[x - 1][y - 1]):
                if x - 2 > -1 and y - 2 < 8:
                    if board[x - 2][y - 2] == FREE:
                        child = Tree((x - 2, y - 2))
                        tree.add_child(child)
                        board_copy = self.copy_board(board)
                        board_copy[x - 1][y - 1] = FREE
                        self.get_move_tree_D_BLACK(x - 2, y - 2, board_copy, child, d + 1)
                        prior = True

        if d == 0 and len(tree.children) == 0:
            if not (x + 1 > 7 or y + 1 > 7):
                if self.board[x + 1][y + 1] == FREE:
                    tree.add_child(Tree((x + 1, y + 1)))
            if not (x + 1 > 7 or y - 1 < 0):
                if self.board[x + 1][y - 1] == FREE:
                    tree.add_child(Tree((x + 1, y - 1)))
            if not (x - 1 < 0 or y + 1 > 7):
                if self.board[x - 1][y + 1] == FREE:
                    tree.add_child(Tree((x - 1, y + 1)))
            if not (x - 1 < 0 or y - 1 < 0):
                if self.board[x - 1][y - 1] == FREE:
                    tree.add_child(Tree((x - 1, y - 1)))

        if prior is True:
            for child in tree.children:
                child.add_child(Tree((-1, -1)))

        return tree

    def get_move_tree_D_WHITE(self, x, y, board, tree=None, d=0, prior=False):

        if tree is None:
            tree = Tree((x, y))
        if not (x + 1 > 7 or y + 1 > 7):
            if isBlack(board[x + 1][y + 1]):
                if x + 2 < 8 and y + 2 < 8:
                    if board[x + 2][y + 2] == FREE:
                        child = Tree((x + 2, y + 2))
                        tree.add_child(child)
                        board_copy = self.copy_board(board)
                        board_copy[x + 1][y + 1] = FREE
                        self.get_move_tree_D_WHITE(x + 2, y + 2,board_copy, child, d + 1)
                        prior = True

        if not (x + 1 > 7 or y - 1 < 0):
            if isBlack(board[x + 1][y - 1]):
                if x + 2 < 8 and y - 2 < 8:
                    if board[x + 2][y - 2] == FREE:
                        child = Tree((x + 2, y - 2))
                        tree.add_child(child)
                        board_copy = self.copy_board(board)
                        board_copy[x + 1][y - 1] = FREE
                        self.get_move_tree_D_WHITE(x + 2, y - 2,board_copy, child, d + 1)
                        prior = True

        if not (x - 1 < 0 or y + 1 > 7):
            if isBlack(board[x - 1][y + 1]):
                if x - 2 > -1 and y + 2 < 8:
                    if board[x - 2][y + 2] == FREE:
                        child = Tree((x - 2, y + 2))
                        tree.add_child(child)
                        board_copy = self.copy_board(board)
                        board_copy[x - 1][y + 1] = FREE
                        self.get_move_tree_D_WHITE(x - 2, y + 2,board_copy, child, d + 1)
                        prior = True

        if not (x - 1 < 0 or y - 1 < 0):
            if isBlack(board[x - 1][y - 1]):
                if x - 2 > -1 and y - 2 < 8:
                    if board[x - 2][y - 2] == FREE:
                        child = Tree((x - 2, y - 2))
                        tree.add_child(child)
                        board_copy = self.copy_board(board)
                        board_copy[x - 1][y - 1] = FREE
                        self.get_move_tree_D_WHITE(x - 2, y - 2,board_copy, child, d + 1)
                        prior = True

        if d == 0 and len(tree.children) == 0:
            if not (x + 1 > 7 or y + 1 > 7):
                if self.board[x + 1][y + 1] == FREE:
                    tree.add_child(Tree((x + 1, y + 1)))
            if not (x + 1 > 7 or y - 1 < 0):
                if self.board[x + 1][y - 1] == FREE:
                    tree.add_child(Tree((x + 1, y - 1)))
            if not (x - 1 < 0 or y + 1 > 7):
                if self.board[x - 1][y + 1] == FREE:
                    tree.add_child(Tree((x - 1, y + 1)))
            if not (x - 1 < 0 or y - 1 < 0):
                if self.board[x - 1][y - 1] == FREE:
                    tree.add_child(Tree((x - 1, y - 1)))

        if prior is True:
            for child in tree.children:
                child.add_child(Tree((-1, -1)))

        return tree

    def is_over(self):
        if len(self.get_move_pool()) == 0:
            return True
        return False

    def play(self, show= False, train=True):
        turn = BLACK
        self.history_reward_BLACK.append(0)
        self.history_reward_WHITE.append(0)
        while self.is_over() is False:

            self.history_board.append(self.get_board_reduced())
            if self.round >= DRAW_AFTER_ROUNDS:
                return -1

            if show == True:
                self.show()

            captured = self.move(self.players[turn].move(self))
#
            # calc the score of the move
            score = 0.1*captured[0] + 0.3*captured[1] + 0.3*captured[2]
            if turn == BLACK:
                #self.history_reward_WHITE.append(-1 * score)
                self.history_reward_BLACK.append(score)

                # remember
                count = len(self.history_reward_BLACK)-2
                while count >= 0 and score != 0:

                    score = score*self.REMEMBER_FACTOR
                    self.history_reward_BLACK[count] = self.history_reward_BLACK[count] + score
                    self.history_reward_WHITE[count] = self.history_reward_WHITE[count] - score
                    count -= 1
            else:
                self.history_reward_WHITE.append(score)
                #self.history_reward_BLACK.append(-1 * score)
                # remember
                count = len(self.history_reward_WHITE) - 2
                while count >= 0 and score != 0:
                    score = score * self.REMEMBER_FACTOR
                    self.history_reward_BLACK[count] = self.history_reward_BLACK[count] - score
                    self.history_reward_WHITE[count] = self.history_reward_WHITE[count] + score

                    count -= 1
            turn = not (turn)


        # end reward
        score = 1
        if turn == BLACK:
            count = len(self.history_reward_BLACK) - 1
            while count >= 0 and score != 0:

                self.history_reward_BLACK[count] = self.history_reward_BLACK[count] + score
                self.history_reward_WHITE[count] = self.history_reward_WHITE[count] - score
                score = score * self.REMEMBER_FACTOR
                count -= 1
        else:
            count = len(self.history_reward_WHITE) - 1
            while count >= 0 and score != 0:

                self.history_reward_BLACK[count] = self.history_reward_BLACK[count] - score
                self.history_reward_WHITE[count] = self.history_reward_WHITE[count] + score
                score = score * self.REMEMBER_FACTOR
                count -= 1

        if train == True:
            self.player_1.train(self.history_board, self.history_reward_BLACK)
            self.player_2.train(self.history_board, self.history_reward_WHITE)

        return turn


pl_1 = KI_Player(12, 0)
pl_2 = Random_Player(12, 1)

eval = []
for i in range(1000):
    game = Game(player_1=pl_1, player_2=pl_2)
    eval.append(game.play())
    print(i, "--->", eval.count(0)/(eval.count(0) + eval.count(1) + 1))

print(eval.count(0))
print(eval.count(1))
print(eval.count(-1))

eval = []
for i in range(1000):
    game = Game(player_1=pl_1, player_2=pl_2)
    eval.append(game.play(train=False))
    print(i, "--->", eval.count(0)/(eval.count(0) + eval.count(1) + 1))

print(eval.count(0))
print(eval.count(1))
print(eval.count(-1))

"""
g = Game()
g.play()
ki =KI_Player(12,1)
ki.train(g.history_board, g.history_reward_WHITE)
for i in range(100):
    print(i)
    g = Game()
    g.play()
    ki.train(g.history_board, g.history_reward_BLACK)

g = Game()
g.play()
ki.train(g.history_board, g.history_reward_BLACK)


g = Game()
ki.move(g)

#pl = KI_Player(12,1)
## only example
#
#g.show()
#
#
#
#ki.train(g.history_board, g.history_reward_BLACK)
#print(g.get_board_reduced())
#print(pl.predict(g.history_board[0], g.history_board[1]))
"""
