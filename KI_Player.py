from keras.engine import Input
from keras.engine import Model
from keras.layers import Conv2D, MaxPooling2D, Flatten, concatenate, Dense, Dropout

from Player import Player

import numpy as np


class KI_Player(Player):
    def __init__(self, score, turn, model=None):
        super().__init__(score, turn)

        if model is None:
            # build the network
            input_1 = Input(shape=(8, 4, 1), name='input_1')
            input_2 = Input(shape=(8, 4, 1), name='input_2')

            c1 = Conv2D(16, (3, 3), padding="same", input_shape=(8, 4, 1))(input_1)
            p1 = MaxPooling2D(pool_size=(2, 2))(c1)
            f1 = Flatten()(p1)
            d1 = Dense(8, activation='sigmoid', kernel_initializer='random_uniform')(f1)
            dr1 = Dropout(0.2)(d1)

            c2 = Conv2D(16, (3, 3), padding="same", input_shape=(8, 4, 1))(input_2)
            p2 = MaxPooling2D(pool_size=(2, 2))(c2)
            f2 = Flatten()(p2)
            d2 = Dense(8, activation='sigmoid', kernel_initializer='random_uniform')(f2)
            dr2 = Dropout(0.2)(d2)

            x = concatenate([dr1, dr2])
            d_all = Dense(16, activation='sigmoid', kernel_initializer='random_uniform')(x)
            drop_out = Dropout(0.2)(d_all)

            out = Dense(1, activation='tanh')(drop_out)

            self.model = Model(inputs=[input_1, input_2], outputs=[out])
            self.model.compile('adam', 'binary_crossentropy', metrics=['accuracy'])
        else:
            self.model = model

    def move(self, game):
        move_pool = game.get_move_pool()

        if len(move_pool) == 1:
            return move_pool[0]

        idx = 0
        best = -2
        count = 0

        for move in move_pool:

            deep_copy = game.copy_board()
            befor = game.copy_board(deep_copy)
            game.move(move, board=deep_copy, silent=True)
            game.get_board_reduced(board=befor)
            game.get_board_reduced(board=deep_copy)

            pred = self.predict(befor, deep_copy)
            if pred > best:
                idx = count
                best = pred

            count += 1
        move_pool = game.get_move_pool()
        return move_pool[idx]

    def train(self, history, Y):

        train_X_1 = []
        train_X_2 = []
        for i in range(self.turn, len(history) - 1, 2):
            train_X_1.append(history[i])
            train_X_2.append(history[i + 1])

        del Y[0]

        train_X_1 = np.array(train_X_1)
        train_X_1 = train_X_1.reshape(train_X_1.shape[0], 8, 4, 1)
        train_X_2 = np.array(train_X_2)
        train_X_2 = train_X_2.reshape(train_X_2.shape[0], 8, 4, 1)

        if len(train_X_1) != len(Y):
            del Y[len(Y) - 1]

        self.model.fit([train_X_1, train_X_2], Y, epochs=30, verbose=0)

    def predict(self, board_before, board_after):
        board_before = np.array(board_before).reshape((8, 4, 1))
        board_after = np.array(board_after).reshape((8, 4, 1))

        pred = self.model.predict([np.array([board_before]), np.array([board_after])])
        return pred[0][0]

    def save(self, name):
        self.model.save("models/" + name + ".h5")
