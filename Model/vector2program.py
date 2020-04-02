# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/4/1 12:20
# @name:vector2program
# @author:TDYe
import json
import re


def load_vocabulary(path):
	with open(path) as f:
		data = json.load(f)
	return data


def tabs(level):
	s = ''
	for i in range(level):
		s += '\t'
	return s


def clean_c_style(code: str):
	"""
	given a code assembled from the vector and convert it to formative C style  text
	:param code: code in a mess, might containing comment lines
	:return: formative C style text
	"""
	code = re.sub(r'^[\s\n]*', '', code)
	code += ' '     # avoid string index out of range
	# code = re.sub(r'[\s\n]*$', '', code)
	code = re.sub(r'[\n\r]+', '\n', code)   # windows -> \n, Mac OS -> \r
	level = 0
	out = tabs(level)
	in_for = False
	in_string = False
	in_comment = False
	i = 0
	while i < len(code):
		ch = code[i]
		if in_comment:
			if in_comment == '//' and ch == '\n':
				in_comment = False
			elif in_comment == '/*' and '*/' == code[i:i+2]:
				in_comment = False
				ch = '*/\n'
				i += 1
			if not in_comment:
				i += 1
				while bool(re.match(r'\s', code[i])):
					i += 1
					if i >= len(code):
						break
				i -= 1
				ch += tabs(level)
			out += ch
		elif in_string:
			if in_string == ch and (code[i-1] != '==' or code[i-2] == '\\'):
				in_string = False
			out += ch
		elif in_for and ch == '(':
			in_for += 1
			out += ch
		elif in_for and ch == ')':
			in_for -= 1
			out += ch
		elif code[i: i+4] == 'else':
			out = re.sub(r'\s*$', '', out) + ' e'
		elif bool(re.match(r'^for\s*\(', code[i:])):
			in_for = 1
			out += 'for ('
			i += 1
			while '(' != code[i]:
				i += 1
		elif code[i: i+2] == '//':
			in_comment = '//'
			out += '//'
			i += 1
		elif code[i: i+2] == '/*':
			in_comment = '/*'
			out += '\n' + tabs(level) + '/*'
			i += 1
		elif ch == '"' or ch == "'":
			if in_string and in_string == ch:
				in_string = False
			else:
				in_string = ch
			out += ch
		elif ch == '{':
			level += 1
			out = re.sub(r'\s*$', '', out) + ' {\n' + tabs(level)
			i += 1
			while bool(re.match(r'\s', code[i])):
				i += 1
				if i >= len(code):
					break
			i -= 1
		elif ch == '}':
			out = re.sub(r'\s*$', '', out)
			level -= 1
			out += '\n' + tabs(level) + '}\n' + tabs(level)
			i += 1
			while bool(re.match(r'\s', code[i])):
				i += 1
				if i >= len(code):
					break
			i -= 1
		elif ch == ';' and not in_for:
			out += ';\n' + tabs(level)
			i += 1
			while bool(re.match(r'\s', code[i])):
				i += 1
				if i >= len(code):
					break
			i -= 1
		elif ch == '\n':
			out += '\n' + tabs(level)
		else:
			out += ch
		i += 1
	out = re.sub(r'[\s\n]*$', '', out)
	return out


def vector2program(vector: [[]]):
	program = ''
	problem = ''
	for item in vector:
		program += item[0] + " "
	i = 0
	while i < len(vector):
		if vector[i][3] == 'B':
			problem += '__' + ' '
		elif vector[i][3] == 'I' and i-1 > 0 and vector[i-1][3] in {'B', 'I'}:
			problem += '__' + ' '
		else:
			problem += vector[i][0] + ' '
		i += 1
	program = clean_c_style(program)
	problem = clean_c_style(problem)
	return program, problem


if __name__ == '__main__':
	index = 0
	vectors = load_vocabulary('./dataset/testing.json')
	for vector_ in vectors:
		program_, problem_ = vector2program(vector_)
		with open('./source/testing/program/program_' + str(index), mode='w') as f:
			f.write(program_)
		with open('./source/testing/problem/problem_' + str(index), mode='w') as f:
			f.write(problem_)
		index += 1
