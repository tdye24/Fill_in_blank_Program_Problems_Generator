# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/3/15 22:48
# @name:model
# @author:TDYe
import json
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Model
from keras.layers import *
from keras.preprocessing.sequence import pad_sequences
from keras.utils.np_utils import to_categorical
from keras.callbacks import ModelCheckpoint
from keras_contrib.layers import CRF
from keras_contrib.losses import crf_loss
from keras_contrib.metrics import crf_accuracy

BASEDIR = 'D:/MyProjects/Fill_in_blank_Program_Problems_Generator/Model/'


def load_data(path):
    """
    Load dataset including training, validation, testing dataset
    :param path: the path of the dataset
    :return:
        raw_tokens like [['int', 'a', '=', '6']]
        norm_tokens like [['int', 'var0', '=', 'numeric_constant']]
        token_ids like [[84, 15, 63, 3]]
        labels like [['B', 'I', 'I', 'O']]
        label_ids like [[1, 2, 2, 3]]
    """
    with open(path) as f:
        data = json.load(f)
    raw_tokens = [[info[0] for info in source] for source in data]
    norm_tokens = [[info[1] for info in source] for source in data]
    token_ids = [[info[2] for info in source] for source in data]
    labels = [[info[3] for info in source] for source in data]
    label_ids = [[label_to_id[label] for label in source] for source in labels]
    return raw_tokens, norm_tokens, token_ids, labels, label_ids


def build(token_vocab_size_, label_vocab_size_, use_crf=False, token_emb_size=50, lstm_units=100):
    """
    Build Model
    :param token_vocab_size_: token_to_id size
    :param label_vocab_size_: label_to_id size
    :param use_crf: whether use crf or not
    :param token_emb_size: dimensionality of the output space in Embedding layer
    :param lstm_units: Positive integer, dimensionality of the output space in LSTM layer
    :return: model
    """
    # Inputs
    token_ids = Input(shape=(None,), dtype='int32')

    # Word Embedding -> Dropout
    x = Embedding(input_dim=token_vocab_size_, output_dim=token_emb_size)(token_ids)
    x = Dropout(0.5)(x)

    # Bidirectional LSTM
    x = Bidirectional(LSTM(units=lstm_units, return_sequences=True))(x)  # return the last output

    # Conditional Random Fields (CRF)
    if use_crf:
        pred = CRF(label_vocab_size_, learn_mode='join')(x)
        loss, accuracy = crf_loss, crf_accuracy
    else:
        pred = Dense(label_vocab_size_, activation='softmax')(x)
        loss, accuracy = 'categorical_crossentropy', 'accuracy'

    model = Model(inputs=token_ids, outputs=pred)
    model.compile(optimizer='adam', loss=loss, metrics=[accuracy])
    return model


def plot_history(history, label='', y_lim=(None, None)):
    """
    Plot Training History
    :param history:
    :param label:
    :param y_lim:
    :return:
    """
    plt.figure(figsize=(10, 6), dpi=100)
    for v in history.values():
        plt.plot([None] + v, marker='.')
    plt.rcParams["font.size"] = 16
    plt.xlabel("epoch", fontsize=14)
    plt.ylabel(label, fontsize=14)
    plt.ylim(y_lim)
    plt.legend(history.keys())
    plt.xticks(np.hstack(([1], np.arange(5, max([len(v) for v in history.values()]) + 1, 5))))
    plt.tick_params(labelsize=14)
    plt.grid()
    plt.show()


def run():
    # Set Model Checkpoint
    modelCheckpoint = ModelCheckpoint(filepath=file, monitor='val_loss', verbose=1,
                                      save_best_only=True, save_weights_only=True, mode='auto')

    # Build Model
    model = build(token_vocab_size, label_vocab_size, use_crf=True, token_emb_size=50, lstm_units=100)
    model.summary()

    # Train Model
    history = model.fit(x_train, y_train, validation_data=(x_valid, y_valid),
                        callbacks=[modelCheckpoint], epochs=100, batch_size=8)

    # Plot Training History
    plot_history({'Training': history.history['crf_accuracy'], 'Validation': history.history['val_crf_accuracy']},
                 'accuracy')
    plot_history({'Training': history.history['loss'], 'Validation': history.history['val_loss']}, 'loss')


id_to_token = json.load(open(BASEDIR + 'dataset/vocabulary.json'))
token_to_id = {token: ID for ID, token in id_to_token.items()}
id_to_label = {0: '<PAD>', 1: 'B', 2: 'I', 3: 'O'}
label_to_id = {label: ID for ID, label in id_to_label.items()}
token_vocab_size, label_vocab_size = len(token_to_id), len(label_to_id)
file = BASEDIR + 'params.hdf5'    # store the model

# Load Data
train_raw_tokens, train_norm_tokens, train_token_ids, train_labels, train_label_ids = \
    load_data(BASEDIR + 'dataset/training.json')
valid_raw_tokens, valid_norm_tokens, valid_token_ids, valid_labels, valid_label_ids = \
    load_data(BASEDIR + 'dataset/validation.json')
test_raw_tokens, test_norm_tokens, test_token_ids, test_labels, test_label_ids = \
    load_data(BASEDIR + 'dataset/testing.json')

# Preprocess
x_train = pad_sequences(train_token_ids, padding='post')
x_valid = pad_sequences(valid_token_ids, padding='post')
x_test = pad_sequences(test_token_ids, padding='post')

y_train = pad_sequences(train_label_ids, padding='post')
y_train = to_categorical(y_train, num_classes=len(label_to_id))

y_valid = pad_sequences(valid_label_ids, padding='post')
y_valid = to_categorical(y_valid, num_classes=len(label_to_id))

y_test = pad_sequences(test_label_ids, padding='post')
y_test = to_categorical(y_test, num_classes=len(label_to_id))


if __name__ == '__main__':
    run()
