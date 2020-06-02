# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/3/30 11:53
# @name:program2vector
# @author:TDYe
keyword2id = {
	'break': 72,
	'case': 73,
	'char': 74,
	'const': 75,
	'continue': 76,
	'do': 77,
	'double': 78,
	'else': 79,
	'float': 80,
	'for': 81,
	'goto': 82,
	'if': 83,
	'int': 84,
	'long': 85,
	'register': 86,
	'return': 87,
	'short': 88,
	'sizeof': 89,
	'struct': 90,
	'switch': 91,
	'typedef': 92,
	'unsigned': 93,
	'void': 94,
	'while': 95,

	'printf': 100,
	'scanf': 101,
	'main': 102,
	'puts': 103,
	'strlen': 104,
	'sqrt': 105,
	'strcmp': 106,
	'pow': 107,
	'strstr': 108,
	'malloc': 109,
	'memset': 110,
	'fgets': 111,
	'putchar': 112,
	'strcat': 113,
	'tolower': 114,
	'toupper': 115,
	'strcpy': 116,
	'sin': 117,
	'cos': 118,
	'fabs': 119,
	'strncpy': 120,
	'exit': 121,
	'atoi': 122,
	'free': 123,
	'strncmp': 124,
	'strncat': 125,
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
	'||': 97,
	'~': 99,
}

delimiter2id = {
	'(': 42,
	')': 43,
	'[': 70,
	']': 71,
	'{': 96,
	'}': 98,
}

setA = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'}

setB = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}

setC = {'+', '-', '*', '/', '=', '&', '|', '^', '%', '!', '>', '<', '?', ':', ',', ';', '.'}

setD = {'(', ')', '[', ']', '{', '}'}

leftD = {'(', '[', '{'}
rightD = {')', ']', '}'}


def is_keyword(word):
	if word in keyword2id.keys():
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


def transform(path):
	ids = []
	content = remove_comment(path)
	content = content.replace('\t', '    ')
	symbol = ''
	state = 0
	for i in range(len(content)):
		item = content[i]
		if i < len(content)-1:
			next_item = content[i+1]
		else:
			next_item = None
		if state == 0:
			if item in setA | {'_'}:    # _, a
				symbol += item
				if next_item in setC | rightD:  # a*, a)
					state = 0
					# print(symbol, ' variable')
					ids.append([symbol, 'var0', 15, 'O'])
					# TODO(tdye): 区分不同变量值
				elif next_item in {'(', '{', '['}:    # else {,  hello(, main(
					state = 0
					if is_keyword(symbol):
						# print(symbol, ' keyword')
						ids.append([symbol, symbol, keyword2id[symbol], 'O'])
					elif next_item in {'['}:
						ids.append([symbol, 'var0', 15, 'O'])
					else:
						# print(symbol, ' function')
						ids.append([symbol, 'func0', 5, 'O'])
				else:
					state = 1
			elif item in {' ', '\n'}:
				state = 0
			elif item == '\'':
				state = 3
				symbol += item
			elif item == '\"':
				state = 5
				symbol += item
			elif item == '+':
				symbol += item
				if next_item not in {'+', '='} and pre not in setC:
					state = 0
					# print(symbol, ' +')     # add +
					ids.append([symbol, symbol, operator2id[symbol], 'O'])
				elif pre in setC:   # positive +
					if next_item not in setB | {' ', '\n', '.'}:
						state = 0
						# print(symbol, ' +')
						ids.append([symbol, symbol, operator2id[symbol], 'O'])
					else:
						state = 8
				else:
					state = 7
			elif item == '-':
				symbol += item
				if next_item not in {'-', '=', '>'} and pre not in setC:
					state = 0
					# print(symbol, ' -')     # sub
					ids.append([symbol, symbol, operator2id[symbol], 'O'])
				elif pre in setC:
					if next_item not in setB | {' ', '\n', '.'}:
						state = 0
						# print(symbol, ' -')
						ids.append([symbol, symbol, operator2id[symbol], 'O'])
					else:
						state = 11
				else:
					state = 10
			elif item == '*':
				symbol += item
				if next_item not in {'='}:
					state = 0
					# print(symbol, ' *')
					ids.append([symbol, symbol, operator2id[symbol], 'O'])
				else:
					state = 13
			elif item == '/':
				symbol += item
				if next_item not in {'='}:
					state = 0
					# print(symbol, ' /')
					ids.append([symbol, symbol, operator2id[symbol], 'O'])
				else:
					state = 14
			elif item == '=':
				symbol += item
				if next_item not in {'='}:
					state = 0
					# print(symbol, ' =')
					ids.append([symbol, symbol, operator2id[symbol], 'O'])
				else:
					state = 15
			elif item == '!':
				symbol += item
				if next_item not in {'='}:
					state = 0
					# print(symbol, ' !')
					ids.append([symbol, symbol, operator2id[symbol], 'O'])
				else:
					state = 16
			elif item == '<':
				symbol += item
				if next_item not in {'=', '<'}:
					state = 0
					# print(symbol, '<')
					ids.append([symbol, symbol, operator2id[symbol], 'O'])
				else:
					state = 17
			elif item == '>':
				symbol += item
				if next_item not in {'>', '='}:
					state = 0
					# print(symbol, ' >')
					ids.append([symbol, symbol, operator2id[symbol], 'O'])
				else:
					state = 19
			elif item == '&':
				symbol += item
				if next_item not in {'&'}:
					state = 0
					# print(symbol, ' &')
					ids.append([symbol, symbol, operator2id[symbol], 'O'])
				else:
					state = 21
			elif item == '%':
				symbol += item
				if next_item not in {'='}:
					state = 0
					# print(symbol, ' %')
					ids.append([symbol, symbol, operator2id[symbol], 'O'])
				else:
					state = 22
			elif item in setB:
				symbol += item
				if next_item not in setB | {'.'}:
					state = 0
					# print(symbol, ' numeric constant')
					ids.append([symbol, 'numeric_constant', 3, 'O'])
				else:
					state = 23
			elif item in setD | {',', ';', '?', ':'}:
				state = 0
				symbol += item
				if item in setD:
					# print(symbol, ' delimiter')
					ids.append([symbol, symbol, delimiter2id[symbol], 'O'])
				else:
					# print(symbol, ' operator')
					ids.append([symbol, symbol, operator2id[symbol], 'O'])
			elif item == '.':
				symbol += item
				state = 0
				# print(symbol, ' .')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
			elif item == '|':
				symbol += item
				if next_item not in {'|'}:
					state = 0
					# print(symbol, ' |')
					ids.append([symbol, symbol, operator2id[symbol], 'O'])
				else:
					state = 24
		elif state == 1:
			if item in setA | setB | {'_'}:    # a_, a5=====>a.  struct is regarded as a variable
				symbol += item
				if next_item in setC | rightD:  # a_*, a_)
					state = 0
					if is_keyword(symbol):
						# print(symbol, ' keyword')
						ids.append([symbol, symbol, keyword2id[symbol], 'O'])
					else:
						# print(symbol, ' variable')
						ids.append([symbol, 'var0', 15, 'O'])
				elif next_item in {'(', '{'}:    # else {,  hello(, main(
					state = 0
					if is_keyword(symbol):
						# print(symbol, ' keyword')
						ids.append([symbol, symbol, keyword2id[symbol], 'O'])
					else:
						# print(symbol, ' function')
						ids.append([symbol, 'func0', 5, 'O'])
			elif item in {' ', '\n'}:
				if next_item in setA | {'_'} | setB | setC | rightD:   # a ), a\n), a *, int a, int _a, return 8
					state = 0
					if is_keyword(symbol):
						# print(symbol, ' keyword')
						ids.append([symbol, symbol, keyword2id[symbol], 'O'])
					else:
						# print(symbol, ' variable')
						ids.append([symbol, 'var0', 15, 'O'])
				elif next_item in {'(', '{'}:   # else {,  hello(, main(
					state = 0
					if is_keyword(symbol):
						# print(symbol, ' keyword')
						ids.append([symbol, symbol, keyword2id[symbol], 'O'])
					else:
						# print(symbol, ' function')
						ids.append([symbol, 'func0', 5, 'O'])
				elif next_item in {'['}:
					state = 0
					# print(symbol, ' variable')
					ids.append([symbol, 'var0', 15, 'O'])
				else:
					state = 2
		elif state == 2:
			if item in {' ', '\n'}:
				if next_item in setA | {'_'} | setB | setC | rightD:  # a  ), a\n ), a  *, int  a, int  _a, return 8
					state = 0
					if is_keyword(symbol):
						# print(symbol, ' keyword')
						ids.append([symbol, symbol, keyword2id[symbol], 'O'])
					else:
						# print(symbol, ' variable')
						ids.append([symbol, 'var0', 15, 'O'])
				elif next_item in {'(', '{'}:    # else {,  hello(, main(
					state = 0
					if is_keyword(symbol):
						# print(symbol, ' keyword')
						ids.append([symbol, symbol, keyword2id[symbol], 'O'])
					else:
						# print(symbol, ' function')
						ids.append([symbol, 'func0', 5, 'O'])
				else:
					state = 2
		elif state == 3:
			symbol += item
			if item == '\'':
				state = 0
				# print(symbol, ' char constant')
				ids.append([symbol, 'char_constant', 4, 'O'])
			elif item == '\\':
				state = 4
		elif state == 4:
			symbol += item
			if item != '\\':
				state = 3
		elif state == 5:
			symbol += item
			if item == '\"':
				state = 0
				# print(symbol, ' string constant')
				ids.append([symbol, 'string_literal', 2, 'O'])
			elif item == '\\':
				state = 6
		elif state == 6:
			symbol += item
			if item != '\\':
				state = 5
		elif state == 7:
			symbol += item
			if item == '+':     # i++
				state = 0
				# print(symbol, ' ++')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
			elif item == '=':   # i+=
				state = 0
				# print(symbol, ' +=')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
		elif state == 8:
			if item in {' ', '\n'}:
				state = 8   # +   6
			elif item in setB | {'.'}:
				symbol += item
				if next_item not in setB | {'.'}:       # + 5end
					state = 0
					# print(symbol, ' numeric constant')
					ids.append([symbol, 'numeric_constant', 3, 'O'])
				else:
					state = 9
		elif state == 9:
			if item in setB | {'.'}:
				symbol += item      # +   6.6
				if next_item not in setB | {'.'}:   # + 5.6end
					state = 0
					# print(symbol, ' numeric constant')
					ids.append([symbol, 'numeric_constant', 3, 'O'])
				else:
					state = 9
		elif state == 10:
			symbol += item
			if item == '=':
				state = 0
				# print(symbol, ' -=')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
			elif item == '-':
				state = 0
				# print(symbol, ' --')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
			elif item == '>':
				state = 0
				# print(symbol, ' ->')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
		elif state == 11:
			if item in {' ', '\n'}:
				state = 11   # -   6
			elif item in setB | {'.'}:
				symbol += item
				if next_item not in setB | {'.'}:       # + 5end
					state = 0
					# print(symbol, ' numeric constant')
					ids.append([symbol, 'numeric_constant', 3, 'O'])
				else:
					state = 12
		elif state == 12:
			if item in setB | {'.'}:
				symbol += item      # -   6.6
				if next_item not in setB | {'.'}:   # - 6.6end
					state = 0
					# print(symbol, ' numeric constant')
					ids.append([symbol, 'numeric_constant', 3, 'O'])
				else:
					state = 12
		elif state == 13:
			symbol += item
			if item == '=':
				state = 0
				# print(symbol, ' *=')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
		elif state == 14:
			symbol += item
			if item == '=':
				state = 0
				# print(symbol, ' /=')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
		elif state == 15:
			symbol += item
			if item == '=':
				state = 0
				# print(symbol, ' ==')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
		elif state == 16:
			symbol += item
			if item == '=':
				state = 0
				# print(symbol, ' !=')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
		elif state == 17:
			symbol += item
			if item == '=':
				state = 0
				# print(symbol, ' <=')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
			elif item == '<':
				if next_item not in {'='}:
					state = 0
					# print(symbol, ' <<')
					ids.append([symbol, symbol, operator2id[symbol], 'O'])
				else:
					state = 18
		elif state == 18:
			symbol += item
			if item == '=':
				state = 0
				# print(symbol, ' <<=')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
		elif state == 19:
			symbol += item
			if item == '=':
				state = 0
				# print(symbol, ' >=')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
			elif item == '>':
				if next_item not in {'='}:
					state = 0
					# print(symbol, ' >>')
					ids.append([symbol, symbol, operator2id[symbol], 'O'])
				else:
					state = 20
		elif state == 20:
			symbol += item
			if item == '=':
				state = 0
				# print(symbol, ' >>=')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
		elif state == 21:
			symbol += item
			if item == '&':
				state = 0
				# print(symbol, ' &&')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
		elif state == 22:
			symbol += item
			if item == '=':
				state = 0
				# print(symbol, ' %=')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
		elif state == 23:
			symbol += item
			if next_item not in setB | {'.'}:
				state = 0
				# print(symbol, ' numeric constant')
				ids.append([symbol, 'numeric_constant', 3, 'O'])
			else:
				state = 23
		elif state == 24:
			symbol += item
			if item == '|':
				state = 0
				# print(symbol, ' ||')
				ids.append([symbol, symbol, operator2id[symbol], 'O'])
		if state == 0 and len(symbol) > 0:
			pre = symbol
			symbol = ''
	return [ids]


if __name__ == '__main__':
	ids_ = transform(path="sum.cpp")
	for item in ids_:
		print(item)
