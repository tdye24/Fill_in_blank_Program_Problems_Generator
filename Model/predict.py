# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/3/14 11:22
# @name:predict
# @author:TDYe
import numpy as np
from model import build, token_vocab_size, label_vocab_size, file, id_to_label, test_labels, x_test
from seqeval.metrics import classification_report


def predict(x):
	model = build(token_vocab_size, label_vocab_size, use_crf=True, token_emb_size=50, lstm_units=100)
	model.summary()
	model.load_weights(file)

	# Predict
	y = model.predict(x)
	y = np.argmax(y, axis=-1)
	y = [[id_to_label[ID] for ID in source if id_to_label[ID] != '<PAD>'] for source in y]

	# Evaluate Model
	print(classification_report(test_labels, y))
	print(y)


if __name__ == '__main__':
	predict(x_test)
