from keras.engine import Input
from keras.engine import Model
from keras.layers import Conv2D, MaxPooling2D, Flatten, concatenate, Dense

from Player import Player

import numpy as np

class KI_Player(Player):

    def __init__(self, score, turn):
        super().__init__(score, turn)

        # build the network
        input_1 = Input(shape = (8, 4, 1), name='input_1')
        input_2 = Input(shape = (8, 4, 1), name='input_2')

        c1 = Conv2D(32, (3, 3), padding="same", input_shape=(8,4, 1))(input_1)
        p1 = MaxPooling2D(pool_size=(2, 2))(c1)
        f1 = Flatten()(p1)
        d1 = Dense(16, activation='sigmoid')(f1)

        c2 = Conv2D(32, (3, 3), padding="same", input_shape=(8,4, 1))(input_1)
        p2 = MaxPooling2D(pool_size=(2, 2))(c2)
        f2 = Flatten()(p2)
        d2 = Dense(16, activation='sigmoid')(f2)

        x = concatenate([d1, d2])
        d_all = Dense(128, activation='sigmoid')(x)

        out = Dense(1, activation='tanh')(d_all)

        self.model = Model(inputs=[input_1, input_2], outputs=[out])
        self.model.compile('adam', 'binary_crossentropy', metrics=['accuracy'])

    def move(self, game):
        # todo:
        return None

    def convert_to_training_batch(self, history, Y):
        # todo:
        pass


    def predict(self, board_before, board_after):
        board_before = np.array(board_before).reshape((8, 4, 1))
        board_after = np.array(board_after).reshape((8, 4, 1))

        pred = self.model.predict([np.array([board_before]), np.array( [board_after] )])
        return pred[0][0]