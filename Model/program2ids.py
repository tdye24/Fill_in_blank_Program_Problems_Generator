# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/3/15 23:12
# @name:program2ids
# @author:TDYe
from Model.program2vector import program2vector
from Model.predict import predict
from Model.vector2program import vector2program


def predict_to_program(path):
	path = 'sum.cpp'
	X = program2vector(path)
	X0 = predict(X)[0]
	program, problem, answer = vector2program(X0)
	print(program)
	print(problem)
	print(answer)


if __name__ == '__main__':
    predict_to_program('sum.cpp')
