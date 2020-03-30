# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/3/30 11:53
# @name:program2vector
# @author:TDYe
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

setA = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'}

setB = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}

setC = {'+', '-', '*', '/', '=', '&', '|', '^', '%', '!', '>', '<', '?', ':', ',', ';'}

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


def program2vector(path):
	content = remove_comment(path)
	symbol = ''
	state = 0
	item, next_item = None, None
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
					print(symbol, ' variable')
				elif next_item in {'('}:    # printf(, pay(
					state = 0
					if is_keyword(symbol):
						print(symbol, ' keyword')
					else:
						print(symbol, ' function')
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
					print(symbol, ' +')     # add +
				elif pre in setC:   # positive +
					if next_item not in {' ', '\n'}:
						state = 0
						print(symbol, ' +')
					else:
						state = 8
				else:
					state = 7
			elif item == '-':
				symbol += item
				if next_item not in {'-', '=', '>'} and pre not in setC:
					state = 0
					print(symbol, ' -')     # sub
				elif pre in setC:
					if next_item not in {' ', '\n'}:
						state = 0
						print(symbol, ' -')
					else:
						state = 11
				else:
					state = 10
			elif item == '*':
				symbol += item
				if next_item not in {'='}:
					state = 0
					print(symbol, ' *')
				else:
					state = 13
			elif item == '/':
				symbol += item
				if next_item not in {'='}:
					state = 0
					print(symbol, ' /')
				else:
					state = 14
			elif item == '=':
				symbol += item
				if next_item not in {'='}:
					state = 0
					print(symbol, ' =')
				else:
					state = 15
			elif item == '!':
				symbol += item
				if next_item not in {'='}:
					state = 0
					print(symbol, ' !')
				else:
					state = 16
			elif item == '<':
				symbol += item
				if next_item not in {'=', '<'}:
					state = 0
					print(symbol, '<')
				else:
					state = 17
			elif item == '>':
				symbol += item
				if next_item not in {'>', '='}:
					state = 0
					print(symbol, ' >')
				else:
					state = 19
			elif item == '&':
				symbol += item
				if next_item not in {'&'}:
					state = 0
					print(symbol, ' &')
				else:
					state = 21
			elif item == '%':
				symbol += item
				if next_item not in {'='}:
					state = 0
					print(symbol, ' %')
				else:
					state = 22
			elif item in setB:
				symbol += item
				if next_item not in setB | {'.'}:
					state = 0
					print(symbol, ' numeric constant')
				else:
					state = 23
			elif item in setD | {',', ';', '?', ':'}:
				state = 0
				symbol += item
				print(symbol, ' delimiter')
		elif state == 1:
			if item in setA | setB | {'_', '.'}:    # a_, a., a5=====>a.  struct is regarded as a variable
				symbol += item
				if next_item in setC | rightD | {' ', '\n'}:  # a_*, a_)
					state = 0
					if is_keyword(symbol):
						print(symbol, ' keyword')
					else:
						print(symbol, ' variable')
				elif next_item in {'('}:    # a5(,
					state = 0
					if is_keyword(symbol):
						print(symbol, ' keyword')   # seemly not exist
					else:
						print(symbol, ' function')
			elif item in {' ', '\n'}:
				if next_item in setA | setB | setC | {'_'} | rightD:   # a ), a\n), a *, int a, int _a
					state = 0
					if is_keyword(symbol):
						print(symbol, ' keyword')
					else:
						print(symbol, ' variable')
				elif next_item in {'('}:
					state = 0
					print(symbol, ' function')
				else:
					state = 2
		elif state == 2:
			if item in {' ', '\n'}:
				if next_item in setA | setB | setC | {'_'} | rightD:  # a  ), a\n ), a  *, int  a, int  _a, return 8, return 0
					state = 0
					if is_keyword(symbol):
						print(symbol, ' keyword')
					else:
						print(symbol, ' variable')
				elif next_item in {'('}:
					state = 0
					print(symbol, ' function')
				else:
					state = 2
		elif state == 3:
			symbol += item
			if item == '\'':
				state = 0
				print(symbol, ' char constant')
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
				print(symbol, ' string constant')
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
				print(symbol, ' ++')
			elif item == '=':   # i+=
				state = 0
				print(symbol, ' +=')
		elif state == 8:
			if item in {' ', '\n'}:
				state = 8   # +   6
			elif item in setB | {'.'}:
				symbol += item
				if next_item not in setB | {'.'}:       # + 5end
					state = 0
					print(symbol, ' numeric constant')
				else:
					state = 9
		elif state == 9:
			if item in setB | {'.'}:
				symbol += item      # +   6.6
				if next_item not in setB | {'.'}:   # + 5.6end
					state = 0
					print(symbol, ' numeric constant')
				else:
					state = 9
		elif state == 10:
			symbol += item
			if item == '=':
				state = 0
				print(symbol, ' -=')
			elif item == '-':
				state = 0
				print(symbol, ' --')
			elif item == '>':
				state = 0
				print(symbol, ' ->')
		elif state == 11:
			if item in {' ', '\n'}:
				state = 11   # -   6
			elif item in setB | {'.'}:
				symbol += item
				if next_item not in setB | {'.'}:       # + 5end
					state = 0
					print(symbol, ' numeric constant')
				else:
					state = 12
		elif state == 12:
			if item in setB | {'.'}:
				symbol += item      # -   6.6
				if next_item not in setB | {'.'}:   # - 6.6end
					state = 0
					print(symbol, ' numeric constant')
				else:
					state = 12
		elif state == 13:
			symbol += item
			if item == '=':
				state = 0
				print(symbol, ' *=')
		elif state == 14:
			symbol += item
			if item == '=':
				state = 0
				print(symbol, ' /=')
		elif state == 15:
			symbol += item
			if item == '=':
				state = 0
				print(symbol, ' ==')
		elif state == 16:
			symbol += item
			if item == '=':
				state = 0
				print(symbol, ' !=')
		elif state == 17:
			symbol += item
			if item == '=':
				state = 0
				print(symbol, ' <=')
			elif item == '<':
				if next_item not in {'='}:
					state = 0
					print(symbol, ' <<')
				else:
					state = 18
		elif state == 18:
			symbol += item
			if item == '=':
				state = 0
				print(symbol, ' <<=')
		elif state == 19:
			symbol += item
			if item == '=':
				state = 0
				print(symbol, ' >=')
			elif item == '>':
				if next_item not in {'='}:
					state = 0
					print(symbol, ' >>')
				else:
					state = 20
		elif state == 20:
			symbol += item
			if item == '=':
				state = 0
				print(symbol, ' >>=')
		elif state == 21:
			symbol += item
			if item == '&':
				state = 0
				print(symbol, ' &&')
		elif state == 22:
			symbol += item
			if item == '=':
				state = 0
				print(symbol, ' %=')
		elif state == 23:
			symbol += item
			if next_item not in setB | {'.'}:
				state = 0
				print(symbol, ' numeric constant')
			else:
				state = 23
		if state == 0 and len(symbol) > 0:
			pre = symbol
			symbol = ''


if __name__ == '__main__':
	program2vector(path="sum.cpp")
