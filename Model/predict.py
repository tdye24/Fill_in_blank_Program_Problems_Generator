# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/3/14 11:22
# @name:predict
# @author:TDYe
import keras
import numpy as np
from keras.preprocessing.sequence import pad_sequences
from Model.model import build, token_vocab_size, label_vocab_size, id_to_label, test_labels, x_test
BASEDIR = 'D:/MyProjects/Fill_in_blank_Program_Problems_Generator/Model/'


def predict(X, themes):
	if '128' in themes:
		file = BASEDIR + 'params-if.hdf5'
	elif '129' in themes:
		file = BASEDIR + 'params-loop.hdf5'
	elif '130' in themes:
		file = BASEDIR + 'params-array.hdf5'
	else:
		file = BASEDIR + 'params-all.hdf5'
	print("Using Model %s" % file)
	keras.backend.clear_session()
	token_ids = [[info[2] for info in source] for source in X]
	x = pad_sequences(token_ids, padding='post')
	model = build(168, label_vocab_size, use_crf=True, token_emb_size=50, lstm_units=100)
	model.summary()
	model.load_weights(file)

	# Predict
	y = model.predict(x)
	y = np.argmax(y, axis=-1)
	FINAL = []
	for i in range(len(y)):
		FINAL.append(y[i][:len(X[i])])
	RES = [[id_to_label[ID] for ID in source if id_to_label[ID] != '<PAD>'] for source in FINAL]

	for i in range(len(X)):
		for j in range(len(X[i])):
			X[i][j][3] = RES[i][j]
	return X


if __name__ == '__main__':
	XX = predict(x_test)