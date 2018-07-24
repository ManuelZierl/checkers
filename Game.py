import sys

from Human_Player import Human_Player
from Random_Player import Random_Player


FREE, BLACK, WHITE = -1, 0, 1
D_BLACK, D_WHITE = 2, 3
X = 4

D_DIR = (-1, -1), (-1, +1), (+1, +1), (+1, -1)
GUI = ["●", "○", "♥", "♡", " "]

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
    def __init__(self, player_1=Random_Player(12, 1), player_2=Random_Player(12, 1)):

        self.turn = BLACK
        self.player_1 = player_1
        self.player_2 = player_2

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

    def move(self, move):
        if isinstance(move, str):
            move = self.get_move_pool()[int(move)]

        start = move.pop(0)
        temp_color = self.board[start[0]][start[1]]
        self.board[start[0]][start[1]] = FREE
        while len(move) != 0:
            for tw in tween(start[0], start[1], move[0][0], move[0][1]):
                if self.board[tw[0]][tw[1]] == (not self.turn):
                    self.board[tw[0]][tw[1]] = FREE
                    break

            start = move.pop(0)

        self.board[start[0]][start[1]] = temp_color

        if temp_color < 2 and (start[0] == 0 or start[0] == 7):
            self.board[start[0]][start[1]] += 2

        self.turn = not self.turn

    def get_move_pool(self):
        move_pool = []
        if self.turn == BLACK:
            for x in range(len(self.board)):
                for y in range(len(self.board[0])):
                    if self.board[x][y] == BLACK:
                        move_pool += self.get_move_tree_BLACK(x, y).paths()

                    if self.board[x][y] == D_BLACK:
                        # todo
                        pass

        if self.turn == WHITE:
            for x in range(len(self.board)):
                for y in range(len(self.board[0])):
                    if self.board[x][y] == WHITE:
                        move_pool += self.get_move_tree_WHITE(x, y).paths()

                    if self.board[x][y] == D_WHITE:
                        # todo
                        pass

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

    def get_move_pool_D_BLACK(self, x, y, tree, d=0, prior=False):
        # todo
        pass

    def get_move_pool_D_WHITE(self, x, y):
        # todo
        pass

    def is_over(self):
        # todo: check if game ist over
        return False

    def play(self):
        while self.is_over() is False:
            # todo: this method is incomplete

            if self.turn == BLACK:
                self.move(self.player_1.move(self))
            if self.turn == WHITE:
                self.move(self.player_2.move(self))


        pass


g = Game()
g.play()
