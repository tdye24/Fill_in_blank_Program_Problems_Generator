# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/4/6 21:34
# @name:utils
# @author:TDYe
import re
import os
# from logfile import logger


def get_test_cases_num(proId: str):
	"""
	given a proId then get test cases num according to this problem
	:param proId: path to the problem
	:return: num of test cases
	"""
	count = 0
	path = '../data/test_cases/%s' % proId
	for _ in os.listdir(path):
		count = count + 1
	return int(count / 2)


def io_redirect(submissionId_proId_th_: str, i: str, o: str):
	content = ''
	problem_id = submissionId_proId_th_.split('-')[1]
	in_path = '../test_cases/%s/%s.in' % (problem_id, i)
	out_path = '../out/%s-%s.out' % (submissionId_proId_th_, o)
	path = '../data/submissions/%s.cpp' % submissionId_proId_th_
	try:
		f = open(file=path, mode='r', encoding='utf-8')
		for line in f.readlines():
			content += line
	except IOError:
		print("reading file failed")
	finally:
		f.close()
		# add include file #include<bits/stdc++.h> and IO redirect
		content = '#include<bits/stdc++.h>\nusing namespace std;\n' + content
		content = re.sub(r'main\s*\(.*?\)\s*{', "main() {\n    freopen(\"%s\",\"r\",stdin);\n    freopen(\"%s\",\"w\",stdout);" % (in_path, out_path), content)
		with open('../data/submissions/%s-normal-%s.cpp' % (submissionId_proId_th_, o), 'w') as f1:
			f1.write(content)


def generate_normal_files(submissionId_proId_th_):
	problem_id = submissionId_proId_th_.split('-')[1]    # str
	test_cases_num = get_test_cases_num(problem_id)
	for i in range(test_cases_num):
		io_redirect(submissionId_proId_th_, str(i+1), str(i+1))


def read_out(path: str):
	out = ''
	try:
		with open(path, 'r') as f:
			out = f.read()
	except IOError as e:
		print(e)
		# logger.error(e)
	finally:
		return out
