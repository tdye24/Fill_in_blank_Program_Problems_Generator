# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/3/15 23:12
# @name:program2ids
# @author:TDYe
import json
import re
numeric_constant_pattern = re.compile(r'^(([1-9]\d*)|0)(\.\d*)?$')
keyword2id = {
	'atoi': 72,
	'break': 73,
	'case': 74,
	'char': 75,
	'const': 76,
	'continue': 77,
	'cos': 78,
	'do': 79,
	'double': 80,
	'else': 81,
	'exit': 82,
	'fabs': 83,
	'fgets': 84,
	'float': 85,
	'for': 86,
	'free': 87,
	'goto': 88,
	'if': 89,
	'int': 90,
	'long': 91,
	'main': 92,
	'malloc': 93,
	'memset': 94,
	'pow': 95,
	'printf': 96,
	'putchar': 97,
	'puts': 98,
	'register': 99,
	'return': 100,
	'scanf': 101,
	'short': 102,
	'sin': 103,
	'sizeof': 104,
	'sqrt': 105,
	'strcat': 106,
	'strcmp': 107,
	'strcpy': 108,
	'strlen': 109,
	'strncat': 110,
	'strncmp': 111,
	'strncpy': 112,
	'strstr': 113,
	'struct': 114,
	'switch': 115,
	'tolower': 116,
	'toupper': 117,
	'typedef': 118,
	'unsigned': 119,
	'void': 120,
	'while': 121,
}
operator2id = {
	'!': 36,
	'!=': 37,
	'%': 38,
	'%=': 39,
	'&': 40,
	'&&': 41,
	'*': 44,
	'*=': 45,
	'+': 46,
	'++': 47,
	'+=': 48,
	',': 49,
	'-': 50,
	'--': 51,
	'-=': 52,
	'->': 53,
	'.': 54,
	'/': 55,
	'/=': 56,
	':': 57,
	';': 58,
	'<': 59,
	'<<': 60,
	'<<=': 61,
	'<=': 62,
	'=': 63,
	'==': 64,
	'>': 65,
	'>=': 66,
	'>>': 67,
	'>>=': 68,
	'?': 69,
	'||': 123,
	'~': 125,
}
delimiter2id = {
	'(': 42,
	')': 43,
	'[': 70,
	']': 71,
	'{': 122,
	'}': 124,
}


def is_keyword(word):
	if word in keyword2id.keys():
		return True
	return False


def is_delimiter(word):
	if word in delimiter2id:
		return True
	return False


def is_operator(word):
	if word in operator2id.keys():
		return True
	return False


def is_numeric_constant(word):
	if re.match(numeric_constant_pattern, word):
		return True
	return False


def remove_comment(path):
	"""
	remove comments in code corresponding to the given path
	:param path: the path of the code in the dir
	:return: comments_removed code
	"""
	state = 0
	pre = ''
	content = ""
	try:
		f = open(file=path, mode='r', encoding='utf-8')
		for line in f.readlines():
			for ch in line:
				if state == 0:
					if ch == '/':
						state = 1
						pre = ch
					else:
						content = "%s%s" % (content, ch)
				elif state == 1:
					if ch == '*':
						state = 2
					elif ch == '/':
						state = 5
					else:
						state = 0
						content = "%s%s%s" % (content, pre, ch)
				elif state == 2:
					if ch == '*':
						state = 3
				elif state == 3:
					if ch == '/':
						state = 4
					elif ch == '*':
						state = 3
					else:
						state = 2
				elif state == 4:
					if ch == '/':
						state = 1
					elif ch == '\n':
						content = "%s%s" % (content, '\n')
						state = 0
					else:
						state = 0
				elif state == 5:
					if ch == '\n':
						state = 0
						content = "%s%s" % (content, ch)
	except IOError:
		print("reading file failed")
	finally:
		f.close()
	return content


def load_vocabulary(path):
	with open(path) as f:
		data = json.load(f)
	return data


def program2ids(path):
	content = remove_comment(path)

	content = content.replace('+', " + ")
	content = content.replace('-', " - ")
	content = content.replace('*', " * ")
	content = content.replace('/', " / ")
	content = content.replace('=', " = ")
	content = content.replace('!', " ! ")
	content = content.replace('%', " % ")
	content = content.replace('&', " & ")
	content = content.replace('(', " ( ")
	content = content.replace(')', " ) ")
	content = content.replace(',', " , ")
	# content = content.replace('.', " . ")
	content = content.replace(':', " : ")
	content = content.replace(';', " ; ")
	content = content.replace('<', " < ")
	content = content.replace('>', " > ")
	content = content.replace('?', " ? ")
	content = content.replace('[', " [ ")
	content = content.replace(']', " ] ")
	content = content.replace('{', " { ")
	content = content.replace('}', " } ")
	content = content.replace('"', " \" ")
	content = content.replace('\'', " ' ")
	content = content.replace('|', " | ")
	content = content.replace('~', " ~ ")

	content_lst = content.split()
	state = 0
	word = ''
	for i in range(len(content_lst)):
		print(content_lst[i])
	for i in range(len(content_lst)):
		item = content_lst[i]

		if i < len(content_lst)-1:
			next_item = content_lst[i+1]
		else:
			next_item = None
		if state == 0:  # start
			if item == '\'':
				state = 1
				word += item
			elif item == '\"':
				state = 3
				word += item
			elif is_keyword(item):
				print(item, '->keyword')
			elif is_delimiter(item):
				print(item, '->delimiter')
			elif is_numeric_constant(item):
				print(item, '->numeric constant')
			elif item == '+':
				word += item
				if next_item not in ['+', '=']:
					state = 0
					print(word, '->+')
					word = ''
				else:
					state = 5
			elif item == '-':
				word += item
				if next_item not in ['-', '=', '>']:
					state = 0
					print(word, '->-')
					word = ''
				else:
					state = 6
			elif item == '*':
				word += item
				if next_item not in ['=']:
					state = 0
					print(word, '->*')
					word = ''
				else:
					state = 7
			elif item == '/':
				word += item
				if next_item not in ['=']:
					state = 0
					print(word, '->/')
					word = ''
				else:
					state = 8
			elif item == '=':
				word += item
				if next_item not in ['=']:
					state = 0
					print(word, '->=')
					word = ''
				else:
					state = 9
			elif item == '!':
				word += item
				if next_item not in ['=']:
					state = 0
					print(word, '->!')
					word = 0
				else:
					state = 10
			elif item == '<':
				word += item
				if next_item not in ['=', '<']:
					state = 0
					print(word, '-><')
					word = ''
				else:
					state = 11
			elif item == '>':
				word += item
				if next_item not in ['>', '=']:
					state = 0
					print(word, '->>')
					word = ''
				else:
					state = 13
			elif item == '&':
				word += item
				if next_item not in ['&']:
					state = 0
					print(word, '->&')
					word = ''
				else:
					state = 15
			elif item == '%':
				word += item
				if next_item not in ['=']:
					state = 0
					print(word, '->%')
					word = ''
				else:
					state = 16
			else:
				print(item, '->variable or function name')
		elif state == 1:    # '...
			word += item
			if item == '\'':
				state = 0
				print(word, '->char constant')
				word = ''
			elif item == '\\':
				state = 2
		elif state == 2:
			word += item
			if item != '\\':
				state = 1
		elif state == 3:
			word += item
			if item == '\"':
				state = 0
				print(word, '->string constant')
				word = ''
			elif item == '\\':
				state = 4
		elif state == 4:
			word += item
			if item != '\\':
				state = 3
		elif state == 5:
			word += item
			if item == '+':
				state = 0
				print(word, '->++')
				word = ''
			elif item == '=':
				state = 0
				print(word, '->+=')
				word = ''
		elif state == 6:
			word += item
			if item == '-':
				state = 0
				print(word, '->--')
				word = ''
			elif item == '=':
				state = 0
				print(word, '->=')
				word = ''
			elif item == '>':
				state = 0
				print(word, '->->')
				word = ''
		elif state == 7:
			word += item
			if item == '=':
				state = 0
				print(word, '->*=')
				word = ''
		elif state == 8:
			word += item
			if item == '=':
				state = 0
				print(word, '->/=')
				word = ''
		elif state == 9:
			word += item
			if item == '=':
				state = 0
				print(word, '->==')
				word = ''
		elif state == 10:
			word += item
			if item == '=':
				state = 0
				print(word, '->!=')
				word = ''
		elif state == 11:
			word += item
			if item == '=':
				state = 0
				print(word, '-><=')
				word = ''
			elif item == '<':
				if next_item not in ['=']:
					state = 0
					print(word, '-><<')
					word = ''
				else:
					state = 12
		elif state == 12:
			word += item
			if item == '=':
				state = 0
				print(word, '-><<=')
				word = ''
		elif state == 13:
			word += item
			if item == '=':
				state = 0
				print(word, '->>=')
				word = ''
			elif item == '>':
				if next_item not in ['=']:
					state = 0
					print(word, '->>>')
				else:
					state = 14
		elif state == 14:
			word += item
			if item == '=':
				state = 0
				print(word, '->>>=')
				word = ''
		elif state == 15:
			word += item
			if item == '&':
				state = 0
				print(word, '->&&')
				word = ''
		elif state == 16:
			word += item
			if item == '=':
				state = 0
				print(word, '->%=')
				word = ''


if __name__ == '__main__':
	program2ids(path="sum.cpp")
