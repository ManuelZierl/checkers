class Player:
    def __init__(self, score, turn):
        self.score = score
        self.turn = turn
        pass

    def move(self, game):
        raise Exception("Not implemented Methode move()")

    def train(self,x,y):
        pass