# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/3/14 11:22
# @name:predict
# @author:TDYe
import keras
import numpy as np
from keras.preprocessing.sequence import pad_sequences
from Model.model import build, token_vocab_size, label_vocab_size, file, id_to_label, test_labels, x_test


def predict(X):
	keras.backend.clear_session()
	token_ids = [[info[2] for info in source] for source in X]
	x = pad_sequences(token_ids, padding='post')
	model = build(token_vocab_size, label_vocab_size, use_crf=True, token_emb_size=50, lstm_units=100)
	model.summary()
	model.load_weights(file)

	# Predict
	y = model.predict(x)
	y = np.argmax(y, axis=-1)
	y = [[id_to_label[ID] for ID in source if id_to_label[ID] != '<PAD>'] for source in y]

	for i in range(len(X)):
		for j in range(len(X[i])):
			X[i][j][3] = y[i][j]
	return X


if __name__ == '__main__':
	XX = predict(x_test)